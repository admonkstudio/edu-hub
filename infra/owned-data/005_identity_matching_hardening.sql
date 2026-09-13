-- EDU-DATA-1 identity-resolution hardening.
-- Apply after 004_staging_boundary.sql.

begin;

create table if not exists edu_staging.matching_runs (
  run_id uuid primary key,
  matching_version integer not null check (matching_version > 0),
  normalization_run_id uuid references edu_staging.normalization_runs(run_id) on delete set null,
  status text not null check (status in ('started','loading','verified','failed')),
  candidate_count bigint not null default 0,
  pair_count bigint not null default 0,
  proposed_count bigint not null default 0,
  review_count bigint not null default 0,
  skipped_block_count bigint not null default 0,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  report_json jsonb,
  error text
);

alter table edu_staging.identity_matches
  add column if not exists run_id uuid references edu_staging.matching_runs(run_id) on delete set null,
  add column if not exists matching_version integer;

create index if not exists identity_matches_run_idx
  on edu_staging.identity_matches(run_id, match_status);
create index if not exists identity_matches_score_idx
  on edu_staging.identity_matches(match_status, score desc);

create unique index if not exists identity_match_evidence_unique_idx
  on edu_staging.identity_match_evidence(match_id, evidence_type, coalesce(evidence_value, ''));

create unique index if not exists review_tasks_identity_unique_idx
  on edu_staging.review_tasks(
    coalesce(candidate_id, 0),
    coalesce(match_id, 0),
    task_type,
    reason
  );

revoke all on edu_staging.matching_runs from public, anon, authenticated;
grant select, insert, update, delete on edu_staging.matching_runs to service_role;

comment on table edu_staging.matching_runs is
  'Versioned identity-resolution run ledger. Matching creates proposals/review tasks only; it does not promote canonical institutions.';

commit;
