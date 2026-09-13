-- EDU-DATA-1 private normalization/matching boundary.
-- Apply after 001_raw_archive.sql and 002_v7_import_hardening.sql.
-- No table in this schema is public-facing or canonical.

begin;

create schema if not exists edu_staging;

create table if not exists edu_staging.normalization_runs (
  run_id uuid primary key,
  normalization_version integer not null check (normalization_version > 0),
  archive_batch_id uuid references edu_raw.import_batches(batch_id) on delete set null,
  status text not null check (status in ('started','loading','verified','failed')),
  source_row_count bigint not null default 0,
  ready_count bigint not null default 0,
  review_count bigint not null default 0,
  suppressed_count bigint not null default 0,
  invalid_count bigint not null default 0,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  report_json jsonb,
  error text
);

create table if not exists edu_staging.entity_candidates (
  candidate_id bigint generated always as identity primary key,
  raw_id bigint not null unique references edu_raw.raw_records(raw_id) on delete cascade,
  run_id uuid not null references edu_staging.normalization_runs(run_id) on delete restrict,
  source_id text not null,
  source_record_id text,
  entity_family text not null,
  entity_type_raw text,
  entity_type_normalized text,
  name_primary text,
  name_ar text,
  name_en text,
  normalized_name text,
  location_raw text,
  governorate_guess text,
  latitude double precision,
  longitude double precision,
  source_url text,
  website_url text,
  phone text,
  email text,
  candidate_status text not null
    check (candidate_status in ('ready','needs_review','suppressed','invalid')),
  review_reasons text[] not null default '{}',
  normalized_payload jsonb not null default '{}'::jsonb,
  normalization_version integer not null,
  normalized_at timestamptz not null default now(),
  check (latitude is null or latitude between -90 and 90),
  check (longitude is null or longitude between -180 and 180)
);

create index if not exists entity_candidates_source_idx
  on edu_staging.entity_candidates(source_id, candidate_status);
create index if not exists entity_candidates_name_idx
  on edu_staging.entity_candidates(normalized_name);
create index if not exists entity_candidates_type_idx
  on edu_staging.entity_candidates(entity_type_normalized, candidate_status);
create index if not exists entity_candidates_geo_idx
  on edu_staging.entity_candidates(latitude, longitude);

create table if not exists edu_staging.field_candidates (
  field_candidate_id bigint generated always as identity primary key,
  candidate_id bigint not null references edu_staging.entity_candidates(candidate_id) on delete cascade,
  field_path text not null,
  value_text text,
  value_jsonb jsonb,
  source_url text,
  confidence numeric(4,3) not null default 1.000 check (confidence between 0 and 1),
  verification_status text not null default 'source_observed'
    check (verification_status in ('source_observed','normalized','inferred','rejected')),
  created_at timestamptz not null default now(),
  unique(candidate_id, field_path)
);

create index if not exists field_candidates_field_idx
  on edu_staging.field_candidates(field_path, verification_status);

create table if not exists edu_staging.identity_matches (
  match_id bigint generated always as identity primary key,
  left_candidate_id bigint not null references edu_staging.entity_candidates(candidate_id) on delete cascade,
  right_candidate_id bigint not null references edu_staging.entity_candidates(candidate_id) on delete cascade,
  match_status text not null default 'proposed'
    check (match_status in ('proposed','accepted','rejected','needs_review')),
  score numeric(5,4) check (score between 0 and 1),
  method text not null,
  created_at timestamptz not null default now(),
  reviewed_at timestamptz,
  check (left_candidate_id < right_candidate_id),
  unique(left_candidate_id, right_candidate_id)
);

create table if not exists edu_staging.identity_match_evidence (
  evidence_id bigint generated always as identity primary key,
  match_id bigint not null references edu_staging.identity_matches(match_id) on delete cascade,
  evidence_type text not null,
  evidence_value text,
  weight numeric(5,4) check (weight between -1 and 1),
  created_at timestamptz not null default now()
);

create table if not exists edu_staging.review_tasks (
  task_id bigint generated always as identity primary key,
  candidate_id bigint references edu_staging.entity_candidates(candidate_id) on delete cascade,
  match_id bigint references edu_staging.identity_matches(match_id) on delete cascade,
  task_type text not null,
  reason text not null,
  status text not null default 'open' check (status in ('open','resolved','dismissed')),
  created_at timestamptz not null default now(),
  resolved_at timestamptz,
  check (candidate_id is not null or match_id is not null)
);

create index if not exists review_tasks_status_idx
  on edu_staging.review_tasks(status, task_type);

revoke all on schema edu_staging from public, anon, authenticated;
revoke all on all tables in schema edu_staging from public, anon, authenticated;
revoke all on all sequences in schema edu_staging from public, anon, authenticated;

grant usage on schema edu_staging to service_role;
grant select, insert, update, delete on all tables in schema edu_staging to service_role;
grant usage, select on all sequences in schema edu_staging to service_role;

alter default privileges for role postgres in schema edu_staging
  revoke all on tables from public, anon, authenticated;
alter default privileges for role postgres in schema edu_staging
  revoke all on sequences from public, anon, authenticated;
alter default privileges for role postgres in schema edu_staging
  revoke execute on functions from public, anon, authenticated;

comment on schema edu_staging is
  'Private normalization, matching and review boundary. Raw evidence enters here before any canonical promotion.';
comment on table edu_staging.entity_candidates is
  'One deterministic normalized candidate per edu_raw.raw_records row. Not canonical data.';
comment on table edu_staging.identity_matches is
  'Cross-source identity-resolution proposals; accepted matches still require a separate canonical promotion step.';

commit;
