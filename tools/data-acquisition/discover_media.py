#!/usr/bin/env python3
"""Discover public media candidates from previously acquired institution profile URLs.

This is a source-level discovery pass, not a copyright/publication decision.
It never rewrites canonical data and it does not require an external API.
"""
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

UA = "EduHubResearchBot/2.0 (+https://github.com/admonkstudio/edu-hub; public-media-discovery)"
SKIP_SCHEMES = ("data:", "javascript:", "mailto:", "tel:")
SKIP_TOKENS = (
    "favicon", "sprite", "emoji", "smiley", "spinner", "loading", "placeholder",
    "blank.gif", "pixel.gif", "tracking", "avatar-default", "gravatar.com/avatar",
)


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=3,
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


def resolve(base: str, value: str | None) -> str | None:
    value = clean(value)
    if not value or value.lower().startswith(SKIP_SCHEMES):
        return None
    try:
        url = urljoin(base, value)
        p = urlparse(url)
    except ValueError:
        return None
    if p.scheme not in {"http", "https"} or not p.netloc:
        return None
    low = url.lower()
    if any(token in low for token in SKIP_TOKENS):
        return None
    return url


def infer_role(url: str, alt: str | None, method: str) -> str:
    text = " ".join(x for x in (url, alt or "", method) if x).lower()
    if "logo" in text or "شعار" in text:
        return "logo_candidate"
    if method in {"og:image", "twitter:image"}:
        return "featured_candidate"
    if any(t in text for t in ("gallery", "campus", "school", "class", "building", "facility", "slider", "slide")):
        return "gallery_candidate"
    return "image_candidate"


def srcset_urls(base: str, value: str | None) -> list[str]:
    if not value:
        return []
    out = []
    for chunk in value.split(","):
        candidate = chunk.strip().split(" ", 1)[0]
        u = resolve(base, candidate)
        if u:
            out.append(u)
    return out


def discover_from_html(page_url: str, html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[dict] = []

    def add(url: str | None, method: str, *, alt: str | None = None, title: str | None = None,
            width: str | int | None = None, height: str | int | None = None) -> None:
        u = resolve(page_url, url)
        if not u:
            return
        try:
            w = int(width) if width not in (None, "") else None
        except (TypeError, ValueError):
            w = None
        try:
            h = int(height) if height not in (None, "") else None
        except (TypeError, ValueError):
            h = None
        candidates.append({
            "media_url": u,
            "role_raw": infer_role(u, clean(alt), method),
            "alt_raw": clean(alt),
            "title_raw": clean(title),
            "width_hint": w,
            "height_hint": h,
            "discovery_method": method,
        })

    for prop in ("og:image", "og:image:url", "twitter:image", "twitter:image:src"):
        meta = soup.find("meta", attrs={"property": prop}) or soup.find("meta", attrs={"name": prop})
        if meta:
            add(meta.get("content"), prop)

    for img in soup.find_all("img"):
        alt = img.get("alt")
        title = img.get("title")
        width = img.get("width")
        height = img.get("height")
        for attr in ("src", "data-src", "data-lazy-src", "data-original", "data-image", "data-url"):
            if img.get(attr):
                add(img.get(attr), f"img:{attr}", alt=alt, title=title, width=width, height=height)
        for attr in ("srcset", "data-srcset"):
            for u in srcset_urls(page_url, img.get(attr)):
                add(u, f"img:{attr}", alt=alt, title=title, width=width, height=height)

    # Some galleries use anchor tags around full-resolution images.
    for a in soup.find_all("a", href=True):
        href = resolve(page_url, a.get("href"))
        if not href:
            continue
        path = urlparse(href).path.lower()
        if path.endswith((".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".svg")):
            add(href, "anchor:image", alt=a.get_text(" ", strip=True))

    out, seen = [], set()
    for item in candidates:
        url = item["media_url"]
        if url in seen:
            continue
        seen.add(url)
        out.append(item)
    return out


def iter_records(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Acquired source JSONL containing source_url/source_record_id")
    ap.add_argument("--output", required=True, help="Output media-candidate JSONL")
    ap.add_argument("--source-id", required=True)
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--max-records", type=int, default=0)
    args = ap.parse_args()

    src = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    s = session()

    processed = 0
    with_media = 0
    candidate_count = 0
    errors: list[dict] = []

    with out.open("w", encoding="utf-8") as f:
        for row in iter_records(src):
            if args.max_records and processed >= args.max_records:
                break
            page_url = row.get("source_url")
            if not page_url:
                continue
            processed += 1
            try:
                r = s.get(page_url, timeout=45, allow_redirects=True)
                r.raise_for_status()
                items = discover_from_html(r.url, r.text)
                if items:
                    with_media += 1
                for idx, item in enumerate(items, 1):
                    f.write(json.dumps({
                        "source_id": args.source_id,
                        "source_record_id": row.get("source_record_id"),
                        "source_page_url": r.url,
                        "source_name_raw": row.get("name_raw"),
                        "candidate_index": idx,
                        **item,
                    }, ensure_ascii=False) + "\n")
                    candidate_count += 1
            except Exception as exc:
                errors.append({"source_page_url": page_url, "error": repr(exc)})
            if processed % 50 == 0:
                print(json.dumps({
                    "processed": processed,
                    "records_with_media": with_media,
                    "media_candidates": candidate_count,
                    "errors": len(errors),
                }, ensure_ascii=False), flush=True)
            if args.delay:
                time.sleep(args.delay)

    report = {
        "ok": len(errors) == 0,
        "source_id": args.source_id,
        "records_processed": processed,
        "records_with_media": with_media,
        "media_candidates": candidate_count,
        "errors": errors,
        "output": str(out),
        "warning": "Media discovery does not establish redistribution/publication rights.",
    }
    Path(out.with_suffix(".report.json")).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
