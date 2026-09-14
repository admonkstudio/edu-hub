#!/usr/bin/env python3
"""Acquire the current MOHESR private higher-institute sector registry.

The MOHESR page is a source of sector occurrences, not a ready-made canonical
institution list. One institute may appear in more than one sector. This scraper
therefore preserves source occurrences exactly and reports distinct normalized
names separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://dportal.mohesr.gov.eg/index.php?id=193&option=com_sppagebuilder&view=page"
UA = "EduHubResearchBot/1.2 (+https://github.com/admonkstudio/edu-hub; public-source-acquisition)"
SECTIONS = [
    ("engineering", 55, ("اولا: المعاهد الخاصة العالية الهندسية", "اولا : المعاهد الخاصة العالية الهندسية")),
    ("commercial", 71, ("ثانيا :المعاهد الخاصة العالية (الشعبة التجارية)", "ثانيا: المعاهد الخاصة العالية (الشعبة التجارية)", "ثانيا : المعاهد الخاصة العالية (الشعبة التجارية)")),
    ("computer_science", 16, ('ثالثا:المعاهد الخاصة العالية "شعبة علوم الحاسب ونظم المعلومات"', 'ثالثا: المعاهد الخاصة العالية "شعبة علوم الحاسب ونظم المعلومات"')),
    ("languages_media", 19, ("رابعا: المعاهد الخاصة العالية للغات والإعلام", "رابعا : المعاهد الخاصة العالية للغات والإعلام")),
    ("tourism_hotels", 19, ("خامسا: المعاهد الخاصة العالية للسياحة والفنادق", "خامسا : المعاهد الخاصة العالية للسياحة والفنادق", "المعاهد الخاصة العالية للسياحة والفنادق")),
    ("social_work", 16, ("سادسا: المعاهد الخاصة العالية للخدمة الاجتماعية", "سادسا : المعاهد الخاصة العالية للخدمة الاجتماعية", "المعاهد الخاصة العالية للخدمة الاجتماعية")),
    ("health_nursing", 10, ("سابعا: المعاهد الخاصة العالية التكنولوجية للعلوم الصحية التطبيقية", "سابعا : المعاهد الخاصة العالية التكنولوجية للعلوم الصحية التطبيقية", "المعاهد الخاصة العالية التكنولوجية للعلوم الصحية التطبيقية")),
    ("agriculture", 2, ("ثامنا: المعاهد الخاصة العالية الزراعية", "ثامنا : المعاهد الخاصة العالية الزراعية", "المعاهد الخاصة العالية الزراعية")),
]
TASHKEEL_RE = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
PUNCT_RE = re.compile(r"[^\w\u0600-\u06ff]+", re.UNICODE)


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=4, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("GET",))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers["User-Agent"] = UA
    return s


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_arabic(value: str) -> str:
    value = clean(value).replace("ـ", "")
    value = TASHKEEL_RE.sub("", value)
    value = value.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي"}))
    value = PUNCT_RE.sub(" ", value)
    return clean(value).casefold()


def parse_page(html: str, source_url: str) -> tuple[list[dict], dict]:
    soup = BeautifulSoup(html, "html.parser")
    lines = [clean(x) for x in soup.stripped_strings]
    lines = [x for x in lines if x]

    found_headings: list[tuple[int, str, int, str]] = []
    for i, line in enumerate(lines):
        for key, expected, variants in SECTIONS:
            if any(line.strip() == v for v in variants) or any(v in line and len(line) < 180 for v in variants):
                found_headings.append((i, key, expected, line))

    first: dict[str, tuple[int, str, int, str]] = {}
    for item in found_headings:
        first.setdefault(item[1], item)
    ordered = sorted(first.values())

    numeral = re.compile(r"^\s*([0-9٠-٩]+)\s*[\.\-–:)،]?\s*(.+)$")
    trans = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    raw_rows: list[dict] = []
    section_report: dict[str, dict] = {}

    for pos, (idx, key, expected, heading) in enumerate(ordered):
        stop = ordered[pos + 1][0] if pos + 1 < len(ordered) else min(len(lines), idx + 260)
        rows: list[dict] = []
        for line in lines[idx + 1:stop]:
            match = numeral.match(line.translate(trans))
            if not match:
                continue
            name = re.sub(r"\s+", " ", match.group(2)).strip(" .،-–")
            if len(name) < 4 or any(x in name for x in ("جميع الحقوق", "العاصمة الادارية", "العاصمة الإدارية", "تواصل معنا")):
                continue
            ordinal = int(match.group(1))
            if ordinal < 1 or ordinal > expected + 5:
                continue
            rows.append({"category_raw": key, "ordinal_raw": ordinal, "name_raw": name, "heading_raw": heading})

        by_ordinal: dict[int, dict] = {}
        for row in rows:
            by_ordinal.setdefault(row["ordinal_raw"], row)
        clean_rows = [by_ordinal[k] for k in sorted(by_ordinal)]
        section_report[key] = {"expected": expected, "acquired": len(clean_rows), "heading": heading}
        raw_rows.extend(clean_rows)

    acquired_keys = {row["category_raw"] for row in raw_rows}
    for key, expected, _ in SECTIONS:
        section_report.setdefault(key, {"expected": expected, "acquired": 0, "heading": None})

    output_rows: list[dict] = []
    for row in raw_rows:
        source_key = f"{row['category_raw']}|{row['ordinal_raw']}|{row['name_raw']}"
        output_rows.append({
            "source_record_id": "mohesr-private-" + hashlib.sha256(source_key.encode("utf-8")).hexdigest()[:18],
            "source_url": source_url,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "name_raw": row["name_raw"],
            "normalized_name_ar": normalize_arabic(row["name_raw"]),
            "entity_type_raw": "private_higher_institute",
            "location_raw": None,
            "payload": row,
        })

    distinct_names = {row["normalized_name_ar"] for row in output_rows if row["normalized_name_ar"]}
    expected_total = sum(item[1] for item in SECTIONS)
    report = {
        "schema_version": 1,
        "source_url": source_url,
        "headline_target_occurrences": expected_total,
        "acquired_sector_occurrences": len(output_rows),
        "distinct_normalized_names": len(distinct_names),
        "detected_sections": sorted(acquired_keys),
        "missing_sections": [key for key, _, _ in SECTIONS if key not in acquired_keys],
        "sections": section_report,
        "complete_against_headline_target": len(output_rows) == expected_total,
        "canonical_entities_created": 0,
        "notes": [
            "Sector occurrence count is not a canonical institution count.",
            "The same institute may legitimately appear in multiple MOHESR sectors.",
            "Missing public-page sections remain acquisition gaps and must not be filled from secondary sources as official coverage.",
        ],
    }
    return output_rows, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/edu-data-1/mohesr_private_institutes.jsonl", type=Path)
    parser.add_argument("--report", default="artifacts/edu-data-1/mohesr_private_institutes_report.json", type=Path)
    parser.add_argument("--page-text", default="artifacts/edu-data-1/mohesr_private_page.txt", type=Path)
    args = parser.parse_args()

    s = session()
    response = s.get(URL, timeout=60, allow_redirects=True)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    lines = [clean(x) for x in soup.stripped_strings if clean(x)]

    rows, report = parse_page(response.text, response.url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.page_text.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.page_text.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if len(rows) < 170:
        raise SystemExit(f"MOHESR private-institute acquisition unexpectedly small: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
