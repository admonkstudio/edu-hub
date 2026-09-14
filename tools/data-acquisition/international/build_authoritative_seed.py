#!/usr/bin/env python3
"""Build a deterministic EDU-DATA-2 authoritative candidate artifact.

This builder intentionally consumes checked-in, source-dated evidence snapshots.
Several authoritative sites (notably IB) block GitHub-hosted direct HTTP clients,
so CI validates evidence captured through browser-capable/source-appropriate paths
rather than pretending a hosted-runner 403 means the source is unavailable.

The output remains source-shaped evidence/candidates; it performs no canonical
merge, database mutation or public promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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


def ib_records(data: dict, detail_data: dict) -> list[dict]:
    source_id = data["source_id"]
    snapshot_date = data["snapshot_date"]
    directory_source_url = data["source_urls"][0]
    detail_by_name = {
        normalize_space(row["name"]).casefold(): row
        for row in detail_data.get("records", [])
    }
    out = []
    for school in data["schools"]:
        name = normalize_space(school["name"])
        detail = detail_by_name.get(name.casefold())
        row = {
            "source_id": source_id,
            "source_record_id": stable_id(source_id, name),
            "source_snapshot_date": snapshot_date,
            "source_url": directory_source_url,
            "directory_source_url": directory_source_url,
            "entity_family": "pre_university",
            "institution_type": "international_school",
            "name_en": name,
            "scope_state": "candidate",
            "scope_class": "international_school",
            "strong_evidence": "ib_world_school_directory",
            "eligibility_pending": "private_or_independent_type_detail_check",
            "curriculum_codes": ["ib"],
            "programmes": {key: bool(school.get(key)) for key in ("pyp", "myp", "dp", "cp")},
            "languages": list(school.get("languages") or []),
            "detail_enrichment_pending": True,
            "source_count_conflict": bool(data.get("count_conflict_requires_review")),
        }
        if detail:
            row.update(
                {
                    "source_url": detail["source_url"],
                    "detail_source_url": detail["source_url"],
                    "ib_school_code": detail.get("ib_school_code"),
                    "ib_school_type": detail.get("type"),
                    "scope_state": detail["scope_state"],
                    "ownership_scope": (
                        "private_independent" if detail.get("type") == "PRIVATE"
                        else "public" if detail.get("type") == "STATE"
                        else "unknown"
                    ),
                    "website": detail.get("website"),
                    "phone": detail.get("phone"),
                    "address": detail.get("address"),
                    "detail_enrichment_pending": False,
                    "eligibility_pending": None,
                    "strong_evidence": (
                        "ib_world_school_private_detail"
                        if detail["scope_state"] == "eligible"
                        else "ib_world_school_state_detail"
                    ),
                }
            )
        out.append(row)
    return out


def bso_records(data: dict, detail_data: dict) -> list[dict]:
    source_id = data["source_id"]
    detail_by_seed_name = {
        normalize_space(row["seed_name"]).casefold(): row
        for row in detail_data.get("records", [])
    }
    out = []
    for source_row in data["records"]:
        seed_name = normalize_space(source_row["name"])
        detail = detail_by_seed_name.get(seed_name.casefold())
        row = {
            "source_id": source_id,
            "source_record_id": stable_id(source_id, seed_name),
            "source_snapshot_date": data["snapshot_date"],
            "source_url": data["source_url"],
            "entity_family": "pre_university",
            "institution_type": "international_school",
            "name_en": seed_name,
            "list_name_en": seed_name,
            "scope_state": "candidate",
            "scope_class": "international_school",
            "strong_evidence": "uk_dfe_british_school_overseas_accreditation",
            "eligibility_pending": "private_or_independent_ownership_check",
            "curriculum_codes": ["british"],
            "bso_accredited_current": True,
            "bso_list_updated": data["list_updated"],
            "inspection_date": source_row["inspection_date"],
            "detail_enrichment_pending": detail is None,
        }
        if detail:
            row.update(
                {
                    "name_en": detail.get("official_name_en") or seed_name,
                    "official_identifier": detail.get("urn"),
                    "gias_urn": detail.get("urn"),
                    "gias_source_url": detail.get("gias_url"),
                    "address": detail.get("address"),
                    "age_min_years": detail.get("age_min"),
                    "age_max_years": detail.get("age_max"),
                    "gender_model": "coeducational" if detail.get("gender") == "mixed" else detail.get("gender"),
                    "lifecycle_status": detail.get("establishment_status"),
                    "website": detail.get("website"),
                    "phone": detail.get("phone"),
                    "inspectorate": detail.get("inspectorate"),
                    "inspection_date": detail.get("last_inspection_date") or source_row["inspection_date"],
                    "detail_enrichment_pending": False,
                }
            )
        out.append(row)
    return out


def french_records(data: dict) -> list[dict]:
    source_id = data["source_id"]
    return [
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
        for row in data["records"]
    ]


def german_records(data: dict) -> list[dict]:
    source_id = data["source_id"]
    return [
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
        for row in data["records"]
    ]


def scu_records(data: dict) -> list[dict]:
    source_id = data["source_id"]
    return [
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
        for row in data["records"]
    ]


def auc_records(data: dict) -> list[dict]:
    source_id = data["source_id"]
    row = data["institution"]
    return [
        {
            "source_id": source_id,
            "source_record_id": "msche-0637",
            "source_snapshot_date": data["snapshot_date"],
            "source_url": row["international_evidence"][0]["source_url"],
            "entity_family": "higher_education",
            "institution_type": "international_independent_university",
            "name_en": row["name_en"],
            "short_name": row["short_name"],
            "city": row["city"],
            "address": row["address"],
            "phone": row["phone"],
            "website": row["website"],
            "scope_state": row["scope_state"],
            "scope_class": row["scope_class"],
            "ownership_scope": row["ownership_scope"],
            "strong_evidence": "msche_institutional_accreditation_plus_egypt_us_framework",
            "international_evidence": row["international_evidence"],
        }
    ]


def validate_inputs(
    ib: dict,
    ib_detail: dict,
    bso: dict,
    bso_detail: dict,
    french: dict,
    german: dict,
    scu: dict,
    auc: dict,
) -> None:
    assert ib["directory_count_observed"] == len(ib["schools"]) == 54
    assert ib_detail["records_count"] == len(ib_detail["records"]) == 7
    assert ib_detail["eligible_private"] == 4
    assert ib_detail["excluded_state"] == 3
    assert bso["records_count"] == len(bso["records"]) == 11
    assert bso_detail["records_count"] == len(bso_detail["records"]) == 11
    assert french["records_count"] == len(french["records"]) == 17
    assert german["records_count"] == len(german["records"]) == 4
    assert scu["records_count"] == len(scu["records"]) == 9
    assert auc["institution"]["scope_state"] == "eligible"
    assert auc["institution"]["scope_class"] == "international_independent_university"

    ib_names = [normalize_space(row["name"]).casefold() for row in ib["schools"]]
    assert len(ib_names) == len(set(ib_names)), "duplicate IB directory rows"
    detail_names = [normalize_space(row["name"]).casefold() for row in ib_detail["records"]]
    assert len(detail_names) == len(set(detail_names)), "duplicate IB detail rows"
    missing_details = sorted(set(detail_names) - set(ib_names))
    assert not missing_details, f"IB detail rows not present in directory snapshot: {missing_details}"

    bso_names = [normalize_space(row["name"]).casefold() for row in bso["records"]]
    assert len(bso_names) == len(set(bso_names)), "duplicate BSO seed rows"
    assert "cairo english school" not in bso_names, "removed BSO school must not be in current seed"
    bso_detail_names = [normalize_space(row["seed_name"]).casefold() for row in bso_detail["records"]]
    assert len(bso_detail_names) == len(set(bso_detail_names)), "duplicate BSO detail rows"
    assert set(bso_detail_names) == set(bso_names), "BSO list/detail seed mismatch"
    urns = [row["urn"] for row in bso_detail["records"]]
    assert len(urns) == len(set(urns)), "duplicate GIAS URNs"

    uais = [row["uai"] for row in french["records"]]
    assert len(uais) == len(set(uais)), "duplicate French UAI"
    german_names = [normalize_space(row["name"]).casefold() for row in german["records"]]
    assert len(german_names) == len(set(german_names)), "duplicate German seed rows"


def build(seed_dir: Path, output_dir: Path) -> dict:
    ib = load_json(seed_dir / "ib-egypt-directory-2026-09-14.json")
    ib_detail = load_json(seed_dir / "ib-detail-evidence-2026-09-14.json")
    bso = load_json(seed_dir / "uk-dfe-bso-egypt-2026-08-26.json")
    bso_detail = load_json(seed_dir / "uk-dfe-gias-bso-egypt-detail-2026-09-14.json")
    french = load_json(seed_dir / "french-homologation-egypt-2026-2027.json")
    german = load_json(seed_dir / "german-kmk-egypt-2026-04.json")
    scu = load_json(seed_dir / "scu-foreign-university-branches-2026-09-14.json")
    auc = load_json(seed_dir / "auc-international-evidence-2026-09-14.json")
    validate_inputs(ib, ib_detail, bso, bso_detail, french, german, scu, auc)

    rows = (
        ib_records(ib, ib_detail)
        + bso_records(bso, bso_detail)
        + french_records(french)
        + german_records(german)
        + scu_records(scu)
        + auc_records(auc)
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "authoritative-source-candidates.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    source_counts: dict[str, int] = {}
    for row in rows:
        source_counts[row["source_id"]] = source_counts.get(row["source_id"], 0) + 1

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source_rows": len(rows),
        "source_counts": source_counts,
        "eligible_source_rows": sum(1 for row in rows if row["scope_state"] == "eligible"),
        "candidate_source_rows": sum(1 for row in rows if row["scope_state"] == "candidate"),
        "excluded_source_rows": sum(1 for row in rows if row["scope_state"] == "excluded"),
        "ib_detail_rows_applied": len(ib_detail["records"]),
        "bso_detail_rows_applied": len(bso_detail["records"]),
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
