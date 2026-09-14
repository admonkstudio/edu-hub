#!/usr/bin/env python3
"""Create review-only identity/campus match proposals across EDU-DATA-2 sources.

This deliberately never auto-accepts a merge. It finds plausible duplicate
source rows so a human can decide whether they represent the same institution,
a campus of the same institution, or unrelated entities with similar names.

Version 2 deliberately treats curriculum/model words such as British, English,
American and International as non-distinctive. A fuzzy proposal now needs at
least one distinctive shared token unless the full normalized name, an official
identifier or a normalized domain is an exact match. This prevents clusters of
unrelated international schools from being proposed merely because they share
model words.
"""
from __future__ import annotations

import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

STOP = {
    "school", "schools", "international", "college", "university", "the",
    "of", "in", "egypt", "branch", "lycee", "ecole", "de", "du", "la",
    "le", "mlf", "cairo", "alexandria", "british", "english", "american",
    "german", "french", "bilingual", "academy", "education",
}


def norm(value: object) -> str:
    text = " ".join(str(value or "").split()).casefold()
    text = text.replace("é", "e").replace("è", "e").replace("ê", "e")
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي")
    text = re.sub(r"[^\w\u0600-\u06ff]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def tokens(value: object) -> set[str]:
    return {token for token in norm(value).split() if token not in STOP and len(token) > 1}


def display_name(row: dict) -> str:
    return str(row.get("name_en") or row.get("name_ar") or row.get("parent_university_en") or "")


def similarity(left: dict, right: dict) -> tuple[float, dict]:
    a = norm(display_name(left))
    b = norm(display_name(right))
    exact_name = bool(a and b and a == b)
    seq = SequenceMatcher(None, a, b).ratio() if a and b else 0.0
    ta, tb = tokens(a), tokens(b)
    shared = ta & tb
    jaccard = len(shared) / len(ta | tb) if ta or tb else 0.0

    exact_official_id = bool(
        left.get("official_identifier")
        and right.get("official_identifier")
        and str(left.get("official_identifier")).casefold() == str(right.get("official_identifier")).casefold()
    )
    same_domain = bool(
        left.get("normalized_domain")
        and right.get("normalized_domain")
        and left.get("normalized_domain") == right.get("normalized_domain")
    )

    # Generic international-school vocabulary is not enough to create a review
    # proposal. Exact full names, official IDs and domains remain strong signals.
    distinctive_overlap = bool(shared)
    if not (exact_name or exact_official_id or same_domain or distinctive_overlap):
        score = 0.0
        generic_only_rejected = True
    else:
        lexical_score = seq * 0.45 + jaccard * 0.55
        score = max(
            lexical_score,
            0.995 if exact_name else 0.0,
            0.99 if exact_official_id else 0.0,
            0.96 if same_domain else 0.0,
        )
        generic_only_rejected = False

    return min(score, 1.0), {
        "sequence_ratio": round(seq, 5),
        "token_jaccard": round(jaccard, 5),
        "shared_distinctive_tokens": sorted(shared),
        "exact_normalized_name": exact_name,
        "exact_official_identifier": exact_official_id,
        "same_normalized_domain": same_domain,
        "generic_only_rejected": generic_only_rejected,
    }


def plan(input_jsonl: Path, output_jsonl: Path, threshold: float) -> dict:
    rows = [json.loads(line) for line in input_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    proposals = []
    for i, left in enumerate(rows):
        for right in rows[i + 1 :]:
            if left.get("source_id") == right.get("source_id"):
                continue
            if left.get("entity_family") != right.get("entity_family"):
                continue
            score, evidence = similarity(left, right)
            if score < threshold:
                continue
            proposals.append({
                "left_source_id": left.get("source_id"),
                "left_source_record_id": left.get("source_record_id"),
                "left_name": display_name(left),
                "right_source_id": right.get("source_id"),
                "right_source_record_id": right.get("source_record_id"),
                "right_name": display_name(right),
                "score": round(score, 5),
                "decision": "needs_review",
                "possible_relationships": ["same_institution", "same_group_different_campus", "unrelated"],
                "evidence": evidence,
                "matcher_version": "edu-data-2-name-v2",
            })

    proposals.sort(key=lambda row: (-row["score"], row["left_name"], row["right_name"]))
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with output_jsonl.open("w", encoding="utf-8") as handle:
        for row in proposals:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "source_rows_compared": len(rows),
        "proposal_count": len(proposals),
        "threshold": threshold,
        "matcher_version": "edu-data-2-name-v2",
        "auto_accept_count": 0,
        "accepted_count": 0,
        "canonical_merges_performed": 0,
        "public_promotion_performed": False,
        "output": str(output_jsonl),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("artifacts/international/import-package/staging-candidates.jsonl"))
    ap.add_argument("--output", type=Path, default=Path("artifacts/international/import-package/identity-review-proposals.jsonl"))
    ap.add_argument("--threshold", type=float, default=0.58)
    args = ap.parse_args()
    plan(args.input, args.output, args.threshold)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
