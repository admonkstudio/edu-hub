#!/usr/bin/env python3
"""Apply the reviewed UK DfE BSO ownership/scope decisions to EDU-DATA-2.

This overlay consumes the already-upgraded 96-row source universe after all
accepted incremental IB detail batches. It upgrades only the 11 exact current
BSO candidate rows whose private/independent/non-public gate has been reviewed
from source-backed evidence. Source record IDs and ordering are preserved.

The output remains a research/source artifact: no identity merge, canonical
runtime database write or public projection is performed.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_REVIEW = HERE / "seeds" / "bso-scope-review-2026-09-15.json"
DEFAULT_BASE = Path("artifacts/international/ib-incremental/authoritative-source-candidates-with-incremental-ib.jsonl")
DEFAULT_OUTPUT_DIR = Path("artifacts/international/bso-scope-review")
SOURCE_ID = "uk_dfe_bso_egypt_2026_08"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def count_states(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        state = row.get("scope_state") or "unknown"
        counts[state] = counts.get(state, 0) + 1
    return counts


def apply(base_path: Path, review_path: Path, output_dir: Path) -> dict:
    rows = load_jsonl(base_path)
    review = json.loads(review_path.read_text(encoding="utf-8"))

    if len(rows) != 96:
        raise AssertionError(f"unexpected upgraded base row count: {len(rows)}")
    before = count_states(rows)
    if before != {"candidate": 11, "eligible": 82, "excluded": 3}:
        raise AssertionError(f"unexpected pre-BSO-review state contract: {before}")

    if review.get("source_id") != SOURCE_ID:
        raise AssertionError(f"unexpected review source_id: {review.get('source_id')}")
    records = review.get("records") or []
    if review.get("records_count") != len(records) or len(records) != 11:
        raise AssertionError("BSO review must contain exactly 11 reviewed source rows")
    if review.get("summary") != {
        "reviewed_rows": 11,
        "eligible_rows": 11,
        "excluded_rows": 0,
        "needs_review_rows": 0,
    }:
        raise AssertionError("BSO review summary contract drifted")
    if any(record.get("scope_state") != "eligible" for record in records):
        raise AssertionError("every accepted BSO scope-review record must be eligible")
    if any(len(record.get("evidence_urls") or []) < 2 for record in records):
        raise AssertionError("every BSO scope-review record requires at least two evidence URLs")
    if any(not record.get("review_note") or not record.get("ownership_scope") for record in records):
        raise AssertionError("every BSO review record requires ownership_scope and review_note")

    ids_before = [row["source_record_id"] for row in rows]
    if len(ids_before) != len(set(ids_before)):
        raise AssertionError("source universe contains duplicate source_record_id values")

    bso_rows = [row for row in rows if row.get("source_id") == SOURCE_ID]
    if len(bso_rows) != 11:
        raise AssertionError(f"expected 11 BSO rows in upgraded base, found {len(bso_rows)}")
    if any(row.get("scope_state") != "candidate" for row in bso_rows):
        raise AssertionError("all BSO rows must still be candidate before the explicit BSO scope review")

    by_id = {row["source_record_id"]: row for row in bso_rows}
    review_ids = [record["source_record_id"] for record in records]
    if len(review_ids) != len(set(review_ids)):
        raise AssertionError("duplicate source_record_id in BSO review seed")
    if set(review_ids) != set(by_id):
        missing = sorted(set(by_id) - set(review_ids))
        unknown = sorted(set(review_ids) - set(by_id))
        raise AssertionError(f"BSO review/source mismatch missing={missing} unknown={unknown}")

    review_by_id = {record["source_record_id"]: record for record in records}
    upgraded: list[dict] = []
    applied: list[dict] = []

    for original in rows:
        row = dict(original)
        if row.get("source_id") == SOURCE_ID:
            decision = review_by_id[row["source_record_id"]]
            source_name = row.get("list_name_en") or row.get("name_en")
            if source_name != decision["name"]:
                raise AssertionError(
                    f"BSO review name drift for {row['source_record_id']}: source={source_name!r} review={decision['name']!r}"
                )
            if row.get("scope_state") != "candidate":
                raise AssertionError(f"BSO review may only upgrade candidate rows: {source_name}")
            source_record_id = row["source_record_id"]
            row.update(
                {
                    "scope_state": "eligible",
                    "ownership_scope": decision["ownership_scope"],
                    "eligibility_pending": None,
                    "scope_review_state": "reviewed_eligible",
                    "scope_review_snapshot_date": review["snapshot_date"],
                    "scope_review_method": decision["evidence_method"],
                    "scope_review_evidence_urls": list(decision["evidence_urls"]),
                    "scope_review_note": decision["review_note"],
                    "strong_evidence": "uk_dfe_bso_plus_reviewed_private_independent_scope",
                }
            )
            if row["source_record_id"] != source_record_id:
                raise AssertionError("BSO scope overlay changed source_record_id")
            applied.append(
                {
                    "name_en": row.get("name_en"),
                    "list_name_en": row.get("list_name_en"),
                    "source_record_id": source_record_id,
                    "official_identifier": row.get("official_identifier"),
                    "previous_scope_state": original.get("scope_state"),
                    "new_scope_state": row["scope_state"],
                    "ownership_scope": row["ownership_scope"],
                    "scope_review_method": row["scope_review_method"],
                    "scope_review_snapshot_date": row["scope_review_snapshot_date"],
                    "scope_review_evidence_urls": row["scope_review_evidence_urls"],
                }
            )
        upgraded.append(row)

    if len(applied) != 11:
        raise AssertionError(f"expected 11 applied BSO decisions, found {len(applied)}")
    if [row["source_record_id"] for row in upgraded] != ids_before:
        raise AssertionError("BSO scope overlay changed source identity order or IDs")

    after = count_states(upgraded)
    if after != {"eligible": 93, "excluded": 3}:
        raise AssertionError(f"unexpected post-BSO-review state contract: {after}")

    output_dir.mkdir(parents=True, exist_ok=True)
    upgraded_path = output_dir / "authoritative-source-candidates-with-bso-scope-review.jsonl"
    applied_path = output_dir / "bso-scope-review-applied.jsonl"
    write_jsonl(upgraded_path, upgraded)
    write_jsonl(applied_path, applied)

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_bso_private_independent_scope_integration",
        "source_rows": len(rows),
        "reviewed_bso_rows": len(records),
        "applied_rows": len(applied),
        "source_record_ids_changed": 0,
        "before_scope_states": before,
        "after_scope_states": after,
        "remaining_foundational_candidates": after.get("candidate", 0),
        "unique_institutions_claimed": None,
        "identity_merges_performed": 0,
        "canonical_institutions_created": 0,
        "canonical_database_rows_written": 0,
        "runtime_database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "upgraded_base": upgraded_path.name,
            "applied_rows": applied_path.name,
        },
    }
    (output_dir / "bso-scope-review-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    apply(args.base, args.review, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
