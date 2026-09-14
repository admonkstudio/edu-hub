#!/usr/bin/env python3
"""Apply explicit primary/recognized evidence review to British Council discovery leads.

British Council Partner School status is only discovery/contact evidence. This
review layer may change the scope state of an exact discovered lead only when a
checked-in decision supplies high-confidence primary/recognized evidence for both
international-model eligibility and non-public/private-independent scope.

Review batches are additive. No canonical identities are created, no fuzzy
matching is performed, and no runtime/public data is mutated.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = Path("artifacts/international/british-council-browser-discovery/british-council-browser-leads.jsonl")
DEFAULT_REVIEW_GLOB = "british-council-primary-scope-review-*.json"
DEFAULT_OUTPUT_DIR = Path("artifacts/international/british-council-primary-scope-review")
KNOWN_CURRICULA = {"american", "british", "canadian", "french", "german", "ib", "egyptian_national"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def discover_reviews() -> list[Path]:
    paths = sorted((HERE / "seeds").glob(DEFAULT_REVIEW_GLOB))
    if not paths:
        raise AssertionError("no British Council primary scope review batches found")
    return paths


def apply(input_path: Path, review_paths: list[Path], output_dir: Path) -> dict:
    leads = load_jsonl(input_path)
    if not leads:
        raise AssertionError("British Council discovery input is empty")

    by_id = {row["source_record_id"]: row for row in leads}
    if len(by_id) != len(leads):
        raise AssertionError("duplicate British Council source_record_id in discovery input")

    reviewed_ids: set[str] = set()
    evidence_rows: list[dict] = []
    batch_details: list[dict] = []
    seen_batch_ids: set[str] = set()

    for review_path in review_paths:
        review = load_json(review_path)
        decisions = review.get("records") or []
        if review.get("records_count") != len(decisions):
            raise AssertionError(f"records_count mismatch in {review_path.name}")
        if not decisions:
            raise AssertionError(f"British Council primary review batch is empty: {review_path.name}")
        batch_id = str(review.get("batch_id") or review_path.stem)
        if batch_id in seen_batch_ids:
            raise AssertionError(f"duplicate British Council primary review batch_id: {batch_id}")
        seen_batch_ids.add(batch_id)

        safety = review.get("safety") or {}
        if safety.get("partner_status_treated_as_international_eligibility") is not False:
            raise AssertionError("Partner School status may not establish eligibility")
        if safety.get("unreviewed_british_council_leads_promoted") is not False:
            raise AssertionError("unreviewed British Council leads may not be promoted")
        if safety.get("automatic_identity_creation_performed") is not False:
            raise AssertionError("scope review must not create canonical identities")
        if safety.get("automatic_merges_performed") != 0:
            raise AssertionError("scope review must perform zero automatic merges")
        if safety.get("canonical_database_rows_written") != 0:
            raise AssertionError("scope review must perform zero canonical database writes")
        if safety.get("public_projection_rows_created") != 0:
            raise AssertionError("scope review must perform zero public projection")

        for decision in decisions:
            source_record_id = decision["source_record_id"]
            if source_record_id in reviewed_ids:
                raise AssertionError(f"duplicate British Council review target across batches: {source_record_id}")
            reviewed_ids.add(source_record_id)
            target = by_id.get(source_record_id)
            if target is None:
                raise AssertionError(f"review target missing from accepted British Council discovery rows: {source_record_id}")
            if target.get("name_en") != decision["source_name"]:
                raise AssertionError(
                    f"British Council discovery name drift for {source_record_id}: "
                    f"expected={decision['source_name']!r} current={target.get('name_en')!r}"
                )
            if decision.get("decision") != "eligible" or decision.get("decision_confidence") != "high":
                raise AssertionError("primary review currently accepts only high-confidence eligible decisions")
            if decision.get("ownership_scope") != "private_independent":
                raise AssertionError("eligible discovery requires explicit private/independent scope")
            evidence_urls = list(decision.get("evidence_urls") or [])
            if len(evidence_urls) < 2:
                raise AssertionError("eligible discovery requires at least two evidence URLs")
            curricula = list(decision.get("curriculum_codes") or [])
            unknown = sorted(set(curricula) - KNOWN_CURRICULA)
            if unknown:
                raise AssertionError(f"unknown curriculum codes for {source_record_id}: {unknown}")
            if not decision.get("eligibility_basis"):
                raise AssertionError("eligible discovery requires explicit eligibility basis")

            target.update({
                "scope_state": "eligible",
                "scope_class": decision["scope_class"],
                "ownership_scope": decision["ownership_scope"],
                "curriculum_codes": curricula,
                "website_reference": decision.get("website") or target.get("website_reference"),
                "eligibility_pending": None,
                "auto_eligibility": False,
                "eligibility_review_state": "reviewed_primary_or_recognized_evidence",
                "eligibility_review_batch_id": batch_id,
                "eligibility_decision_confidence": decision["decision_confidence"],
                "eligibility_evidence_urls": evidence_urls,
                "eligibility_basis": list(decision["eligibility_basis"]),
                "eligibility_review_note": decision["review_note"],
                "partner_status_was_not_eligibility_basis": True,
            })
            evidence_rows.append({
                "source_record_id": source_record_id,
                "source_name": decision["source_name"],
                "review_batch_id": batch_id,
                "decision": decision["decision"],
                "decision_confidence": decision["decision_confidence"],
                "ownership_scope": decision["ownership_scope"],
                "curriculum_codes": curricula,
                "evidence_urls": evidence_urls,
                "eligibility_basis": list(decision["eligibility_basis"]),
                "review_note": decision["review_note"],
                "canonical_identity_created": False,
                "automatic_merge_performed": False,
                "database_mutation_performed": False,
                "public_promotion_performed": False,
            })

        batch_details.append({
            "batch_id": batch_id,
            "seed": review_path.name,
            "reviewed_rows": len(decisions),
        })

    # Every non-target row must remain an unqualified supporting candidate.
    for row in leads:
        if row["source_record_id"] in reviewed_ids:
            continue
        if row.get("scope_state") is not None:
            raise AssertionError(f"unreviewed British Council lead unexpectedly has scope_state: {row['source_record_id']}")
        if row.get("lead_state") != "supporting_candidate":
            raise AssertionError(f"unreviewed British Council lead drifted from supporting_candidate: {row['source_record_id']}")
        if row.get("auto_eligibility") is not False:
            raise AssertionError(f"unreviewed British Council lead must keep auto_eligibility=false: {row['source_record_id']}")

    output_dir.mkdir(parents=True, exist_ok=True)
    reviewed_path = output_dir / "british-council-leads-with-primary-review.jsonl"
    evidence_path = output_dir / "primary-scope-review-evidence.jsonl"
    write_jsonl(reviewed_path, leads)
    write_jsonl(evidence_path, evidence_rows)

    summary = {
        "schema_version": 2,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_british_council_primary_scope_review",
        "source_rows": len(leads),
        "review_batches": len(batch_details),
        "review_batch_details": batch_details,
        "reviewed_rows": len(reviewed_ids),
        "eligible_rows": sum(1 for row in leads if row.get("scope_state") == "eligible"),
        "remaining_supporting_candidates": sum(
            1 for row in leads if row.get("scope_state") is None and row.get("lead_state") == "supporting_candidate"
        ),
        "partner_status_treated_as_international_eligibility": False,
        "automatic_identity_creation_performed": False,
        "automatic_merges_performed": 0,
        "canonical_database_rows_written": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
        "outputs": {
            "reviewed_leads": reviewed_path.name,
            "review_evidence": evidence_path.name,
        },
    }
    if summary["eligible_rows"] != len(reviewed_ids):
        raise AssertionError(f"reviewed rows and eligible rows diverged: {summary}")
    if summary["remaining_supporting_candidates"] != len(leads) - len(reviewed_ids):
        raise AssertionError(f"unreviewed candidate count drifted: {summary}")

    (output_dir / "british-council-primary-scope-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--review", dest="reviews", action="append", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    review_paths = args.reviews if args.reviews else discover_reviews()
    apply(args.input, review_paths, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
