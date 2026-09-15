#!/usr/bin/env python3
"""Attempt supporting Egypt international-education discovery from OSM.

OpenStreetMap is supporting identity/geography discovery only. Egypt is covered
by a fixed 3x4 bounding-box grid and three bounded workers query public Overpass
mirrors. Public Overpass access is not guaranteed from hosted CI environments,
so failed tiles are recorded as an explicit coverage diagnostic rather than
being mistaken for zero results or repeatedly failing the entire D2.1 pipeline.

Any returned rows remain supporting-only and never establish eligibility.
"""
from __future__ import annotations

import argparse
import json
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests

OVERPASS_ENDPOINTS = [
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]
NAME_PATTERN = (
    "international|american|british|english|french|francais|français|german|deutsch|"
    "canadian|pakistan|indian|japanese|korean|italian|spanish|swiss|baccalaureate|"
    "choueifat|sabis|montessori"
)
LAT_EDGES = [22.0, 25.3, 28.6, 31.9]
LON_EDGES = [24.5, 27.625, 30.75, 33.875, 37.0]
MAX_WORKERS = 3


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


def tiles() -> list[tuple[float, float, float, float]]:
    return [
        (LAT_EDGES[i], LON_EDGES[j], LAT_EDGES[i + 1], LON_EDGES[j + 1])
        for i in range(len(LAT_EDGES) - 1)
        for j in range(len(LON_EDGES) - 1)
    ]


def query_for(bbox: tuple[float, float, float, float]) -> str:
    south, west, north, east = bbox
    return f'''[out:json][timeout:10];
(
  nwr["amenity"~"^(school|college|university)$"]["name"~"{NAME_PATTERN}",i]({south},{west},{north},{east});
);
out center tags;'''


def fetch_tile(index: int, bbox: tuple[float, float, float, float], request_timeout_s: int) -> dict:
    errors: list[str] = []
    headers = {"User-Agent": "EduHub-D2.1-supporting-discovery/1.0", "Accept": "application/json"}
    query = query_for(bbox)
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            response = requests.post(endpoint, data={"data": query}, headers=headers, timeout=request_timeout_s)
            if response.status_code == 200:
                payload = response.json()
                return {
                    "tile": index, "bbox": bbox, "status": "success", "endpoint": endpoint,
                    "errors": errors, "elements": payload.get("elements", []),
                }
            errors.append(f"{endpoint}: HTTP {response.status_code}")
        except Exception as exc:
            errors.append(f"{endpoint}: {type(exc).__name__}: {exc}")
        time.sleep(0.25)
    return {"tile": index, "bbox": bbox, "status": "failed", "endpoint": None, "errors": errors, "elements": []}


def build(output: Path, timeout_s: int) -> dict:
    request_timeout_s = min(max(timeout_s, 5), 8)
    work = list(enumerate(tiles(), start=1))
    tile_results: list[dict] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_tile, index, bbox, request_timeout_s): index for index, bbox in work}
        for future in as_completed(futures):
            tile_results.append(future.result())
    tile_results.sort(key=lambda item: item["tile"])

    successful_tiles = [item for item in tile_results if item["status"] == "success"]
    failed_tiles = [item for item in tile_results if item["status"] != "success"]
    if not failed_tiles:
        coverage_state = "complete"
    elif not successful_tiles:
        coverage_state = "environment_blocked_all_tiles"
    else:
        coverage_state = "partial_public_overpass_availability"

    elements: list[dict] = []
    endpoint_counts: dict[str, int] = {}
    tile_summaries: list[dict] = []
    for item in tile_results:
        elements.extend(item["elements"])
        endpoint = item["endpoint"]
        if endpoint:
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
        tile_summaries.append({
            "tile": item["tile"], "bbox": item["bbox"], "status": item["status"],
            "endpoint": endpoint, "errors": item["errors"], "element_count": len(item["elements"]),
        })

    records: list[dict] = []
    seen = set()
    for element in elements:
        tags = element.get("tags") or {}
        name = normalize(tags.get("name"))
        if not name:
            continue
        key = (element.get("type"), element.get("id"))
        if key in seen:
            continue
        seen.add(key)
        center = element.get("center") or {}
        records.append({
            "osm_type": element.get("type"), "osm_id": element.get("id"), "name": name,
            "name_normalized": normalize_name(name), "name_ar": normalize(tags.get("name:ar")),
            "name_en": normalize(tags.get("name:en")), "amenity": normalize(tags.get("amenity")),
            "operator": normalize(tags.get("operator")),
            "website": normalize(tags.get("website") or tags.get("contact:website")),
            "phone": normalize(tags.get("phone") or tags.get("contact:phone")),
            "email": normalize(tags.get("email") or tags.get("contact:email")),
            "street": normalize(tags.get("addr:street")), "city": normalize(tags.get("addr:city")),
            "postcode": normalize(tags.get("addr:postcode")),
            "latitude": element.get("lat", center.get("lat")), "longitude": element.get("lon", center.get("lon")),
            "raw_tags": tags, "source_role": "supporting_identity_geography_discovery_only",
            "international_eligibility_granted": False,
        })
    records.sort(key=lambda row: (row["name_normalized"], row["osm_type"], row["osm_id"]))

    by_name: dict[str, list[int]] = {}
    for index, record in enumerate(records, start=1):
        by_name.setdefault(record["name_normalized"], []).append(index)
    duplicate_groups = {name: ids for name, ids in by_name.items() if len(ids) > 1}

    result = {
        "schema_version": 5,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_osm_egypt_international_education_supporting_discovery",
        "source": "OpenStreetMap via public Overpass API",
        "coverage_bbox": [22.0, 24.5, 31.9, 37.0],
        "coverage_state": coverage_state,
        "coverage_complete": coverage_state == "complete",
        "tile_count": len(tile_summaries),
        "successful_tile_count": len(successful_tiles),
        "failed_tile_count": len(failed_tiles),
        "failed_tile_ids": [item["tile"] for item in failed_tiles],
        "max_concurrent_tile_requests": MAX_WORKERS,
        "tile_summaries": tile_summaries,
        "endpoint_tile_counts": endpoint_counts,
        "name_signal_pattern": NAME_PATTERN,
        "record_count": len(records),
        "duplicate_normalized_name_group_count": len(duplicate_groups),
        "duplicate_normalized_name_groups": duplicate_groups,
        "records": records,
        "rules": {
            "osm_auto_international_eligibility": False,
            "osm_auto_identity_merge": False,
            "osm_auto_canonical_creation": False,
            "failed_coverage_never_interpreted_as_zero_candidates": True,
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
        "coverage_state": coverage_state, "successful_tile_count": len(successful_tiles),
        "failed_tile_count": len(failed_tiles), "record_count": len(records),
    }, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/international/osm-egypt-international-education/osm-egypt-international-education.json"))
    parser.add_argument("--timeout-s", type=int, default=6)
    args = parser.parse_args()
    build(args.output, args.timeout_s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
