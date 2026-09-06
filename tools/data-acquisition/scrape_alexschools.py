#!/usr/bin/env python3
"""Acquire public Alexandria school directory records from alexschools.info.

Secondary discovery source only. The crawler retains factual public profile text and
basic contact/taxonomy metadata, while excluding reviews/comments, share controls and
media bodies. Values remain source-specific raw evidence; nothing here is canonical.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://alexschools.info"
ARCHIVE = BASE + "/listings/"
UA = "EduHubResearchBot/1.6 (+https://github.com/admonkstudio/edu-hub; public-source-acquisition)"

SOURCE_HOSTS = {
    "alexschools.info",
    "www.alexschools.info",
    "egyptschools.info",
    "www.egyptschools.info",
    "shop.egyptschools.info",
    "alexschools.b-cdn.net",
}
EXCLUDED_EXTERNAL_HOSTS = {
    "facebook.com", "www.facebook.com", "m.facebook.com",
    "instagram.com", "www.instagram.com",
    "youtube.com", "www.youtube.com", "youtu.be",
    "twitter.com", "www.twitter.com", "x.com", "www.x.com",
    "api.whatsapp.com", "wa.me",
    "telegram.me", "t.me",
    "pinterest.com", "www.pinterest.com",
    "linkedin.com", "www.linkedin.com",
    "tumblr.com", "www.tumblr.com",
    "reddit.com", "www.reddit.com",
    "vk.com", "www.vk.com",
    "nagdy.net", "www.nagdy.net",
}
MEDIA_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".pdf", ".mp4", ".webm")
EMAIL_RE = re.compile(r"^[^\s@?]+@[^\s@?]+\.[^\s@?]+$")


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=4,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": UA, "Accept-Language": "ar,en;q=0.8"})
    return s


def clean(v: str | None) -> str | None:
    if not v:
        return None
    v = re.sub(r"\s+", " ", v).strip()
    return v or None


def source_id(url: str) -> str:
    return "alexschools-" + hashlib.sha256(url.encode()).hexdigest()[:18]


def discover(s: requests.Session, max_pages: int, delay: float) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for page in range(1, max_pages + 1):
        u = ARCHIVE if page == 1 else f"{ARCHIVE}page/{page}/"
        r = s.get(u, timeout=45)
        if r.status_code == 404:
            print(json.dumps({"stage": "archive_end", "page": page, "reason": "404", "total": len(found)}, ensure_ascii=False), flush=True)
            break
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        page_urls = []
        for a in soup.find_all("a", href=True):
            href = urljoin(r.url, a.get("href", ""))
            if urlparse(href).netloc not in {"alexschools.info", "www.alexschools.info"}:
                continue
            if "/school/" not in urlparse(href).path:
                continue
            label = clean(a.get_text(" ", strip=True))
            if not label:
                continue
            page_urls.append(href)
            row = found.setdefault(href, {"source_url": href, "listing_names": set(), "listing_pages": set()})
            row["listing_names"].add(label)
            row["listing_pages"].add(r.url)
        print(json.dumps({"stage": "archive", "page": page, "profiles_on_page": len(set(page_urls)), "total": len(found)}, ensure_ascii=False), flush=True)
        if not page_urls:
            break
        if delay:
            time.sleep(delay)
    return found


def strip_non_factual(soup: BeautifulSoup) -> None:
    selectors = (
        "script", "style", "noscript", "iframe", "form", "nav", "footer",
        "#comments", ".comments", ".comment",
        "[class*='review']", "[id*='review']", "[class*='rating']", "[id*='rating']",
        "[class*='gallery']", "[id*='gallery']", "[class*='share']", "[id*='share']",
        "[class*='social']", "[id*='social']",
    )
    for sel in selectors:
        for node in soup.select(sel):
            node.decompose()


def is_external_website_candidate(href: str) -> bool:
    try:
        p = urlparse(href)
    except ValueError:
        return False
    if p.scheme not in {"http", "https"}:
        return False
    host = p.netloc.lower().split(":", 1)[0]
    if host in SOURCE_HOSTS or host in EXCLUDED_EXTERNAL_HOSTS:
        return False
    if any(host.endswith("." + h) for h in EXCLUDED_EXTERNAL_HOSTS):
        return False
    path = p.path.lower()
    if path.endswith(MEDIA_EXTENSIONS):
        return False
    if any(token in path for token in ("/share", "/sharer", "/submit")):
        return False
    return True


def coords_from_map_url(href: str) -> dict[str, float] | None:
    try:
        p = urlparse(href)
        qs = parse_qs(p.query)
    except ValueError:
        return None
    values = []
    for key in ("daddr", "q", "query", "ll", "destination"):
        values.extend(qs.get(key, []))
    values.append(href)
    for value in values:
        m = re.search(r"(-?\d{1,2}\.\d+)\s*[,\s]%?2C?\s*(-?\d{1,3}\.\d+)", value, re.I)
        if not m:
            m = re.search(r"(-?\d{1,2}\.\d+)%2C(-?\d{1,3}\.\d+)", value, re.I)
        if m:
            lat, lon = float(m.group(1)), float(m.group(2))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return {"latitude": lat, "longitude": lon}
    return None


def extract_address(text: str, name: str) -> str | None:
    map_markers = ["الموقع علي الخريطة", "الموقع على الخريطة", "الموقع علي خريطة", "الموقع على خريطة"]
    map_pos = max((text.rfind(marker) for marker in map_markers), default=-1)
    if map_pos < 0:
        return None
    addr_pos = text.rfind("عنوان ", 0, map_pos)
    if addr_pos < 0:
        return None
    raw = clean(text[addr_pos + len("عنوان "):map_pos])
    if not raw:
        return None
    # The source usually renders "عنوان <school name> <address>".
    if raw.startswith(name):
        raw = clean(raw[len(name):])
    else:
        # Normalize dash variants only for prefix removal; retain the source address text itself.
        raw_norm = raw.replace("–", "-").replace("—", "-")
        name_norm = name.replace("–", "-").replace("—", "-")
        if raw_norm.startswith(name_norm):
            raw = clean(raw[len(name):])
    return raw


def extract_profile_taxonomy_text(text: str, name: str) -> dict[str, str]:
    """Preserve label-delimited profile metadata as raw source text.

    We deliberately do not split these values into canonical terms here; that belongs
    to the later taxonomy/matching layer.
    """
    start_candidates = [f"عن {name}", f"عن {name.replace(' - ', ' – ')}"]
    start = -1
    for marker in start_candidates:
        start = text.find(marker)
        if start >= 0:
            start += len(marker)
            break
    end_candidates = [f"معلومات عن {name}", "معلومات عن"]
    end = -1
    if start >= 0:
        for marker in end_candidates:
            end = text.find(marker, start)
            if end >= 0:
                break
    block = text[start:end] if start >= 0 and end > start else ""
    if not block:
        return {}

    labels = [
        ("نوع", "type"),
        ("لغات", "languages"),
        ("اللغة الثانية الإضافية في", "second_language"),
        ("الشهادة الممنوحة من", "certificates"),
        ("مراحل", "stages"),
        ("جهات اعتماد", "accreditations"),
        ("تلاميذ", "gender"),
    ]
    positions = []
    for label, key in labels:
        pos = block.find(label)
        if pos >= 0:
            positions.append((pos, label, key))
    positions.sort()
    out: dict[str, str] = {}
    for i, (pos, label, key) in enumerate(positions):
        value_start = pos + len(label)
        value_end = positions[i + 1][0] if i + 1 < len(positions) else len(block)
        value = clean(block[value_start:value_end])
        if value:
            out[key] = value
    return out


def parse_profile(url: str, discovered: dict, html: str, final_url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    name = clean(h1.get_text(" ", strip=True) if h1 else None) or sorted(discovered["listing_names"])[0]

    contacts = {"phones": [], "emails": [], "websites": [], "maps": []}
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        low = href.lower()
        if low.startswith("tel:"):
            value = clean(href[4:])
            if value:
                contacts["phones"].append(value)
        elif low.startswith("mailto:"):
            value = href[7:].split("?", 1)[0].strip()
            if EMAIL_RE.match(value):
                contacts["emails"].append(value)
        elif any(x in low for x in ("google.com/maps", "maps.google.", "maps.app.goo.gl", "goo.gl/maps")):
            contacts["maps"].append(href)
        elif is_external_website_candidate(href):
            contacts["websites"].append(href)
    contacts = {k: list(dict.fromkeys(v))[:30] for k, v in contacts.items()}

    text_before = " ".join(soup.get_text(" ", strip=True).split())

    fee = None
    m = re.search(r"تبدأ\s+المصاريف\s+من\s*(?:LE|جنيه)?\s*([0-9٠-٩][0-9٠-٩,\.٬،\s]*)", text_before, re.I)
    if m:
        fee = clean(m.group(1))
        if fee:
            fee = re.sub(r"\s+(?=\D|$)", "", fee)

    map_coordinates = None
    for map_url in contacts["maps"]:
        map_coordinates = coords_from_map_url(map_url)
        if map_coordinates:
            break

    address = extract_address(text_before, name)
    profile_taxonomy_text = extract_profile_taxonomy_text(text_before, name)

    # Retain DOM-derived blocks too when the theme exposes true headings.
    taxonomy_blocks = {}
    heading_keys = {
        "لغات": "languages", "مراحل": "stages", "جهات اعتماد": "accreditations", "تلاميذ": "gender",
        "نوع": "type", "معلومات إضافية": "features", "وسائل اتصال": "contacts_block",
    }
    for h in soup.find_all(re.compile(r"^h[2-6]$")):
        ht = clean(h.get_text(" ", strip=True)) or ""
        key = next((v for k, v in heading_keys.items() if k in ht), None)
        if not key:
            continue
        vals = []
        node = h
        for _ in range(8):
            node = node.find_next_sibling()
            if node is None or (getattr(node, "name", "") and re.match(r"^h[2-6]$", node.name)):
                break
            if hasattr(node, "get_text"):
                t = clean(node.get_text(" | ", strip=True))
                if t and t not in vals:
                    vals.append(t)
        if vals:
            taxonomy_blocks[key] = vals[:30]

    strip_non_factual(soup)
    factual_text = clean(soup.get_text(" ", strip=True)) or ""
    return {
        "source_record_id": source_id(final_url),
        "source_url": final_url,
        "name_raw": name,
        "entity_type_raw": "school",
        "location_raw": address,
        "latitude": map_coordinates["latitude"] if map_coordinates else None,
        "longitude": map_coordinates["longitude"] if map_coordinates else None,
        "payload": {
            "source_class": "secondary_directory",
            "archive_names": sorted(discovered["listing_names"]),
            "archive_pages": sorted(discovered["listing_pages"]),
            "starting_fee_raw": fee,
            "profile_taxonomy_text": profile_taxonomy_text,
            "taxonomy_blocks": taxonomy_blocks,
            "contacts": contacts,
            "factual_text_excerpt": factual_text[:40000],
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="artifacts/alexschools.jsonl")
    ap.add_argument("--max-pages", type=int, default=20)
    ap.add_argument("--delay", type=float, default=.35)
    args = ap.parse_args()

    s = session()
    discovered = discover(s, args.max_pages, args.delay)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    errors = []
    field_counts = {
        "named": 0, "location": 0, "coordinates": 0, "starting_fee": 0,
        "phones": 0, "emails": 0, "websites": 0, "maps": 0, "profile_taxonomy_text": 0,
    }

    with out.open("w", encoding="utf-8") as f:
        for i, (u, row) in enumerate(sorted(discovered.items()), 1):
            try:
                r = s.get(u, timeout=45, allow_redirects=True)
                r.raise_for_status()
                record = parse_profile(u, row, r.text, r.url)
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                written += 1
                field_counts["named"] += bool(record.get("name_raw"))
                field_counts["location"] += bool(record.get("location_raw"))
                field_counts["coordinates"] += bool(record.get("latitude") is not None and record.get("longitude") is not None)
                payload = record["payload"]
                field_counts["starting_fee"] += bool(payload.get("starting_fee_raw"))
                field_counts["profile_taxonomy_text"] += bool(payload.get("profile_taxonomy_text"))
                for k in ("phones", "emails", "websites", "maps"):
                    field_counts[k] += bool(payload["contacts"].get(k))
            except Exception as e:
                errors.append({"url": u, "error": repr(e)})
            if i % 25 == 0:
                print(json.dumps({"stage": "profiles", "processed": i, "written": written, "errors": len(errors)}, ensure_ascii=False), flush=True)
            if args.delay:
                time.sleep(args.delay)

    report = {
        "ok": not errors,
        "discovered": len(discovered),
        "written": written,
        "errors": errors,
        "field_counts": field_counts,
        "output": str(out),
    }
    Path(out.with_suffix(".report.json")).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
