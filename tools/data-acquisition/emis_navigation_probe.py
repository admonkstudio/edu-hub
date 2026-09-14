#!/usr/bin/env python3
"""Resolve EMIS top-level school-search navigation through the live ASP.NET form.

The Egyptian Schools Directory root currently exposes school categories as
server-side submit buttons rather than stable GET links. Direct GETs to historical
search routes can return HTTP 500 even though the root is healthy.

This probe performs only bounded top-level navigation:
- GET a fresh root form for each button;
- preserve the live hidden ASP.NET state;
- POST exactly one visible category button;
- capture the resulting page/form contract;
- append redacted evidence to the existing capture report.

It never selects governorates/administrations, executes a school search, follows
result pagination, enumerates school rows, authenticates or bypasses controls.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import emis_local_capture as capture  # noqa: E402

ROOT_URL = "https://search.emis.gov.eg/"
ALLOWED_BUTTON_PREFIX = "ctl00$ContentPlaceHolder1$Button"
MAX_ROOT_BUTTONS = 8


def navigation_session() -> requests.Session:
    """Use no status-code retries so live EMIS 500s remain explicit evidence."""
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": capture.USER_AGENT,
            "Accept-Language": "ar-EG,ar;q=0.9,en;q=0.7",
        }
    )
    return s


def root_navigation_buttons(html_text: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html_text, "html.parser")
    form = soup.find("form")
    if form is None:
        return []
    out: list[dict[str, str]] = []
    for element in form.find_all("input"):
        if (element.get("type") or "").lower() != "submit":
            continue
        name = str(element.get("name") or "")
        value = capture.clean(element.get("value"))
        if not name.startswith(ALLOWED_BUTTON_PREFIX) or not value:
            continue
        out.append({"name": name, "value": value, "id": str(element.get("id") or "")})
    return out[:MAX_ROOT_BUTTONS]


def build_button_submission(html_text: str, button_name: str) -> tuple[str, dict[str, str], str]:
    """Return (form_action, payload, button_value) for one visible root button."""
    soup = BeautifulSoup(html_text, "html.parser")
    form = soup.find("form")
    if form is None:
        raise ValueError("EMIS root has no form")

    button = form.find("input", attrs={"name": button_name})
    if button is None or (button.get("type") or "").lower() != "submit":
        raise ValueError(f"Root navigation button not found: {button_name}")
    if not button_name.startswith(ALLOWED_BUTTON_PREFIX):
        raise ValueError(f"Refusing non-navigation button: {button_name}")

    payload: dict[str, str] = {}
    for inp in form.find_all("input"):
        name = inp.get("name")
        if not name:
            continue
        input_type = (inp.get("type") or "text").lower()
        if input_type == "hidden":
            payload[str(name)] = str(inp.get("value") or "")

    button_value = str(button.get("value") or "")
    payload[button_name] = button_value
    action = urljoin(ROOT_URL, form.get("action") or ROOT_URL)
    return action, payload, button_value


def response_manifest(
    response: requests.Response,
    out_dir: Path,
    started: float,
    button: dict[str, str],
) -> dict:
    elapsed = time.monotonic() - started
    result: dict[str, object] = {
        "request_kind": "root_button_navigation",
        "requested_url": ROOT_URL,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "button_name": button["name"],
        "button_id": button.get("id"),
        "button_value": button["value"],
        "ok": response.ok,
        "status_code": response.status_code,
        "final_url": response.url,
        "elapsed_seconds": round(elapsed, 3),
        "content_type": response.headers.get("content-type"),
        "content_length": len(response.content),
        "sha256": capture.sha256_bytes(response.content),
        "redirect_chain": [
            {"status_code": item.status_code, "url": item.url, "location": item.headers.get("location")}
            for item in response.history
        ],
        "headers": {
            key: value
            for key, value in response.headers.items()
            if key.lower() in {
                "content-type",
                "content-length",
                "server",
                "cache-control",
                "date",
                "last-modified",
                "etag",
                "x-powered-by",
            }
        },
    }
    if not response.ok:
        return result

    stem = "nav-" + (button.get("id") or button["name"].split("$")[-1])
    raw_path = out_dir / f"{stem}.raw.html"
    redacted_path = out_dir / f"{stem}.redacted.html"
    raw_path.write_bytes(response.content)
    redacted_path.write_text(capture.redact_hidden_values(response.text), encoding="utf-8")
    result["saved_html"] = redacted_path.name
    result["saved_raw_html_local"] = raw_path.name

    soup = BeautifulSoup(response.text, "html.parser")
    result["title"] = capture.clean(soup.title.get_text(" ", strip=True)) if soup.title else None
    result["html_lang"] = soup.html.get("lang") if soup.html else None
    result["forms"] = [capture.form_manifest(response.url, form, i) for i, form in enumerate(soup.find_all("form"))]
    result["scripts"] = list(dict.fromkeys(urljoin(response.url, tag.get("src", "")) for tag in soup.find_all("script", src=True)))

    links = []
    for tag in soup.find_all("a", href=True):
        href = urljoin(response.url, tag.get("href", ""))
        text = capture.clean(tag.get_text(" ", strip=True))
        blob = (href + " " + text).lower()
        if any(token in blob for token in ("school", "sch_", "search", "مدرس", ".aspx", ".asmx", ".ashx", "ajax")):
            links.append({"text": text, "href": href})
    result["candidate_links"] = links[:500]

    hidden_names = [
        inp.get("name")
        for inp in soup.find_all("input", attrs={"type": "hidden", "name": True})
        if inp.get("name")
    ]
    result["hidden_field_names"] = list(dict.fromkeys(hidden_names))
    result["aspnet_detected"] = any(
        name in {"__VIEWSTATE", "__EVENTVALIDATION", "__VIEWSTATEGENERATOR"}
        for name in hidden_names
    )
    return result


def probe(output_dir: Path, timeout: float = 45.0, max_buttons: int = 6) -> dict:
    report_path = output_dir / "capture-report.json"
    if not report_path.exists():
        raise FileNotFoundError(f"Missing capture report: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))

    discovery_session = navigation_session()
    root = discovery_session.get(ROOT_URL, timeout=timeout, allow_redirects=True)
    root.raise_for_status()
    buttons = root_navigation_buttons(root.text)[: max(1, min(max_buttons, MAX_ROOT_BUTTONS))]
    if not buttons:
        raise RuntimeError("No bounded EMIS root navigation buttons were found")

    navigation_pages: list[dict] = []
    for button in buttons:
        session = navigation_session()
        started = time.monotonic()
        try:
            fresh_root = session.get(ROOT_URL, timeout=timeout, allow_redirects=True)
            fresh_root.raise_for_status()
            action, payload, live_value = build_button_submission(fresh_root.text, button["name"])
            live_button = {**button, "value": live_value}
            response = session.post(
                action,
                data=payload,
                timeout=timeout,
                allow_redirects=True,
                headers={"Referer": ROOT_URL},
            )
            navigation_pages.append(response_manifest(response, output_dir, started, live_button))
        except Exception as exc:
            navigation_pages.append({
                "request_kind": "root_button_navigation",
                "requested_url": ROOT_URL,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "button_name": button["name"],
                "button_id": button.get("id"),
                "button_value": button["value"],
                "ok": False,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "error": repr(exc),
            })

    base_pages = [page for page in report.get("pages") or [] if page.get("request_kind") != "root_button_navigation"]
    report["pages"] = base_pages + navigation_pages
    report["reachable_pages"] = sum(1 for page in report["pages"] if page.get("ok"))
    report["navigation_probe"] = {
        "performed": True,
        "root_url": ROOT_URL,
        "buttons_discovered": len(buttons),
        "buttons_submitted": len(navigation_pages),
        "successful_navigation_pages": sum(1 for page in navigation_pages if page.get("ok")),
        "school_searches_submitted": 0,
        "result_pagination_followed": 0,
        "school_rows_enumerated": 0,
    }
    safety = report.setdefault("safety", {})
    safety["root_navigation_form_submissions_performed"] = len(navigation_pages)
    safety["school_search_form_submissions_performed"] = 0
    safety["bulk_enumeration_performed"] = False

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = report["navigation_probe"]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="artifacts/emis-local-capture", type=Path)
    ap.add_argument("--timeout", type=float, default=45.0)
    ap.add_argument("--max-buttons", type=int, default=6)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = probe(args.output_dir, args.timeout, args.max_buttons)
    return 0 if int(result.get("successful_navigation_pages", 0)) > 0 else 5


if __name__ == "__main__":
    raise SystemExit(main())
