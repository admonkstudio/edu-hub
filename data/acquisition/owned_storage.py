#!/usr/bin/env python3
"""Edu Hub raw record and media ownership storage.

The source URL is provenance. The database row and content-addressed media file
are the locally held acquisition copy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OWNER_ID = "edu-hub"
OWNER_NAME = "Edu Hub"
MAX_MEDIA_BYTES = 30 * 1024 * 1024


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA journal_mode = WAL")
    return db


def init(db_path: Path, schema_path: Path) -> None:
    with connect(db_path) as db:
        db.executescript(schema_path.read_text(encoding="utf-8"))
        timestamp = now()
        db.execute(
            "INSERT OR IGNORE INTO storage_owners(owner_id, display_name, created_at) VALUES (?, ?, ?)",
            (OWNER_ID, OWNER_NAME, timestamp),
        )
        rows = db.execute("SELECT raw_id, raw_hash, payload_json, retrieved_at FROM raw_records").fetchall()
        for row in rows:
            digest = hashlib.sha256(row["payload_json"].encode("utf-8")).hexdigest()
            db.execute(
                """INSERT OR IGNORE INTO record_ownership
                   (raw_id, owner_id, first_stored_at, last_verified_at, payload_sha256)
                   VALUES (?, ?, ?, ?, ?)""",
                (row["raw_id"], OWNER_ID, row["retrieved_at"], timestamp, digest),
            )


def register_media(db: sqlite3.Connection, item: dict[str, Any]) -> int:
    discovered_at = item.get("discovered_at") or now()
    raw_id = item.get("raw_id")
    source_id = item.get("source_id")
    source_record_id = item.get("source_record_id")
    if raw_id is not None:
        record = db.execute(
            "SELECT source_id, source_record_id, source_url FROM raw_records WHERE raw_id = ?", (raw_id,)
        ).fetchone()
        if not record:
            raise ValueError(f"raw_id {raw_id} does not exist")
        source_id = source_id or record["source_id"]
        source_record_id = source_record_id or record["source_record_id"]
        item.setdefault("source_page_url", record["source_url"])
    if not source_id:
        raise ValueError("source_id is required when raw_id is absent")
    values = (
        raw_id,
        source_id,
        source_record_id,
        item.get("source_page_url"),
        item["original_url"],
        item.get("media_type", "unknown"),
        item.get("alt_text"),
        discovered_at,
        item.get("rights_status", "unknown"),
        item.get("license_name"),
        item.get("copyright_owner"),
        item.get("credit_text"),
        int(bool(item.get("public_reuse_allowed", False))),
        json.dumps(item.get("metadata", {}), ensure_ascii=False, sort_keys=True),
    )
    db.execute(
        """INSERT INTO raw_media
           (raw_id, source_id, source_record_id, source_page_url, original_url,
            media_type, alt_text, discovered_at, rights_status, license_name,
            copyright_owner, credit_text, public_reuse_allowed, metadata_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(source_id, original_url, source_record_id) DO UPDATE SET
             raw_id = COALESCE(excluded.raw_id, raw_media.raw_id),
             source_page_url = COALESCE(excluded.source_page_url, raw_media.source_page_url),
             media_type = CASE WHEN raw_media.media_type = 'unknown' THEN excluded.media_type ELSE raw_media.media_type END,
             alt_text = COALESCE(excluded.alt_text, raw_media.alt_text),
             metadata_json = excluded.metadata_json""",
        values,
    )
    row = db.execute(
        "SELECT raw_media_id FROM raw_media WHERE source_id = ? AND original_url = ? AND source_record_id IS ?",
        (source_id, item["original_url"], source_record_id),
    ).fetchone()
    return int(row[0])


def sniff_image(data: bytes, content_type: str | None) -> tuple[str, str]:
    signatures = (
        (b"\xff\xd8\xff", "image/jpeg", ".jpg"),
        (b"\x89PNG\r\n\x1a\n", "image/png", ".png"),
        (b"GIF87a", "image/gif", ".gif"),
        (b"GIF89a", "image/gif", ".gif"),
        (b"RIFF", "image/webp", ".webp"),
    )
    for signature, mime, extension in signatures:
        if data.startswith(signature):
            if mime == "image/webp" and data[8:12] != b"WEBP":
                continue
            return mime, extension
    if data.lstrip().startswith(b"<svg") or b"<svg" in data[:512].lower():
        return "image/svg+xml", ".svg"
    if content_type and content_type.split(";", 1)[0].strip().startswith("image/"):
        mime = content_type.split(";", 1)[0].strip().lower()
        return mime, mimetypes.guess_extension(mime) or ".img"
    raise ValueError("response is not a recognized image")


def image_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        from PIL import Image
        with Image.open(path) as image:
            return image.size
    except Exception:
        return None, None


def fetch_one(db: sqlite3.Connection, media_id: int, store_root: Path) -> None:
    row = db.execute("SELECT * FROM raw_media WHERE raw_media_id = ?", (media_id,)).fetchone()
    if not row:
        raise ValueError(f"raw_media_id {media_id} does not exist")
    attempted_at = now()
    try:
        request = urllib.request.Request(row["original_url"], headers={"User-Agent": "EduHubMediaAcquisition/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            declared = int(response.headers.get("Content-Length") or 0)
            if declared > MAX_MEDIA_BYTES:
                raise ValueError(f"media exceeds {MAX_MEDIA_BYTES} bytes")
            data = response.read(MAX_MEDIA_BYTES + 1)
            if len(data) > MAX_MEDIA_BYTES:
                raise ValueError(f"media exceeds {MAX_MEDIA_BYTES} bytes")
            mime, extension = sniff_image(data, response.headers.get("Content-Type"))
            http_status = getattr(response, "status", 200)
        digest = hashlib.sha256(data).hexdigest()
        storage_key = f"sha256/{digest[:2]}/{digest[2:4]}/{digest}{extension}"
        target = store_root / storage_key
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        width, height = image_dimensions(target)
        verified_at = now()
        db.execute(
            """INSERT OR IGNORE INTO media_files
               (owner_id, sha256, storage_backend, storage_key, mime_type,
                file_extension, byte_size, width, height, downloaded_at, verified_at)
               VALUES (?, ?, 'local', ?, ?, ?, ?, ?, ?, ?, ?)""",
            (OWNER_ID, digest, storage_key, mime, extension, len(data), width, height, attempted_at, verified_at),
        )
        file_id = db.execute("SELECT media_file_id FROM media_files WHERE sha256 = ?", (digest,)).fetchone()[0]
        db.execute(
            """UPDATE raw_media SET media_file_id = ?, retrieval_status = 'downloaded',
               last_attempted_at = ?, failure_reason = NULL WHERE raw_media_id = ?""",
            (file_id, attempted_at, media_id),
        )
        db.execute(
            """INSERT INTO media_fetch_attempts
               (raw_media_id, attempted_at, outcome, http_status, bytes_received)
               VALUES (?, ?, 'downloaded', ?, ?)""",
            (media_id, attempted_at, http_status, len(data)),
        )
    except Exception as exc:
        status = exc.code if isinstance(exc, urllib.error.HTTPError) else None
        outcome = "blocked" if status in (401, 403, 429) else "failed"
        db.execute(
            "UPDATE raw_media SET retrieval_status = ?, last_attempted_at = ?, failure_reason = ? WHERE raw_media_id = ?",
            (outcome, attempted_at, str(exc)[:1000], media_id),
        )
        db.execute(
            """INSERT INTO media_fetch_attempts
               (raw_media_id, attempted_at, outcome, http_status, error)
               VALUES (?, ?, ?, ?, ?)""",
            (media_id, attempted_at, outcome, status, str(exc)[:1000]),
        )
        raise


def import_manifest(db_path: Path, manifest: Path) -> int:
    count = 0
    with connect(db_path) as db, manifest.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                register_media(db, json.loads(line))
                count += 1
            except Exception as exc:
                raise ValueError(f"{manifest}:{line_number}: {exc}") from exc
    return count


def fetch_pending(db_path: Path, store_root: Path, limit: int) -> tuple[int, int]:
    succeeded = failed = 0
    with connect(db_path) as db:
        ids = [row[0] for row in db.execute(
            "SELECT raw_media_id FROM raw_media WHERE retrieval_status IN ('discovered', 'failed') ORDER BY raw_media_id LIMIT ?",
            (limit,),
        )]
        for media_id in ids:
            try:
                fetch_one(db, media_id, store_root)
                db.commit()
                succeeded += 1
            except Exception as exc:
                db.commit()
                failed += 1
                print(f"media {media_id}: {exc}", file=sys.stderr)
    return succeeded, failed


def report(db_path: Path) -> list[dict[str, Any]]:
    with connect(db_path) as db:
        return [dict(row) for row in db.execute("SELECT * FROM media_coverage_by_source ORDER BY source_id")]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    init_parser = sub.add_parser("init")
    init_parser.add_argument("--schema", type=Path, default=Path(__file__).with_name("schema.sql"))
    import_parser = sub.add_parser("import-media")
    import_parser.add_argument("manifest", type=Path)
    fetch_parser = sub.add_parser("fetch-media")
    fetch_parser.add_argument("--store", type=Path, required=True)
    fetch_parser.add_argument("--limit", type=int, default=100)
    sub.add_parser("report")
    args = parser.parse_args()
    if args.command == "init":
        init(args.db, args.schema)
        print(json.dumps({"status": "initialized", "database": str(args.db)}))
    elif args.command == "import-media":
        print(json.dumps({"registered": import_manifest(args.db, args.manifest)}))
    elif args.command == "fetch-media":
        succeeded, failed = fetch_pending(args.db, args.store, args.limit)
        print(json.dumps({"downloaded": succeeded, "failed": failed}))
    elif args.command == "report":
        print(json.dumps(report(args.db), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

