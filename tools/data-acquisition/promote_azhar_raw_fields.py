#!/usr/bin/env python3
"""Promote verified Al-Azhar detail controls into raw acquisition fields.

This is not canonical normalization. It only copies values already present in each
raw Al-Azhar payload into the convenience columns expected by raw ingestion while
preserving the original payload unchanged.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CONTROL_SUFFIXES = {
    "name": "txtName",
    "famous_name": "txtFamousName",
    "administration": "ddlcenter",
    "stage": "TxtSTG",
    "education_type": "TxtTyp",
    "gender": "TxtSex",
    "address": "TxtAdd",
    "telephone": "TxtTel",
}


def value_by_suffix(inputs: dict, suffix: str):
    for key, value in inputs.items():
        if str(key).split("$")[-1].lower() == suffix.lower():
            if value is not None and str(value).strip():
                return str(value).strip()
    return None


def promote(row: dict) -> dict:
    payload = row.get("payload") or {}
    inputs = payload.get("inputs") or {}
    verified = {name: value_by_suffix(inputs, suffix) for name, suffix in CONTROL_SUFFIXES.items()}
    verified = {k: v for k, v in verified.items() if v}

    if not row.get("name_raw") and verified.get("name"):
        row["name_raw"] = verified["name"]

    location_parts = []
    for key in ("administration", "address"):
        value = verified.get(key)
        if value and value not in location_parts:
            location_parts.append(value)
    if location_parts and not row.get("location_raw"):
        row["location_raw"] = " | ".join(location_parts)

    # Keep these as source-specific raw facts. They are not Edu Hub canonical
    # mappings and still require provenance/reviewer handling later.
    payload["verified_live_controls"] = verified
    row["payload"] = payload
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    seen = named = located = 0
    with inp.open("r", encoding="utf-8") as src, out.open("w", encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            seen += 1
            row = promote(json.loads(line))
            named += int(bool(row.get("name_raw")))
            located += int(bool(row.get("location_raw")))
            dst.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"ok": True, "seen": seen, "named": named, "located": located, "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
