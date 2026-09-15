#!/usr/bin/env python3
"""Append explicitly reviewed substantive-international higher-ed evidence to D2.1.

This overlay preserves the accepted 597-row checkpoint as the reproducible base.
It adds only checked-in reviewed evidence rows whose international status is
substantive (binational/intergovernmental/transnational/international-organization),
not merely branding, partnership, validation, or a dual-degree arrangement.

No canonical identity, automatic merge, runtime database write, or public
projection is performed.
"""
from __future__ import annotations

import argparse
import json
import unicodedata
from collections import Counter
from pathlib import Path


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build(universe_path: Path, summary_path: Path, seed_path: Path, output_dir: Path) -> dict:
    rows = read_jsonl(universe_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    seed = json.loads(seed_path.read_text(encoding="utf-8"))

    if len(rows) != 597 or summary.get("current_source_lead_rows") != 597:
        raise RuntimeError("Expected the accepted 597-row pre-higher-ed checkpoint")
    base_states = Counter(str(r.get("scope_state") or r.get("lead_state") or "candidate") for r in rows)
    if base_states != Counter({"eligible": 128, "supporting_candidate": 466, "excluded": 3}):
        raise RuntimeError(f"Unexpected pre-overlay states: {dict(base_states)}")

    reviewed = seed.get("records", [])
    if seed.get("records_count") != 5 or len(reviewed) != 5:
        raise RuntimeError("Expected exactly five reviewed substantive-international HE rows")
    if any(r.get("scope_state") != "eligible" for r in reviewed):
        raise RuntimeError("Every reviewed HE row must be explicitly scope-eligible")
    if any(not r.get("strong_evidence") or len(r.get("evidence_urls") or []) < 2 for r in reviewed):
        raise RuntimeError("Every reviewed HE row must retain strong multi-source evidence")

    existing_keys = {(str(r.get("source_id")), str(r.get("source_record_id"))) for r in rows}
    new_keys = [(str(r.get("source_id")), str(r.get("source_record_id"))) for r in reviewed]
    if len(set(new_keys)) != 5 or any(key in existing_keys for key in new_keys):
        raise RuntimeError("Reviewed HE source keys must be five unique additive keys")

    for source in reviewed:
        name = source["name_en"]
        normalized = normalize(name)
        rows.append({
            "discovery_record_id": f"reviewed-he-{source['source_record_id']}",
            "source_id": source["source_id"],
            "source_record_id": source["source_record_id"],
            "source_url": source["evidence_urls"][0],
            "source_snapshot_date": seed["snapshot_date"],
            "entity_family": "higher_education",
            "institution_type": source["institution_type"],
            "name_en": name,
            "name_ar": None,
            "scope_state": "eligible",
            "scope_class": source["scope_class"],
            "lead_state": None,
            "strong_evidence": source["strong_evidence"],
            "evidence_urls": source["evidence_urls"],
            "review_note": source["review_note"],
            "storage_policy": "reviewed_current_substantive_international_he_evidence",
            "normalized_name_en": normalized,
            "normalized_name_ar": None,
            "discovery_cluster_key": f"en:{normalized}",
            "cluster_is_review_hint_only": True,
            "record_role": "reviewed_substantive_international_higher_education_evidence",
            "canonical_identity_created": False,
            "automatic_merge_performed": False,
            "scope_decision_origin": "explicit_substantive_international_he_review_2026_09_15",
        })

    states = Counter(str(r.get("scope_state") or r.get("lead_state") or "candidate") for r in rows)
    if len(rows) != 602:
        raise RuntimeError(f"Expected 602 rows after HE overlay, got {len(rows)}")
    if states != Counter({"eligible": 133, "supporting_candidate": 466, "excluded": 3}):
        raise RuntimeError(f"Unexpected post-overlay states: {dict(states)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    out_universe = output_dir / "source-lead-universe.jsonl"
    with out_universe.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    source_counts = Counter(str(r.get("source_id") or "unknown") for r in rows)
    updated = dict(summary)
    updated.update({
        "schema_version": max(int(summary.get("schema_version", 1)), 5),
        "pre_substantive_international_he_source_lead_rows": 597,
        "substantive_international_he_review_rows": 5,
        "current_source_lead_rows": 602,
        "source_counts": dict(sorted(source_counts.items())),
        "scope_or_lead_state_counts": dict(sorted(states.items())),
        "unique_institutions_claimed": None,
        "substantive_he_rows_auto_identity_merged": 0,
        "canonical_institutions_created": 0,
        "automatic_identity_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "d2_1_complete": False,
    })
    (output_dir / "checkpoint-summary.json").write_text(
        json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    family = {
        "schema_version": 1,
        "review_package": seed["review_package"],
        "scope_rule": seed["scope_rule"],
        "records_count": 5,
        "source_keys": [{"source_id": r["source_id"], "source_record_id": r["source_record_id"]} for r in reviewed],
        "unique_institutions_claimed": None,
        "canonical_institutions_created": 0,
        "automatic_identity_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
    }
    (output_dir / "substantive-international-he-source-family.json").write_text(
        json.dumps(family, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(updated, ensure_ascii=False, indent=2))
    return updated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", type=Path, default=Path("artifacts/international/d2-1-universe-checkpoint/source-lead-universe.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("artifacts/international/d2-1-universe-checkpoint/checkpoint-summary.json"))
    parser.add_argument("--seed", type=Path, default=Path("tools/data-acquisition/international/seeds/substantive-international-higher-ed-review-2026-09-15.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/international/d2-1-universe-checkpoint"))
    args = parser.parse_args()
    build(args.universe, args.summary, args.seed, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
