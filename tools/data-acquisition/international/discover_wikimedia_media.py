#!/usr/bin/env python3
"""Discover Wikimedia Commons media candidates for EDU-DATA-2 institutions.

This tool only discovers media and records license/provenance metadata. It does
not declare an institution identity match as verified and does not authorize
publication. A later review must confirm that the media depicts the intended
institution/campus.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import time
from pathlib import Path

import requests

API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "EduHubResearch/2.0 (+https://github.com/admonkstudio/edu-hub)"
REUSABLE_LICENSE_PATTERNS = (
    "cc by",
    "cc-by",
    "cc by-sa",
    "cc-by-sa",
    "creative commons attribution",
    "public domain",
    "cc0",
)


def strip_html(value: object) -> str:
    text = html.unescape(str(value or ""))
    return " ".join(re.sub(r"<[^>]+>", " ", text).split())


def candidate_name(row: dict) -> str | None:
    return row.get("name_en") or row.get("parent_university_en") or row.get("name_ar")


def license_looks_reusable(short_name: str, usage_terms: str) -> bool:
    blob = f"{short_name} {usage_terms}".casefold()
    return any(token in blob for token in REUSABLE_LICENSE_PATTERNS)


def search(session: requests.Session, query: str, limit: int, timeout: float) -> list[dict]:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "generator": "search",
        "gsrsearch": f'filetype:bitmap "{query}"',
        "gsrnamespace": 6,
        "gsrlimit": max(1, min(limit, 10)),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime|size",
        "iiurlwidth": 1280,
    }
    response = session.get(API, params=params, timeout=timeout)
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", [])
    out = []
    for page in pages:
        infos = page.get("imageinfo") or []
        if not infos:
            continue
        info = infos[0]
        meta = info.get("extmetadata") or {}
        short_license = strip_html((meta.get("LicenseShortName") or {}).get("value"))
        usage_terms = strip_html((meta.get("UsageTerms") or {}).get("value"))
        artist = strip_html((meta.get("Artist") or {}).get("value"))
        attribution = strip_html((meta.get("Attribution") or {}).get("value"))
        description = strip_html((meta.get("ImageDescription") or {}).get("value"))
        license_url = strip_html((meta.get("LicenseUrl") or {}).get("value"))
        out.append(
            {
                "commons_page_id": page.get("pageid"),
                "commons_title": page.get("title"),
                "original_url": info.get("url"),
                "thumbnail_url": info.get("thumburl"),
                "description_page_url": info.get("descriptionurl"),
                "mime": info.get("mime"),
                "width": info.get("width"),
                "height": info.get("height"),
                "description": description,
                "creator": artist or None,
                "attribution_text": attribution or None,
                "license_name": short_license or None,
                "license_url": license_url or None,
                "usage_terms": usage_terms or None,
                "license_looks_reusable": license_looks_reusable(short_license, usage_terms),
                "identity_match_state": "unreviewed",
                "public_use_allowed": False,
            }
        )
    return out


def run(input_jsonl: Path, output_jsonl: Path, limit: int, delay: float, timeout: float) -> dict:
    rows = [json.loads(line) for line in input_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en,ar;q=0.8"})
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    institutions_queried = 0
    candidates_found = 0
    reusable_license_candidates = 0
    with output_jsonl.open("w", encoding="utf-8") as handle:
        for index, row in enumerate(rows):
            name = candidate_name(row)
            if not name:
                continue
            institutions_queried += 1
            try:
                candidates = search(session, str(name), limit, timeout)
            except requests.RequestException as exc:
                handle.write(json.dumps({
                    "source_record_id": row.get("source_record_id"),
                    "institution_name": name,
                    "query_error": repr(exc),
                    "media_candidates": [],
                }, ensure_ascii=False, sort_keys=True) + "\n")
                continue
            candidates_found += len(candidates)
            reusable_license_candidates += sum(1 for c in candidates if c["license_looks_reusable"])
            handle.write(json.dumps({
                "source_record_id": row.get("source_record_id"),
                "source_id": row.get("source_id"),
                "institution_name": name,
                "media_candidates": candidates,
            }, ensure_ascii=False, sort_keys=True) + "\n")
            if delay and index < len(rows) - 1:
                time.sleep(delay)

    summary = {
        "institutions_queried": institutions_queried,
        "media_candidates_found": candidates_found,
        "candidates_with_apparently_reusable_license": reusable_license_candidates,
        "identity_matches_verified": 0,
        "public_media_authorized": 0,
        "database_mutation_performed": False,
        "public_promotion_performed": False,
        "output": str(output_jsonl),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("artifacts/international/authoritative-source-candidates.jsonl"))
    ap.add_argument("--output", type=Path, default=Path("artifacts/international/wikimedia-media-candidates.jsonl"))
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--delay", type=float, default=0.1)
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()
    run(args.input, args.output, args.limit, args.delay, args.timeout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
