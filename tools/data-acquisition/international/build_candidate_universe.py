#!/usr/bin/env python3
"""Build the D2.1 candidate universe without performing canonical merges.

Inputs are source-shaped evidence rows already acquired under the EDU-DATA-2
source policy. The builder normalizes names only to create *review hints* and
coverage metrics. It never claims a unique institution count, never merges
records, and never promotes anything to public data.

Supporting lead files may be supplied, but each row must explicitly declare its
storage policy. Sources whose terms prohibit systematic storage (for example
Edarabia) should contribute only a URL/reference lead that is then re-sourced
from an official/authoritative source before factual fields are retained.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
NON_ALNUM = re.compile(r"[^\w\u0600-\u06ff]+", re.UNICODE)


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def compact(value: object) -> str:
    return " ".join(str(value or "").split())


def normalize_ar(value: object) -> str:
    text = unicodedata.normalize("NFKC", compact(value))
    text = ARABIC_DIACRITICS.sub("", text)
    table = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ؤ": "و", "ئ": "ي", "ة": "ه"})
    text = text.translate(table)
    text = NON_ALNUM.sub(" ", text)
    return " ".join(text.split()).casefold()


def normalize_en(value: object) -> str:
    text = unicodedata.normalize("NFKD", compact(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = NON_ALNUM.sub(" ", text)
    tokens = [t for t in text.casefold().split() if t not in {"the"}]
    return " ".join(tokens)


def discovery_key(row: dict) -> str | None:
    en = normalize_en(row.get("name_en") or row.get("parent_university_en"))
    ar = normalize_ar(row.get("name_ar"))
    if en:
        return f"en:{en}"
    if ar:
        return f"ar:{ar}"
    return None


def row_id(row: dict) -> str:
    source_id = str(row.get("source_id") or "unknown")
    source_record_id = str(row.get("source_record_id") or "")
    seed = source_id + "\0" + source_record_id + "\0" + compact(row.get("name_en") or row.get("name_ar"))
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]


def validate_supporting_lead(row: dict) -> None:
    required = ("source_id", "source_url", "lead_state", "storage_policy")
    missing = [key for key in required if not row.get(key)]
    if missing:
        raise ValueError(f"supporting lead missing {missing}: {row}")
    if row["lead_state"] not in {"reference_only", "official_site_candidate", "supporting_candidate"}:
        raise ValueError(f"unsupported lead_state: {row['lead_state']}")
    if row["source_id"] == "edarabia_egypt" and row["lead_state"] != "reference_only":
        raise ValueError("Edarabia must remain reference_only unless written reuse permission is recorded")


def build(authoritative: Path, lead_files: list[Path], output_dir: Path) -> dict:
    rows = read_jsonl(authoritative)
    source_kind = {id(row): "authoritative_or_primary" for row in rows}

    for lead_path in lead_files:
        for lead in read_jsonl(lead_path):
            validate_supporting_lead(lead)
            rows.append(lead)
            source_kind[id(lead)] = "supporting_lead"

    universe: list[dict] = []
    gaps: list[dict] = []
    key_groups: dict[str, list[dict]] = defaultdict(list)
    source_counts: Counter[str] = Counter()
    state_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()

    for row in rows:
        source_id = str(row.get("source_id") or "unknown")
        source_counts[source_id] += 1
        scope_state = str(row.get("scope_state") or row.get("lead_state") or "candidate")
        state_counts[scope_state] += 1
        family = str(row.get("entity_family") or "unknown")
        family_counts[family] += 1
        key = discovery_key(row)
        record = {
            "discovery_record_id": row_id(row),
            "source_id": source_id,
            "source_record_id": row.get("source_record_id"),
            "source_url": row.get("source_url"),
            "source_snapshot_date": row.get("source_snapshot_date"),
            "entity_family": row.get("entity_family"),
            "institution_type": row.get("institution_type"),
            "name_en": row.get("name_en") or row.get("parent_university_en"),
            "name_ar": row.get("name_ar"),
            "city": row.get("city"),
            "scope_state": row.get("scope_state"),
            "scope_class": row.get("scope_class"),
            "lead_state": row.get("lead_state"),
            "storage_policy": row.get("storage_policy"),
            "normalized_name_en": normalize_en(row.get("name_en") or row.get("parent_university_en")) or None,
            "normalized_name_ar": normalize_ar(row.get("name_ar")) or None,
            "discovery_cluster_key": key,
            "cluster_is_review_hint_only": True,
            "record_role": source_kind[id(row)],
            "canonical_identity_created": False,
            "automatic_merge_performed": False,
        }
        universe.append(record)
        if key:
            key_groups[key].append(record)

        if record["record_role"] == "authoritative_or_primary":
            missing_locales = []
            if not record["name_en"]:
                missing_locales.append("en-EG")
            if not record["name_ar"]:
                missing_locales.append("ar-EG")
            if missing_locales:
                gaps.append(
                    {
                        "discovery_record_id": record["discovery_record_id"],
                        "source_id": source_id,
                        "source_record_id": record["source_record_id"],
                        "name_en": record["name_en"],
                        "name_ar": record["name_ar"],
                        "missing_name_locales": missing_locales,
                        "required_action": "find_official_localized_name_or_create_reviewed_translation_transliteration",
                        "automatic_translation_allowed": False,
                    }
                )

    overlap_groups = []
    for key, group in sorted(key_groups.items()):
        distinct_sources = sorted({str(row["source_id"]) for row in group})
        if len(group) > 1 and len(distinct_sources) > 1:
            overlap_groups.append(
                {
                    "discovery_cluster_key": key,
                    "source_record_count": len(group),
                    "sources": distinct_sources,
                    "decision": "needs_review",
                    "canonical_merge_authorized": False,
                }
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "candidate-universe.jsonl").open("w", encoding="utf-8") as handle:
        for row in universe:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    with (output_dir / "bilingual-name-gaps.jsonl").open("w", encoding="utf-8") as handle:
        for row in gaps:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    with (output_dir / "discovery-overlap-review.jsonl").open("w", encoding="utf-8") as handle:
        for row in overlap_groups:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_candidate_universe_completion",
        "source_record_count": len(universe),
        "source_counts": dict(sorted(source_counts.items())),
        "scope_or_lead_state_counts": dict(sorted(state_counts.items())),
        "entity_family_counts": dict(sorted(family_counts.items())),
        "english_name_present": sum(1 for row in universe if row.get("name_en")),
        "arabic_name_present": sum(1 for row in universe if row.get("name_ar")),
        "bilingual_name_gap_count": len(gaps),
        "cross_source_overlap_review_groups": len(overlap_groups),
        "unique_institutions_claimed": None,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "public_projection_rows_created": 0,
        "database_mutation_performed": False,
        "presentation_runtime_dependency": None,
    }
    (output_dir / "candidate-universe-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--authoritative",
        type=Path,
        default=Path("artifacts/international/authoritative-source-candidates.jsonl"),
    )
    parser.add_argument("--lead-file", action="append", type=Path, default=[])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/international/candidate-universe"),
    )
    args = parser.parse_args()
    build(args.authoritative, args.lead_file, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
