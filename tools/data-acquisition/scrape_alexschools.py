#!/usr/bin/env python3
"""Acquire public Alexandria school directory records from alexschools.info.

Secondary discovery source only. The crawler retains factual public profile text,
contact/location evidence and source-labelled metadata while excluding reviews,
comments, share controls and media bodies. Values remain source-specific raw evidence;
nothing here is canonical and generic external links are not called official websites.
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
from bs4 import BeautifulSoup, NavigableString, Tag
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://alexschools.info"
ARCHIVE = BASE + "/listings/"
UA = "EduHubResearchBot/1.8 (+https://github.com/admonkstudio/edu-hub; public-source-acquisition)"

SOURCE_HOSTS = {
    "alexschools.info", "www.alexschools.info",
    "egyptschools.info", "www.egyptschools.info", "shop.egyptschools.info",
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
    "google.com", "www.google.com", "google.com.eg", "www.google.com.eg",
}
MEDIA_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".pdf", ".mp4", ".webm")
EMAIL_RE = re.compile(r"(?<![\w.+-])([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})(?![\w.-])", re.I)
HEADING_RE = re.compile(r"^h[2-6]$")
RAW_FIELD_HEADINGS = {
    "نوع": "type",
    "لغات": "languages",
    "اللغة الثانية الإضافية في": "second_language",
    "الشهادة الممنوحة من": "certificates",
    "مراحل": "stages",
    "جهات اعتماد": "accreditations",
    "تلاميذ": "gender",
    "مصروفات": "fees",
    "معلومات إضافية عن": "additional_information",
    "وسائل اتصال": "contact_information",
}


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=4, backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("GET",), respect_retry_after_header=True)
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
            if urlparse(href).netloc not in {"alexschools.info", "www.alexschools.info"} or "/school/" not in urlparse(href).path:
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


def is_external_link_candidate(href: str) -> bool:
    try:
        p = urlparse(href)
    except ValueError:
        return False
    if p.scheme not in {"http", "https"}:
        return False
    host = p.netloc.lower().split(":", 1)[0]
    if host in SOURCE_HOSTS or host in EXCLUDED_EXTERNAL_HOSTS or any(host.endswith("." + h) for h in EXCLUDED_EXTERNAL_HOSTS):
        return False
    path = p.path.lower()
    if path.endswith(MEDIA_EXTENSIONS) or any(token in path for token in ("/share", "/sharer", "/submit")):
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
        m = re.search(r"(-?\d{1,2}\.\d+)\s*[,\s]%?2C?\s*(-?\d{1,3}\.\d+)", value, re.I) or re.search(r"(-?\d{1,2}\.\d+)%2C(-?\d{1,3}\.\d+)", value, re.I)
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
    if raw.startswith(name):
        raw = clean(raw[len(name):])
    else:
        raw_norm = raw.replace("–", "-").replace("—", "-")
        name_norm = name.replace("–", "-").replace("—", "-")
        if raw_norm.startswith(name_norm):
            raw = clean(raw[len(name):])
    return raw


def text_between_headings(heading: Tag, stop_levels: set[str] | None = None) -> str | None:
    pieces: list[str] = []
    for node in heading.next_elements:
        if isinstance(node, Tag) and node is not heading and HEADING_RE.match(node.name or ""):
            if stop_levels is None or node.name in stop_levels:
                break
        if isinstance(node, NavigableString):
            if heading in node.parents:
                continue
            parent = node.parent
            if parent and parent.name in {"script", "style", "noscript"}:
                continue
            value = clean(str(node))
            if value and (not pieces or pieces[-1] != value):
                pieces.append(value)
    return clean(" | ".join(pieces))


def extract_heading_evidence(soup: BeautifulSoup) -> tuple[list[dict], dict[str, list[str]], str | None]:
    groups: list[dict] = []
    fields: dict[str, list[str]] = {}
    about_raw = None
    for h in soup.find_all(HEADING_RE):
        label = clean(h.get_text(" ", strip=True))
        if not label:
            continue
        value = text_between_headings(h)
        if value:
            groups.append({"heading": label, "value": value})
        normalized = label.rstrip(":：").strip()
        key = RAW_FIELD_HEADINGS.get(normalized)
        if key and value:
            fields.setdefault(key, [])
            if value not in fields[key]:
                fields[key].append(value)
        if h.name == "h2" and normalized.startswith("عن ") and about_raw is None:
            about_raw = text_between_headings(h, {"h2"})
    return groups[:80], fields, about_raw


def extract_contacts_and_links(soup: BeautifulSoup, contact_evidence: str | None) -> dict:
    phones: list[str] = []
    emails: list[str] = []
    maps: list[str] = []
    external_links: list[dict] = []
    website_candidates: list[dict] = []

    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        low = href.lower()
        label = clean(a.get_text(" ", strip=True))
        if low.startswith("tel:"):
            value = clean(href[4:])
            if value:
                phones.append(value)
        elif low.startswith("mailto:"):
            value = href[7:].split("?", 1)[0].strip()
            if value and EMAIL_RE.fullmatch(value):
                emails.append(value)
        elif any(x in low for x in ("google.com/maps", "maps.google.", "maps.app.goo.gl", "goo.gl/maps")):
            maps.append(href)
        elif is_external_link_candidate(href):
            item = {"url": href, "label": label}
            external_links.append(item)
            label_low = (label or "").lower()
            if any(token in label_low for token in ("website", "web site", "الموقع الرسمي", "الموقع الإلكتروني", "الموقع الالكتروني")):
                website_candidates.append(item)

    # The site often renders the institution email as plain text. Restrict regex
    # extraction to the source-labelled contact block so page-author/share emails
    # cannot leak into institution contact evidence.
    if contact_evidence:
        emails.extend(m.group(1) for m in EMAIL_RE.finditer(contact_evidence))

    def dedupe_strings(values: list[str]) -> list[str]:
        return list(dict.fromkeys(v.strip() for v in values if v and v.strip()))[:30]

    def dedupe_links(values: list[dict]) -> list[dict]:
        out, seen = [], set()
        for item in values:
            url = item.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            out.append(item)
        return out[:30]

    return {
        "phones": dedupe_strings(phones),
        "emails": dedupe_strings(emails),
        "maps": dedupe_strings(maps),
        "external_links": dedupe_links(external_links),
        "website_candidates": dedupe_links(website_candidates),
    }


def parse_profile(url: str, discovered: dict, html: str, final_url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    name = clean(h1.get_text(" ", strip=True) if h1 else None) or sorted(discovered["listing_names"])[0]
    text_before = " ".join(soup.get_text(" ", strip=True).split())

    heading_groups, profile_fields, profile_metadata_raw = extract_heading_evidence(soup)
    contact_evidence = " | ".join(profile_fields.get("contact_information", [])) or None
    contacts = extract_contacts_and_links(soup, contact_evidence)

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
            "profile_metadata_raw": profile_metadata_raw,
            "heading_groups_raw": heading_groups,
            "profile_fields_raw": profile_fields,
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
    written, errors = 0, []
    field_counts = {
        "named": 0, "location": 0, "coordinates": 0, "starting_fee": 0,
        "phones": 0, "emails": 0, "maps": 0, "external_links": 0,
        "website_candidates": 0, "profile_metadata_raw": 0, "profile_fields_raw": 0,
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
                field_counts["profile_metadata_raw"] += bool(payload.get("profile_metadata_raw"))
                field_counts["profile_fields_raw"] += bool(payload.get("profile_fields_raw"))
                contacts = payload["contacts"]
                for k in ("phones", "emails", "maps", "external_links", "website_candidates"):
                    field_counts[k] += bool(contacts.get(k))
            except Exception as e:
                errors.append({"url": u, "error": repr(e)})
            if i % 25 == 0:
                print(json.dumps({"stage": "profiles", "processed": i, "written": written, "errors": len(errors)}, ensure_ascii=False), flush=True)
            if args.delay:
                time.sleep(args.delay)

    report = {"ok": not errors, "discovered": len(discovered), "written": written, "errors": errors, "field_counts": field_counts, "output": str(out)}
    Path(out.with_suffix(".report.json")).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
