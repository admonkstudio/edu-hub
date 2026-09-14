#!/usr/bin/env python3
"""Perform bounded non-search ASP.NET control-hydration probes on EMIS.

The live Special Education route is currently the only reachable category form.
Its dependent governorate/stage selects are populated only after choosing one of
three school-type radio controls. This probe tests those observed controls in
fresh sessions to distinguish a client-side postback problem from a server-side
data-load failure.

Safety boundary:
- one already-observed top-level category route only;
- at most three explicit non-placeholder radio postbacks;
- fresh category navigation before every postback;
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
MAX_HYDRATION_CONTROLS = 3


def plain_session() -> requests.Session:
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


def hydration_controls(form, limit: int = MAX_HYDRATION_CONTROLS) -> list[dict[str, str]]:
    """Return bounded non-placeholder radio controls with explicit postbacks."""
    out: list[dict[str, str]] = []
    for control in form.find_all("input", attrs={"type": "radio"}):
        target = event_target_from_control(control)
        value = str(control.get("value") or "")
        name = str(control.get("name") or "")
        if not target or not name or value in {"", "0"}:
            continue
        label = form.find("label", attrs={"for": control.get("id")})
        out.append(
            {
                "name": name,
                "id": str(control.get("id") or ""),
                "value": value,
                "label": capture.clean(label.get_text(" ", strip=True)) if label else "",
                "event_target": target,
            }
        )
        if len(out) >= max(1, min(limit, MAX_HYDRATION_CONTROLS)):
            break
    return out


def hydration_control(form) -> dict[str, str] | None:
    """Backward-compatible helper returning the first safe hydration control."""
    controls = hydration_controls(form, 1)
    return controls[0] if controls else None


def build_hydration_submission(
    html_text: str,
    chosen_control: dict[str, str] | None = None,
) -> tuple[str, dict[str, str], dict[str, str]]:
    soup = BeautifulSoup(html_text, "html.parser")
    form = soup.find("form")
    if form is None:
        raise ValueError("Navigated EMIS page has no form")

    available = hydration_controls(form)
    if not available:
        raise ValueError("No bounded postback hydration control was found")

    if chosen_control is None:
        chosen = available[0]
    else:
        chosen = next(
            (
                row
                for row in available
                if row["name"] == chosen_control.get("name")
                and row["value"] == chosen_control.get("value")
                and row["event_target"] == chosen_control.get("event_target")
            ),
            None,
        )
        if chosen is None:
            raise ValueError("Requested hydration control is not present on the fresh live form")

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


def visible_error_messages(html_text: str) -> list[str]:
    soup = BeautifulSoup(html_text, "html.parser")
    messages: list[str] = []
    for tag in soup.find_all(id=True):
        tag_id = str(tag.get("id") or "").casefold()
        text = capture.clean(tag.get_text(" ", strip=True))
        if not text:
            continue
        if "error" in tag_id or "خطأ" in text or "خطا" in text:
            messages.append(text)
    return list(dict.fromkeys(messages))[:20]


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

    stem = "hydrate-" + (control.get("id") or control.get("value") or "control")
    raw_path = output_dir / f"{stem}.raw.html"
    redacted_path = output_dir / f"{stem}.redacted.html"
    raw_path.write_bytes(response.content)
    redacted_path.write_text(capture.redact_hidden_values(response.text), encoding="utf-8")
    result["saved_html"] = redacted_path.name
    result["saved_raw_html_local"] = raw_path.name
    result["visible_error_messages"] = visible_error_messages(response.text)

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


def probe(output_dir: Path, timeout: float = 45.0, max_controls: int = MAX_HYDRATION_CONTROLS) -> dict:
    report_path = output_dir / "capture-report.json"
    if not report_path.exists():
        raise FileNotFoundError(f"Missing capture report: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    source_page = choose_source_page(report)

    button_name = str(source_page.get("button_name") or "")
    if not button_name.startswith(navigation.ALLOWED_BUTTON_PREFIX):
        raise RuntimeError("Captured source page is not tied to an allowed root category button")

    discovery_session = plain_session()
    category_response = navigated_category(discovery_session, button_name, timeout)
    category_response.raise_for_status()
    soup = BeautifulSoup(category_response.text, "html.parser")
    form = soup.find("form")
    if form is None:
        raise RuntimeError("Reachable EMIS search page has no form")
    controls = hydration_controls(form, max_controls)
    if not controls:
        raise RuntimeError("No safe non-search hydration controls were found")

    hydration_pages: list[dict] = []
    for requested_control in controls:
        session = plain_session()
        started = time.monotonic()
        try:
            fresh_category = navigated_category(session, button_name, timeout)
            fresh_category.raise_for_status()
            action, payload, live_control = build_hydration_submission(
                fresh_category.text,
                requested_control,
            )
            response = session.post(
                action,
                data=payload,
                timeout=timeout,
                allow_redirects=True,
                headers={"Referer": fresh_category.url},
            )
            hydration_pages.append(
                page_manifest(response, output_dir, started, source_page, live_control)
            )
        except Exception as exc:
            hydration_pages.append(
                {
                    "request_kind": "control_hydration",
                    "source_button_name": source_page.get("button_name"),
                    "source_button_value": source_page.get("button_value"),
                    "requested_url": source_page.get("final_url"),
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "hydration_control": requested_control,
                    "ok": False,
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                    "error": repr(exc),
                }
            )

    base_pages = [
        page for page in report.get("pages") or []
        if page.get("request_kind") != "control_hydration"
    ]
    report["pages"] = base_pages + hydration_pages
    report["reachable_pages"] = sum(1 for page in report["pages"] if page.get("ok"))

    populated_selects = 0
    pages_with_populated_selects = 0
    pages_with_visible_errors = 0
    for page in hydration_pages:
        page_populated = 0
        for form_manifest in page.get("forms") or []:
            page_populated += sum(
                1
                for field in form_manifest.get("fields") or []
                if field.get("tag") == "select" and int(field.get("options_count") or 0) > 1
            )
        populated_selects += page_populated
        if page_populated:
            pages_with_populated_selects += 1
        if page.get("visible_error_messages"):
            pages_with_visible_errors += 1

    report["hydration_probe"] = {
        "performed": True,
        "source_button_name": source_page.get("button_name"),
        "source_button_value": source_page.get("button_value"),
        "controls_discovered": len(controls),
        "controls_submitted": len(hydration_pages),
        "successful_hydration_pages": sum(1 for page in hydration_pages if page.get("ok")),
        "pages_with_populated_selects": pages_with_populated_selects,
        "populated_selects": populated_selects,
        "pages_with_visible_errors": pages_with_visible_errors,
        "school_searches_submitted": 0,
        "result_pagination_followed": 0,
        "school_rows_enumerated": 0,
    }
    safety = report.setdefault("safety", {})
    safety["control_hydration_form_submissions_performed"] = len(hydration_pages)
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
    ap.add_argument("--max-controls", type=int, default=MAX_HYDRATION_CONTROLS)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    try:
        result = probe(args.output_dir, args.timeout, args.max_controls)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 6
    return 0 if int(result.get("populated_selects", 0)) > 0 else 6


if __name__ == "__main__":
    raise SystemExit(main())
