#!/usr/bin/env python3
"""Compare the owned V7 raw archive to the current D2.1 source/lead universe.

V7 is historical/supporting evidence only. This tool opens the V7 SQLite archive
read-only, selects rows with likely international-education name signals plus
exact current-universe names, and separates deterministic normalized-name
overlaps from unmatched legacy review leads.

It intentionally performs no fuzzy matching, no eligibility decisions, no
identity creation, no canonical writes and no public projection. Any unmatched
legacy lead must be re-sourced from a current permitted source before it can be
used beyond discovery/review.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

EN_SIGNALS = [
    "international", "american", "british", "french", "german", "deutsch", "canadian",
    "japanese", "korean", "italian", "spanish", "swiss", "baccalaureate", "montessori",
    "choueifat", "sabis", "ib world", "foreign university", "university branch",
]
AR_SIGNALS = [
    "دولي", "دولية", "أمريكي", "امريكي", "أمريكية", "امريكية", "بريطاني", "بريطانية",
    "فرنسي", "فرنسية", "ألماني", "الماني", "ألمانية", "المانية", "كندي", "كندية",
    "ياباني", "يابانية", "إيطالي", "ايطالي", "إيطالية", "ايطالية", "إسباني", "اسباني",
    "سويسري", "سويسرية", "بكالوريا", "منتسوري", "سابس", "جامعة أجنبية", "جامعة اجنبية",
]


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def compact(value: object) -> str | None:
    text = " ".join(str(value or "").split()).strip()
    return text or None


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def has_signal(*values: object) -> bool:
    joined = " ".join(compact(value) or "" for value in values).casefold()
    return any(signal.casefold() in joined for signal in EN_SIGNALS + AR_SIGNALS)


def open_readonly(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise FileNotFoundError(path)
    return sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)


def build(v7_db: Path, universe_path: Path, output_dir: Path) -> dict:
    universe = read_jsonl(universe_path)
    current_names: dict[str, list[dict]] = defaultdict(list)
    for row in universe:
        for field in ("name_en", "name_ar"):
            key = normalize(row.get(field))
            if key:
                current_names[key].append(row)

    db = open_readonly(v7_db)
    table = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='raw_records'"
    ).fetchone()
    if not table:
        raise RuntimeError("V7 database does not contain raw_records")
    total_records = db.execute("SELECT COUNT(*) FROM raw_records").fetchone()[0]
    columns = {row[1] for row in db.execute("PRAGMA table_info(raw_records)")}
    required = {
        "raw_id", "source_id", "source_record_id", "entity_family", "entity_type_raw",
        "name_raw", "name_ar_raw", "name_en_raw", "location_raw", "latitude", "longitude",
        "source_url", "retrieved_at", "raw_hash", "payload_json",
    }
    missing = sorted(required - columns)
    if missing:
        raise RuntimeError(f"V7 raw_records schema missing columns: {missing}")

    rows = db.execute(
        """SELECT raw_id,source_id,source_record_id,entity_family,entity_type_raw,
                  name_raw,name_ar_raw,name_en_raw,location_raw,latitude,longitude,
                  source_url,retrieved_at,raw_hash
           FROM raw_records
           ORDER BY raw_id"""
    )

    selected: list[dict] = []
    exact_overlaps: list[dict] = []
    unmatched: list[dict] = []
    for values in rows:
        (
            raw_id, source_id, source_record_id, entity_family, entity_type_raw,
            name_raw, name_ar_raw, name_en_raw, location_raw, latitude, longitude,
            source_url, retrieved_at, raw_hash,
        ) = values
        candidate_names = [name_en_raw, name_ar_raw, name_raw]
        normalized_candidates = [normalize(value) for value in candidate_names if normalize(value)]
        exact_keys = [key for key in normalized_candidates if key in current_names]
        signaled = has_signal(name_raw, name_ar_raw, name_en_raw, entity_type_raw)
        if not signaled and not exact_keys:
            continue
        record = {
            "v7_raw_id": raw_id,
            "v7_source_id": source_id,
            "v7_source_record_id": source_record_id,
            "entity_family": entity_family,
            "entity_type_raw": compact(entity_type_raw),
            "name_raw": compact(name_raw),
            "name_ar_raw": compact(name_ar_raw),
            "name_en_raw": compact(name_en_raw),
            "location_raw": compact(location_raw),
            "latitude": latitude,
            "longitude": longitude,
            "source_url": compact(source_url),
            "retrieved_at": compact(retrieved_at),
            "raw_hash": raw_hash,
            "international_name_signal": signaled,
            "normalized_name_candidates": normalized_candidates,
            "current_exact_match_keys": sorted(set(exact_keys)),
            "source_role": "historical_owned_archive_supporting_discovery_only",
            "international_eligibility_granted": False,
        }
        selected.append(record)
        if exact_keys:
            memberships = []
            seen = set()
            for key in sorted(set(exact_keys)):
                for current in current_names[key]:
                    token = (current.get("source_id"), current.get("source_record_id"), key)
                    if token in seen:
                        continue
                    seen.add(token)
                    memberships.append({
                        "match_key": key,
                        "current_source_id": current.get("source_id"),
                        "current_source_record_id": current.get("source_record_id"),
                        "current_name_en": current.get("name_en"),
                        "current_name_ar": current.get("name_ar"),
                        "match_basis": "exact_normalized_name_review_hint_only",
                        "identity_merge_performed": False,
                    })
            exact_overlaps.append({**record, "current_source_matches": memberships})
        else:
            unmatched.append({
                **record,
                "review_state": "legacy_gap_candidate_requires_current_resourcing",
                "auto_add_to_d2_1_universe": False,
            })
    db.close()

    grouped: dict[str, list[int]] = defaultdict(list)
    for record in unmatched:
        preferred = normalize(record.get("name_en_raw") or record.get("name_raw") or record.get("name_ar_raw"))
        grouped[preferred or f"raw:{record['v7_raw_id']}"] .append(record["v7_raw_id"])
    unmatched_groups = [
        {"normalized_name": key, "v7_raw_ids": ids, "record_count": len(ids)}
        for key, ids in sorted(grouped.items())
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, data in (
        ("v7-selected-supporting-rows.jsonl", selected),
        ("v7-exact-name-overlaps.jsonl", exact_overlaps),
        ("v7-unmatched-gap-candidates.jsonl", unmatched),
    ):
        with (output_dir / filename).open("w", encoding="utf-8") as handle:
            for item in data:
                handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    (output_dir / "v7-unmatched-normalized-groups.json").write_text(
        json.dumps(unmatched_groups, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    source_counts = Counter(str(row.get("v7_source_id") or "unknown") for row in selected)
    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_v7_owned_archive_international_gap_review",
        "v7_total_raw_records": total_records,
        "expected_v7_total_raw_records": 24916,
        "current_universe_source_rows": len(universe),
        "selected_legacy_supporting_rows": len(selected),
        "exact_normalized_name_overlap_rows": len(exact_overlaps),
        "unmatched_legacy_gap_candidate_rows": len(unmatched),
        "unmatched_normalized_name_groups": len(unmatched_groups),
        "selected_rows_by_v7_source": dict(sorted(source_counts.items())),
        "fuzzy_matches_performed": 0,
        "legacy_rows_auto_added_to_universe": 0,
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_identity_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "current_resourcing_required_for_unmatched_leads": True,
    }
    if total_records != 24916:
        raise RuntimeError(f"Unexpected V7 raw-record count: {total_records}")
    (output_dir / "v7-gap-review-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v7-db", type=Path, required=True)
    parser.add_argument("--universe", type=Path, required=True)
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("artifacts/international/v7-international-gap-review"),
    )
    args = parser.parse_args()
    build(args.v7_db, args.universe, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
