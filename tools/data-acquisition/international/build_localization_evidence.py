#!/usr/bin/env python3
"""Build reviewed D2.3 localization evidence without mutating canonical data.

Only institution-origin Arabic name evidence is emitted. Historical official
names remain flagged for current revalidation instead of being silently treated
as current. The output is a review package, not an auto-localization pipeline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SEED = HERE / "seeds" / "official-arabic-name-evidence-2026-09-15.json"


def stable_id(name_en: str, source_url: str) -> str:
    digest = hashlib.sha256(f"{name_en}\0{source_url}".encode("utf-8")).hexdigest()[:20]
    return f"official-ar-name:{digest}"


def build(seed_path: Path, output_dir: Path) -> dict:
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    records = seed["records"]
    assert seed["records_count"] == len(records) == 4
    assert all(row["locale"] == "ar-EG" for row in records)
    assert all(row["localization_origin"] == "official_institution_source" for row in records)
    assert len({row["name_en"] for row in records}) == len(records)

    rows = []
    for row in records:
        rows.append(
            {
                "localization_evidence_id": stable_id(row["name_en"], row["source_url"]),
                "name_en": row["name_en"],
                "name_ar": row["name_ar"],
                "locale": row["locale"],
                "localization_origin": row["localization_origin"],
                "source_url": row["source_url"],
                "source_observed_date": row["source_observed_date"],
                "source_recency_state": row["source_recency_state"],
                "review_state": row["review_state"],
                "canonical_localization_created": False,
                "automatic_translation_performed": False,
                "public_promotion_performed": False,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "official-arabic-name-evidence.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.3_official_arabic_name_evidence",
        "records": len(rows),
        "current_official_name_evidence": sum(
            1 for row in rows if row["source_recency_state"] == "current"
        ),
        "historical_official_name_evidence": sum(
            1 for row in rows if row["source_recency_state"].startswith("historical_")
        ),
        "canonical_localizations_created": 0,
        "automatic_translations_performed": 0,
        "public_projection_rows_created": 0,
        "database_mutation_performed": False,
        "output": output_path.name,
    }
    (output_dir / "localization-evidence-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/international/localization-evidence"),
    )
    args = parser.parse_args()
    build(args.seed, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
