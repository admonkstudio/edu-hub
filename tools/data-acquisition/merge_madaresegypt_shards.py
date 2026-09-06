#!/usr/bin/env python3
"""Merge/dedupe raw MadaresEgypt JSONL shards without canonical entity merging."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path


def merge_payload(base: dict, incoming: dict) -> dict:
    out = dict(base)
    for key in ("categories", "listing_names", "listing_urls", "listing_contexts"):
        vals = []
        for source in (base.get(key) or [], incoming.get(key) or []):
            if isinstance(source, list):
                vals.extend(source)
        if vals:
            out[key] = sorted(dict.fromkeys(str(v) for v in vals if v not in (None, "")))
    # Preserve richer profile payload if one is present; the listing arrays above
    # are still unioned across all shards/categories.
    if incoming.get("acquisition_level") == "profile" and base.get("acquisition_level") != "profile":
        richer = dict(incoming)
        for key in ("categories", "listing_names", "listing_urls", "listing_contexts"):
            if key in out:
                richer[key] = out[key]
        out = richer
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", action="append", required=True, help="Glob pattern; may be repeated")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    paths: list[str] = []
    for pattern in args.input:
        paths.extend(glob.glob(pattern, recursive=True))
    paths = sorted(dict.fromkeys(paths))
    if not paths:
        raise SystemExit("No MadaresEgypt shard files found")

    rows: dict[str, dict] = {}
    seen = 0
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                seen += 1
                row = json.loads(line)
                sid = str(row.get("source_record_id") or "").strip()
                if not sid:
                    continue
                if sid not in rows:
                    rows[sid] = row
                    continue
                current = rows[sid]
                current_payload = current.get("payload") or {}
                incoming_payload = row.get("payload") or {}
                current["payload"] = merge_payload(current_payload, incoming_payload)
                if not current.get("name_raw") and row.get("name_raw"):
                    current["name_raw"] = row.get("name_raw")
                if not current.get("source_url") and row.get("source_url"):
                    current["source_url"] = row.get("source_url")
                cats = (current.get("payload") or {}).get("categories") or []
                current["entity_type_raw"] = "+".join(sorted(dict.fromkeys(cats))) if cats else (current.get("entity_type_raw") or row.get("entity_type_raw"))

    ordered = sorted(rows.values(), key=lambda r: int(str(r.get("source_record_id"))))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in ordered:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(json.dumps({"ok": True, "input_files": len(paths), "input_rows": seen, "unique_rows": len(ordered), "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
