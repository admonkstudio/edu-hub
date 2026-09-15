#!/usr/bin/env python3
"""Materialize explicit D2.2 identities for separately qualified discovery rows.

This stage starts from the accepted incremental identity-review artifacts for the
original 106-row universe and may add only discovery rows that have already passed
a separate D2.1 primary/recognized eligibility review.

Two explicit relationships are supported:
1. a qualified discovery row reviewed as a standalone institution identity; and
2. a qualified discovery row reviewed as the same institution as an original
   source row that is still in the accepted D2.2 review queue.

Neither relationship is inferred automatically. Absence of a match is never
uniqueness proof, and qualified discovery rows without an explicit D2.2 decision
remain in a separate queue.
"""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_BASE_DIR = Path("artifacts/international/incremental-identity-review")
DEFAULT_QUALIFIED_LEADS = Path(
    "artifacts/international/british-council-primary-scope-review/british-council-leads-with-primary-review.jsonl"
)
DEFAULT_DECISION_GLOB = "discovered-identity-decisions-*.json"
DEFAULT_OUTPUT_DIR = Path("artifacts/international/discovery-identity-review")
DRAFT_NAMESPACE = uuid.UUID("ed2d2f67-d75d-5b1f-a408-8aa6510a7f5a")


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
    """Read names from both source-universe rows and materialized queue rows."""
    return str(
        row.get("source_name")
        or row.get("name_en")
        or row.get("name_ar")
        or row.get("parent_university_en")
        or ""
    )


def discover_decisions() -> list[Path]:
    paths = sorted((HERE / "seeds").glob(DEFAULT_DECISION_GLOB))
    if not paths:
        raise AssertionError("no discovered identity decision batches found")
    return paths


def build(base_dir: Path, qualified_leads_path: Path, decision_paths: list[Path], output_dir: Path) -> dict:
    base_summary = load_json(base_dir / "incremental-identity-summary.json")
    institutions = load_jsonl(base_dir / "reviewed-institution-drafts.jsonl")
    divisions = load_jsonl(base_dir / "reviewed-school-division-drafts.jsonl")
    division_memberships = load_jsonl(base_dir / "division-source-scope-memberships.jsonl")
    original_queue = load_jsonl(base_dir / "unreviewed-source-queue.jsonl")
    discovery_rows = load_jsonl(qualified_leads_path)

    if base_summary.get("reviewed_institution_drafts") != len(institutions) or len(institutions) != 24:
        raise AssertionError("discovery identity review requires the accepted 24-institution incremental base")
    if base_summary.get("reviewed_division_drafts") != len(divisions) or len(divisions) != 10:
        raise AssertionError("discovery identity review requires the accepted 10-division incremental base")
    if base_summary.get("reviewed_unique_source_rows") != 35:
        raise AssertionError("incremental base reviewed-source contract drifted")
    if base_summary.get("unreviewed_source_rows") != len(original_queue) or len(original_queue) != 71:
        raise AssertionError("incremental base original review queue contract drifted")
    if not discovery_rows:
        raise AssertionError("British Council discovery review input is empty")

    lead_by_key = {(row["source_id"], row["source_record_id"]): row for row in discovery_rows}
    if len(lead_by_key) != len(discovery_rows):
        raise AssertionError("duplicate discovery source key in reviewed-lead input")

    original_queue_by_key = {(row["source_id"], row["source_record_id"]): row for row in original_queue}
    if len(original_queue_by_key) != len(original_queue):
        raise AssertionError("duplicate source key in accepted original-source identity queue")

    institution_by_review_key = {row["review_identity_key"]: row for row in institutions}
    if len(institution_by_review_key) != len(institutions):
        raise AssertionError("duplicate review identity key in incremental identity base")

    existing_source_keys = {
        (member["source_id"], member["source_record_id"])
        for institution in institutions
        for member in institution.get("source_memberships", [])
    }
    existing_source_keys |= {
        (member["source_id"], member["source_record_id"])
        for member in division_memberships
    }

    discovered_memberships: list[dict] = []
    overlap_original_memberships: list[dict] = []
    seen_discovery_source_keys: set[tuple[str, str]] = set()
    reviewed_original_overlap_keys: set[tuple[str, str]] = set()
    seen_batch_ids: set[str] = set()
    batch_details: list[dict] = []

    for decisions_path in decision_paths:
        decisions = load_json(decisions_path)
        decision_rows = decisions.get("records") or []
        if decisions.get("records_count") != len(decision_rows):
            raise AssertionError(f"records_count mismatch in {decisions_path.name}")
        if not decision_rows:
            raise AssertionError(f"discovered identity decision batch is empty: {decisions_path.name}")
        batch_id = str(decisions.get("batch_id") or decisions_path.stem)
        if batch_id in seen_batch_ids:
            raise AssertionError(f"duplicate discovered identity batch_id: {batch_id}")
        seen_batch_ids.add(batch_id)

        safety = decisions.get("safety") or {}
        if safety.get("absence_of_match_treated_as_uniqueness_proof") is not False:
            raise AssertionError("absence of a match may not be uniqueness proof")
        if safety.get("unqualified_discovery_rows_entered_identity_review") is not False:
            raise AssertionError("unqualified discovery rows may not enter D2.2 identity materialization")
        if safety.get("automatic_identity_creation_performed") is not False:
            raise AssertionError("identity creation must be explicit, not automatic")
        if safety.get("automatic_merges_performed") != 0:
            raise AssertionError("discovery identity review must perform zero automatic merges")

        for decision in decision_rows:
            decision_type = decision.get("decision")
            if decision_type not in {
                "confirmed_discovered_single_source_identity",
                "confirmed_discovery_overlap_with_original_source_identity",
            }:
                raise AssertionError(f"unsupported discovery identity decision: {decision_type}")
            if decision.get("decision_confidence") != "high":
                raise AssertionError("discovery identities require high-confidence explicit review")
            if len(decision.get("evidence_urls") or []) < 2:
                raise AssertionError("discovery identity decision requires at least two evidence URLs")

            review_key = decision["review_identity_key"]
            if review_key in institution_by_review_key:
                raise AssertionError(f"discovery identity review key already exists: {review_key}")

            discovery_key = (decision["source_id"], decision["source_record_id"])
            if discovery_key in existing_source_keys or discovery_key in seen_discovery_source_keys:
                raise AssertionError(f"discovery source row already has a reviewed D2.2 membership: {discovery_key}")
            discovery = lead_by_key.get(discovery_key)
            if discovery is None:
                raise AssertionError(f"discovery identity source row missing from reviewed lead input: {discovery_key}")
            if discovery.get("scope_state") != "eligible":
                raise AssertionError(f"discovery identity row must pass D2.1 eligibility first: {discovery_key}")
            if discovery.get("eligibility_review_state") != "reviewed_primary_or_recognized_evidence":
                raise AssertionError(f"discovery identity row lacks explicit D2.1 primary review: {discovery_key}")
            if discovery.get("name_en") != decision["source_name"]:
                raise AssertionError(
                    f"discovery source name drift for {discovery_key}: "
                    f"expected={decision['source_name']!r} current={discovery.get('name_en')!r}"
                )

            discovery_membership = {
                "source_id": discovery["source_id"],
                "source_record_id": discovery["source_record_id"],
                "source_name": discovery["name_en"],
                "division_scope": None,
                "source_scope_state": discovery["scope_state"],
                "source_url": discovery["source_url"],
                "eligibility_review_batch_id": discovery.get("eligibility_review_batch_id"),
            }
            source_memberships = [discovery_membership]
            review_origin = "explicit_qualified_discovery_single_source_identity_review"

            if decision_type == "confirmed_discovery_overlap_with_original_source_identity":
                original_key = (decision["original_source_id"], decision["original_source_record_id"])
                if original_key in existing_source_keys or original_key in reviewed_original_overlap_keys:
                    raise AssertionError(f"original source row already has a reviewed D2.2 membership: {original_key}")
                original = original_queue_by_key.get(original_key)
                if original is None:
                    raise AssertionError(f"overlap target is not in the accepted original-source review queue: {original_key}")
                if current_name(original) != decision["original_source_name"]:
                    raise AssertionError(
                        f"original source name drift for {original_key}: "
                        f"expected={decision['original_source_name']!r} current={current_name(original)!r}"
                    )
                if original.get("scope_state") != "eligible":
                    raise AssertionError(f"overlap target must be scope-eligible: {original_key}")

                original_membership = {
                    "source_id": original["source_id"],
                    "source_record_id": original["source_record_id"],
                    "source_name": current_name(original),
                    "division_scope": None,
                    "source_scope_state": original.get("scope_state"),
                    "source_url": original.get("source_url"),
                }
                source_memberships.insert(0, original_membership)
                reviewed_original_overlap_keys.add(original_key)
                del original_queue_by_key[original_key]
                review_origin = "explicit_qualified_discovery_to_original_source_identity_review"
            else:
                original_membership = None

            draft = {
                "draft_institution_id": stable_uuid("institution", review_key),
                "review_identity_key": review_key,
                "review_origin": review_origin,
                "review_batch_id": batch_id,
                "canonical_name_en": decision["provisional_canonical_name_en"],
                "canonical_name_status": "reviewed_provisional",
                "identity_review_decision": decision_type,
                "identity_review_confidence": decision["decision_confidence"],
                "source_record_count": len(source_memberships),
                "source_memberships": source_memberships,
                "division_scoped_evidence": False,
                "evidence_urls": list(decision["evidence_urls"]),
                "review_note": decision["review_note"],
                "uniqueness_inferred_from_absence_of_match": False,
                "campus_structure_state": "requires_separate_review",
                "canonical_database_write_performed": False,
                "public_projection_performed": False,
            }
            institutions.append(draft)
            institution_by_review_key[review_key] = draft
            seen_discovery_source_keys.add(discovery_key)
            discovered_memberships.append({
                "draft_institution_id": draft["draft_institution_id"],
                "review_identity_key": review_key,
                "review_batch_id": batch_id,
                **discovery_membership,
            })
            if original_membership is not None:
                overlap_original_memberships.append({
                    "draft_institution_id": draft["draft_institution_id"],
                    "review_identity_key": review_key,
                    "review_batch_id": batch_id,
                    **original_membership,
                })

        batch_details.append({
            "batch_id": batch_id,
            "seed": decisions_path.name,
            "reviewed_identity_rows": len(decision_rows),
        })

    if len({row["draft_institution_id"] for row in institutions}) != len(institutions):
        raise AssertionError("deterministic institution IDs are not unique after discovery identity review")

    unqualified_discovery = [row for row in discovery_rows if row.get("scope_state") != "eligible"]
    qualified_identity_queue = [
        row for row in discovery_rows
        if row.get("scope_state") == "eligible"
        and (row["source_id"], row["source_record_id"]) not in seen_discovery_source_keys
    ]
    original_queue_out = sorted(
        original_queue_by_key.values(), key=lambda row: (row["source_id"], row["source_record_id"])
    )

    institutions.sort(key=lambda row: row["review_identity_key"])
    divisions.sort(key=lambda row: (row["review_identity_key"], row["division_key"]))
    discovered_memberships.sort(key=lambda row: (row["review_identity_key"], row["source_record_id"]))
    overlap_original_memberships.sort(key=lambda row: (row["review_identity_key"], row["source_record_id"]))

    output_dir.mkdir(parents=True, exist_ok=True)
    institutions_path = output_dir / "reviewed-institution-drafts.jsonl"
    divisions_path = output_dir / "reviewed-school-division-drafts.jsonl"
    discovered_memberships_path = output_dir / "discovered-source-memberships.jsonl"
    overlap_original_memberships_path = output_dir / "discovery-overlap-original-source-memberships.jsonl"
    original_queue_path = output_dir / "original-unreviewed-source-queue.jsonl"
    discovery_queue_path = output_dir / "unqualified-discovery-queue.jsonl"
    qualified_queue_path = output_dir / "qualified-discovery-identity-queue.jsonl"
    write_jsonl(institutions_path, institutions)
    write_jsonl(divisions_path, divisions)
    write_jsonl(discovered_memberships_path, discovered_memberships)
    write_jsonl(overlap_original_memberships_path, overlap_original_memberships)
    write_jsonl(original_queue_path, original_queue_out)
    write_jsonl(discovery_queue_path, unqualified_discovery)
    write_jsonl(qualified_queue_path, qualified_identity_queue)

    reviewed_source_or_lead_rows = 35 + len(reviewed_original_overlap_keys) + len(discovered_memberships)
    summary = {
        "schema_version": 3,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.2_discovery_identity_review_materialization",
        "deterministic_id_namespace": str(DRAFT_NAMESPACE),
        "base_reviewed_institution_drafts": 24,
        "discovery_identity_review_batches": len(batch_details),
        "discovery_identity_review_batch_details": batch_details,
        "new_discovery_driven_identity_drafts": len(discovered_memberships),
        "reviewed_institution_drafts": len(institutions),
        "reviewed_division_drafts": len(divisions),
        "base_reviewed_original_source_rows": 35,
        "reviewed_original_source_rows_from_discovery_overlap": len(reviewed_original_overlap_keys),
        "reviewed_discovery_source_rows": len(discovered_memberships),
        "reviewed_source_or_lead_rows": reviewed_source_or_lead_rows,
        "original_unreviewed_source_rows": len(original_queue_out),
        "unqualified_discovery_rows": len(unqualified_discovery),
        "qualified_discovery_rows_pending_identity_review": len(qualified_identity_queue),
        "full_universe_unique_institution_count_claimed": None,
        "absence_of_match_treated_as_uniqueness_proof": False,
        "unqualified_discovery_rows_entered_identity_review": False,
        "automatic_merges_performed": 0,
        "canonical_database_rows_written": 0,
        "runtime_database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "institutions": institutions_path.name,
            "school_divisions": divisions_path.name,
            "discovered_source_memberships": discovered_memberships_path.name,
            "discovery_overlap_original_source_memberships": overlap_original_memberships_path.name,
            "original_unreviewed_source_queue": original_queue_path.name,
            "unqualified_discovery_queue": discovery_queue_path.name,
            "qualified_discovery_identity_queue": qualified_queue_path.name,
        },
    }
    (output_dir / "discovery-identity-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--qualified-leads", type=Path, default=DEFAULT_QUALIFIED_LEADS)
    parser.add_argument("--decisions", dest="decisions", action="append", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    decision_paths = args.decisions if args.decisions else discover_decisions()
    build(args.base_dir, args.qualified_leads, decision_paths, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
