#!/usr/bin/env python3
"""Apply the reviewed Mansoura College provider/school topology to D2.1.

The overlay adds only the two explicitly qualified international school units:
Mansoura College British School and Mansoura College 2 International American
School. The provider umbrella and two National school units remain topology
context only. Existing British Council, Cognia and Overture rows are preserved
as separate provenance and are never mutated or automatically merged.
"""
from __future__ import annotations

import argparse
import json
import unicodedata
from collections import Counter
from pathlib import Path

BRITISH_SOURCE_ID = "reviewed_mansoura_college_british_school_2026_09_15"
AMERICAN_SOURCE_ID = "reviewed_mansoura_college_american_school_2026_09_15"
BC_KEY = ("british_council_partner_schools_egypt_2026_09", "bcps2026:mansoura-college-modern")
COGNIA_KEY = ("cognia_accreditation_registry_egypt_2026_09_15", "registry-row-147")
OVERTURE_AMERICAN_ID = "2f30ad71-e0bb-47d5-b86e-238edfb1826a"
OVERTURE_UMBRELLA_ID = "9e34fa47-a93e-4c90-a902-9a8181834ec2"


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build(
    universe_path: Path,
    summary_path: Path,
    seed_path: Path,
    overture_path: Path,
    output_dir: Path,
) -> dict:
    universe = read_jsonl(universe_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    overture = json.loads(overture_path.read_text(encoding="utf-8"))

    if len(universe) != 602 or summary.get("current_source_lead_rows") != 602:
        raise RuntimeError("Expected the accepted 602-row pre-Mansoura checkpoint")
    states = Counter(str(r.get("scope_state") or r.get("lead_state") or "candidate") for r in universe)
    if states != Counter({"eligible": 133, "supporting_candidate": 466, "excluded": 3}):
        raise RuntimeError(f"Unexpected pre-Mansoura states: {dict(states)}")

    if seed.get("review_package") != "mansoura_college_provider_school_topology_review":
        raise RuntimeError("Unexpected Mansoura review package")
    provider = seed.get("provider") or {}
    if provider.get("review_state") != "provider_group_evidenced_not_canonicalized":
        raise RuntimeError("Mansoura provider must remain non-canonical review context")

    units = seed.get("units") or []
    if len(units) != 4:
        raise RuntimeError(f"Expected four reviewed provider units, found {len(units)}")
    eligible_units = [u for u in units if u.get("d2_1_scope_state") == "eligible"]
    context_units = [u for u in units if u.get("d2_1_scope_state") == "excluded_provider_context_only"]
    if len(eligible_units) != 2 or len(context_units) != 2:
        raise RuntimeError("Expected exactly two eligible international units and two national context units")

    by_review_key = {str(u.get("review_key")): u for u in units}
    british = by_review_key.get("mansoura-college-british-school")
    american = by_review_key.get("mansoura-college-2-international-american-school")
    if not british or not american:
        raise RuntimeError("Mansoura British/American reviewed units are missing")
    if british.get("recognized_identifier") != "Pearson centre 92720":
        raise RuntimeError("Mansoura British reviewed centre identifier changed unexpectedly")
    if len(british.get("primary_evidence_urls") or []) < 2 or not british.get("recognized_evidence_urls"):
        raise RuntimeError("Mansoura British unit lacks current primary + recognized evidence")
    if len(american.get("primary_evidence_urls") or []) < 2 or len(american.get("recognized_evidence_urls") or []) < 2:
        raise RuntimeError("Mansoura American unit lacks current primary + recognized evidence")

    universe_by_key = {
        (str(r.get("source_id")), str(r.get("source_record_id"))): r
        for r in universe
    }
    bc_row = universe_by_key.get(BC_KEY)
    cognia_row = universe_by_key.get(COGNIA_KEY)
    if not bc_row or bc_row.get("name_en") != "Mansoura College Modern":
        raise RuntimeError("Expected British Council Mansoura College Modern source row")
    if not cognia_row or cognia_row.get("name_en") != "Mansoura College 2 International School":
        raise RuntimeError("Expected Cognia Mansoura College 2 International School source row")
    if (cognia_row.get("scope_state") or cognia_row.get("lead_state")) != "supporting_candidate":
        raise RuntimeError("Existing Cognia Mansoura row must remain supporting source evidence")
    if (bc_row.get("scope_state") or bc_row.get("lead_state")) != "supporting_candidate":
        raise RuntimeError("Existing British Council Mansoura row must remain supporting source evidence")

    overture_records = {str(r.get("overture_id")): r for r in overture.get("records", [])}
    american_overture = overture_records.get(OVERTURE_AMERICAN_ID)
    umbrella_overture = overture_records.get(OVERTURE_UMBRELLA_ID)
    if not american_overture or american_overture.get("name") != "Mansoura College American Schools In Egypt":
        raise RuntimeError("Expected supporting Overture American-school row")
    if not umbrella_overture or umbrella_overture.get("name") != "Mansoura College International Schools":
        raise RuntimeError("Expected supporting Overture provider-umbrella row")

    rerouted = seed.get("rerouted_overture_provider_row") or {}
    if str(rerouted.get("overture_id")) != OVERTURE_UMBRELLA_ID:
        raise RuntimeError("Mansoura provider reroute must target the exact Overture umbrella row")
    if rerouted.get("decision") != "provider_umbrella_alias_not_separate_institution":
        raise RuntimeError("Mansoura Overture umbrella must remain provider context, not an institution")

    existing_keys = set(universe_by_key)
    new_keys = {
        (BRITISH_SOURCE_ID, "pearson-centre-92720"),
        (AMERICAN_SOURCE_ID, "mcas-reviewed-2026-09-15"),
    }
    if existing_keys.intersection(new_keys):
        raise RuntimeError("Mansoura reviewed source keys must be additive")

    def evidence_row(source_id: str, source_record_id: str, unit: dict, role: str, memberships: list[dict]) -> dict:
        name = unit["name_en"]
        evidence_urls = list(unit.get("primary_evidence_urls") or []) + list(unit.get("recognized_evidence_urls") or [])
        return {
            "discovery_record_id": f"mansoura-topology-{source_record_id}",
            "source_id": source_id,
            "source_record_id": source_record_id,
            "source_url": evidence_urls[0],
            "source_snapshot_date": seed["snapshot_date"],
            "entity_family": "pre_university",
            "institution_type": "international_school",
            "name_en": name,
            "name_ar": None,
            "scope_state": "eligible",
            "scope_class": "international_school",
            "lead_state": None,
            "strong_evidence": unit["strong_evidence"],
            "curriculum_scope": unit.get("curriculum_scope"),
            "evidence_urls": evidence_urls,
            "recognized_identifier": unit.get("recognized_identifier"),
            "reviewed_provider_key": provider.get("review_key"),
            "provider_relationship_state": "reviewed_same_provider_group_not_canonical_provider_merge",
            "source_membership_review_hints": memberships,
            "storage_policy": "reviewed_current_primary_and_recognized_source_evidence",
            "normalized_name_en": normalize(name),
            "normalized_name_ar": None,
            "discovery_cluster_key": f"en:{normalize(name)}",
            "cluster_is_review_hint_only": True,
            "record_role": role,
            "canonical_identity_created": False,
            "automatic_merge_performed": False,
            "scope_decision_origin": "explicit_mansoura_college_topology_review_2026_09_15",
        }

    british_row = evidence_row(
        BRITISH_SOURCE_ID,
        "pearson-centre-92720",
        british,
        "reviewed_mansoura_british_school_evidence",
        [],
    )
    american_row = evidence_row(
        AMERICAN_SOURCE_ID,
        "mcas-reviewed-2026-09-15",
        american,
        "reviewed_mansoura_american_school_evidence",
        list(american.get("source_links") or []),
    )

    current = list(universe) + [british_row, american_row]
    post_states = Counter(str(r.get("scope_state") or r.get("lead_state") or "candidate") for r in current)
    if len(current) != 604:
        raise RuntimeError(f"Expected 604 rows after Mansoura overlay, got {len(current)}")
    if post_states != Counter({"eligible": 135, "supporting_candidate": 466, "excluded": 3}):
        raise RuntimeError(f"Unexpected post-Mansoura states: {dict(post_states)}")

    source_counts = Counter(str(r.get("source_id") or "unknown") for r in current)
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "source-lead-universe.jsonl").open("w", encoding="utf-8") as handle:
        for row in current:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    updated = dict(summary)
    updated.update({
        "schema_version": max(int(summary.get("schema_version", 1)), 6),
        "pre_mansoura_topology_source_lead_rows": 602,
        "mansoura_college_reviewed_international_school_rows": 2,
        "mansoura_college_provider_units_reviewed": 4,
        "mansoura_college_provider_umbrella_materialized_as_institution": False,
        "current_source_lead_rows": 604,
        "source_counts": dict(sorted(source_counts.items())),
        "scope_or_lead_state_counts": dict(sorted(post_states.items())),
        "unique_institutions_claimed": None,
        "mansoura_rows_auto_identity_merged": 0,
        "canonical_institutions_created": 0,
        "automatic_identity_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "d2_1_complete": False,
    })
    (output_dir / "checkpoint-summary.json").write_text(
        json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    topology = {
        "schema_version": 1,
        "review_package": seed["review_package"],
        "provider": provider,
        "units": units,
        "rerouted_overture_provider_row": rerouted,
        "existing_source_rows_preserved": [
            {
                "source_id": BC_KEY[0],
                "source_record_id": BC_KEY[1],
                "name_en": bc_row.get("name_en"),
                "mutated": False,
            },
            {
                "source_id": COGNIA_KEY[0],
                "source_record_id": COGNIA_KEY[1],
                "name_en": cognia_row.get("name_en"),
                "mutated": False,
            },
        ],
        "supporting_overture_rows_reviewed": [
            {"overture_id": OVERTURE_AMERICAN_ID, "name": american_overture.get("name")},
            {"overture_id": OVERTURE_UMBRELLA_ID, "name": umbrella_overture.get("name")},
        ],
        "new_universe_source_rows": 2,
        "new_eligible_source_rows": 2,
        "provider_umbrella_is_separate_canonical_institution": False,
        "national_units_added_to_active_universe": 0,
        "british_council_partner_status_granted_eligibility": False,
        "cognia_alone_granted_eligibility": False,
        "overture_granted_eligibility": False,
        "unique_institutions_claimed": None,
        "canonical_institutions_created": 0,
        "automatic_identity_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
    }
    (output_dir / "mansoura-college-topology-source-family.json").write_text(
        json.dumps(topology, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"checkpoint": updated, "mansoura_topology": topology}, ensure_ascii=False, indent=2))
    return updated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", type=Path, default=Path("artifacts/international/d2-1-universe-checkpoint/source-lead-universe.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("artifacts/international/d2-1-universe-checkpoint/checkpoint-summary.json"))
    parser.add_argument("--seed", type=Path, default=Path("tools/data-acquisition/international/seeds/mansoura-college-topology-review-2026-09-15.json"))
    parser.add_argument("--overture", type=Path, default=Path("artifacts/international/overture-egypt-international-education/overture-egypt-international-education.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/international/d2-1-universe-checkpoint"))
    args = parser.parse_args()
    build(args.universe, args.summary, args.seed, args.overture, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
