#!/usr/bin/env python3
"""Capture the live public MOE/EMIS Egyptian Schools Directory contract.

This tool is intentionally a *capture/probe*, not a bulk scraper. The current
search.emis.gov.eg host times out from the project's GitHub-hosted runners, so
this script is designed to be run from an Egypt/local network where the public
directory is reachable.

It saves the public HTML, headers, forms/selects, script references and likely
ASP.NET endpoints needed to implement a tested row-level enumerator afterwards.
It does not authenticate, bypass access controls, submit private forms or evade
rate limits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TARGETS = [
    "https://search.emis.gov.eg/",
    "https://search.emis.gov.eg/sch_data.aspx",
    "https://search.emis.gov.eg/search_schpriv.aspx",
]

USER_AGENT = (
    "EduHubResearchBot/1.0 "
    "(+https://github.com/admonkstudio/edu-hub; public-source-contract-capture)"
)


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept-Language": "ar-EG,ar;q=0.9,en;q=0.7",
        }
    )
    return s


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_name(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/") or "index"
    path = re.sub(r"[^A-Za-z0-9._-]+", "_", path)
    return path[:120]


def option_manifest(select) -> list[dict[str, str | bool]]:
    out = []
    for opt in select.find_all("option"):
        out.append(
            {
                "value": opt.get("value", ""),
                "text": clean(opt.get_text(" ", strip=True)),
                "selected": opt.has_attr("selected"),
            }
        )
    return out


def form_manifest(page_url: str, form) -> dict:
    fields = []
    for element in form.find_all(["input", "select", "button", "textarea"]):
        item: dict[str, object] = {
            "tag": element.name,
            "name": element.get("name"),
            "id": element.get("id"),
        }
        if element.name == "input":
            item.update(
                {
                    "type": element.get("type", "text"),
                    "value": element.get("value", ""),
                }
            )
        elif element.name == "select":
            opts = option_manifest(element)
            item.update(
                {
                    "options_count": len(opts),
                    "options": opts,
                    "autopostback": "__doPostBack" in str(element),
                }
            )
        elif element.name == "button":
            item["text"] = clean(element.get_text(" ", strip=True))
            item["value"] = element.get("value", "")
        else:
            item["value"] = clean(element.get_text(" ", strip=True))
        fields.append(item)

    return {
        "id": form.get("id"),
        "name": form.get("name"),
        "method": (form.get("method") or "get").lower(),
        "action": urljoin(page_url, form.get("action") or page_url),
        "fields": fields,
    }


def capture_page(s: requests.Session, url: str, out_dir: Path, timeout: float) -> dict:
    started = time.monotonic()
    result: dict[str, object] = {
        "requested_url": url,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        response = s.get(url, timeout=timeout, allow_redirects=True)
        elapsed = time.monotonic() - started
        result.update(
            {
                "ok": response.ok,
                "status_code": response.status_code,
                "final_url": response.url,
                "elapsed_seconds": round(elapsed, 3),
                "content_type": response.headers.get("content-type"),
                "content_length": len(response.content),
                "sha256": sha256_bytes(response.content),
                "headers": dict(response.headers),
            }
        )
        if not response.ok:
            return result

        file_stem = safe_name(response.url)
        html_path = out_dir / f"{file_stem}.html"
        html_path.write_bytes(response.content)
        result["saved_html"] = str(html_path)

        soup = BeautifulSoup(response.text, "html.parser")
        result["title"] = clean(soup.title.get_text(" ", strip=True)) if soup.title else None
        result["forms"] = [form_manifest(response.url, f) for f in soup.find_all("form")]

        scripts = []
        for tag in soup.find_all("script", src=True):
            scripts.append(urljoin(response.url, tag.get("src", "")))
        result["scripts"] = list(dict.fromkeys(scripts))

        links = []
        for tag in soup.find_all("a", href=True):
            href = urljoin(response.url, tag.get("href", ""))
            text = clean(tag.get_text(" ", strip=True))
            blob = (href + " " + text).lower()
            if any(
                needle in blob
                for needle in (
                    "school",
                    "sch_",
                    "search",
                    "مدرس",
                    ".aspx",
                    ".asmx",
                    ".ashx",
                    "ajax",
                )
            ):
                links.append({"text": text, "href": href})
        result["candidate_links"] = links[:500]

        inline_refs: set[str] = set()
        for script in soup.find_all("script"):
            text = script.string or script.get_text() or ""
            for match in re.findall(
                r"['\"]([^'\"]+\.(?:aspx|asmx|ashx|json|php)(?:\?[^'\"]*)?)['\"]",
                text,
                re.I,
            ):
                inline_refs.add(urljoin(response.url, match))
        result["inline_endpoint_refs"] = sorted(inline_refs)

        # Preserve hidden ASP.NET form-state names without printing full token
        # values into the human report. The raw HTML remains the evidence copy.
        hidden_names = []
        for inp in soup.find_all("input", attrs={"type": "hidden", "name": True}):
            hidden_names.append(inp.get("name"))
        result["hidden_field_names"] = list(dict.fromkeys(hidden_names))

        return result
    except Exception as exc:  # network diagnostics must preserve failures
        result.update(
            {
                "ok": False,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "error": repr(exc),
            }
        )
        return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output-dir",
        default="artifacts/emis-local-capture",
        help="Directory for raw HTML and manifests",
    )
    ap.add_argument("--timeout", type=float, default=45.0)
    ap.add_argument(
        "--url",
        action="append",
        default=[],
        help="Additional or replacement public URL(s). May be specified multiple times.",
    )
    args = ap.parse_args()

    targets = args.url or DEFAULT_TARGETS
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    s = session()
    pages = []
    for target in targets:
        print(f"Capturing {target}", flush=True)
        pages.append(capture_page(s, target, out_dir, args.timeout))

    report = {
        "tool": "emis_local_capture",
        "version": 1,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "user_agent": USER_AGENT,
        "targets": targets,
        "reachable_pages": sum(1 for p in pages if p.get("ok")),
        "pages": pages,
        "next_gate": (
            "Do not bulk-enumerate yet. Review the captured forms/endpoints, then implement "
            "and test a conservative public-directory enumerator against the current live contract."
        ),
    }
    report_path = out_dir / "capture-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(
        {
            "ok": report["reachable_pages"] > 0,
            "reachable_pages": report["reachable_pages"],
            "total_targets": len(targets),
            "report": str(report_path),
        },
        ensure_ascii=False,
    ))

    # Reachability failure is a useful diagnostic but should return non-zero so
    # an operator does not mistakenly believe a capture succeeded.
    return 0 if report["reachable_pages"] > 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
