#!/usr/bin/env python3
"""Acquire public Alexandria school directory records from alexschools.info.

Secondary discovery source only. The crawler retains factual public profile text and
basic contact/taxonomy metadata, while excluding reviews/comments and media bodies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://alexschools.info"
ARCHIVE = BASE + "/listings/"
UA = "EduHubResearchBot/1.5 (+https://github.com/admonkstudio/edu-hub; public-source-acquisition)"


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=4, backoff_factor=1.0, status_forcelist=(429,500,502,503,504), allowed_methods=("GET",), respect_retry_after_header=True)
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": UA, "Accept-Language": "ar,en;q=0.8"})
    return s


def clean(v: str | None) -> str | None:
    if not v: return None
    v = re.sub(r"\s+", " ", v).strip()
    return v or None


def source_id(url: str) -> str:
    return "alexschools-" + hashlib.sha256(url.encode()).hexdigest()[:18]


def discover(s: requests.Session, max_pages: int, delay: float) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for page in range(1, max_pages + 1):
        u = ARCHIVE if page == 1 else f"{ARCHIVE}page/{page}/"
        r = s.get(u, timeout=45); r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        page_urls = []
        for a in soup.find_all("a", href=True):
            href = urljoin(r.url, a.get("href", ""))
            if urlparse(href).netloc not in {"alexschools.info", "www.alexschools.info"}: continue
            if "/school/" not in urlparse(href).path: continue
            label = clean(a.get_text(" ", strip=True))
            if not label: continue
            page_urls.append(href)
            row = found.setdefault(href, {"source_url": href, "listing_names": set(), "listing_pages": set()})
            row["listing_names"].add(label); row["listing_pages"].add(r.url)
        print(json.dumps({"stage":"archive","page":page,"profiles_on_page":len(set(page_urls)),"total":len(found)}, ensure_ascii=False), flush=True)
        if not page_urls: break
        if delay: time.sleep(delay)
    return found


def strip_non_factual(soup: BeautifulSoup) -> None:
    for sel in ("script","style","noscript","iframe","form","#comments",".comments",".comment","[class*='review']","[id*='review']","[class*='rating']","[id*='rating']","[class*='gallery']","[id*='gallery']"):
        for node in soup.select(sel): node.decompose()


def parse_profile(url: str, discovered: dict, html: str, final_url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    name = clean(h1.get_text(" ", strip=True) if h1 else None) or sorted(discovered["listing_names"])[0]

    contacts = {"phones": [], "emails": [], "websites": [], "maps": []}
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip(); low = href.lower()
        if low.startswith("tel:"): contacts["phones"].append(href[4:].strip())
        elif low.startswith("mailto:"): contacts["emails"].append(href[7:].strip())
        elif any(x in low for x in ("google.com/maps","maps.google.","maps.app.goo.gl","goo.gl/maps")): contacts["maps"].append(href)
        elif low.startswith("http") and urlparse(href).netloc not in {"alexschools.info","www.alexschools.info","egyptschools.info","shop.egyptschools.info"}:
            if not any(x in low for x in ("facebook.com","instagram.com","youtube.com","youtu.be","twitter.com","x.com")):
                contacts["websites"].append(href)
    contacts = {k:list(dict.fromkeys(v))[:30] for k,v in contacts.items()}

    fee = None
    text_before = " ".join(soup.get_text(" ", strip=True).split())
    m = re.search(r"تبدأ\s+المصاريف\s+من\s*(?:LE|جنيه)?\s*([0-9][0-9,\.]*)", text_before, re.I)
    if m: fee = m.group(1)

    # Capture public taxonomy labels by nearby section headings/blocks.
    tax = {}
    heading_keys = {
        "لغات":"languages", "مراحل":"stages", "جهات اعتماد":"accreditations", "تلاميذ":"gender",
        "نوع":"type", "معلومات إضافية":"features", "وسائل اتصال":"contacts_block"
    }
    for h in soup.find_all(re.compile(r"^h[2-6]$")):
        ht = clean(h.get_text(" ", strip=True)) or ""
        key = next((v for k,v in heading_keys.items() if k in ht), None)
        if not key: continue
        vals=[]
        node=h
        for _ in range(8):
            node=node.find_next_sibling()
            if node is None or (getattr(node,"name","") and re.match(r"^h[2-6]$", node.name)): break
            if hasattr(node,"get_text"):
                t=clean(node.get_text(" | ",strip=True))
                if t and t not in vals: vals.append(t)
        if vals: tax[key]=vals[:30]

    strip_non_factual(soup)
    factual_text = clean(soup.get_text(" ", strip=True)) or ""
    return {
        "source_record_id": source_id(final_url),
        "source_url": final_url,
        "name_raw": name,
        "entity_type_raw": "school",
        "location_raw": None,
        "payload": {
            "source_class": "secondary_directory",
            "archive_names": sorted(discovered["listing_names"]),
            "archive_pages": sorted(discovered["listing_pages"]),
            "starting_fee_raw": fee,
            "taxonomy_blocks": tax,
            "contacts": contacts,
            "factual_text_excerpt": factual_text[:40000],
        },
    }


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",default="artifacts/alexschools.jsonl"); ap.add_argument("--max-pages",type=int,default=20); ap.add_argument("--delay",type=float,default=.35)
    args=ap.parse_args(); s=session(); discovered=discover(s,args.max_pages,args.delay)
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    written=0; errors=[]
    with out.open("w",encoding="utf-8") as f:
        for i,(u,row) in enumerate(sorted(discovered.items()),1):
            try:
                r=s.get(u,timeout=45,allow_redirects=True); r.raise_for_status()
                f.write(json.dumps(parse_profile(u,row,r.text,r.url),ensure_ascii=False)+"\n"); written+=1
            except Exception as e:
                errors.append({"url":u,"error":repr(e)})
            if i%25==0: print(json.dumps({"stage":"profiles","processed":i,"written":written,"errors":len(errors)},ensure_ascii=False),flush=True)
            if args.delay: time.sleep(args.delay)
    report={"ok":not errors,"discovered":len(discovered),"written":written,"errors":errors,"output":str(out)}
    Path(out.with_suffix('.report.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__ == "__main__": main()
