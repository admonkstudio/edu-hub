#!/usr/bin/env python3
"""Ingest a MadaresEgypt listing snapshot into the raw-first Edu Hub SQLite DB.

This script does not canonicalize, match, or deduplicate across sources. It only
adds one secondary source assertion per unique MadaresEgypt payload hash, then
rebuilds the field census and source-count reports.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SOURCE_ID = "madaresegypt_public_directory"
SOURCE = {
    "name": "MadaresEgypt public schools and nurseries directory snapshot",
    "url": "https://madaresegypt.com/",
    "source_type": "secondary_directory_snapshot",
    "authority": "secondary",
    "notes": "Public listing-level directory used for institution discovery and field census. Not proof of licensing, accreditation or current regulatory status.",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_source(db: sqlite3.Connection) -> None:
    db.execute(
        "INSERT OR REPLACE INTO sources(source_id,name,url,source_type,authority,notes) VALUES(?,?,?,?,?,?)",
        (SOURCE_ID, SOURCE["name"], SOURCE["url"], SOURCE["source_type"], SOURCE["authority"], SOURCE["notes"]),
    )
    db.commit()


def add_record(db: sqlite3.Connection, row: dict) -> bool:
    payload = row.get("payload") or {}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    h = hashlib.sha256((SOURCE_ID + "\n" + raw).encode()).hexdigest()
    entity_type = row.get("entity_type_raw") or "school"
    family = "early_education" if "nursery" in str(entity_type).lower() else "pre_university"
    try:
        db.execute(
            """INSERT INTO raw_records(
                source_id,source_record_id,entity_family,entity_type_raw,name_raw,name_ar_raw,name_en_raw,
                location_raw,latitude,longitude,source_url,retrieved_at,raw_hash,payload_json
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                SOURCE_ID,
                row.get("source_record_id"),
                family,
                entity_type,
                row.get("name_raw"),
                row.get("name_ar_raw"),
                row.get("name_en_raw"),
                row.get("location_raw"),
                row.get("latitude"),
                row.get("longitude"),
                row.get("source_url"),
                now(),
                h,
                raw,
            ),
        )
        return True
    except sqlite3.IntegrityError:
        return False


def walk_fields(value, prefix=""):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from walk_fields(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(value, list):
        yield prefix, value
    else:
        yield prefix, value


def rebuild_field_inventory(db: sqlite3.Connection) -> None:
    db.execute("DELETE FROM field_inventory")
    for (sid,) in db.execute("SELECT source_id FROM sources"):
        counts = Counter()
        examples = defaultdict(list)
        distinct = defaultdict(set)
        for (payload_json,) in db.execute("SELECT payload_json FROM raw_records WHERE source_id=?", (sid,)):
            for path, value in walk_fields(json.loads(payload_json)):
                if not path or value in (None, "", [], {}):
                    continue
                counts[path] += 1
                sample = json.dumps(value, ensure_ascii=False, default=str) if isinstance(value, (dict, list)) else str(value)
                if len(distinct[path]) < 1000:
                    distinct[path].add(sample)
                if len(examples[path]) < 5 and sample not in examples[path]:
                    examples[path].append(sample[:500])
        for path, count in counts.items():
            db.execute(
                "INSERT INTO field_inventory(source_id,field_path,populated_records,distinct_sample_count,example_values_json) VALUES(?,?,?,?,?)",
                (sid, path, count, len(distinct[path]), json.dumps(examples[path], ensure_ascii=False)),
            )
    db.commit()


def export_reports(db: sqlite3.Connection, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    source_counts = list(db.execute(
        """SELECT s.source_id,s.name,s.authority,COUNT(r.raw_id),
        SUM(CASE WHEN r.name_raw IS NOT NULL AND TRIM(r.name_raw)<>'' THEN 1 ELSE 0 END)
        FROM sources s LEFT JOIN raw_records r ON r.source_id=s.source_id
        GROUP BY s.source_id,s.name,s.authority ORDER BY COUNT(r.raw_id) DESC"""
    ))
    with (outdir / "source_counts.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source_id", "source_name", "authority", "raw_records", "named_records"])
        w.writerows(source_counts)

    inventory = list(db.execute(
        "SELECT source_id,field_path,populated_records,distinct_sample_count,example_values_json FROM field_inventory ORDER BY source_id,populated_records DESC,field_path"
    ))
    with (outdir / "field_inventory.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source_id", "field_path", "populated_records", "distinct_sample_count", "example_values_json"])
        w.writerows(inventory)

    coverage = list(db.execute("SELECT target_id,label,official_count,target_basis,reference_url FROM coverage_targets ORDER BY target_id"))
    with (outdir / "coverage.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target_id", "label", "official_count", "target_basis", "reference_url"])
        w.writerows(coverage)

    summary = {
        "generated_at": now(),
        "principle": "raw-first; no cross-source deduplication or canonical merging performed",
        "raw_record_count": db.execute("SELECT COUNT(*) FROM raw_records").fetchone()[0],
        "named_raw_record_count": db.execute("SELECT COUNT(*) FROM raw_records WHERE name_raw IS NOT NULL AND TRIM(name_raw)<>''").fetchone()[0],
        "source_counts": [
            {"source_id": r[0], "source_name": r[1], "authority": r[2], "raw_records": r[3], "named_records": r[4]}
            for r in source_counts
        ],
        "known_coverage_targets": [
            {"target_id": r[0], "label": r[1], "official_count": r[2], "basis": r[3], "url": r[4]}
            for r in coverage
        ],
        "warning": "Raw record count is not unique-institution count. Duplicates across sources are intentionally preserved.",
    }
    (outdir / "acquisition_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    db = sqlite3.connect(args.db)
    ensure_source(db)
    started = now()
    cur = db.execute("INSERT INTO acquisition_runs(source_id,started_at,status) VALUES(?,?,?)", (SOURCE_ID, started, "running"))
    run_id = int(cur.lastrowid)
    seen = 0
    added = 0
    try:
        for line in Path(args.snapshot).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            seen += 1
            if add_record(db, json.loads(line)):
                added += 1
        db.commit()
        db.execute("UPDATE acquisition_runs SET finished_at=?,status='completed',records_added=? WHERE run_id=?", (now(), added, run_id))
        db.commit()
        rebuild_field_inventory(db)
        export_reports(db, Path(args.outdir))
        total = db.execute("SELECT COUNT(*) FROM raw_records").fetchone()[0]
        print(json.dumps({"ok": True, "seen": seen, "added": added, "total_raw_records": total}, ensure_ascii=False))
    except Exception as exc:
        db.rollback()
        db.execute("UPDATE acquisition_runs SET finished_at=?,status='failed',records_added=?,error=? WHERE run_id=?", (now(), added, repr(exc), run_id))
        db.commit()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
