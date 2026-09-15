#!/usr/bin/env python3
"""Match the 24 first-party Cognia claims against the full official Egypt registry.

Only normalized exact-name matches are classified as deterministic registry
matches. Similar names are emitted as review proposals with similarity scores;
they are not accreditation confirmations, identity merges, or eligibility
claims. This protects division/campus/provider scope for D2.2 review.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_QUEUE = Path(
    "tools/data-acquisition/international/seeds/"
    "cognia-registry-verification-queue-2026-09-15.json"
)
DEFAULT_REGISTRY = Path(
    "artifacts/international/cognia-egypt-registry/cognia-egypt-registry.json"
)
DEFAULT_OUTPUT = Path(
    "artifacts/international/cognia-egypt-registry/cognia-verification-queue-match.json"
)


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(ch for ch in value if ch.isalnum() or ch.isspace())
    return " ".join(value.split())


def tokens(value: str) -> set[str]:
    return set(normalize_name(value).split())


def score(a: str, b: str) -> float:
    na, nb = normalize_name(a), normalize_name(b)
    sequence = difflib.SequenceMatcher(None, na, nb).ratio()
    ta, tb = tokens(a), tokens(b)
    jaccard = len(ta & tb) / len(ta | tb) if ta | tb else 0.0
    containment = max(
        len(ta & tb) / len(ta) if ta else 0.0,
        len(ta & tb) / len(tb) if tb else 0.0,
    )
    return round((sequence * 0.5) + (jaccard * 0.3) + (containment * 0.2), 6)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    queue = json.loads(args.queue.read_text(encoding="utf-8"))
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    rows = registry["records"]
    by_normalized: dict[str, list[dict]] = {}
    for row in rows:
        by_normalized.setdefault(row["institution_name_normalized"], []).append(row)

    matches: list[dict] = []
    exact_count = 0
    for lead in queue["records"]:
        query = lead["query_name"]
        normalized = normalize_name(query)
        exact = by_normalized.get(normalized, [])
        if exact:
            exact_count += 1
            state = "deterministic_normalized_exact_registry_match"
            proposals = []
        else:
            state = "requires_registry_identity_scope_review"
            ranked = sorted(
                (
                    {
                        "source_row_number": row["source_row_number"],
                        "institution_name": row["institution_name"],
                        "city": row.get("city"),
                        "institution_type": row.get("institution_type"),
                        "system": row.get("system"),
                        "similarity_score": score(query, row["institution_name"]),
                    }
                    for row in rows
                ),
                key=lambda item: (-item["similarity_score"], item["source_row_number"]),
            )
            proposals = [item for item in ranked[:5] if item["similarity_score"] >= 0.45]

        matches.append(
            {
                "query_name": query,
                "query_name_normalized": normalized,
                "primary_url": lead["primary_url"],
                "primary_claim_state": lead["primary_claim_state"],
                "location_hint": lead.get("location_hint"),
                "identity_note": lead.get("identity_note"),
                "registry_match_state": state,
                "deterministic_exact_rows": [
                    {
                        "source_row_number": row["source_row_number"],
                        "institution_name": row["institution_name"],
                        "city": row.get("city"),
                        "institution_type": row.get("institution_type"),
                        "system": row.get("system"),
                    }
                    for row in exact
                ],
                "review_proposals": proposals,
                "accreditation_confirmed_by_this_matcher": bool(exact),
                "international_eligibility_granted": False,
                "identity_merge_performed": False,
            }
        )

    unresolved = len(matches) - exact_count
    result = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_cognia_registry_verification_queue_match",
        "registry_source_result_count": registry["source_result_count"],
        "queue_record_count": len(matches),
        "deterministic_exact_match_count": exact_count,
        "requires_identity_scope_review_count": unresolved,
        "records": matches,
        "rules": {
            "exact_normalized_name_confirms_registry_presence": True,
            "fuzzy_proposals_auto_confirm_accreditation": False,
            "cognia_registry_presence_auto_grants_international_eligibility": False,
            "automatic_identity_merge": False,
            "database_mutation": False,
            "public_projection": False,
        },
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "queue_record_count": len(matches),
                "deterministic_exact_match_count": exact_count,
                "requires_identity_scope_review_count": unresolved,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
