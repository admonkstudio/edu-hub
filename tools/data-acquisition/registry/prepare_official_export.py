#!/usr/bin/env python3
"""Validate a machine-readable official registry export and wrap rows as raw evidence.

This utility is intentionally source-preserving. It does not normalize identities,
deduplicate institutions across sources, or write to edu_core. It validates that an
incoming row-level export belongs to a declared official registry and emits a stable
JSONL evidence envelope suitable for the edu_raw import gate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_registry(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("sources"), list):
        raise SystemExit("source registry must use schema_version 1 and contain sources[]")
    return data


def source_contract(registry: dict, source_id: str) -> dict:
    matches = [s for s in registry["sources"] if s.get("source_id") == source_id]
    if len(matches) != 1:
        raise SystemExit(f"unknown or duplicate source_id in registry: {source_id}")
    source = matches[0]
    if source.get("authority_class") != "primary_official_registry":
        raise SystemExit(
            f"{source_id} is {source.get('authority_class')!r}; this intake tool only accepts primary_official_registry sources"
        )
    return source


def load_rows(path: Path, fmt: str) -> Iterable[dict]:
    resolved = fmt
    if fmt == "auto":
        suffix = path.suffix.casefold()
        resolved = {".csv": "csv", ".jsonl": "jsonl", ".ndjson": "jsonl", ".json": "json"}.get(suffix, "")
        if not resolved:
            raise SystemExit("cannot infer input format; pass --format csv|jsonl|json")

    if resolved == "csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                yield dict(row)
        return

    if resolved == "jsonl":
        with path.open("r", encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"invalid JSONL at line {line_number}: {exc}") from exc
                if not isinstance(row, dict):
                    raise SystemExit(f"JSONL line {line_number} is not an object")
                yield row
        return

    if resolved == "json":
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(data, dict) and isinstance(data.get("rows"), list):
            data = data["rows"]
        if not isinstance(data, list):
            raise SystemExit("JSON input must be an array of row objects or an object with rows[]")
        for index, row in enumerate(data, 1):
            if not isinstance(row, dict):
                raise SystemExit(f"JSON row {index} is not an object")
            yield row
        return

    raise SystemExit(f"unsupported input format: {resolved}")


def nested_value(row: dict, path: str) -> object:
    value: object = row
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def nonempty(value: object) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-id", required=True)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--id-field", required=True, help="Stable source identifier field, dotted paths allowed")
    ap.add_argument("--format", choices=("auto", "csv", "jsonl", "json"), default="auto")
    ap.add_argument("--registry", type=Path, default=Path("tools/data-acquisition/registry/source_registry.json"))
    ap.add_argument("--out-dir", type=Path, default=Path("artifacts/edu-data-1/official-export"))
    ap.add_argument("--allow-duplicate-source-ids", action="store_true")
    args = ap.parse_args()

    registry = load_registry(args.registry)
    source = source_contract(registry, args.source_id)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    seen_ids: set[str] = set()
    duplicates: list[str] = []
    rows_seen = 0
    missing_ids = 0
    output_path = args.out_dir / f"{args.source_id}.raw.jsonl"

    with output_path.open("w", encoding="utf-8") as out:
        for row_number, row in enumerate(load_rows(args.input, args.format), 1):
            rows_seen += 1
            source_record_id = nonempty(nested_value(row, args.id_field))
            if not source_record_id:
                missing_ids += 1
                continue
            if source_record_id in seen_ids:
                duplicates.append(source_record_id)
                if not args.allow_duplicate_source_ids:
                    continue
            seen_ids.add(source_record_id)
            payload_canonical = canonical_json(row)
            envelope = {
                "source_id": args.source_id,
                "source_record_id": source_record_id,
                "raw_hash": sha256_text(payload_canonical),
                "payload": row,
                "intake_row_number": row_number,
            }
            out.write(canonical_json(envelope) + "\n")

    emitted_rows = len(seen_ids) if not args.allow_duplicate_source_ids else rows_seen - missing_ids
    target = (source.get("coverage_target") or {}).get("count")
    coverage_percent = round((len(seen_ids) / target) * 100, 4) if target else None
    report = {
        "schema_version": 1,
        "source_id": args.source_id,
        "source_name": source.get("name"),
        "authority_class": source.get("authority_class"),
        "input_file": str(args.input),
        "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "id_field": args.id_field,
        "rows_seen": rows_seen,
        "unique_source_ids": len(seen_ids),
        "missing_source_ids": missing_ids,
        "duplicate_source_ids": len(duplicates),
        "duplicate_source_id_sample": sorted(set(duplicates))[:25],
        "rows_emitted": emitted_rows,
        "official_target": target,
        "coverage_percent_before_identity_resolution": coverage_percent,
        "canonical_entities_created": 0,
        "automatic_identity_acceptances": 0,
        "core_promotion_performed": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output": str(output_path),
        "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
        "notes": [
            "Coverage percentage is source-row coverage, not canonical institution coverage.",
            "Rows remain raw evidence until staging normalization and identity review.",
            "This utility never writes to edu_core or public projections."
        ],
    }
    report_path = args.out_dir / f"{args.source_id}.intake-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if missing_ids:
        return 4
    if duplicates and not args.allow_duplicate_source_ids:
        return 5
    if rows_seen == 0:
        return 6
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
