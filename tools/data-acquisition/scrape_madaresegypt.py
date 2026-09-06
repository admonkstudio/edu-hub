#!/usr/bin/env python3
"""Acquire public school and nursery facts from MadaresEgypt.

This adapter is discovery-only/raw-first. It reads public listing/profile pages,
keeps source IDs/URLs and visible factual fields, and intentionally excludes media
assets, comments/reviews and any authenticated/private content.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://madaresegypt.com"
CATEGORIES = {
    "school": f"{BASE}/ar/Results/{quote('مدارس')}",
    "nursery": f"{BASE}/ar/Results/{quote('حضانات')}",
}
USER_AGENT = "EduHubResearchBot/0.4 (+https://github.com/admonkstudio/edu-hub; public-source-acquisition)"


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=4,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "ar,en;q=0.8"})
    return s


def clean(v: str | None) -> str | None:
    if v is None:
        return None
    v = re.sub(r"\s+", " ", v).strip()
    return v or None


def item_id_from_href(href: str) -> str | None:
    m = re.search(r"/(?:ar|en)/item/(\d+)(?:/|$)", urlparse(href).path, re.I)
    return m.group(1) if m else None


def canonical_item_url(href: str, source_id: str) -> str:
    absolute = urljoin(BASE, href)
    p = urlparse(absolute)
    path = p.path or f"/ar/Item/{source_id}"
    return f"{p.scheme or 'https'}://{p.netloc or 'madaresegypt.com'}{path}"


def discover_items(s: requests.Session, max_pages: int, delay: float) -> dict[str, dict]:
    items: dict[str, dict] = {}
    for category, base_url in CATEGORIES.items():
        empty_streak = 0
        previous_page_ids: tuple[str, ...] | None = None
        for page in range(1, max_pages + 1):
            url = base_url if page == 1 else f"{base_url}?page={page}"
            r = s.get(url, timeout=60)
            if r.status_code == 404:
                break
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            page_ids: list[str] = []
            before = len(items)
            for a in soup.find_all("a", href=True):
                href = urljoin(BASE, a.get("href", ""))
                sid = item_id_from_href(href)
                if not sid:
                    continue
                page_ids.append(sid)
                label = clean(a.get_text(" ", strip=True))
                row = items.setdefault(
                    sid,
                    {
                        "source_record_id": sid,
                        "source_url": canonical_item_url(href, sid),
                        "categories": set(),
                        "listing_names": set(),
                        "listing_urls": set(),
                    },
                )
                row["categories"].add(category)
                row["listing_urls"].add(url)
                if label:
                    row["listing_names"].add(label)
            unique_page = tuple(sorted(set(page_ids)))
            new_count = len(items) - before
            print(json.dumps({
                "stage": "listing",
                "category": category,
                "page": page,
                "page_items": len(unique_page),
                "new": new_count,
                "total": len(items),
            }, ensure_ascii=False))
            if not unique_page or unique_page == previous_page_ids or new_count == 0:
                empty_streak += 1
            else:
                empty_streak = 0
            previous_page_ids = unique_page
            if empty_streak >= 3:
                break
            time.sleep(delay)
    return items


def strip_non_factual(soup: BeautifulSoup) -> None:
    selectors = (
        "script", "style", "noscript", "form", "iframe", "video", "audio",
        "#comments", ".comments", ".comment", ".comment-list",
        "[class*='review']", "[id*='review']", "[class*='rating']", "[id*='rating']",
        "[class*='gallery']", "[id*='gallery']", "[class*='album']", "[id*='album']",
    )
    for sel in selectors:
        for node in soup.select(sel):
            node.decompose()


def section_values(heading) -> list[str]:
    vals: list[str] = []
    for sib in heading.next_siblings:
        name = getattr(sib, "name", None)
        if name and re.match(r"^h[1-6]$", name):
            break
        if hasattr(sib, "get_text"):
            txt = clean(sib.get_text(" ", strip=True))
        elif isinstance(sib, str):
            txt = clean(sib)
        else:
            txt = None
        if txt and txt not in vals:
            vals.append(txt)
        if sum(len(x) for x in vals) > 12000:
            break
    return vals[:40]


def extract_coordinates(urls: list[str]) -> tuple[float | None, float | None]:
    patterns = (
        r"[?&](?:q|query)=(-?\d{1,2}\.\d+),\s*(-?\d{1,3}\.\d+)",
        r"@(-?\d{1,2}\.\d+),(-?\d{1,3}\.\d+)",
    )
    for url in urls:
        for pat in patterns:
            m = re.search(pat, url)
            if m:
                lat, lon = float(m.group(1)), float(m.group(2))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return lat, lon
    return None, None


def parse_profile(source_id: str, discovered: dict, html: str, final_url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title_node = soup.find("h1")
    name = clean(title_node.get_text(" ", strip=True) if title_node else None)
    meta = soup.find("meta", attrs={"name": "description"})
    meta_description = clean(meta.get("content") if meta else None)

    # Capture contacts/maps before stripping non-factual UI blocks.
    contacts = defaultdict(list)
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        low = href.lower()
        if low.startswith("tel:"):
            contacts["phones"].append(href[4:].strip())
        elif low.startswith("mailto:"):
            contacts["emails"].append(href[7:].strip())
        elif any(x in low for x in ("google.com/maps", "maps.google.", "goo.gl/maps", "maps.app.goo.gl")):
            contacts["maps"].append(href)
        elif low.startswith("http") and urlparse(href).netloc not in {"madaresegypt.com", "www.madaresegypt.com", "images.madaresegypt.com"}:
            if "facebook.com" in low:
                contacts["facebook"].append(href)
            elif "instagram.com" in low:
                contacts["instagram"].append(href)
            elif "youtube.com" in low or "youtu.be" in low:
                contacts["youtube"].append(href)
            else:
                contacts["websites"].append(href)
    contacts = {k: list(dict.fromkeys(v))[:30] for k, v in contacts.items()}
    lat, lon = extract_coordinates(contacts.get("maps", []))

    strip_non_factual(soup)
    sections: dict[str, list[str]] = {}
    for heading in soup.find_all(re.compile(r"^h[2-6]$")):
        key = clean(heading.get_text(" ", strip=True))
        if not key:
            continue
        vals = section_values(heading)
        if vals:
            sections[key] = vals

    tables: list[list[list[str]]] = []
    for table in soup.find_all("table"):
        rows: list[list[str]] = []
        for tr in table.find_all("tr"):
            cells = [clean(c.get_text(" ", strip=True)) or "" for c in tr.find_all(["th", "td"])]
            if any(cells):
                rows.append(cells)
        if rows:
            tables.append(rows[:200])

    breadcrumb = []
    for nav in soup.find_all(["nav", "ol", "ul"]):
        text_value = clean(nav.get_text(" > ", strip=True))
        if text_value and any(x in text_value for x in ("الرئيسية", "مدارس", "حضانات")):
            breadcrumb.append(text_value[:1000])
            if len(breadcrumb) >= 3:
                break

    all_text = clean(soup.get_text(" ", strip=True)) or ""
    return {
        "source_record_id": source_id,
        "source_url": final_url,
        "name_raw": name or (sorted(discovered["listing_names"])[0] if discovered["listing_names"] else None),
        "entity_type_raw": "+".join(sorted(discovered["categories"])),
        "location_raw": None,
        "latitude": lat,
        "longitude": lon,
        "payload": {
            "categories": sorted(discovered["categories"]),
            "listing_names": sorted(discovered["listing_names"]),
            "listing_urls": sorted(discovered["listing_urls"]),
            "title": name,
            "meta_description": meta_description,
            "breadcrumb": breadcrumb,
            "sections": sections,
            "tables": tables,
            "contacts": contacts,
            "text_excerpt": all_text[:30000],
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="artifacts/madaresegypt_snapshot.jsonl")
    ap.add_argument("--max-pages", type=int, default=1000)
    ap.add_argument("--max-profiles", type=int, default=0)
    ap.add_argument("--delay", type=float, default=0.20)
    args = ap.parse_args()

    s = session()
    discovered = discover_items(s, args.max_pages, args.delay)
    ordered = sorted(discovered.items(), key=lambda kv: int(kv[0]))
    if args.max_profiles > 0:
        ordered = ordered[: args.max_profiles]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    errors = 0
    with out.open("w", encoding="utf-8") as f:
        for index, (source_id, item) in enumerate(ordered, start=1):
            url = item["source_url"]
            try:
                r = s.get(url, timeout=60, allow_redirects=True)
                r.raise_for_status()
                f.write(json.dumps(parse_profile(source_id, item, r.text, r.url), ensure_ascii=False) + "\n")
                written += 1
            except Exception as exc:
                errors += 1
                print(json.dumps({"stage": "profile_error", "id": source_id, "url": url, "error": repr(exc)}, ensure_ascii=False))
            if index % 100 == 0:
                print(json.dumps({"stage": "profiles", "processed": index, "written": written, "errors": errors, "total": len(ordered)}, ensure_ascii=False))
            time.sleep(args.delay)

    print(json.dumps({"ok": True, "discovered": len(discovered), "written": written, "errors": errors, "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
