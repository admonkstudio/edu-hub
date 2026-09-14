#!/usr/bin/env python3
"""Build review-only higher-education reconciliation proposals.

The current scope reconciles SCU <-> MOHESR private-institute identities and
preserves the official MOHESR technological-college -> technical-institute
hierarchy as source-backed relationship proposals.

No identity or relationship is accepted automatically and this tool never
writes to edu_core or any public projection.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
import uuid
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

NAMESPACE = uuid.UUID("1dfb8e15-79ae-48f5-9db6-09182a95db36")
TASHKEEL_RE = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
PUNCT_RE = re.compile(r"[^\w\u0600-\u06ff]+", re.UNICODE)
GENERIC_TOKENS = {"المعهد", "معهد", "العالي", "العالى", "الخاصة", "الخاص", "ل", "لل", "في", "فى"}


def clean(value: object) -> str:
    if value is None:
        return ""
    return " ".join(unicodedata.normalize("NFKC", str(value)).split())


def normalize_arabic(value: object) -> str:
    value = clean(value).replace("ـ", "")
    value = TASHKEEL_RE.sub("", value)
    value = value.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي"}))
    value = PUNCT_RE.sub(" ", value)
    return clean(value).casefold()


def compact_tokens(value: str) -> str:
    tokens = [tok for tok in normalize_arabic(value).split() if tok not in GENERIC_TOKENS]
    return " ".join(tokens)


def load_scu(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if row.get("higher_ed_category") == "accredited_private_institute"]


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise SystemExit(f"{path}:{line_no}: expected object")
            rows.append(value)
    return rows


def group_mohesr(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        normalized = row.get("normalized_name_ar") or normalize_arabic(row.get("name_raw"))
        if normalized:
            grouped[normalized].append(row)
    out = []
    for normalized, members in sorted(grouped.items()):
        names = sorted({clean(m.get("name_raw")) for m in members if clean(m.get("name_raw"))})
        categories = sorted({clean((m.get("payload") or {}).get("category_raw")) for m in members if clean((m.get("payload") or {}).get("category_raw"))})
        out.append({
            "normalized_name_ar": normalized,
            "display_names": names,
            "category_memberships": categories,
            "source_record_ids": sorted({m.get("source_record_id") for m in members if m.get("source_record_id")}),
            "source_occurrences": len(members),
        })
    return out


def group_scu(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        normalized = normalize_arabic(row.get("name_ar"))
        if normalized:
            grouped[normalized].append(row)
    out = []
    for normalized, members in sorted(grouped.items()):
        out.append({
            "normalized_name_ar": normalized,
            "display_names": sorted({clean(m.get("name_ar")) for m in members if clean(m.get("name_ar"))}),
            "seed_ids": sorted({m.get("seed_id") for m in members if m.get("seed_id")}),
            "source_rows": len(members),
        })
    return out


def similarity(left: str, right: str) -> float:
    left_compact = compact_tokens(left)
    right_compact = compact_tokens(right)
    if not left_compact or not right_compact:
        return 0.0
    return SequenceMatcher(None, left_compact, right_compact).ratio()


def reconcile(scu_rows: list[dict], mohesr_rows: list[dict], fuzzy_threshold: float = 0.90) -> tuple[list[dict], list[dict], dict]:
    scu = group_scu(scu_rows)
    mohesr = group_mohesr(mohesr_rows)
    scu_by_name = {row["normalized_name_ar"]: row for row in scu}
    exact = []
    review = []
    matched_scu = set()
    matched_moh = set()

    for m in mohesr:
        s = scu_by_name.get(m["normalized_name_ar"])
        if not s:
            continue
        proposal_key = "exact|" + m["normalized_name_ar"]
        exact.append({
            "proposal_id": str(uuid.uuid5(NAMESPACE, proposal_key)),
            "match_type": "exact_normalized_name",
            "decision": "unreviewed",
            "automatic_acceptance": False,
            "core_mutation_allowed": False,
            "normalized_name_ar": m["normalized_name_ar"],
            "mohesr": m,
            "scu": s,
        })
        matched_scu.add(s["normalized_name_ar"])
        matched_moh.add(m["normalized_name_ar"])

    unresolved_moh = [m for m in mohesr if m["normalized_name_ar"] not in matched_moh]
    unresolved_scu = [s for s in scu if s["normalized_name_ar"] not in matched_scu]

    for m in unresolved_moh:
        ranked = sorted(
            ((similarity(m["normalized_name_ar"], s["normalized_name_ar"]), s) for s in unresolved_scu),
            key=lambda item: item[0], reverse=True
        )[:3]
        candidates = [
            {"score": round(score, 5), "scu": s}
            for score, s in ranked if score >= fuzzy_threshold
        ]
        if candidates:
            review.append({
                "task_type": "cross_registry_identity_match",
                "status": "open",
                "decision": "needs_review",
                "automatic_acceptance": False,
                "mohesr": m,
                "candidate_scu_matches": candidates,
            })

    fuzzy_edges = sum(len(task["candidate_scu_matches"]) for task in review)
    report = {
        "schema_version": 3,
        "scu_private_source_rows": len(scu_rows),
        "scu_private_distinct_normalized_names": len(scu),
        "mohesr_sector_occurrences": len(mohesr_rows),
        "mohesr_distinct_normalized_names": len(mohesr),
        "mohesr_duplicate_sector_occurrences": len(mohesr_rows) - len(mohesr),
        "exact_normalized_name_proposals": len(exact),
        "mohesr_unresolved_after_exact": len(unresolved_moh),
        "scu_unresolved_after_exact": len(unresolved_scu),
        "fuzzy_similarity_threshold": fuzzy_threshold,
        "fuzzy_review_tasks": len(review),
        "fuzzy_candidate_edges": fuzzy_edges,
        "mohesr_without_fuzzy_suggestion": len(unresolved_moh) - len(review),
        "unmatched_mohesr_distinct_names": len(unresolved_moh),
        "unmatched_scu_distinct_names": len(unresolved_scu),
        "automatic_identity_acceptances": 0,
        "automatic_relationship_acceptances": 0,
        "edu_core_rows_created": 0,
        "core_mutation_performed": False,
        "public_promotion_performed": False,
        "notes": [
            "MOHESR sector occurrences are grouped by normalized name before cross-registry comparison.",
            "Exact normalized-name matches are proposals only and still require review before canonical merge.",
            "Fuzzy matches are suggestions only and never reduce unresolved identity counts until a review decision is recorded.",
            "The default fuzzy threshold is intentionally conservative to favor review precision over recall.",
            "Unresolved counts are acquisition/reconciliation gaps, not proof that one source is wrong.",
        ],
    }
    return exact, review, report


def build_technical_hierarchy(parents: list[dict], institutes: list[dict]) -> tuple[list[dict], list[dict], dict]:
    """Create review-only parent/child proposals from the official MOHESR hierarchy."""
    parent_ids = [clean(row.get("source_record_id")) for row in parents]
    child_ids = [clean(row.get("source_record_id")) for row in institutes]
    duplicate_parent_ids = sorted({value for value in parent_ids if value and parent_ids.count(value) > 1})
    duplicate_child_ids = sorted({value for value in child_ids if value and child_ids.count(value) > 1})
    parent_by_id = {clean(row.get("source_record_id")): row for row in parents if clean(row.get("source_record_id"))}

    proposals: list[dict] = []
    review: list[dict] = []
    for child in institutes:
        child_id = clean(child.get("source_record_id"))
        parent_id = clean(child.get("parent_source_record_id"))
        parent = parent_by_id.get(parent_id)
        if not child_id or not parent_id or parent is None:
            review.append({
                "task_type": "technical_hierarchy_integrity_review",
                "status": "open",
                "decision": "needs_review",
                "automatic_acceptance": False,
                "child_source_record_id": child_id or None,
                "parent_source_record_id": parent_id or None,
                "reason": "missing_child_id" if not child_id else "missing_parent_id" if not parent_id else "unknown_parent_reference",
                "child": child,
            })
            continue

        proposal_key = f"technical-hierarchy|{parent_id}|{child_id}"
        proposals.append({
            "proposal_id": str(uuid.uuid5(NAMESPACE, proposal_key)),
            "task_type": "higher_ed_hierarchy_link",
            "relationship_type": "technological_college_parent",
            "source_authority": "primary_official_registry",
            "decision": "unreviewed",
            "automatic_acceptance": False,
            "core_mutation_allowed": False,
            "parent_source_record_id": parent_id,
            "child_source_record_id": child_id,
            "parent": parent,
            "child": child,
        })

    report = {
        "technical_parent_source_rows": len(parents),
        "technical_parent_distinct_ids": len({value for value in parent_ids if value}),
        "technical_parent_duplicate_ids": len(duplicate_parent_ids),
        "technical_institute_source_rows": len(institutes),
        "technical_institute_distinct_ids": len({value for value in child_ids if value}),
        "technical_institute_duplicate_ids": len(duplicate_child_ids),
        "technical_hierarchy_source_backed_proposals": len(proposals),
        "technical_hierarchy_review_tasks": len(review),
        "technical_hierarchy_invalid_links": len(review),
        "automatic_relationship_acceptances": 0,
        "edu_core_rows_created": 0,
        "core_mutation_performed": False,
        "public_promotion_performed": False,
    }
    return proposals, review, report


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scu-csv", required=True, type=Path)
    parser.add_argument("--mohesr-private", required=True, type=Path)
    parser.add_argument("--mohesr-technical-parents", type=Path)
    parser.add_argument("--mohesr-technical-institutes", type=Path)
    parser.add_argument("--out-dir", default="artifacts/edu-data-1/higher-ed-reconciliation", type=Path)
    parser.add_argument("--fuzzy-threshold", type=float, default=0.90)
    args = parser.parse_args()

    if bool(args.mohesr_technical_parents) != bool(args.mohesr_technical_institutes):
        raise SystemExit("Provide both --mohesr-technical-parents and --mohesr-technical-institutes, or neither")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    exact, review, report = reconcile(load_scu(args.scu_csv), load_jsonl(args.mohesr_private), args.fuzzy_threshold)
    write_jsonl(args.out_dir / "exact_name_proposals.jsonl", exact)
    write_jsonl(args.out_dir / "fuzzy_review_tasks.jsonl", review)

    if args.mohesr_technical_parents and args.mohesr_technical_institutes:
        hierarchy, hierarchy_review, hierarchy_report = build_technical_hierarchy(
            load_jsonl(args.mohesr_technical_parents),
            load_jsonl(args.mohesr_technical_institutes),
        )
        write_jsonl(args.out_dir / "technical_hierarchy_proposals.jsonl", hierarchy)
        write_jsonl(args.out_dir / "technical_hierarchy_review_tasks.jsonl", hierarchy_review)
        report.update(hierarchy_report)
        report["notes"].append(
            "MOHESR technological-college parent links are preserved as source-backed proposals only; no canonical relationship is accepted automatically."
        )

    (args.out_dir / "reconciliation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
