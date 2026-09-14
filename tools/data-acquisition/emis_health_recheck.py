#!/usr/bin/env python3
"""Run a lightweight, non-enumerating health recheck against the EMIS directory.

This is the post-diagnostic D1.3 monitor. It only verifies whether the official
root and category-navigation routes have recovered enough to justify a fresh
contract capture. It never selects school filters, submits a school search,
follows result pagination, or enumerates school rows.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import emis_navigation_probe as navigation  # noqa: E402

ROOT_URL = navigation.ROOT_URL
GOVERNMENT_ROUTE_TOKEN = "search_schgov.aspx"
VISIBLE_ERROR_TOKENS = ("خطأ اثناء محاولة تحميل الصفحة", "خطا اثناء محاولة تحميل الصفحة")


def page_has_visible_load_error(text: str) -> bool:
    normalized = " ".join((text or "").split())
    return any(token in normalized for token in VISIBLE_ERROR_TOKENS)


def government_route_healthy(row: dict) -> bool:
    if not row.get("ok"):
        return False
    if int(row.get("status_code") or 0) != 200:
        return False
    if GOVERNMENT_ROUTE_TOKEN not in str(row.get("final_url") or "").lower():
        return False
    if row.get("visible_load_error"):
        return False
    return True


def category_row(button: dict[str, str], timeout: float) -> dict:
    session = navigation.navigation_session()
    started = time.monotonic()
    try:
        root = session.get(ROOT_URL, timeout=timeout, allow_redirects=True)
        root.raise_for_status()
        action, payload, live_value = navigation.build_button_submission(root.text, button["name"])
        response = session.post(
            action,
            data=payload,
            timeout=timeout,
            allow_redirects=True,
            headers={"Referer": ROOT_URL},
        )
        return {
            "button_name": button["name"],
            "button_value": live_value,
            "status_code": response.status_code,
            "ok": response.ok,
            "final_url": response.url,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "visible_load_error": page_has_visible_load_error(response.text) if response.ok else False,
        }
    except Exception as exc:
        return {
            "button_name": button.get("name"),
            "button_value": button.get("value"),
            "ok": False,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "error": repr(exc),
        }


def probe(timeout: float = 30.0, max_buttons: int = 6) -> dict:
    discovery = navigation.navigation_session()
    started = time.monotonic()
    try:
        root = discovery.get(ROOT_URL, timeout=timeout, allow_redirects=True)
        root.raise_for_status()
        buttons = navigation.root_navigation_buttons(root.text)[:max_buttons]
        root_result = {
            "ok": True,
            "status_code": root.status_code,
            "final_url": root.url,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "buttons_discovered": len(buttons),
        }
    except Exception as exc:
        return {
            "schema_version": 1,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "root": {
                "ok": False,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "error": repr(exc),
            },
            "categories": [],
            "government_route_healthy": False,
            "fresh_contract_capture_recommended": False,
            "pilot_enumeration_authorized": False,
        }

    rows = [category_row(button, timeout) for button in buttons]
    government = next(
        (
            row
            for row in rows
            if "حكوم" in str(row.get("button_value") or "")
            or GOVERNMENT_ROUTE_TOKEN in str(row.get("final_url") or "").lower()
        ),
        None,
    )
    gov_healthy = bool(government and government_route_healthy(government))

    return {
        "schema_version": 1,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "root": root_result,
        "categories": rows,
        "government_route_healthy": gov_healthy,
        "fresh_contract_capture_recommended": gov_healthy,
        "pilot_enumeration_authorized": False,
        "next_gate": (
            "Government route recovered: run a fresh full contract capture and review it before any bounded pilot."
            if gov_healthy
            else "Government route is still unhealthy: keep enumeration blocked and continue the official-export track."
        ),
        "safety": {
            "school_searches_submitted": 0,
            "result_pagination_followed": 0,
            "school_rows_enumerated": 0,
            "registry_mutation_performed": False,
            "public_promotion_performed": False,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--max-buttons", type=int, default=6)
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/emis-health-recheck.json"),
    )
    args = ap.parse_args()

    result = probe(args.timeout, max(1, min(args.max_buttons, 6)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
