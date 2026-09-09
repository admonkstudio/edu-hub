-- V7 operational hardening for the private, source-shaped archive.
-- Apply after 001_raw_archive.sql.

begin;

create table if not exists edu_raw.storage_owners (
  owner_id text primary key,
  display_name text not null,
  created_at timestamptz not null
);

create table if not exists edu_raw.record_ownership (
  raw_id bigint primary key references edu_raw.raw_records(raw_id) on delete cascade,
  owner_id text not null references edu_raw.storage_owners(owner_id),
  ownership_status text not null default 'locally_held'
    check (ownership_status in ('locally_held', 'archived', 'quarantined')),
  first_stored_at timestamptz not null,
  last_verified_at timestamptz not null,
  payload_sha256 text not null check (payload_sha256 ~ '^[0-9a-f]{64}$')
);

create index if not exists record_ownership_owner_idx
  on edu_raw.record_ownership(owner_id);

create table if not exists edu_raw.import_batches (
  batch_id uuid primary key,
  archive_version integer not null check (archive_version > 0),
  archive_sha256 text not null check (archive_sha256 ~ '^[0-9a-f]{64}$'),
  archive_name text not null,
  status text not null
    check (status in ('started', 'loading', 'verified', 'failed')),
  expected_records bigint not null check (expected_records >= 0),
  imported_records bigint not null default 0 check (imported_records >= 0),
  expected_media_assets bigint not null default 0 check (expected_media_assets >= 0),
  imported_media_assets bigint not null default 0 check (imported_media_assets >= 0),
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  error text,
  unique (archive_version, archive_sha256)
);

create index if not exists import_batches_status_idx
  on edu_raw.import_batches(status, started_at desc);

alter table edu_raw.acquisition_runs
  add column if not exists archive_version integer,
  add column if not exists archive_run_id bigint;

create unique index if not exists acquisition_runs_archive_identity_idx
  on edu_raw.acquisition_runs(archive_version, archive_run_id)
  where archive_version is not null and archive_run_id is not null;

alter table edu_raw.raw_records
  drop constraint if exists raw_records_raw_hash_format;
alter table edu_raw.raw_records
  add constraint raw_records_raw_hash_format
  check (raw_hash ~ '^[0-9a-f]{64}$') not valid;

alter table edu_raw.media_files
  drop constraint if exists media_files_sha256_format;
alter table edu_raw.media_files
  add constraint media_files_sha256_format
  check (file_sha256 ~ '^[0-9a-f]{64}$') not valid;

alter table edu_raw.media_assets
  drop constraint if exists media_assets_public_rights_gate;
alter table edu_raw.media_assets
  add constraint media_assets_public_rights_gate
  check (not public_use_allowed or rights_status <> 'unknown') not valid;

alter table edu_raw.media_assets
  drop constraint if exists media_assets_file_sha256_fkey;
alter table edu_raw.media_assets
  add constraint media_assets_file_sha256_fkey
  foreign key (file_sha256) references edu_raw.media_files(file_sha256) not valid;

create index if not exists acquisition_runs_source_idx
  on edu_raw.acquisition_runs(source_id);

-- The raw payload is evidence storage, not a runtime search document. Avoid a
-- large speculative GIN index; public search belongs on the future read model.
drop index if exists edu_raw.raw_records_payload_gin_idx;

alter table edu_raw.sources enable row level security;
alter table edu_raw.acquisition_runs enable row level security;
alter table edu_raw.raw_records enable row level security;
alter table edu_raw.field_inventory enable row level security;
alter table edu_raw.coverage_targets enable row level security;
alter table edu_raw.media_assets enable row level security;
alter table edu_raw.media_files enable row level security;
alter table edu_raw.storage_owners enable row level security;
alter table edu_raw.record_ownership enable row level security;
alter table edu_raw.import_batches enable row level security;

revoke all on schema edu_raw from public, anon, authenticated;
revoke all on all tables in schema edu_raw from public, anon, authenticated;
revoke all on all sequences in schema edu_raw from public, anon, authenticated;

grant usage on schema edu_raw to service_role;
grant select, insert, update, delete on all tables in schema edu_raw to service_role;
grant usage, select on all sequences in schema edu_raw to service_role;

alter default privileges for role postgres in schema edu_raw
  revoke all on tables from public, anon, authenticated;
alter default privileges for role postgres in schema edu_raw
  revoke all on sequences from public, anon, authenticated;
alter default privileges for role postgres in schema edu_raw
  revoke execute on functions from public, anon, authenticated;

comment on table edu_raw.import_batches is
  'Resumable import ledger for independently checksummed owned archives.';
comment on table edu_raw.record_ownership is
  'Operational possession metadata; does not imply copyright or publication rights.';

commit;
