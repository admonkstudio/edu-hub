-- EDU-DATA-2 bilingual database completion layer
-- Depends on 001_raw_archive.sql, 004_national_registry_layers.sql and
-- 005_international_registry.sql.
--
-- Purpose:
--   * make English and Arabic first-class without duplicating language-neutral facts
--   * extend provenance beyond institution-level assertions
--   * represent school stages/grades, facilities, admissions requirements and media captions
--   * provide explicit per-locale/per-domain completeness tracking
--
-- This remains a presentation-neutral relational reference model. It does not
-- imply a particular runtime/CMS/database provider.

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- Localization provenance and aliases
-- ---------------------------------------------------------------------------

alter table edu_core.provider_localizations
  add column if not exists source_raw_id bigint references edu_raw.raw_records(raw_id),
  add column if not exists source_url text,
  add column if not exists localization_origin text not null default 'official_source',
  add column if not exists review_status text not null default 'unreviewed',
  add column if not exists observed_at timestamptz not null default now(),
  add column if not exists reviewed_at timestamptz,
  add column if not exists reviewed_by text;

alter table edu_core.institution_localizations
  add column if not exists source_raw_id bigint references edu_raw.raw_records(raw_id),
  add column if not exists source_url text,
  add column if not exists localization_origin text not null default 'official_source',
  add column if not exists review_status text not null default 'unreviewed',
  add column if not exists observed_at timestamptz not null default now(),
  add column if not exists reviewed_at timestamptz,
  add column if not exists reviewed_by text;

do $$
begin
  if not exists (
    select 1 from pg_constraint where conname='provider_localizations_origin_check'
  ) then
    alter table edu_core.provider_localizations add constraint provider_localizations_origin_check
      check (localization_origin in (
        'official_source','institution_source','verified_translation',
        'editorial_translation','transliteration','source_variant','needs_review'
      ));
  end if;
  if not exists (
    select 1 from pg_constraint where conname='provider_localizations_review_check'
  ) then
    alter table edu_core.provider_localizations add constraint provider_localizations_review_check
      check (review_status in ('unreviewed','verified','needs_review','rejected','superseded'));
  end if;
  if not exists (
    select 1 from pg_constraint where conname='institution_localizations_origin_check'
  ) then
    alter table edu_core.institution_localizations add constraint institution_localizations_origin_check
      check (localization_origin in (
        'official_source','institution_source','verified_translation',
        'editorial_translation','transliteration','source_variant','needs_review'
      ));
  end if;
  if not exists (
    select 1 from pg_constraint where conname='institution_localizations_review_check'
  ) then
    alter table edu_core.institution_localizations add constraint institution_localizations_review_check
      check (review_status in ('unreviewed','verified','needs_review','rejected','superseded'));
  end if;
end $$;

create table if not exists edu_core.institution_aliases (
  alias_id bigint generated always as identity primary key,
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  locale text not null default 'und' check (locale in ('ar-EG','en-EG','und')),
  alias text not null,
  alias_type text not null default 'source_variant'
    check (alias_type in (
      'official_previous','abbreviation','source_variant','transliteration',
      'spelling_variant','campus_variant','other'
    )),
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  verification_status text not null default 'unreviewed'
    check (verification_status in ('unreviewed','verified','rejected','superseded')),
  is_searchable boolean not null default true,
  observed_at timestamptz not null default now(),
  unique (edu_hub_id, locale, alias)
);

create index if not exists institution_aliases_lookup_idx
  on edu_core.institution_aliases(locale, alias);

-- ---------------------------------------------------------------------------
-- Campus bilingual representation and source evidence
-- ---------------------------------------------------------------------------

alter table edu_core.campuses
  add column if not exists campus_type text,
  add column if not exists source_raw_id bigint references edu_raw.raw_records(raw_id),
  add column if not exists source_url text,
  add column if not exists observed_at timestamptz not null default now(),
  add column if not exists gender_model text,
  add column if not exists attendance_model text;

do $$
begin
  if not exists (select 1 from pg_constraint where conname='campuses_type_check') then
    alter table edu_core.campuses add constraint campuses_type_check
      check (campus_type is null or campus_type in (
        'main','branch','early_years','school_section','university_branch','other'
      ));
  end if;
  if not exists (select 1 from pg_constraint where conname='campuses_gender_model_check') then
    alter table edu_core.campuses add constraint campuses_gender_model_check
      check (gender_model is null or gender_model in ('coeducational','boys','girls','mixed_by_stage','unknown'));
  end if;
  if not exists (select 1 from pg_constraint where conname='campuses_attendance_model_check') then
    alter table edu_core.campuses add constraint campuses_attendance_model_check
      check (attendance_model is null or attendance_model in ('day','boarding','day_and_boarding','unknown'));
  end if;
end $$;

create table if not exists edu_core.campus_localizations (
  campus_id uuid not null references edu_core.campuses(campus_id) on delete cascade,
  locale text not null check (locale in ('ar-EG','en-EG')),
  name text,
  address text,
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
  primary key (campus_id, locale),
  check (name is not null or address is not null or description is not null)
);

-- ---------------------------------------------------------------------------
-- School levels / grades / ages
-- ---------------------------------------------------------------------------

create table if not exists edu_core.education_levels (
  education_level_id uuid primary key default gen_random_uuid(),
  code text not null unique,
  label_en text not null,
  label_ar text not null,
  family text not null
    check (family in ('early_years','primary','secondary','post_secondary','higher_education','other')),
  sort_order integer not null default 0,
  status text not null default 'active'
);

insert into edu_core.education_levels(code,label_en,label_ar,family,sort_order)
values
  ('pre_nursery','Pre-Nursery','ما قبل الحضانة','early_years',10),
  ('nursery','Nursery','الحضانة','early_years',20),
  ('kindergarten','Kindergarten / Early Years','رياض الأطفال / السنوات المبكرة','early_years',30),
  ('primary','Primary / Elementary','المرحلة الابتدائية','primary',40),
  ('middle','Middle / Lower Secondary','المرحلة الإعدادية / المتوسطة','secondary',50),
  ('secondary','Secondary / High School','المرحلة الثانوية','secondary',60),
  ('sixth_form','Sixth Form / Senior Secondary','المرحلة الثانوية العليا / Sixth Form','secondary',70),
  ('undergraduate','Undergraduate','البكالوريوس','higher_education',80),
  ('postgraduate','Postgraduate','الدراسات العليا','higher_education',90)
on conflict (code) do nothing;

create table if not exists edu_core.campus_level_offerings (
  campus_level_offering_id bigint generated always as identity primary key,
  campus_id uuid not null references edu_core.campuses(campus_id) on delete cascade,
  education_level_id uuid not null references edu_core.education_levels(education_level_id),
  curriculum_id uuid references edu_core.curricula(curriculum_id),
  grade_from text,
  grade_to text,
  age_min_years numeric(4,1),
  age_max_years numeric(4,1),
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  verification_status text not null default 'sourced'
    check (verification_status in ('candidate','sourced','verified','expired','rejected')),
  observed_at timestamptz not null default now(),
  unique (campus_id, education_level_id, curriculum_id, grade_from, grade_to)
);

-- ---------------------------------------------------------------------------
-- Facilities and student-support profile
-- ---------------------------------------------------------------------------

create table if not exists edu_core.facilities (
  facility_id uuid primary key default gen_random_uuid(),
  code text not null unique,
  label_en text not null,
  label_ar text not null,
  category text not null default 'general',
  status text not null default 'active'
);

insert into edu_core.facilities(code,label_en,label_ar,category)
values
  ('library','Library','مكتبة','academic'),
  ('science_labs','Science Laboratories','معامل علوم','academic'),
  ('computer_labs','Computer / Technology Laboratories','معامل حاسب / تكنولوجيا','academic'),
  ('sports_fields','Sports Fields','ملاعب رياضية','sports'),
  ('sports_hall','Indoor Sports Hall','صالة رياضية مغطاة','sports'),
  ('swimming_pool','Swimming Pool','حمام سباحة','sports'),
  ('theatre','Theatre / Auditorium','مسرح / قاعة عروض','arts'),
  ('music_rooms','Music Rooms','غرف موسيقى','arts'),
  ('art_rooms','Art Rooms','غرف فنون','arts'),
  ('clinic','Clinic / Medical Room','عيادة / غرفة طبية','student_support'),
  ('sen_support','Special Educational Needs Support','دعم الاحتياجات التعليمية الخاصة','student_support'),
  ('counselling','Counselling / Wellbeing Support','إرشاد ودعم نفسي','student_support'),
  ('cafeteria','Cafeteria / Dining','كافتيريا / مطعم','general'),
  ('school_transport','School Transport','نقل مدرسي','general'),
  ('boarding','Boarding Facilities','سكن داخلي','general')
on conflict (code) do nothing;

create table if not exists edu_core.campus_facilities (
  campus_id uuid not null references edu_core.campuses(campus_id) on delete cascade,
  facility_id uuid not null references edu_core.facilities(facility_id),
  availability_status text not null default 'reported'
    check (availability_status in ('candidate','reported','verified','unavailable','unknown')),
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  observed_at timestamptz not null default now(),
  notes text,
  primary key (campus_id, facility_id)
);

-- ---------------------------------------------------------------------------
-- Admissions requirements and bilingual volatile content
-- ---------------------------------------------------------------------------

create table if not exists edu_core.admission_requirements (
  admission_requirement_id uuid primary key default gen_random_uuid(),
  admission_cycle_id uuid references edu_core.admission_cycles(admission_cycle_id) on delete cascade,
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  campus_id uuid references edu_core.campuses(campus_id) on delete cascade,
  requirement_type text not null
    check (requirement_type in (
      'document','assessment','interview','age','previous_grade','language',
      'application_fee','deposit','medical','other'
    )),
  required boolean,
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  verification_status text not null default 'sourced'
    check (verification_status in ('candidate','sourced','verified','stale','rejected')),
  observed_at timestamptz not null default now()
);

create table if not exists edu_core.admission_requirement_localizations (
  admission_requirement_id uuid not null references edu_core.admission_requirements(admission_requirement_id) on delete cascade,
  locale text not null check (locale in ('ar-EG','en-EG')),
  label text,
  details text not null,
  localization_origin text not null default 'official_source'
    check (localization_origin in (
      'official_source','institution_source','verified_translation',
      'editorial_translation','transliteration','needs_review'
    )),
  review_status text not null default 'unreviewed'
    check (review_status in ('unreviewed','verified','needs_review','rejected','superseded')),
  primary key (admission_requirement_id, locale)
);

create table if not exists edu_core.fee_item_localizations (
  fee_item_id bigint not null references edu_core.fee_items(fee_item_id) on delete cascade,
  locale text not null check (locale in ('ar-EG','en-EG')),
  level_or_program_label text,
  fee_type_label text,
  notes text,
  localization_origin text not null default 'official_source'
    check (localization_origin in (
      'official_source','institution_source','verified_translation',
      'editorial_translation','transliteration','needs_review'
    )),
  review_status text not null default 'unreviewed'
    check (review_status in ('unreviewed','verified','needs_review','rejected','superseded')),
  primary key (fee_item_id, locale)
);

-- ---------------------------------------------------------------------------
-- Higher-education bilingual structure
-- ---------------------------------------------------------------------------

create table if not exists edu_core.academic_unit_localizations (
  academic_unit_id uuid not null references edu_core.academic_units(academic_unit_id) on delete cascade,
  locale text not null check (locale in ('ar-EG','en-EG')),
  name text not null,
  description text,
  localization_origin text not null default 'official_source'
    check (localization_origin in (
      'official_source','institution_source','verified_translation',
      'editorial_translation','transliteration','needs_review'
    )),
  review_status text not null default 'unreviewed'
    check (review_status in ('unreviewed','verified','needs_review','rejected','superseded')),
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  primary key (academic_unit_id, locale)
);

create table if not exists edu_core.program_localizations (
  program_id uuid not null references edu_core.programs(program_id) on delete cascade,
  locale text not null check (locale in ('ar-EG','en-EG')),
  name text not null,
  summary text,
  degree_label text,
  duration_label text,
  localization_origin text not null default 'official_source'
    check (localization_origin in (
      'official_source','institution_source','verified_translation',
      'editorial_translation','transliteration','needs_review'
    )),
  review_status text not null default 'unreviewed'
    check (review_status in ('unreviewed','verified','needs_review','rejected','superseded')),
  source_raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  primary key (program_id, locale)
);

-- ---------------------------------------------------------------------------
-- Media bilingual metadata
-- ---------------------------------------------------------------------------

create table if not exists edu_core.institution_media_localizations (
  institution_media_id bigint not null references edu_core.institution_media(institution_media_id) on delete cascade,
  locale text not null check (locale in ('ar-EG','en-EG')),
  alt_text text,
  caption text,
  credit_line text,
  localization_origin text not null default 'editorial_translation'
    check (localization_origin in (
      'official_source','institution_source','verified_translation',
      'editorial_translation','transliteration','needs_review'
    )),
  review_status text not null default 'unreviewed'
    check (review_status in ('unreviewed','verified','needs_review','rejected','superseded')),
  primary key (institution_media_id, locale),
  check (alt_text is not null or caption is not null or credit_line is not null)
);

-- ---------------------------------------------------------------------------
-- Universal evidence ledger for non-institution facts
-- ---------------------------------------------------------------------------

create table if not exists edu_core.evidence_assertions (
  evidence_assertion_id bigint generated always as identity primary key,
  subject_type text not null
    check (subject_type in (
      'provider','institution','campus','location','curriculum','certificate',
      'accreditation','contact','fee_schedule','fee_item','admission_cycle',
      'admission_requirement','academic_unit','program','facility','media','other'
    )),
  subject_id text not null,
  field_path text not null,
  locale text check (locale in ('ar-EG','en-EG','und')),
  value_json jsonb not null,
  raw_id bigint references edu_raw.raw_records(raw_id),
  source_url text,
  authority_class text,
  confidence numeric(5,4) not null default 0.5 check (confidence between 0 and 1),
  review_status text not null default 'unreviewed'
    check (review_status in ('unreviewed','verified','rejected','superseded','conflict','not_applicable')),
  selected_canonical boolean not null default false,
  observed_at timestamptz not null default now(),
  valid_from date,
  valid_to date,
  notes text
);

create index if not exists evidence_assertions_subject_idx
  on edu_core.evidence_assertions(subject_type, subject_id, field_path);
create index if not exists evidence_assertions_raw_idx
  on edu_core.evidence_assertions(raw_id);
create index if not exists evidence_assertions_review_idx
  on edu_core.evidence_assertions(review_status, selected_canonical);

-- ---------------------------------------------------------------------------
-- Database-completion metrics (not publication eligibility)
-- ---------------------------------------------------------------------------

create table if not exists edu_core.international_profile_completeness (
  edu_hub_id uuid primary key references edu_core.institutions(edu_hub_id) on delete cascade,
  identity_reviewed boolean not null default false,
  eligibility_reviewed boolean not null default false,
  campus_structure_reviewed boolean not null default false,
  name_en_present boolean not null default false,
  name_ar_present boolean not null default false,
  name_ar_origin text,
  location_present boolean not null default false,
  coordinates_present boolean not null default false,
  official_website_present boolean not null default false,
  contact_present boolean not null default false,
  curriculum_present boolean not null default false,
  level_grade_profile_present boolean not null default false,
  accreditation_profile_present boolean not null default false,
  admissions_profile_present boolean not null default false,
  current_fee_profile_present boolean not null default false,
  facilities_profile_present boolean not null default false,
  higher_ed_program_profile_present boolean not null default false,
  media_candidate_present boolean not null default false,
  publication_safe_media_present boolean not null default false,
  unresolved_conflict_count integer not null default 0,
  factual_completeness_score numeric(6,5) not null default 0 check (factual_completeness_score between 0 and 1),
  english_completeness_score numeric(6,5) not null default 0 check (english_completeness_score between 0 and 1),
  arabic_completeness_score numeric(6,5) not null default 0 check (arabic_completeness_score between 0 and 1),
  media_completeness_score numeric(6,5) not null default 0 check (media_completeness_score between 0 and 1),
  evaluated_at timestamptz not null default now(),
  evaluator_version text not null
);

comment on table edu_core.evidence_assertions is
  'Presentation-neutral evidence ledger for canonical facts below institution scope. It complements institution-level field_assertions.';

comment on table edu_core.international_profile_completeness is
  'Database-completion metrics for factual, English, Arabic and media coverage. This does not itself authorize publication.';

revoke all on schema edu_core from public;
