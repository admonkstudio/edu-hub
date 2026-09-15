#!/usr/bin/env python3
"""Probe Cognia's public JS accreditation registry without mutating project data.

The public Cognia registry is a JavaScript application, so static HTML does not
expose its search contract. This D2.1 probe records only public UI structure and
network endpoint metadata needed to build a deterministic Egypt registry
extractor. It does not submit institution decisions, create canonical entities,
or promote any candidate to the public dataset.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

REGISTRY_URL = "https://home.cognia.org/registry"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
)


def compact(value: object, limit: int = 500) -> str | None:
    text = " ".join(str(value or "").split())
    if not text:
        return None
    return text[:limit]


def probe(output: Path, timeout_ms: int) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    network: list[dict] = []
    navigation_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-quic"])
        context = browser.new_context(user_agent=USER_AGENT, locale="en-US")
        page = context.new_page()

        def on_response(response) -> None:
            try:
                request = response.request
                resource_type = request.resource_type
                url = response.url
                if "cognia" not in url.casefold() and resource_type not in {"xhr", "fetch"}:
                    return
                network.append(
                    {
                        "url": url[:2000],
                        "status": response.status,
                        "resource_type": resource_type,
                        "content_type": response.headers.get("content-type", "")[:250],
                    }
                )
            except Exception:
                return

        page.on("response", on_response)
        response_status = None
        try:
            response = page.goto(REGISTRY_URL, wait_until="domcontentloaded", timeout=timeout_ms)
            response_status = response.status if response else None
            page.wait_for_timeout(8000)
        except PlaywrightError as exc:
            navigation_errors.append(str(exc))

        title = compact(page.title(), 300)
        final_url = page.url
        body_text = compact(page.locator("body").inner_text(timeout=5000), 20000)

        controls = page.locator("input, select, textarea, button").evaluate_all(
            """els => els.slice(0, 250).map(el => ({
              tag: el.tagName.toLowerCase(),
              type: el.getAttribute('type'),
              name: el.getAttribute('name'),
              id: el.id || null,
              placeholder: el.getAttribute('placeholder'),
              ariaLabel: el.getAttribute('aria-label'),
              text: (el.innerText || el.value || '').trim().slice(0, 500)
            }))"""
        )
        links = page.locator("a[href]").evaluate_all(
            """els => els.slice(0, 250).map(a => ({
              text: (a.innerText || '').trim().slice(0, 500),
              href: a.href
            }))"""
        )
        scripts = page.locator("script[src]").evaluate_all(
            "els => els.slice(0, 250).map(s => s.src)"
        )
        browser.close()

    dedup_network: list[dict] = []
    seen: set[tuple[str, int, str]] = set()
    for item in network:
        key = (item["url"], item["status"], item["resource_type"])
        if key in seen:
            continue
        seen.add(key)
        dedup_network.append(item)

    result = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_cognia_registry_public_browser_probe",
        "requested_url": REGISTRY_URL,
        "final_url": final_url,
        "initial_response_status": response_status,
        "title": title,
        "navigation_errors": navigation_errors,
        "body_text_sample": body_text,
        "controls": controls,
        "links": links,
        "script_sources": scripts,
        "network_responses": dedup_network,
        "network_response_count": len(dedup_network),
        "official_registry_verification_performed": False,
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
    }
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/international/cognia-registry-probe/cognia-registry-probe.json"),
    )
    parser.add_argument("--timeout-ms", type=int, default=45000)
    args = parser.parse_args()
    probe(args.output, args.timeout_ms)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
