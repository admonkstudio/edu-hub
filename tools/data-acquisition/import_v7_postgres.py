#!/usr/bin/env python3
"""Validate and idempotently import the V7 SQLite archive into PostgreSQL."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


EXPECTED = {
    "raw_records": 24_916,
    "sources": 13,
    "record_ownership": 24_916,
    "media_assets": 2_101,
    "media_files": 453,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def chunks(rows: Iterable[Sequence], size: int) -> Iterable[list[Sequence]]:
    batch: list[Sequence] = []
    for row in rows:
        batch.append(row)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def sqlite_counts(db: sqlite3.Connection) -> dict[str, int]:
    return {table: db.execute(f"select count(*) from {table}").fetchone()[0] for table in EXPECTED}


def validate_sqlite(db: sqlite3.Connection) -> dict:
    counts = sqlite_counts(db)
    integrity = db.execute("pragma integrity_check").fetchone()[0]
    foreign_keys = list(db.execute("pragma foreign_key_check"))
    duplicate_hashes = db.execute(
        """select count(*) from (
             select source_id,raw_hash,count(*) c from raw_records
             group by source_id,raw_hash having c > 1
           )"""
    ).fetchone()[0]
    invalid_raw_hashes = db.execute(
        "select count(*) from raw_records where length(raw_hash) <> 64 or raw_hash glob '*[^0-9a-f]*'"
    ).fetchone()[0]
    orphaned_media_files = db.execute(
        """select count(*) from media_assets a left join media_files f
             on f.file_sha256=a.file_sha256
           where a.file_sha256 is not null and f.file_sha256 is null"""
    ).fetchone()[0]
    unsafe_unknown_rights = db.execute(
        "select count(*) from media_assets where public_use_allowed <> 0 and rights_status='unknown'"
    ).fetchone()[0]
    ownership_hash_mismatches = sum(
        hashlib.sha256(payload.encode("utf-8")).hexdigest() != stored_hash
        for payload, stored_hash in db.execute(
            """select r.payload_json,o.payload_sha256
               from raw_records r join record_ownership o using(raw_id)"""
        )
    )
    failures = {
        key: {"expected": value, "actual": counts.get(key)}
        for key, value in EXPECTED.items()
        if counts.get(key) != value
    }
    if integrity != "ok":
        failures["sqlite_integrity"] = integrity
    if foreign_keys:
        failures["foreign_keys"] = foreign_keys
    if duplicate_hashes:
        failures["duplicate_source_hash_groups"] = duplicate_hashes
    if invalid_raw_hashes:
        failures["invalid_raw_hashes"] = invalid_raw_hashes
    if orphaned_media_files:
        failures["orphaned_media_files"] = orphaned_media_files
    if unsafe_unknown_rights:
        failures["unsafe_unknown_rights"] = unsafe_unknown_rights
    if ownership_hash_mismatches:
        failures["ownership_hash_mismatches"] = ownership_hash_mismatches
    return {
        "ok": not failures,
        "counts": counts,
        "sqlite_integrity": integrity,
        "foreign_key_errors": foreign_keys,
        "duplicate_source_hash_groups": duplicate_hashes,
        "invalid_raw_hashes": invalid_raw_hashes,
        "orphaned_media_files": orphaned_media_files,
        "unsafe_unknown_rights": unsafe_unknown_rights,
        "ownership_hash_mismatches": ownership_hash_mismatches,
        "failures": failures,
    }


def upsert_many(pg, sql: str, rows: Iterable[Sequence], batch_size: int) -> int:
    total = 0
    for batch in chunks(rows, batch_size):
        with pg.cursor() as cursor:
            cursor.executemany(sql, batch)
        pg.commit()
        total += len(batch)
    return total


def import_archive(sqlite_db: sqlite3.Connection, database_url: str, archive_hash: str, archive_name: str, batch_size: int) -> dict:
    try:
        import psycopg
    except ImportError as exc:
        raise SystemExit("Install psycopg[binary]==3.2.10 before a live import") from exc

    batch_id = uuid.uuid5(uuid.NAMESPACE_URL, f"edu-hub:v7:{archive_hash}")
    pg = psycopg.connect(database_url, autocommit=False)
    try:
        with pg.cursor() as cursor:
            cursor.execute(
                """insert into edu_raw.import_batches
                   (batch_id,archive_version,archive_sha256,archive_name,status,
                    expected_records,expected_media_assets)
                   values (%s,7,%s,%s,'started',%s,%s)
                   on conflict (archive_version,archive_sha256) do update
                   set status='loading', error=null, finished_at=null""",
                (batch_id, archive_hash, archive_name, EXPECTED["raw_records"], EXPECTED["media_assets"]),
            )
        pg.commit()

        upsert_many(
            pg,
            """insert into edu_raw.sources(source_id,name,url,source_type,authority,notes)
               values (%s,%s,%s,%s,%s,%s)
               on conflict (source_id) do update set
                 name=excluded.name,url=excluded.url,source_type=excluded.source_type,
                 authority=excluded.authority,notes=excluded.notes""",
            sqlite_db.execute("select source_id,name,url,source_type,authority,notes from sources order by source_id"),
            batch_size,
        )

        upsert_many(
            pg,
            """insert into edu_raw.raw_records
               (source_id,source_record_id,entity_family,entity_type_raw,name_raw,name_ar_raw,
                name_en_raw,location_raw,latitude,longitude,source_url,retrieved_at,raw_hash,payload_json)
               values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
               on conflict (source_id,raw_hash) do nothing""",
            sqlite_db.execute(
                """select source_id,source_record_id,entity_family,entity_type_raw,name_raw,
                          name_ar_raw,name_en_raw,location_raw,latitude,longitude,source_url,
                          retrieved_at,raw_hash,payload_json
                   from raw_records order by raw_id"""
            ),
            batch_size,
        )

        upsert_many(
            pg,
            """insert into edu_raw.storage_owners(owner_id,display_name,created_at)
               values (%s,%s,%s)
               on conflict (owner_id) do update set display_name=excluded.display_name""",
            sqlite_db.execute("select owner_id,display_name,created_at from storage_owners"),
            batch_size,
        )

        upsert_many(
            pg,
            """insert into edu_raw.acquisition_runs
               (source_id,started_at,finished_at,status,records_added,error,archive_version,archive_run_id)
               values (%s,%s,%s,%s,%s,%s,7,%s)
               on conflict (archive_version,archive_run_id)
               where archive_version is not null and archive_run_id is not null
               do update set
                 source_id=excluded.source_id,started_at=excluded.started_at,
                 finished_at=excluded.finished_at,status=excluded.status,
                 records_added=excluded.records_added,error=excluded.error""",
            sqlite_db.execute(
                """select source_id,started_at,finished_at,status,records_added,error,run_id
                   from acquisition_runs order by run_id"""
            ),
            batch_size,
        )

        upsert_many(
            pg,
            """insert into edu_raw.coverage_targets
               (target_id,label,official_count,target_basis,reference_url)
               values (%s,%s,%s,%s,%s)
               on conflict (target_id) do update set
                 label=excluded.label,official_count=excluded.official_count,
                 target_basis=excluded.target_basis,reference_url=excluded.reference_url,
                 updated_at=now()""",
            sqlite_db.execute(
                """select target_id,label,official_count,target_basis,reference_url
                   from coverage_targets order by target_id"""
            ),
            batch_size,
        )

        upsert_many(
            pg,
            """insert into edu_raw.record_ownership
               (raw_id,owner_id,ownership_status,first_stored_at,last_verified_at,payload_sha256)
               select r.raw_id,%s,%s,%s,%s,%s
               from edu_raw.raw_records r where r.source_id=%s and r.raw_hash=%s
               on conflict (raw_id) do update set
                 owner_id=excluded.owner_id,ownership_status=excluded.ownership_status,
                 last_verified_at=excluded.last_verified_at,payload_sha256=excluded.payload_sha256""",
            (
                (owner_id, status, first_at, verified_at, payload_hash, source_id, raw_hash)
                for owner_id, status, first_at, verified_at, payload_hash, source_id, raw_hash in sqlite_db.execute(
                    """select o.owner_id,o.ownership_status,o.first_stored_at,o.last_verified_at,
                              o.payload_sha256,r.source_id,r.raw_hash
                       from record_ownership o join raw_records r using(raw_id) order by r.raw_id"""
                )
            ),
            batch_size,
        )

        upsert_many(
            pg,
            """insert into edu_raw.media_files
               (file_sha256,storage_key,mime_type,byte_size,width,height,first_acquired_at)
               values (%s,%s,%s,%s,%s,%s,%s)
               on conflict (file_sha256) do update set
                 storage_key=excluded.storage_key,mime_type=excluded.mime_type,
                 byte_size=excluded.byte_size,width=excluded.width,height=excluded.height""",
            sqlite_db.execute(
                """select file_sha256,storage_key,mime_type,byte_size,width,height,first_acquired_at
                   from media_files order by file_sha256"""
            ),
            batch_size,
        )

        media_columns = [row[1] for row in sqlite_db.execute("pragma table_info(media_assets)") if row[1] != "media_id"]
        media_names = ",".join(media_columns)
        placeholders = ",".join(["%s"] * len(media_columns))
        updates = ",".join(
            f"{name}=excluded.{name}" for name in media_columns if name not in {"source_id", "source_record_id", "original_url"}
        )
        upsert_many(
            pg,
            f"""insert into edu_raw.media_assets({media_names}) values ({placeholders})
                on conflict (source_id,source_record_id,original_url) do update set {updates}""",
            sqlite_db.execute(f"select {media_names} from media_assets order by media_id"),
            batch_size,
        )

        upsert_many(
            pg,
            """insert into edu_raw.field_inventory
               (source_id,field_path,populated_records,distinct_sample_count,example_values_json)
               values (%s,%s,%s,%s,%s::jsonb)
               on conflict (source_id,field_path) do update set
                 populated_records=excluded.populated_records,
                 distinct_sample_count=excluded.distinct_sample_count,
                 example_values_json=excluded.example_values_json""",
            sqlite_db.execute(
                """select source_id,field_path,populated_records,distinct_sample_count,example_values_json
                   from field_inventory order by source_id,field_path"""
            ),
            batch_size,
        )

        with pg.cursor() as cursor:
            cursor.execute("analyze edu_raw.raw_records")
            cursor.execute("analyze edu_raw.media_assets")
            cursor.execute("select count(*) from edu_raw.raw_records")
            raw_count = cursor.fetchone()[0]
            cursor.execute("select count(*) from edu_raw.media_assets")
            media_count = cursor.fetchone()[0]
            if raw_count != EXPECTED["raw_records"] or media_count != EXPECTED["media_assets"]:
                raise RuntimeError(f"post-import count mismatch: records={raw_count}, media={media_count}")
            cursor.execute(
                """update edu_raw.import_batches set
                     status='verified',imported_records=%s,imported_media_assets=%s,finished_at=now()
                   where batch_id=%s""",
                (raw_count, media_count, batch_id),
            )
        pg.commit()
        return {"ok": True, "batch_id": str(batch_id), "records": raw_count, "media_assets": media_count}
    except Exception as exc:
        pg.rollback()
        with pg.cursor() as cursor:
            cursor.execute(
                """update edu_raw.import_batches set status='failed',error=%s,finished_at=now()
                   where batch_id=%s""",
                (repr(exc), batch_id),
            )
        pg.commit()
        raise
    finally:
        pg.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", required=True, type=Path)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--database-url", help="PostgreSQL URL; omit for a non-mutating dry run")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.batch_size < 1:
        raise SystemExit("--batch-size must be positive")

    sqlite_db = sqlite3.connect(f"file:{args.sqlite}?mode=ro", uri=True)
    validation = validate_sqlite(sqlite_db)
    archive_hash = sha256_file(args.archive) if args.archive else "unknown"
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "mode": "live-import" if args.database_url else "dry-run",
        "sqlite": str(args.sqlite),
        "archive": str(args.archive) if args.archive else None,
        "archive_sha256": archive_hash,
        "validation": validation,
    }
    if validation["ok"] and args.database_url:
        report["import"] = import_archive(
            sqlite_db, args.database_url, archive_hash, args.archive.name if args.archive else args.sqlite.name, args.batch_size
        )
    sqlite_db.close()
    report["ok"] = validation["ok"] and (not args.database_url or report.get("import", {}).get("ok", False))
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
