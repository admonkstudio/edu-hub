#!/usr/bin/env python3
"""Apply the second 2026-09-15 IB detail batch to the accepted 96-row base.

This is an additive deterministic overlay over build_authoritative_seed.py. It
updates only the five exact IB source rows named in the checked-in batch2
snapshot, preserves every source_record_id, and performs no identity merge,
canonical database mutation or public promotion.

The overlay exists so new source evidence can be accepted independently from a
larger refactor of the historical seed builder. It can later be folded into that
builder without changing source identities.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_BATCH = HERE / "seeds" / "ib-detail-evidence-2026-09-15-batch2.json"
DEFAULT_BASE = Path("artifacts/international/authoritative-source-candidates.jsonl")
DEFAULT_OUTPUT_DIR = Path("artifacts/international/ib-batch2")
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


def apply(base_path: Path, batch_path: Path, output_dir: Path) -> dict:
    rows = load_jsonl(base_path)
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    records = batch["records"]

    assert len(rows) == 96, f"unexpected accepted base size: {len(rows)}"
    assert batch["source_id"] == SOURCE_ID
    assert batch["records_count"] == len(records) == 5
    assert batch["eligible_private"] == 5
    assert batch["excluded_state"] == 0
    assert batch["integration_state"] == "captured_pending_deterministic_seed_integration"
    assert all(row["type"] == "PRIVATE" for row in records)
    assert all(row["scope_state"] == "eligible" for row in records)

    base_ids = [row["source_record_id"] for row in rows]
    if len(base_ids) != len(set(base_ids)):
        raise AssertionError("accepted base contains duplicate source_record_id values")

    ib_by_name = {
        row["name_en"].casefold(): row
        for row in rows
        if row.get("source_id") == SOURCE_ID and row.get("name_en")
    }
    batch_names = [row["name"].casefold() for row in records]
    if len(batch_names) != len(set(batch_names)):
        raise AssertionError("batch2 contains duplicate IB school names")

    missing = sorted(name for name in batch_names if name not in ib_by_name)
    if missing:
        raise AssertionError(f"batch2 schools missing from accepted IB directory base: {missing}")

    before = count_states(rows)
    applied: list[dict] = []
    batch_by_name = {row["name"].casefold(): row for row in records}
    upgraded: list[dict] = []

    for original in rows:
        row = dict(original)
        if row.get("source_id") == SOURCE_ID and row.get("name_en", "").casefold() in batch_by_name:
            detail = batch_by_name[row["name_en"].casefold()]
            if row.get("scope_state") != "candidate":
                raise AssertionError(
                    f"batch2 expected unresolved candidate before upgrade: {row['name_en']}={row.get('scope_state')}"
                )
            old_source_record_id = row["source_record_id"]
            row.update(
                {
                    "source_url": detail["source_url"],
                    "detail_source_url": detail["source_url"],
                    "detail_source_snapshot_date": batch["snapshot_date"],
                    "ib_school_code": detail["ib_school_code"],
                    "ib_school_type": detail["type"],
                    "scope_state": detail["scope_state"],
                    "ownership_scope": "private_independent",
                    "website": detail.get("website"),
                    "phone": detail.get("phone"),
                    "address": detail.get("address"),
                    "detail_enrichment_pending": False,
                    "eligibility_pending": None,
                    "strong_evidence": "ib_world_school_private_detail",
                }
            )
            if row["source_record_id"] != old_source_record_id:
                raise AssertionError("IB batch2 changed a source_record_id")
            applied.append(
                {
                    "name_en": row["name_en"],
                    "source_record_id": row["source_record_id"],
                    "ib_school_code": row["ib_school_code"],
                    "previous_scope_state": original.get("scope_state"),
                    "new_scope_state": row["scope_state"],
                    "detail_source_url": row["detail_source_url"],
                }
            )
        upgraded.append(row)

    assert len(applied) == 5
    assert len(upgraded) == len(rows) == 96
    assert [row["source_record_id"] for row in upgraded] == base_ids

    after = count_states(upgraded)
    assert before == {"candidate": 53, "eligible": 40, "excluded": 3}
    assert after == {"candidate": 48, "eligible": 45, "excluded": 3}

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "authoritative-source-candidates-with-ib-batch2.jsonl"
    applied_path = output_dir / "ib-batch2-applied.jsonl"
    write_jsonl(output_path, upgraded)
    write_jsonl(applied_path, applied)

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_ib_detail_batch2_integration",
        "base_source_rows": len(rows),
        "batch_source_rows": len(records),
        "applied_rows": len(applied),
        "source_record_ids_changed": 0,
        "before_scope_states": before,
        "after_scope_states": after,
        "accepted_ib_detail_rows_after_overlay": 17,
        "unique_institutions_claimed": None,
        "identity_merges_performed": 0,
        "canonical_institutions_created": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "upgraded_base": output_path.name,
            "applied_rows": applied_path.name,
        },
    }
    (output_dir / "ib-batch2-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--batch", type=Path, default=DEFAULT_BATCH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    apply(args.base, args.batch, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
