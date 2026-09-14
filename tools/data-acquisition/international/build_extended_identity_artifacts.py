#!/usr/bin/env python3
"""Build the next D2.2 reviewed identity universe from cross-source and explicit single-source review.

The original reviewed identity package focused on cross-source duplicate resolution.
Database completion also requires explicit review of legitimate identities that have
only one row in the current authoritative source universe. An unmatched row is not
silently assumed unique: it enters this build only through the checked-in
single-source review package with primary/authoritative evidence.

Outputs remain portable review artifacts. No runtime database write, automatic merge
or public projection is performed.
"""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CROSS_SOURCE = HERE / "seeds" / "identity-review-decisions-2026-09-15.json"
DEFAULT_SINGLE_SOURCE = HERE / "seeds" / "single-source-identity-decisions-2026-09-15.json"
DEFAULT_DIVISIONS = HERE / "seeds" / "division-review-decisions-2026-09-15.json"
DEFAULT_UNIVERSE = Path("artifacts/international/accreditor-scope-review/reviewed-source-universe.jsonl")
DEFAULT_OUTPUT_DIR = Path("artifacts/international/extended-identity-review")
DRAFT_NAMESPACE = uuid.UUID("ed2d2f67-d75d-5b1f-a408-8aa6510a7f5a")
KNOWN_CURRICULA = {"american", "british", "canadian", "french", "german", "ib"}


def stable_uuid(kind: str, key: str) -> str:
    return str(uuid.uuid5(DRAFT_NAMESPACE, f"{kind}:{key}"))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def current_name(row: dict) -> str:
    return str(row.get("name_en") or row.get("name_ar") or row.get("parent_university_en") or "")


def build(cross_path: Path, single_path: Path, division_path: Path, universe_path: Path, output_dir: Path) -> dict:
    cross = load_json(cross_path)
    single = load_json(single_path)
    divisions = load_json(division_path)
    universe = load_jsonl(universe_path)

    if len(universe) != 106:
        raise AssertionError(f"expected current 106-row source universe, found {len(universe)}")
    states: dict[str, int] = {}
    for row in universe:
        states[row.get("scope_state") or "unknown"] = states.get(row.get("scope_state") or "unknown", 0) + 1
    if states != {"eligible": 103, "excluded": 3}:
        raise AssertionError(f"unexpected current scope-state contract: {states}")

    source_by_key = {(r["source_id"], r["source_record_id"]): r for r in universe}
    if len(source_by_key) != len(universe):
        raise AssertionError("duplicate source keys in current source universe")

    cross_groups = cross["groups"]
    single_records = single["records"]
    division_rows = divisions["divisions"]
    if cross.get("groups_count") != len(cross_groups) or len(cross_groups) != 9:
        raise AssertionError("cross-source review contract drifted")
    if single.get("records_count") != len(single_records) or len(single_records) != 10:
        raise AssertionError("single-source review contract drifted")
    if divisions.get("divisions_count") != len(division_rows) or len(division_rows) != 4:
        raise AssertionError("division review contract drifted")
    if single["safety"].get("absence_of_match_treated_as_uniqueness_proof") is not False:
        raise AssertionError("single-source review must explicitly reject absence-of-match as uniqueness proof")
    if single["safety"].get("automatic_identity_creation_performed") is not False:
        raise AssertionError("single-source identity review must not auto-create identities")

    institution_drafts: list[dict] = []
    reviewed_keys: set[tuple[str, str]] = set()
    review_identity_keys: set[str] = set()

    # Cross-source groups: preserve IDs from the accepted first D2.2 builder.
    for group in cross_groups:
        review_key = group["review_group_id"]
        if review_key in review_identity_keys:
            raise AssertionError(f"duplicate review identity key: {review_key}")
        review_identity_keys.add(review_key)
        memberships: list[dict] = []
        for member in group["source_records"]:
            key = (member["source_id"], member["source_record_id"])
            if key in reviewed_keys:
                raise AssertionError(f"source row reviewed more than once: {key}")
            source = source_by_key.get(key)
            if source is None:
                raise AssertionError(f"cross-source membership missing from current universe: {key}")
            if current_name(source) != member["source_name"]:
                raise AssertionError(
                    f"cross-source name drift for {key}: expected={member['source_name']!r} current={current_name(source)!r}"
                )
            reviewed_keys.add(key)
            memberships.append({
                "source_id": member["source_id"],
                "source_record_id": member["source_record_id"],
                "source_name": member["source_name"],
                "division_scope": member.get("division_scope"),
                "source_scope_state": source.get("scope_state"),
                "source_url": source.get("source_url"),
            })
        institution_drafts.append({
            "draft_institution_id": stable_uuid("institution", review_key),
            "review_identity_key": review_key,
            "review_origin": "cross_source_reconciliation",
            "canonical_name_en": group["provisional_canonical_name_en"],
            "canonical_name_status": "reviewed_provisional",
            "identity_review_decision": group["decision"],
            "identity_review_confidence": group["decision_confidence"],
            "source_record_count": len(memberships),
            "source_memberships": memberships,
            "division_scoped_evidence": group["decision"] == "same_institution_with_division_scoped_evidence",
            "evidence_urls": list(group.get("evidence_urls") or []),
            "review_note": group["review_note"],
            "campus_structure_state": "requires_separate_review",
            "canonical_database_write_performed": False,
            "public_projection_performed": False,
        })

    # Explicit single-source identities: they require review evidence, not merely no matcher hit.
    for record in single_records:
        if record.get("decision") != "confirmed_single_source_identity":
            raise AssertionError(f"unsupported single-source decision: {record.get('decision')}")
        if record.get("decision_confidence") != "high":
            raise AssertionError("single-source identity review currently requires high confidence")
        if len(record.get("evidence_urls") or []) < 2:
            raise AssertionError("single-source identity requires at least two evidence URLs")
        review_key = record["review_identity_key"]
        if review_key in review_identity_keys:
            raise AssertionError(f"single-source review key collides with existing reviewed identity: {review_key}")
        review_identity_keys.add(review_key)
        key = (record["source_id"], record["source_record_id"])
        if key in reviewed_keys:
            raise AssertionError(f"single-source decision targets an already-reviewed source row: {key}")
        source = source_by_key.get(key)
        if source is None:
            raise AssertionError(f"single-source reviewed row missing from current universe: {key}")
        if current_name(source) != record["source_name"]:
            raise AssertionError(
                f"single-source name drift for {key}: expected={record['source_name']!r} current={current_name(source)!r}"
            )
        if source.get("scope_state") != "eligible":
            raise AssertionError(f"single-source identity must be scope-eligible before D2.2 materialization: {key}")
        reviewed_keys.add(key)
        institution_drafts.append({
            "draft_institution_id": stable_uuid("institution", review_key),
            "review_identity_key": review_key,
            "review_origin": "explicit_single_source_identity_review",
            "canonical_name_en": record["provisional_canonical_name_en"],
            "canonical_name_status": "reviewed_provisional",
            "identity_review_decision": record["decision"],
            "identity_review_confidence": record["decision_confidence"],
            "source_record_count": 1,
            "source_memberships": [{
                "source_id": record["source_id"],
                "source_record_id": record["source_record_id"],
                "source_name": record["source_name"],
                "division_scope": None,
                "source_scope_state": source.get("scope_state"),
                "source_url": source.get("source_url"),
            }],
            "division_scoped_evidence": False,
            "evidence_urls": list(record["evidence_urls"]),
            "review_note": record["review_note"],
            "uniqueness_inferred_from_absence_of_match": False,
            "campus_structure_state": "requires_separate_review",
            "canonical_database_write_performed": False,
            "public_projection_performed": False,
        })

    # Preserve the four already-reviewed division drafts under their established parent IDs.
    group_by_id = {g["review_group_id"]: g for g in cross_groups}
    division_drafts: list[dict] = []
    for division in division_rows:
        group_id = division["review_group_id"]
        parent = group_by_id.get(group_id)
        if parent is None or parent["decision"] != "same_institution_with_division_scoped_evidence":
            raise AssertionError(f"division references invalid parent review group: {group_id}")
        parent_keys = {(r["source_id"], r["source_record_id"]) for r in parent["source_records"]}
        for membership in division["source_memberships"]:
            key = (membership["source_id"], membership["source_record_id"])
            if key not in parent_keys:
                raise AssertionError(f"division membership outside parent identity: {key}")
        curricula = list(division.get("curriculum_codes") or [])
        unknown = sorted(set(curricula) - KNOWN_CURRICULA)
        if unknown:
            raise AssertionError(f"unknown division curricula: {unknown}")
        division_drafts.append({
            "draft_school_division_id": stable_uuid("school_division", f"{group_id}:{division['division_key']}"),
            "draft_institution_id": stable_uuid("institution", group_id),
            "review_identity_key": group_id,
            "division_key": division["division_key"],
            "canonical_name_en": division["canonical_name_en"],
            "canonical_name_status": "reviewed_provisional",
            "division_type": division["division_type"],
            "curriculum_codes": curricula,
            "source_memberships": list(division["source_memberships"]),
            "evidence_urls": list(division.get("evidence_urls") or []),
            "review_note": division["review_note"],
            "canonical_database_write_performed": False,
            "public_projection_performed": False,
        })

    institution_drafts.sort(key=lambda row: row["review_identity_key"])
    division_drafts.sort(key=lambda row: (row["review_identity_key"], row["division_key"]))
    if len({row["draft_institution_id"] for row in institution_drafts}) != len(institution_drafts):
        raise AssertionError("deterministic draft institution IDs are not unique")

    unreviewed = [
        {
            "source_id": row["source_id"],
            "source_record_id": row["source_record_id"],
            "source_name": current_name(row),
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
    memberships_path = output_dir / "reviewed-source-memberships.jsonl"
    queue_path = output_dir / "unreviewed-source-queue.jsonl"
    write_jsonl(institutions_path, institution_drafts)
    write_jsonl(divisions_path, division_drafts)
    write_jsonl(queue_path, unreviewed)
    memberships = []
    for institution in institution_drafts:
        for membership in institution["source_memberships"]:
            memberships.append({
                "draft_institution_id": institution["draft_institution_id"],
                "review_identity_key": institution["review_identity_key"],
                "review_origin": institution["review_origin"],
                **membership,
            })
    write_jsonl(memberships_path, memberships)

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.2_extended_reviewed_identity_materialization",
        "deterministic_id_namespace": str(DRAFT_NAMESPACE),
        "source_universe_rows": len(universe),
        "source_scope_states": states,
        "cross_source_reviewed_identities": len(cross_groups),
        "explicit_single_source_reviewed_identities": len(single_records),
        "reviewed_identity_drafts": len(institution_drafts),
        "reviewed_source_memberships": len(reviewed_keys),
        "reviewed_division_drafts": len(division_drafts),
        "unreviewed_source_rows": len(unreviewed),
        "full_universe_unique_institution_count_claimed": None,
        "absence_of_match_treated_as_uniqueness_proof": False,
        "automatic_merges_performed": 0,
        "canonical_database_rows_written": 0,
        "runtime_database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "institutions": institutions_path.name,
            "source_memberships": memberships_path.name,
            "school_divisions": divisions_path.name,
            "unreviewed_source_queue": queue_path.name,
        },
    }
    (output_dir / "extended-identity-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cross-source-decisions", type=Path, default=DEFAULT_CROSS_SOURCE)
    parser.add_argument("--single-source-decisions", type=Path, default=DEFAULT_SINGLE_SOURCE)
    parser.add_argument("--division-decisions", type=Path, default=DEFAULT_DIVISIONS)
    parser.add_argument("--universe", type=Path, default=DEFAULT_UNIVERSE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    build(args.cross_source_decisions, args.single_source_decisions, args.division_decisions, args.universe, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
