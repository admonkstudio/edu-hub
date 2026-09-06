#!/usr/bin/env python3
"""Mirror discovered public media candidates into Edu Hub-controlled storage.

The archive owns/controls the stored copy operationally. Copyright/publication rights
remain separate metadata and default to unknown/not-public.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import mimetypes
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from PIL import Image
except Exception:  # Pillow is optional; dimensions remain null when unavailable.
    Image = None

UA = "EduHubResearchBot/2.0 (+https://github.com/admonkstudio/edu-hub; owned-media-archive)"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": UA, "Accept": "image/avif,image/webp,image/*,*/*;q=0.5"})
    return s


def setup(db: sqlite3.Connection) -> None:
    db.executescript("""
    PRAGMA journal_mode=WAL;
    PRAGMA foreign_keys=ON;

    CREATE TABLE IF NOT EXISTS media_assets (
      media_id INTEGER PRIMARY KEY AUTOINCREMENT,
      source_id TEXT NOT NULL,
      source_record_id TEXT,
      source_name_raw TEXT,
      source_page_url TEXT NOT NULL,
      original_url TEXT NOT NULL,
      candidate_index INTEGER,
      role_raw TEXT,
      alt_raw TEXT,
      title_raw TEXT,
      width_hint INTEGER,
      height_hint INTEGER,
      discovery_method TEXT,
      discovered_at TEXT NOT NULL,
      rights_status TEXT NOT NULL DEFAULT 'unknown',
      public_use_allowed INTEGER NOT NULL DEFAULT 0,
      mirror_status TEXT NOT NULL DEFAULT 'discovered',
      file_sha256 TEXT,
      storage_key TEXT,
      mime_type TEXT,
      byte_size INTEGER,
      width INTEGER,
      height INTEGER,
      acquired_at TEXT,
      error TEXT,
      UNIQUE(source_id, source_record_id, original_url)
    );

    CREATE INDEX IF NOT EXISTS idx_media_source_record
      ON media_assets(source_id, source_record_id);
    CREATE INDEX IF NOT EXISTS idx_media_sha
      ON media_assets(file_sha256);
    CREATE INDEX IF NOT EXISTS idx_media_rights
      ON media_assets(rights_status, public_use_allowed);

    CREATE TABLE IF NOT EXISTS media_files (
      file_sha256 TEXT PRIMARY KEY,
      storage_key TEXT NOT NULL,
      mime_type TEXT,
      byte_size INTEGER NOT NULL,
      width INTEGER,
      height INTEGER,
      first_acquired_at TEXT NOT NULL
    );
    """)
    db.commit()


def ext_for(mime: str | None, url: str) -> str:
    if mime:
        m = mime.split(";", 1)[0].strip().lower()
        overrides = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/avif": ".avif",
            "image/gif": ".gif",
            "image/svg+xml": ".svg",
        }
        if m in overrides:
            return overrides[m]
        guess = mimetypes.guess_extension(m)
        if guess:
            return guess
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".svg"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    return ".img"


def dimensions(data: bytes, mime: str | None) -> tuple[int | None, int | None]:
    if Image is None or (mime and mime.lower().startswith("image/svg")):
        return None, None
    try:
        with Image.open(io.BytesIO(data)) as im:
            return int(im.width), int(im.height)
    except Exception:
        return None, None


def insert_candidate(db: sqlite3.Connection, row: dict) -> int:
    db.execute(
        """INSERT OR IGNORE INTO media_assets(
          source_id,source_record_id,source_name_raw,source_page_url,original_url,candidate_index,
          role_raw,alt_raw,title_raw,width_hint,height_hint,discovery_method,discovered_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            row.get("source_id"), row.get("source_record_id"), row.get("source_name_raw"),
            row.get("source_page_url"), row.get("media_url"), row.get("candidate_index"),
            row.get("role_raw"), row.get("alt_raw"), row.get("title_raw"),
            row.get("width_hint"), row.get("height_hint"), row.get("discovery_method"), now(),
        ),
    )
    rec = db.execute(
        "SELECT media_id FROM media_assets WHERE source_id=? AND source_record_id IS ? AND original_url=?",
        (row.get("source_id"), row.get("source_record_id"), row.get("media_url")),
    ).fetchone()
    if not rec:
        raise RuntimeError("candidate insert/lookup failed")
    return int(rec[0])


def mirror_one(s: requests.Session, db: sqlite3.Connection, media_id: int, row: dict,
               media_root: Path, max_bytes: int) -> bool:
    url = row["media_url"]
    try:
        r = s.get(url, timeout=60, allow_redirects=True)
        r.raise_for_status()
        data = r.content
        if not data:
            raise ValueError("empty media response")
        if len(data) > max_bytes:
            raise ValueError(f"media exceeds max bytes: {len(data)} > {max_bytes}")
        mime = (r.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower() or None
        if mime and not mime.startswith("image/"):
            raise ValueError(f"not an image content type: {mime}")
        sha = hashlib.sha256(data).hexdigest()
        width, height = dimensions(data, mime)
        ext = ext_for(mime, r.url)
        source_id = row.get("source_id") or "unknown-source"
        storage_key = f"raw-media/{source_id}/{sha[:2]}/{sha}{ext}"
        target = media_root / storage_key
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)

        db.execute(
            """INSERT OR IGNORE INTO media_files(
              file_sha256,storage_key,mime_type,byte_size,width,height,first_acquired_at
            ) VALUES(?,?,?,?,?,?,?)""",
            (sha, storage_key, mime, len(data), width, height, now()),
        )
        db.execute(
            """UPDATE media_assets SET mirror_status='mirrored',file_sha256=?,storage_key=?,mime_type=?,
              byte_size=?,width=?,height=?,acquired_at=?,error=NULL WHERE media_id=?""",
            (sha, storage_key, mime, len(data), width, height, now(), media_id),
        )
        db.commit()
        return True
    except Exception as exc:
        db.execute(
            "UPDATE media_assets SET mirror_status='failed',error=? WHERE media_id=?",
            (repr(exc), media_id),
        )
        db.commit()
        return False


def export_coverage(db: sqlite3.Connection, path: Path) -> None:
    rows = list(db.execute("""
      SELECT source_id,
        COUNT(DISTINCT source_record_id) AS records_with_candidates,
        COUNT(*) AS candidates,
        SUM(CASE WHEN mirror_status='mirrored' THEN 1 ELSE 0 END) AS mirrored_assets,
        COUNT(DISTINCT CASE WHEN mirror_status='mirrored' THEN source_record_id END) AS records_with_mirrors,
        SUM(CASE WHEN role_raw='logo_candidate' THEN 1 ELSE 0 END) AS logo_candidates,
        SUM(CASE WHEN role_raw='featured_candidate' THEN 1 ELSE 0 END) AS featured_candidates,
        SUM(CASE WHEN public_use_allowed=1 THEN 1 ELSE 0 END) AS public_eligible_assets
      FROM media_assets
      GROUP BY source_id
      ORDER BY candidates DESC
    """))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "source_id", "records_with_candidates", "media_candidates", "mirrored_assets",
            "records_with_mirrors", "logo_candidates", "featured_candidates", "public_eligible_assets",
        ])
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Media candidate JSONL from discover_media.py")
    ap.add_argument("--db", required=True, help="Owned media SQLite registry")
    ap.add_argument("--media-root", required=True, help="Directory that holds mirrored binary files")
    ap.add_argument("--coverage", default="artifacts/media_coverage.csv")
    ap.add_argument("--max-bytes", type=int, default=20 * 1024 * 1024)
    ap.add_argument("--max-assets", type=int, default=0)
    args = ap.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path)
    setup(db)
    media_root = Path(args.media_root)
    s = session()

    seen = mirrored = failed = 0
    with Path(args.input).open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            if args.max_assets and seen >= args.max_assets:
                break
            row = json.loads(line)
            if not row.get("media_url") or not row.get("source_id") or not row.get("source_page_url"):
                continue
            seen += 1
            media_id = insert_candidate(db, row)
            existing = db.execute("SELECT mirror_status FROM media_assets WHERE media_id=?", (media_id,)).fetchone()
            if existing and existing[0] == "mirrored":
                mirrored += 1
                continue
            if mirror_one(s, db, media_id, row, media_root, args.max_bytes):
                mirrored += 1
            else:
                failed += 1
            if seen % 100 == 0:
                print(json.dumps({"seen": seen, "mirrored": mirrored, "failed": failed}), flush=True)

    export_coverage(db, Path(args.coverage))
    summary = {
        "ok": failed == 0,
        "seen": seen,
        "mirrored": mirrored,
        "failed": failed,
        "registry_db": str(db_path),
        "media_root": str(media_root),
        "coverage": args.coverage,
        "rights_default": "unknown",
        "public_use_allowed_default": False,
    }
    Path(args.coverage).with_suffix(".summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
