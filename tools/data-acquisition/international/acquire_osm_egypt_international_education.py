#!/usr/bin/env python3
"""Acquire supporting Egypt international-education candidates from OSM.

OpenStreetMap is a supporting discovery/geography source only. This adapter uses
the read-only Overpass API and intentionally narrows the Egypt query to school,
college and university features whose names carry likely international-system
signals. Results may reveal missing institutions, alternate names, campuses and
coordinates, but they never establish Edu Hub eligibility or canonical identity.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
NAME_PATTERN = (
    "international|american|british|english|french|francais|français|german|deutsch|"
    "canadian|pakistan|indian|japanese|korean|italian|spanish|swiss|ib |baccalaureate|"
    "choueifat|sabis|montessori"
)
QUERY = f'''[out:json][timeout:90];
area["ISO3166-1"="EG"]["boundary"="administrative"]->.egypt;
(
  nwr(area.egypt)["amenity"~"^(school|college|university)$"]["name"~"{NAME_PATTERN}",i];
  nwr(area.egypt)["education"~"^(school|college|university)$"]["name"~"{NAME_PATTERN}",i];
);
out center tags;'''


def normalize(value: str | None) -> str | None:
    if value is None:
        return None
    value = unicodedata.normalize("NFKC", value)
    value = " ".join(value.split()).strip()
    return value or None


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(ch for ch in value if ch.isalnum() or ch.isspace())
    return " ".join(value.split())


def fetch(timeout_s: int) -> tuple[dict, str, list[str]]:
    errors: list[str] = []
    headers = {
        "User-Agent": "EduHub-D2.1-supporting-discovery/1.0",
        "Accept": "application/json",
    }
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            response = requests.post(
                endpoint,
                data={"data": QUERY},
                headers=headers,
                timeout=timeout_s,
            )
            if response.status_code == 200:
                return response.json(), endpoint, errors
            errors.append(f"{endpoint}: HTTP {response.status_code}")
        except Exception as exc:
            errors.append(f"{endpoint}: {type(exc).__name__}: {exc}")
        time.sleep(1)
    raise RuntimeError("All Overpass endpoints failed: " + " | ".join(errors))


def build(output: Path, timeout_s: int) -> dict:
    payload, endpoint, endpoint_errors = fetch(timeout_s)
    records: list[dict] = []
    seen = set()
    for element in payload.get("elements", []):
        tags = element.get("tags") or {}
        name = normalize(tags.get("name"))
        if not name:
            continue
        key = (element.get("type"), element.get("id"))
        if key in seen:
            continue
        seen.add(key)
        center = element.get("center") or {}
        lat = element.get("lat", center.get("lat"))
        lon = element.get("lon", center.get("lon"))
        records.append(
            {
                "osm_type": element.get("type"),
                "osm_id": element.get("id"),
                "name": name,
                "name_normalized": normalize_name(name),
                "name_ar": normalize(tags.get("name:ar")),
                "name_en": normalize(tags.get("name:en")),
                "amenity": normalize(tags.get("amenity")),
                "education": normalize(tags.get("education")),
                "operator": normalize(tags.get("operator")),
                "website": normalize(tags.get("website") or tags.get("contact:website")),
                "phone": normalize(tags.get("phone") or tags.get("contact:phone")),
                "email": normalize(tags.get("email") or tags.get("contact:email")),
                "street": normalize(tags.get("addr:street")),
                "city": normalize(tags.get("addr:city")),
                "postcode": normalize(tags.get("addr:postcode")),
                "latitude": lat,
                "longitude": lon,
                "raw_tags": tags,
                "source_role": "supporting_identity_geography_discovery_only",
                "international_eligibility_granted": False,
            }
        )

    records.sort(key=lambda row: (row["name_normalized"], row["osm_type"], row["osm_id"]))
    duplicate_names: dict[str, list[int]] = {}
    for index, record in enumerate(records, start=1):
        duplicate_names.setdefault(record["name_normalized"], []).append(index)
    duplicate_groups = {
        name: indices for name, indices in duplicate_names.items() if len(indices) > 1
    }

    result = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_osm_egypt_international_education_supporting_discovery",
        "source": "OpenStreetMap via Overpass API",
        "source_endpoint": endpoint,
        "source_endpoint_fallback_errors": endpoint_errors,
        "query": QUERY,
        "name_signal_pattern": NAME_PATTERN,
        "record_count": len(records),
        "duplicate_normalized_name_group_count": len(duplicate_groups),
        "duplicate_normalized_name_groups": duplicate_groups,
        "records": records,
        "rules": {
            "osm_auto_international_eligibility": False,
            "osm_auto_identity_merge": False,
            "osm_auto_canonical_creation": False,
            "coordinates_require_identity_review_before_attachment": True,
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
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_endpoint": endpoint,
        "record_count": len(records),
        "duplicate_normalized_name_group_count": len(duplicate_groups),
    }, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/international/osm-egypt-international-education/osm-egypt-international-education.json"),
    )
    parser.add_argument("--timeout-s", type=int, default=120)
    args = parser.parse_args()
    build(args.output, args.timeout_s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
