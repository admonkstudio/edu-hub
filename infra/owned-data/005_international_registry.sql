-- EDU-DATA-2 international education registry
-- Depends on 001_raw_archive.sql and 004_national_registry_layers.sql.
--
-- This migration narrows active product scope to international/private education
-- in Egypt while preserving the source -> staging -> core evidence boundary.
-- Historical national-registry data is not deleted and is not auto-promoted.

create extension if not exists pgcrypto;
create extension if not exists postgis;

-- ---------------------------------------------------------------------------
-- International scope / eligibility
-- ---------------------------------------------------------------------------

create table if not exists edu_core.international_eligibility (
  edu_hub_id uuid primary key references edu_core.institutions(edu_hub_id) on delete cascade,
  scope_state text not null default 'candidate'
    check (scope_state in ('candidate','eligible','excluded','needs_review')),
  scope_class text
    check (scope_class in (
      'international_school',
      'foreign_university_branch',
      'international_independent_university',
      'international_early_years',
      'other_international'
    )),
  ownership_scope text not null default 'unknown'
    check (ownership_scope in ('private_independent','foreign_mission','public','unknown')),
  strongest_evidence_class text
    check (strongest_evidence_class in (
      'international_authorizer',
      'foreign_government',
      'egyptian_regulator',
      'recognized_accreditor',
      'official_institution',
      'supporting_source',
      'unknown'
    )),
  eligibility_note text,
  reviewed_at timestamptz,
  reviewed_by text,
  updated_at timestamptz not null default now()
);

create index if not exists international_eligibility_state_idx
  on edu_core.international_eligibility(scope_state, scope_class);

create table if not exists edu_core.international_scope_evidence (
  scope_evidence_id bigint generated always as identity primary key,
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  raw_id bigint references edu_raw.raw_records(raw_id),
  evidence_code text not null,
  evidence_class text not null
    check (evidence_class in (
      'international_authorizer',
      'foreign_government',
      'egyptian_regulator',
      'recognized_accreditor',
      'official_institution',
      'supporting_source'
    )),
  evidence_value text,
  source_url text,
  observed_at timestamptz not null default now(),
  valid_from date,
  valid_to date,
  supports_eligibility boolean not null default true,
  notes text,
  unique (edu_hub_id, evidence_code, source_url, evidence_value)
);

create index if not exists international_scope_evidence_institution_idx
  on edu_core.international_scope_evidence(edu_hub_id, evidence_class);

-- ---------------------------------------------------------------------------
-- Provider / group identity and bilingual institution content
-- ---------------------------------------------------------------------------

create table if not exists edu_core.providers (
  provider_id uuid primary key default gen_random_uuid(),
  provider_type text not null default 'operator'
    check (provider_type in ('operator','school_group','university_operator','foreign_parent_university','foundation','other')),
  official_name text not null,
  website_url text,
  lifecycle_status text not null default 'active'
    check (lifecycle_status in ('active','inactive','closed','unknown')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists edu_core.provider_localizations (
  provider_id uuid not null references edu_core.providers(provider_id) on delete cascade,
  locale text not null check (locale in ('ar-EG','en-EG')),
  name text not null,
  description text,
  slug text,
  primary key (provider_id, locale),
  unique (locale, slug)
);

alter table edu_core.institutions
  add column if not exists provider_id uuid references edu_core.providers(provider_id),
  add column if not exists official_website_url text,
  add column if not exists founded_year smallint,
  add column if not exists publication_status text not null default 'draft',
  add column if not exists merged_into_id uuid references edu_core.institutions(edu_hub_id);

create table if not exists edu_core.institution_localizations (
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  locale text not null check (locale in ('ar-EG','en-EG')),
  name text not null,
  short_name text,
  alternate_names jsonb not null default '[]'::jsonb,
  summary text,
  description text,
  slug text,
  seo_title text,
  seo_description text,
  primary key (edu_hub_id, locale),
  unique (locale, slug)
);

create index if not exists institutions_provider_idx on edu_core.institutions(provider_id);
create index if not exists institutions_publication_idx on edu_core.institutions(publication_status, data_status);

-- ---------------------------------------------------------------------------
-- Geography and campuses
-- ---------------------------------------------------------------------------

create table if not exists edu_core.locations (
  location_id uuid primary key default gen_random_uuid(),
  parent_id uuid references edu_core.locations(location_id),
  country_code char(2) not null default 'EG',
  location_type text not null
    check (location_type in ('country','governorate','city','district','area','neighborhood')),
  official_code text,
  name_en text,
  name_ar text,
  slug_en text,
  slug_ar text,
  centroid geography(point,4326),
  status text not null default 'active'
    check (status in ('active','historical','unknown')),
  check (name_en is not null or name_ar is not null)
);

create index if not exists locations_parent_idx on edu_core.locations(parent_id);
create index if not exists locations_country_type_idx on edu_core.locations(country_code, location_type);
create index if not exists locations_centroid_gist on edu_core.locations using gist(centroid);

create table if not exists edu_core.campuses (
  campus_id uuid primary key default gen_random_uuid(),
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  location_id uuid references edu_core.locations(location_id),
  canonical_name_en text,
  canonical_name_ar text,
  is_main boolean not null default false,
  address_en text,
  address_ar text,
  postal_code text,
  coordinates geography(point,4326),
  latitude double precision,
  longitude double precision,
  lifecycle_status text not null default 'active'
    check (lifecycle_status in ('active','inactive','closed','planned','unknown')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (
    (latitude is null and longitude is null)
    or (latitude between -90 and 90 and longitude between -180 and 180)
  )
);

create index if not exists campuses_institution_idx on edu_core.campuses(edu_hub_id, is_main);
create index if not exists campuses_location_idx on edu_core.campuses(location_id);
create index if not exists campuses_coordinates_gist on edu_core.campuses using gist(coordinates);

-- ---------------------------------------------------------------------------
-- Controlled international education taxonomies
-- ---------------------------------------------------------------------------

create table if not exists edu_core.curricula (
  curriculum_id uuid primary key default gen_random_uuid(),
  code text not null unique,
  label_en text not null,
  label_ar text,
  issuing_country_code char(2),
  authority_name text,
  status text not null default 'active'
);

create table if not exists edu_core.certificates (
  certificate_id uuid primary key default gen_random_uuid(),
  code text not null unique,
  label_en text not null,
  label_ar text,
  awarding_body text,
  status text not null default 'active'
);

create table if not exists edu_core.languages (
  language_code text primary key,
  label_en text not null,
  label_ar text,
  status text not null default 'active'
);

create table if not exists edu_core.accreditation_bodies (
  accreditation_body_id uuid primary key default gen_random_uuid(),
  code text not null unique,
  official_name text not null,
  country_code char(2),
  website_url text,
  body_type text not null
    check (body_type in ('international_authorizer','government','regulator','institutional_accreditor','programmatic_accreditor','exam_board','other')),
  status text not null default 'active'
);

create table if not exists edu_core.institution_curricula (
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  curriculum_id uuid not null references edu_core.curricula(curriculum_id),
  campus_id uuid references edu_core.campuses(campus_id) on delete cascade,
  valid_from date,
  valid_to date,
  raw_id bigint references edu_raw.raw_records(raw_id),
  verification_status text not null default 'sourced'
    check (verification_status in ('candidate','sourced','verified','expired','rejected')),
  primary key (edu_hub_id, curriculum_id, campus_id)
);

create table if not exists edu_core.institution_certificates (
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  certificate_id uuid not null references edu_core.certificates(certificate_id),
  campus_id uuid references edu_core.campuses(campus_id) on delete cascade,
  raw_id bigint references edu_raw.raw_records(raw_id),
  verification_status text not null default 'sourced',
  primary key (edu_hub_id, certificate_id, campus_id)
);

create table if not exists edu_core.institution_languages (
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  language_code text not null references edu_core.languages(language_code),
  campus_id uuid references edu_core.campuses(campus_id) on delete cascade,
  role text not null default 'instruction'
    check (role in ('instruction','additional','administration','other')),
  raw_id bigint references edu_raw.raw_records(raw_id),
  primary key (edu_hub_id, language_code, campus_id, role)
);

create table if not exists edu_core.institution_accreditations (
  institution_accreditation_id bigint generated always as identity primary key,
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  campus_id uuid references edu_core.campuses(campus_id) on delete cascade,
  accreditation_body_id uuid not null references edu_core.accreditation_bodies(accreditation_body_id),
  accreditation_type text not null default 'institutional',
  external_identifier text,
  status text not null default 'active'
    check (status in ('candidate','active','expired','withdrawn','rejected','unknown')),
  valid_from date,
  valid_to date,
  source_url text,
  raw_id bigint references edu_raw.raw_records(raw_id),
  observed_at timestamptz not null default now(),
  unique (edu_hub_id, campus_id, accreditation_body_id, external_identifier)
);

-- Seed stable cross-source taxonomy values. These are labels, not assertions
-- that any particular institution offers them.
insert into edu_core.curricula(code,label_en,label_ar,issuing_country_code,authority_name)
values
  ('ib','International Baccalaureate','البكالوريا الدولية',null,'International Baccalaureate Organization'),
  ('british','British Curriculum','المنهج البريطاني','GB',null),
  ('american','American Curriculum','المنهج الأمريكي','US',null),
  ('french','French Curriculum','المنهج الفرنسي','FR','Ministère de l’Éducation nationale'),
  ('german','German Curriculum','المنهج الألماني','DE','Kultusministerkonferenz / ZfA'),
  ('canadian','Canadian Curriculum','المنهج الكندي','CA',null)
on conflict (code) do nothing;

insert into edu_core.languages(language_code,label_en,label_ar)
values
  ('ar','Arabic','العربية'),
  ('en','English','الإنجليزية'),
  ('fr','French','الفرنسية'),
  ('de','German','الألمانية')
on conflict (language_code) do nothing;

insert into edu_core.accreditation_bodies(code,official_name,country_code,website_url,body_type)
values
  ('ib','International Baccalaureate Organization',null,'https://ibo.org/','international_authorizer'),
  ('scu','Supreme Council of Universities','EG','https://scu.eg/','regulator'),
  ('mohesr','Ministry of Higher Education and Scientific Research','EG','https://mohesr.gov.eg/','government'),
  ('cognia','Cognia','US','https://www.cognia.org/','institutional_accreditor'),
  ('msche','Middle States Commission on Higher Education','US','https://www.msche.org/','institutional_accreditor'),
  ('kmk','Kultusministerkonferenz','DE','https://www.kmk.org/','government'),
  ('french_men','French Ministry of National Education','FR','https://www.education.gouv.fr/','government'),
  ('british_council','British Council','GB','https://www.britishcouncil.org.eg/','exam_board')
on conflict (code) do nothing;

-- ---------------------------------------------------------------------------
-- Contacts, admissions and fees
-- ---------------------------------------------------------------------------

create table if not exists edu_core.entity_contacts (
  contact_id bigint generated always as identity primary key,
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  campus_id uuid references edu_core.campuses(campus_id) on delete cascade,
  contact_type text not null
    check (contact_type in ('phone','mobile','email','website','admissions_url','facebook','instagram','linkedin','youtube','tiktok','whatsapp','other')),
  value text not null,
  label text,
  is_primary boolean not null default false,
  is_official boolean not null default false,
  raw_id bigint references edu_raw.raw_records(raw_id),
  observed_at timestamptz not null default now(),
  valid_to date,
  unique (edu_hub_id, campus_id, contact_type, value)
);

create index if not exists entity_contacts_institution_idx on edu_core.entity_contacts(edu_hub_id, contact_type);

create table if not exists edu_core.fee_schedules (
  fee_schedule_id uuid primary key default gen_random_uuid(),
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  campus_id uuid references edu_core.campuses(campus_id) on delete cascade,
  academic_year text not null,
  currency_code char(3) not null,
  valid_from date,
  valid_to date,
  source_url text,
  raw_id bigint references edu_raw.raw_records(raw_id),
  verification_status text not null default 'sourced'
    check (verification_status in ('candidate','sourced','verified','stale','rejected')),
  retrieved_at timestamptz not null default now(),
  unique (edu_hub_id, campus_id, academic_year, currency_code, source_url)
);

create table if not exists edu_core.fee_items (
  fee_item_id bigint generated always as identity primary key,
  fee_schedule_id uuid not null references edu_core.fee_schedules(fee_schedule_id) on delete cascade,
  level_or_program_label text,
  fee_type text not null,
  amount_exact numeric(14,2),
  amount_min numeric(14,2),
  amount_max numeric(14,2),
  frequency text,
  mandatory boolean,
  notes text,
  check (amount_exact is not null or amount_min is not null or amount_max is not null)
);

create table if not exists edu_core.admission_cycles (
  admission_cycle_id uuid primary key default gen_random_uuid(),
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  campus_id uuid references edu_core.campuses(campus_id) on delete cascade,
  academic_year text not null,
  opens_on date,
  closes_on date,
  application_status text
    check (application_status in ('open','closed','rolling','upcoming','unknown')),
  application_url text,
  notes text,
  raw_id bigint references edu_raw.raw_records(raw_id),
  observed_at timestamptz not null default now(),
  unique (edu_hub_id, campus_id, academic_year, application_url)
);

-- ---------------------------------------------------------------------------
-- Higher-education structure
-- ---------------------------------------------------------------------------

create table if not exists edu_core.academic_units (
  academic_unit_id uuid primary key default gen_random_uuid(),
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  parent_academic_unit_id uuid references edu_core.academic_units(academic_unit_id),
  unit_type text not null
    check (unit_type in ('faculty','college','school','institute','department','center','other')),
  official_name text not null,
  lifecycle_status text not null default 'active',
  source_url text,
  raw_id bigint references edu_raw.raw_records(raw_id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists academic_units_institution_idx on edu_core.academic_units(edu_hub_id, unit_type);

create table if not exists edu_core.programs (
  program_id uuid primary key default gen_random_uuid(),
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  academic_unit_id uuid references edu_core.academic_units(academic_unit_id) on delete set null,
  campus_id uuid references edu_core.campuses(campus_id) on delete set null,
  official_name text not null,
  degree_level text,
  awarding_institution_name text,
  study_mode text,
  duration_text text,
  application_url text,
  lifecycle_status text not null default 'active',
  source_url text,
  raw_id bigint references edu_raw.raw_records(raw_id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists programs_institution_idx on edu_core.programs(edu_hub_id, degree_level);

-- ---------------------------------------------------------------------------
-- Media rights hardening
-- ---------------------------------------------------------------------------

alter table edu_raw.media_assets
  add column if not exists license_name text,
  add column if not exists license_url text,
  add column if not exists creator_name text,
  add column if not exists attribution_text text,
  add column if not exists rights_evidence_url text;

-- Only publication-reviewed media can enter the public-safe core link table.
-- Institution-site images may still be preserved in edu_raw as candidates with
-- public_use_allowed=false.

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conname = 'institution_media_rights_basis_required'
      and conrelid = 'edu_core.institution_media'::regclass
  ) then
    alter table edu_core.institution_media
      add constraint institution_media_rights_basis_required
      check (public_use_allowed = false or rights_basis is not null);
  end if;
end $$;

comment on table edu_core.international_eligibility is
  'EDU-DATA-2 scope gate. Historical/public-school records may remain in raw/staging but are not active unless scope_state=eligible.';

comment on table edu_core.international_scope_evidence is
  'Source-backed evidence establishing or rejecting international-education eligibility.';

revoke all on schema edu_core from public;
