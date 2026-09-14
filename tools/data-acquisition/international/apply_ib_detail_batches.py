#!/usr/bin/env python3
"""Apply all accepted incremental IB detail batches to the foundational source build.

The foundational 96-row build remains independently reproducible. This overlay
loads checked-in ``ib-detail-evidence-*-batch*.json`` snapshots in deterministic
filename order, updates only exact existing IB directory identities, preserves
all source_record_id values and list ordering, and emits an upgraded research
universe without any identity merge, runtime database write or public promotion.

A source identity may appear in at most one incremental batch. New batches are
therefore auditable, additive review units instead of silent rewrites.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SEED_DIR = HERE / "seeds"
DEFAULT_BASE = Path("artifacts/international/authoritative-source-candidates.jsonl")
DEFAULT_OUTPUT_DIR = Path("artifacts/international/ib-incremental")
SOURCE_ID = "ib_world_schools_egypt"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def count_states(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        state = row.get("scope_state") or "unknown"
        counts[state] = counts.get(state, 0) + 1
    return counts


def default_batch_paths(seed_dir: Path) -> list[Path]:
    return sorted(seed_dir.glob("ib-detail-evidence-*-batch*.json"), key=lambda path: path.name)


def apply(base_path: Path, batch_paths: list[Path], output_dir: Path) -> dict:
    rows = load_jsonl(base_path)
    if len(rows) != 96:
        raise AssertionError(f"unexpected foundational source row count: {len(rows)}")
    if not batch_paths:
        raise AssertionError("no incremental IB detail batches supplied")

    source_ids_before = [row["source_record_id"] for row in rows]
    if len(source_ids_before) != len(set(source_ids_before)):
        raise AssertionError("foundational source build contains duplicate source_record_id values")

    ib_names = {
        row["name_en"].casefold(): row
        for row in rows
        if row.get("source_id") == SOURCE_ID and row.get("name_en")
    }
    if len(ib_names) != 54:
        raise AssertionError(f"expected 54 IB directory source identities, found {len(ib_names)}")

    records_by_name: dict[str, tuple[dict, dict, Path]] = {}
    batch_summaries: list[dict] = []
    for batch_path in batch_paths:
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
        if batch["source_id"] != SOURCE_ID:
            raise AssertionError(f"wrong source_id in {batch_path.name}: {batch['source_id']}")
        records = batch.get("records") or []
        if batch["records_count"] != len(records):
            raise AssertionError(f"records_count mismatch in {batch_path.name}")
        if not records:
            raise AssertionError(f"empty IB detail batch: {batch_path.name}")
        if batch.get("integration_state") != "captured_pending_deterministic_seed_integration":
            raise AssertionError(f"unexpected integration_state in {batch_path.name}")
        if any(row.get("type") != "PRIVATE" or row.get("scope_state") != "eligible" for row in records):
            raise AssertionError(f"incremental batch is not exclusively reviewed PRIVATE/eligible evidence: {batch_path.name}")

        for detail in records:
            normalized = detail["name"].casefold()
            if normalized in records_by_name:
                other = records_by_name[normalized][2].name
                raise AssertionError(
                    f"IB identity appears in multiple incremental batches: {detail['name']} ({other}, {batch_path.name})"
                )
            if normalized not in ib_names:
                raise AssertionError(
                    f"incremental IB identity missing from foundational directory: {detail['name']}"
                )
            records_by_name[normalized] = (detail, batch, batch_path)

        batch_summaries.append(
            {
                "file": batch_path.name,
                "snapshot_date": batch["snapshot_date"],
                "records": len(records),
                "eligible_private": batch.get("eligible_private"),
                "excluded_state": batch.get("excluded_state"),
            }
        )

    before = count_states(rows)
    if before != {"candidate": 53, "eligible": 40, "excluded": 3}:
        raise AssertionError(f"foundational scope-state contract drifted: {before}")

    upgraded: list[dict] = []
    applied_rows: list[dict] = []
    for original in rows:
        row = dict(original)
        normalized = row.get("name_en", "").casefold()
        match = records_by_name.get(normalized) if row.get("source_id") == SOURCE_ID else None
        if match:
            detail, batch, batch_path = match
            if row.get("scope_state") != "candidate":
                raise AssertionError(
                    f"incremental overlay may only upgrade unresolved candidate rows: {row.get('name_en')}={row.get('scope_state')}"
                )
            source_record_id = row["source_record_id"]
            row.update(
                {
                    "source_url": detail["source_url"],
                    "detail_source_url": detail["source_url"],
                    "detail_source_snapshot_date": batch["snapshot_date"],
                    "ib_school_code": detail["ib_school_code"],
                    "ib_school_type": detail["type"],
                    "scope_state": "eligible",
                    "ownership_scope": "private_independent",
                    "website": detail.get("website"),
                    "phone": detail.get("phone"),
                    "address": detail.get("address"),
                    "detail_enrichment_pending": False,
                    "eligibility_pending": None,
                    "strong_evidence": "ib_world_school_private_detail",
                }
            )
            if row["source_record_id"] != source_record_id:
                raise AssertionError("incremental overlay changed a source_record_id")
            applied_rows.append(
                {
                    "batch_file": batch_path.name,
                    "name_en": row["name_en"],
                    "source_record_id": source_record_id,
                    "ib_school_code": row["ib_school_code"],
                    "previous_scope_state": original.get("scope_state"),
                    "new_scope_state": row["scope_state"],
                    "detail_source_snapshot_date": row["detail_source_snapshot_date"],
                    "detail_source_url": row["detail_source_url"],
                }
            )
        upgraded.append(row)

    if len(applied_rows) != len(records_by_name):
        raise AssertionError(
            f"not every incremental detail record was applied: records={len(records_by_name)} applied={len(applied_rows)}"
        )
    if [row["source_record_id"] for row in upgraded] != source_ids_before:
        raise AssertionError("incremental overlay changed source identity ordering or identifiers")

    after = count_states(upgraded)
    expected_eligible = before["eligible"] + len(applied_rows)
    expected_candidate = before["candidate"] - len(applied_rows)
    expected_after = {
        "candidate": expected_candidate,
        "eligible": expected_eligible,
        "excluded": before["excluded"],
    }
    if after != expected_after:
        raise AssertionError(f"unexpected post-overlay scope states: expected={expected_after} actual={after}")

    output_dir.mkdir(parents=True, exist_ok=True)
    upgraded_path = output_dir / "authoritative-source-candidates-with-incremental-ib.jsonl"
    applied_path = output_dir / "ib-incremental-applied.jsonl"
    write_jsonl(upgraded_path, upgraded)
    write_jsonl(applied_path, applied_rows)

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_incremental_ib_detail_integration",
        "foundational_source_rows": len(rows),
        "incremental_batch_count": len(batch_paths),
        "incremental_detail_rows": len(records_by_name),
        "applied_rows": len(applied_rows),
        "source_record_ids_changed": 0,
        "before_scope_states": before,
        "after_scope_states": after,
        "accepted_ib_detail_rows_after_overlay": 12 + len(applied_rows),
        "batches": batch_summaries,
        "unique_institutions_claimed": None,
        "identity_merges_performed": 0,
        "canonical_institutions_created": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "upgraded_base": upgraded_path.name,
            "applied_rows": applied_path.name,
        },
    }
    (output_dir / "ib-incremental-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--seed-dir", type=Path, default=DEFAULT_SEED_DIR)
    parser.add_argument("--batch", action="append", type=Path, default=[])
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    batch_paths = args.batch or default_batch_paths(args.seed_dir)
    apply(args.base, batch_paths, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
