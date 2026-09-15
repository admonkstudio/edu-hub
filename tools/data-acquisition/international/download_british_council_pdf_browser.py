#!/usr/bin/env python3
"""Download the British Council Egypt Partner Schools PDF through a real browser.

The September 2026 PDF is browser-accessible but direct GitHub-hosted HTTP
requests have returned 403, and Chromium on GitHub-hosted runners can hit an
HTTP/2 protocol error on the British Council landing page. This adapter keeps
browser acquisition as the source-of-truth path while making it resilient:

1. launch Chromium with HTTP/2 and QUIC disabled;
2. retry the official landing page and discover the current Partner Schools PDF;
3. if landing-page navigation remains unavailable, fall back only to the pinned
   September 2026 official PDF URL already registered in the project; and
4. retrieve the PDF as a browser response first, with same-context fetch as a
   secondary browser method.

The script writes only the PDF bytes and an acquisition manifest. It does not
create institution identities, grant eligibility, mutate the database or
project rows to the public site.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

LANDING_URL = (
    "https://www.britishcouncil.org.eg/en/exam/igcse-school/choosing/"
    "find-british-council-attached-centre"
)
PINNED_PDF_URL = (
    "https://www.britishcouncil.org.eg/sites/default/files/"
    "british_council_partner_schools_list_-_sep_2026_0.pdf"
)
EXPECTED_PDF_FRAGMENT = "british_council_partner_schools_list_-_sep_2026"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
)


def _discover_pdf(page, timeout_ms: int) -> tuple[str, str, list[str]]:
    """Return PDF URL, discovery mode and landing-page navigation errors."""
    errors: list[str] = []
    for attempt in range(1, 4):
        try:
            response = page.goto(
                LANDING_URL,
                wait_until="domcontentloaded",
                timeout=timeout_ms,
            )
            if response is not None and response.ok:
                hrefs = page.locator("a[href]").evaluate_all(
                    "els => els.map(a => a.href).filter(Boolean)"
                )
                pdf_candidates = [
                    urljoin(LANDING_URL, href)
                    for href in hrefs
                    if EXPECTED_PDF_FRAGMENT in href.casefold()
                    and ".pdf" in href.casefold()
                ]
                if not pdf_candidates:
                    pdf_candidates = [
                        urljoin(LANDING_URL, href)
                        for href in hrefs
                        if ".pdf" in href.casefold()
                        and "partner" in href.casefold()
                    ]
                if pdf_candidates:
                    return pdf_candidates[0], "landing_page_discovery", errors
                errors.append(
                    f"attempt {attempt}: landing page loaded but no Partner Schools PDF link was found"
                )
            else:
                status = response.status if response else "no response"
                errors.append(f"attempt {attempt}: landing page HTTP {status}")
        except PlaywrightError as exc:
            errors.append(f"attempt {attempt}: {exc}")
        if attempt < 3:
            time.sleep(attempt)

    # This fallback is intentionally narrow and version-pinned. It is not a
    # generic guess and cannot silently move to another source/version.
    return PINNED_PDF_URL, "pinned_official_url_after_landing_failure", errors


def _browser_response_pdf(page, pdf_url: str, timeout_ms: int) -> tuple[bytes, int, str, str]:
    """Prefer browser navigation response bytes; fall back to in-page fetch."""
    try:
        response = page.goto(pdf_url, wait_until="commit", timeout=timeout_ms)
        if response is not None:
            status = response.status
            content_type = response.headers.get("content-type", "")
            body = response.body()
            if response.ok and body.startswith(b"%PDF"):
                return body, status, content_type, "browser_navigation_response"
    except PlaywrightError:
        pass

    result = page.evaluate(
        """async (url) => {
          const response = await fetch(url, {
            credentials: 'include',
            cache: 'no-store',
            redirect: 'follow'
          });
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
    pdf_bytes = base64.b64decode(result["bodyBase64"])
    if not result["ok"]:
        raise RuntimeError(f"Browser PDF fetch failed with HTTP {result['status']}")
    if not pdf_bytes.startswith(b"%PDF"):
        raise RuntimeError(
            f"Browser fetch did not return a PDF: status={result['status']} "
            f"content_type={result['contentType']!r} bytes={len(pdf_bytes)}"
        )
    return pdf_bytes, result["status"], result["contentType"], "same_context_fetch"


def download(output: Path, manifest: Path, timeout_ms: int) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-http2", "--disable-quic"],
        )
        context = browser.new_context(
            user_agent=USER_AGENT,
            locale="en-GB",
            extra_http_headers={
                "Accept-Language": "en-GB,en;q=0.9",
                "Upgrade-Insecure-Requests": "1",
            },
        )
        page = context.new_page()
        pdf_url, discovery_mode, landing_errors = _discover_pdf(page, timeout_ms)
        pdf_bytes, status, content_type, retrieval_mode = _browser_response_pdf(
            page, pdf_url, timeout_ms
        )
        browser.close()

    if not pdf_bytes.startswith(b"%PDF"):
        raise RuntimeError("British Council browser acquisition did not return PDF bytes")

    output.write_bytes(pdf_bytes)
    acquisition = {
        "schema_version": 2,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "landing_url": LANDING_URL,
        "pdf_url": pdf_url,
        "capture_mode": "headless_chromium_browser_acquisition",
        "discovery_mode": discovery_mode,
        "retrieval_mode": retrieval_mode,
        "landing_navigation_errors": landing_errors,
        "http_status": status,
        "content_type": content_type,
        "pdf_bytes": len(pdf_bytes),
        "pdf_sha256": hashlib.sha256(pdf_bytes).hexdigest(),
        "output": str(output),
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "database_mutation_performed": False,
        "public_projection_rows_created": 0,
    }
    manifest.write_text(
        json.dumps(acquisition, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
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
        default=Path(
            "artifacts/international/british-council-full-pdf/browser-download-manifest.json"
        ),
    )
    parser.add_argument("--timeout-ms", type=int, default=60000)
    args = parser.parse_args()
    download(args.output, args.manifest, args.timeout_ms)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
