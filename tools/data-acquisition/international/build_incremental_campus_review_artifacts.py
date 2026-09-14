#!/usr/bin/env python3
"""Extend accepted D2.2 campus evidence with explicit incremental review batches.

The first campus package covers the original nine cross-source identities. This
builder carries that accepted evidence forward and may add current-campus drafts
only for institution identities already present in the current D2.2 reviewed
identity artifact. Each campus requires checked-in first-party evidence.

A reviewed current location is not proof of complete campus topology. The builder
therefore preserves campus_structure_complete=false and never infers additional
campuses, writes canonical/runtime data, or creates a public projection.
"""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_IDENTITIES_DIR = Path("artifacts/international/discovery-identity-review")
DEFAULT_BASE_CAMPUS_DIR = Path("artifacts/international/reviewed-campus-draft")
DEFAULT_OUTPUT_DIR = Path("artifacts/international/incremental-campus-review")
DEFAULT_BATCH_GLOB = "campus-review-decisions-*-batch*.json"
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


def discover_batches() -> list[Path]:
    return sorted((HERE / "seeds").glob(DEFAULT_BATCH_GLOB))


def build(identities_dir: Path, base_campus_dir: Path, output_dir: Path, batch_paths: list[Path]) -> dict:
    if not batch_paths:
        raise AssertionError("at least one incremental campus review batch is required")

    identity_summary = load_json(identities_dir / "discovery-identity-summary.json")
    institutions = load_jsonl(identities_dir / "reviewed-institution-drafts.jsonl")
    base_summary = load_json(base_campus_dir / "reviewed-campus-draft-summary.json")
    campuses = load_jsonl(base_campus_dir / "reviewed-current-campus-drafts.jsonl")
    structures = load_jsonl(base_campus_dir / "campus-structure-review.jsonl")

    if identity_summary.get("reviewed_institution_drafts") != len(institutions) or len(institutions) != 26:
        raise AssertionError("incremental campus review requires the accepted 26-institution D2.2 identity artifact")
    if base_summary.get("reviewed_current_campus_records") != len(campuses) or len(campuses) != 9:
        raise AssertionError("incremental campus review requires the accepted 9-campus base artifact")
    if len(structures) != 9:
        raise AssertionError("accepted base campus structure review must contain 9 records")

    institution_by_key = {row["review_identity_key"]: row for row in institutions}
    if len(institution_by_key) != len(institutions):
        raise AssertionError("duplicate review_identity_key in current institution drafts")

    reviewed_identity_keys = {
        row.get("review_identity_key") or row.get("review_group_id") for row in structures
    }
    if None in reviewed_identity_keys or len(reviewed_identity_keys) != len(structures):
        raise AssertionError("base campus structure review contains duplicate or missing identity keys")

    campus_ids = {row["draft_campus_id"] for row in campuses}
    if len(campus_ids) != len(campuses):
        raise AssertionError("duplicate campus IDs in accepted base campus artifact")

    applied_batches: list[dict] = []
    new_campuses: list[dict] = []
    seen_batch_ids: set[str] = set()

    for batch_path in batch_paths:
        batch = load_json(batch_path)
        records = batch.get("records") or []
        if batch.get("records_count") != len(records):
            raise AssertionError(f"records_count mismatch in {batch_path.name}")
        batch_id = str(batch.get("batch_id") or batch_path.stem)
        if batch_id in seen_batch_ids:
            raise AssertionError(f"duplicate incremental campus batch_id: {batch_id}")
        seen_batch_ids.add(batch_id)
        safety = batch.get("safety") or {}
        if safety.get("campus_structure_complete_records") != 0:
            raise AssertionError(f"{batch_path.name} must not declare complete campus structures")
        if safety.get("automatic_additional_campus_inference_performed") is not False:
            raise AssertionError(f"{batch_path.name} must reject automatic additional-campus inference")
        if safety.get("canonical_database_rows_written") != 0:
            raise AssertionError(f"{batch_path.name} must perform zero canonical writes")
        if safety.get("runtime_database_mutation_performed") is not False:
            raise AssertionError(f"{batch_path.name} must perform zero runtime mutation")
        if safety.get("public_projection_rows_created") != 0:
            raise AssertionError(f"{batch_path.name} must perform zero public projection")

        for record in records:
            key = record["review_identity_key"]
            institution = institution_by_key.get(key)
            if institution is None:
                raise AssertionError(f"campus review references unknown reviewed institution: {key}")
            if key in reviewed_identity_keys:
                raise AssertionError(
                    f"identity already has accepted current-campus evidence; explicit multi-campus review required: {key}"
                )
            if record.get("campus_structure_complete") is not False:
                raise AssertionError(f"incremental current-campus evidence cannot declare structure complete: {key}")
            if record.get("lifecycle_status") != "active":
                raise AssertionError(f"incremental campus package currently supports active campuses only: {key}")
            if not record.get("address_en"):
                raise AssertionError(f"current-campus review requires a source-backed location: {key}")
            source_urls = list(record.get("source_urls") or [])
            if not source_urls:
                raise AssertionError(f"current-campus review requires first-party source URLs: {key}")

            campus_key = record["campus_key"]
            campus_id = stable_uuid("campus", f"{key}:{campus_key}")
            if campus_id in campus_ids:
                raise AssertionError(f"duplicate deterministic campus ID: {key}:{campus_key}")
            campus_ids.add(campus_id)
            institution_id = institution["draft_institution_id"]

            campus_row = {
                "draft_campus_id": campus_id,
                "draft_institution_id": institution_id,
                "review_identity_key": key,
                "institution_name_en": institution["canonical_name_en"],
                "review_batch_id": batch_id,
                "campus_key": campus_key,
                "campus_type": record["campus_type"],
                "lifecycle_status": record["lifecycle_status"],
                "source_named_campus_name_en": record.get("source_named_campus_name_en"),
                "address_en": record["address_en"],
                "source_urls": source_urls,
                "evidence_note": record["evidence_note"],
                "current_campus_evidence_reviewed": True,
                "campus_structure_complete": False,
                "additional_current_campuses_ruled_out": False,
                "canonical_campus_created": False,
                "canonical_database_write_performed": False,
                "public_projection_performed": False,
            }
            campuses.append(campus_row)
            new_campuses.append(campus_row)
            structures.append({
                "draft_institution_id": institution_id,
                "review_identity_key": key,
                "institution_name_en": institution["canonical_name_en"],
                "review_batch_id": batch_id,
                "campus_structure_state": "at_least_one_current_campus_reviewed_structure_not_exhaustive",
                "reviewed_current_campus_ids": [campus_id],
                "reviewed_current_campus_count": 1,
                "campus_structure_complete": False,
                "additional_current_campuses_ruled_out": False,
                "further_campus_review_required": True,
                "canonical_database_write_performed": False,
                "public_projection_performed": False,
            })
            reviewed_identity_keys.add(key)

        applied_batches.append({
            "batch_id": batch_id,
            "path": batch_path.name,
            "records_count": len(records),
        })

    pending_keys = sorted(set(institution_by_key) - reviewed_identity_keys)
    pending = [
        {
            "draft_institution_id": institution_by_key[key]["draft_institution_id"],
            "review_identity_key": key,
            "institution_name_en": institution_by_key[key]["canonical_name_en"],
            "campus_review_state": "requires_current_campus_review",
            "campus_structure_complete": False,
            "automatic_campus_inference_performed": False,
        }
        for key in pending_keys
    ]

    campuses.sort(key=lambda row: (row.get("review_identity_key") or row.get("review_group_id"), row["campus_key"]))
    structures.sort(key=lambda row: row.get("review_identity_key") or row.get("review_group_id"))
    new_campuses.sort(key=lambda row: row["review_identity_key"])

    output_dir.mkdir(parents=True, exist_ok=True)
    campuses_path = output_dir / "reviewed-current-campus-drafts.jsonl"
    structures_path = output_dir / "campus-structure-review.jsonl"
    new_path = output_dir / "incremental-current-campus-drafts.jsonl"
    pending_path = output_dir / "campus-review-queue.jsonl"
    write_jsonl(campuses_path, campuses)
    write_jsonl(structures_path, structures)
    write_jsonl(new_path, new_campuses)
    write_jsonl(pending_path, pending)

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.2_incremental_current_campus_materialization",
        "deterministic_id_namespace": str(DRAFT_NAMESPACE),
        "reviewed_institution_drafts": len(institutions),
        "base_current_campus_records": 9,
        "incremental_review_batches": len(applied_batches),
        "incremental_review_batch_details": applied_batches,
        "new_current_campus_records": len(new_campuses),
        "reviewed_current_campus_records": len(campuses),
        "institutions_with_current_campus_evidence": len(reviewed_identity_keys),
        "institutions_pending_current_campus_review": len(pending),
        "campus_structure_complete_records": 0,
        "additional_current_campuses_ruled_out_records": 0,
        "automatic_additional_campus_inference_performed": False,
        "canonical_campus_rows_created": 0,
        "canonical_database_rows_written": 0,
        "runtime_database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "current_campus_drafts": campuses_path.name,
            "campus_structure_review": structures_path.name,
            "incremental_current_campus_drafts": new_path.name,
            "campus_review_queue": pending_path.name,
        },
    }
    (output_dir / "incremental-campus-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--identities-dir", type=Path, default=DEFAULT_IDENTITIES_DIR)
    parser.add_argument("--base-campus-dir", type=Path, default=DEFAULT_BASE_CAMPUS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--batch", dest="batches", action="append", type=Path)
    args = parser.parse_args()
    batch_paths = args.batches if args.batches else discover_batches()
    build(args.identities_dir, args.base_campus_dir, args.output_dir, batch_paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
