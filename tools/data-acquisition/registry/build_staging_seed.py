#!/usr/bin/env python3
"""Build deterministic EDU-DATA-1 staging candidates and a coverage report.

The input is an owned raw SQLite archive. This tool is deliberately non-mutating:
it never creates edu_core identities and never claims current national coverage from
historical or secondary records.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ARABIC_RE = re.compile(r"[\u0600-\u06ff]")
TASHKEEL_RE = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
PHONE_RE = re.compile(r"(?:\+?20|0)?1[0125]\d{8}|(?:\+?20|0)?[2-9]\d{7,8}")
URL_RE = re.compile(r"https?://[^\s<>\"']+")

TYPE_MAP = {
    "azhar_institute": "azhar_institute",
    "university": "university",
    "higher_institute": "higher_institute",
    "technical_institute": "technical_institute",
    "school": "school",
    "nursery": "nursery",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text(value: object) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def normalize_space(value: object) -> str | None:
    value = text(value)
    if not value:
        return None
    return " ".join(unicodedata.normalize("NFKC", value).split())


def normalize_arabic(value: object) -> str | None:
    value = normalize_space(value)
    if not value:
        return None
    value = value.replace("ـ", "")
    value = TASHKEEL_RE.sub("", value)
    value = value.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي"}))
    return " ".join(value.split()).casefold()


def normalize_latin(value: object) -> str | None:
    value = normalize_space(value)
    return value.casefold() if value else None


def walk_strings(value: object, prefix: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from walk_strings(child, child_prefix)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_strings(child, f"{prefix}[{index}]")
    elif isinstance(value, str) and value.strip():
        yield prefix.casefold(), value.strip()


def first_payload_value(payload: dict, key_fragments: tuple[str, ...]) -> str | None:
    for path, value in walk_strings(payload):
        if any(fragment in path for fragment in key_fragments):
            return value
    return None


def normalize_phone(payload: dict) -> str | None:
    candidate = first_payload_value(payload, ("phone", "telephone", "mobile", "whatsapp", "tel"))
    if not candidate:
        return None
    match = PHONE_RE.search(candidate.replace(" ", "").replace("-", ""))
    if not match:
        return None
    digits = re.sub(r"\D", "", match.group(0))
    if digits.startswith("20"):
        digits = "0" + digits[2:]
    return digits


def normalize_domain(payload: dict) -> str | None:
    candidate = first_payload_value(payload, ("official_website", "website", "domain"))
    if not candidate:
        return None
    match = URL_RE.search(candidate) or URL_RE.search("https://" + candidate)
    if not match:
        return None
    parsed = urlparse(match.group(0))
    host = parsed.hostname.casefold() if parsed.hostname else ""
    if host.startswith("www."):
        host = host[4:]
    return host or None


def parse_payload(raw: object) -> dict:
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def split_display_names(row: sqlite3.Row, payload: dict) -> tuple[str | None, str | None]:
    name_ar = text(row["name_ar_raw"])
    name_en = text(row["name_en_raw"])
    raw = text(row["name_raw"])
    if not name_ar and raw and ARABIC_RE.search(raw):
        name_ar = raw
    if not name_en and raw and not ARABIC_RE.search(raw):
        name_en = raw
    if not name_ar:
        candidate = first_payload_value(payload, ("name_ar", "arabic_name"))
        if candidate and ARABIC_RE.search(candidate):
            name_ar = candidate
    if not name_en:
        candidate = first_payload_value(payload, ("name_en", "english_name"))
        if candidate and not ARABIC_RE.search(candidate):
            name_en = candidate
    return normalize_space(name_ar), normalize_space(name_en)


def normalized_type(row: sqlite3.Row, payload: dict) -> str | None:
    proposed = text(payload.get("entity_type_proposed"))
    raw_type = text(row["entity_type_raw"])
    return TYPE_MAP.get(proposed or "", proposed) or TYPE_MAP.get(raw_type or "", raw_type)


def source_alias_map(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("aliases"), list):
        raise SystemExit("source aliases must use schema_version 1 and contain aliases[]")
    aliases: dict[str, dict] = {}
    for item in data["aliases"]:
        source_id = item.get("raw_source_id")
        if not source_id or source_id in aliases:
            raise SystemExit(f"invalid or duplicate raw_source_id in aliases: {source_id!r}")
        if item.get("coverage_credit") not in {"current", "historical", "none"}:
            raise SystemExit(f"invalid coverage_credit for {source_id}")
        aliases[source_id] = item
    return aliases


def load_registry(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise SystemExit("source registry schema_version must be 1")
    return data


def candidate_from_row(row: sqlite3.Row, alias: dict | None) -> dict:
    payload = parse_payload(row["payload_json"])
    name_ar, name_en = split_display_names(row, payload)
    location = normalize_space(row["location_raw"])
    issues: list[str] = []
    authority = alias.get("authority_class") if alias else "unmapped_historical_source"
    coverage_credit = alias.get("coverage_credit") if alias else "none"
    status = alias.get("default_candidate_status") if alias else "needs_review"
    if not (name_ar or name_en):
        issues.append("missing_name")
        status = "invalid"
    if coverage_credit == "historical":
        issues.append("historical_evidence_not_current_coverage")
    if authority.startswith("secondary_"):
        issues.append("secondary_evidence_requires_identity_reconciliation")
    if alias is None:
        issues.append("source_not_in_registry_alias_contract")

    official_identifier = None
    if row["source_id"] == "azhar_official_institute_guide":
        official_identifier = text(row["source_record_id"])

    match_features = {
        "registry_source_id": alias.get("registry_source_id") if alias else None,
        "authority_class": authority,
        "coverage_credit": coverage_credit,
        "raw_hash": row["raw_hash"],
    }
    return {
        "raw_id": row["raw_id"],
        "source_id": row["source_id"],
        "source_record_id": row["source_record_id"],
        "entity_family": row["entity_family"],
        "entity_type_raw": row["entity_type_raw"],
        "normalized_type": normalized_type(row, payload),
        "name_ar": name_ar,
        "name_en": name_en,
        "normalized_name_ar": normalize_arabic(name_ar),
        "normalized_name_en": normalize_latin(name_en),
        "normalized_location": normalize_space(location),
        "governorate": None,
        "city": None,
        "district": None,
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "normalized_phone": normalize_phone(payload),
        "normalized_domain": normalize_domain(payload),
        "official_identifier": official_identifier,
        "match_features": match_features,
        "normalization_issues": issues,
        "candidate_status": status,
    }


def build_report(registry: dict, aliases: dict[str, dict], raw_counts: Counter, staged_counts: Counter, archive_sha: str) -> dict:
    current_by_registry = Counter()
    historical_by_registry = Counter()
    secondary_or_uncredited = Counter()
    for raw_source_id, count in raw_counts.items():
        alias = aliases.get(raw_source_id)
        if not alias or not alias.get("registry_source_id"):
            secondary_or_uncredited[raw_source_id] += count
            continue
        registry_id = alias["registry_source_id"]
        if alias["coverage_credit"] == "current":
            current_by_registry[registry_id] += count
        elif alias["coverage_credit"] == "historical":
            historical_by_registry[registry_id] += count
        else:
            secondary_or_uncredited[raw_source_id] += count

    sources = []
    for source in registry.get("sources", []):
        source_id = source["source_id"]
        target = source.get("coverage_target") or {}
        target_count = target.get("count")
        current = current_by_registry[source_id]
        historical = historical_by_registry[source_id]
        coverage_percent = round((current / target_count) * 100, 4) if target_count else None
        sources.append({
            "source_id": source_id,
            "name": source["name"],
            "authority_class": source["authority_class"],
            "entity_family": source["entity_family"],
            "official_target": target_count,
            "current_coverage_rows": current,
            "historical_evidence_rows": historical,
            "coverage_percent": coverage_percent,
            "row_level_status": source["row_level_status"],
        })

    current_official_rows = sum(current_by_registry.values())
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_archive_sha256": archive_sha,
        "raw_records_seen": sum(raw_counts.values()),
        "staging_candidates_generated": sum(staged_counts.values()),
        "current_official_seed_rows": current_official_rows,
        "canonical_entities_created": 0,
        "automatic_identity_acceptances": 0,
        "core_promotion_performed": False,
        "headline_targets": {
            "moe_emis_schools": 62690,
            "moss_nurseries": 48225,
            "moe_plus_moss": 110915,
            "note": "These are official universe targets, not acquired or canonical entity counts."
        },
        "sources": sources,
        "raw_source_counts": dict(sorted(raw_counts.items())),
        "staged_source_counts": dict(sorted(staged_counts.items())),
        "uncredited_or_secondary_raw_rows": sum(secondary_or_uncredited.values()),
        "notes": [
            "Raw records are evidence, not canonical institutions.",
            "Historical EMIS rows are staged as evidence but do not count toward the current MOE target.",
            "Secondary records never satisfy official national coverage targets.",
            "No edu_core identities are created by this tool."
        ],
    }


def write_csv(report: dict, path: Path) -> None:
    fieldnames = [
        "source_id", "name", "authority_class", "entity_family", "official_target",
        "current_coverage_rows", "historical_evidence_rows", "coverage_percent", "row_level_status"
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report["sources"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", required=True, type=Path)
    parser.add_argument("--registry", default="tools/data-acquisition/registry/source_registry.json", type=Path)
    parser.add_argument("--aliases", default="tools/data-acquisition/registry/source_aliases.json", type=Path)
    parser.add_argument("--out-dir", default="artifacts/edu-data-1/registry-seed", type=Path)
    args = parser.parse_args()

    registry = load_registry(args.registry)
    aliases = source_alias_map(args.aliases)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    db = sqlite3.connect(f"file:{args.sqlite.resolve()}?mode=ro&immutable=1", uri=True)
    db.row_factory = sqlite3.Row
    required = {"raw_id", "source_id", "source_record_id", "entity_family", "entity_type_raw", "name_raw", "name_ar_raw", "name_en_raw", "location_raw", "latitude", "longitude", "raw_hash", "payload_json"}
    columns = {row[1] for row in db.execute("pragma table_info(raw_records)")}
    missing = required - columns
    if missing:
        raise SystemExit("raw_records missing columns: " + ", ".join(sorted(missing)))

    raw_counts: Counter = Counter()
    staged_counts: Counter = Counter()
    candidates_path = args.out_dir / "staging_candidates.jsonl"
    with candidates_path.open("w", encoding="utf-8") as out:
        for row in db.execute("select * from raw_records order by raw_id"):
            raw_counts[row["source_id"]] += 1
            alias = aliases.get(row["source_id"])
            candidate = candidate_from_row(row, alias)
            staged_counts[row["source_id"]] += 1
            out.write(json.dumps(candidate, ensure_ascii=False, sort_keys=True) + "\n")
    db.close()

    archive_sha = sha256_file(args.sqlite)
    report = build_report(registry, aliases, raw_counts, staged_counts, archive_sha)
    report["outputs"] = {
        "staging_candidates": str(candidates_path),
        "staging_candidates_sha256": sha256_file(candidates_path),
    }
    report_path = args.out_dir / "coverage_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(report, args.out_dir / "coverage_report.csv")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
