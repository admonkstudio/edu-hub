#!/usr/bin/env python3
"""Materialize the Cognia Egypt official-registry verification queue.

Institution-primary accreditation claims are discovery evidence only. They remain
pending until verified against Cognia's official registry and do not grant Edu
Hub eligibility or create canonical identities.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SEED = HERE / "seeds" / "cognia-registry-verification-queue-2026-09-15.json"


def stable_id(name: str) -> str:
    digest = hashlib.sha256(name.casefold().encode("utf-8")).hexdigest()[:20]
    return f"cognia-registry-query:{digest}"


def build(seed_path: Path, output_dir: Path) -> dict:
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    records = data["records"]
    assert data["records_count"] == len(records)
    assert data["rules"]["official_registry_verification_required"] is True
    assert data["rules"]["primary_claim_auto_accreditation"] is False
    assert data["rules"]["cognia_auto_international_eligibility"] is False

    names = [row["query_name"] for row in records]
    if len(names) != len(set(names)):
        raise ValueError("duplicate Cognia registry query_name")

    queue = []
    for row in records:
        claim = row["primary_claim_state"]
        if claim not in {"claims_cognia_accredited", "cognia_engagement_review_observed"}:
            raise ValueError(f"unsupported primary_claim_state: {claim}")
        queue.append(
            {
                "review_id": stable_id(row["query_name"]),
                "query_name": row["query_name"],
                "primary_url": row["primary_url"],
                "primary_claim_state": claim,
                "location_hint": row.get("location_hint"),
                "identity_note": row.get("identity_note"),
                "cognia_registry_url": data["registry_url"],
                "official_registry_verification_state": "pending",
                "accreditation_confirmed_from_cognia": False,
                "international_eligibility_granted": False,
                "canonical_identity_created": False,
                "automatic_merge_performed": False,
                "database_mutation_performed": False,
                "public_projection_performed": False,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    queue_path = output_dir / "cognia-registry-verification-queue.jsonl"
    with queue_path.open("w", encoding="utf-8") as handle:
        for row in queue:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": data["work_package"],
        "snapshot_date": data["snapshot_date"],
        "registry_url": data["registry_url"],
        "queue_rows": len(queue),
        "institution_primary_accreditation_claims": sum(
            1 for row in queue if row["primary_claim_state"] == "claims_cognia_accredited"
        ),
        "engagement_review_only_rows": sum(
            1 for row in queue if row["primary_claim_state"] == "cognia_engagement_review_observed"
        ),
        "official_registry_verified_rows": 0,
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "registry_access_note": data["registry_access_note"],
        "output": queue_path.name,
    }
    (output_dir / "cognia-registry-verification-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/international/cognia-registry-verification"),
    )
    args = parser.parse_args()
    build(args.seed, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
