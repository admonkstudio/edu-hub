#!/usr/bin/env python3
"""Analyze a local EMIS contract capture and produce an enumerator design contract.

This tool is intentionally offline. It consumes the redacted capture manifest and
saved public HTML produced by the EMIS local tools; it does not contact EMIS,
submit forms, enumerate schools or mutate any registry layer.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROLE_RULES = {
    "governorate": ("govern", "gov", "mud", "محافظ"),
    "directorate": ("director", "modir", "modyr", "مديري", "مديرية"),
    "administration": ("admin", "edara", "idara", "إدار", "ادار"),
    "district_or_center": ("district", "markaz", "qism", "قسم", "مركز"),
    "school_type": ("schooltype", "school_type", "type", "نوع المدرس", "نوع المدرسة", "النوع"),
    "education_stage": ("stage", "level", "phase", "مرحلة"),
    "gender": ("gender", "sex", "بنين", "بنات", "طلاب"),
    "language": ("language", "lang", "لغة"),
    "ownership": ("ownership", "affiliation", "تبعية", "ملكية"),
}


def clean(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def norm(value: object) -> str:
    text = clean(value).casefold()
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي")
    return re.sub(r"\s+", " ", text)


def infer_role(field: dict) -> dict | None:
    evidence_parts = [field.get("name"), field.get("id"), field.get("label")]
    option_text = " ".join(clean(opt.get("text")) for opt in field.get("options", [])[:40])
    evidence_parts.append(option_text)
    haystack = norm(" ".join(clean(x) for x in evidence_parts if x))
    best: tuple[str, int, list[str]] | None = None
    for role, tokens in ROLE_RULES.items():
        hits = [token for token in tokens if norm(token) in haystack]
        if not hits:
            continue
        score = len(hits)
        candidate = (role, score, hits)
        if best is None or candidate[1] > best[1]:
            best = candidate
    if best is None:
        return None
    return {
        "role": best[0],
        "confidence": "medium" if best[1] == 1 else "high",
        "matched_terms": best[2],
    }


def score_form(form: dict) -> int:
    fields = form.get("fields") or []
    all_selects = [f for f in fields if f.get("tag") == "select"]
    populated_selects = [f for f in all_selects if int(f.get("options_count") or 0) > 1]
    postback_selects = [f for f in populated_selects if f.get("autopostback")]
    postback_controls = [
        f for f in fields
        if "__doPostBack" in " ".join(str(v) for v in (f.get("attrs") or {}).values())
    ]
    submits = [
        f for f in fields
        if (f.get("tag") == "button" and (f.get("type") or "submit") == "submit")
        or (f.get("tag") == "input" and f.get("type") in {"submit", "button", "image"})
    ]
    score = (
        len(all_selects) * 6
        + len(populated_selects) * 10
        + len(postback_selects) * 5
        + len(postback_controls) * 4
        + len(submits) * 3
    )
    state = set(form.get("aspnet_state_fields") or [])
    if "__VIEWSTATE" in state:
        score += 25
    if "__EVENTVALIDATION" in state:
        score += 15
    if (form.get("method") or "").lower() == "post":
        score += 5
    return score


def page_scope(page: dict) -> str:
    button = norm(page.get("button_value") or page.get("source_button_value"))
    final_url = norm(page.get("final_url"))
    if "حكوم" in button or "search_schgov" in final_url:
        return "government"
    if ("خاص" in button and "تربي" not in button) or "search_schpriv" in final_url:
        return "private"
    if "تربي" in button or "specialedu" in final_url:
        return "special_education"
    if "رياضي" in button or "sports" in final_url:
        return "sports"
    if "عسكر" in button or "military" in final_url:
        return "military"
    if "تجري" in button or "schlan" in final_url:
        return "experimental_language"
    return "unknown"


def analyze(report: dict, capture_dir: Path) -> dict:
    pages = report.get("pages") or []
    reachable = [p for p in pages if p.get("ok")]
    candidates: list[dict] = []

    for page in reachable:
        html_file = page.get("saved_html")
        html_exists = bool(html_file and (capture_dir / str(html_file)).exists())
        for form in page.get("forms") or []:
            fields = form.get("fields") or []
            selects = []
            for field in fields:
                if field.get("tag") != "select":
                    continue
                inferred = infer_role(field)
                selects.append({
                    "name": field.get("name"),
                    "id": field.get("id"),
                    "label": field.get("label"),
                    "options_count": int(field.get("options_count") or 0),
                    "autopostback": bool(field.get("autopostback")),
                    "inferred_role": inferred,
                })

            hydration_controls = []
            for field in fields:
                attrs_blob = " ".join(str(v) for v in (field.get("attrs") or {}).values())
                if field.get("tag") == "input" and field.get("type") in {"radio", "checkbox"} and "__doPostBack" in attrs_blob:
                    hydration_controls.append({
                        "name": field.get("name"),
                        "id": field.get("id"),
                        "value": field.get("value"),
                        "label": field.get("label"),
                        "attrs": field.get("attrs") or {},
                    })

            candidates.append({
                "score": score_form(form),
                "page": {
                    "request_kind": page.get("request_kind"),
                    "scope": page_scope(page),
                    "button_name": page.get("button_name") or page.get("source_button_name"),
                    "button_value": page.get("button_value") or page.get("source_button_value"),
                    "requested_url": page.get("requested_url"),
                    "final_url": page.get("final_url"),
                    "saved_html": html_file,
                    "saved_html_present": html_exists,
                    "sha256": page.get("sha256"),
                    "aspnet_detected": bool(page.get("aspnet_detected")),
                },
                "form": {
                    "index": form.get("index"),
                    "id": form.get("id"),
                    "name": form.get("name"),
                    "method": form.get("method"),
                    "action": form.get("action"),
                    "aspnet_state_fields": form.get("aspnet_state_fields") or [],
                    "postback_targets": form.get("postback_targets") or [],
                    "selects": selects,
                    "hydration_controls": hydration_controls,
                },
            })

    candidates.sort(key=lambda row: row["score"], reverse=True)
    primary = candidates[0] if candidates else None
    warnings: list[str] = []

    if not reachable:
        warnings.append("No reachable EMIS page was captured; adapter design must remain blocked.")
    if primary is None:
        warnings.append("No form candidate was found in reachable pages.")
    else:
        multi = [s for s in primary["form"]["selects"] if s["options_count"] > 1]
        empty_selects = [s for s in primary["form"]["selects"] if s["options_count"] == 0]
        if not multi:
            if empty_selects and primary["form"]["hydration_controls"]:
                warnings.append(
                    "Primary search form exposes empty select controls that require a bounded ASP.NET "
                    "control-hydration postback before adapter design can be finalized."
                )
            else:
                warnings.append("Primary form has no multi-option select controls to enumerate.")
        if not primary["page"]["saved_html_present"]:
            warnings.append("The primary page HTML evidence file is missing from the capture folder.")
        if primary["page"]["aspnet_detected"] and "__VIEWSTATE" not in primary["form"]["aspnet_state_fields"]:
            warnings.append("ASP.NET was detected but __VIEWSTATE is not present on the selected form.")
        if primary["page"]["scope"] != "government":
            warnings.append(
                f"Primary usable form scope is {primary['page']['scope']}; this is not evidence that "
                "the government-school route is healthy or enumerable."
            )

    inferred_roles = {}
    if primary:
        for field in primary["form"]["selects"]:
            role = field.get("inferred_role")
            if role:
                inferred_roles.setdefault(role["role"], []).append({
                    "name": field.get("name"),
                    "id": field.get("id"),
                    "label": field.get("label"),
                    "confidence": role.get("confidence"),
                    "matched_terms": role.get("matched_terms"),
                })

    adapter_design_unblocked = bool(
        primary
        and primary["page"]["saved_html_present"]
        and any(s["options_count"] > 1 for s in primary["form"]["selects"])
    )
    government_adapter_design_unblocked = bool(
        adapter_design_unblocked and primary and primary["page"]["scope"] == "government"
    )
    hydration_probe_recommended = bool(
        primary
        and primary["page"]["saved_html_present"]
        and primary["form"]["selects"]
        and not any(s["options_count"] > 1 for s in primary["form"]["selects"])
        and primary["form"]["hydration_controls"]
    )

    if government_adapter_design_unblocked:
        next_gate = (
            "Implement a bounded government-school pilot adapter against the selected live form contract, "
            "preserve ASP.NET state/postbacks, and verify source IDs, pagination, failures and rate limits "
            "before any national enumeration."
        )
    elif adapter_design_unblocked:
        next_gate = (
            f"Use the {primary['page']['scope']} contract only as a bounded ASP.NET mechanics pilot. "
            "Keep government-school national enumeration blocked until a healthy government search form is captured."
        )
    elif hydration_probe_recommended:
        next_gate = (
            f"Run one bounded non-search control-hydration postback on the {primary['page']['scope']} form, "
            "capture the populated selects, then re-run offline analysis. Do not submit the school-search button."
        )
    else:
        next_gate = (
            "Obtain a successful Egypt-reachable school-search form capture or official machine-readable export "
            "before adapter implementation."
        )

    return {
        "schema_version": 2,
        "capture_tool": report.get("tool"),
        "capture_version": report.get("version"),
        "captured_at": report.get("captured_at"),
        "reachable_pages": len(reachable),
        "candidate_forms": len(candidates),
        "adapter_design_unblocked": adapter_design_unblocked,
        "government_adapter_design_unblocked": government_adapter_design_unblocked,
        "hydration_probe_recommended": hydration_probe_recommended,
        "bulk_enumeration_authorized_by_this_tool": False,
        "primary_form_candidate": primary,
        "inferred_control_roles": inferred_roles,
        "warnings": warnings,
        "required_next_gate": next_gate,
        "safety": {
            "network_requests_performed": False,
            "form_submissions_performed": False,
            "school_rows_enumerated": 0,
            "edu_core_mutated": False,
            "public_promotion_performed": False,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture-dir", default="artifacts/emis-local-capture", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    report_path = args.capture_dir / "capture-report.json"
    if not report_path.exists():
        raise SystemExit(f"Missing capture report: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    result = analyze(report, args.capture_dir)

    output = args.output or (args.capture_dir / "enumerator-contract.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["adapter_design_unblocked"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
