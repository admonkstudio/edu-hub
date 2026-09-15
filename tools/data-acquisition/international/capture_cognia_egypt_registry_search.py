#!/usr/bin/env python3
"""Capture Cognia's official Egypt accreditation-registry search result surface.

This D2.1 adapter operates only through Cognia's public registry UI. It selects
Egypt, executes Search, and records the rendered result structures plus bounded
network metadata so a deterministic extractor can be built from observed
behaviour rather than guessed backend calls.

The output remains source evidence only. Cognia accreditation does not itself
establish Edu Hub international-school eligibility, and this adapter never
creates/merges canonical identities or mutates public/database state.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

REGISTRY_URL = "https://home.cognia.org/registry"
COUNTRY_SELECT_ID = "p.RegistryModule.RegistryRequest_NewEdit.referenceSelector1_ird_6"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
)


def compact(text: object, limit: int = 20000) -> str:
    value = " ".join(str(text or "").split())
    return value[:limit]


def capture(output: Path, timeout_ms: int) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    xas_responses: list[dict] = []
    errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-quic"])
        context = browser.new_context(user_agent=USER_AGENT, locale="en-US")
        page = context.new_page()

        def on_response(response) -> None:
            try:
                if "/xas/" not in response.url:
                    return
                item = {
                    "url": response.url,
                    "status": response.status,
                    "resource_type": response.request.resource_type,
                    "content_type": response.headers.get("content-type", "")[:250],
                    "content_length": response.headers.get("content-length"),
                }
                xas_responses.append(item)
            except Exception:
                return

        page.on("response", on_response)
        response = page.goto(REGISTRY_URL, wait_until="domcontentloaded", timeout=timeout_ms)
        initial_status = response.status if response else None
        page.wait_for_timeout(3000)

        country = page.locator(f"#{COUNTRY_SELECT_ID}")
        if country.count() != 1:
            raise RuntimeError("Cognia country selector was not found exactly once")
        selected_value = country.select_option(label="Egypt")

        search_button = page.get_by_role("button", name="Search", exact=True)
        if search_button.count() != 1:
            raise RuntimeError("Cognia Search button was not found exactly once")

        try:
            search_button.click(timeout=timeout_ms)
            page.wait_for_timeout(8000)
        except PlaywrightError as exc:
            errors.append(str(exc))

        body_text = compact(page.locator("body").inner_text(timeout=5000), 50000)

        table_rows = page.locator("table tr").evaluate_all(
            """rows => rows.slice(0, 1000).map((row, index) => ({
              index,
              text: (row.innerText || '').trim().slice(0, 4000),
              cells: Array.from(row.querySelectorAll('th,td')).map(cell => (cell.innerText || '').trim().slice(0, 2000)),
              className: row.className || null
            })).filter(row => row.text)"""
        )
        role_rows = page.locator("[role='row']").evaluate_all(
            """rows => rows.slice(0, 1000).map((row, index) => ({
              index,
              text: (row.innerText || '').trim().slice(0, 4000),
              className: row.className || null
            })).filter(row => row.text)"""
        )
        list_items = page.locator("li").evaluate_all(
            """els => els.slice(0, 1000).map((el, index) => ({
              index,
              text: (el.innerText || '').trim().slice(0, 4000),
              className: el.className || null
            })).filter(item => item.text)"""
        )
        buttons = page.locator("button").evaluate_all(
            """els => els.slice(0, 250).map((el, index) => ({
              index,
              text: (el.innerText || '').trim().slice(0, 1000),
              title: el.getAttribute('title'),
              ariaLabel: el.getAttribute('aria-label'),
              disabled: !!el.disabled,
              className: el.className || null
            }))"""
        )
        anchors = page.locator("a[href]").evaluate_all(
            """els => els.slice(0, 1000).map((el, index) => ({
              index,
              text: (el.innerText || '').trim().slice(0, 2000),
              href: el.href,
              className: el.className || null
            })).filter(item => item.text || item.href)"""
        )
        candidate_containers = page.locator(
            ".mx-grid, .mx-datagrid, .mx-listview, .table, [class*='grid'], [class*='list']"
        ).evaluate_all(
            """els => els.slice(0, 250).map((el, index) => ({
              index,
              tag: el.tagName.toLowerCase(),
              className: el.className || null,
              text: (el.innerText || '').trim().slice(0, 10000)
            })).filter(item => item.text)"""
        )
        browser.close()

    dedup_xas: list[dict] = []
    seen = set()
    for item in xas_responses:
        key = (item["url"], item["status"], item["resource_type"], item.get("content_length"))
        if key in seen:
            continue
        seen.add(key)
        dedup_xas.append(item)

    result = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_cognia_egypt_registry_search_capture",
        "registry_url": REGISTRY_URL,
        "initial_response_status": initial_status,
        "country": "Egypt",
        "country_selected_values": selected_value,
        "errors": errors,
        "body_text_after_search": body_text,
        "table_rows": table_rows,
        "role_rows": role_rows,
        "list_items": list_items,
        "buttons": buttons,
        "anchors": anchors,
        "candidate_result_containers": candidate_containers,
        "xas_responses": dedup_xas,
        "xas_response_count": len(dedup_xas),
        "official_registry_query_performed": True,
        "official_registry_rows_promoted": 0,
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
    }
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "country": result["country"],
        "table_rows": len(table_rows),
        "role_rows": len(role_rows),
        "list_items": len(list_items),
        "candidate_result_containers": len(candidate_containers),
        "xas_response_count": len(dedup_xas),
        "errors": errors,
    }, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/international/cognia-egypt-search/cognia-egypt-search.json"),
    )
    parser.add_argument("--timeout-ms", type=int, default=45000)
    args = parser.parse_args()
    capture(args.output, args.timeout_ms)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
