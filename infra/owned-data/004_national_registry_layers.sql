-- EDU-DATA-1 national education registry layers
-- Depends on infra/owned-data/001_raw_archive.sql.
--
-- Architecture boundary:
--   edu_raw     = source-shaped evidence, immutable-ish acquisition archive
--   edu_staging = normalization, matching, conflicts and human review
--   edu_core    = canonical institution identities + field-level provenance
--
-- This migration intentionally does NOT create the public read model. Public
-- projection is a later gate and must never read directly from edu_raw.

create extension if not exists pgcrypto;

create schema if not exists edu_staging;
create schema if not exists edu_core;

-- ---------------------------------------------------------------------------
-- Staging: one normalized candidate per raw source record.
-- ---------------------------------------------------------------------------

create table if not exists edu_staging.entity_candidates (
  candidate_id uuid primary key default gen_random_uuid(),
  raw_id bigint not null unique references edu_raw.raw_records(raw_id) on delete cascade,
  source_id text not null,
  source_record_id text,
  entity_family text not null,
  entity_type_raw text,
  normalized_type text,
  name_ar text,
  name_en text,
  normalized_name_ar text,
  normalized_name_en text,
  normalized_location text,
  governorate text,
  city text,
  district text,
  latitude double precision,
  longitude double precision,
  normalized_phone text,
  normalized_domain text,
  official_identifier text,
  match_features jsonb not null default '{}'::jsonb,
  normalization_issues jsonb not null default '[]'::jsonb,
  candidate_status text not null default 'ready'
    check (candidate_status in ('ready','needs_review','invalid','suppressed')),
  normalized_at timestamptz not null default now()
);

create index if not exists entity_candidates_source_idx
  on edu_staging.entity_candidates(source_id, source_record_id);
create index if not exists entity_candidates_family_idx
  on edu_staging.entity_candidates(entity_family, normalized_type);
create index if not exists entity_candidates_name_ar_idx
  on edu_staging.entity_candidates(normalized_name_ar);
create index if not exists entity_candidates_name_en_idx
  on edu_staging.entity_candidates(normalized_name_en);
create index if not exists entity_candidates_geo_idx
  on edu_staging.entity_candidates(latitude, longitude);
create index if not exists entity_candidates_domain_idx
  on edu_staging.entity_candidates(normalized_domain);

-- Pairwise match proposals are evidence, not merges.
create table if not exists edu_staging.identity_match_candidates (
  match_id bigint generated always as identity primary key,
  left_candidate_id uuid not null references edu_staging.entity_candidates(candidate_id) on delete cascade,
  right_candidate_id uuid not null references edu_staging.entity_candidates(candidate_id) on delete cascade,
  score numeric(6,5) not null check (score >= 0 and score <= 1),
  decision text not null default 'unreviewed'
    check (decision in ('unreviewed','auto_accept','accepted','rejected','needs_review')),
  evidence jsonb not null default '{}'::jsonb,
  matcher_version text not null,
  created_at timestamptz not null default now(),
  reviewed_at timestamptz,
  reviewed_by text,
  review_note text,
  check (left_candidate_id <> right_candidate_id),
  unique(left_candidate_id, right_candidate_id, matcher_version)
);

create index if not exists identity_match_candidates_decision_idx
  on edu_staging.identity_match_candidates(decision, score desc);

-- Review queue for ambiguous identity, hierarchy and field conflicts.
create table if not exists edu_staging.review_tasks (
  review_task_id bigint generated always as identity primary key,
  task_type text not null
    check (task_type in ('identity_match','identity_split','field_conflict','hierarchy','invalid_source_record','other')),
  priority smallint not null default 50 check (priority between 0 and 100),
  status text not null default 'open'
    check (status in ('open','in_progress','resolved','dismissed')),
  subject jsonb not null,
  evidence jsonb not null default '{}'::jsonb,
  resolution jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  resolved_at timestamptz,
  resolved_by text
);

create index if not exists review_tasks_queue_idx
  on edu_staging.review_tasks(status, priority desc, created_at);

-- ---------------------------------------------------------------------------
-- Canonical core: one durable Edu Hub identity per institution.
-- ---------------------------------------------------------------------------

create table if not exists edu_core.institutions (
  edu_hub_id uuid primary key default gen_random_uuid(),
  entity_family text not null
    check (entity_family in ('early_education','pre_university','higher_education','other')),
  institution_type text not null,
  canonical_name_ar text,
  canonical_name_en text,
  lifecycle_status text not null default 'active'
    check (lifecycle_status in ('active','inactive','closed','planned','unknown')),
  data_status text not null default 'registered'
    check (data_status in ('candidate','registered','verified','enriched','complete','claimed','suppressed')),
  completeness_level smallint not null default 1 check (completeness_level between 0 and 6),
  parent_edu_hub_id uuid references edu_core.institutions(edu_hub_id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  verified_at timestamptz,
  check (canonical_name_ar is not null or canonical_name_en is not null),
  check (parent_edu_hub_id is null or parent_edu_hub_id <> edu_hub_id)
);

create index if not exists institutions_family_type_idx
  on edu_core.institutions(entity_family, institution_type);
create index if not exists institutions_status_idx
  on edu_core.institutions(data_status, lifecycle_status);
create index if not exists institutions_parent_idx
  on edu_core.institutions(parent_edu_hub_id);

-- Every canonical institution must ultimately have at least one source link.
-- Enforcement is performed by release validation because a row may be created
-- and its first link inserted in the same application transaction.
create table if not exists edu_core.institution_sources (
  institution_source_id bigint generated always as identity primary key,
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  raw_id bigint not null references edu_raw.raw_records(raw_id),
  relation text not null default 'identity_evidence'
    check (relation in ('identity_evidence','alternate_identity','enrichment','historical','geospatial','accreditation','other')),
  confidence numeric(5,4) not null default 1.0 check (confidence >= 0 and confidence <= 1),
  is_primary_identity_evidence boolean not null default false,
  linked_at timestamptz not null default now(),
  linked_by text,
  notes text,
  unique (edu_hub_id, raw_id)
);

create index if not exists institution_sources_raw_idx
  on edu_core.institution_sources(raw_id);
create index if not exists institution_sources_identity_idx
  on edu_core.institution_sources(edu_hub_id, is_primary_identity_evidence);

-- Field-level assertions preserve competing evidence. A selected canonical
-- value is still an assertion with a source, never an untraceable overwrite.
create table if not exists edu_core.field_assertions (
  assertion_id bigint generated always as identity primary key,
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  field_name text not null,
  value_json jsonb not null,
  raw_id bigint references edu_raw.raw_records(raw_id),
  assertion_source text not null default 'external_source'
    check (assertion_source in ('external_source','institution_claim','human_review','derived')),
  authority_class text,
  confidence numeric(5,4) not null default 0.5 check (confidence >= 0 and confidence <= 1),
  review_status text not null default 'unreviewed'
    check (review_status in ('unreviewed','verified','rejected','superseded','not_applicable')),
  selected_canonical boolean not null default false,
  valid_from date,
  valid_to date,
  created_at timestamptz not null default now(),
  reviewed_at timestamptz,
  reviewed_by text,
  notes text
);

create index if not exists field_assertions_field_idx
  on edu_core.field_assertions(edu_hub_id, field_name);
create index if not exists field_assertions_selected_idx
  on edu_core.field_assertions(edu_hub_id, field_name, selected_canonical)
  where selected_canonical = true;
create index if not exists field_assertions_raw_idx
  on edu_core.field_assertions(raw_id);

-- Publication-safe media is linked only after rights/publication review. The
-- underlying media provenance remains in edu_raw.media_assets/media_files.
create table if not exists edu_core.institution_media (
  institution_media_id bigint generated always as identity primary key,
  edu_hub_id uuid not null references edu_core.institutions(edu_hub_id) on delete cascade,
  raw_media_id bigint references edu_raw.media_assets(media_id),
  role text not null default 'gallery'
    check (role in ('logo','cover','featured','gallery','campus','facility','other')),
  storage_key text,
  rights_basis text,
  public_use_allowed boolean not null default false,
  sort_order integer not null default 0,
  created_at timestamptz not null default now(),
  check (public_use_allowed = false or storage_key is not null)
);

create index if not exists institution_media_public_idx
  on edu_core.institution_media(edu_hub_id, public_use_allowed, role);

-- One row per institution with transparent completeness components. This is
-- recomputed by a later evaluator; it is not the identity truth itself.
create table if not exists edu_core.institution_completeness (
  edu_hub_id uuid primary key references edu_core.institutions(edu_hub_id) on delete cascade,
  identity_verified boolean not null default false,
  useful_location boolean not null default false,
  contact_present boolean not null default false,
  education_profile_present boolean not null default false,
  commercial_profile_present boolean not null default false,
  accreditation_profile_present boolean not null default false,
  description_present boolean not null default false,
  publication_safe_media_present boolean not null default false,
  institution_claimed boolean not null default false,
  applicable_fields integer not null default 0,
  populated_applicable_fields integer not null default 0,
  completeness_score numeric(6,5) not null default 0 check (completeness_score >= 0 and completeness_score <= 1),
  completeness_level smallint not null default 0 check (completeness_level between 0 and 6),
  evaluated_at timestamptz not null default now(),
  evaluator_version text not null
);

comment on schema edu_staging is
  'Private normalization, matching, conflict and review layer. Never a public API.';

comment on schema edu_core is
  'Canonical Edu Hub institution identities and provenance-backed assertions.';

comment on table edu_core.field_assertions is
  'Competing and selected field values with raw/source evidence. Missing values must not be invented.';

-- Keep private layers private by default. Deployments may use additional roles,
-- but anon/authenticated must never gain direct access here.
revoke all on schema edu_staging from public;
revoke all on schema edu_core from public;
