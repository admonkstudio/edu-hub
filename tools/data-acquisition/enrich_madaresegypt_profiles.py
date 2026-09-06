#!/usr/bin/env python3
"""Acquire factual MadaresEgypt profile evidence for an existing raw record batch."""
from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path


def load_adapter():
    path = Path(__file__).with_name("scrape_madaresegypt.py")
    spec = importlib.util.spec_from_file_location("madaresegypt_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load adapter: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--delay", type=float, default=0.75)
    args = ap.parse_args()

    adapter = load_adapter()
    source = Path(args.input)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    session = adapter.session()
    processed = written = 0
    errors = []

    with source.open("r", encoding="utf-8") as src, output.open("w", encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            row = json.loads(line)
            processed += 1
            sid = str(row.get("source_record_id") or "").strip()
            url = row.get("source_url")
            payload = row.get("payload") or {}
            categories = payload.get("categories") or ([payload["category"]] if payload.get("category") else [])
            if not categories and row.get("entity_type_raw"):
                categories = str(row["entity_type_raw"]).split("+")
            discovered = {
                "categories": set(categories or ["school"]),
                "listing_names": set(payload.get("listing_names") or ([row["name_raw"]] if row.get("name_raw") else [])),
                "listing_urls": set(payload.get("listing_urls") or []),
                "listing_contexts": set(payload.get("listing_contexts") or []),
            }
            try:
                response = session.get(url, timeout=60, allow_redirects=True)
                response.raise_for_status()
                enriched = adapter.parse_profile(sid, discovered, response.text, response.url)
                dst.write(json.dumps(enriched, ensure_ascii=False) + "\n")
                written += 1
            except Exception as exc:
                errors.append({"source_record_id": sid, "source_url": url, "error": repr(exc)})
            if args.delay:
                time.sleep(args.delay)

    report = {
        "ok": not errors,
        "records_processed": processed,
        "records_written": written,
        "errors": errors,
        "output": str(output),
        "principle": "raw factual profile evidence; no canonical overwrite",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
