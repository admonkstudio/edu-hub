#!/usr/bin/env python3
"""Compare full British Council PDF extraction with accepted browser-review rows.

This is a D2.1 coverage audit only. Full-PDF rows missing from the historical
browser-reviewed 210-row set are emitted as supporting discovery gaps, not as
canonical institutions or automatically eligible schools.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def name_key(row: dict) -> str:
    return normalize(row.get("name_en"))


def build(full_path: Path, reviewed_path: Path, output_dir: Path) -> dict:
    full_rows = load_jsonl(full_path)
    reviewed_rows = load_jsonl(reviewed_path)
    if not full_rows:
        raise AssertionError("full British Council extraction is empty")
    if not reviewed_rows:
        raise AssertionError("reviewed British Council discovery is empty")

    full_by_name: dict[str, list[dict]] = {}
    for row in full_rows:
        key = name_key(row)
        if not key:
            raise AssertionError("full extraction row missing name")
        full_by_name.setdefault(key, []).append(row)

    reviewed_by_name: dict[str, list[dict]] = {}
    for row in reviewed_rows:
        key = name_key(row)
        if not key:
            raise AssertionError("reviewed row missing name")
        reviewed_by_name.setdefault(key, []).append(row)

    full_names = set(full_by_name)
    reviewed_names = set(reviewed_by_name)
    matched_names = full_names & reviewed_names
    missing_names = full_names - reviewed_names
    reviewed_not_found_names = reviewed_names - full_names

    gaps: list[dict] = []
    for key in sorted(missing_names):
        for row in full_by_name[key]:
            gaps.append({
                **row,
                "coverage_state": "full_pdf_row_missing_from_reviewed_browser_set",
                "lead_state": "supporting_candidate",
                "eligibility_pending": "requires_primary_or_authoritative_international_school_evidence_and_private_independent_check",
                "auto_eligibility": False,
                "canonical_identity_created": False,
                "automatic_merge_performed": False,
                "database_mutation_performed": False,
                "public_promotion_performed": False,
            })

    reviewed_not_found: list[dict] = []
    for key in sorted(reviewed_not_found_names):
        for row in reviewed_by_name[key]:
            reviewed_not_found.append({
                "source_record_id": row.get("source_record_id"),
                "name_en": row.get("name_en"),
                "source_page_zero_based": row.get("source_page_zero_based"),
                "city": row.get("city"),
                "coverage_state": "reviewed_name_not_exactly_reproduced_by_full_pdf_parser",
                "requires_parser_or_name_review": True,
            })

    duplicate_full_names = {
        key: [row.get("source_record_id") for row in rows]
        for key, rows in full_by_name.items()
        if len(rows) > 1
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    gap_path = output_dir / "full-pdf-unreviewed-supporting-leads.jsonl"
    with gap_path.open("w", encoding="utf-8") as handle:
        for row in gaps:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    mismatch_path = output_dir / "reviewed-names-not-found-exactly.jsonl"
    with mismatch_path.open("w", encoding="utf-8") as handle:
        for row in reviewed_not_found:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_british_council_full_pdf_coverage_audit",
        "full_pdf_extracted_rows": len(full_rows),
        "full_pdf_normalized_names": len(full_names),
        "reviewed_browser_rows": len(reviewed_rows),
        "reviewed_browser_normalized_names": len(reviewed_names),
        "exact_normalized_name_matches": len(matched_names),
        "full_pdf_normalized_names_missing_from_reviewed_set": len(missing_names),
        "full_pdf_gap_rows": len(gaps),
        "reviewed_normalized_names_not_found_by_full_parser": len(reviewed_not_found_names),
        "reviewed_rows_not_found_by_full_parser": len(reviewed_not_found),
        "full_parser_duplicate_normalized_name_groups": len(duplicate_full_names),
        "full_parser_duplicate_normalized_name_details": duplicate_full_names,
        "full_pdf_extraction_complete_claimed": False,
        "coverage_audit_complete": True,
        "gaps_auto_added_to_accepted_universe": False,
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "unreviewed_supporting_leads": gap_path.name,
            "reviewed_names_not_found_exactly": mismatch_path.name,
        },
    }
    (output_dir / "british-council-full-pdf-coverage-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        type=Path,
        default=Path("artifacts/international/british-council-full-pdf/extracted/british-council-partner-schools.jsonl"),
    )
    parser.add_argument(
        "--reviewed",
        type=Path,
        default=Path("artifacts/international/british-council-browser-discovery/british-council-browser-leads.jsonl"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/international/british-council-full-pdf/coverage"),
    )
    args = parser.parse_args()
    build(args.full, args.reviewed, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
