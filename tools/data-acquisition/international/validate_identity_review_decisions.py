#!/usr/bin/env python3
"""Validate source-backed D2.2 identity/division review decisions.

The decision seed is an explicit research-review artifact. Validation confirms
that every referenced source row exists in the currently generated D2.1 source
universe and that no row is assigned to two incompatible reviewed groups.
The validator never creates or merges canonical institutions.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DECISIONS = HERE / "seeds" / "identity-review-decisions-2026-09-15.json"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate(decisions_path: Path, universe_path: Path, output_dir: Path) -> dict:
    decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
    universe = load_jsonl(universe_path)
    by_key = {(row["source_id"], row["source_record_id"]): row for row in universe}

    groups = decisions["groups"]
    assert decisions["groups_count"] == len(groups) == 9
    assert decisions["safety"]["canonical_institutions_created"] == 0
    assert decisions["safety"]["canonical_merges_performed"] == 0
    assert decisions["safety"]["public_projection_rows_created"] == 0
    assert decisions["safety"]["database_mutation_performed"] is False

    referenced_keys: set[tuple[str, str]] = set()
    missing: list[dict] = []
    name_mismatches: list[dict] = []
    reviewed_rows: list[dict] = []

    for group in groups:
        assert group["decision"] in {
            "same_institution",
            "same_institution_with_division_scoped_evidence",
        }
        assert group["decision_confidence"] == "high"
        assert len(group.get("evidence_urls") or []) >= 2
        assert group.get("review_note")
        assert len(group["source_records"]) >= 2

        for member in group["source_records"]:
            key = (member["source_id"], member["source_record_id"])
            if key in referenced_keys:
                raise AssertionError(f"source row assigned to multiple reviewed groups: {key}")
            referenced_keys.add(key)
            current = by_key.get(key)
            if current is None:
                missing.append(member)
                continue
            current_name = current.get("name_en") or current.get("name_ar") or current.get("parent_university_en")
            if current_name != member["source_name"]:
                name_mismatches.append({
                    "key": key,
                    "decision_name": member["source_name"],
                    "current_name": current_name,
                })
            reviewed_rows.append({
                "review_group_id": group["review_group_id"],
                "decision": group["decision"],
                "provisional_canonical_name_en": group["provisional_canonical_name_en"],
                "source_id": member["source_id"],
                "source_record_id": member["source_record_id"],
                "source_name": member["source_name"],
                "division_scope": member.get("division_scope"),
                "source_scope_state": current.get("scope_state"),
                "source_url": current.get("source_url"),
                "canonical_merge_performed": False,
            })

    assert not missing, f"review decisions reference missing source rows: {missing}"
    assert not name_mismatches, f"review decision names drifted from source universe: {name_mismatches}"
    assert len(reviewed_rows) == len(referenced_keys) == 20

    division_groups = [
        row for row in groups
        if row["decision"] == "same_institution_with_division_scoped_evidence"
    ]
    assert {row["review_group_id"] for row in division_groups} == {
        "el-alsson-newgiza",
        "misr-language-schools",
    }
    assert all(any(member.get("division_scope") for member in row["source_records"]) for row in division_groups)

    output_dir.mkdir(parents=True, exist_ok=True)
    reviewed_path = output_dir / "reviewed-source-memberships.jsonl"
    with reviewed_path.open("w", encoding="utf-8") as handle:
        for row in reviewed_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": 1,
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.2_identity_and_division_reconciliation",
        "review_groups": len(groups),
        "reviewed_source_rows": len(reviewed_rows),
        "same_institution_groups": sum(1 for row in groups if row["decision"] == "same_institution"),
        "division_scoped_groups": len(division_groups),
        "source_universe_rows": len(universe),
        "missing_source_rows": 0,
        "name_drift_rows": 0,
        "canonical_institutions_created": 0,
        "canonical_merges_performed": 0,
        "public_projection_rows_created": 0,
        "database_mutation_performed": False,
        "output": reviewed_path.name,
    }
    (output_dir / "identity-review-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument(
        "--universe",
        type=Path,
        default=Path("artifacts/international/accreditor-expansion/authoritative-source-candidates-with-accreditors.jsonl"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/international/identity-review"),
    )
    args = parser.parse_args()
    validate(args.decisions, args.universe, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
