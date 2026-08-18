-- Milestone 2: trustworthy data operations. Public wrappers are invokers;
-- privileged mutation logic stays in the unexposed private schema.

alter table public.staff_users drop constraint staff_users_role_check;
alter table public.staff_users add constraint staff_users_role_check check (
  role in ('super_admin','admin','researcher','editor','reviewer','seo_manager')
);

create function private.has_staff_role(allowed_roles text[] default null)
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (
    select 1 from public.staff_users
    where user_id = (select auth.uid()) and status = 'active'
      and (allowed_roles is null or role = any(allowed_roles))
  );
$$;
revoke all on function private.has_staff_role(text[]) from public;
grant execute on function private.has_staff_role(text[]) to authenticated, service_role;

create table public.change_sets (
  id uuid primary key default gen_random_uuid(),
  actor_id uuid not null references auth.users(id) on delete restrict,
  reason text not null check (length(trim(reason)) >= 3),
  source_id uuid,
  created_at timestamptz not null default now()
);
create table public.entity_revisions (
  id bigint generated always as identity primary key,
  change_set_id uuid not null references public.change_sets(id) on delete restrict,
  entity_type text not null check (entity_type in ('institution','institution_localization','campus','institution_relationship','source','assertion','research_task')),
  entity_id uuid not null,
  operation text not null check (operation in ('create','update','delete','transition','replace')),
  field_key text not null,
  old_value jsonb,
  new_value jsonb,
  created_at timestamptz not null default now()
);
create index entity_revisions_entity_idx on public.entity_revisions(entity_type,entity_id,created_at desc);
create index entity_revisions_change_set_idx on public.entity_revisions(change_set_id);

create table public.sources (
  id uuid primary key default gen_random_uuid(),
  source_type text not null check (source_type in ('government','regulator','institution_website','institution_social','accreditation_authority','curriculum_authority','official_document','authoritative_publication','secondary')),
  publisher text not null, title text not null, url text not null,
  language text not null check (language in ('ar','en','mixed','other')),
  authority_level smallint not null check (authority_level between 1 and 6),
  published_at timestamptz, retrieved_at timestamptz not null default now(),
  status text not null default 'active' check (status in ('active','unavailable','retired','disputed')),
  notes text, created_by uuid not null references auth.users(id) on delete restrict,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  check (url ~ '^https?://'), unique(url)
);
create table public.source_snapshots (
  id uuid primary key default gen_random_uuid(), source_id uuid not null references public.sources(id) on delete restrict,
  retrieved_at timestamptz not null, content_hash text not null check (content_hash ~ '^[a-f0-9]{64}$'),
  extracted_metadata jsonb not null default '{}', storage_path text,
  capture_method text not null default 'manual' check (capture_method in ('manual','metadata','permitted_file','permitted_screenshot')),
  status text not null default 'captured' check (status in ('captured','failed','restricted','removed')),
  created_by uuid not null references auth.users(id) on delete restrict, created_at timestamptz not null default now(),
  unique(source_id,content_hash)
);
alter table public.change_sets add constraint change_sets_source_fk foreign key(source_id) references public.sources(id) on delete set null;

create table public.entity_assertions (
  id uuid primary key default gen_random_uuid(),
  entity_type text not null check (entity_type in ('institution','institution_localization','campus')),
  entity_id uuid not null, field_key text not null,
  locale text check (locale is null or locale in ('en-EG','ar-EG')),
  value_jsonb jsonb not null, source_id uuid not null references public.sources(id) on delete restrict,
  source_snapshot_id uuid references public.source_snapshots(id) on delete restrict,
  confidence smallint not null default 50 check (confidence between 0 and 100),
  assertion_status text not null default 'unreviewed' check (assertion_status in ('unreviewed','accepted','rejected','superseded','conflicting')),
  observed_at timestamptz not null, valid_from date, valid_to date,
  created_by uuid not null references auth.users(id) on delete restrict,
  reviewed_by uuid references auth.users(id) on delete restrict, reviewed_at timestamptz, review_reason text,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  check (valid_to is null or valid_from is null or valid_to >= valid_from),
  check ((assertion_status in ('accepted','rejected','superseded')) = (reviewed_by is not null))
);
create index entity_assertions_entity_field_idx on public.entity_assertions(entity_type,entity_id,field_key,assertion_status);
create index entity_assertions_source_idx on public.entity_assertions(source_id);

create table public.assertion_conflicts (
  id uuid primary key default gen_random_uuid(), entity_type text not null, entity_id uuid not null, field_key text not null,
  locale text, status text not null default 'open' check (status in ('open','resolved','dismissed')),
  resolution_reason text, resolved_by uuid references auth.users(id) on delete restrict, resolved_at timestamptz,
  created_at timestamptz not null default now(), unique nulls not distinct(entity_type,entity_id,field_key,locale,status)
);
create table public.assertion_conflict_members (
  conflict_id uuid not null references public.assertion_conflicts(id) on delete cascade,
  assertion_id uuid not null references public.entity_assertions(id) on delete restrict,
  primary key(conflict_id,assertion_id)
);

create table public.research_tasks (
  id uuid primary key default gen_random_uuid(),
  task_type text not null check (task_type in ('initial_research','source_verification','conflict_resolution','contact_refresh','translation','duplicate_review','quality_review')),
  entity_type text not null default 'institution', entity_id uuid not null,
  source_id uuid references public.sources(id) on delete set null,
  assertion_id uuid references public.entity_assertions(id) on delete set null,
  conflict_id uuid references public.assertion_conflicts(id) on delete set null,
  priority text not null default 'normal' check (priority in ('low','normal','high','critical')),
  status text not null default 'open' check (status in ('open','assigned','in_progress','in_review','completed','cancelled')),
  assigned_to uuid references auth.users(id) on delete set null, due_at timestamptz,
  notes text, outcome text, created_by uuid not null references auth.users(id) on delete restrict,
  completed_by uuid references auth.users(id) on delete restrict, completed_at timestamptz,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
alter table public.research_tasks add constraint research_tasks_entity_id_fkey foreign key(entity_id) references public.institutions(id) on delete cascade;
create index research_tasks_queue_idx on public.research_tasks(status,priority,due_at);
create index research_tasks_assignee_idx on public.research_tasks(assigned_to,status);

create table public.freshness_policies (
  id uuid primary key default gen_random_uuid(), entity_type text not null, field_key text not null,
  review_interval_days integer not null check (review_interval_days > 0),
  due_soon_days integer not null default 14 check (due_soon_days >= 0),
  priority text not null default 'normal' check (priority in ('low','normal','high','critical')),
  status text not null default 'active' check (status in ('active','inactive')), notes text,
  unique(entity_type,field_key)
);
create table public.field_freshness (
  entity_type text not null, entity_id uuid not null, field_key text not null,
  last_verified_at timestamptz, next_review_at timestamptz,
  status text not null default 'unknown' check (status in ('fresh','due_soon','due','stale','unknown')),
  assertion_id uuid references public.entity_assertions(id) on delete set null,
  updated_at timestamptz not null default now(), primary key(entity_type,entity_id,field_key)
);
create index field_freshness_queue_idx on public.field_freshness(status,next_review_at);

create table public.completeness_requirements (
  id uuid primary key default gen_random_uuid(), institution_type_id uuid references public.institution_types(id) on delete cascade,
  stage text not null check (stage in ('public','indexable','enriched')), field_key text not null,
  critical boolean not null default true, status text not null default 'active' check (status in ('active','inactive')),
  unique nulls not distinct(institution_type_id,stage,field_key)
);

do $$ declare table_name text; begin
  foreach table_name in array array['change_sets','entity_revisions','sources','source_snapshots','entity_assertions','assertion_conflicts','assertion_conflict_members','research_tasks','freshness_policies','field_freshness','completeness_requirements'] loop
    execute format('alter table public.%I enable row level security',table_name);
    execute format('grant all on public.%I to service_role',table_name);
    execute format('grant select,insert,update on public.%I to authenticated',table_name);
  end loop;
end $$;
grant usage,select on all sequences in schema public to authenticated, service_role;

do $$ declare table_name text; begin
  foreach table_name in array array['change_sets','entity_revisions','sources','source_snapshots','entity_assertions','assertion_conflicts','assertion_conflict_members','research_tasks','freshness_policies','field_freshness','completeness_requirements'] loop
    execute format('create policy %I on public.%I for select to authenticated using ((select private.is_internal_user()))',table_name||'_staff_read',table_name);
  end loop;
end $$;
create policy sources_research_insert on public.sources for insert to authenticated with check ((select private.has_staff_role(array['super_admin','admin','researcher','editor'])) and created_by=(select auth.uid()));
create policy sources_research_update on public.sources for update to authenticated using ((select private.has_staff_role(array['super_admin','admin','researcher','editor']))) with check ((select private.has_staff_role(array['super_admin','admin','researcher','editor'])));
create policy snapshots_research_insert on public.source_snapshots for insert to authenticated with check ((select private.has_staff_role(array['super_admin','admin','researcher','editor'])) and created_by=(select auth.uid()));
create policy assertions_research_insert on public.entity_assertions for insert to authenticated with check ((select private.has_staff_role(array['super_admin','admin','researcher','editor'])) and created_by=(select auth.uid()) and assertion_status in ('unreviewed','conflicting'));
create policy assertions_reviewer_update on public.entity_assertions for update to authenticated using ((select private.has_staff_role(array['super_admin','admin','reviewer']))) with check ((select private.has_staff_role(array['super_admin','admin','reviewer'])));
create policy tasks_staff_insert on public.research_tasks for insert to authenticated with check ((select private.is_internal_user()) and created_by=(select auth.uid()));
create policy tasks_staff_update on public.research_tasks for update to authenticated using ((select private.is_internal_user())) with check ((select private.is_internal_user()));
create policy freshness_admin_insert on public.freshness_policies for insert to authenticated with check ((select private.has_staff_role(array['super_admin','admin'])));
create policy freshness_admin_update on public.freshness_policies for update to authenticated using ((select private.has_staff_role(array['super_admin','admin']))) with check ((select private.has_staff_role(array['super_admin','admin'])));
create policy freshness_admin_delete on public.freshness_policies for delete to authenticated using ((select private.has_staff_role(array['super_admin','admin'])));
create policy completeness_admin_insert on public.completeness_requirements for insert to authenticated with check ((select private.has_staff_role(array['super_admin','admin','seo_manager'])));
create policy completeness_admin_update on public.completeness_requirements for update to authenticated using ((select private.has_staff_role(array['super_admin','admin','seo_manager']))) with check ((select private.has_staff_role(array['super_admin','admin','seo_manager'])));
create policy completeness_admin_delete on public.completeness_requirements for delete to authenticated using ((select private.has_staff_role(array['super_admin','admin','seo_manager'])));

create function private.write_revision(p_change_set uuid,p_entity_type text,p_entity_id uuid,p_operation text,p_field_key text,p_old jsonb,p_new jsonb)
returns void language sql security definer set search_path='' as $$
  insert into public.entity_revisions(change_set_id,entity_type,entity_id,operation,field_key,old_value,new_value)
  values(p_change_set,p_entity_type,p_entity_id,p_operation,p_field_key,p_old,p_new);
$$;
revoke all on function private.write_revision(uuid,text,uuid,text,text,jsonb,jsonb) from public;

create function private.save_institution(p_id uuid,p_payload jsonb,p_reason text)
returns uuid language plpgsql security definer set search_path='' as $$
declare v_id uuid:=coalesce(p_id,gen_random_uuid()); v_actor uuid:=(select auth.uid()); v_change uuid; v_old jsonb; v_locale jsonb; v_campus jsonb; v_kind text; v_table regclass; v_column text; v_related text; begin
  if v_actor is null or not private.has_staff_role(array['super_admin','admin','researcher','editor']) then raise exception 'not authorized' using errcode='42501'; end if;
  if length(trim(coalesce(p_reason,'')))<3 then raise exception 'change reason is required' using errcode='22023'; end if;
  select to_jsonb(i) into v_old from public.institutions i where i.id=v_id for update;
  insert into public.change_sets(actor_id,reason,source_id) values(v_actor,p_reason,nullif(p_payload->>'source_id','')::uuid) returning id into v_change;
  if p_id is null then
    insert into public.institutions(id,provider_id,institution_type_id,ownership_type_id,education_model_id,official_name,official_website_url,founded_year,publication_status,data_status)
    values(v_id,nullif(p_payload#>>'{core,provider_id}','')::uuid,(p_payload#>>'{core,institution_type_id}')::uuid,nullif(p_payload#>>'{core,ownership_type_id}','')::uuid,nullif(p_payload#>>'{core,education_model_id}','')::uuid,p_payload#>>'{core,official_name}',nullif(p_payload#>>'{core,official_website_url}',''),nullif(p_payload#>>'{core,founded_year}','')::integer,coalesce(p_payload#>>'{core,publication_status}','draft'),coalesce(p_payload#>>'{core,data_status}','candidate'));
    perform private.write_revision(v_change,'institution',v_id,'create','record',null,(select to_jsonb(i) from public.institutions i where i.id=v_id));
  else
    if v_old is null then raise exception 'institution not found' using errcode='P0002'; end if;
    update public.institutions set provider_id=nullif(p_payload#>>'{core,provider_id}','')::uuid,institution_type_id=(p_payload#>>'{core,institution_type_id}')::uuid,ownership_type_id=nullif(p_payload#>>'{core,ownership_type_id}','')::uuid,education_model_id=nullif(p_payload#>>'{core,education_model_id}','')::uuid,official_name=p_payload#>>'{core,official_name}',official_website_url=nullif(p_payload#>>'{core,official_website_url}',''),founded_year=nullif(p_payload#>>'{core,founded_year}','')::integer,publication_status=coalesce(p_payload#>>'{core,publication_status}',publication_status),data_status=coalesce(p_payload#>>'{core,data_status}',data_status) where id=v_id;
    perform private.write_revision(v_change,'institution',v_id,'update','record',v_old,(select to_jsonb(i) from public.institutions i where i.id=v_id));
  end if;
  for v_locale in select * from jsonb_array_elements(coalesce(p_payload->'localizations','[]')) loop
    insert into public.institution_localizations(institution_id,locale,name,slug,summary) values(v_id,v_locale->>'locale',v_locale->>'name',v_locale->>'slug',nullif(v_locale->>'summary','')) on conflict(institution_id,locale) do update set name=excluded.name,slug=excluded.slug,summary=excluded.summary;
  end loop;
  v_campus:=p_payload->'campus';
  if v_campus is not null then
    insert into public.campuses(id,institution_id,location_id,name,is_main,address_en,address_ar) values(coalesce(nullif(v_campus->>'id','')::uuid,gen_random_uuid()),v_id,(v_campus->>'location_id')::uuid,v_campus->>'name',true,nullif(v_campus->>'address_en',''),nullif(v_campus->>'address_ar','')) on conflict(id) do update set location_id=excluded.location_id,name=excluded.name,address_en=excluded.address_en,address_ar=excluded.address_ar;
  end if;
  for v_kind,v_table,v_column in values ('education_levels','public.institution_education_levels'::regclass,'education_level_id'),('curricula','public.institution_curricula'::regclass,'curriculum_id'),('languages','public.institution_languages'::regclass,'language_id'),('certificates','public.institution_certificates'::regclass,'certificate_id') loop
    execute format('delete from %s where institution_id=$1',v_table) using v_id;
    for v_related in select * from jsonb_array_elements_text(coalesce(p_payload#>array['relationships',v_kind],'[]')) loop execute format('insert into %s(institution_id,%I) values($1,$2)',v_table,v_column) using v_id,v_related::uuid; end loop;
  end loop;
  perform private.write_revision(v_change,'institution',v_id,'replace','relationships',null,p_payload->'relationships');
  return v_id;
end; $$;
revoke all on function private.save_institution(uuid,jsonb,text) from public;
grant execute on function private.save_institution(uuid,jsonb,text) to authenticated;
grant usage on schema private to authenticated;

create function public.create_institution_command(payload jsonb,reason text) returns uuid language sql security invoker set search_path='' as $$ select private.save_institution(null,payload,reason); $$;
create function public.update_institution_command(institution_id uuid,payload jsonb,reason text) returns uuid language sql security invoker set search_path='' as $$ select private.save_institution(institution_id,payload,reason); $$;
revoke all on function public.create_institution_command(jsonb,text),public.update_institution_command(uuid,jsonb,text) from public,anon;
grant execute on function public.create_institution_command(jsonb,text),public.update_institution_command(uuid,jsonb,text) to authenticated;

do $$ declare table_name text; begin
  foreach table_name in array array['sources','entity_assertions','research_tasks'] loop execute format('create trigger %I before update on public.%I for each row execute function private.set_updated_at()',table_name||'_set_updated_at',table_name); end loop;
end $$;

create function private.detect_assertion_conflict()
returns trigger language plpgsql security definer set search_path='' as $$
declare v_other uuid; v_conflict uuid; begin
  if new.reviewed_by is not null then return new; end if;
  if new.assertion_status not in ('unreviewed','accepted') then return new; end if;
  select id into v_other from public.entity_assertions
  where entity_type=new.entity_type and entity_id=new.entity_id and field_key=new.field_key
    and locale is not distinct from new.locale and id<>new.id
    and assertion_status in ('unreviewed','accepted','conflicting') and value_jsonb<>new.value_jsonb limit 1;
  if v_other is null then return new; end if;
  new.assertion_status:='conflicting'; new.reviewed_by:=null; new.reviewed_at:=null;
  update public.entity_assertions set assertion_status='conflicting',reviewed_by=null,reviewed_at=null where id=v_other;
  select id into v_conflict from public.assertion_conflicts where entity_type=new.entity_type and entity_id=new.entity_id and field_key=new.field_key and locale is not distinct from new.locale and status='open';
  if v_conflict is null then insert into public.assertion_conflicts(entity_type,entity_id,field_key,locale) values(new.entity_type,new.entity_id,new.field_key,new.locale) returning id into v_conflict; end if;
  insert into public.assertion_conflict_members(conflict_id,assertion_id) values(v_conflict,v_other) on conflict do nothing;
  return new;
end $$;
create trigger entity_assertions_detect_conflict before insert or update of value_jsonb,assertion_status on public.entity_assertions for each row execute function private.detect_assertion_conflict();
create function private.attach_assertion_conflict()
returns trigger language plpgsql security definer set search_path='' as $$
begin
  if new.assertion_status='conflicting' then
    insert into public.assertion_conflict_members(conflict_id,assertion_id)
    select id,new.id from public.assertion_conflicts where entity_type=new.entity_type and entity_id=new.entity_id and field_key=new.field_key and locale is not distinct from new.locale and status='open'
    on conflict do nothing;
  end if;
  return new;
end $$;
create trigger entity_assertions_attach_conflict after insert or update of assertion_status on public.entity_assertions for each row execute function private.attach_assertion_conflict();

create function public.institution_readiness(institution_id uuid)
returns jsonb language sql stable security invoker set search_path='' as $$
  with facts as (
    select i.id,
      exists(select 1 from public.campuses c where c.institution_id=i.id and c.status='active') has_campus,
      exists(select 1 from public.entity_assertions a where a.entity_type='institution' and a.entity_id=i.id and a.assertion_status='accepted') has_evidence,
      exists(select 1 from public.institution_localizations l where l.institution_id=i.id and l.locale='en-EG' and nullif(trim(l.summary),'') is not null) has_en,
      exists(select 1 from public.institution_localizations l where l.institution_id=i.id and l.locale='ar-EG' and nullif(trim(l.summary),'') is not null) has_ar,
      exists(select 1 from public.assertion_conflicts c where c.entity_type='institution' and c.entity_id=i.id and c.status='open') has_conflict
    from public.institutions i where i.id=institution_id
  ) select jsonb_build_object(
    'record_exists',id is not null,
    'public_ready',has_campus and has_evidence and not has_conflict,
    'index_ready',has_campus and has_evidence and has_en and has_ar and not has_conflict,
    'reasons',to_jsonb(array_remove(array[
      case when not has_campus then 'missing_active_campus' end,
      case when not has_evidence then 'missing_accepted_evidence' end,
      case when not has_en then 'missing_english_summary' end,
      case when not has_ar then 'missing_arabic_summary' end,
      case when has_conflict then 'open_critical_conflict' end
    ],null))
  ) from facts;
$$;
revoke all on function public.institution_readiness(uuid) from public,anon;
grant execute on function public.institution_readiness(uuid) to authenticated;

insert into public.freshness_policies(entity_type,field_key,review_interval_days,due_soon_days,priority,notes) values
('institution','official_website_url',180,30,'normal','Official website availability'),
('institution','founded_year',3650,90,'low','Effectively permanent, periodic sanity review'),
('institution','curricula',365,30,'high','Curriculum offering'),
('institution','education_levels',365,30,'high','Education levels'),
('campus','address',180,30,'normal','Campus address');

insert into public.completeness_requirements(stage,field_key,critical) values
('public','name',true),('public','institution_type',true),('public','governorate',true),('public','campus',true),('public','official_source',true),('public','education_levels',true),
('indexable','english_content',true),('indexable','arabic_content',true),('indexable','source_backed_key_facts',true),('indexable','no_critical_conflict',true),('indexable','no_critical_stale_field',true);
