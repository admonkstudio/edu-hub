#!/usr/bin/env python3
"""Acquire the British Council Egypt Partner Schools PDF resiliently.

GitHub-hosted runners have shown two source-specific behaviours: direct Python
HTTP requests can return 403, while Chromium can fail/hang on HTTP/2. The
adapter therefore uses bounded, source-safe acquisition paths:

1. curl over HTTP/1.1 with a realistic browser UA, cookie jar and Referer;
2. Chromium with HTTP/2 and QUIC disabled;
3. a version-pinned September 2026 official PDF URL if the landing page cannot
   be reached.

Only official British Council URLs are accepted. Every network path has a hard
timeout. The adapter writes source bytes and a manifest; it never grants
eligibility, creates canonical identities, merges entities, mutates the database
or projects public rows.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import tempfile
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


def _validate_pdf_url(url: str) -> str:
    if not url.startswith("https://www.britishcouncil.org.eg/"):
        raise RuntimeError(f"Refusing non-British-Council PDF URL: {url}")
    if ".pdf" not in url.casefold():
        raise RuntimeError(f"Refusing non-PDF URL: {url}")
    return url


def _extract_pdf_from_html(html: str) -> str | None:
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.I)
    absolute = [urljoin(LANDING_URL, href) for href in hrefs]
    preferred = [
        url
        for url in absolute
        if EXPECTED_PDF_FRAGMENT in url.casefold() and ".pdf" in url.casefold()
    ]
    if not preferred:
        preferred = [
            url
            for url in absolute
            if ".pdf" in url.casefold() and "partner" in url.casefold()
        ]
    return _validate_pdf_url(preferred[0]) if preferred else None


def _curl_acquire(timeout_s: int) -> tuple[bytes, str, str, list[str]] | None:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="edu-bc-") as tmp:
        tmpdir = Path(tmp)
        cookies = tmpdir / "cookies.txt"
        landing_cmd = [
            "curl",
            "--http1.1",
            "--location",
            "--fail-with-body",
            "--silent",
            "--show-error",
            "--max-time",
            str(timeout_s),
            "--retry",
            "1",
            "--user-agent",
            USER_AGENT,
            "--header",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "--header",
            "Accept-Language: en-GB,en;q=0.9",
            "--cookie-jar",
            str(cookies),
            LANDING_URL,
        ]
        landing = subprocess.run(landing_cmd, capture_output=True, check=False)
        pdf_url = None
        discovery_mode = "pinned_official_url_after_landing_failure"
        if landing.returncode == 0:
            pdf_url = _extract_pdf_from_html(
                landing.stdout.decode("utf-8", errors="replace")
            )
            if pdf_url:
                discovery_mode = "landing_page_discovery_http1"
            else:
                errors.append(
                    "curl landing page loaded but no Partner Schools PDF link was found"
                )
        else:
            errors.append(
                "curl landing failed: "
                + landing.stderr.decode("utf-8", errors="replace").strip()
            )

        pdf_url = _validate_pdf_url(pdf_url or PINNED_PDF_URL)
        pdf_path = tmpdir / "source.pdf"
        pdf_cmd = [
            "curl",
            "--http1.1",
            "--location",
            "--fail-with-body",
            "--silent",
            "--show-error",
            "--max-time",
            str(max(timeout_s, 20)),
            "--retry",
            "1",
            "--user-agent",
            USER_AGENT,
            "--header",
            "Accept: application/pdf,*/*;q=0.8",
            "--header",
            "Accept-Language: en-GB,en;q=0.9",
            "--referer",
            LANDING_URL,
            "--cookie",
            str(cookies),
            "--output",
            str(pdf_path),
            "--write-out",
            "%{http_code}",
            pdf_url,
        ]
        pdf = subprocess.run(pdf_cmd, capture_output=True, text=True, check=False)
        if pdf.returncode == 0 and pdf_path.exists():
            data = pdf_path.read_bytes()
            if data.startswith(b"%PDF"):
                return data, pdf_url, discovery_mode, errors
            errors.append(
                f"curl returned non-PDF bytes={len(data)} status={pdf.stdout.strip()}"
            )
        else:
            errors.append(f"curl PDF failed: {pdf.stderr.strip()}")
    return None


def _discover_pdf_browser(page, timeout_ms: int) -> tuple[str, str, list[str]]:
    errors: list[str] = []
    for attempt in range(1, 3):
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
                candidates = [
                    urljoin(LANDING_URL, href)
                    for href in hrefs
                    if EXPECTED_PDF_FRAGMENT in href.casefold()
                    and ".pdf" in href.casefold()
                ]
                if not candidates:
                    candidates = [
                        urljoin(LANDING_URL, href)
                        for href in hrefs
                        if ".pdf" in href.casefold() and "partner" in href.casefold()
                    ]
                if candidates:
                    return (
                        _validate_pdf_url(candidates[0]),
                        "landing_page_discovery_browser",
                        errors,
                    )
                errors.append(
                    f"attempt {attempt}: landing page loaded without PDF link"
                )
            else:
                errors.append(f"attempt {attempt}: landing page unavailable")
        except PlaywrightError as exc:
            errors.append(f"attempt {attempt}: {exc}")
        if attempt < 2:
            time.sleep(1)
    return PINNED_PDF_URL, "pinned_official_url_after_landing_failure", errors


def _browser_pdf(page, pdf_url: str, timeout_ms: int) -> tuple[bytes, int, str, str]:
    """Fetch source bytes only through a bounded in-page browser request.

    Do not call Playwright Response.body() on PDF navigation: on this source the
    navigation can commit while the body stream never completes on hosted
    runners, leaving the job unbounded. AbortController guarantees termination.
    """
    result = page.evaluate(
        """async ({url, timeoutMs}) => {
          const controller = new AbortController();
          const timer = setTimeout(() => controller.abort(), timeoutMs);
          try {
            const response = await fetch(url, {
              credentials: 'include',
              cache: 'no-store',
              redirect: 'follow',
              signal: controller.signal
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
          } finally {
            clearTimeout(timer);
          }
        }""",
        {"url": pdf_url, "timeoutMs": timeout_ms},
    )
    data = base64.b64decode(result["bodyBase64"])
    if not result["ok"] or not data.startswith(b"%PDF"):
        raise RuntimeError(
            "Browser fetch failed: "
            f"status={result['status']} "
            f"content_type={result['contentType']!r} bytes={len(data)}"
        )
    return data, result["status"], result["contentType"], "same_context_fetch"


def download(output: Path, manifest: Path, timeout_ms: int) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    timeout_s = max(5, int(timeout_ms / 1000))
    landing_errors: list[str] = []

    curl_result = _curl_acquire(timeout_s)
    if curl_result is not None:
        pdf_bytes, pdf_url, discovery_mode, curl_errors = curl_result
        landing_errors.extend(curl_errors)
        status = 200
        content_type = "application/pdf"
        retrieval_mode = "curl_http1_cookie_referer"
    else:
        landing_errors.append(
            "bounded curl HTTP/1.1 acquisition did not produce PDF bytes"
        )
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-http2", "--disable-quic"],
            )
            context = browser.new_context(
                user_agent=USER_AGENT,
                locale="en-GB",
                extra_http_headers={"Accept-Language": "en-GB,en;q=0.9"},
            )
            page = context.new_page()
            pdf_url, discovery_mode, browser_errors = _discover_pdf_browser(
                page, timeout_ms
            )
            landing_errors.extend(browser_errors)
            pdf_bytes, status, content_type, retrieval_mode = _browser_pdf(
                page, pdf_url, timeout_ms
            )
            browser.close()

    if not pdf_bytes.startswith(b"%PDF"):
        raise RuntimeError("British Council acquisition did not return PDF bytes")

    output.write_bytes(pdf_bytes)
    acquisition = {
        "schema_version": 4,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "landing_url": LANDING_URL,
        "pdf_url": pdf_url,
        "capture_mode": "official_pdf_resilient_acquisition",
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
    parser.add_argument("--timeout-ms", type=int, default=10000)
    args = parser.parse_args()
    download(args.output, args.manifest, args.timeout_ms)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
