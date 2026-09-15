#!/usr/bin/env python3
"""Discover likely international-education places in Egypt from Overture Maps.

Overture Places is supporting identity/geography discovery only. The current
2026-08-19.0 public Places release is queried directly from the official AWS
GeoParquet distribution with an Egypt bounding box and education/name signals.
Rows are retained as source candidates and are never used to grant eligibility,
create identities, merge records, mutate a database or create public output.
"""
from __future__ import annotations

import argparse
import json
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import duckdb

RELEASE = "2026-08-19.0"
SOURCE_PATH = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*"
EGYPT_BBOX = (24.5, 22.0, 37.0, 31.9)
NAME_SIGNALS = [
    "international", "american", "british", "english", "french", "francais", "français",
    "german", "deutsch", "canadian", "pakistan", "indian", "japanese", "korean",
    "italian", "spanish", "swiss", "baccalaureate", "choueifat", "sabis", "montessori",
]
CATEGORY_SIGNALS = ["school", "university", "college", "education"]


def compact(value: object) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split()).strip()
    return text or None


def normalize_name(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).casefold()
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def sql_like(column: str, values: list[str]) -> str:
    escaped = [value.replace("'", "''") for value in values]
    return " OR ".join(f"lower(coalesce({column}, '')) LIKE '%{value.casefold()}%'" for value in escaped)


def build(output: Path) -> dict:
    xmin, ymin, xmax, ymax = EGYPT_BBOX
    name_filter = sql_like("names.primary", NAME_SIGNALS)
    category_filter = sql_like("categories.primary", CATEGORY_SIGNALS)
    sql = f"""
        SELECT
          id,
          names.primary AS name,
          categories.primary AS category,
          confidence,
          websites,
          emails,
          phones,
          addresses,
          sources,
          geometry,
          bbox.xmin AS longitude,
          bbox.ymin AS latitude
        FROM read_parquet('{SOURCE_PATH}', filename=true, hive_partitioning=1)
        WHERE bbox.xmin BETWEEN {xmin} AND {xmax}
          AND bbox.ymin BETWEEN {ymin} AND {ymax}
          AND ({category_filter})
          AND ({name_filter})
        ORDER BY lower(names.primary), id
    """

    con = duckdb.connect(database=":memory:")
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")
    con.execute("SET s3_region='us-west-2'")
    con.execute("SET threads=4")
    rows = con.execute(sql).fetchall()
    columns = [item[0] for item in con.description]
    con.close()

    records: list[dict] = []
    seen_ids = set()
    for values in rows:
        row = dict(zip(columns, values))
        source_id = str(row["id"])
        if source_id in seen_ids:
            continue
        seen_ids.add(source_id)
        name = compact(row.get("name"))
        if not name:
            continue
        records.append({
            "overture_id": source_id,
            "name": name,
            "name_normalized": normalize_name(name),
            "category": compact(row.get("category")),
            "confidence": row.get("confidence"),
            "longitude": row.get("longitude"),
            "latitude": row.get("latitude"),
            "websites_json": compact(row.get("websites")),
            "emails_json": compact(row.get("emails")),
            "phones_json": compact(row.get("phones")),
            "addresses_json": compact(row.get("addresses")),
            "sources_json": compact(row.get("sources")),
            "source_role": "supporting_identity_geography_discovery_only",
            "international_eligibility_granted": False,
        })

    by_name: dict[str, list[str]] = {}
    for record in records:
        by_name.setdefault(record["name_normalized"], []).append(record["overture_id"])
    duplicate_groups = {name: ids for name, ids in by_name.items() if len(ids) > 1}

    result = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_overture_egypt_international_education_supporting_discovery",
        "source": "Overture Maps Places",
        "release": RELEASE,
        "source_path": SOURCE_PATH,
        "coverage_bbox": list(EGYPT_BBOX),
        "name_signals": NAME_SIGNALS,
        "category_signals": CATEGORY_SIGNALS,
        "record_count": len(records),
        "duplicate_normalized_name_group_count": len(duplicate_groups),
        "duplicate_normalized_name_groups": duplicate_groups,
        "records": records,
        "rules": {
            "overture_auto_international_eligibility": False,
            "overture_auto_identity_merge": False,
            "overture_auto_canonical_creation": False,
            "coordinates_require_identity_review_before_attachment": True,
            "current_primary_or_authoritative_resourcing_required_for_useful_gap_leads": True,
            "database_mutation": False,
            "public_projection": False,
        },
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({
        "release": RELEASE,
        "record_count": len(records),
        "duplicate_normalized_name_group_count": len(duplicate_groups),
    }, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/international/overture-egypt-international-education/overture-egypt-international-education.json"),
    )
    args = parser.parse_args()
    build(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
