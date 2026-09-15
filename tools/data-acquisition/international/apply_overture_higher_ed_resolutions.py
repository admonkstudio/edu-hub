#!/usr/bin/env python3
"""Apply complete explicit review decisions to the Overture higher-ed queue.

The input queue is expected to contain the 70 rows remaining after the reviewed
five-row substantive-international HE overlay introduces exact-name overlaps.
Every row must be explicitly classified by Overture ID. This script performs no
fuzzy matching, no automatic eligibility, no canonical identity creation and no
runtime/public mutation.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ALLOWED = {
    "existing_eligible_he_identity_or_subunit",
    "rerouted_preuniversity_existing_identity",
    "rerouted_preuniversity_unresolved",
    "out_of_scope_egyptian_higher_education",
    "supporting_only_no_current_qualifying_he_evidence",
}
TARGET_REQUIRED = {
    "existing_eligible_he_identity_or_subunit",
    "rerouted_preuniversity_existing_identity",
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build(queue_path: Path, universe_path: Path, decisions_path: Path, output_dir: Path) -> dict:
    queue = read_jsonl(queue_path)
    universe = read_jsonl(universe_path)
    seed = json.loads(decisions_path.read_text(encoding="utf-8"))

    if seed.get("expected_input_rows") != 70 or len(queue) != 70:
        raise RuntimeError(f"Expected complete 70-row higher-ed queue, got {len(queue)}")
    queue_by_id = {str(r.get("overture_id")): r for r in queue}
    if len(queue_by_id) != 70:
        raise RuntimeError("Higher-ed queue Overture IDs must be unique")
    universe_by_key = {(str(r.get("source_id")), str(r.get("source_record_id"))): r for r in universe}

    reviewed = []
    seen = set()
    for group in seed.get("groups", []):
        decision = str(group.get("decision") or "")
        if decision not in ALLOWED:
            raise RuntimeError(f"Unsupported higher-ed decision: {decision}")
        target_id = group.get("target_source_id")
        target_record = group.get("target_source_record_id")
        target = None
        if decision in TARGET_REQUIRED:
            if not target_id or not target_record:
                raise RuntimeError(f"Decision {decision} requires an exact universe target")
            target = universe_by_key.get((str(target_id), str(target_record)))
            if target is None:
                raise RuntimeError(f"Universe target missing: {target_id}/{target_record}")
            expected_target_name = group.get("target_name_en")
            if expected_target_name and target.get("name_en") != expected_target_name:
                raise RuntimeError(f"Universe target name mismatch for {target_id}/{target_record}")
        elif target_id is not None or target_record is not None:
            raise RuntimeError(f"Decision {decision} must not attach a universe target")

        for overture_id in group.get("overture_ids", []):
            overture_id = str(overture_id)
            if overture_id in seen:
                raise RuntimeError(f"Duplicate higher-ed decision target: {overture_id}")
            source = queue_by_id.get(overture_id)
            if source is None:
                raise RuntimeError(f"Decision Overture ID is not in current higher-ed queue: {overture_id}")
            seen.add(overture_id)
            reviewed.append({
                **source,
                "resolution_batch_id": seed["batch_id"],
                "resolution_decision": decision,
                "target_source_id": target_id,
                "target_source_record_id": target_record,
                "target_name_en": group.get("target_name_en"),
                "evidence_urls": group.get("evidence_urls", []),
                "review_note": group.get("review_note"),
                "higher_ed_queue_resolved": True,
                "canonical_identity_created": False,
                "automatic_merge_performed": False,
                "international_eligibility_granted_by_overture": False,
            })

    if seen != set(queue_by_id):
        missing = sorted(set(queue_by_id) - seen)
        raise RuntimeError(f"Higher-ed review is incomplete; missing {len(missing)} rows: {missing[:5]}")

    counts = Counter(r["resolution_decision"] for r in reviewed)
    existing = [r for r in reviewed if r["resolution_decision"] == "existing_eligible_he_identity_or_subunit"]
    rerouted_existing = [r for r in reviewed if r["resolution_decision"] == "rerouted_preuniversity_existing_identity"]
    rerouted_unresolved = [r for r in reviewed if r["resolution_decision"] == "rerouted_preuniversity_unresolved"]
    out_scope = [r for r in reviewed if r["resolution_decision"] == "out_of_scope_egyptian_higher_education"]
    supporting = [r for r in reviewed if r["resolution_decision"] == "supporting_only_no_current_qualifying_he_evidence"]

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "reviewed-higher-ed-decisions.jsonl": reviewed,
        "existing-eligible-he-aliases-and-subunits.jsonl": existing,
        "rerouted-preuniversity-existing.jsonl": rerouted_existing,
        "rerouted-preuniversity-unresolved.jsonl": rerouted_unresolved,
        "out-of-scope-egyptian-higher-ed.jsonl": out_scope,
        "supporting-only-no-qualifying-he-evidence.jsonl": supporting,
    }
    for filename, items in outputs.items():
        with (output_dir / filename).open("w", encoding="utf-8") as handle:
            for row in items:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": 1,
        "work_package": "D2.1_overture_higher_education_complete_review",
        "input_higher_ed_rows": 70,
        "reviewed_rows": len(reviewed),
        "higher_ed_queue_outstanding_rows": 0,
        "decision_counts": dict(sorted(counts.items())),
        "existing_eligible_he_alias_or_subunit_rows": len(existing),
        "rerouted_preuniversity_existing_rows": len(rerouted_existing),
        "rerouted_preuniversity_unresolved_rows": len(rerouted_unresolved),
        "out_of_scope_egyptian_he_rows": len(out_scope),
        "supporting_only_no_qualifying_he_rows": len(supporting),
        "new_preuniversity_followup_rows": len(rerouted_unresolved),
        "fuzzy_matches_performed": 0,
        "overture_rows_auto_added_to_universe": 0,
        "international_eligibility_granted_by_overture": 0,
        "canonical_institutions_created": 0,
        "automatic_identity_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
    }
    (output_dir / "higher-ed-review-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, default=Path("artifacts/international/overture-gap-review/higher-ed-scope-review.jsonl"))
    parser.add_argument("--universe", type=Path, default=Path("artifacts/international/d2-1-universe-checkpoint/source-lead-universe.jsonl"))
    parser.add_argument("--decisions", type=Path, default=Path("tools/data-acquisition/international/seeds/overture-higher-ed-scope-review-2026-09-15-batch1.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/international/overture-higher-ed-resolution"))
    args = parser.parse_args()
    build(args.queue, args.universe, args.decisions, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
