#!/usr/bin/env python3
"""Acquire the British Council Egypt Partner Schools contact list.

The British Council describes the downloadable PDF as the list of schools and
institutions currently offering British Council school exams in Egypt. That is
valuable discovery/contact evidence, but it is *not* sufficient on its own to
establish Edu Hub international-school eligibility.

The source currently returns HTTP 403 to GitHub-hosted direct Python requests,
while remaining browser-accessible. Therefore this adapter supports both:

1. direct public download in environments where the source permits it; and
2. a locally/browser-downloaded PDF supplied with ``--pdf-path``.

The adapter extracts the ruled four-column tables with pdfplumber, preserves a
source-shaped supporting snapshot and never creates canonical identities,
auto-merges or public rows.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber
import requests

SOURCE_ID = "british_council_partner_schools_egypt_2026_09"
SOURCE_URL = (
    "https://www.britishcouncil.org.eg/sites/default/files/"
    "british_council_partner_schools_list_-_sep_2026_0.pdf"
)
LANDING_URL = (
    "https://www.britishcouncil.org.eg/en/exam/igcse-school/choosing/"
    "find-british-council-attached-centre"
)
USER_AGENT = "EduHubResearch/2.0 (+https://github.com/admonkstudio/edu-hub)"

EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
URL_RE = re.compile(r"(?:https?://|www\.)[^\s;,]+", re.I)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]+")


def clean(value: object) -> str | None:
    text = str(value or "")
    text = CONTROL_RE.sub("", text)
    text = text.replace("\u00ad", "").replace("\u2013", "-").replace("\u2014", "-")
    text = " ".join(text.split())
    return text or None


def stable_id(name: str, address: str | None) -> str:
    seed = f"{SOURCE_ID}\0{name.casefold()}\0{(address or '').casefold()}"
    return f"{SOURCE_ID}:{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:20]}"


def extract_contacts(contact_text: str | None) -> tuple[list[str], list[str]]:
    text = contact_text or ""
    emails = sorted({match.rstrip(".") for match in EMAIL_RE.findall(text)})
    urls = sorted({match.rstrip(".)]};,") for match in URL_RE.findall(text)})
    return emails, urls


def looks_like_header(row: list[object]) -> bool:
    cells = [clean(cell) or "" for cell in row]
    joined = " ".join(cells).casefold()
    return "school" in joined and "address" in joined and ("phone" in joined or "e-mail" in joined or "website" in joined)


def extract_rows(pdf_bytes: bytes) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    pages_with_tables = 0
    tables_seen = 0
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page_count = len(pdf.pages)
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables(
                {
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "intersection_tolerance": 5,
                    "snap_tolerance": 4,
                    "join_tolerance": 4,
                    "edge_min_length": 20,
                }
            ) or []
            if tables:
                pages_with_tables += 1
            for table in tables:
                tables_seen += 1
                for raw_row in table:
                    if not raw_row or len(raw_row) < 4 or looks_like_header(raw_row):
                        continue
                    name = clean(raw_row[0])
                    address = clean(raw_row[1])
                    phones = clean(raw_row[2])
                    contact = clean(" ".join(str(cell or "") for cell in raw_row[3:]))
                    if not name:
                        continue
                    lowered = name.casefold()
                    if lowered in {"school", "address", "phones", "e-mail / website", "e-mail /website"}:
                        continue
                    if len(name) < 3:
                        continue
                    emails, urls = extract_contacts(contact)
                    rows.append(
                        {
                            "source_id": SOURCE_ID,
                            "source_record_id": stable_id(name, address),
                            "source_snapshot_date": "2026-09-14",
                            "source_url": SOURCE_URL,
                            "source_landing_url": LANDING_URL,
                            "source_page": page_number,
                            "entity_family": "pre_university",
                            "institution_type": "school_exam_partner_candidate",
                            "name_en": name,
                            "address": address,
                            "phones_raw": phones,
                            "contact_raw": contact,
                            "emails": emails,
                            "websites": urls,
                            "scope_state": "candidate",
                            "scope_class": "international_school_candidate",
                            "supporting_evidence": "british_council_partner_school_exam_delivery",
                            "eligibility_pending": "requires_additional_international_school_evidence_and_private_independent_check",
                            "auto_eligibility": False,
                            "canonical_identity_created": False,
                            "automatic_merge_performed": False,
                            "public_promotion_performed": False,
                        }
                    )

    deduped: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = ((row.get("name_en") or "").casefold(), (row.get("address") or "").casefold())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    meta = {
        "pdf_page_count": page_count,
        "pages_with_tables": pages_with_tables,
        "tables_seen": tables_seen,
        "rows_before_exact_dedup": len(rows),
        "rows_after_exact_dedup": len(deduped),
    }
    return deduped, meta


def load_pdf(pdf_path: Path | None, timeout: float) -> tuple[bytes, str]:
    if pdf_path is not None:
        data = pdf_path.read_bytes()
        if not data.startswith(b"%PDF"):
            raise RuntimeError(f"Local file is not a PDF: {pdf_path}")
        return data, "local_browser_download"

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*;q=0.8"})
    response = session.get(SOURCE_URL, timeout=timeout)
    response.raise_for_status()
    content_type = (response.headers.get("content-type") or "").casefold()
    if "pdf" not in content_type and not response.content.startswith(b"%PDF"):
        raise RuntimeError(f"British Council download did not return a PDF: {content_type!r}")
    return response.content, "direct_http_download"


def acquire(output_dir: Path, timeout: float, pdf_path: Path | None = None) -> dict:
    pdf_bytes, capture_mode = load_pdf(pdf_path, timeout)
    rows, meta = extract_rows(pdf_bytes)
    if not rows:
        raise RuntimeError("No British Council table rows extracted")

    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "british-council-partner-schools.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source_id": SOURCE_ID,
        "source_url": SOURCE_URL,
        "landing_url": LANDING_URL,
        "capture_mode": capture_mode,
        "source_role": "supporting_discovery_contact_evidence",
        "source_rows": len(rows),
        "rows_with_address": sum(1 for row in rows if row.get("address")),
        "rows_with_phone": sum(1 for row in rows if row.get("phones_raw")),
        "rows_with_email": sum(1 for row in rows if row.get("emails")),
        "rows_with_website": sum(1 for row in rows if row.get("websites")),
        "unique_institutions_claimed": None,
        "international_eligibility_granted": 0,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "public_projection_rows_created": 0,
        "database_mutation_performed": False,
        "pdf_sha256": hashlib.sha256(pdf_bytes).hexdigest(),
        "pdf_bytes": len(pdf_bytes),
        **meta,
        "output": jsonl_path.name,
    }
    (output_dir / "british-council-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/international/british-council"))
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument("--pdf-path", type=Path)
    args = parser.parse_args()
    acquire(args.output_dir, args.timeout, args.pdf_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
