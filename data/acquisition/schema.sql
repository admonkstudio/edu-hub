PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS storage_owners (
  owner_id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS record_ownership (
  raw_id INTEGER PRIMARY KEY REFERENCES raw_records(raw_id) ON DELETE CASCADE,
  owner_id TEXT NOT NULL REFERENCES storage_owners(owner_id),
  ownership_status TEXT NOT NULL DEFAULT 'locally_held'
    CHECK (ownership_status IN ('locally_held', 'archived', 'quarantined')),
  first_stored_at TEXT NOT NULL,
  last_verified_at TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS media_files (
  media_file_id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id TEXT NOT NULL REFERENCES storage_owners(owner_id),
  sha256 TEXT NOT NULL UNIQUE,
  storage_backend TEXT NOT NULL DEFAULT 'local',
  storage_key TEXT NOT NULL UNIQUE,
  mime_type TEXT NOT NULL,
  file_extension TEXT NOT NULL,
  byte_size INTEGER NOT NULL CHECK (byte_size >= 0),
  width INTEGER,
  height INTEGER,
  downloaded_at TEXT NOT NULL,
  verified_at TEXT NOT NULL,
  file_status TEXT NOT NULL DEFAULT 'available'
    CHECK (file_status IN ('available', 'quarantined', 'missing'))
);

CREATE TABLE IF NOT EXISTS raw_media (
  raw_media_id INTEGER PRIMARY KEY AUTOINCREMENT,
  raw_id INTEGER REFERENCES raw_records(raw_id) ON DELETE SET NULL,
  source_id TEXT NOT NULL REFERENCES sources(source_id),
  source_record_id TEXT,
  source_page_url TEXT,
  original_url TEXT NOT NULL,
  media_type TEXT NOT NULL DEFAULT 'unknown',
  alt_text TEXT,
  discovered_at TEXT NOT NULL,
  last_attempted_at TEXT,
  retrieval_status TEXT NOT NULL DEFAULT 'discovered'
    CHECK (retrieval_status IN ('discovered', 'downloaded', 'failed', 'blocked', 'invalid', 'skipped')),
  media_file_id INTEGER REFERENCES media_files(media_file_id),
  rights_status TEXT NOT NULL DEFAULT 'unknown'
    CHECK (rights_status IN ('unknown', 'open_license', 'permission_granted', 'institution_supplied', 'restricted')),
  license_name TEXT,
  copyright_owner TEXT,
  credit_text TEXT,
  public_reuse_allowed INTEGER NOT NULL DEFAULT 0 CHECK (public_reuse_allowed IN (0, 1)),
  failure_reason TEXT,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  UNIQUE(source_id, original_url, source_record_id)
);

CREATE TABLE IF NOT EXISTS media_fetch_attempts (
  attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
  raw_media_id INTEGER NOT NULL REFERENCES raw_media(raw_media_id) ON DELETE CASCADE,
  attempted_at TEXT NOT NULL,
  outcome TEXT NOT NULL,
  http_status INTEGER,
  bytes_received INTEGER,
  error TEXT
);

CREATE INDEX IF NOT EXISTS idx_record_ownership_owner ON record_ownership(owner_id);
CREATE INDEX IF NOT EXISTS idx_raw_media_record ON raw_media(raw_id);
CREATE INDEX IF NOT EXISTS idx_raw_media_source ON raw_media(source_id);
CREATE INDEX IF NOT EXISTS idx_raw_media_status ON raw_media(retrieval_status);
CREATE INDEX IF NOT EXISTS idx_raw_media_rights ON raw_media(rights_status, public_reuse_allowed);
CREATE INDEX IF NOT EXISTS idx_media_files_owner ON media_files(owner_id);
CREATE INDEX IF NOT EXISTS idx_media_files_hash ON media_files(sha256);

CREATE VIEW IF NOT EXISTS media_coverage_by_source AS
SELECT
  s.source_id,
  s.name AS source_name,
  COUNT(DISTINCT r.raw_id) AS records_total,
  COUNT(DISTINCT rm.raw_id) AS records_with_media_discovered,
  COUNT(DISTINCT CASE WHEN rm.media_file_id IS NOT NULL THEN rm.raw_id END) AS records_with_owned_media,
  COUNT(rm.raw_media_id) AS media_discovered,
  COUNT(rm.media_file_id) AS media_downloaded,
  COUNT(CASE WHEN rm.public_reuse_allowed = 1 THEN 1 END) AS media_public_reuse_allowed
FROM sources s
LEFT JOIN raw_records r ON r.source_id = s.source_id
LEFT JOIN raw_media rm ON rm.raw_id = r.raw_id
GROUP BY s.source_id, s.name;

