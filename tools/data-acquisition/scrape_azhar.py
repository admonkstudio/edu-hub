#!/usr/bin/env python3
"""Acquire public institute records from Al-Azhar's official institute guide.

The directory is an ASP.NET WebForms application. Its server requires governorate,
educational administration, education type and stage before it returns results.
This adapter enumerates those public filters, leaves gender unfiltered, follows the
public result-grid pagination and then fetches each public institute detail page.

No authentication, access-control bypass, reviews or private data are involved.
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
USER_AGENT = "EduHubResearchBot/0.3 (+https://github.com/admonkstudio/edu-hub; public-source-acquisition)"
GRID_EVENT_TARGET = "ctl00$MainContent$gv"


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
        # This WebForms app uses 0 for every placeholder option.
        if val in {"", "0", "-1"} or not label:
            continue
        out.append((val, label))
    return out


def form_selects(html: str):
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        raise RuntimeError("Azhar search form not found")
    return soup, form, form.find_all("select", attrs={"name": True})


def post_form(s: requests.Session, html: str, data: dict[str, str]) -> str:
    _, form, _ = form_selects(html)
    action = urljoin(SEARCH_URL, form.get("action") or SEARCH_URL)
    r = s.post(action, data=data, timeout=90)
    r.raise_for_status()
    return r.text


def postback(s: requests.Session, html: str, select_index: int, value: str) -> str:
    _, form, selects = form_selects(html)
    if select_index >= len(selects):
        return html
    target = selects[select_index].get("name")
    data = form_payload(form)
    data[target] = value
    data["__EVENTTARGET"] = target
    data["__EVENTARGUMENT"] = ""
    return post_form(s, html, data)


def submit_search(s: requests.Session, html: str, values: dict[int, str]) -> str:
    _, form, selects = form_selects(html)
    data = form_payload(form)
    for idx, val in values.items():
        if idx < len(selects):
            data[selects[idx].get("name")] = val
    # Confirmed from the live form: MainContent_btnSearch is a normal submit
    # button. The app's validation group requires gov/admin/type/stage; gender
    # and institute name may stay at their placeholder/blank values.
    data["ctl00$MainContent$btnSearch"] = "بحث"
    data["__EVENTTARGET"] = ""
    data["__EVENTARGUMENT"] = ""
    return post_form(s, html, data)


def result_ids(html: str) -> set[str]:
    return set(re.findall(r"Guide_Resault\.aspx\?id=([0-9]+)", html, re.I))


def pager_pages(html: str) -> set[int]:
    return {int(x) for x in re.findall(r"__doPostBack\(['\"]ctl00\$MainContent\$gv['\"],['\"]Page\$([0-9]+)['\"]\)", html, re.I)}


def paginate_result_ids(s: requests.Session, first_html: str, delay: float) -> set[str]:
    ids = set(result_ids(first_html))
    current_html = first_html
    max_page = max(pager_pages(first_html), default=1)
    page = 2
    while page <= max_page:
        _, form, _ = form_selects(current_html)
        data = form_payload(form)
        data["__EVENTTARGET"] = GRID_EVENT_TARGET
        data["__EVENTARGUMENT"] = f"Page${page}"
        current_html = post_form(s, current_html, data)
        ids.update(result_ids(current_html))
        max_page = max(max_page, max(pager_pages(current_html), default=max_page))
        page += 1
        if delay:
            time.sleep(delay)
    return ids


def input_label_map(soup: BeautifulSoup) -> dict[str, str]:
    """Map nearby visible labels to input values without guessing canonical fields."""
    out: dict[str, str] = {}
    for inp in soup.find_all("input"):
        value = text(inp.get("value"))
        if not value:
            continue
        label = None
        # Prefer a preceding sibling/parent label or the first cell in the row.
        parent_tr = inp.find_parent("tr")
        if parent_tr:
            cells = parent_tr.find_all(["th", "td"])
            if len(cells) >= 2:
                for cell in cells:
                    if inp in cell.descendants or cell is inp.parent:
                        continue
                    candidate = text(cell.get_text(" ", strip=True))
                    if candidate and candidate != value:
                        label = candidate
                        break
        if not label and inp.get("id"):
            lab = soup.find("label", attrs={"for": inp.get("id")})
            if lab:
                label = text(lab.get_text(" ", strip=True))
        if label:
            out[label] = value
    return out


def parse_profile(source_id: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    fields = input_label_map(soup)

    inputs = {}
    for inp in soup.find_all("input", attrs={"name": True}):
        val = text(inp.get("value"))
        typ = (inp.get("type") or "text").lower()
        if val and typ not in {"hidden", "submit", "button", "image"}:
            inputs[inp.get("name")] = val

    tables: list[list[list[str]]] = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            row = [text(c.get_text(" ", strip=True)) or "" for c in tr.find_all(["th", "td"])]
            if any(row):
                rows.append(row)
        if rows:
            tables.append(rows[:300])

    name = None
    for key, val in fields.items():
        if "اسم المعهد" in key:
            name = val
            break
    if not name:
        # Known live control naming still remains raw evidence, not a canonical
        # field mapping. Try institution-name-like controls before other inputs.
        for k, val in inputs.items():
            kl = k.lower()
            if "instname" in kl or ("inst" in kl and "name" in kl):
                name = val
                break
    if not name:
        # Public result pages expose the institution name in the document text;
        # retain null if we cannot reliably bind it to an input.
        name = None

    location_parts = []
    for key, val in fields.items():
        if any(x in key for x in ("العنوان", "الادارة التعليمية", "الإدارة التعليمية")):
            if val not in location_parts:
                location_parts.append(val)

    map_urls = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "maps" in href.lower() or "google." in href.lower():
            map_urls.append(urljoin(RESULT_URL.format(source_id), href))

    return {
        "source_record_id": source_id,
        "source_url": RESULT_URL.format(source_id),
        "name_raw": name,
        "entity_type_raw": "azhar_institute",
        "location_raw": " | ".join(location_parts) or None,
        "payload": {
            "fields": fields,
            "inputs": inputs,
            "tables": tables,
            "map_urls": list(dict.fromkeys(map_urls))[:10],
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="artifacts/azhar_snapshot.jsonl")
    ap.add_argument("--delay", type=float, default=0.25)
    ap.add_argument("--max-governorates", type=int, default=0)
    ap.add_argument("--max-admins-per-governorate", type=int, default=0)
    ap.add_argument("--max-profiles", type=int, default=0)
    args = ap.parse_args()

    s = session()
    first = s.get(SEARCH_URL, timeout=90)
    first.raise_for_status()
    _, form, selects = form_selects(first.text)
    if len(selects) < 5:
        raise RuntimeError(f"Expected 5 Azhar search selects, found {len(selects)}")
    govs = options(selects[0])
    if args.max_governorates > 0:
        govs = govs[: args.max_governorates]
    print(json.dumps({"stage": "form_inventory", "select_count": len(selects), "governorates": len(govs), "select_names": [x.get("name") for x in selects]}, ensure_ascii=False))

    ids: set[str] = set()
    query_count = 0
    for gi, (gov_value, gov_label) in enumerate(govs, start=1):
        try:
            gov_html = postback(s, first.text, 0, gov_value)
            _, _, gov_selects = form_selects(gov_html)
            admins = options(gov_selects[1])
            if args.max_admins_per_governorate > 0:
                admins = admins[: args.max_admins_per_governorate]
            gov_found: set[str] = set()

            for ai, (admin_value, admin_label) in enumerate(admins, start=1):
                try:
                    admin_html = postback(s, gov_html, 1, admin_value)
                    _, _, admin_selects = form_selects(admin_html)
                    type_opts = options(admin_selects[2])
                    stage_opts = options(admin_selects[3])
                    admin_found: set[str] = set()

                    for type_value, type_label in type_opts:
                        for stage_value, stage_label in stage_opts:
                            # Gender remains 0 (unfiltered); the live validation
                            # message confirms it is not required.
                            result_html = submit_search(
                                s,
                                admin_html,
                                {0: gov_value, 1: admin_value, 2: type_value, 3: stage_value, 4: "0"},
                            )
                            query_count += 1
                            combo_ids = paginate_result_ids(s, result_html, args.delay)
                            admin_found.update(combo_ids)
                            if combo_ids:
                                print(json.dumps({
                                    "stage": "filter",
                                    "governorate": gov_label,
                                    "administration": admin_label,
                                    "education_type": type_label,
                                    "education_stage": stage_label,
                                    "found": len(combo_ids),
                                    "total_ids": len(ids | gov_found | admin_found),
                                }, ensure_ascii=False))
                            if args.delay:
                                time.sleep(args.delay)

                    gov_found.update(admin_found)
                    print(json.dumps({
                        "stage": "administration",
                        "governorate": gov_label,
                        "index": ai,
                        "administration": admin_label,
                        "found": len(admin_found),
                        "governorate_total": len(gov_found),
                    }, ensure_ascii=False))
                except Exception as exc:
                    print(json.dumps({"stage": "administration_error", "governorate": gov_label, "administration": admin_label, "error": repr(exc)}, ensure_ascii=False))
                if args.delay:
                    time.sleep(args.delay)

            before = len(ids)
            ids.update(gov_found)
            print(json.dumps({
                "stage": "governorate",
                "index": gi,
                "governorate": gov_label,
                "administrations": len(admins),
                "found": len(gov_found),
                "new": len(ids) - before,
                "total": len(ids),
                "search_queries": query_count,
            }, ensure_ascii=False))
        except Exception as exc:
            print(json.dumps({"stage": "governorate_error", "governorate": gov_label, "error": repr(exc)}, ensure_ascii=False))
        if args.delay:
            time.sleep(args.delay)

    ordered = sorted(ids)
    if args.max_profiles > 0:
        ordered = ordered[: args.max_profiles]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    named = 0
    with out.open("w", encoding="utf-8") as f:
        for i, source_id in enumerate(ordered, start=1):
            try:
                r = s.get(RESULT_URL.format(source_id), timeout=90)
                r.raise_for_status()
                row = parse_profile(source_id, r.text)
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1
                if row.get("name_raw"):
                    named += 1
            except Exception as exc:
                print(json.dumps({"stage": "profile_error", "id": source_id, "error": repr(exc)}, ensure_ascii=False))
            if i % 100 == 0:
                print(json.dumps({"stage": "profiles", "processed": i, "written": written, "named": named, "total": len(ordered)}, ensure_ascii=False))
            if args.delay:
                time.sleep(args.delay)
    print(json.dumps({"ok": True, "discovered": len(ids), "written": written, "named": named, "search_queries": query_count, "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
