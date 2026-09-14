#!/usr/bin/env python3
"""Apply dated incremental D2.2 single-source identity review batches.

The accepted hierarchy-review artifact is the immutable base for this stage. New
single-source identities are admitted only through checked-in review batches with
primary/authoritative evidence. The builder never treats an unmatched source row
as uniqueness proof, never changes a source ID, never merges identities, and never
writes a runtime/canonical database or public projection.
"""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_BASE_DIR = Path("artifacts/international/hierarchy-review")
DEFAULT_UNIVERSE = Path("artifacts/international/accreditor-scope-review/reviewed-source-universe.jsonl")
DEFAULT_OUTPUT_DIR = Path("artifacts/international/incremental-identity-review")
DEFAULT_BATCH_GLOB = "single-source-identity-decisions-*-batch*.json"
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
    return str(row.get("name_en") or row.get("name_ar") or row.get("parent_university_en") or "")


def discover_batches() -> list[Path]:
    return sorted((HERE / "seeds").glob(DEFAULT_BATCH_GLOB))


def build(base_dir: Path, universe_path: Path, output_dir: Path, batch_paths: list[Path]) -> dict:
    if not batch_paths:
        raise AssertionError("at least one incremental single-source identity review batch is required")

    base_summary = load_json(base_dir / "hierarchy-review-summary.json")
    institutions = load_jsonl(base_dir / "reviewed-institution-drafts.jsonl")
    divisions = load_jsonl(base_dir / "reviewed-school-division-drafts.jsonl")
    division_memberships = load_jsonl(base_dir / "division-source-scope-memberships.jsonl")
    queue = load_jsonl(base_dir / "unreviewed-source-queue.jsonl")
    universe = load_jsonl(universe_path)

    if len(universe) != 106:
        raise AssertionError(f"expected current 106-row source universe, found {len(universe)}")
    if base_summary.get("reviewed_institution_drafts") != len(institutions) or len(institutions) != 20:
        raise AssertionError("incremental identity base must contain the accepted 20 hierarchy-reviewed institution drafts")
    if base_summary.get("reviewed_division_drafts") != len(divisions) or len(divisions) != 10:
        raise AssertionError("incremental identity base must contain the accepted 10 hierarchy-reviewed division drafts")
    if base_summary.get("reviewed_unique_source_rows") != 31:
        raise AssertionError("incremental identity base reviewed-source contract drifted")
    if base_summary.get("unreviewed_source_rows") != len(queue) or len(queue) != 75:
        raise AssertionError("incremental identity base queue contract drifted")

    source_by_key = {(row["source_id"], row["source_record_id"]): row for row in universe}
    if len(source_by_key) != len(universe):
        raise AssertionError("current source universe contains duplicate source keys")

    institution_by_key = {row["review_identity_key"]: row for row in institutions}
    if len(institution_by_key) != len(institutions):
        raise AssertionError("duplicate review_identity_key in hierarchy-reviewed institution drafts")

    covered_source_keys: set[tuple[str, str]] = {
        (member["source_id"], member["source_record_id"])
        for institution in institutions
        for member in institution.get("source_memberships", [])
    }
    covered_source_keys |= {
        (member["source_id"], member["source_record_id"])
        for member in division_memberships
    }
    if len(covered_source_keys) != 31:
        raise AssertionError(f"expected 31 source rows covered by hierarchy review, found {len(covered_source_keys)}")

    queue_by_key = {(row["source_id"], row["source_record_id"]): row for row in queue}
    if len(queue_by_key) != len(queue):
        raise AssertionError("duplicate source key in hierarchy review queue")

    incremental_memberships: list[dict] = []
    applied_batches: list[dict] = []
    seen_batch_ids: set[str] = set()
    new_source_keys: set[tuple[str, str]] = set()

    for batch_path in batch_paths:
        batch = load_json(batch_path)
        records = batch.get("records") or []
        if batch.get("records_count") != len(records):
            raise AssertionError(f"records_count mismatch in {batch_path.name}")
        batch_id = str(batch.get("batch_id") or batch_path.stem)
        if batch_id in seen_batch_ids:
            raise AssertionError(f"duplicate incremental identity batch_id: {batch_id}")
        seen_batch_ids.add(batch_id)
        safety = batch.get("safety") or {}
        if safety.get("absence_of_match_treated_as_uniqueness_proof") is not False:
            raise AssertionError(f"{batch_path.name} must reject absence-of-match as uniqueness proof")
        if safety.get("automatic_identity_creation_performed") is not False:
            raise AssertionError(f"{batch_path.name} must reject automatic identity creation")
        if safety.get("automatic_merges_performed") != 0:
            raise AssertionError(f"{batch_path.name} must perform zero automatic merges")

        for record in records:
            if record.get("decision") != "confirmed_single_source_identity":
                raise AssertionError(f"unsupported incremental identity decision: {record.get('decision')}")
            if record.get("decision_confidence") != "high":
                raise AssertionError("incremental single-source identities require high-confidence review")
            if len(record.get("evidence_urls") or []) < 2:
                raise AssertionError("incremental single-source identity requires at least two evidence URLs")

            review_key = record["review_identity_key"]
            if review_key in institution_by_key:
                raise AssertionError(f"incremental review identity already exists: {review_key}")
            source_key = (record["source_id"], record["source_record_id"])
            if source_key in covered_source_keys or source_key in new_source_keys:
                raise AssertionError(f"incremental identity source row already reviewed: {source_key}")
            if source_key not in queue_by_key:
                raise AssertionError(f"incremental identity source row is not in the accepted review queue: {source_key}")

            source = source_by_key.get(source_key)
            if source is None:
                raise AssertionError(f"incremental identity source row missing from current universe: {source_key}")
            if source.get("scope_state") != "eligible":
                raise AssertionError(f"incremental identity source row must be scope-eligible: {source_key}")
            if current_name(source) != record["source_name"]:
                raise AssertionError(
                    f"incremental identity name drift for {source_key}: "
                    f"expected={record['source_name']!r} current={current_name(source)!r}"
                )

            membership = {
                "source_id": record["source_id"],
                "source_record_id": record["source_record_id"],
                "source_name": record["source_name"],
                "division_scope": None,
                "source_scope_state": source.get("scope_state"),
                "source_url": source.get("source_url"),
            }
            draft = {
                "draft_institution_id": stable_uuid("institution", review_key),
                "review_identity_key": review_key,
                "review_origin": "incremental_explicit_single_source_identity_review",
                "review_batch_id": batch_id,
                "canonical_name_en": record["provisional_canonical_name_en"],
                "canonical_name_status": "reviewed_provisional",
                "identity_review_decision": record["decision"],
                "identity_review_confidence": record["decision_confidence"],
                "source_record_count": 1,
                "source_memberships": [membership],
                "division_scoped_evidence": False,
                "evidence_urls": list(record["evidence_urls"]),
                "review_note": record["review_note"],
                "uniqueness_inferred_from_absence_of_match": False,
                "campus_structure_state": "requires_separate_review",
                "canonical_database_write_performed": False,
                "public_projection_performed": False,
            }
            institutions.append(draft)
            institution_by_key[review_key] = draft
            new_source_keys.add(source_key)
            incremental_memberships.append({
                "draft_institution_id": draft["draft_institution_id"],
                "review_identity_key": review_key,
                "review_batch_id": batch_id,
                **membership,
            })
            del queue_by_key[source_key]

        applied_batches.append({
            "batch_id": batch_id,
            "path": batch_path.name,
            "records_count": len(records),
        })

    if len({row["draft_institution_id"] for row in institutions}) != len(institutions):
        raise AssertionError("deterministic institution IDs are not unique after incremental review")

    institutions.sort(key=lambda row: row["review_identity_key"])
    divisions.sort(key=lambda row: (row["review_identity_key"], row["division_key"]))
    division_memberships.sort(key=lambda row: (row["review_identity_key"], row["division_key"], row["source_id"]))
    incremental_memberships.sort(key=lambda row: (row["review_identity_key"], row["source_id"], row["source_record_id"]))
    queue_out = sorted(queue_by_key.values(), key=lambda row: (row["source_id"], row["source_record_id"]))

    reviewed_unique_source_rows = len(covered_source_keys | new_source_keys)
    output_dir.mkdir(parents=True, exist_ok=True)
    institutions_path = output_dir / "reviewed-institution-drafts.jsonl"
    divisions_path = output_dir / "reviewed-school-division-drafts.jsonl"
    division_memberships_path = output_dir / "division-source-scope-memberships.jsonl"
    incremental_memberships_path = output_dir / "incremental-source-memberships.jsonl"
    queue_path = output_dir / "unreviewed-source-queue.jsonl"
    write_jsonl(institutions_path, institutions)
    write_jsonl(divisions_path, divisions)
    write_jsonl(division_memberships_path, division_memberships)
    write_jsonl(incremental_memberships_path, incremental_memberships)
    write_jsonl(queue_path, queue_out)

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.2_incremental_identity_review_materialization",
        "deterministic_id_namespace": str(DRAFT_NAMESPACE),
        "source_universe_rows": len(universe),
        "base_reviewed_institution_drafts": 20,
        "base_reviewed_division_drafts": 10,
        "base_reviewed_unique_source_rows": 31,
        "incremental_review_batches": len(applied_batches),
        "incremental_review_batch_details": applied_batches,
        "new_explicit_single_source_identities": len(new_source_keys),
        "reviewed_institution_drafts": len(institutions),
        "reviewed_division_drafts": len(divisions),
        "reviewed_unique_source_rows": reviewed_unique_source_rows,
        "unreviewed_source_rows": len(queue_out),
        "full_universe_unique_institution_count_claimed": None,
        "absence_of_match_treated_as_uniqueness_proof": False,
        "automatic_identity_creation_performed": False,
        "automatic_merges_performed": 0,
        "canonical_database_rows_written": 0,
        "runtime_database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "institutions": institutions_path.name,
            "school_divisions": divisions_path.name,
            "division_source_scope_memberships": division_memberships_path.name,
            "incremental_source_memberships": incremental_memberships_path.name,
            "unreviewed_source_queue": queue_path.name,
        },
    }
    (output_dir / "incremental-identity-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--universe", type=Path, default=DEFAULT_UNIVERSE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--batch", dest="batches", action="append", type=Path)
    args = parser.parse_args()
    batch_paths = args.batches if args.batches else discover_batches()
    build(args.base_dir, args.universe, args.output_dir, batch_paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
