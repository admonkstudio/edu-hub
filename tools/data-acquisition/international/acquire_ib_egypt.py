#!/usr/bin/env python3
"""Acquire the current IB World School universe for Egypt.

EDU-DATA-2 scope rule:
- acquire every Egypt IB World School as raw evidence;
- only PRIVATE schools are automatically eligible for the active international
  school scope;
- state/public schools are retained as excluded evidence, not discarded;
- no data is published by this tool.

Outputs JSONL plus a summary suitable for later edu_raw ingestion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://ibo.org"
SEARCH_URL = BASE + "/programmes/find-an-ib-school/"
COUNTRY = "EG"
USER_AGENT = "EduHubResearch/2.0 (+https://github.com/admonkstudio/edu-hub)"
SCHOOL_RE = re.compile(r"/school/(\d+)/?$")
COUNT_RE = re.compile(r"Found\s+(\d+)\s+matching school", re.I)


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept-Language": "en,en-US;q=0.9,ar;q=0.7",
        }
    )
    return s


def result_links(html_text: str) -> tuple[int | None, list[dict]]:
    soup = BeautifulSoup(html_text, "html.parser")
    page_text = clean(soup.get_text(" ", strip=True))
    count_match = COUNT_RE.search(page_text)
    total = int(count_match.group(1)) if count_match else None

    rows: list[dict] = []
    seen: set[str] = set()
    for link in soup.find_all("a", href=True):
        href = str(link.get("href") or "")
        match = SCHOOL_RE.search(href)
        if not match:
            continue
        code = match.group(1)
        if code in seen:
            continue
        seen.add(code)
        row = link.find_parent("tr")
        programme_flags: dict[str, bool] = {}
        languages: list[str] = []
        if row is not None:
            cells = row.find_all("td")
            for idx, key in enumerate(("pyp", "myp", "dp", "cp"), start=1):
                if len(cells) > idx:
                    blob = clean(cells[idx].get_text(" ", strip=True)).casefold()
                    programme_flags[key] = bool(blob and blob not in {"-", "no"})
            if len(cells) >= 6:
                languages = [clean(x.get_text(" ", strip=True)) for x in cells[5].find_all("li")]
                if not languages:
                    text = clean(cells[5].get_text(" ", strip=True))
                    languages = [text] if text else []
        rows.append(
            {
                "ib_school_code": code,
                "name": clean(link.get_text(" ", strip=True)),
                "detail_url": urljoin(BASE, href),
                "programmes_from_list": programme_flags,
                "languages_from_list": languages,
            }
        )
    return total, rows


def stripped_strings(soup: BeautifulSoup) -> list[str]:
    return [clean(x) for x in soup.stripped_strings if clean(x)]


def value_after(strings: list[str], label: str) -> str | None:
    target = label.casefold().rstrip(":")
    for i, value in enumerate(strings[:-1]):
        if value.casefold().rstrip(":") == target:
            return strings[i + 1]
    return None


def section_between(strings: list[str], start: str, end: str) -> list[str]:
    try:
        a = next(i for i, value in enumerate(strings) if value.casefold() == start.casefold())
        b = next(i for i, value in enumerate(strings[a + 1 :], start=a + 1) if value.casefold() == end.casefold())
    except StopIteration:
        return []
    return strings[a + 1 : b]


def parse_detail(html_text: str, seed: dict) -> dict:
    soup = BeautifulSoup(html_text, "html.parser")
    strings = stripped_strings(soup)
    h1 = soup.find("h1")
    name = clean(h1.get_text(" ", strip=True)) if h1 else seed["name"]

    website = value_after(strings, "Website:")
    phone = value_after(strings, "Phone:")
    school_type = value_after(strings, "Type:")
    head = value_after(strings, "Head of school:")
    ib_since = value_after(strings, "IB School since:")
    school_code = value_after(strings, "IB School code:") or seed["ib_school_code"]
    region = value_after(strings, "Region:")

    coordinator_block = section_between(strings, "Our coordinator", "Contact coordinator")
    coordinator_name = coordinator_block[0] if coordinator_block else None
    coordinator_address = "\n".join(coordinator_block[1:]) if len(coordinator_block) > 1 else None

    subjects = section_between(
        strings,
        "Students are currently registered for the following subjects:",
        "World school",
    )

    normalized_type = clean(school_type).upper() if school_type else None
    if normalized_type == "PRIVATE":
        scope_state = "eligible"
        ownership_scope = "private_independent"
    elif normalized_type in {"STATE", "PUBLIC"}:
        scope_state = "excluded"
        ownership_scope = "public"
    else:
        scope_state = "needs_review"
        ownership_scope = "unknown"

    return {
        "source_id": "ib_world_schools_egypt",
        "source_record_id": str(school_code),
        "entity_family": "pre_university",
        "institution_type": "international_school",
        "name_en": name,
        "ib_school_code": str(school_code),
        "ib_school_since": ib_since,
        "ib_region": region,
        "ib_type": normalized_type,
        "head_of_school": head,
        "website": website,
        "phone": phone,
        "coordinator_name": coordinator_name,
        "address_raw": coordinator_address,
        "programmes": seed.get("programmes_from_list") or {},
        "languages": seed.get("languages_from_list") or [],
        "registered_subjects": subjects,
        "scope_state": scope_state,
        "scope_class": "international_school",
        "ownership_scope": ownership_scope,
        "eligibility_evidence": "active_ib_world_school",
        "source_url": seed["detail_url"],
    }


def acquire(output_dir: Path, expected_count: int = 54, delay: float = 0.15, timeout: float = 30.0) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    s = session()
    retrieved_at = datetime.now(timezone.utc).isoformat()

    seeds: list[dict] = []
    source_total: int | None = None
    seen_codes: set[str] = set()
    page_hashes: dict[str, str] = {}

    for page in range(1, 8):
        response = s.get(
            SEARCH_URL,
            params={"SearchFields.Country": COUNTRY, "page": page},
            timeout=timeout,
        )
        response.raise_for_status()
        page_hashes[str(page)] = sha256_text(response.text)
        total, rows = result_links(response.text)
        if total is not None:
            source_total = total
        new_rows = [row for row in rows if row["ib_school_code"] not in seen_codes]
        if not new_rows:
            break
        for row in new_rows:
            seen_codes.add(row["ib_school_code"])
            seeds.append(row)
        if source_total is not None and len(seeds) >= source_total:
            break

    if source_total is None:
        raise RuntimeError("Could not read the IB Egypt source count")
    if len(seeds) != source_total:
        raise RuntimeError(f"IB pagination incomplete: discovered {len(seeds)} of {source_total}")
    if expected_count and source_total != expected_count:
        raise RuntimeError(
            f"IB Egypt source count changed: expected {expected_count}, observed {source_total}. "
            "Review the source before accepting the new universe."
        )

    records: list[dict] = []
    detail_hashes: dict[str, str] = {}
    for index, seed in enumerate(seeds):
        response = s.get(seed["detail_url"], timeout=timeout)
        response.raise_for_status()
        detail_hashes[seed["ib_school_code"]] = sha256_text(response.text)
        record = parse_detail(response.text, seed)
        record["retrieved_at"] = retrieved_at
        record["source_sha256"] = detail_hashes[seed["ib_school_code"]]
        records.append(record)
        if delay and index < len(seeds) - 1:
            time.sleep(delay)

    jsonl_path = output_dir / "ib-egypt-2026.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in records:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "source_id": "ib_world_schools_egypt",
        "retrieved_at": retrieved_at,
        "source_reported_count": source_total,
        "records_acquired": len(records),
        "eligible_private": sum(1 for row in records if row["scope_state"] == "eligible"),
        "excluded_public": sum(1 for row in records if row["scope_state"] == "excluded"),
        "needs_review": sum(1 for row in records if row["scope_state"] == "needs_review"),
        "search_page_sha256": page_hashes,
        "detail_pages_hashed": len(detail_hashes),
        "public_promotion_performed": False,
        "database_mutation_performed": False,
        "output": jsonl_path.name,
    }
    (output_dir / "ib-egypt-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/international"))
    parser.add_argument("--expected-count", type=int, default=54)
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    acquire(args.output_dir, args.expected_count, args.delay, args.timeout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
