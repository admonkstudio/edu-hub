#!/usr/bin/env python3
"""Acquire public institute records from Al-Azhar's official institute guide.

The directory is an ASP.NET WebForms application. This adapter uses the public search
form only, preserves source IDs/URLs, and does not attempt to bypass access controls.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SEARCH_URL = "https://azhar.gov.eg/IDSC/InstGuide/Guide_Search.aspx"
RESULT_URL = "https://azhar.gov.eg/IDSC/InstGuide/Guide_Resault.aspx?id={}"
USER_AGENT = "EduHubResearchBot/0.2 (+https://github.com/admonkstudio/edu-hub; public-source-acquisition)"


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=4, backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("GET", "POST"))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "ar,en;q=0.8"})
    return s


def text(v: str | None) -> str | None:
    if v is None:
        return None
    v = re.sub(r"\s+", " ", v).strip()
    return v or None


def form_payload(form: BeautifulSoup) -> dict[str, str]:
    data: dict[str, str] = {}
    for inp in form.find_all("input", attrs={"name": True}):
        typ = (inp.get("type") or "text").lower()
        if typ in {"submit", "button", "image", "file"}:
            continue
        if typ in {"checkbox", "radio"} and not inp.has_attr("checked"):
            continue
        data[inp.get("name")] = inp.get("value", "")
    for sel in form.find_all("select", attrs={"name": True}):
        opt = sel.find("option", selected=True) or sel.find("option")
        data[sel.get("name")] = opt.get("value", "") if opt else ""
    return data


def options(sel) -> list[tuple[str, str]]:
    out = []
    for opt in sel.find_all("option"):
        val = (opt.get("value") or "").strip()
        label = text(opt.get_text(" ", strip=True)) or ""
        if val and label and label not in {"اختر", "Select", "-- اختر --", "- اختر -"}:
            out.append((val, label))
    return out


def postback(s: requests.Session, html: str, select_index: int, value: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise RuntimeError("Azhar search form not found")
    selects = form.find_all("select", attrs={"name": True})
    if select_index >= len(selects):
        return html
    target = selects[select_index].get("name")
    data = form_payload(form)
    data[target] = value
    data["__EVENTTARGET"] = target
    data["__EVENTARGUMENT"] = ""
    action = urljoin(SEARCH_URL, form.get("action") or SEARCH_URL)
    r = s.post(action, data=data, timeout=90)
    r.raise_for_status()
    return r.text


def submit_search(s: requests.Session, html: str, values: dict[int, str]) -> str:
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise RuntimeError("Azhar search form not found")
    selects = form.find_all("select", attrs={"name": True})
    data = form_payload(form)
    for idx, val in values.items():
        if idx < len(selects):
            data[selects[idx].get("name")] = val
    submit = None
    for node in form.find_all(["input", "button"]):
        typ = (node.get("type") or "").lower()
        val = text(node.get("value") or node.get_text(" ", strip=True)) or ""
        if typ in {"submit", "button"} and any(k in val for k in ("بحث", "Search", "اظهار", "عرض")):
            submit = node
            break
    if submit and submit.get("name"):
        data[submit.get("name")] = submit.get("value", "")
    data["__EVENTTARGET"] = ""
    data["__EVENTARGUMENT"] = ""
    action = urljoin(SEARCH_URL, form.get("action") or SEARCH_URL)
    r = s.post(action, data=data, timeout=90)
    r.raise_for_status()
    return r.text


def result_ids(html: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    ids: set[str] = set()
    for a in soup.find_all("a", href=True):
        m = re.search(r"Guide_Resault\.aspx\?id=([0-9]+)", a.get("href", ""), re.I)
        if m:
            ids.add(m.group(1))
    # Some WebForms result grids use JS window.open strings rather than anchors.
    for m in re.finditer(r"Guide_Resault\.aspx\?id=([0-9]+)", html, re.I):
        ids.add(m.group(1))
    return ids


def parse_profile(source_id: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    fields: dict[str, str] = {}
    # Most detail fields are rendered as labelled table rows with input values.
    for tr in soup.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if len(cells) < 2:
            continue
        label = text(cells[0].get_text(" ", strip=True))
        value = None
        inp = cells[1].find("input")
        if inp is not None:
            value = text(inp.get("value"))
        if not value:
            value = text(cells[1].get_text(" ", strip=True))
        if label and value:
            fields[label] = value
    # Fallback: capture named readonly/text inputs when row semantics differ.
    inputs = {}
    for inp in soup.find_all("input", attrs={"name": True}):
        val = text(inp.get("value"))
        if val:
            inputs[inp.get("name")] = val

    tables: list[list[list[str]]] = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            row = [text(c.get_text(" ", strip=True)) or "" for c in tr.find_all(["th", "td"])]
            if any(row):
                rows.append(row)
        if rows:
            tables.append(rows[:200])

    name = None
    for key, val in fields.items():
        if "اسم المعهد" in key:
            name = val
            break
    if not name:
        for k, val in inputs.items():
            if "name" in k.lower() or "inst" in k.lower():
                name = val
                break

    location = None
    for key, val in fields.items():
        if any(x in key for x in ("العنوان", "الادارة التعليمية", "الإدارة التعليمية")):
            location = (location + " | " if location else "") + val

    return {
        "source_record_id": source_id,
        "source_url": RESULT_URL.format(source_id),
        "name_raw": name,
        "entity_type_raw": "azhar_institute",
        "location_raw": location,
        "payload": {"fields": fields, "inputs": inputs, "tables": tables},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="artifacts/azhar_snapshot.jsonl")
    ap.add_argument("--delay", type=float, default=0.25)
    ap.add_argument("--max-governorates", type=int, default=0)
    ap.add_argument("--max-profiles", type=int, default=0)
    args = ap.parse_args()

    s = session()
    first = s.get(SEARCH_URL, timeout=90)
    first.raise_for_status()
    soup = BeautifulSoup(first.text, "html.parser")
    form = soup.find("form")
    if not form:
        raise RuntimeError("Azhar search form not found")
    selects = form.find_all("select", attrs={"name": True})
    if not selects:
        raise RuntimeError("Azhar governorate select not found")
    govs = options(selects[0])
    if args.max_governorates > 0:
        govs = govs[: args.max_governorates]
    print(json.dumps({"stage": "form_inventory", "select_count": len(selects), "governorates": len(govs), "select_names": [x.get("name") for x in selects]}, ensure_ascii=False))

    ids: set[str] = set()
    for gi, (gov_value, gov_label) in enumerate(govs, start=1):
        try:
            gov_html = postback(s, first.text, 0, gov_value)
            gov_soup = BeautifulSoup(gov_html, "html.parser")
            gov_form = gov_soup.find("form")
            gov_selects = gov_form.find_all("select", attrs={"name": True}) if gov_form else []
            admins = options(gov_selects[1]) if len(gov_selects) > 1 else []

            # First try a governorate-wide search. If the application requires an
            # administration, fall back to each populated administration option.
            result_html = submit_search(s, gov_html, {0: gov_value, 1: ""})
            found = result_ids(result_html)
            if not found and admins:
                for admin_value, admin_label in admins:
                    try:
                        admin_html = postback(s, gov_html, 1, admin_value)
                        result_html = submit_search(s, admin_html, {0: gov_value, 1: admin_value})
                        admin_ids = result_ids(result_html)
                        found.update(admin_ids)
                        print(json.dumps({"stage": "administration", "governorate": gov_label, "administration": admin_label, "found": len(admin_ids)}, ensure_ascii=False))
                        time.sleep(args.delay)
                    except Exception as exc:
                        print(json.dumps({"stage": "administration_error", "governorate": gov_label, "administration": admin_label, "error": repr(exc)}, ensure_ascii=False))
            before = len(ids)
            ids.update(found)
            print(json.dumps({"stage": "governorate", "index": gi, "governorate": gov_label, "found": len(found), "new": len(ids)-before, "total": len(ids)}, ensure_ascii=False))
        except Exception as exc:
            print(json.dumps({"stage": "governorate_error", "governorate": gov_label, "error": repr(exc)}, ensure_ascii=False))
        time.sleep(args.delay)

    ordered = sorted(ids)
    if args.max_profiles > 0:
        ordered = ordered[: args.max_profiles]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with out.open("w", encoding="utf-8") as f:
        for i, source_id in enumerate(ordered, start=1):
            try:
                r = s.get(RESULT_URL.format(source_id), timeout=90)
                r.raise_for_status()
                f.write(json.dumps(parse_profile(source_id, r.text), ensure_ascii=False) + "\n")
                written += 1
            except Exception as exc:
                print(json.dumps({"stage": "profile_error", "id": source_id, "error": repr(exc)}, ensure_ascii=False))
            if i % 100 == 0:
                print(json.dumps({"stage": "profiles", "processed": i, "written": written, "total": len(ordered)}, ensure_ascii=False))
            time.sleep(args.delay)
    print(json.dumps({"ok": True, "discovered": len(ids), "written": written, "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
