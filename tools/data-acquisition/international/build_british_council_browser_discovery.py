#!/usr/bin/env python3
"""Materialize reviewed browser-captured British Council discovery batches.

The September 2026 British Council Partner Schools PDF is supporting discovery
and contact evidence only. It does not establish international-school eligibility,
ownership, canonical identity, campus identity or division identity.

This builder aggregates dated checked-in browser review batches into one stable
source-lead artifact while enforcing cross-batch source-record/name uniqueness and
the discovery-only safety boundary.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SEED_GLOB = "british-council-browser-discovery-2026-09-15*.json"
DEFAULT_OUTPUT_DIR = Path("artifacts/international/british-council-browser-discovery")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_seeds() -> list[Path]:
    paths = sorted((HERE / "seeds").glob(DEFAULT_SEED_GLOB))
    if not paths:
        raise AssertionError("no British Council browser discovery seeds found")
    return paths


def build(seed_paths: list[Path], output_dir: Path) -> dict:
    if not seed_paths:
        raise AssertionError("at least one British Council discovery seed is required")

    leads: list[dict] = []
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    source_id: str | None = None
    source_url: str | None = None
    snapshot_date: str | None = None
    capture_mode: str | None = None
    batch_summaries: list[dict] = []

    for seed_path in seed_paths:
        seed = load_json(seed_path)
        records = seed.get("records") or []
        if seed.get("records_count") != len(records):
            raise AssertionError(f"records_count mismatch in {seed_path.name}")
        if not records:
            raise AssertionError(f"British Council discovery batch is empty: {seed_path.name}")
        if seed.get("international_eligibility_granted") is not False:
            raise AssertionError("British Council Partner School status must not grant international eligibility")
        safety = seed.get("safety") or {}
        if safety.get("partner_status_treated_as_international_eligibility") is not False:
            raise AssertionError("Partner School status may only be supporting discovery evidence")
        if safety.get("automatic_identity_creation_performed") is not False:
            raise AssertionError("British Council discovery must not auto-create identities")
        if safety.get("automatic_merges_performed") != 0:
            raise AssertionError("British Council discovery must perform zero automatic merges")
        if safety.get("canonical_database_rows_written") != 0:
            raise AssertionError("British Council discovery must perform zero canonical database writes")
        if safety.get("public_projection_rows_created") != 0:
            raise AssertionError("British Council discovery must perform zero public projection")

        current_source_id = seed["source_id"]
        current_source_url = seed["source_url"]
        current_snapshot_date = seed["snapshot_date"]
        current_capture_mode = seed["capture_mode"]
        if source_id is None:
            source_id = current_source_id
            source_url = current_source_url
            snapshot_date = current_snapshot_date
            capture_mode = current_capture_mode
        elif (
            current_source_id != source_id
            or current_source_url != source_url
            or current_snapshot_date != snapshot_date
            or current_capture_mode != capture_mode
        ):
            raise AssertionError(f"British Council discovery source contract drift in {seed_path.name}")

        batch_id = str(seed.get("batch_id") or seed_path.stem)
        batch_websites = 0
        for raw in records:
            if not isinstance(raw, list) or len(raw) != 5:
                raise AssertionError(f"invalid compact British Council discovery row: {raw!r}")
            slug, name, page_zero_based, city, website = raw
            source_record_id = f"bcps2026:{slug}"
            if source_record_id in seen_ids:
                raise AssertionError(f"duplicate British Council source_record_id across batches: {source_record_id}")
            seen_ids.add(source_record_id)
            name_key = " ".join(str(name).split()).casefold()
            if name_key in seen_names:
                raise AssertionError(f"duplicate British Council discovery name across batches: {name}")
            seen_names.add(name_key)
            if not isinstance(page_zero_based, int) or page_zero_based < 2 or page_zero_based > 17:
                raise AssertionError(f"unexpected British Council PDF page index for {name}: {page_zero_based}")
            if website:
                batch_websites += 1

            leads.append({
                "source_id": source_id,
                "source_record_id": source_record_id,
                "source_url": source_url,
                "source_snapshot_date": snapshot_date,
                "source_page_zero_based": page_zero_based,
                "capture_mode": capture_mode,
                "discovery_batch_id": batch_id,
                "entity_family": "pre_university",
                "institution_type": "school_exam_partner_candidate",
                "name_en": name,
                "city": city,
                "website_reference": website,
                "lead_state": "supporting_candidate",
                "storage_policy": "browser_extracted_supporting_discovery_only_re_source_before_eligibility",
                "supporting_evidence": "british_council_partner_school_exam_delivery",
                "eligibility_pending": "requires_primary_or_authoritative_international_school_evidence_and_private_independent_check",
                "auto_eligibility": False,
                "canonical_identity_created": False,
                "automatic_merge_performed": False,
                "public_promotion_performed": False,
            })

        batch_summaries.append({
            "batch_id": batch_id,
            "seed": seed_path.name,
            "rows": len(records),
            "rows_with_website_reference": batch_websites,
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "british-council-browser-leads.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for row in leads:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": 2,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_british_council_browser_discovery",
        "source_id": source_id,
        "source_rows_in_pdf_claimed": None,
        "reviewed_discovery_batches": len(batch_summaries),
        "batch_details": batch_summaries,
        "reviewed_discovery_rows": len(leads),
        "rows_with_website_reference": sum(1 for row in leads if row.get("website_reference")),
        "unique_institutions_claimed": None,
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "full_pdf_extraction_complete": False,
        "output": output_path.name,
    }
    (output_dir / "british-council-browser-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", dest="seeds", action="append", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    seed_paths = args.seeds if args.seeds else discover_seeds()
    build(seed_paths, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
