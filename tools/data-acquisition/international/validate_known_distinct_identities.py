#!/usr/bin/env python3
"""Validate explicit D2.2 known-distinct identity decisions.

Negative identity evidence is important because similar names can otherwise
produce future false merges. Every pair in the checked-in seed must resolve to
existing source rows in the current scope-reviewed universe and must retain its
reviewed source names. This validator never mutates or merges identities.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DECISIONS = HERE / "seeds" / "known-distinct-identity-decisions-2026-09-15.json"
DEFAULT_UNIVERSE = Path("artifacts/international/accreditor-scope-review/reviewed-source-universe.jsonl")
DEFAULT_OUTPUT_DIR = Path("artifacts/international/known-distinct-review")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def current_name(row: dict) -> str:
    return str(row.get("name_en") or row.get("name_ar") or row.get("parent_university_en") or "")


def validate(decisions_path: Path, universe_path: Path, output_dir: Path) -> dict:
    decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
    universe = load_jsonl(universe_path)
    if len(universe) != 106:
        raise AssertionError(f"expected current 106-row source universe, found {len(universe)}")
    by_key = {(row["source_id"], row["source_record_id"]): row for row in universe}
    if len(by_key) != len(universe):
        raise AssertionError("duplicate source key in current universe")

    pairs = decisions.get("pairs") or []
    if decisions.get("pairs_count") != len(pairs) or len(pairs) != 2:
        raise AssertionError("known-distinct review currently expects two explicit pairs")
    safety = decisions.get("safety") or {}
    if safety.get("automatic_negative_match_inference_performed") is not False:
        raise AssertionError("known-distinct decisions must be explicit, not inferred automatically")

    validated: list[dict] = []
    seen_pair_ids: set[str] = set()
    seen_unordered_pairs: set[frozenset[tuple[str, str]]] = set()
    for pair in pairs:
        decision_id = pair["decision_id"]
        if decision_id in seen_pair_ids:
            raise AssertionError(f"duplicate known-distinct decision_id: {decision_id}")
        seen_pair_ids.add(decision_id)
        if not pair.get("decision", "").startswith("distinct_institutions"):
            raise AssertionError(f"unsupported known-distinct decision: {pair.get('decision')}")
        if pair.get("decision_confidence") != "high":
            raise AssertionError("known-distinct decisions require high confidence")
        if len(pair.get("evidence_urls") or []) < 2:
            raise AssertionError("known-distinct decisions require at least two evidence URLs")

        resolved = []
        pair_keys = []
        for side_name in ("left", "right"):
            side = pair[side_name]
            key = (side["source_id"], side["source_record_id"])
            row = by_key.get(key)
            if row is None:
                raise AssertionError(f"known-distinct source row missing from current universe: {key}")
            name = current_name(row)
            if name != side["source_name"]:
                raise AssertionError(
                    f"known-distinct source name drift for {key}: expected={side['source_name']!r} current={name!r}"
                )
            resolved.append({
                "side": side_name,
                "source_id": side["source_id"],
                "source_record_id": side["source_record_id"],
                "source_name": name,
                "scope_state": row.get("scope_state"),
                "source_url": row.get("source_url"),
            })
            pair_keys.append(key)

        if pair_keys[0] == pair_keys[1]:
            raise AssertionError(f"known-distinct pair points to the same source row: {decision_id}")
        unordered = frozenset(pair_keys)
        if unordered in seen_unordered_pairs:
            raise AssertionError(f"duplicate known-distinct unordered pair: {decision_id}")
        seen_unordered_pairs.add(unordered)

        validated.append({
            "decision_id": decision_id,
            "decision": pair["decision"],
            "decision_confidence": pair["decision_confidence"],
            "resolved_source_rows": resolved,
            "evidence_urls": list(pair["evidence_urls"]),
            "review_note": pair["review_note"],
            "automatic_merge_blocked": True,
            "canonical_database_write_performed": False,
            "public_projection_performed": False,
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "known-distinct-identity-pairs.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for row in validated:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": 1,
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.2_known_distinct_identity_review",
        "source_universe_rows": len(universe),
        "validated_distinct_pairs": len(validated),
        "resolved_source_rows": len(validated) * 2,
        "automatic_negative_match_inference_performed": False,
        "automatic_merges_performed": 0,
        "canonical_database_rows_written": 0,
        "runtime_database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "output": output_path.name,
    }
    (output_dir / "known-distinct-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--universe", type=Path, default=DEFAULT_UNIVERSE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    validate(args.decisions, args.universe, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
