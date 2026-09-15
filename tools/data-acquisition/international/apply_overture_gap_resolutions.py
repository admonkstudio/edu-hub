#!/usr/bin/env python3
"""Apply explicit reviewed decisions to the Overture high-signal gap queue.

This is discovery triage only. It verifies that each checked-in decision targets
an exact Overture row and, when a current source target is named, an exact row
in the accepted D2.1 source/lead universe. It never performs a fuzzy merge,
creates a canonical identity, mutates a database or promotes unresolved rows.
"""
from __future__ import annotations

import argparse
import json
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_DECISIONS = {
    "covered_by_current_authoritative_source_family",
    "existing_source_identity_alias",
    "existing_provider_division_requires_d2_2_review",
    "unresolved_supporting_only",
}
RESOLVED_DECISIONS = ALLOWED_DECISIONS - {"unresolved_supporting_only"}


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build(high_signal: Path, universe: Path, decision_files: list[Path], output_dir: Path) -> dict:
    high_rows = read_jsonl(high_signal)
    universe_rows = read_jsonl(universe)
    high_by_id = {str(row.get("overture_id")): row for row in high_rows}
    if len(high_by_id) != len(high_rows):
        raise RuntimeError("High-signal Overture queue contains duplicate overture_id values")
    universe_by_key = {
        (str(row.get("source_id")), str(row.get("source_record_id"))): row
        for row in universe_rows
    }

    decisions: list[dict] = []
    batch_ids: list[str] = []
    for path in decision_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        batch_id = str(payload.get("batch_id") or "")
        if not batch_id or batch_id in batch_ids:
            raise RuntimeError(f"Invalid or duplicate Overture resolution batch id: {batch_id!r}")
        batch_ids.append(batch_id)
        records = payload.get("records", [])
        if payload.get("records_count") != len(records):
            raise RuntimeError(f"Decision count mismatch in {path}")
        for row in records:
            decisions.append({**row, "batch_id": batch_id})

    decision_ids = [str(row.get("overture_id") or "") for row in decisions]
    if not all(decision_ids) or len(set(decision_ids)) != len(decision_ids):
        raise RuntimeError("Resolution decisions must target unique non-empty overture_id values")

    reviewed: list[dict] = []
    for decision in decisions:
        overture_id = str(decision["overture_id"])
        source = high_by_id.get(overture_id)
        if source is None:
            raise RuntimeError(f"Resolution target is not in the current high-signal gap queue: {overture_id}")
        if normalize(source.get("name")) != normalize(decision.get("overture_name")):
            raise RuntimeError(f"Overture name mismatch for {overture_id}")
        state = decision.get("decision")
        if state not in ALLOWED_DECISIONS:
            raise RuntimeError(f"Unsupported Overture gap decision {state!r} for {overture_id}")

        target_source_id = decision.get("target_source_id")
        target_source_record_id = decision.get("target_source_record_id")
        target = None
        if state == "unresolved_supporting_only":
            if target_source_id is not None or target_source_record_id is not None:
                raise RuntimeError(f"Unresolved decision {overture_id} must not name a current-universe target")
        else:
            if not target_source_id or not target_source_record_id:
                raise RuntimeError(f"Resolved decision {overture_id} must name an exact current-universe target")
            target = universe_by_key.get((str(target_source_id), str(target_source_record_id)))
            if target is None:
                raise RuntimeError(f"Current-universe target not found for {overture_id}: {target_source_id}/{target_source_record_id}")
            expected_name = decision.get("target_name_en")
            if expected_name and normalize(target.get("name_en")) != normalize(expected_name):
                raise RuntimeError(f"Target name mismatch for {overture_id}")

        reviewed.append({
            **source,
            "resolution_batch_id": decision["batch_id"],
            "resolution_decision": state,
            "target_source_id": target_source_id,
            "target_source_record_id": target_source_record_id,
            "target_name_en": decision.get("target_name_en"),
            "evidence_urls": decision.get("evidence_urls", []),
            "review_note": decision.get("review_note"),
            "resolution_state": "resolved_from_gap_queue" if state in RESOLVED_DECISIONS else "reviewed_but_still_unresolved",
            "canonical_identity_created": False,
            "automatic_merge_performed": False,
            "international_eligibility_granted_by_overture": False,
        })

    reviewed_ids = set(decision_ids)
    unreviewed = [row for row in high_rows if str(row.get("overture_id")) not in reviewed_ids]
    resolved = [row for row in reviewed if row["resolution_state"] == "resolved_from_gap_queue"]
    reviewed_unresolved = [row for row in reviewed if row["resolution_state"] == "reviewed_but_still_unresolved"]
    counts = Counter(row["resolution_decision"] for row in reviewed)

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "reviewed-gap-decisions.jsonl": reviewed,
        "resolved-existing-or-authoritative.jsonl": resolved,
        "reviewed-still-unresolved.jsonl": reviewed_unresolved,
        "unreviewed-high-signal-queue.jsonl": unreviewed,
    }
    for filename, rows in outputs.items():
        with (output_dir / filename).open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_overture_high_signal_gap_resolution",
        "input_high_signal_rows": len(high_rows),
        "reviewed_rows": len(reviewed),
        "resolved_existing_or_authoritative_rows": len(resolved),
        "reviewed_still_unresolved_rows": len(reviewed_unresolved),
        "unreviewed_high_signal_rows": len(unreviewed),
        "outstanding_high_signal_rows": len(unreviewed) + len(reviewed_unresolved),
        "decision_counts": dict(sorted(counts.items())),
        "batch_ids": batch_ids,
        "fuzzy_matches_performed": 0,
        "overture_rows_auto_added_to_universe": 0,
        "international_eligibility_granted_by_overture": 0,
        "canonical_institutions_created": 0,
        "automatic_identity_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
    }
    (output_dir / "resolution-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--high-signal", type=Path,
        default=Path("artifacts/international/overture-gap-review/high-signal-preuniversity-review.jsonl"),
    )
    parser.add_argument(
        "--universe", type=Path,
        default=Path("artifacts/international/d2-1-universe-checkpoint/source-lead-universe.jsonl"),
    )
    parser.add_argument(
        "--decisions", type=Path, nargs="+",
        default=[Path("tools/data-acquisition/international/seeds/overture-gap-resolution-2026-09-15-batch1.json")],
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("artifacts/international/overture-gap-resolution"),
    )
    args = parser.parse_args()
    build(args.high_signal, args.universe, args.decisions, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
