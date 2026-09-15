#!/usr/bin/env python3
"""Build the current D2.1 source/lead-universe checkpoint.

The historical reviewed universe contains the four Cognia milestone rows. The
complete Cognia Egypt registry supersedes those four rows for *universe-count*
purposes while the exact-name reviewed scope decisions are carried forward to
the corresponding registry rows. This is source-family supersession, not an
identity merge: all other Cognia registry rows remain supporting candidates.

A current Canadian offshore-school evidence family is then added independently.
Those rows are authoritative source evidence, not unique-institution claims;
known cross-source overlap (for example Royal Canadian School) and BCCIS
East/West topology remain D2.2 identity/campus review work.

The output is still a source/lead universe. It never claims a unique institution
count and never writes canonical/public/database state.
"""
from __future__ import annotations

import argparse
import json
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

MILESTONE_SOURCE = "cognia_member_milestones_egypt_2026_2027"
REGISTRY_SOURCE = "cognia_accreditation_registry_egypt_2026_09_15"
REGISTRY_URL = "https://home.cognia.org/registry"
CANADIAN_SOURCE = "cicic_canadian_offshore_schools_egypt_2026_09_15"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def build(
    previous_universe: Path,
    cognia_registry: Path,
    milestone_seed: Path,
    canadian_seed: Path,
    output_dir: Path,
) -> dict:
    previous = read_jsonl(previous_universe)
    registry = json.loads(cognia_registry.read_text(encoding="utf-8"))
    milestone = json.loads(milestone_seed.read_text(encoding="utf-8"))
    canadian = json.loads(canadian_seed.read_text(encoding="utf-8"))

    if registry.get("source_result_count") != 256 or registry.get("extracted_record_count") != 256:
        raise RuntimeError("Expected the verified 256-row Cognia Egypt registry extraction")
    if not registry.get("official_registry_extraction_complete"):
        raise RuntimeError("Cognia registry extraction is not marked complete")

    previous_milestones = [row for row in previous if row.get("source_id") == MILESTONE_SOURCE]
    if len(previous_milestones) != milestone.get("records_count") or len(previous_milestones) != 4:
        raise RuntimeError(f"Expected four prior Cognia milestone rows, found {len(previous_milestones)}")

    prior_by_name = {normalize(row.get("name_en")): row for row in previous_milestones}
    seed_names = {normalize(row.get("name")) for row in milestone.get("records", [])}
    if set(prior_by_name) != seed_names:
        raise RuntimeError("Prior universe Cognia milestone names do not match checked-in milestone seed")
    if any(row.get("scope_state") != "eligible" for row in previous_milestones):
        raise RuntimeError("All four previously reviewed Cognia milestone rows must remain eligible")

    registry_name_counts = Counter(normalize(row.get("institution_name")) for row in registry.get("records", []))
    missing = sorted(name for name in seed_names if registry_name_counts[name] != 1)
    if missing:
        raise RuntimeError(f"Cognia source-family supersession is not deterministic for: {missing}")

    retained = [row for row in previous if row.get("source_id") != MILESTONE_SOURCE]
    current = list(retained)
    superseded = []
    for source in registry.get("records", []):
        normalized = normalize(source.get("institution_name"))
        prior = prior_by_name.get(normalized)
        scope_state = prior.get("scope_state") if prior else "supporting_candidate"
        scope_class = prior.get("scope_class") if prior else None
        if prior:
            superseded.append({
                "milestone_source_record_id": prior.get("source_record_id"),
                "registry_source_row_number": source.get("source_row_number"),
                "name_en": source.get("institution_name"),
                "scope_state_carried_forward": scope_state,
                "match_basis": "same_publisher_exact_normalized_name",
                "identity_merge_performed": False,
            })
        current.append({
            "discovery_record_id": f"cognia-registry-{source.get('source_row_number'):03d}",
            "source_id": REGISTRY_SOURCE,
            "source_record_id": f"registry-row-{source.get('source_row_number'):03d}",
            "source_url": REGISTRY_URL,
            "source_snapshot_date": "2026-09-15",
            "entity_family": "pre_university",
            "institution_type": source.get("institution_type"),
            "name_en": source.get("institution_name"),
            "name_ar": None,
            "city": source.get("city"),
            "scope_state": scope_state,
            "scope_class": scope_class,
            "lead_state": None if prior else "supporting_candidate",
            "storage_policy": "official_registry_snapshot_evidence",
            "normalized_name_en": normalized or None,
            "normalized_name_ar": None,
            "discovery_cluster_key": f"en:{normalized}" if normalized else None,
            "cluster_is_review_hint_only": True,
            "record_role": "official_accreditor_registry_evidence",
            "canonical_identity_created": False,
            "automatic_merge_performed": False,
            "cognia_system": source.get("system"),
            "scope_decision_origin": "prior_review_exact_source_family_supersession" if prior else "unreviewed_registry_supporting_candidate",
        })

    pre_canadian_source_counts = Counter(str(row.get("source_id") or "unknown") for row in current)
    pre_canadian_state_counts = Counter(str(row.get("scope_state") or row.get("lead_state") or "candidate") for row in current)
    if len(current) != 584:
        raise RuntimeError(f"Expected 584 pre-Canadian source/lead rows, got {len(current)}")
    if pre_canadian_source_counts[REGISTRY_SOURCE] != 256:
        raise RuntimeError("Current universe does not contain all 256 Cognia registry rows")
    if MILESTONE_SOURCE in pre_canadian_source_counts:
        raise RuntimeError("Superseded Cognia milestone rows remain in current universe count")
    if len(superseded) != 4:
        raise RuntimeError(f"Expected four deterministic Cognia supersessions, got {len(superseded)}")
    if pre_canadian_state_counts != Counter({"supporting_candidate": 466, "eligible": 115, "excluded": 3}):
        raise RuntimeError(f"Unexpected pre-Canadian scope/lead counts: {dict(pre_canadian_state_counts)}")

    if canadian.get("source_id") != CANADIAN_SOURCE:
        raise RuntimeError(f"Unexpected Canadian source id: {canadian.get('source_id')}")
    canadian_records = canadian.get("records", [])
    if canadian.get("records_count") != 6 or len(canadian_records) != 6:
        raise RuntimeError("Expected six current Canadian-authorized Egypt offshore-school rows")
    canadian_ids = [str(row.get("cicic_id") or "") for row in canadian_records]
    if not all(canadian_ids) or len(set(canadian_ids)) != 6:
        raise RuntimeError("Canadian offshore-school CICIC IDs must be six unique non-empty values")
    if any(row.get("legal_status") != "authorized" for row in canadian_records):
        raise RuntimeError("Every Canadian offshore-school row must be currently authorized")
    if any(row.get("ownership_scope") != "private_for_profit" for row in canadian_records):
        raise RuntimeError("Every Canadian offshore-school row must retain its private-for-profit scope evidence")
    if any(row.get("scope_state") != "eligible" for row in canadian_records):
        raise RuntimeError("Every accepted Canadian offshore-school source row must be scope-eligible")

    for source in canadian_records:
        normalized = normalize(source.get("name"))
        current.append({
            "discovery_record_id": f"canadian-offshore-{source['cicic_id']}",
            "source_id": CANADIAN_SOURCE,
            "source_record_id": f"cicic-{source['cicic_id']}",
            "source_url": source.get("official_profile_url"),
            "source_snapshot_date": canadian.get("snapshot_date"),
            "entity_family": "pre_university",
            "institution_type": "international_school",
            "name_en": source.get("name"),
            "name_ar": None,
            "city": source.get("city"),
            "scope_state": "eligible",
            "scope_class": "international_school",
            "lead_state": None,
            "ownership_scope": source.get("ownership_scope"),
            "legal_status": source.get("legal_status"),
            "strong_evidence": source.get("strong_evidence"),
            "canadian_province_system": source.get("province_system"),
            "province_authority_url": source.get("province_authority_url"),
            "website": source.get("institution_site"),
            "storage_policy": "current_authorized_offshore_school_source_evidence",
            "normalized_name_en": normalized or None,
            "normalized_name_ar": None,
            "discovery_cluster_key": f"en:{normalized}" if normalized else None,
            "cluster_is_review_hint_only": True,
            "record_role": "recognized_canadian_offshore_school_authorization_evidence",
            "canonical_identity_created": False,
            "automatic_merge_performed": False,
            "scope_decision_origin": "current_authorized_canadian_offshore_school_plus_private_scope",
            "known_existing_source_identity_hint": source.get("known_existing_source_identity_hint"),
        })

    source_counts = Counter(str(row.get("source_id") or "unknown") for row in current)
    state_counts = Counter(str(row.get("scope_state") or row.get("lead_state") or "candidate") for row in current)
    if len(current) != 590:
        raise RuntimeError(f"Expected 590 current source/lead rows, got {len(current)}")
    if source_counts[CANADIAN_SOURCE] != 6:
        raise RuntimeError("Current universe does not contain all six Canadian offshore-school rows")
    if state_counts != Counter({"supporting_candidate": 466, "eligible": 121, "excluded": 3}):
        raise RuntimeError(f"Unexpected current scope/lead counts: {dict(state_counts)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "source-lead-universe.jsonl").open("w", encoding="utf-8") as handle:
        for row in current:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    (output_dir / "cognia-source-family-supersession.json").write_text(
        json.dumps(superseded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "canadian-offshore-source-family.json").write_text(
        json.dumps({
            "source_id": CANADIAN_SOURCE,
            "records_count": len(canadian_records),
            "source_record_ids": [f"cicic-{value}" for value in canadian_ids],
            "unique_institutions_claimed": None,
            "known_cross_source_identity_hints_are_review_only": True,
            "canonical_institutions_created": 0,
            "automatic_identity_merges_performed": 0,
            "database_mutation_performed": False,
            "public_projection_rows_created": 0,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    summary = {
        "schema_version": 2,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_expanded_source_lead_universe_checkpoint",
        "foundational_authoritative_seed_rows": 96,
        "historical_classified_strong_rows": 106,
        "previous_reviewed_source_lead_rows": len(previous),
        "pre_canadian_current_source_lead_rows": 584,
        "british_council_rows": source_counts.get("british_council_partner_schools_egypt_2026_09", 0),
        "cognia_full_registry_rows": source_counts[REGISTRY_SOURCE],
        "cognia_milestone_rows_superseded": len(superseded),
        "cognia_new_rows_beyond_milestone_subset": source_counts[REGISTRY_SOURCE] - len(superseded),
        "canadian_authorized_offshore_school_rows": source_counts[CANADIAN_SOURCE],
        "current_source_lead_rows": len(current),
        "source_counts": dict(sorted(source_counts.items())),
        "scope_or_lead_state_counts": dict(sorted(state_counts.items())),
        "unique_institutions_claimed": None,
        "cognia_registry_rows_auto_granted_eligibility": 0,
        "scope_decisions_carried_forward_by_exact_source_family_supersession": len(superseded),
        "canadian_rows_auto_identity_merged": 0,
        "canonical_institutions_created": 0,
        "automatic_identity_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "d2_1_complete": False,
        "remaining_gap_sources": ["osm_diagnostic_overture_resolution", "v7_owned_archive", "edarabia_reference_only", "institution_primary_gap_check"],
    }
    (output_dir / "checkpoint-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous-universe", type=Path, default=Path("artifacts/international/british-council-reviewed-candidate-universe/candidate-universe.jsonl"))
    parser.add_argument("--cognia-registry", type=Path, default=Path("artifacts/international/cognia-egypt-registry/cognia-egypt-registry.json"))
    parser.add_argument("--milestone-seed", type=Path, default=Path("tools/data-acquisition/international/seeds/cognia-egypt-milestones-2026-2027.json"))
    parser.add_argument("--canadian-seed", type=Path, default=Path("tools/data-acquisition/international/seeds/canadian-offshore-schools-egypt-2026-09-15.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/international/d2-1-universe-checkpoint"))
    args = parser.parse_args()
    build(args.previous_universe, args.cognia_registry, args.milestone_seed, args.canadian_seed, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
