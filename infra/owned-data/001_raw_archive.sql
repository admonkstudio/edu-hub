-- Edu Hub source-neutral owned raw archive
-- This is NOT the final canonical/public institution schema.
-- It exists so Admonk/Edu Hub can permanently hold acquired source data and media
-- without depending on source APIs or third-party directories at render time.

create schema if not exists edu_raw;

create table if not exists edu_raw.sources (
  source_id text primary key,
  name text not null,
  url text not null,
  source_type text not null,
  authority text not null,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists edu_raw.acquisition_runs (
  run_id bigint generated always as identity primary key,
  source_id text not null references edu_raw.sources(source_id),
  started_at timestamptz not null,
  finished_at timestamptz,
  status text not null,
  records_added bigint not null default 0,
  error text
);

create table if not exists edu_raw.raw_records (
  raw_id bigint generated always as identity primary key,
  source_id text not null references edu_raw.sources(source_id),
  source_record_id text,
  entity_family text not null,
  entity_type_raw text,
  name_raw text,
  name_ar_raw text,
  name_en_raw text,
  location_raw text,
  latitude double precision,
  longitude double precision,
  source_url text,
  retrieved_at timestamptz not null,
  raw_hash text not null,
  payload_json jsonb not null,
  created_at timestamptz not null default now(),
  unique (source_id, raw_hash)
);

create index if not exists raw_records_source_idx on edu_raw.raw_records(source_id);
create index if not exists raw_records_family_idx on edu_raw.raw_records(entity_family);
create index if not exists raw_records_name_idx on edu_raw.raw_records(name_raw);
create index if not exists raw_records_source_record_idx on edu_raw.raw_records(source_id, source_record_id);
create index if not exists raw_records_geo_idx on edu_raw.raw_records(latitude, longitude);
create index if not exists raw_records_payload_gin_idx on edu_raw.raw_records using gin(payload_json);

create table if not exists edu_raw.field_inventory (
  source_id text not null references edu_raw.sources(source_id),
  field_path text not null,
  populated_records bigint not null,
  distinct_sample_count bigint not null,
  example_values_json jsonb not null,
  primary key (source_id, field_path)
);

create table if not exists edu_raw.coverage_targets (
  target_id text primary key,
  label text not null,
  official_count bigint,
  target_basis text not null,
  reference_url text not null,
  updated_at timestamptz not null default now()
);

create table if not exists edu_raw.media_assets (
  media_id bigint generated always as identity primary key,
  source_id text not null references edu_raw.sources(source_id),
  source_record_id text,
  source_name_raw text,
  source_page_url text not null,
  original_url text not null,
  candidate_index integer,
  role_raw text,
  alt_raw text,
  title_raw text,
  width_hint integer,
  height_hint integer,
  discovery_method text,
  discovered_at timestamptz not null,
  rights_status text not null default 'unknown',
  public_use_allowed boolean not null default false,
  mirror_status text not null default 'discovered',
  file_sha256 text,
  storage_key text,
  mime_type text,
  byte_size bigint,
  width integer,
  height integer,
  acquired_at timestamptz,
  error text,
  unique(source_id, source_record_id, original_url)
);

create index if not exists media_assets_source_record_idx on edu_raw.media_assets(source_id, source_record_id);
create index if not exists media_assets_sha_idx on edu_raw.media_assets(file_sha256);
create index if not exists media_assets_rights_idx on edu_raw.media_assets(rights_status, public_use_allowed);
create index if not exists media_assets_mirror_idx on edu_raw.media_assets(mirror_status);

create table if not exists edu_raw.media_files (
  file_sha256 text primary key,
  storage_key text not null unique,
  mime_type text,
  byte_size bigint not null,
  width integer,
  height integer,
  first_acquired_at timestamptz not null
);

comment on schema edu_raw is
  'Source-neutral owned raw archive. Not the final canonical/public institution model.';

comment on column edu_raw.raw_records.payload_json is
  'Complete source-shaped payload retained so later field selection does not lose information.';

comment on column edu_raw.media_assets.original_url is
  'Provenance/discovery URL only. Production rendering must use an owned storage_key after rights/publication review.';
