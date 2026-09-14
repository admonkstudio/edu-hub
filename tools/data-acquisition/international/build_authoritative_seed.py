#!/usr/bin/env python3
"""Build a deterministic EDU-DATA-2 authoritative candidate artifact.

This builder intentionally consumes checked-in, source-dated evidence snapshots.
Several authoritative sites (notably IB) block GitHub-hosted direct HTTP clients,
so CI must validate the evidence we captured through a browser-capable path rather
than pretending a 403 means the source is unavailable.

The output remains source-shaped evidence/candidates; it performs no canonical
merge, database mutation or public promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SEED_DIR = HERE / "seeds"


def stable_id(source_id: str, identity: str) -> str:
    digest = hashlib.sha256(f"{source_id}\0{identity}".encode("utf-8")).hexdigest()[:20]
    return f"{source_id}:{digest}"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_space(value: object) -> str:
    return " ".join(str(value or "").split())


def ib_records(data: dict) -> list[dict]:
    source_id = data["source_id"]
    snapshot_date = data["snapshot_date"]
    source_url = data["source_urls"][0]
    out = []
    for school in data["schools"]:
        name = normalize_space(school["name"])
        out.append(
            {
                "source_id": source_id,
                "source_record_id": stable_id(source_id, name),
                "source_snapshot_date": snapshot_date,
                "source_url": source_url,
                "entity_family": "pre_university",
                "institution_type": "international_school",
                "name_en": name,
                "scope_state": "candidate",
                "scope_class": "international_school",
                "strong_evidence": "ib_world_school_directory",
                "eligibility_pending": "private_or_independent_type_detail_check",
                "curriculum_codes": ["ib"],
                "programmes": {
                    key: bool(school.get(key))
                    for key in ("pyp", "myp", "dp", "cp")
                },
                "languages": list(school.get("languages") or []),
                "detail_enrichment_pending": True,
                "source_count_conflict": bool(data.get("count_conflict_requires_review")),
            }
        )
    return out


def french_records(data: dict) -> list[dict]:
    source_id = data["source_id"]
    out = []
    for row in data["records"]:
        out.append(
            {
                "source_id": source_id,
                "source_record_id": row["uai"],
                "source_snapshot_date": data["snapshot_date"],
                "source_url": data["source_url"],
                "entity_family": "pre_university",
                "institution_type": "international_school",
                "name_en": row["name"],
                "city": row["city"],
                "official_identifier": row["uai"],
                "scope_state": "eligible",
                "scope_class": "international_school",
                "strong_evidence": "french_ministry_homologation",
                "curriculum_codes": ["french"],
                "education_levels": row["levels"],
                "homologated_classes": row["homologated_classes"],
                "source_limitation": row.get("remark"),
            }
        )
    return out


def german_records(data: dict) -> list[dict]:
    source_id = data["source_id"]
    out = []
    for row in data["records"]:
        out.append(
            {
                "source_id": source_id,
                "source_record_id": stable_id(source_id, row["name"]),
                "source_snapshot_date": data["snapshot_date"],
                "source_url": data["source_url"],
                "entity_family": "pre_university",
                "institution_type": "international_school",
                "name_en": row["name"],
                "city": row["city"],
                "scope_state": row["scope_state"],
                "scope_class": row["scope_class"],
                "strong_evidence": "kmk_recognized_german_school_abroad",
                "curriculum_codes": ["german"],
                "recognition_decision_date": row["recognition_decision_date"],
            }
        )
    return out


def scu_records(data: dict) -> list[dict]:
    source_id = data["source_id"]
    out = []
    for row in data["records"]:
        out.append(
            {
                "source_id": source_id,
                "source_record_id": stable_id(source_id, row["name_ar"]),
                "source_snapshot_date": data["snapshot_date"],
                "source_url": data["source_url"],
                "entity_family": "higher_education",
                "institution_type": "foreign_university_branch",
                "name_ar": row["name_ar"],
                "parent_university_en": row["parent_university_en"],
                "parent_country_code": row["country_code"],
                "scope_state": row["scope_state"],
                "scope_class": row["scope_class"],
                "strong_evidence": "scu_recognized_foreign_university_branch",
            }
        )
    return out


def validate_inputs(ib: dict, french: dict, german: dict, scu: dict) -> None:
    assert ib["directory_count_observed"] == len(ib["schools"]) == 54
    assert french["records_count"] == len(french["records"]) == 17
    assert german["records_count"] == len(german["records"]) == 4
    assert scu["records_count"] == len(scu["records"]) == 9

    ib_names = [normalize_space(row["name"]).casefold() for row in ib["schools"]]
    assert len(ib_names) == len(set(ib_names)), "duplicate IB directory rows"
    uais = [row["uai"] for row in french["records"]]
    assert len(uais) == len(set(uais)), "duplicate French UAI"
    german_names = [normalize_space(row["name"]).casefold() for row in german["records"]]
    assert len(german_names) == len(set(german_names)), "duplicate German seed rows"


def build(seed_dir: Path, output_dir: Path) -> dict:
    ib = load_json(seed_dir / "ib-egypt-directory-2026-09-14.json")
    french = load_json(seed_dir / "french-homologation-egypt-2026-2027.json")
    german = load_json(seed_dir / "german-kmk-egypt-2026-04.json")
    scu = load_json(seed_dir / "scu-foreign-university-branches-2026-09-14.json")
    validate_inputs(ib, french, german, scu)

    rows = ib_records(ib) + french_records(french) + german_records(german) + scu_records(scu)
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "authoritative-source-candidates.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    source_counts: dict[str, int] = {}
    for row in rows:
        source_counts[row["source_id"]] = source_counts.get(row["source_id"], 0) + 1

    # This is a source-row count, NOT a unique-institution count. Cross-source
    # duplicates (e.g. IB + French/German recognition) are intentionally retained
    # until staging identity reconciliation.
    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source_rows": len(rows),
        "source_counts": source_counts,
        "eligible_source_rows": sum(1 for row in rows if row["scope_state"] == "eligible"),
        "candidate_source_rows": sum(1 for row in rows if row["scope_state"] == "candidate"),
        "unique_institutions_claimed": None,
        "identity_reconciliation_required": True,
        "ib_directory_country_summary_conflict": {
            "directory": ib["directory_count_observed"],
            "country_summary": ib["country_summary_count_observed"],
            "review_required": ib["count_conflict_requires_review"],
        },
        "database_mutation_performed": False,
        "public_promotion_performed": False,
        "output": jsonl_path.name,
    }
    (output_dir / "authoritative-source-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-dir", type=Path, default=DEFAULT_SEED_DIR)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/international"))
    args = parser.parse_args()
    build(args.seed_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
