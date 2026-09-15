#!/usr/bin/env python3
"""Build the current D2.1 source/lead-universe checkpoint.

The previous reviewed universe contains the four Cognia milestone rows. The
complete Cognia Egypt registry supersedes those four rows for *universe-count*
purposes while the exact-name reviewed scope decisions are carried forward to
the corresponding registry rows. This is source-family supersession, not an
identity merge: all other Cognia registry rows remain supporting candidates.

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


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def build(previous_universe: Path, cognia_registry: Path, milestone_seed: Path, output_dir: Path) -> dict:
    previous = read_jsonl(previous_universe)
    registry = json.loads(cognia_registry.read_text(encoding="utf-8"))
    milestone = json.loads(milestone_seed.read_text(encoding="utf-8"))

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

    source_counts = Counter(str(row.get("source_id") or "unknown") for row in current)
    state_counts = Counter(str(row.get("scope_state") or row.get("lead_state") or "candidate") for row in current)
    if len(current) != 584:
        raise RuntimeError(f"Expected 584 current source/lead rows, got {len(current)}")
    if source_counts[REGISTRY_SOURCE] != 256:
        raise RuntimeError("Current universe does not contain all 256 Cognia registry rows")
    if MILESTONE_SOURCE in source_counts:
        raise RuntimeError("Superseded Cognia milestone rows remain in current universe count")
    if len(superseded) != 4:
        raise RuntimeError(f"Expected four deterministic Cognia supersessions, got {len(superseded)}")
    if state_counts != Counter({"supporting_candidate": 466, "eligible": 115, "excluded": 3}):
        raise RuntimeError(f"Unexpected current scope/lead counts: {dict(state_counts)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "source-lead-universe.jsonl").open("w", encoding="utf-8") as handle:
        for row in current:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    (output_dir / "cognia-source-family-supersession.json").write_text(
        json.dumps(superseded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_expanded_source_lead_universe_checkpoint",
        "foundational_authoritative_seed_rows": 96,
        "historical_classified_strong_rows": 106,
        "previous_reviewed_source_lead_rows": len(previous),
        "british_council_rows": source_counts.get("british_council_partner_schools_egypt_2026_09", 0),
        "cognia_full_registry_rows": source_counts[REGISTRY_SOURCE],
        "cognia_milestone_rows_superseded": len(superseded),
        "cognia_new_rows_beyond_milestone_subset": source_counts[REGISTRY_SOURCE] - len(superseded),
        "current_source_lead_rows": len(current),
        "source_counts": dict(sorted(source_counts.items())),
        "scope_or_lead_state_counts": dict(sorted(state_counts.items())),
        "unique_institutions_claimed": None,
        "cognia_registry_rows_auto_granted_eligibility": 0,
        "scope_decisions_carried_forward_by_exact_source_family_supersession": len(superseded),
        "canonical_institutions_created": 0,
        "automatic_identity_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "d2_1_complete": False,
        "remaining_gap_sources": ["osm_overture", "v7_owned_archive", "edarabia_reference_only", "institution_primary_gap_check"],
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
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/international/d2-1-universe-checkpoint"))
    args = parser.parse_args()
    build(args.previous_universe, args.cognia_registry, args.milestone_seed, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
