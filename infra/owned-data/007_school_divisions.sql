-- EDU-DATA-2 pre-university school-division / curriculum-stream layer
-- Depends on 001_raw_archive.sql, 004_national_registry_layers.sql,
-- 005_international_registry.sql and 006_bilingual_completion.sql.
--
-- Evidence from institutions such as Misr Language Schools and El Alsson shows
-- that one canonical institution/campus can operate distinct British, American,
-- French, IB or other sections with section-specific authorization, admissions,
-- contacts and fees. Flattening those sections into separate institutions would
-- create false duplicates; flattening their accreditation onto the whole
-- institution would overstate the scope of the evidence.
--
-- This migration therefore introduces a first-class school_division entity while
-- keeping institution and campus as the stable identity/geography layers.

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- Division identity and bilingual representation
-- ---------------------------------------------------------------------------

create table if not exists edu_core.school_divisions (
  school_division_id uuid primary key default gen_random_uuid(),
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  campus_id uuid references edu_core.campuses(campus_id) on delete cascade,
  parent_school_division_id uuid references edu_core.school_divisions(school_division_id) on delete set null,
  division_type text not null default 'curriculum_stream'
    check (division_type in (
      'curriculum_stream','language_stream','phase_section','special_education',
      'early_years_section','other'
    )),
  canonical_name_en text,
  canonical_name_ar text,
  lifecycle_status text not null default 'active'
    check (lifecycle_status in ('active','inactive','closed','planned','unknown')),
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  observed_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (canonical_name_en is not null or canonical_name_ar is not null)
);

create index if not exists school_divisions_institution_idx
  on edu_core.school_divisions(edu_hub_id, division_type, lifecycle_status);
create index if not exists school_divisions_campus_idx
  on edu_core.school_divisions(campus_id, lifecycle_status);

create table if not exists edu_core.school_division_localizations (
  school_division_id uuid not null references edu_core.school_divisions(school_division_id) on delete cascade,
  locale text not null check (locale in ('ar-EG','en-EG')),
  name text not null,
  description text,
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  localization_origin text not null default 'official_source'
    check (localization_origin in (
      'official_source','institution_source','verified_translation',
      'editorial_translation','transliteration','source_variant','needs_review'
    )),
  review_status text not null default 'unreviewed'
    check (review_status in ('unreviewed','verified','needs_review','rejected','superseded')),
  observed_at timestamptz not null default now(),
  reviewed_at timestamptz,
  reviewed_by text,
  primary key (school_division_id, locale)
);

create table if not exists edu_core.school_division_aliases (
  school_division_alias_id bigint generated always as identity primary key,
  school_division_id uuid not null references edu_core.school_divisions(school_division_id) on delete cascade,
  locale text not null default 'und' check (locale in ('ar-EG','en-EG','und')),
  alias text not null,
  alias_type text not null default 'source_variant'
    check (alias_type in ('official_previous','abbreviation','source_variant','transliteration','spelling_variant','other')),
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  verification_status text not null default 'unreviewed'
    check (verification_status in ('unreviewed','verified','rejected','superseded')),
  observed_at timestamptz not null default now(),
  unique (school_division_id, locale, alias)
);

-- ---------------------------------------------------------------------------
-- Division-scoped academic / authorization relationships
-- ---------------------------------------------------------------------------

create table if not exists edu_core.school_division_curricula (
  school_division_id uuid not null references edu_core.school_divisions(school_division_id) on delete cascade,
  curriculum_id uuid not null references edu_core.curricula(curriculum_id),
  valid_from date,
  valid_to date,
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  verification_status text not null default 'sourced'
    check (verification_status in ('candidate','sourced','verified','expired','rejected')),
  observed_at timestamptz not null default now(),
  primary key (school_division_id, curriculum_id)
);

create table if not exists edu_core.school_division_certificates (
  school_division_id uuid not null references edu_core.school_divisions(school_division_id) on delete cascade,
  certificate_id uuid not null references edu_core.certificates(certificate_id),
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  verification_status text not null default 'sourced'
    check (verification_status in ('candidate','sourced','verified','expired','rejected')),
  observed_at timestamptz not null default now(),
  primary key (school_division_id, certificate_id)
);

create table if not exists edu_core.school_division_languages (
  school_division_id uuid not null references edu_core.school_divisions(school_division_id) on delete cascade,
  language_code text not null references edu_core.languages(language_code),
  role text not null default 'instruction'
    check (role in ('instruction','additional','administration','other')),
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  observed_at timestamptz not null default now(),
  primary key (school_division_id, language_code, role)
);

create table if not exists edu_core.school_division_accreditations (
  school_division_accreditation_id bigint generated always as identity primary key,
  school_division_id uuid not null references edu_core.school_divisions(school_division_id) on delete cascade,
  accreditation_body_id uuid not null references edu_core.accreditation_bodies(accreditation_body_id),
  accreditation_type text not null default 'institutional',
  external_identifier text,
  status text not null default 'active'
    check (status in ('candidate','active','expired','withdrawn','rejected','unknown')),
  valid_from date,
  valid_to date,
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  observed_at timestamptz not null default now()
);

create unique index if not exists school_division_accreditations_unique_idx
  on edu_core.school_division_accreditations(
    school_division_id,
    accreditation_body_id,
    coalesce(external_identifier, '')
  );

create table if not exists edu_core.school_division_level_offerings (
  school_division_level_offering_id bigint generated always as identity primary key,
  school_division_id uuid not null references edu_core.school_divisions(school_division_id) on delete cascade,
  education_level_id uuid not null references edu_core.education_levels(education_level_id),
  grade_from text,
  grade_to text,
  age_min_years numeric(4,1),
  age_max_years numeric(4,1),
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  verification_status text not null default 'sourced'
    check (verification_status in ('candidate','sourced','verified','expired','rejected')),
  observed_at timestamptz not null default now()
);

create unique index if not exists school_division_level_offerings_unique_idx
  on edu_core.school_division_level_offerings(
    school_division_id,
    education_level_id,
    coalesce(grade_from, ''),
    coalesce(grade_to, '')
  );

-- ---------------------------------------------------------------------------
-- Division-scoped contacts, admissions and fees
-- ---------------------------------------------------------------------------

create table if not exists edu_core.school_division_contacts (
  school_division_contact_id bigint generated always as identity primary key,
  school_division_id uuid not null references edu_core.school_divisions(school_division_id) on delete cascade,
  contact_type text not null
    check (contact_type in (
      'phone','mobile','email','website','admissions_url','facebook','instagram',
      'linkedin','youtube','tiktok','whatsapp','other'
    )),
  value text not null,
  label text,
  is_primary boolean not null default false,
  is_official boolean not null default false,
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  observed_at timestamptz not null default now(),
  valid_to date,
  unique (school_division_id, contact_type, value)
);

create table if not exists edu_core.school_division_admission_cycles (
  school_division_admission_cycle_id uuid primary key default gen_random_uuid(),
  school_division_id uuid not null references edu_core.school_divisions(school_division_id) on delete cascade,
  academic_year text not null,
  opens_on date,
  closes_on date,
  application_status text
    check (application_status in ('open','closed','rolling','upcoming','unknown')),
  application_url text,
  notes text,
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  observed_at timestamptz not null default now()
);

create unique index if not exists school_division_admission_cycles_unique_idx
  on edu_core.school_division_admission_cycles(
    school_division_id,
    academic_year,
    coalesce(application_url, '')
  );

create table if not exists edu_core.school_division_admission_requirements (
  school_division_admission_requirement_id uuid primary key default gen_random_uuid(),
  school_division_admission_cycle_id uuid references edu_core.school_division_admission_cycles(school_division_admission_cycle_id) on delete cascade,
  school_division_id uuid not null references edu_core.school_divisions(school_division_id) on delete cascade,
  requirement_type text not null
    check (requirement_type in (
      'document','assessment','interview','age','previous_grade','language',
      'application_fee','deposit','medical','other'
    )),
  required boolean,
  details_en text,
  details_ar text,
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  verification_status text not null default 'sourced'
    check (verification_status in ('candidate','sourced','verified','stale','rejected')),
  observed_at timestamptz not null default now()
);

create table if not exists edu_core.school_division_fee_schedules (
  school_division_fee_schedule_id uuid primary key default gen_random_uuid(),
  school_division_id uuid not null references edu_core.school_divisions(school_division_id) on delete cascade,
  academic_year text not null,
  currency_code char(3) not null,
  valid_from date,
  valid_to date,
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  verification_status text not null default 'sourced'
    check (verification_status in ('candidate','sourced','verified','stale','rejected')),
  retrieved_at timestamptz not null default now()
);

create unique index if not exists school_division_fee_schedules_unique_idx
  on edu_core.school_division_fee_schedules(
    school_division_id,
    academic_year,
    currency_code,
    coalesce(source_url, '')
  );

create table if not exists edu_core.school_division_fee_items (
  school_division_fee_item_id bigint generated always as identity primary key,
  school_division_fee_schedule_id uuid not null references edu_core.school_division_fee_schedules(school_division_fee_schedule_id) on delete cascade,
  level_or_program_label_en text,
  level_or_program_label_ar text,
  fee_type text not null,
  amount_exact numeric(14,2),
  amount_min numeric(14,2),
  amount_max numeric(14,2),
  frequency text,
  mandatory boolean,
  notes_en text,
  notes_ar text,
  check (amount_exact is not null or amount_min is not null or amount_max is not null)
);

-- ---------------------------------------------------------------------------
-- Division-level completion and evidence ledger support
-- ---------------------------------------------------------------------------

create table if not exists edu_core.school_division_completeness (
  school_division_id uuid primary key references edu_core.school_divisions(school_division_id) on delete cascade,
  identity_reviewed boolean not null default false,
  name_en_present boolean not null default false,
  name_ar_present boolean not null default false,
  curriculum_present boolean not null default false,
  accreditation_present boolean not null default false,
  level_grade_profile_present boolean not null default false,
  admissions_profile_present boolean not null default false,
  current_fee_profile_present boolean not null default false,
  contact_present boolean not null default false,
  unresolved_conflict_count integer not null default 0,
  factual_completeness_score numeric(6,5) not null default 0 check (factual_completeness_score between 0 and 1),
  english_completeness_score numeric(6,5) not null default 0 check (english_completeness_score between 0 and 1),
  arabic_completeness_score numeric(6,5) not null default 0 check (arabic_completeness_score between 0 and 1),
  evaluated_at timestamptz not null default now(),
  evaluator_version text not null
);

do $$
begin
  if exists (
    select 1 from pg_constraint
    where conname = 'evidence_assertions_subject_type_check'
      and conrelid = 'edu_core.evidence_assertions'::regclass
  ) then
    alter table edu_core.evidence_assertions
      drop constraint evidence_assertions_subject_type_check;
  end if;

  if not exists (
    select 1 from pg_constraint
    where conname = 'evidence_assertions_subject_type_check'
      and conrelid = 'edu_core.evidence_assertions'::regclass
  ) then
    alter table edu_core.evidence_assertions
      add constraint evidence_assertions_subject_type_check
      check (subject_type in (
        'provider','institution','campus','school_division','location','curriculum','certificate',
        'accreditation','contact','fee_schedule','fee_item','admission_cycle',
        'admission_requirement','academic_unit','program','facility','media','other'
      ));
  end if;
end $$;

insert into edu_core.accreditation_bodies(code,official_name,country_code,website_url,body_type)
values
  ('cis','Council of International Schools',null,'https://www.cois.org/','institutional_accreditor'),
  ('uk_dfe_bso','UK Department for Education - British Schools Overseas','GB','https://www.gov.uk/government/publications/british-schools-overseas-inspection-reports','government')
on conflict (code) do nothing;

comment on table edu_core.school_divisions is
  'Pre-university curriculum/language/phase section below institution/campus identity. Use when authorization, admissions, fees or curriculum evidence applies to a specific school section rather than the whole institution.';

comment on table edu_core.school_division_accreditations is
  'Accreditation/authorization evidence scoped to a school division, preventing French, American, British or IB section evidence from being overstated as institution-wide.';

revoke all on schema edu_core from public;
