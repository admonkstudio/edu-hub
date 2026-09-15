#!/usr/bin/env python3
"""Extract every Egypt row from Cognia's public accreditation registry.

The public registry currently reports 256 Egypt results and paginates them 25 at
a time. This D2.1 extractor drives the official UI, preserves every registry row
(including duplicate names, campuses, divisions and corporation-system rows),
and emits source evidence plus duplicate-name diagnostics.

No record is promoted to Edu Hub eligibility here. Identity resolution belongs
to D2.2; accreditation evidence and international-school eligibility remain
separate decisions.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

REGISTRY_URL = "https://home.cognia.org/registry"
COUNTRY_SELECT_ID = "p.RegistryModule.RegistryRequest_NewEdit.referenceSelector1_ird_6"
ROW_SELECTOR = ".mx-name-listView2 li[class*='mx-name-index-']"
GRID_SELECTOR = ".mx-name-grid1_SSP"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
)
DISPLAY_RE = re.compile(r"Displaying\s+(\d+)\s+to\s+(\d+)\s+of\s+(\d+)\s+results?\.", re.I)


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(ch for ch in value if ch.isalnum() or ch.isspace())
    return " ".join(value.split())


def parse_row(text: str, page_number: int, row_number: int) -> dict:
    lines = [line.replace("\xa0", " ").strip() for line in text.splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    if len(lines) < 6:
        raise RuntimeError(
            f"Unexpected Cognia row shape on page {page_number}, row {row_number}: {lines!r}"
        )
    name, city, state_province, postal_code, country, institution_type = lines[:6]
    system = " ".join(part for part in lines[6:] if part).strip() or None
    if country != "Egypt":
        raise RuntimeError(
            f"Country drift on page {page_number}, row {row_number}: {country!r}"
        )
    return {
        "source_row_number": None,
        "page_number": page_number,
        "page_row_number": row_number,
        "institution_name": name,
        "institution_name_normalized": normalize_name(name),
        "city": city or None,
        "state_province": state_province or None,
        "postal_code": postal_code or None,
        "country": country,
        "institution_type": institution_type or None,
        "system": system,
        "raw_text": text,
    }


def extract(output: Path, timeout_ms: int) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    page_summaries: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-quic"])
        context = browser.new_context(user_agent=USER_AGENT, locale="en-US")
        page = context.new_page()
        response = page.goto(REGISTRY_URL, wait_until="domcontentloaded", timeout=timeout_ms)
        initial_status = response.status if response else None
        page.wait_for_timeout(3000)

        country = page.locator(f'select[id="{COUNTRY_SELECT_ID}"]')
        if country.count() != 1:
            candidates = page.locator("select").filter(
                has=page.locator("option", has_text="Egypt")
            )
            if candidates.count() != 1:
                raise RuntimeError(
                    f"Cognia country selector unresolved: exact={country.count()} candidates={candidates.count()}"
                )
            country = candidates
        country.select_option(label="Egypt")
        page.get_by_role("button", name="Search", exact=True).click(timeout=timeout_ms)
        page.wait_for_timeout(5000)

        grid = page.locator(GRID_SELECTOR)
        grid.wait_for(state="visible", timeout=timeout_ms)
        summary_text = grid.inner_text(timeout=timeout_ms)
        first_match = DISPLAY_RE.search(summary_text)
        if not first_match:
            raise RuntimeError("Could not parse Cognia result-count summary")
        expected_total = int(first_match.group(3))
        expected_pages = (expected_total + 24) // 25

        for page_number in range(1, expected_pages + 1):
            summary_text = grid.inner_text(timeout=timeout_ms)
            match = DISPLAY_RE.search(summary_text)
            if not match:
                raise RuntimeError(f"Missing Cognia pagination summary on page {page_number}")
            start, end, total = map(int, match.groups())
            if total != expected_total:
                raise RuntimeError(
                    f"Cognia total changed during extraction: {expected_total} -> {total}"
                )

            rows = page.locator(ROW_SELECTOR)
            row_count = rows.count()
            expected_page_rows = end - start + 1
            if row_count != expected_page_rows:
                raise RuntimeError(
                    f"Cognia row count mismatch page {page_number}: DOM={row_count} summary={expected_page_rows}"
                )

            first_row_before = rows.nth(0).inner_text() if row_count else ""
            page_summaries.append(
                {
                    "page_number": page_number,
                    "start": start,
                    "end": end,
                    "total": total,
                    "row_count": row_count,
                }
            )
            for index in range(row_count):
                record = parse_row(rows.nth(index).inner_text(), page_number, index + 1)
                record["source_row_number"] = len(records) + 1
                records.append(record)

            if page_number < expected_pages:
                next_button = page.locator('button[aria-label="Next page"]')
                if next_button.count() != 1:
                    raise RuntimeError(
                        f"Expected one Cognia Next page button, found {next_button.count()}"
                    )
                next_button.click(timeout=timeout_ms)
                page.wait_for_function(
                    """({selector, previous}) => {
                      const row = document.querySelector(selector);
                      return row && row.innerText !== previous;
                    }""",
                    {"selector": ROW_SELECTOR, "previous": first_row_before},
                    timeout=timeout_ms,
                )
                page.wait_for_timeout(500)

        browser.close()

    if len(records) != expected_total:
        raise RuntimeError(
            f"Cognia extraction incomplete: extracted={len(records)} expected={expected_total}"
        )

    counts = Counter(record["institution_name_normalized"] for record in records)
    duplicate_groups = [
        {
            "institution_name_normalized": normalized,
            "count": count,
            "source_row_numbers": [
                record["source_row_number"]
                for record in records
                if record["institution_name_normalized"] == normalized
            ],
            "names": sorted(
                {
                    record["institution_name"]
                    for record in records
                    if record["institution_name_normalized"] == normalized
                }
            ),
        }
        for normalized, count in sorted(counts.items())
        if count > 1
    ]

    result = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_cognia_egypt_registry_full_extraction",
        "registry_url": REGISTRY_URL,
        "publisher": "Cognia",
        "country_filter": "Egypt",
        "initial_response_status": initial_status,
        "source_result_count": expected_total,
        "extracted_record_count": len(records),
        "page_count": len(page_summaries),
        "page_summaries": page_summaries,
        "duplicate_normalized_name_group_count": len(duplicate_groups),
        "duplicate_normalized_name_groups": duplicate_groups,
        "records": records,
        "official_registry_extraction_complete": True,
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
    }
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "source_result_count": expected_total,
                "extracted_record_count": len(records),
                "page_count": len(page_summaries),
                "duplicate_normalized_name_group_count": len(duplicate_groups),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/international/cognia-egypt-registry/cognia-egypt-registry.json"),
    )
    parser.add_argument("--timeout-ms", type=int, default=45000)
    args = parser.parse_args()
    extract(args.output, args.timeout_ms)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
