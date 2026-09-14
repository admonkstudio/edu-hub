#!/usr/bin/env python3
"""Apply explicit primary/recognized evidence review to British Council discovery leads.

British Council Partner School status is only discovery/contact evidence. This
review layer may change the scope state of an exact discovered lead only when a
checked-in decision supplies high-confidence primary/recognized evidence for both
international-model eligibility and non-public/private-independent scope.

No canonical identities are created, no fuzzy matching is performed, and no
runtime/public data is mutated.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = Path("artifacts/international/british-council-browser-discovery/british-council-browser-leads.jsonl")
DEFAULT_REVIEW = HERE / "seeds" / "british-council-primary-scope-review-2026-09-15-batch1.json"
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


def apply(input_path: Path, review_path: Path, output_dir: Path) -> dict:
    leads = load_jsonl(input_path)
    review = load_json(review_path)
    decisions = review.get("records") or []

    if len(leads) != 35:
        raise AssertionError(f"expected accepted 35-row British Council discovery batch, found {len(leads)}")
    if review.get("records_count") != len(decisions) or len(decisions) != 2:
        raise AssertionError("first British Council primary review batch must contain exactly two decisions")
    safety = review.get("safety") or {}
    if safety.get("partner_status_treated_as_international_eligibility") is not False:
        raise AssertionError("Partner School status may not establish eligibility")
    if safety.get("unreviewed_british_council_leads_promoted") is not False:
        raise AssertionError("unreviewed British Council leads may not be promoted")
    if safety.get("automatic_identity_creation_performed") is not False:
        raise AssertionError("scope review must not create canonical identities")
    if safety.get("automatic_merges_performed") != 0:
        raise AssertionError("scope review must perform zero automatic merges")

    by_id = {row["source_record_id"]: row for row in leads}
    if len(by_id) != len(leads):
        raise AssertionError("duplicate British Council source_record_id in discovery input")

    reviewed_ids: set[str] = set()
    evidence_rows: list[dict] = []
    for decision in decisions:
        source_record_id = decision["source_record_id"]
        if source_record_id in reviewed_ids:
            raise AssertionError(f"duplicate British Council review target: {source_record_id}")
        reviewed_ids.add(source_record_id)
        target = by_id.get(source_record_id)
        if target is None:
            raise AssertionError(f"review target missing from accepted British Council discovery batch: {source_record_id}")
        if target.get("name_en") != decision["source_name"]:
            raise AssertionError(
                f"British Council discovery name drift for {source_record_id}: "
                f"expected={decision['source_name']!r} current={target.get('name_en')!r}"
            )
        if decision.get("decision") != "eligible" or decision.get("decision_confidence") != "high":
            raise AssertionError("this primary review batch accepts only high-confidence eligible decisions")
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
            "eligibility_review_batch_id": review["batch_id"],
            "eligibility_decision_confidence": decision["decision_confidence"],
            "eligibility_evidence_urls": evidence_urls,
            "eligibility_basis": list(decision["eligibility_basis"]),
            "eligibility_review_note": decision["review_note"],
            "partner_status_was_not_eligibility_basis": True,
        })
        evidence_rows.append({
            "source_record_id": source_record_id,
            "source_name": decision["source_name"],
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
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_british_council_primary_scope_review",
        "source_rows": len(leads),
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
    if summary["eligible_rows"] != 2 or summary["remaining_supporting_candidates"] != 33:
        raise AssertionError(f"unexpected first primary-review result: {summary}")
    (output_dir / "british-council-primary-scope-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    apply(args.input, args.review, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
