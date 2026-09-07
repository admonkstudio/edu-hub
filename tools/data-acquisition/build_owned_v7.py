#!/usr/bin/env python3
"""Build a portable V7 owned archive by consolidating V5 and V6."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import tarfile
from datetime import datetime, timezone
from pathlib import Path


RAW_COLUMNS = (
    "source_id,source_record_id,entity_family,entity_type_raw,name_raw,"
    "name_ar_raw,name_en_raw,location_raw,latitude,longitude,source_url,"
    "retrieved_at,raw_hash,payload_json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scalar(db: sqlite3.Connection, sql: str, args: tuple = ()) -> int | str:
    return db.execute(sql, args).fetchone()[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v5-db", required=True, type=Path)
    parser.add_argument("--v6-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--archive", required=True, type=Path)
    args = parser.parse_args()

    v6_db = args.v6_root / "edu_hub_owned_archive.sqlite"
    v6_media = args.v6_root / "media"
    for required in (args.v5_db, v6_db, v6_media):
        if not required.exists():
            raise SystemExit(f"missing input: {required}")

    if args.output_root.exists():
        raise SystemExit(f"output already exists: {args.output_root}")
    if args.archive.exists():
        raise SystemExit(f"archive already exists: {args.archive}")

    args.output_root.mkdir(parents=True)
    output_db = args.output_root / "edu_hub_owned_archive_v7.sqlite"
    shutil.copy2(v6_db, output_db)
    shutil.copytree(v6_media, args.output_root / "media")

    db = sqlite3.connect(output_db)
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("ATTACH DATABASE ? AS v5", (str(args.v5_db),))
    before = scalar(db, "SELECT COUNT(*) FROM raw_records")

    with db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS storage_owners (
              owner_id TEXT PRIMARY KEY,
              display_name TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS record_ownership (
              raw_id INTEGER PRIMARY KEY REFERENCES raw_records(raw_id) ON DELETE CASCADE,
              owner_id TEXT NOT NULL REFERENCES storage_owners(owner_id),
              ownership_status TEXT NOT NULL DEFAULT 'locally_held'
                CHECK (ownership_status IN ('locally_held','archived','quarantined')),
              first_stored_at TEXT NOT NULL,
              last_verified_at TEXT NOT NULL,
              payload_sha256 TEXT NOT NULL
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_record_ownership_owner ON record_ownership(owner_id)")
        db.execute("INSERT OR IGNORE INTO storage_owners SELECT * FROM v5.storage_owners")
        db.execute("INSERT OR IGNORE INTO sources SELECT * FROM v5.sources")
        db.execute(f"""
            INSERT OR IGNORE INTO raw_records ({RAW_COLUMNS})
            SELECT {RAW_COLUMNS} FROM v5.raw_records
        """)
        db.execute("""
            INSERT OR IGNORE INTO acquisition_runs
              (source_id,started_at,finished_at,status,records_added,error)
            SELECT source_id,started_at,finished_at,status,records_added,error
            FROM v5.acquisition_runs
        """)
        db.execute("INSERT OR IGNORE INTO coverage_targets SELECT * FROM v5.coverage_targets")
        db.execute("INSERT OR IGNORE INTO field_inventory SELECT * FROM v5.field_inventory")

    # SQLite has no built-in SHA-256 in standard Python builds; fill ownership hashes here.
    rows = db.execute("SELECT raw_id,payload_json,retrieved_at FROM raw_records").fetchall()
    now = datetime.now(timezone.utc).isoformat()
    with db:
        db.execute("DELETE FROM record_ownership")
        db.executemany(
            """INSERT INTO record_ownership
               (raw_id,owner_id,ownership_status,first_stored_at,last_verified_at,payload_sha256)
               VALUES (?, 'edu-hub', 'locally_held', ?, ?, ?)""",
            [
                (raw_id, retrieved_at, now, hashlib.sha256(payload.encode("utf-8")).hexdigest())
                for raw_id, payload, retrieved_at in rows
            ],
        )

    db.execute("DETACH DATABASE v5")
    db.execute("VACUUM")
    integrity = scalar(db, "PRAGMA integrity_check")
    foreign_key_errors = list(db.execute("PRAGMA foreign_key_check"))
    total = scalar(db, "SELECT COUNT(*) FROM raw_records")
    sources = dict(db.execute("SELECT source_id,COUNT(*) FROM raw_records GROUP BY source_id ORDER BY source_id"))
    ownership = scalar(db, "SELECT COUNT(*) FROM record_ownership")
    media_assets = scalar(db, "SELECT COUNT(*) FROM media_assets")
    media_files = scalar(db, "SELECT COUNT(*) FROM media_files")
    public_media = scalar(db, "SELECT COUNT(*) FROM media_assets WHERE public_use_allowed != 0")
    duplicate_source_hashes = scalar(
        db,
        """SELECT COUNT(*) FROM (
             SELECT source_id,raw_hash,COUNT(*) c FROM raw_records
             GROUP BY source_id,raw_hash HAVING c > 1
           )""",
    )
    duplicate_source_ids = scalar(
        db,
        """SELECT COUNT(*) FROM (
             SELECT source_id,source_record_id,COUNT(*) c FROM raw_records
             WHERE source_record_id IS NOT NULL AND source_record_id != ''
             GROUP BY source_id,source_record_id HAVING c > 1
           )""",
    )
    db.close()

    verified_media = 0
    missing_media: list[str] = []
    bad_media: list[str] = []
    check = sqlite3.connect(f"file:{output_db}?mode=ro", uri=True)
    for file_hash, storage_key in check.execute("SELECT file_sha256,storage_key FROM media_files"):
        path = args.output_root / "media" / storage_key
        if not path.is_file():
            missing_media.append(storage_key)
        elif sha256_file(path) != file_hash:
            bad_media.append(storage_key)
        else:
            verified_media += 1
    check.close()

    report = {
        "version": 7,
        "created_at": now,
        "inputs": {"v5_records": 13452, "v6_records": before},
        "records": total,
        "records_added_from_v5": total - before,
        "source_count": len(sources),
        "records_by_source": sources,
        "ownership_rows": ownership,
        "media_assets": media_assets,
        "unique_media_files": media_files,
        "verified_media_files": verified_media,
        "public_media_assets": public_media,
        "duplicate_source_hash_groups": duplicate_source_hashes,
        "duplicate_source_record_id_groups": duplicate_source_ids,
        "sqlite_integrity": integrity,
        "foreign_key_errors": foreign_key_errors,
        "missing_media": missing_media,
        "bad_media": bad_media,
    }
    expected = {
        "records": 24916,
        "ownership_rows": 24916,
        "media_assets": 2101,
        "unique_media_files": 453,
        "verified_media_files": 453,
        "public_media_assets": 0,
        "duplicate_source_hash_groups": 0,
        "sqlite_integrity": "ok",
    }
    failures = {key: {"expected": value, "actual": report[key]} for key, value in expected.items() if report[key] != value}
    if foreign_key_errors or missing_media or bad_media:
        failures["referential_or_media_integrity"] = True
    report["ok"] = not failures
    report["failures"] = failures

    report_path = args.output_root / "V7-VALIDATION.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checksums = {
        output_db.relative_to(args.output_root).as_posix(): sha256_file(output_db),
        report_path.relative_to(args.output_root).as_posix(): sha256_file(report_path),
    }
    for path in sorted((args.output_root / "media").rglob("*")):
        if path.is_file():
            checksums[path.relative_to(args.output_root).as_posix()] = sha256_file(path)
    (args.output_root / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in checksums.items()), encoding="utf-8"
    )

    if failures:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit("V7 validation failed")

    args.archive.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.archive, "w:gz") as archive:
        archive.add(args.output_root, arcname=args.output_root.name)
    with tarfile.open(args.archive, "r:gz") as archive:
        members = archive.getmembers()
        if not members:
            raise SystemExit("archive verification failed: no members")
    archive_hash = sha256_file(args.archive)
    args.archive.with_suffix(args.archive.suffix + ".sha256").write_text(
        f"{archive_hash}  {args.archive.name}\n", encoding="utf-8"
    )
    print(json.dumps({**report, "archive": str(args.archive), "archive_sha256": archive_hash}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
