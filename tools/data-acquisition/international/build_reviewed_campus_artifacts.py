#!/usr/bin/env python3
"""Materialize source-backed D2.2 current-campus evidence as deterministic drafts.

This layer is deliberately separate from institution identity materialization.
It may establish that a reviewed institution has an evidenced current operating
campus at a source-backed location, but it does not claim that the institution's
entire campus structure is complete and it does not infer additional campuses.

Outputs are portable review artifacts only: zero runtime database mutation and
zero public projection.
"""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_IDENTITY_DECISIONS = HERE / "seeds" / "identity-review-decisions-2026-09-15.json"
DEFAULT_CAMPUS_DECISIONS = HERE / "seeds" / "campus-review-decisions-2026-09-15.json"
DEFAULT_OUTPUT_DIR = Path("artifacts/international/reviewed-campus-draft")

# Must remain identical to build_reviewed_canonical_artifacts.py.
DRAFT_NAMESPACE = uuid.UUID("ed2d2f67-d75d-5b1f-a408-8aa6510a7f5a")


def stable_uuid(kind: str, key: str) -> str:
    return str(uuid.uuid5(DRAFT_NAMESPACE, f"{kind}:{key}"))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def build(identity_path: Path, campus_path: Path, output_dir: Path) -> dict:
    identity = load_json(identity_path)
    campus = load_json(campus_path)
    groups = identity["groups"]
    records = campus["records"]

    assert identity["groups_count"] == len(groups) == 9
    assert campus["records_count"] == len(records) == 9
    assert campus["safety"]["reviewed_current_campus_evidence_records"] == 9
    assert campus["safety"]["campus_structure_complete_records"] == 0
    assert campus["safety"]["automatic_additional_campus_inference_performed"] is False
    assert campus["safety"]["canonical_database_rows_written"] == 0
    assert campus["safety"]["database_mutation_performed"] is False
    assert campus["safety"]["public_projection_rows_created"] == 0

    group_by_id = {row["review_group_id"]: row for row in groups}
    if len(group_by_id) != len(groups):
        raise AssertionError("duplicate identity review_group_id")

    reviewed_group_ids: set[str] = set()
    campus_ids: set[str] = set()
    campus_drafts: list[dict] = []
    structure_states: list[dict] = []

    for record in records:
        group_id = record["review_group_id"]
        group = group_by_id.get(group_id)
        if group is None:
            raise AssertionError(f"campus decision references unknown identity review group: {group_id}")
        if group_id in reviewed_group_ids:
            raise AssertionError(f"multiple current-campus decisions for review group without explicit multi-campus review: {group_id}")
        reviewed_group_ids.add(group_id)

        if record["campus_structure_complete"] is not False:
            raise AssertionError(f"current campus evidence may not claim exhaustive campus structure: {group_id}")
        if record["lifecycle_status"] != "active":
            raise AssertionError(f"this first current-campus package is limited to active campuses: {group_id}")
        if not record.get("address_en"):
            raise AssertionError(f"reviewed current campus requires a source-backed address/location: {group_id}")
        if not record.get("source_urls"):
            raise AssertionError(f"reviewed current campus requires source URLs: {group_id}")

        institution_id = stable_uuid("institution", group_id)
        campus_key = record["campus_key"]
        campus_id = stable_uuid("campus", f"{group_id}:{campus_key}")
        if campus_id in campus_ids:
            raise AssertionError(f"duplicate deterministic campus ID: {group_id}:{campus_key}")
        campus_ids.add(campus_id)

        campus_drafts.append(
            {
                "draft_campus_id": campus_id,
                "draft_institution_id": institution_id,
                "review_group_id": group_id,
                "institution_name_en": group["provisional_canonical_name_en"],
                "campus_key": campus_key,
                "campus_type": record["campus_type"],
                "lifecycle_status": record["lifecycle_status"],
                "source_named_campus_name_en": record.get("source_named_campus_name_en"),
                "address_en": record["address_en"],
                "source_urls": list(record["source_urls"]),
                "evidence_note": record["evidence_note"],
                "current_campus_evidence_reviewed": True,
                "campus_structure_complete": False,
                "additional_current_campuses_ruled_out": False,
                "canonical_campus_created": False,
                "canonical_database_write_performed": False,
                "public_projection_performed": False,
            }
        )

        structure_states.append(
            {
                "draft_institution_id": institution_id,
                "review_group_id": group_id,
                "institution_name_en": group["provisional_canonical_name_en"],
                "campus_structure_state": "at_least_one_current_campus_reviewed_structure_not_exhaustive",
                "reviewed_current_campus_ids": [campus_id],
                "reviewed_current_campus_count": 1,
                "campus_structure_complete": False,
                "additional_current_campuses_ruled_out": False,
                "further_campus_review_required": True,
                "canonical_database_write_performed": False,
                "public_projection_performed": False,
            }
        )

    missing_groups = sorted(set(group_by_id) - reviewed_group_ids)
    if missing_groups:
        raise AssertionError(f"first campus review package does not cover all reviewed identity groups: {missing_groups}")

    output_dir.mkdir(parents=True, exist_ok=True)
    campus_drafts_path = output_dir / "reviewed-current-campus-drafts.jsonl"
    structure_states_path = output_dir / "campus-structure-review.jsonl"
    write_jsonl(campus_drafts_path, campus_drafts)
    write_jsonl(structure_states_path, structure_states)

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.2_reviewed_current_campus_materialization",
        "deterministic_id_namespace": str(DRAFT_NAMESPACE),
        "reviewed_identity_groups": len(groups),
        "reviewed_current_campus_records": len(campus_drafts),
        "identity_groups_with_current_campus_evidence": len(reviewed_group_ids),
        "campus_structure_complete_records": 0,
        "additional_current_campuses_ruled_out_records": 0,
        "automatic_additional_campus_inference_performed": False,
        "canonical_campus_rows_created": 0,
        "canonical_database_rows_written": 0,
        "runtime_database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "current_campus_drafts": campus_drafts_path.name,
            "campus_structure_review": structure_states_path.name,
        },
    }
    (output_dir / "reviewed-campus-draft-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity-decisions", type=Path, default=DEFAULT_IDENTITY_DECISIONS)
    parser.add_argument("--campus-decisions", type=Path, default=DEFAULT_CAMPUS_DECISIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    build(args.identity_decisions, args.campus_decisions, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
