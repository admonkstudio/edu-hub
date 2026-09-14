#!/usr/bin/env python3
"""Apply explicit D2.1 scope decisions to the CIS/Cognia expansion rows.

The input is the 106-row source universe after the foundational authoritative
families, complete IB ownership review, reviewed BSO scope review and the
CIS/Cognia expansion have been assembled. This overlay upgrades only the exact
10 accreditor expansion candidates whose ownership/international scope has now
been separately reviewed.

No source identity, canonical entity, runtime database or public projection is
created by this transformation.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_REVIEW = HERE / "seeds" / "accreditor-scope-review-2026-09-15.json"
DEFAULT_BASE = Path(
    "artifacts/international/bso-scope-review/accreditor-expansion/"
    "authoritative-source-candidates-with-accreditors.jsonl"
)
DEFAULT_OUTPUT_DIR = Path("artifacts/international/accreditor-scope-review")
ALLOWED_SOURCE_IDS = {
    "cis_international_accreditation_egypt",
    "cognia_member_milestones_egypt_2026_2027",
}


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

    if len(rows) != 106:
        raise AssertionError(f"unexpected accreditor-expanded row count: {len(rows)}")
    before = count_states(rows)
    if before != {"eligible": 93, "candidate": 10, "excluded": 3}:
        raise AssertionError(f"unexpected pre-accreditor-review state contract: {before}")

    records = review.get("records") or []
    if review.get("records_count") != len(records) or len(records) != 10:
        raise AssertionError("accreditor scope review must contain exactly 10 records")
    if review.get("summary") != {
        "reviewed_rows": 10,
        "eligible_rows": 10,
        "excluded_rows": 0,
        "needs_review_rows": 0,
    }:
        raise AssertionError("accreditor scope review summary contract drifted")

    review_keys = [(r["source_id"], r["source_record_id"]) for r in records]
    if len(review_keys) != len(set(review_keys)):
        raise AssertionError("duplicate source key in accreditor scope review")
    if any(r["source_id"] not in ALLOWED_SOURCE_IDS for r in records):
        raise AssertionError("review contains a source outside the CIS/Cognia expansion")
    if any(r.get("scope_state") != "eligible" for r in records):
        raise AssertionError("every accepted accreditor review record must be eligible")
    if any(len(r.get("evidence_urls") or []) < 2 for r in records):
        raise AssertionError("every accreditor review record requires at least two evidence URLs")
    if any(not r.get("scope_basis") or not r.get("ownership_scope") or not r.get("review_note") for r in records):
        raise AssertionError("every accreditor review record needs ownership_scope, scope_basis and review_note")

    source_by_key = {(r["source_id"], r["source_record_id"]): r for r in rows}
    expansion_candidates = {
        (r["source_id"], r["source_record_id"])
        for r in rows
        if r.get("source_id") in ALLOWED_SOURCE_IDS and r.get("scope_state") == "candidate"
    }
    if len(expansion_candidates) != 10:
        raise AssertionError(f"expected 10 CIS/Cognia candidate rows, found {len(expansion_candidates)}")
    if set(review_keys) != expansion_candidates:
        missing = sorted(expansion_candidates - set(review_keys))
        unknown = sorted(set(review_keys) - expansion_candidates)
        raise AssertionError(f"accreditor review/source mismatch missing={missing} unknown={unknown}")

    source_keys_before = [(r["source_id"], r["source_record_id"]) for r in rows]
    if len(source_keys_before) != len(set(source_keys_before)):
        raise AssertionError("source universe contains duplicate source keys")

    review_by_key = {(r["source_id"], r["source_record_id"]): r for r in records}
    upgraded: list[dict] = []
    applied: list[dict] = []

    for original in rows:
        row = dict(original)
        key = (row["source_id"], row["source_record_id"])
        decision = review_by_key.get(key)
        if decision:
            current_name = row.get("name_en") or row.get("name_ar") or row.get("parent_university_en")
            if current_name != decision["name"]:
                raise AssertionError(
                    f"accreditor review name drift for {key}: source={current_name!r} review={decision['name']!r}"
                )
            if row.get("scope_state") != "candidate":
                raise AssertionError(f"accreditor review may only upgrade candidate rows: {current_name}")
            row.update(
                {
                    "scope_state": "eligible",
                    "ownership_scope": decision["ownership_scope"],
                    "eligibility_pending": None,
                    "scope_review_state": "reviewed_eligible",
                    "scope_review_snapshot_date": review["snapshot_date"],
                    "scope_review_basis": decision["scope_basis"],
                    "scope_review_evidence_urls": list(decision["evidence_urls"]),
                    "scope_review_note": decision["review_note"],
                    "auto_eligibility": False,
                }
            )
            applied.append(
                {
                    "source_id": row["source_id"],
                    "source_record_id": row["source_record_id"],
                    "name_en": current_name,
                    "previous_scope_state": original.get("scope_state"),
                    "new_scope_state": row["scope_state"],
                    "ownership_scope": row["ownership_scope"],
                    "scope_review_basis": row["scope_review_basis"],
                    "scope_review_snapshot_date": row["scope_review_snapshot_date"],
                }
            )
        upgraded.append(row)

    if len(applied) != 10:
        raise AssertionError(f"expected 10 applied accreditor decisions, found {len(applied)}")
    if [(r["source_id"], r["source_record_id"]) for r in upgraded] != source_keys_before:
        raise AssertionError("accreditor scope overlay changed source identity order or keys")

    after = count_states(upgraded)
    if after != {"eligible": 103, "excluded": 3}:
        raise AssertionError(f"unexpected post-accreditor-review state contract: {after}")

    output_dir.mkdir(parents=True, exist_ok=True)
    upgraded_path = output_dir / "reviewed-source-universe.jsonl"
    applied_path = output_dir / "accreditor-scope-review-applied.jsonl"
    write_jsonl(upgraded_path, upgraded)
    write_jsonl(applied_path, applied)

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_accreditor_expansion_scope_integration",
        "source_rows": len(rows),
        "reviewed_accreditor_rows": len(records),
        "applied_rows": len(applied),
        "source_record_ids_changed": 0,
        "before_scope_states": before,
        "after_scope_states": after,
        "remaining_scope_candidates_in_current_106_row_universe": after.get("candidate", 0),
        "unique_institutions_claimed": None,
        "identity_merges_performed": 0,
        "canonical_institutions_created": 0,
        "canonical_database_rows_written": 0,
        "runtime_database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "reviewed_source_universe": upgraded_path.name,
            "applied_rows": applied_path.name,
        },
    }
    (output_dir / "accreditor-scope-review-summary.json").write_text(
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
