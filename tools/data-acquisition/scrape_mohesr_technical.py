#!/usr/bin/env python3
"""Acquire MOHESR technological-college parents and technical institutes.

The official source describes 44 technical institutes under 8 technological
college parents. This adapter preserves that hierarchy explicitly and never
writes canonical/public data.
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

URL = "https://mohesr.gov.eg/index.php?id=190&option=com_sppagebuilder&view=page"
UA = "EduHubResearchBot/1.2 (+https://github.com/admonkstudio/edu-hub; public-source-acquisition)"
COLLEGE_RE = re.compile(r"^([1-8])\s*[-–]\s*(الكلية التكنولوجية.+)$")
INSTITUTE_PREFIXES = ("المعهد الفني", "المعهد الصناعي", "المعهد المتوسط")


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=4, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("GET",))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers["User-Agent"] = UA
    return s


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def source_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:18]
    return f"{prefix}-{digest}"


def parse_page(html: str, source_url: str) -> tuple[list[dict], list[dict], dict]:
    soup = BeautifulSoup(html, "html.parser")
    root = soup.find("main") or soup
    lines = [clean(x) for x in root.stripped_strings]

    current_college: str | None = None
    current_ordinal: int | None = None
    child_rows: list[dict] = []
    parent_order: dict[str, int] = {}

    for line in lines:
        match = COLLEGE_RE.match(line)
        if match:
            current_ordinal = int(match.group(1))
            current_college = clean(match.group(2))
            parent_order.setdefault(current_college, current_ordinal)
            continue
        if not current_college:
            continue
        value = line.strip(" •\t")
        if value.startswith(INSTITUTE_PREFIXES) and len(value) > 8:
            child_rows.append({
                "technical_college_raw": current_college,
                "technical_college_ordinal": current_ordinal,
                "name_raw": value,
            })

    seen_pairs: set[tuple[str, str]] = set()
    clean_children: list[dict] = []
    for row in child_rows:
        key = (row["technical_college_raw"], row["name_raw"])
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        clean_children.append(row)

    retrieved_at = datetime.now(timezone.utc).isoformat()
    parents = [
        {
            "source_record_id": source_id("mohesr-tech-college", str(parent_order[name]), name),
            "source_url": source_url,
            "retrieved_at": retrieved_at,
            "name_raw": name,
            "entity_type_raw": "technological_college",
            "payload": {"ordinal_raw": parent_order[name], "source_role": "parent technological college heading"},
        }
        for name in sorted(parent_order, key=lambda n: parent_order[n])
    ]

    children = [
        {
            "source_record_id": source_id("mohesr-tech-institute", row["technical_college_raw"], row["name_raw"]),
            "source_url": source_url,
            "retrieved_at": retrieved_at,
            "name_raw": row["name_raw"],
            "entity_type_raw": "technical_institute",
            "parent_source_record_id": source_id(
                "mohesr-tech-college",
                str(parent_order[row["technical_college_raw"]]),
                row["technical_college_raw"],
            ),
            "payload": row,
        }
        for row in clean_children
    ]

    by_parent: dict[str, int] = {}
    for row in clean_children:
        parent = row["technical_college_raw"]
        by_parent[parent] = by_parent.get(parent, 0) + 1

    report = {
        "schema_version": 1,
        "source_url": source_url,
        "expected_parent_colleges": 8,
        "acquired_parent_colleges": len(parents),
        "expected_child_institutes": 44,
        "acquired_child_institutes": len(children),
        "by_parent": by_parent,
        "hierarchy_preserved": all(row.get("parent_source_record_id") for row in children),
        "canonical_entities_created": 0,
        "public_promotion_performed": False,
    }
    return parents, children, report


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parents-output", default="artifacts/edu-data-1/mohesr_technological_colleges.jsonl", type=Path)
    parser.add_argument("--institutes-output", default="artifacts/edu-data-1/mohesr_technical_institutes.jsonl", type=Path)
    parser.add_argument("--report", default="artifacts/edu-data-1/mohesr_technical_report.json", type=Path)
    args = parser.parse_args()

    response = session().get(URL, timeout=60, allow_redirects=True)
    response.raise_for_status()
    parents, children, report = parse_page(response.text, response.url)
    write_jsonl(args.parents_output, parents)
    write_jsonl(args.institutes_output, children)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if len(parents) != 8 or len(children) != 44:
        raise SystemExit(f"Expected 8 technological colleges / 44 technical institutes; acquired {len(parents)} / {len(children)}")
    if not report["hierarchy_preserved"]:
        raise SystemExit("Technical institute parent links were not preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
