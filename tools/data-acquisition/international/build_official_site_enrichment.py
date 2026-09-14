#!/usr/bin/env python3
"""Build the first D2.4 first-party enrichment review package.

Inputs are checked-in facts from institution-controlled websites plus current
regulator/authorizer pages. The package measures which profile fields have been
attempted and evidenced. It does not create canonical identities, overwrite
canonical values, infer missing fees, or publish anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SEED = HERE / "seeds" / "official-site-enrichment-evidence-2026-09-15.json"

FIELD_GROUPS = {
    "website": {"official_website"},
    "location": {"address_en"},
    "contact": {"general_phone", "general_email", "admissions_phone", "admissions_email", "front_desk_phone"},
    "admissions": {"admissions_url", "admissions_2026_2027_note", "admissions_status_source_text", "application_2026_2027_link_present"},
    "curriculum_programmes": {"curriculum_evidence", "programmes_evidence"},
    "education_range": {"education_range", "age_min_years", "age_max_years"},
    "provider": {"provider_group"},
    "facilities": {"facilities_evidence"},
    "founding": {"founded_year"},
    "regulatory_identifiers": {"ib_school_code", "bso_status"},
}


def stable_id(name: str) -> str:
    digest = hashlib.sha256(name.casefold().encode("utf-8")).hexdigest()[:20]
    return f"official-site-enrichment:{digest}"


def has_any(record: dict, keys: set[str]) -> bool:
    facts = record.get("facts") or {}
    if "official_website" in keys and record.get("official_website"):
        return True
    return any(facts.get(key) not in (None, "", [], {}) for key in keys)


def build(seed_path: Path, output_dir: Path) -> dict:
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    records = seed["records"]
    assert seed["records_count"] == len(records) == 8
    assert len({row["name_en"].casefold() for row in records}) == len(records)
    assert all(row.get("official_website") for row in records)
    assert all(row.get("source_urls") for row in records)

    rows = []
    for source in records:
        coverage = {
            group: has_any(source, fields)
            for group, fields in FIELD_GROUPS.items()
        }
        row = {
            "enrichment_evidence_id": stable_id(source["name_en"]),
            "name_en": source["name_en"],
            "official_website": source["official_website"],
            "facts": source.get("facts") or {},
            "source_urls": source["source_urls"],
            "source_snapshot_date": seed["snapshot_date"],
            "coverage": coverage,
            "coverage_groups_present": sum(1 for present in coverage.values() if present),
            "coverage_groups_total": len(FIELD_GROUPS),
            "canonical_identity_created": False,
            "canonical_fields_mutated": False,
            "fees_inferred": False,
            "automatic_merge_performed": False,
            "public_promotion_performed": False,
        }
        rows.append(row)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "official-site-enrichment.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    group_counts = {
        group: sum(1 for row in rows if row["coverage"][group])
        for group in FIELD_GROUPS
    }
    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.4_first_party_profile_enrichment",
        "institution_evidence_records": len(rows),
        "coverage_group_counts": group_counts,
        "website_coverage": group_counts["website"],
        "location_coverage": group_counts["location"],
        "contact_coverage": group_counts["contact"],
        "admissions_coverage": group_counts["admissions"],
        "curriculum_or_programme_coverage": group_counts["curriculum_programmes"],
        "facilities_coverage": group_counts["facilities"],
        "current_fee_schedules_asserted": 0,
        "canonical_institutions_created": 0,
        "canonical_fields_mutated": 0,
        "automatic_merges_performed": 0,
        "public_projection_rows_created": 0,
        "database_mutation_performed": False,
        "output": output_path.name,
    }
    (output_dir / "official-site-enrichment-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/international/official-site-enrichment"),
    )
    args = parser.parse_args()
    build(args.seed, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
