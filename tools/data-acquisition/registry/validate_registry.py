#!/usr/bin/env python3
"""Validate the EDU-DATA-1 source registry and raw-source alias contracts.

This is intentionally dependency-free so it can run in CI and on acquisition
workers before any network calls are made.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_AUTHORITY_CLASSES = {
    "primary_official_registry",
    "primary_official_aggregate",
    "primary_official_institution",
    "primary_accreditation",
    "secondary_open_data",
    "secondary_directory",
    "historical_official",
}

SECONDARY_AUTHORITY_CLASSES = {
    "secondary_open_data",
    "secondary_directory",
}

PRIMARY_ROW_AUTHORITY_CLASSES = {
    "primary_official_registry",
    "primary_official_institution",
    "primary_accreditation",
}

REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "name",
    "entity_family",
    "authority_class",
    "base_url",
    "row_level_status",
    "preferred_acquisition",
    "publication_role",
    "notes",
}

ALLOWED_COVERAGE_CREDITS = {"current", "historical", "none"}
ALLOWED_CANDIDATE_STATUSES = {"ready", "needs_review", "invalid", "suppressed"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def valid_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate_aliases(path: Path, source_by_id: dict[str, dict], errors: list[str], warnings: list[str]) -> int:
    if not path.exists():
        fail(errors, f"source aliases not found: {path}")
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"source aliases unreadable: {exc}")
        return 0

    if data.get("schema_version") != 1:
        fail(errors, "source aliases schema_version must be 1")
    aliases = data.get("aliases")
    if not isinstance(aliases, list):
        fail(errors, "source aliases must contain aliases[]")
        return 0

    seen_raw: set[str] = set()
    mapped_registry_sources: set[str] = set()
    for idx, alias in enumerate(aliases):
        prefix = f"aliases[{idx}]"
        if not isinstance(alias, dict):
            fail(errors, f"{prefix}: must be an object")
            continue
        raw_source_id = alias.get("raw_source_id")
        if not isinstance(raw_source_id, str) or not raw_source_id.strip():
            fail(errors, f"{prefix}: raw_source_id must be non-empty")
        elif raw_source_id in seen_raw:
            fail(errors, f"{prefix}: duplicate raw_source_id {raw_source_id}")
        else:
            seen_raw.add(raw_source_id)

        registry_source_id = alias.get("registry_source_id")
        if registry_source_id is not None:
            if not isinstance(registry_source_id, str) or registry_source_id not in source_by_id:
                fail(errors, f"{prefix}: registry_source_id {registry_source_id!r} is not present in source_registry.json")
            else:
                mapped_registry_sources.add(registry_source_id)

        authority = alias.get("authority_class")
        if authority not in ALLOWED_AUTHORITY_CLASSES:
            fail(errors, f"{prefix}: unsupported authority_class {authority!r}")

        credit = alias.get("coverage_credit")
        if credit not in ALLOWED_COVERAGE_CREDITS:
            fail(errors, f"{prefix}: invalid coverage_credit {credit!r}")
        if credit == "current":
            if registry_source_id is None:
                fail(errors, f"{prefix}: current coverage requires a registry_source_id")
            if authority not in PRIMARY_ROW_AUTHORITY_CLASSES:
                fail(errors, f"{prefix}: current coverage requires primary row-level authority, got {authority!r}")
            if isinstance(registry_source_id, str) and registry_source_id in source_by_id:
                target_authority = source_by_id[registry_source_id].get("authority_class")
                if target_authority not in PRIMARY_ROW_AUTHORITY_CLASSES:
                    fail(errors, f"{prefix}: current coverage maps to non-row-level source authority {target_authority!r}")

        status = alias.get("default_candidate_status")
        if status not in ALLOWED_CANDIDATE_STATUSES:
            fail(errors, f"{prefix}: invalid default_candidate_status {status!r}")

    for source_id, source in source_by_id.items():
        if source.get("row_level_status") == "acquired" and source_id not in mapped_registry_sources:
            warnings.append(f"registry source {source_id} is marked acquired but has no raw-source alias")

    return len(aliases)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--registry",
        default="tools/data-acquisition/registry/source_registry.json",
        help="Path to source_registry.json",
    )
    ap.add_argument(
        "--aliases",
        default="tools/data-acquisition/registry/source_aliases.json",
        help="Path to source_aliases.json",
    )
    ap.add_argument("--report", default="", help="Optional JSON report output")
    args = ap.parse_args()

    path = Path(args.registry)
    if not path.exists():
        print(f"registry not found: {path}", file=sys.stderr)
        return 2

    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []

    if data.get("schema_version") != 1:
        fail(errors, "schema_version must be 1")

    principles = data.get("principles") or {}
    for required_true in (
        "raw_records_are_not_canonical_entities",
        "secondary_sources_cannot_satisfy_official_coverage_targets",
        "missing_fields_must_not_be_invented",
        "mirrored_media_is_not_automatically_public",
    ):
        if principles.get(required_true) is not True:
            fail(errors, f"principle must be true: {required_true}")

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        fail(errors, "sources must be a non-empty list")
        sources = []

    seen: set[str] = set()
    source_by_id: dict[str, dict] = {}
    official_target_total = 0
    target_sources = 0

    for idx, source in enumerate(sources):
        label = source.get("source_id") if isinstance(source, dict) else None
        prefix = f"sources[{idx}]" + (f" ({label})" if label else "")
        if not isinstance(source, dict):
            fail(errors, f"{prefix}: must be an object")
            continue

        missing = sorted(REQUIRED_SOURCE_FIELDS - set(source))
        if missing:
            fail(errors, f"{prefix}: missing required fields: {', '.join(missing)}")

        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            fail(errors, f"{prefix}: source_id must be non-empty")
        elif source_id in seen:
            fail(errors, f"{prefix}: duplicate source_id {source_id}")
        else:
            seen.add(source_id)
            source_by_id[source_id] = source

        authority = source.get("authority_class")
        if authority not in ALLOWED_AUTHORITY_CLASSES:
            fail(errors, f"{prefix}: unsupported authority_class {authority!r}")

        if not valid_https_url(source.get("base_url")):
            fail(errors, f"{prefix}: base_url must be an https URL")

        preferred = source.get("preferred_acquisition")
        if not isinstance(preferred, list) or not preferred or not all(isinstance(x, str) and x for x in preferred):
            fail(errors, f"{prefix}: preferred_acquisition must be a non-empty string list")

        target = source.get("coverage_target")
        if target is not None:
            if not isinstance(target, dict):
                fail(errors, f"{prefix}: coverage_target must be null or object")
            else:
                count = target.get("count")
                if not isinstance(count, int) or count <= 0:
                    fail(errors, f"{prefix}: coverage_target.count must be a positive integer")
                else:
                    official_target_total += count
                    target_sources += 1
                if not target.get("basis"):
                    fail(errors, f"{prefix}: coverage_target.basis is required")
                if not valid_https_url(target.get("reference_url")):
                    fail(errors, f"{prefix}: coverage_target.reference_url must be an https URL")
                if authority in SECONDARY_AUTHORITY_CLASSES:
                    fail(errors, f"{prefix}: secondary source cannot define an official coverage target")

        if source.get("row_level_status") == "acquired" and authority == "primary_official_aggregate":
            warnings.append(f"{prefix}: aggregate source marked acquired; ensure this does not imply row-level identity coverage")

    required_ids = {
        "moe_emis_school_directory",
        "azhar_institute_guide",
        "scu_institutions",
        "moss_nursery_census",
    }
    missing_required = sorted(required_ids - seen)
    if missing_required:
        fail(errors, "missing required national-registry sources: " + ", ".join(missing_required))

    alias_count = validate_aliases(Path(args.aliases), source_by_id, errors, warnings)

    report = {
        "ok": not errors,
        "schema_version": data.get("schema_version"),
        "source_count": len(sources),
        "alias_count": alias_count,
        "coverage_target_sources": target_sources,
        "sum_of_noncomparable_target_counts": official_target_total,
        "errors": errors,
        "warnings": warnings,
        "note": "Coverage target counts may describe overlapping or different universes and must not be interpreted as a canonical entity total.",
    }

    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output + "\n", encoding="utf-8")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
