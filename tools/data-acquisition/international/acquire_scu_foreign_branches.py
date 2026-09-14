#!/usr/bin/env python3
"""Acquire SCU-recognized branches of international universities in Egypt."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://scu.eg/branches-of-international-universities/"
USER_AGENT = "EduHubResearch/2.0 (+https://github.com/admonkstudio/edu-hub)"


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def normalize_name(value: str) -> str:
    value = clean(value)
    value = re.sub(r"^فرع\s+", "", value)
    return value


def parse_branches(html_text: str) -> list[str]:
    soup = BeautifulSoup(html_text, "html.parser")
    candidates: list[str] = []
    for tag in soup.find_all(["h2", "h3", "h4", "h5", "h6", "p", "a"]):
        text = clean(tag.get_text(" ", strip=True))
        if not text:
            continue
        if "فرع جامعة" in text or "جامعة" in text and any(
            token in text for token in ("كوفنتري", "جزيرة الأمير", "هيرتفوردشاير", "نوفا", "لندن", "إيست لندن", "لانكشاير", "كازان", "سان بطرسبرج")
        ):
            candidates.append(text)
    out: list[str] = []
    seen: set[str] = set()
    for text in candidates:
        if text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def acquire(output_dir: Path, expected_count: int = 9, timeout: float = 30.0) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(URL, timeout=timeout, headers={"User-Agent": USER_AGENT, "Accept-Language": "ar,en;q=0.8"})
    response.raise_for_status()
    branches = parse_branches(response.text)
    if len(branches) != expected_count:
        raise RuntimeError(f"SCU foreign-branch count changed or parser drifted: expected {expected_count}, found {len(branches)}")

    retrieved_at = datetime.now(timezone.utc).isoformat()
    source_sha = hashlib.sha256(response.content).hexdigest()
    records = []
    for index, name in enumerate(branches, start=1):
        records.append(
            {
                "source_id": "scu_foreign_university_branches",
                "source_record_id": f"scu-foreign-branch-{index:02d}",
                "entity_family": "higher_education",
                "institution_type": "foreign_university_branch",
                "name_ar": name,
                "normalized_branch_name_ar": normalize_name(name),
                "scope_state": "eligible",
                "scope_class": "foreign_university_branch",
                "ownership_scope": "private_independent",
                "eligibility_evidence": "scu_recognized_foreign_branch",
                "source_url": URL,
                "retrieved_at": retrieved_at,
                "source_sha256": source_sha,
            }
        )

    jsonl = output_dir / "scu-foreign-university-branches.jsonl"
    with jsonl.open("w", encoding="utf-8") as handle:
        for row in records:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "source_id": "scu_foreign_university_branches",
        "retrieved_at": retrieved_at,
        "records_acquired": len(records),
        "expected_count": expected_count,
        "source_sha256": source_sha,
        "database_mutation_performed": False,
        "public_promotion_performed": False,
        "output": jsonl.name,
    }
    (output_dir / "scu-foreign-university-branches-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, default=Path("artifacts/international"))
    ap.add_argument("--expected-count", type=int, default=9)
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()
    acquire(args.output_dir, args.expected_count, args.timeout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
