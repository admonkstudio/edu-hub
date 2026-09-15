#!/usr/bin/env python3
"""Reconcile current SCU foreign-branch evidence with the MOHESR branch listing.

This D2.1 package preserves both regulator source rows. A MOHESR listing is not
silently promoted when current SCU membership or institution-primary lifecycle
evidence conflicts with it. The output is research/review material only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED_DIR = HERE / "seeds"

SCU_PARENT_KEYS = {
    "Coventry University": "coventry",
    "University of Prince Edward Island": "upei",
    "University of Hertfordshire": "hertfordshire",
    "NOVA University Lisbon": "nova",
    "University of London": "university_of_london",
    "University of East London": "uel",
    "University of Central Lancashire": "uclan",
    "Kazan Federal University": "kazan",
    "Saint Petersburg State University": "saint_petersburg",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_id(source_id: str, source_key: str) -> str:
    digest = hashlib.sha256(f"{source_id}\0{source_key}".encode("utf-8")).hexdigest()[:20]
    return f"{source_id}:{digest}"


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def build(seed_dir: Path, output_dir: Path) -> dict:
    scu = load_json(seed_dir / "scu-foreign-university-branches-2026-09-14.json")
    mohesr = load_json(seed_dir / "mohesr-foreign-university-branches-2026-09-15.json")

    assert scu["records_count"] == len(scu["records"])
    assert mohesr["records_count"] == len(mohesr["records"])

    scu_by_key: dict[str, dict] = {}
    for row in scu["records"]:
        key = SCU_PARENT_KEYS[row["parent_university_en"]]
        if key in scu_by_key:
            raise ValueError(f"duplicate SCU reconciliation key: {key}")
        scu_by_key[key] = row

    mohesr_by_key = {row["source_key"]: row for row in mohesr["records"]}
    if len(mohesr_by_key) != len(mohesr["records"]):
        raise ValueError("duplicate MOHESR source_key")

    missing_from_mohesr = sorted(set(scu_by_key) - set(mohesr_by_key))
    mohesr_only = sorted(set(mohesr_by_key) - set(scu_by_key))

    source_rows: list[dict] = []
    reconciliation_rows: list[dict] = []
    for source in mohesr["records"]:
        key = source["source_key"]
        scu_row = scu_by_key.get(key)
        is_current_scu = scu_row is not None
        is_lifecycle_conflict = bool(source.get("lifecycle_review_required")) or not is_current_scu

        source_rows.append(
            {
                "source_id": mohesr["source_id"],
                "source_record_id": stable_id(mohesr["source_id"], key),
                "source_snapshot_date": mohesr["snapshot_date"],
                "source_url": mohesr["source_url"],
                "entity_family": "higher_education",
                "institution_type": "foreign_university_branch_candidate",
                "name_ar": source["name_ar"],
                "parent_university_en": source.get("parent_university_en") or source.get("current_parent_university_en"),
                "parent_university_en_at_source": source.get("parent_university_en_at_source"),
                "country_code": source["country_code"],
                "operator_heading_ar": source["operator_heading_ar"],
                "source_listing_state": source["source_listing_state"],
                "scope_state": "eligible" if is_current_scu else "needs_review",
                "scope_class": "foreign_university_branch" if is_current_scu else "foreign_university_branch_lifecycle_review",
                "current_scu_corroboration": is_current_scu,
                "lifecycle_review_required": is_lifecycle_conflict,
                "eligibility_basis": "current_scu_foreign_branch" if is_current_scu else None,
                "mohesr_listing_auto_eligibility": False,
                "canonical_identity_created": False,
                "automatic_merge_performed": False,
                "database_mutation_performed": False,
                "public_promotion_performed": False,
            }
        )

        reconciliation_rows.append(
            {
                "reconciliation_key": key,
                "mohesr_name_ar": source["name_ar"],
                "mohesr_source_record_id": stable_id(mohesr["source_id"], key),
                "scu_name_ar": scu_row["name_ar"] if scu_row else None,
                "scu_parent_university_en": scu_row["parent_university_en"] if scu_row else None,
                "relationship": "same_current_branch_source_membership" if is_current_scu else "mohesr_only_lifecycle_conflict",
                "current_branch_confirmed": is_current_scu,
                "lifecycle_review_required": is_lifecycle_conflict,
                "conflict_sources": source.get("conflict_sources", []),
                "automatic_identity_merge_performed": False,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    source_path = output_dir / "mohesr-branch-source-candidates.jsonl"
    reconciliation_path = output_dir / "scu-mohesr-branch-reconciliation.jsonl"
    write_jsonl(source_path, source_rows)
    write_jsonl(reconciliation_path, reconciliation_rows)

    matched = sum(1 for row in reconciliation_rows if row["current_branch_confirmed"])
    conflicts = sum(1 for row in reconciliation_rows if row["lifecycle_review_required"])
    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_higher_ed_branch_source_reconciliation",
        "scu_snapshot_date": scu["snapshot_date"],
        "scu_current_branch_rows": len(scu["records"]),
        "mohesr_snapshot_date": mohesr["snapshot_date"],
        "mohesr_listing_rows": len(mohesr["records"]),
        "matched_current_branch_rows": matched,
        "scu_rows_missing_from_mohesr": len(missing_from_mohesr),
        "scu_keys_missing_from_mohesr": missing_from_mohesr,
        "mohesr_only_rows": len(mohesr_only),
        "mohesr_only_keys": mohesr_only,
        "lifecycle_conflict_rows": conflicts,
        "current_active_branches_added_by_mohesr_only": 0,
        "mohesr_listing_auto_eligibility": False,
        "unique_institutions_claimed": None,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "mohesr_source_candidates": source_path.name,
            "reconciliation": reconciliation_path.name,
        },
    }
    (output_dir / "higher-ed-branch-reconciliation-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-dir", type=Path, default=SEED_DIR)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/international/higher-ed-branch-reconciliation"),
    )
    args = parser.parse_args()
    build(args.seed_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
