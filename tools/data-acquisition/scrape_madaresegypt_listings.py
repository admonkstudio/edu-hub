#!/usr/bin/env python3
"""Resilient raw-first MadaresEgypt listing acquisition.

This adapter collects public listing-level institution identities only. MadaresEgypt
is a secondary discovery source, not regulatory authority. It is intentionally
fault tolerant: individual page failures are recorded and retried without losing
already discovered records.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://madaresegypt.com"
CATEGORY_URLS = {
    "school": f"{BASE}/ar/Results/{quote('مدارس')}",
    "nursery": f"{BASE}/ar/Results/{quote('حضانات')}",
}
UA = "EduHubResearchBot/0.6 (+https://github.com/admonkstudio/edu-hub; public-source-acquisition)"


def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=1.2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": UA, "Accept-Language": "ar,en;q=0.8"})
    return s


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def item_id(href: str) -> str | None:
    m = re.search(r"/(?:ar|en)/item/(\d+)(?:/|$)", urlparse(href).path, re.I)
    return m.group(1) if m else None


def card_context(anchor) -> str | None:
    candidates = []
    node = anchor
    for _ in range(5):
        node = node.parent
        if node is None:
            break
        if hasattr(node, "get_text"):
            txt = clean(node.get_text(" ", strip=True))
            if txt and 10 <= len(txt) <= 1200:
                candidates.append(txt)
    return min(candidates, key=len) if candidates else None


def fetch_page(session: requests.Session, url: str, attempts: int = 3) -> str:
    last = None
    for attempt in range(1, attempts + 1):
        try:
            r = session.get(url, timeout=(15, 35), allow_redirects=True)
            if r.status_code == 404:
                return ""
            r.raise_for_status()
            return r.text
        except Exception as exc:
            last = exc
            if attempt < attempts:
                time.sleep(2.5 * attempt)
    raise RuntimeError(f"page failed after {attempts} attempts: {url}: {last!r}")


def parse_listing_page(html: str, page_url: str, category: str) -> dict[str, dict]:
    soup = BeautifulSoup(html, "html.parser")
    found: dict[str, dict] = {}
    for a in soup.find_all("a", href=True):
        href = urljoin(BASE, a.get("href", ""))
        sid = item_id(href)
        if not sid:
            continue
        label = clean(a.get_text(" ", strip=True))
        context = card_context(a)
        row = found.setdefault(sid, {
            "source_record_id": sid,
            "source_url": f"{BASE}/ar/Item/{sid}",
            "name_raw": None,
            "entity_type_raw": category,
            "location_raw": None,
            "payload": {
                "acquisition_level": "listing",
                "category": category,
                "listing_names": [],
                "listing_urls": [],
                "listing_contexts": [],
            },
        })
        if label and label not in row["payload"]["listing_names"]:
            row["payload"]["listing_names"].append(label)
        if page_url not in row["payload"]["listing_urls"]:
            row["payload"]["listing_urls"].append(page_url)
        if context and context not in row["payload"]["listing_contexts"]:
            row["payload"]["listing_contexts"].append(context)
    for row in found.values():
        names = row["payload"]["listing_names"]
        row["name_raw"] = names[0] if names else None
        row["payload"]["listing_contexts"] = row["payload"]["listing_contexts"][:10]
    return found


def merge_record(target: dict, incoming: dict) -> None:
    if not target.get("name_raw") and incoming.get("name_raw"):
        target["name_raw"] = incoming["name_raw"]
    for key in ("listing_names", "listing_urls", "listing_contexts"):
        existing = target["payload"].setdefault(key, [])
        for value in incoming["payload"].get(key, []):
            if value not in existing:
                existing.append(value)
        if key == "listing_contexts":
            del existing[10:]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", required=True, choices=("school", "nursery"))
    ap.add_argument("--start-page", required=True, type=int)
    ap.add_argument("--end-page", required=True, type=int)
    ap.add_argument("--output", required=True)
    ap.add_argument("--delay", type=float, default=0.60)
    ap.add_argument("--max-consecutive-failures", type=int, default=8)
    args = ap.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    report_path = out.with_suffix(".report.json")
    session = make_session()
    base = CATEGORY_URLS[args.category]

    records: dict[str, dict] = {}
    failed_pages: list[int] = []
    pages_ok = 0
    consecutive_failures = 0
    repeated_signature = None
    repeated_count = 0

    for page in range(args.start_page, args.end_page + 1):
        url = base if page == 1 else f"{base}?page={page}"
        try:
            html = fetch_page(session, url)
            if not html:
                break
            page_rows = parse_listing_page(html, url, args.category)
            signature = tuple(sorted(page_rows))
            if signature and signature == repeated_signature:
                repeated_count += 1
            else:
                repeated_count = 0
            repeated_signature = signature
            if repeated_count >= 3:
                print(json.dumps({"stage":"end_detected","page":page,"reason":"repeated_page_signature"}, ensure_ascii=False), flush=True)
                break

            before = len(records)
            for sid, row in page_rows.items():
                if sid in records:
                    merge_record(records[sid], row)
                else:
                    records[sid] = row
            pages_ok += 1
            consecutive_failures = 0
            print(json.dumps({"stage":"page","category":args.category,"page":page,"page_records":len(page_rows),"new":len(records)-before,"total":len(records)}, ensure_ascii=False), flush=True)
        except Exception as exc:
            failed_pages.append(page)
            consecutive_failures += 1
            print(json.dumps({"stage":"page_error","category":args.category,"page":page,"error":repr(exc)}, ensure_ascii=False), flush=True)
            if consecutive_failures >= args.max_consecutive_failures:
                break
        if args.delay:
            time.sleep(args.delay)

    # One repair pass after the main scan, so transient failures do not become gaps.
    unresolved = []
    for page in failed_pages:
        url = base if page == 1 else f"{base}?page={page}"
        try:
            html = fetch_page(session, url, attempts=2)
            for sid, row in parse_listing_page(html, url, args.category).items():
                if sid in records:
                    merge_record(records[sid], row)
                else:
                    records[sid] = row
            pages_ok += 1
        except Exception:
            unresolved.append(page)
        if args.delay:
            time.sleep(args.delay)

    with out.open("w", encoding="utf-8") as f:
        for sid in sorted(records, key=lambda x: int(x)):
            f.write(json.dumps(records[sid], ensure_ascii=False) + "\n")

    report = {
        "ok": len(unresolved) == 0,
        "category": args.category,
        "start_page": args.start_page,
        "end_page": args.end_page,
        "pages_ok": pages_ok,
        "initial_failed_pages": failed_pages,
        "unresolved_failed_pages": unresolved,
        "unique_records": len(records),
        "named_records": sum(bool(r.get("name_raw")) for r in records.values()),
        "output": str(out),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
