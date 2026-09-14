#!/usr/bin/env python3
"""Materialize reviewed D2.2 identity/division decisions into deterministic draft artifacts.

This builder deliberately stops before runtime/database mutation. It converts only
explicitly reviewed relationship decisions into portable draft records with stable
UUIDv5 identifiers, preserves every source membership, emits an unresolved campus
review state instead of inventing campuses, and keeps the remaining source universe
in a review queue.

The outputs are *reviewed canonical drafts*, not public/canonical database rows.
"""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_IDENTITY_DECISIONS = HERE / "seeds" / "identity-review-decisions-2026-09-15.json"
DEFAULT_DIVISION_DECISIONS = HERE / "seeds" / "division-review-decisions-2026-09-15.json"
DEFAULT_UNIVERSE = Path(
    "artifacts/international/accreditor-expansion/authoritative-source-candidates-with-accreditors.jsonl"
)
DEFAULT_OUTPUT_DIR = Path("artifacts/international/reviewed-canonical-draft")

# Fixed namespace makes draft identifiers reproducible across machines/runs.
DRAFT_NAMESPACE = uuid.UUID("ed2d2f67-d75d-5b1f-a408-8aa6510a7f5a")
KNOWN_CURRICULA = {"american", "british", "canadian", "french", "german", "ib"}


def stable_uuid(kind: str, key: str) -> str:
    return str(uuid.uuid5(DRAFT_NAMESPACE, f"{kind}:{key}"))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def build(
    identity_decisions_path: Path,
    division_decisions_path: Path,
    universe_path: Path,
    output_dir: Path,
) -> dict:
    identity = load_json(identity_decisions_path)
    divisions = load_json(division_decisions_path)
    universe = load_jsonl(universe_path)

    groups = identity["groups"]
    division_rows = divisions["divisions"]

    assert identity["groups_count"] == len(groups) == 9
    assert divisions["divisions_count"] == len(division_rows) == 4
    assert identity["safety"]["canonical_institutions_created"] == 0
    assert identity["safety"]["canonical_merges_performed"] == 0
    assert identity["safety"]["database_mutation_performed"] is False
    assert divisions["safety"]["canonical_database_rows_written"] == 0
    assert divisions["safety"]["automatic_division_inference_performed"] is False

    source_by_key = {
        (row["source_id"], row["source_record_id"]): row
        for row in universe
    }
    if len(source_by_key) != len(universe):
        raise AssertionError("source universe contains duplicate source_id/source_record_id keys")

    group_by_id = {group["review_group_id"]: group for group in groups}
    if len(group_by_id) != len(groups):
        raise AssertionError("duplicate identity review_group_id")

    reviewed_keys: set[tuple[str, str]] = set()
    institution_drafts: list[dict] = []
    campus_review_states: list[dict] = []

    for group in groups:
        group_id = group["review_group_id"]
        draft_institution_id = stable_uuid("institution", group_id)
        memberships: list[dict] = []
        source_scope_states: set[str] = set()

        for member in group["source_records"]:
            key = (member["source_id"], member["source_record_id"])
            if key in reviewed_keys:
                raise AssertionError(f"source row assigned to multiple reviewed institutions: {key}")
            reviewed_keys.add(key)
            source = source_by_key.get(key)
            if source is None:
                raise AssertionError(f"reviewed source row missing from current universe: {key}")
            current_name = source.get("name_en") or source.get("name_ar") or source.get("parent_university_en")
            if current_name != member["source_name"]:
                raise AssertionError(
                    f"reviewed source name drift for {key}: decision={member['source_name']!r} current={current_name!r}"
                )
            if source.get("scope_state"):
                source_scope_states.add(source["scope_state"])
            memberships.append(
                {
                    "source_id": member["source_id"],
                    "source_record_id": member["source_record_id"],
                    "source_name": member["source_name"],
                    "division_scope": member.get("division_scope"),
                    "source_scope_state": source.get("scope_state"),
                    "source_url": source.get("source_url"),
                }
            )

        institution_drafts.append(
            {
                "draft_institution_id": draft_institution_id,
                "review_group_id": group_id,
                "canonical_name_en": group["provisional_canonical_name_en"],
                "canonical_name_status": "reviewed_provisional",
                "identity_review_decision": group["decision"],
                "identity_review_confidence": group["decision_confidence"],
                "division_scoped_evidence": group["decision"] == "same_institution_with_division_scoped_evidence",
                "source_scope_states": sorted(source_scope_states),
                "eligibility_selection_performed": False,
                "source_record_count": len(memberships),
                "source_memberships": memberships,
                "evidence_urls": list(group.get("evidence_urls") or []),
                "review_note": group["review_note"],
                "campus_structure_state": "not_yet_reviewed",
                "canonical_database_write_performed": False,
                "public_projection_performed": False,
            }
        )

        campus_review_states.append(
            {
                "draft_institution_id": draft_institution_id,
                "review_group_id": group_id,
                "canonical_name_en": group["provisional_canonical_name_en"],
                "campus_structure_state": "not_yet_reviewed",
                "review_required": True,
                "canonical_campus_id": None,
                "canonical_campus_created": False,
                "reason": "Identity is reviewed, but campus count/relationships have not yet been explicitly reviewed from source evidence.",
            }
        )

    division_drafts: list[dict] = []
    division_ids: set[str] = set()
    for division in division_rows:
        group_id = division["review_group_id"]
        parent_group = group_by_id.get(group_id)
        if parent_group is None:
            raise AssertionError(f"division references unknown review group: {group_id}")
        if parent_group["decision"] != "same_institution_with_division_scoped_evidence":
            raise AssertionError(f"division attached to non-division-scoped identity group: {group_id}")

        parent_member_keys = {
            (row["source_id"], row["source_record_id"])
            for row in parent_group["source_records"]
        }
        memberships: list[dict] = []
        for membership in division["source_memberships"]:
            key = (membership["source_id"], membership["source_record_id"])
            if key not in parent_member_keys:
                raise AssertionError(
                    f"division source membership is not part of parent identity group {group_id}: {key}"
                )
            if key not in source_by_key:
                raise AssertionError(f"division source row missing from current universe: {key}")
            memberships.append(dict(membership))

        curricula = list(division.get("curriculum_codes") or [])
        unknown_curricula = sorted(set(curricula) - KNOWN_CURRICULA)
        if unknown_curricula:
            raise AssertionError(f"unknown division curricula {unknown_curricula} for {group_id}")

        division_key = division["division_key"]
        draft_division_id = stable_uuid("school_division", f"{group_id}:{division_key}")
        if draft_division_id in division_ids:
            raise AssertionError(f"duplicate deterministic division id for {group_id}:{division_key}")
        division_ids.add(draft_division_id)

        division_drafts.append(
            {
                "draft_school_division_id": draft_division_id,
                "draft_institution_id": stable_uuid("institution", group_id),
                "review_group_id": group_id,
                "division_key": division_key,
                "canonical_name_en": division["canonical_name_en"],
                "canonical_name_status": "reviewed_provisional",
                "division_type": division["division_type"],
                "curriculum_codes": curricula,
                "source_memberships": memberships,
                "evidence_urls": list(division.get("evidence_urls") or []),
                "review_note": division["review_note"],
                "identity_reviewed": True,
                "canonical_database_write_performed": False,
                "public_projection_performed": False,
            }
        )

    reviewed_institution_ids = {row["draft_institution_id"] for row in institution_drafts}
    if len(reviewed_institution_ids) != len(institution_drafts):
        raise AssertionError("deterministic institution IDs are not unique")
    if not all(row["draft_institution_id"] in reviewed_institution_ids for row in division_drafts):
        raise AssertionError("division draft references a missing reviewed institution")

    unreviewed_source_rows = [
        {
            "source_id": row["source_id"],
            "source_record_id": row["source_record_id"],
            "source_name": row.get("name_en") or row.get("name_ar") or row.get("parent_university_en"),
            "entity_family": row.get("entity_family"),
            "scope_state": row.get("scope_state"),
            "source_url": row.get("source_url"),
            "d2_2_identity_review_state": "unreviewed",
        }
        for row in universe
        if (row["source_id"], row["source_record_id"]) not in reviewed_keys
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    institutions_path = output_dir / "reviewed-institution-drafts.jsonl"
    divisions_path = output_dir / "reviewed-school-division-drafts.jsonl"
    campuses_path = output_dir / "campus-review-state.jsonl"
    queue_path = output_dir / "unreviewed-source-queue.jsonl"
    write_jsonl(institutions_path, institution_drafts)
    write_jsonl(divisions_path, division_drafts)
    write_jsonl(campuses_path, campus_review_states)
    write_jsonl(queue_path, unreviewed_source_rows)

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.2_reviewed_canonical_draft_materialization",
        "deterministic_id_namespace": str(DRAFT_NAMESPACE),
        "source_universe_rows": len(universe),
        "reviewed_identity_groups": len(institution_drafts),
        "reviewed_source_memberships": len(reviewed_keys),
        "draft_institution_records": len(institution_drafts),
        "division_scoped_identity_groups": sum(1 for row in institution_drafts if row["division_scoped_evidence"]),
        "draft_school_division_records": len(division_drafts),
        "campus_review_state_records": len(campus_review_states),
        "resolved_canonical_campuses": 0,
        "unreviewed_source_rows": len(unreviewed_source_rows),
        "unique_institutions_claimed_for_full_universe": None,
        "eligibility_selection_performed": False,
        "automatic_merges_performed": 0,
        "canonical_database_rows_written": 0,
        "runtime_database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "institutions": institutions_path.name,
            "school_divisions": divisions_path.name,
            "campus_review_state": campuses_path.name,
            "unreviewed_source_queue": queue_path.name,
        },
    }
    (output_dir / "reviewed-canonical-draft-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity-decisions", type=Path, default=DEFAULT_IDENTITY_DECISIONS)
    parser.add_argument("--division-decisions", type=Path, default=DEFAULT_DIVISION_DECISIONS)
    parser.add_argument("--universe", type=Path, default=DEFAULT_UNIVERSE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    build(args.identity_decisions, args.division_decisions, args.universe, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
