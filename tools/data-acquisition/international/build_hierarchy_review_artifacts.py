#!/usr/bin/env python3
"""Extend reviewed D2.2 drafts with explicit institution -> division hierarchy decisions.

Some authoritative source rows describe a curriculum division rather than the
parent institution. Conversely, a current first-party parent identity can be
well evidenced even when no row in the present source universe names that parent
verbatim. This builder materializes only checked-in hierarchy decisions and
preserves source scope instead of forcing every source row to institution level.

The outputs are portable review artifacts only: no runtime database write,
automatic hierarchy inference, automatic identity merge or public projection.
"""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DECISIONS = HERE / "seeds" / "hierarchy-review-decisions-2026-09-15.json"
DEFAULT_EXTENDED_DIR = Path("artifacts/international/extended-identity-review")
DEFAULT_UNIVERSE = Path("artifacts/international/accreditor-scope-review/reviewed-source-universe.jsonl")
DEFAULT_OUTPUT_DIR = Path("artifacts/international/hierarchy-review")
DRAFT_NAMESPACE = uuid.UUID("ed2d2f67-d75d-5b1f-a408-8aa6510a7f5a")
KNOWN_CURRICULA = {"american", "british", "canadian", "french", "german", "ib", "egyptian_national"}


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


def build(decisions_path: Path, extended_dir: Path, universe_path: Path, output_dir: Path) -> dict:
    decisions = load_json(decisions_path)
    universe = load_jsonl(universe_path)
    institutions = load_jsonl(extended_dir / "reviewed-institution-drafts.jsonl")
    divisions = load_jsonl(extended_dir / "reviewed-school-division-drafts.jsonl")
    queue = load_jsonl(extended_dir / "unreviewed-source-queue.jsonl")
    extended_summary = load_json(extended_dir / "extended-identity-summary.json")

    if extended_summary.get("reviewed_identity_drafts") != len(institutions) or len(institutions) != 19:
        raise AssertionError("extended identity input must contain 19 reviewed institution drafts")
    if extended_summary.get("reviewed_division_drafts") != len(divisions) or len(divisions) != 4:
        raise AssertionError("extended identity input must contain 4 reviewed division drafts")
    if extended_summary.get("reviewed_source_memberships") != 30:
        raise AssertionError("extended identity source-membership contract drifted")
    if extended_summary.get("unreviewed_source_rows") != len(queue) or len(queue) != 76:
        raise AssertionError("extended identity review queue contract drifted")
    if len(universe) != 106:
        raise AssertionError(f"expected 106 source rows, found {len(universe)}")

    source_by_key = {(row["source_id"], row["source_record_id"]): row for row in universe}
    if len(source_by_key) != len(universe):
        raise AssertionError("current source universe contains duplicate source keys")

    parents = decisions.get("new_parent_institutions") or []
    extensions = decisions.get("division_extensions") or []
    if decisions.get("new_parent_institutions_count") != len(parents) or len(parents) != 1:
        raise AssertionError("hierarchy review must contain exactly one new parent institution in this batch")
    if decisions.get("division_extensions_count") != len(extensions) or len(extensions) != 6:
        raise AssertionError("hierarchy review must contain exactly six division extensions in this batch")
    safety = decisions.get("safety") or {}
    if safety.get("automatic_hierarchy_inference_performed") is not False:
        raise AssertionError("hierarchy decisions must reject automatic hierarchy inference")
    if safety.get("new_parent_created_from_absence_of_source_match") is not False:
        raise AssertionError("new parent identity requires affirmative first-party evidence")
    if safety.get("source_row_forced_to_institution_level") is not False:
        raise AssertionError("source rows must retain their reviewed real scope")

    institution_by_key = {row["review_identity_key"]: row for row in institutions}
    if len(institution_by_key) != len(institutions):
        raise AssertionError("duplicate review_identity_key in extended identity artifacts")

    added_parents: list[dict] = []
    for parent in parents:
        key = parent["review_identity_key"]
        if key in institution_by_key:
            raise AssertionError(f"new hierarchy parent already exists: {key}")
        if parent.get("decision") != "confirmed_parent_institution_from_first_party_evidence":
            raise AssertionError(f"unsupported parent review decision: {parent.get('decision')}")
        if parent.get("decision_confidence") != "high":
            raise AssertionError("new hierarchy parent requires high-confidence review")
        if len(parent.get("evidence_urls") or []) < 2:
            raise AssertionError("new hierarchy parent requires at least two first-party evidence URLs")
        if parent.get("source_memberships"):
            raise AssertionError("this hierarchy-parent batch expects the new parent to be first-party evidence-only")

        row = {
            "draft_institution_id": stable_uuid("institution", key),
            "review_identity_key": key,
            "review_origin": "explicit_first_party_parent_hierarchy_review",
            "canonical_name_en": parent["provisional_canonical_name_en"],
            "canonical_name_status": "reviewed_provisional",
            "identity_review_decision": parent["decision"],
            "identity_review_confidence": parent["decision_confidence"],
            "source_record_count": 0,
            "source_memberships": [],
            "division_scoped_evidence": True,
            "evidence_urls": list(parent["evidence_urls"]),
            "review_note": parent["review_note"],
            "created_from_absence_of_match": False,
            "campus_structure_state": "requires_separate_review",
            "canonical_database_write_performed": False,
            "public_projection_performed": False,
        }
        institutions.append(row)
        institution_by_key[key] = row
        added_parents.append(row)

    existing_division_keys = {(row["review_identity_key"], row["division_key"]) for row in divisions}
    hierarchy_memberships: list[dict] = []
    newly_reviewed_source_keys: set[tuple[str, str]] = set()

    # Source keys already covered by an institution-level reviewed membership.
    identity_reviewed_source_keys = {
        (member["source_id"], member["source_record_id"])
        for institution in institutions
        for member in institution.get("source_memberships", [])
    }

    for extension in extensions:
        parent_key = extension["review_identity_key"]
        parent = institution_by_key.get(parent_key)
        if parent is None:
            raise AssertionError(f"division extension references unknown reviewed parent: {parent_key}")
        div_key = extension["division_key"]
        pair = (parent_key, div_key)
        if pair in existing_division_keys:
            raise AssertionError(f"division extension duplicates an existing reviewed division: {pair}")
        existing_division_keys.add(pair)
        if extension.get("division_type") != "curriculum_stream":
            raise AssertionError("current hierarchy extension supports curriculum_stream divisions only")
        curricula = list(extension.get("curriculum_codes") or [])
        unknown = sorted(set(curricula) - KNOWN_CURRICULA)
        if unknown:
            raise AssertionError(f"unknown curriculum codes for {pair}: {unknown}")
        if not extension.get("evidence_urls"):
            raise AssertionError(f"division extension requires first-party evidence: {pair}")

        memberships = []
        for membership in extension.get("source_memberships") or []:
            source_key = (membership["source_id"], membership["source_record_id"])
            source = source_by_key.get(source_key)
            if source is None:
                raise AssertionError(f"division membership missing from source universe: {source_key}")
            if source.get("scope_state") != "eligible":
                raise AssertionError(f"division membership must be eligible before hierarchy materialization: {source_key}")
            if membership.get("source_scope") != div_key:
                raise AssertionError(f"division source_scope must match division_key for {source_key}")
            normalized = dict(membership)
            normalized["source_name"] = source.get("name_en") or source.get("name_ar") or source.get("parent_university_en")
            normalized["source_url"] = source.get("source_url")
            memberships.append(normalized)
            hierarchy_memberships.append({
                "draft_institution_id": parent["draft_institution_id"],
                "draft_school_division_id": stable_uuid("school_division", f"{parent_key}:{div_key}"),
                "review_identity_key": parent_key,
                "division_key": div_key,
                **normalized,
            })
            if source_key not in identity_reviewed_source_keys:
                newly_reviewed_source_keys.add(source_key)

        divisions.append({
            "draft_school_division_id": stable_uuid("school_division", f"{parent_key}:{div_key}"),
            "draft_institution_id": parent["draft_institution_id"],
            "review_identity_key": parent_key,
            "division_key": div_key,
            "canonical_name_en": extension["canonical_name_en"],
            "canonical_name_status": "reviewed_provisional",
            "division_type": extension["division_type"],
            "curriculum_codes": curricula,
            "source_memberships": memberships,
            "evidence_urls": list(extension["evidence_urls"]),
            "review_note": extension["review_note"],
            "hierarchy_reviewed": True,
            "canonical_database_write_performed": False,
            "public_projection_performed": False,
        })

    if len({row["draft_institution_id"] for row in institutions}) != len(institutions):
        raise AssertionError("deterministic institution IDs are not unique after hierarchy extension")
    if len({row["draft_school_division_id"] for row in divisions}) != len(divisions):
        raise AssertionError("deterministic division IDs are not unique after hierarchy extension")

    queue_keys = {(row["source_id"], row["source_record_id"]): row for row in queue}
    for key in newly_reviewed_source_keys:
        if key not in queue_keys:
            raise AssertionError(f"newly division-reviewed source was not in prior review queue: {key}")
        del queue_keys[key]
    queue_out = list(queue_keys.values())
    queue_out.sort(key=lambda row: (row["source_id"], row["source_record_id"]))

    reviewed_unique_source_keys = identity_reviewed_source_keys | newly_reviewed_source_keys
    institutions.sort(key=lambda row: row["review_identity_key"])
    divisions.sort(key=lambda row: (row["review_identity_key"], row["division_key"]))
    hierarchy_memberships.sort(key=lambda row: (row["review_identity_key"], row["division_key"], row["source_id"]))

    output_dir.mkdir(parents=True, exist_ok=True)
    institutions_path = output_dir / "reviewed-institution-drafts.jsonl"
    divisions_path = output_dir / "reviewed-school-division-drafts.jsonl"
    memberships_path = output_dir / "division-source-scope-memberships.jsonl"
    queue_path = output_dir / "unreviewed-source-queue.jsonl"
    write_jsonl(institutions_path, institutions)
    write_jsonl(divisions_path, divisions)
    write_jsonl(memberships_path, hierarchy_memberships)
    write_jsonl(queue_path, queue_out)

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.2_hierarchy_review_materialization",
        "source_universe_rows": len(universe),
        "base_reviewed_institution_drafts": 19,
        "new_first_party_parent_institutions": len(added_parents),
        "reviewed_institution_drafts": len(institutions),
        "base_reviewed_division_drafts": 4,
        "new_reviewed_division_drafts": len(extensions),
        "reviewed_division_drafts": len(divisions),
        "division_source_scope_memberships": len(hierarchy_memberships),
        "newly_reviewed_source_rows_via_division_scope": len(newly_reviewed_source_keys),
        "reviewed_unique_source_rows": len(reviewed_unique_source_keys),
        "unreviewed_source_rows": len(queue_out),
        "full_universe_unique_institution_count_claimed": None,
        "automatic_hierarchy_inference_performed": False,
        "source_row_forced_to_institution_level": False,
        "automatic_merges_performed": 0,
        "canonical_database_rows_written": 0,
        "runtime_database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "institutions": institutions_path.name,
            "school_divisions": divisions_path.name,
            "division_source_scope_memberships": memberships_path.name,
            "unreviewed_source_queue": queue_path.name,
        },
    }
    (output_dir / "hierarchy-review-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--extended-dir", type=Path, default=DEFAULT_EXTENDED_DIR)
    parser.add_argument("--universe", type=Path, default=DEFAULT_UNIVERSE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    build(args.decisions, args.extended_dir, args.universe, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
