#!/usr/bin/env python3
"""Analyze a local EMIS contract capture and produce an enumerator design contract.

This tool is intentionally offline. It consumes the redacted capture manifest and
saved public HTML produced by `emis_local_capture.py`; it does not contact EMIS,
submit forms, enumerate schools or mutate any registry layer.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROLE_RULES = {
    "governorate": ("govern", "gov", "محافظ"),
    "directorate": ("director", "modir", "modyr", "مديري", "مديرية"),
    "administration": ("admin", "edara", "idara", "إدار", "ادار"),
    "district_or_center": ("district", "markaz", "qism", "قسم", "مركز"),
    "school_type": ("schooltype", "school_type", "type", "نوع المدرس", "نوع المدرسة"),
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
    selects = [f for f in fields if f.get("tag") == "select" and int(f.get("options_count") or 0) > 1]
    postback_selects = [f for f in selects if f.get("autopostback")]
    submits = [
        f for f in fields
        if (f.get("tag") == "button" and (f.get("type") or "submit") == "submit")
        or (f.get("tag") == "input" and f.get("type") in {"submit", "button", "image"})
    ]
    score = len(selects) * 10 + len(postback_selects) * 5 + len(submits) * 3
    state = set(form.get("aspnet_state_fields") or [])
    if "__VIEWSTATE" in state:
        score += 25
    if "__EVENTVALIDATION" in state:
        score += 15
    if (form.get("method") or "").lower() == "post":
        score += 5
    return score


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
            candidates.append({
                "score": score_form(form),
                "page": {
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
        if not multi:
            warnings.append("Primary form has no multi-option select controls to enumerate.")
        if not primary["page"]["saved_html_present"]:
            warnings.append("The primary page HTML evidence file is missing from the capture folder.")
        if primary["page"]["aspnet_detected"] and "__VIEWSTATE" not in primary["form"]["aspnet_state_fields"]:
            warnings.append("ASP.NET was detected but __VIEWSTATE is not present on the selected form.")

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

    return {
        "schema_version": 1,
        "capture_tool": report.get("tool"),
        "capture_version": report.get("version"),
        "captured_at": report.get("captured_at"),
        "reachable_pages": len(reachable),
        "candidate_forms": len(candidates),
        "adapter_design_unblocked": adapter_design_unblocked,
        "bulk_enumeration_authorized_by_this_tool": False,
        "primary_form_candidate": primary,
        "inferred_control_roles": inferred_roles,
        "warnings": warnings,
        "required_next_gate": (
            "Implement a bounded pilot adapter against the selected live form contract, preserve ASP.NET state/postbacks, "
            "and verify source IDs, pagination, failures and rate limits before any national enumeration."
            if adapter_design_unblocked
            else "Obtain a successful Egypt-reachable capture or official machine-readable export before adapter implementation."
        ),
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
