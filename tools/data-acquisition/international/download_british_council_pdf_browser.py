#!/usr/bin/env python3
"""Download the British Council Egypt Partner Schools PDF through a real browser.

The September 2026 PDF is browser-accessible but direct GitHub-hosted HTTP
requests have returned 403. This adapter opens the official landing page in
Chromium, discovers the current PDF link and performs a same-origin browser
fetch. It writes only the PDF bytes and a small acquisition manifest.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

LANDING_URL = (
    "https://www.britishcouncil.org.eg/en/exam/igcse-school/choosing/"
    "find-british-council-attached-centre"
)
EXPECTED_PDF_FRAGMENT = "british_council_partner_schools_list_-_sep_2026"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 EduHubResearch/2.0"
)


def download(output: Path, manifest: Path, timeout_ms: int) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT, locale="en-GB")
        page = context.new_page()
        response = page.goto(LANDING_URL, wait_until="domcontentloaded", timeout=timeout_ms)
        if response is None or not response.ok:
            raise RuntimeError(
                f"British Council landing page failed: {response.status if response else 'no response'}"
            )

        hrefs = page.locator("a[href]").evaluate_all(
            "els => els.map(a => a.href).filter(Boolean)"
        )
        pdf_candidates = [
            urljoin(LANDING_URL, href)
            for href in hrefs
            if EXPECTED_PDF_FRAGMENT in href.casefold() and ".pdf" in href.casefold()
        ]
        if not pdf_candidates:
            pdf_candidates = [
                urljoin(LANDING_URL, href)
                for href in hrefs
                if ".pdf" in href.casefold() and "partner" in href.casefold()
            ]
        if not pdf_candidates:
            raise RuntimeError("No Partner Schools PDF link found on British Council landing page")

        pdf_url = pdf_candidates[0]
        result = page.evaluate(
            """async (url) => {
              const response = await fetch(url, {credentials: 'include', cache: 'no-store'});
              const contentType = response.headers.get('content-type') || '';
              const buffer = await response.arrayBuffer();
              const bytes = new Uint8Array(buffer);
              let binary = '';
              const chunk = 0x8000;
              for (let i = 0; i < bytes.length; i += chunk) {
                binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
              }
              return {
                ok: response.ok,
                status: response.status,
                contentType,
                bodyBase64: btoa(binary)
              };
            }""",
            pdf_url,
        )
        browser.close()

    if not result["ok"]:
        raise RuntimeError(f"Browser PDF fetch failed with HTTP {result['status']}")
    pdf_bytes = base64.b64decode(result["bodyBase64"])
    if not pdf_bytes.startswith(b"%PDF"):
        raise RuntimeError(
            f"Browser fetch did not return a PDF: status={result['status']} "
            f"content_type={result['contentType']!r} bytes={len(pdf_bytes)}"
        )

    output.write_bytes(pdf_bytes)
    acquisition = {
        "schema_version": 1,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "landing_url": LANDING_URL,
        "pdf_url": pdf_url,
        "capture_mode": "headless_chromium_same_origin_fetch",
        "http_status": result["status"],
        "content_type": result["contentType"],
        "pdf_bytes": len(pdf_bytes),
        "pdf_sha256": hashlib.sha256(pdf_bytes).hexdigest(),
        "output": str(output),
    }
    manifest.write_text(json.dumps(acquisition, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(acquisition, ensure_ascii=False, indent=2))
    return acquisition


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/international/british-council-full-pdf/source.pdf"),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("artifacts/international/british-council-full-pdf/browser-download-manifest.json"),
    )
    parser.add_argument("--timeout-ms", type=int, default=60000)
    args = parser.parse_args()
    download(args.output, args.manifest, args.timeout_ms)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
