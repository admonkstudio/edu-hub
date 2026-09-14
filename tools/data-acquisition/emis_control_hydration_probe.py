#!/usr/bin/env python3
"""Perform one bounded ASP.NET control-hydration postback on a captured EMIS search form.

This probe exists to learn the live dependent-control contract without running a
school search. It may select one non-placeholder radio option that explicitly
declares an ASP.NET __doPostBack handler, then captures the resulting populated
search form.

Safety boundary:
- one already-observed top-level category route only;
- one explicit postback control only;
- no search button submission;
- no pagination;
- no school rows enumerated;
- no registry mutation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import emis_local_capture as capture  # noqa: E402
import emis_navigation_probe as navigation  # noqa: E402

ROOT_URL = navigation.ROOT_URL
ALLOWED_EVENT_PREFIX = "ctl00$ContentPlaceHolder1$RadioButtonList"
POSTBACK_TARGET_RE = re.compile(r"__doPostBack\(\s*\\?['\"]([^\\'\"]+)", re.I)


def plain_session() -> requests.Session:
    """Session without status-code retries so server failures remain observable."""
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": capture.USER_AGENT,
            "Accept-Language": "ar-EG,ar;q=0.9,en;q=0.7",
        }
    )
    return s


def event_target_from_control(control) -> str | None:
    onclick = str(control.get("onclick") or "")
    match = POSTBACK_TARGET_RE.search(onclick)
    if not match:
        return None
    target = match.group(1)
    if not target.startswith(ALLOWED_EVENT_PREFIX):
        return None
    return target


def hydration_control(form) -> dict[str, str] | None:
    """Pick the first non-placeholder radio with an explicit whitelisted postback."""
    for control in form.find_all("input", attrs={"type": "radio"}):
        target = event_target_from_control(control)
        value = str(control.get("value") or "")
        name = str(control.get("name") or "")
        if not target or not name or value in {"", "0"}:
            continue
        label = form.find("label", attrs={"for": control.get("id")})
        return {
            "name": name,
            "id": str(control.get("id") or ""),
            "value": value,
            "label": capture.clean(label.get_text(" ", strip=True)) if label else "",
            "event_target": target,
        }
    return None


def build_hydration_submission(html_text: str) -> tuple[str, dict[str, str], dict[str, str]]:
    soup = BeautifulSoup(html_text, "html.parser")
    form = soup.find("form")
    if form is None:
        raise ValueError("Navigated EMIS page has no form")

    chosen = hydration_control(form)
    if chosen is None:
        raise ValueError("No bounded postback hydration control was found")

    payload: dict[str, str] = {}
    for inp in form.find_all("input"):
        name = inp.get("name")
        if not name:
            continue
        input_type = (inp.get("type") or "text").lower()
        if input_type == "hidden":
            payload[str(name)] = str(inp.get("value") or "")

    payload["__EVENTTARGET"] = chosen["event_target"]
    payload["__EVENTARGUMENT"] = ""
    payload[chosen["name"]] = chosen["value"]

    action = urljoin(ROOT_URL, form.get("action") or ROOT_URL)
    if urlparse(action).hostname != urlparse(ROOT_URL).hostname:
        raise ValueError("Refusing off-origin hydration action")
    return action, payload, chosen


def navigated_category(session: requests.Session, button_name: str, timeout: float) -> requests.Response:
    root = session.get(ROOT_URL, timeout=timeout, allow_redirects=True)
    root.raise_for_status()
    action, payload, _value = navigation.build_button_submission(root.text, button_name)
    return session.post(
        action,
        data=payload,
        timeout=timeout,
        allow_redirects=True,
        headers={"Referer": ROOT_URL},
    )


def page_manifest(
    response: requests.Response,
    output_dir: Path,
    started: float,
    source_page: dict,
    control: dict[str, str],
) -> dict:
    elapsed = time.monotonic() - started
    result: dict[str, object] = {
        "request_kind": "control_hydration",
        "source_button_name": source_page.get("button_name"),
        "source_button_value": source_page.get("button_value"),
        "requested_url": response.request.url,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "hydration_control": control,
        "ok": response.ok,
        "status_code": response.status_code,
        "final_url": response.url,
        "elapsed_seconds": round(elapsed, 3),
        "content_type": response.headers.get("content-type"),
        "content_length": len(response.content),
        "sha256": capture.sha256_bytes(response.content),
    }
    if not response.ok:
        return result

    stem = "hydrate-" + (control.get("id") or "control")
    raw_path = output_dir / f"{stem}.raw.html"
    redacted_path = output_dir / f"{stem}.redacted.html"
    raw_path.write_bytes(response.content)
    redacted_path.write_text(capture.redact_hidden_values(response.text), encoding="utf-8")
    result["saved_html"] = redacted_path.name
    result["saved_raw_html_local"] = raw_path.name

    soup = BeautifulSoup(response.text, "html.parser")
    result["title"] = capture.clean(soup.title.get_text(" ", strip=True)) if soup.title else None
    result["html_lang"] = soup.html.get("lang") if soup.html else None
    result["forms"] = [
        capture.form_manifest(response.url, form, i)
        for i, form in enumerate(soup.find_all("form"))
    ]
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


def choose_source_page(report: dict) -> dict:
    for page in report.get("pages") or []:
        if page.get("request_kind") != "root_button_navigation" or not page.get("ok"):
            continue
        forms = page.get("forms") or []
        if not forms:
            continue
        fields = forms[0].get("fields") or []
        has_select = any(field.get("tag") == "select" for field in fields)
        has_postback_radio = any(
            field.get("tag") == "input"
            and field.get("type") == "radio"
            and "__doPostBack" in " ".join(str(v) for v in (field.get("attrs") or {}).values())
            for field in fields
        )
        if has_select and has_postback_radio:
            return page
    raise RuntimeError("No reachable EMIS search form requires safe control hydration")


def probe(output_dir: Path, timeout: float = 45.0) -> dict:
    report_path = output_dir / "capture-report.json"
    if not report_path.exists():
        raise FileNotFoundError(f"Missing capture report: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    source_page = choose_source_page(report)

    button_name = str(source_page.get("button_name") or "")
    if not button_name.startswith(navigation.ALLOWED_BUTTON_PREFIX):
        raise RuntimeError("Captured source page is not tied to an allowed root category button")

    session = plain_session()
    started = time.monotonic()
    category_response = navigated_category(session, button_name, timeout)
    category_response.raise_for_status()

    action, payload, control = build_hydration_submission(category_response.text)
    response = session.post(
        action,
        data=payload,
        timeout=timeout,
        allow_redirects=True,
        headers={"Referer": category_response.url},
    )
    hydration_page = page_manifest(response, output_dir, started, source_page, control)

    base_pages = [
        page for page in report.get("pages") or []
        if page.get("request_kind") != "control_hydration"
    ]
    report["pages"] = base_pages + [hydration_page]
    report["reachable_pages"] = sum(1 for page in report["pages"] if page.get("ok"))

    populated_selects = 0
    for form in hydration_page.get("forms") or []:
        populated_selects += sum(
            1
            for field in form.get("fields") or []
            if field.get("tag") == "select" and int(field.get("options_count") or 0) > 1
        )

    report["hydration_probe"] = {
        "performed": True,
        "source_button_name": source_page.get("button_name"),
        "source_button_value": source_page.get("button_value"),
        "controls_submitted": 1,
        "hydration_control": control,
        "successful_hydration_pages": 1 if hydration_page.get("ok") else 0,
        "populated_selects": populated_selects,
        "school_searches_submitted": 0,
        "result_pagination_followed": 0,
        "school_rows_enumerated": 0,
    }
    safety = report.setdefault("safety", {})
    safety["control_hydration_form_submissions_performed"] = 1
    safety["school_search_form_submissions_performed"] = 0
    safety["bulk_enumeration_performed"] = False

    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["hydration_probe"], ensure_ascii=False, indent=2))
    return report["hydration_probe"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="artifacts/emis-local-capture", type=Path)
    ap.add_argument("--timeout", type=float, default=45.0)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    try:
        result = probe(args.output_dir, args.timeout)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 6
    return 0 if int(result.get("populated_selects", 0)) > 0 else 6


if __name__ == "__main__":
    raise SystemExit(main())
