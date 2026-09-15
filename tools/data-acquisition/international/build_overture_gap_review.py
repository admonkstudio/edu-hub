#!/usr/bin/env python3
"""Compare Egypt-only Overture discovery rows to the current D2.1 universe.

This is a discovery triage layer, not identity resolution. Exact normalized-name
matches are recorded as overlap evidence only. Unmatched rows are partitioned
into high-signal pre-university review, higher-education review and lower-priority
supporting leads. Nothing is added to the accepted universe automatically.
"""
from __future__ import annotations

import argparse
import json
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

PREUNIVERSITY_CATEGORIES = {
    "school", "private_school", "high_school", "elementary_school", "middle_school"
}
HIGHER_ED_CATEGORIES = {"college_university"}
STRONG_NAME_SIGNALS = [
    "international", "american", "british", "french", "francais", "français",
    "german", "deutsch", "canadian", "pakistan", "indian", "japanese", "korean",
    "italian", "spanish", "swiss", "baccalaureate", "choueifat", "sabis",
]


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def has_strong_signal(name: str) -> bool:
    folded = name.casefold()
    return any(signal.casefold() in folded for signal in STRONG_NAME_SIGNALS)


def review_tier(record: dict) -> str:
    category = str(record.get("category") or "").casefold()
    strong = has_strong_signal(str(record.get("name") or ""))
    if category in PREUNIVERSITY_CATEGORIES and strong:
        return "high_signal_preuniversity_review"
    if category in HIGHER_ED_CATEGORIES and strong:
        return "higher_ed_scope_review"
    return "lower_priority_supporting_review"


def build(universe_path: Path, overture_path: Path, output_dir: Path) -> dict:
    universe = read_jsonl(universe_path)
    overture = json.loads(overture_path.read_text(encoding="utf-8"))

    if overture.get("country_filter") != "EG":
        raise RuntimeError("Overture input is not restricted to Egypt country code EG")
    if overture.get("record_count") != len(overture.get("records", [])):
        raise RuntimeError("Overture record_count does not match records")

    current_names: dict[str, list[dict]] = defaultdict(list)
    for row in universe:
        for field in ("name_en", "name_ar"):
            key = normalize(row.get(field))
            if key:
                current_names[key].append(row)

    exact_overlaps: list[dict] = []
    unmatched_by_tier: dict[str, list[dict]] = defaultdict(list)
    for source in overture.get("records", []):
        normalized = normalize(source.get("name"))
        matches = current_names.get(normalized, [])
        base = {
            **source,
            "comparison_name_normalized": normalized,
            "auto_added_to_universe": False,
            "canonical_identity_created": False,
            "automatic_merge_performed": False,
            "international_eligibility_granted": False,
        }
        if matches:
            memberships = []
            seen = set()
            for match in matches:
                token = (match.get("source_id"), match.get("source_record_id"))
                if token in seen:
                    continue
                seen.add(token)
                memberships.append({
                    "current_source_id": match.get("source_id"),
                    "current_source_record_id": match.get("source_record_id"),
                    "current_name_en": match.get("name_en"),
                    "current_name_ar": match.get("name_ar"),
                    "match_basis": "exact_normalized_name_review_hint_only",
                })
            exact_overlaps.append({**base, "current_source_matches": memberships})
            continue

        tier = review_tier(source)
        unmatched_by_tier[tier].append({
            **base,
            "review_tier": tier,
            "review_state": "supporting_gap_candidate_requires_current_resourcing",
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "exact-name-overlaps.jsonl": exact_overlaps,
        "high-signal-preuniversity-review.jsonl": unmatched_by_tier["high_signal_preuniversity_review"],
        "higher-ed-scope-review.jsonl": unmatched_by_tier["higher_ed_scope_review"],
        "lower-priority-supporting-review.jsonl": unmatched_by_tier["lower_priority_supporting_review"],
    }
    for filename, rows in outputs.items():
        with (output_dir / filename).open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    all_unmatched = [row for rows in unmatched_by_tier.values() for row in rows]
    tier_counts = Counter(row["review_tier"] for row in all_unmatched)
    tier_unique_names = {
        tier: len({row["comparison_name_normalized"] for row in rows})
        for tier, rows in unmatched_by_tier.items()
    }
    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_overture_vs_current_universe_gap_review",
        "current_universe_source_rows": len(universe),
        "overture_egypt_rows": overture["record_count"],
        "overture_non_egypt_bbox_rows_rejected_upstream": overture.get("non_egypt_rows_rejected"),
        "exact_normalized_name_overlap_rows": len(exact_overlaps),
        "unmatched_supporting_rows": len(all_unmatched),
        "unmatched_unique_normalized_names": len({row["comparison_name_normalized"] for row in all_unmatched}),
        "unmatched_rows_by_review_tier": dict(sorted(tier_counts.items())),
        "unmatched_unique_names_by_review_tier": dict(sorted(tier_unique_names.items())),
        "high_signal_preuniversity_rows": len(unmatched_by_tier["high_signal_preuniversity_review"]),
        "higher_ed_scope_review_rows": len(unmatched_by_tier["higher_ed_scope_review"]),
        "lower_priority_supporting_rows": len(unmatched_by_tier["lower_priority_supporting_review"]),
        "fuzzy_matches_performed": 0,
        "overture_rows_auto_added_to_universe": 0,
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_identity_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "current_resourcing_required_before_promotion": True,
    }
    (output_dir / "gap-review-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--universe", type=Path,
        default=Path("artifacts/international/d2-1-universe-checkpoint/source-lead-universe.jsonl"),
    )
    parser.add_argument(
        "--overture", type=Path,
        default=Path("artifacts/international/overture-egypt-international-education/overture-egypt-international-education.json"),
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("artifacts/international/overture-gap-review"),
    )
    args = parser.parse_args()
    build(args.universe, args.overture, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
