-- Candidate records may start with any established supported locale. Missing
-- launch locales remain absent and are enforced by publication readiness.

create function private.validate_institution_localizations(
  p_id uuid,
  p_payload jsonb
) returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_localizations jsonb := p_payload->'localizations';
  v_publication_status text := coalesce(
    p_payload#>>'{core,publication_status}',
    'draft'
  );
  v_locale_count integer;
begin
  if jsonb_typeof(v_localizations) is distinct from 'array'
    or jsonb_array_length(v_localizations) = 0 then
    raise exception 'at least one complete localization is required'
      using errcode = '22023';
  end if;

  if exists (
    select 1
    from jsonb_array_elements(v_localizations) item
    where coalesce(item->>'locale', '') not in ('en-EG', 'ar-EG')
      or nullif(trim(item->>'name'), '') is null
      or nullif(trim(item->>'slug'), '') is null
  ) then
    raise exception 'each localization requires a supported locale, name, and slug'
      using errcode = '22023';
  end if;

  if (
    select count(*) <> count(distinct item->>'locale')
    from jsonb_array_elements(v_localizations) item
  ) then
    raise exception 'localization locales must be unique'
      using errcode = '22023';
  end if;

  if v_publication_status in ('public_noindex', 'index_ready', 'published') then
    select count(distinct locale) into v_locale_count
    from (
      select l.locale
      from public.institution_localizations l
      where p_id is not null and l.institution_id = p_id
      union all
      select item->>'locale'
      from jsonb_array_elements(v_localizations) item
    ) launch_locales
    where locale in ('en-EG', 'ar-EG');

    if v_locale_count < 2 then
      raise exception 'both launch localizations are required for publication'
        using errcode = '22023';
    end if;
  end if;
end;
$$;

revoke all on function private.validate_institution_localizations(uuid, jsonb)
from public, anon;
grant execute on function private.validate_institution_localizations(uuid, jsonb)
to authenticated, service_role;

create or replace function private.save_institution(
  p_id uuid,
  p_payload jsonb,
  p_reason text
) returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_id uuid := coalesce(p_id, gen_random_uuid());
  v_actor uuid := (select auth.uid());
  v_change uuid;
  v_old jsonb;
  v_old_locale jsonb;
  v_locale jsonb;
  v_campus jsonb;
  v_kind text;
  v_table regclass;
  v_column text;
  v_related text;
begin
  if v_actor is null
    or not private.has_staff_role(array['super_admin','admin','researcher','editor']) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  if length(trim(coalesce(p_reason, ''))) < 3 then
    raise exception 'change reason is required' using errcode = '22023';
  end if;

  select to_jsonb(i) into v_old
  from public.institutions i where i.id = v_id for update;
  insert into public.change_sets(actor_id, reason, source_id)
  values(v_actor, p_reason, nullif(p_payload->>'source_id', '')::uuid)
  returning id into v_change;

  if p_id is null then
    insert into public.institutions(
      id, provider_id, institution_type_id, ownership_type_id,
      education_model_id, official_name, official_website_url, founded_year,
      publication_status, data_status
    ) values (
      v_id,
      nullif(p_payload#>>'{core,provider_id}', '')::uuid,
      (p_payload#>>'{core,institution_type_id}')::uuid,
      nullif(p_payload#>>'{core,ownership_type_id}', '')::uuid,
      nullif(p_payload#>>'{core,education_model_id}', '')::uuid,
      p_payload#>>'{core,official_name}',
      nullif(p_payload#>>'{core,official_website_url}', ''),
      nullif(p_payload#>>'{core,founded_year}', '')::integer,
      coalesce(p_payload#>>'{core,publication_status}', 'draft'),
      coalesce(p_payload#>>'{core,data_status}', 'candidate')
    );
    perform private.write_revision(
      v_change, 'institution', v_id, 'create', 'record', null,
      (select to_jsonb(i) from public.institutions i where i.id = v_id)
    );
  else
    if v_old is null then
      raise exception 'institution not found' using errcode = 'P0002';
    end if;
    update public.institutions set
      provider_id = nullif(p_payload#>>'{core,provider_id}', '')::uuid,
      institution_type_id = (p_payload#>>'{core,institution_type_id}')::uuid,
      ownership_type_id = nullif(p_payload#>>'{core,ownership_type_id}', '')::uuid,
      education_model_id = nullif(p_payload#>>'{core,education_model_id}', '')::uuid,
      official_name = p_payload#>>'{core,official_name}',
      official_website_url = nullif(p_payload#>>'{core,official_website_url}', ''),
      founded_year = nullif(p_payload#>>'{core,founded_year}', '')::integer,
      publication_status = coalesce(
        p_payload#>>'{core,publication_status}', publication_status
      ),
      data_status = coalesce(p_payload#>>'{core,data_status}', data_status)
    where id = v_id;
    perform private.write_revision(
      v_change, 'institution', v_id, 'update', 'record', v_old,
      (select to_jsonb(i) from public.institutions i where i.id = v_id)
    );
  end if;

  for v_locale in
    select * from jsonb_array_elements(p_payload->'localizations')
  loop
    select to_jsonb(l) into v_old_locale
    from public.institution_localizations l
    where l.institution_id = v_id and l.locale = v_locale->>'locale';

    insert into public.institution_localizations(
      institution_id, locale, name, slug, summary
    ) values (
      v_id, v_locale->>'locale', v_locale->>'name', v_locale->>'slug',
      nullif(v_locale->>'summary', '')
    ) on conflict(institution_id, locale) do update set
      name = excluded.name,
      slug = excluded.slug,
      summary = excluded.summary;

    perform private.write_revision(
      v_change,
      'institution_localization',
      v_id,
      case when v_old_locale is null then 'create' else 'update' end,
      v_locale->>'locale',
      v_old_locale,
      (select to_jsonb(l) from public.institution_localizations l
       where l.institution_id = v_id and l.locale = v_locale->>'locale')
    );
  end loop;

  v_campus := p_payload->'campus';
  if v_campus is not null then
    insert into public.campuses(
      id, institution_id, location_id, name, is_main, address_en, address_ar
    ) values (
      coalesce(nullif(v_campus->>'id', '')::uuid, gen_random_uuid()),
      v_id, (v_campus->>'location_id')::uuid, v_campus->>'name', true,
      nullif(v_campus->>'address_en', ''), nullif(v_campus->>'address_ar', '')
    ) on conflict(id) do update set
      location_id = excluded.location_id,
      name = excluded.name,
      address_en = excluded.address_en,
      address_ar = excluded.address_ar;
  end if;

  for v_kind, v_table, v_column in values
    ('education_levels','public.institution_education_levels'::regclass,'education_level_id'),
    ('curricula','public.institution_curricula'::regclass,'curriculum_id'),
    ('languages','public.institution_languages'::regclass,'language_id'),
    ('certificates','public.institution_certificates'::regclass,'certificate_id')
  loop
    execute format('delete from %s where institution_id=$1', v_table) using v_id;
    for v_related in
      select * from jsonb_array_elements_text(
        coalesce(p_payload#>array['relationships', v_kind], '[]')
      )
    loop
      execute format(
        'insert into %s(institution_id,%I) values($1,$2)', v_table, v_column
      ) using v_id, v_related::uuid;
    end loop;
  end loop;
  perform private.write_revision(
    v_change, 'institution', v_id, 'replace', 'relationships', null,
    p_payload->'relationships'
  );
  return v_id;
end;
$$;

create or replace function public.create_institution_command(
  payload jsonb,
  reason text
) returns uuid
language plpgsql
security invoker
set search_path = ''
as $$
begin
  perform private.validate_institution_localizations(null, payload);
  return private.save_institution(null, payload, reason);
end;
$$;

create or replace function public.update_institution_command(
  institution_id uuid,
  payload jsonb,
  reason text
) returns uuid
language plpgsql
security invoker
set search_path = ''
as $$
begin
  perform private.validate_institution_localizations(institution_id, payload);
  return private.save_institution(institution_id, payload, reason);
end;
$$;

create or replace function public.institution_readiness(institution_id uuid)
returns jsonb
language sql
stable
security invoker
set search_path = ''
as $$
  with facts as (
    select i.id,
      exists(
        select 1 from public.campuses c
        where c.institution_id = i.id and c.status = 'active'
      ) has_campus,
      exists(
        select 1 from public.entity_assertions a
        where a.entity_type = 'institution'
          and a.entity_id = i.id
          and a.assertion_status = 'accepted'
      ) has_evidence,
      exists(
        select 1 from public.institution_localizations l
        where l.institution_id = i.id and l.locale = 'en-EG'
          and nullif(trim(l.name), '') is not null
          and nullif(trim(l.slug), '') is not null
      ) has_en_locale,
      exists(
        select 1 from public.institution_localizations l
        where l.institution_id = i.id and l.locale = 'ar-EG'
          and nullif(trim(l.name), '') is not null
          and nullif(trim(l.slug), '') is not null
      ) has_ar_locale,
      exists(
        select 1 from public.institution_localizations l
        where l.institution_id = i.id and l.locale = 'en-EG'
          and nullif(trim(l.summary), '') is not null
      ) has_en_summary,
      exists(
        select 1 from public.institution_localizations l
        where l.institution_id = i.id and l.locale = 'ar-EG'
          and nullif(trim(l.summary), '') is not null
      ) has_ar_summary,
      exists(
        select 1 from public.assertion_conflicts c
        where c.entity_type = 'institution'
          and c.entity_id = i.id
          and c.status = 'open'
      ) has_conflict
    from public.institutions i
    where i.id = institution_id
  )
  select jsonb_build_object(
    'record_exists', id is not null,
    'public_ready',
      has_campus and has_evidence and has_en_locale and has_ar_locale
      and not has_conflict,
    'index_ready',
      has_campus and has_evidence and has_en_locale and has_ar_locale
      and has_en_summary and has_ar_summary and not has_conflict,
    'reasons', to_jsonb(array_remove(array[
      case when not has_campus then 'missing_active_campus' end,
      case when not has_evidence then 'missing_accepted_evidence' end,
      case when not has_en_locale then 'missing_required_localization: en-EG' end,
      case when not has_ar_locale then 'missing_required_localization: ar-EG' end,
      case when has_en_locale and not has_en_summary then 'missing_english_summary' end,
      case when has_ar_locale and not has_ar_summary then 'missing_arabic_summary' end,
      case when has_conflict then 'open_critical_conflict' end
    ], null))
  )
  from facts;
$$;
