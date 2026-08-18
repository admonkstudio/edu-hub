create extension if not exists postgis schema extensions;
create extension if not exists pgcrypto schema extensions;

create schema if not exists private;
revoke all on schema private from public, anon, authenticated;

create function private.set_updated_at()
returns trigger language plpgsql security invoker set search_path = '' as $$
begin new.updated_at = now(); return new; end;
$$;

create table public.staff_users (
  user_id uuid primary key references auth.users(id) on delete cascade,
  role text not null check (role in ('admin','editor')),
  status text not null default 'active' check (status in ('active','suspended')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create function private.is_internal_user()
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (
    select 1 from public.staff_users
    where user_id = (select auth.uid()) and status = 'active'
  );
$$;
revoke all on function private.is_internal_user() from public;
grant execute on function private.is_internal_user() to anon, authenticated, service_role;

create table public.institution_types (
  id uuid primary key default gen_random_uuid(), code text not null unique,
  label_en text not null, label_ar text not null, slug_en text not null unique, slug_ar text not null unique,
  status text not null default 'active' check (status in ('active','inactive')), sort_order integer not null default 0
);
create table public.ownership_types (like public.institution_types including all);
create table public.education_models (like public.institution_types including all);
create table public.education_levels (like public.institution_types including all);
create table public.curricula (like public.institution_types including all);
create table public.certificates (like public.institution_types including all);
create table public.languages (like public.institution_types including all);
create table public.accreditation_bodies (like public.institution_types including all);
create table public.facilities (like public.institution_types including all);

create table public.providers (
  id uuid primary key default gen_random_uuid(),
  provider_type text not null default 'organization' check (provider_type in ('organization','group','government','foundation','company','individual')),
  official_name text not null, website_url text,
  status text not null default 'active' check (status in ('active','inactive','archived')),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  check (website_url is null or website_url ~ '^https?://')
);
create table public.provider_localizations (
  provider_id uuid not null references public.providers(id) on delete cascade,
  locale text not null check (locale in ('en-EG','ar-EG')),
  name text not null, description text, slug text not null,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  primary key (provider_id, locale), unique (locale, slug)
);

create table public.locations (
  id uuid primary key default gen_random_uuid(), parent_id uuid references public.locations(id) on delete restrict,
  country_code char(2) not null, location_type text not null check (location_type in ('country','governorate','city','district','area','neighborhood')),
  official_code text, name_en text not null, name_ar text not null, slug_en text not null, slug_ar text not null,
  coordinates extensions.geography(point,4326), status text not null default 'active' check (status in ('active','inactive')),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  check (parent_id is null or parent_id <> id), unique nulls not distinct (country_code, location_type, official_code),
  unique (parent_id, slug_en), unique (parent_id, slug_ar)
);

create table public.institutions (
  id uuid primary key default gen_random_uuid(), provider_id uuid references public.providers(id) on delete set null,
  institution_type_id uuid not null references public.institution_types(id) on delete restrict,
  ownership_type_id uuid references public.ownership_types(id) on delete restrict,
  education_model_id uuid references public.education_models(id) on delete restrict,
  official_name text not null, official_website_url text, founded_year integer,
  publication_status text not null default 'draft' check (publication_status in ('draft','public_noindex','index_ready','published','archived','redirected')),
  data_status text not null default 'candidate' check (data_status in ('candidate','researching','sourced','reviewed','officially_sourced','institution_confirmed','conflicting','stale','disputed')),
  claim_status text not null default 'unclaimed' check (claim_status in ('unclaimed','claim_requested','verification_pending','claimed','suspended')),
  commercial_status text not null default 'free' check (commercial_status in ('free','premium','sponsored','partner')),
  merged_into_id uuid references public.institutions(id) on delete restrict,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  check (official_website_url is null or official_website_url ~ '^https?://'),
  check (founded_year is null or founded_year between 900 and extract(year from current_date)::integer),
  check (merged_into_id is null or merged_into_id <> id),
  check ((publication_status = 'redirected') = (merged_into_id is not null))
);
create table public.institution_localizations (
  institution_id uuid not null references public.institutions(id) on delete cascade,
  locale text not null check (locale in ('en-EG','ar-EG')), name text not null, short_name text,
  alternate_names text[] not null default '{}', summary text, description text, slug text not null,
  seo_title text, seo_description text, created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  primary key (institution_id, locale), unique (locale, slug)
);
create table public.campuses (
  id uuid primary key default gen_random_uuid(), institution_id uuid not null references public.institutions(id) on delete cascade,
  location_id uuid not null references public.locations(id) on delete restrict, name text not null, is_main boolean not null default false,
  address_en text, address_ar text, postal_code text, coordinates extensions.geography(point,4326),
  status text not null default 'active' check (status in ('active','inactive','closed')),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create unique index campuses_one_main_per_institution on public.campuses(institution_id) where is_main;
create index campuses_coordinates_gist on public.campuses using gist(coordinates);
create index locations_coordinates_gist on public.locations using gist(coordinates);

create table public.institution_education_levels (institution_id uuid references public.institutions(id) on delete cascade, education_level_id uuid references public.education_levels(id) on delete restrict, valid_from date, valid_to date, primary key(institution_id,education_level_id), check(valid_to is null or valid_from is null or valid_to >= valid_from));
create table public.institution_curricula (institution_id uuid references public.institutions(id) on delete cascade, curriculum_id uuid references public.curricula(id) on delete restrict, valid_from date, valid_to date, primary key(institution_id,curriculum_id), check(valid_to is null or valid_from is null or valid_to >= valid_from));
create table public.institution_certificates (institution_id uuid references public.institutions(id) on delete cascade, certificate_id uuid references public.certificates(id) on delete restrict, primary key(institution_id,certificate_id));
create table public.institution_languages (institution_id uuid references public.institutions(id) on delete cascade, language_id uuid references public.languages(id) on delete restrict, primary key(institution_id,language_id));
create table public.institution_accreditations (institution_id uuid references public.institutions(id) on delete cascade, accreditation_body_id uuid references public.accreditation_bodies(id) on delete restrict, valid_from date, valid_to date, primary key(institution_id,accreditation_body_id), check(valid_to is null or valid_from is null or valid_to >= valid_from));
create table public.campus_facilities (campus_id uuid references public.campuses(id) on delete cascade, facility_id uuid references public.facilities(id) on delete restrict, primary key(campus_id,facility_id));

create index institutions_provider_id_idx on public.institutions(provider_id);
create index institutions_type_status_idx on public.institutions(institution_type_id,publication_status);
create index institutions_ownership_type_id_idx on public.institutions(ownership_type_id) where ownership_type_id is not null;
create index institutions_education_model_id_idx on public.institutions(education_model_id) where education_model_id is not null;
create index institutions_data_status_idx on public.institutions(data_status);
create index institutions_merged_into_id_idx on public.institutions(merged_into_id) where merged_into_id is not null;
create index locations_parent_id_idx on public.locations(parent_id);
create index locations_type_status_idx on public.locations(location_type,status);
create index campuses_institution_id_idx on public.campuses(institution_id);
create index campuses_location_id_idx on public.campuses(location_id);

do $$ declare table_name text; begin
  foreach table_name in array array['staff_users','providers','provider_localizations','locations','institutions','institution_localizations','campuses','institution_types','ownership_types','education_models','education_levels','curricula','certificates','languages','accreditation_bodies','facilities','institution_education_levels','institution_curricula','institution_certificates','institution_languages','institution_accreditations','campus_facilities'] loop
    execute format('alter table public.%I enable row level security', table_name);
    execute format('grant all on public.%I to service_role', table_name);
  end loop;
end $$;

grant select on public.institution_types, public.ownership_types, public.education_models, public.education_levels, public.curricula, public.certificates, public.languages, public.accreditation_bodies, public.facilities, public.locations to anon, authenticated;
grant select on public.staff_users to authenticated;
grant select on public.providers, public.provider_localizations, public.institutions, public.institution_localizations, public.campuses, public.institution_education_levels, public.institution_curricula, public.institution_certificates, public.institution_languages, public.institution_accreditations, public.campus_facilities to anon, authenticated;
grant insert, update, delete on all tables in schema public to authenticated;

create policy staff_read_self on public.staff_users for select to authenticated using (user_id = (select auth.uid()) or (select private.is_internal_user()));

do $$ declare table_name text; begin
  foreach table_name in array array['institution_types','ownership_types','education_models','education_levels','curricula','certificates','languages','accreditation_bodies','facilities','locations'] loop
    execute format('create policy %I on public.%I for select to anon, authenticated using (status = ''active'' or (select private.is_internal_user()))', table_name || '_public_read', table_name);
    execute format('create policy %I on public.%I for insert to authenticated with check ((select private.is_internal_user()))', table_name || '_staff_insert', table_name);
    execute format('create policy %I on public.%I for update to authenticated using ((select private.is_internal_user())) with check ((select private.is_internal_user()))', table_name || '_staff_update', table_name);
    execute format('create policy %I on public.%I for delete to authenticated using ((select private.is_internal_user()))', table_name || '_staff_delete', table_name);
  end loop;
end $$;
create policy providers_public_read on public.providers for select to anon, authenticated using ((status = 'active' and exists(select 1 from public.institutions i where i.provider_id=providers.id and i.publication_status in ('public_noindex','index_ready','published'))) or (select private.is_internal_user()));
create policy providers_staff_insert on public.providers for insert to authenticated with check ((select private.is_internal_user()));
create policy providers_staff_update on public.providers for update to authenticated using ((select private.is_internal_user())) with check ((select private.is_internal_user()));
create policy providers_staff_delete on public.providers for delete to authenticated using ((select private.is_internal_user()));
create policy provider_localizations_public_read on public.provider_localizations for select to anon, authenticated using (exists(select 1 from public.providers p where p.id=provider_id and p.status='active') or (select private.is_internal_user()));
create policy provider_localizations_staff_insert on public.provider_localizations for insert to authenticated with check ((select private.is_internal_user()));
create policy provider_localizations_staff_update on public.provider_localizations for update to authenticated using ((select private.is_internal_user())) with check ((select private.is_internal_user()));
create policy provider_localizations_staff_delete on public.provider_localizations for delete to authenticated using ((select private.is_internal_user()));
create policy institutions_public_read on public.institutions for select to anon, authenticated using (publication_status in ('public_noindex','index_ready','published') or (select private.is_internal_user()));
create policy institutions_staff_insert on public.institutions for insert to authenticated with check ((select private.is_internal_user()));
create policy institutions_staff_update on public.institutions for update to authenticated using ((select private.is_internal_user())) with check ((select private.is_internal_user()));
create policy institutions_staff_delete on public.institutions for delete to authenticated using ((select private.is_internal_user()));
create policy institution_localizations_public_read on public.institution_localizations for select to anon, authenticated using (exists(select 1 from public.institutions i where i.id=institution_id and i.publication_status in ('public_noindex','index_ready','published')) or (select private.is_internal_user()));
create policy institution_localizations_staff_insert on public.institution_localizations for insert to authenticated with check ((select private.is_internal_user()));
create policy institution_localizations_staff_update on public.institution_localizations for update to authenticated using ((select private.is_internal_user())) with check ((select private.is_internal_user()));
create policy institution_localizations_staff_delete on public.institution_localizations for delete to authenticated using ((select private.is_internal_user()));
create policy campuses_public_read on public.campuses for select to anon, authenticated using (exists(select 1 from public.institutions i where i.id=institution_id and i.publication_status in ('public_noindex','index_ready','published')) or (select private.is_internal_user()));
create policy campuses_staff_insert on public.campuses for insert to authenticated with check ((select private.is_internal_user()));
create policy campuses_staff_update on public.campuses for update to authenticated using ((select private.is_internal_user())) with check ((select private.is_internal_user()));
create policy campuses_staff_delete on public.campuses for delete to authenticated using ((select private.is_internal_user()));

do $$ declare table_name text; begin
  foreach table_name in array array['institution_education_levels','institution_curricula','institution_certificates','institution_languages','institution_accreditations'] loop
    execute format('create policy %I on public.%I for select to anon, authenticated using (exists(select 1 from public.institutions i where i.id=institution_id and i.publication_status in (''public_noindex'',''index_ready'',''published'')) or (select private.is_internal_user()))', table_name || '_public_read', table_name);
    execute format('create policy %I on public.%I for insert to authenticated with check ((select private.is_internal_user()))', table_name || '_staff_insert', table_name);
    execute format('create policy %I on public.%I for update to authenticated using ((select private.is_internal_user())) with check ((select private.is_internal_user()))', table_name || '_staff_update', table_name);
    execute format('create policy %I on public.%I for delete to authenticated using ((select private.is_internal_user()))', table_name || '_staff_delete', table_name);
  end loop;
end $$;
create policy campus_facilities_public_read on public.campus_facilities for select to anon, authenticated using (exists(select 1 from public.campuses c join public.institutions i on i.id=c.institution_id where c.id=campus_id and i.publication_status in ('public_noindex','index_ready','published')) or (select private.is_internal_user()));
create policy campus_facilities_staff_insert on public.campus_facilities for insert to authenticated with check ((select private.is_internal_user()));
create policy campus_facilities_staff_update on public.campus_facilities for update to authenticated using ((select private.is_internal_user())) with check ((select private.is_internal_user()));
create policy campus_facilities_staff_delete on public.campus_facilities for delete to authenticated using ((select private.is_internal_user()));

do $$ declare table_name text; begin
  foreach table_name in array array['staff_users','providers','provider_localizations','locations','institutions','institution_localizations','campuses'] loop
    execute format('create trigger %I before update on public.%I for each row execute function private.set_updated_at()', table_name || '_set_updated_at', table_name);
  end loop;
end $$;
