#!/usr/bin/env python3
"""Acquire public institution facts from MasrSchools without importing reviews/media."""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://masrschools.com"
LISTING = f"{BASE}/schools/"
USER_AGENT = "EduHubResearchBot/0.2 (+https://github.com/admonkstudio/edu-hub; public-source-acquisition)"
RESERVED = {
    "", "schools", "articles", "contact", "privacy-policy", "add-school", "edit-school",
    "governorate", "category", "tag", "author", "wp-admin", "wp-login.php", "feed",
}


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=4, backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("GET",))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "ar,en;q=0.8"})
    return s


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def school_links(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(BASE, a.get("href"))
        p = urlparse(href)
        if p.netloc not in {"masrschools.com", "www.masrschools.com"}:
            continue
        parts = [x for x in p.path.split("/") if x]
        if len(parts) != 1 or parts[0].lower() in RESERVED:
            continue
        text = clean_text(a.get_text(" ", strip=True)) or ""
        # Listing cards include a fee/contact phrase. This avoids nav/editorial links.
        if not any(token in text for token in ("المصروفات", "تواصل مع المدرسة", "مدرسة", "معهد")):
            continue
        canonical = f"{BASE}/{parts[0]}/"
        if canonical not in seen:
            out.append((canonical, text))
            seen.add(canonical)
    return out


def strip_ugc(soup: BeautifulSoup) -> None:
    # Do not acquire parent/user reviews, comments, forms, media or scripts.
    for sel in (
        "script", "style", "noscript", "form", "#comments", ".comments", ".comment-list",
        ".comment", "[class*='review']", "[id*='review']", "[class*='rating']", "[id*='rating']",
    ):
        for node in soup.select(sel):
            node.decompose()


def parse_profile(url: str, listing_text: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    strip_ugc(soup)
    h1 = soup.find("h1")
    title = clean_text(h1.get_text(" ", strip=True) if h1 else None)
    meta = soup.find("meta", attrs={"name": "description"})
    meta_description = clean_text(meta.get("content") if meta else None)

    sections: dict[str, list[str]] = {}
    for heading in soup.find_all(re.compile(r"^h[2-6]$")):
        key = clean_text(heading.get_text(" ", strip=True))
        if not key:
            continue
        vals: list[str] = []
        for sib in heading.next_siblings:
            if getattr(sib, "name", None) and re.match(r"^h[2-6]$", sib.name or ""):
                break
            if hasattr(sib, "get_text"):
                txt = clean_text(sib.get_text(" ", strip=True))
                if txt and txt not in vals:
                    vals.append(txt)
            elif isinstance(sib, str):
                txt = clean_text(sib)
                if txt and txt not in vals:
                    vals.append(txt)
            if sum(len(x) for x in vals) > 6000:
                break
        if vals:
            sections[key] = vals[:20]

    tables: list[list[list[str]]] = []
    for table in soup.find_all("table"):
        rows: list[list[str]] = []
        for tr in table.find_all("tr"):
            cells = [clean_text(c.get_text(" ", strip=True)) or "" for c in tr.find_all(["th", "td"])]
            if any(cells):
                rows.append(cells)
        if rows:
            tables.append(rows[:100])

    contacts = {"phones": [], "emails": [], "websites": [], "maps": []}
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        text = clean_text(a.get_text(" ", strip=True))
        if href.startswith("tel:"):
            contacts["phones"].append(href[4:].strip())
        elif href.startswith("mailto:"):
            contacts["emails"].append(href[7:].strip())
        elif "google." in href or "maps." in href or "goo.gl/maps" in href:
            contacts["maps"].append(href)
        elif href.startswith("http") and urlparse(href).netloc not in {"masrschools.com", "www.masrschools.com"}:
            if not any(x in href for x in ("facebook.com", "instagram.com", "youtube.com", "twitter.com", "x.com", "tiktok.com")):
                contacts["websites"].append(href)
    contacts = {k: list(dict.fromkeys(v))[:20] for k, v in contacts.items()}

    jsonld = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = tag.string or tag.get_text()
        try:
            jsonld.append(json.loads(raw))
        except Exception:
            continue

    slug = [x for x in urlparse(url).path.split("/") if x][0]
    return {
        "source_record_id": slug,
        "source_url": url,
        "name_raw": title,
        "entity_type_raw": None,
        "location_raw": None,
        "listing_text": listing_text,
        "payload": {
            "title": title,
            "meta_description": meta_description,
            "listing_text": listing_text,
            "sections": sections,
            "tables": tables,
            "contacts": contacts,
            "jsonld": jsonld,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="artifacts/masrschools_snapshot.jsonl")
    ap.add_argument("--max-pages", type=int, default=1000)
    ap.add_argument("--max-profiles", type=int, default=0, help="0 = all discovered")
    ap.add_argument("--delay", type=float, default=0.25)
    args = ap.parse_args()

    s = session()
    discovered: dict[str, str] = {}
    empty_streak = 0
    for page in range(1, args.max_pages + 1):
        url = LISTING if page == 1 else f"{LISTING}?page={page}"
        r = s.get(url, timeout=60)
        r.raise_for_status()
        found = school_links(r.text)
        before = len(discovered)
        for href, text in found:
            discovered.setdefault(href, text)
        new = len(discovered) - before
        print(json.dumps({"stage": "listing", "page": page, "found": len(found), "new": new, "total": len(discovered)}, ensure_ascii=False))
        empty_streak = empty_streak + 1 if new == 0 else 0
        if empty_streak >= 2:
            break
        time.sleep(args.delay)

    items = list(discovered.items())
    if args.max_profiles > 0:
        items = items[: args.max_profiles]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    ok = 0
    with out.open("w", encoding="utf-8") as f:
        for i, (url, listing_text) in enumerate(items, start=1):
            try:
                r = s.get(url, timeout=60)
                r.raise_for_status()
                row = parse_profile(url, listing_text, r.text)
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                ok += 1
            except Exception as exc:
                print(json.dumps({"stage": "profile_error", "url": url, "error": repr(exc)}, ensure_ascii=False))
            if i % 100 == 0:
                print(json.dumps({"stage": "profiles", "processed": i, "written": ok, "total": len(items)}, ensure_ascii=False))
            time.sleep(args.delay)
    print(json.dumps({"ok": True, "discovered": len(discovered), "written": ok, "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
