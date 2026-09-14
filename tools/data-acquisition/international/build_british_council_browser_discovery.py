#!/usr/bin/env python3
"""Materialize a reviewed browser-captured British Council discovery batch.

The September 2026 British Council Partner Schools PDF is supporting discovery
and contact evidence only. It does not establish international-school eligibility,
ownership or canonical identity. This builder converts a checked-in browser review
batch into candidate-universe lead rows while enforcing that boundary.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SEED = HERE / "seeds" / "british-council-browser-discovery-2026-09-15.json"
DEFAULT_OUTPUT_DIR = Path("artifacts/international/british-council-browser-discovery")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build(seed_path: Path, output_dir: Path) -> dict:
    seed = load_json(seed_path)
    records = seed.get("records") or []
    if seed.get("records_count") != len(records) or len(records) != 35:
        raise AssertionError("British Council browser discovery batch must contain 35 reviewed leads")
    if seed.get("international_eligibility_granted") is not False:
        raise AssertionError("British Council Partner School status must not grant international eligibility")
    safety = seed.get("safety") or {}
    if safety.get("partner_status_treated_as_international_eligibility") is not False:
        raise AssertionError("Partner School status may only be supporting discovery evidence")
    if safety.get("automatic_identity_creation_performed") is not False:
        raise AssertionError("British Council discovery must not auto-create identities")
    if safety.get("automatic_merges_performed") != 0:
        raise AssertionError("British Council discovery must perform zero automatic merges")

    source_id = seed["source_id"]
    source_url = seed["source_url"]
    snapshot_date = seed["snapshot_date"]
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    leads: list[dict] = []

    for raw in records:
        if not isinstance(raw, list) or len(raw) != 5:
            raise AssertionError(f"invalid compact British Council discovery row: {raw!r}")
        slug, name, page_zero_based, city, website = raw
        source_record_id = f"bcps2026:{slug}"
        if source_record_id in seen_ids:
            raise AssertionError(f"duplicate British Council source_record_id: {source_record_id}")
        seen_ids.add(source_record_id)
        name_key = " ".join(str(name).split()).casefold()
        if name_key in seen_names:
            raise AssertionError(f"duplicate British Council discovery name in batch: {name}")
        seen_names.add(name_key)
        if not isinstance(page_zero_based, int) or page_zero_based < 2 or page_zero_based > 17:
            raise AssertionError(f"unexpected British Council PDF page index for {name}: {page_zero_based}")

        leads.append({
            "source_id": source_id,
            "source_record_id": source_record_id,
            "source_url": source_url,
            "source_snapshot_date": snapshot_date,
            "source_page_zero_based": page_zero_based,
            "capture_mode": seed["capture_mode"],
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

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "british-council-browser-leads.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for row in leads:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_british_council_browser_discovery",
        "source_id": source_id,
        "source_rows_in_pdf_claimed": None,
        "reviewed_discovery_batch_rows": len(leads),
        "rows_with_website_reference": sum(1 for row in leads if row.get("website_reference")),
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
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    build(args.seed, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
