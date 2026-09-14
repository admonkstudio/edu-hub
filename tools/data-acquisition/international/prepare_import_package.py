#!/usr/bin/env python3
"""Prepare a provenance-safe EDU-DATA-2 import package.

Inputs are the deterministic authoritative candidate artifact and the reviewed
Wikimedia media seed. The package mirrors edu_raw / edu_staging boundaries but
does NOT connect to PostgreSQL and does NOT create canonical edu_core identities.

This is deliberately an import *package*, not an auto-merge tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
SEED_DIR = HERE / "seeds"

SOURCE_META = {
    "ib_world_schools_egypt": ("International Baccalaureate - Egypt World Schools", "international_authorizer"),
    "french_homologation_2026_2027": ("French Ministry - Homologated French Schools Abroad 2026-2027", "foreign_government"),
    "kmk_german_schools_2026_04": ("KMK German Schools Abroad - Egypt", "foreign_government"),
    "scu_foreign_university_branches": ("Supreme Council of Universities - International University Branches", "egyptian_regulator"),
    "msche_auc": ("MSCHE - The American University in Cairo", "recognized_accreditor"),
}


def sha256_json(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_name(value: object) -> str | None:
    text = " ".join(str(value or "").strip().split()).casefold()
    if not text:
        return None
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي")
    text = re.sub(r"[^\w\u0600-\u06ff]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split()) or None


def normalized_domain(value: object) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    if "://" not in text:
        text = "https://" + text
    try:
        host = (urlparse(text).hostname or "").casefold()
    except ValueError:
        return None
    return host.removeprefix("www.") or None


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def build(input_jsonl: Path, media_seed: Path, output_dir: Path) -> dict:
    source_rows = [json.loads(line) for line in input_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    media = json.loads(media_seed.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    built_at = datetime.now(timezone.utc).isoformat()

    used_source_ids = sorted({row["source_id"] for row in source_rows})
    sources = []
    for source_id in used_source_ids:
        rows = [row for row in source_rows if row["source_id"] == source_id]
        name, authority = SOURCE_META[source_id]
        sources.append({
            "source_id": source_id,
            "name": name,
            "url": rows[0]["source_url"],
            "source_type": "authoritative_snapshot",
            "authority": authority,
            "notes": "EDU-DATA-2 dated evidence snapshot; import is source-shaped and non-canonical.",
        })

    raw_records = []
    candidates = []
    for row in source_rows:
        raw_hash = sha256_json({"source_record_id": row["source_record_id"], "row": row})
        entity_type = row.get("institution_type")
        name_en = row.get("name_en") or row.get("parent_university_en")
        name_ar = row.get("name_ar")
        raw_records.append({
            "source_id": row["source_id"],
            "source_record_id": row["source_record_id"],
            "entity_family": row["entity_family"],
            "entity_type_raw": entity_type,
            "name_raw": name_en or name_ar,
            "name_ar_raw": name_ar,
            "name_en_raw": name_en,
            "location_raw": row.get("city") or row.get("address"),
            "latitude": row.get("latitude"),
            "longitude": row.get("longitude"),
            "source_url": row["source_url"],
            "retrieved_at": row.get("source_snapshot_date") or built_at,
            "raw_hash": raw_hash,
            "payload_json": row,
        })
        candidates.append({
            "source_id": row["source_id"],
            "source_record_id": row["source_record_id"],
            "raw_hash": raw_hash,
            "entity_family": row["entity_family"],
            "entity_type_raw": entity_type,
            "normalized_type": entity_type,
            "name_ar": name_ar,
            "name_en": name_en,
            "normalized_name_ar": normalize_name(name_ar),
            "normalized_name_en": normalize_name(name_en),
            "normalized_location": normalize_name(row.get("city") or row.get("address")),
            "city": row.get("city"),
            "official_identifier": row.get("official_identifier"),
            "normalized_domain": normalized_domain(row.get("website")),
            "match_features": {
                "scope_state": row.get("scope_state"),
                "scope_class": row.get("scope_class"),
                "strong_evidence": row.get("strong_evidence"),
                "curriculum_codes": row.get("curriculum_codes") or [],
            },
            "candidate_status": "needs_review" if row.get("scope_state") == "candidate" else "ready",
        })

    media_assets = []
    for index, asset in enumerate(media.get("assets") or [], start=1):
        media_assets.append({
            "media_external_id": f"wikimedia-reviewed-{index:03d}",
            "source_id": "wikimedia_commons",
            "institution_name": asset["institution_name"],
            "campus_label": asset.get("campus_label"),
            "source_page_url": asset["description_page_url"],
            "original_url": None,
            "role_raw": "campus",
            "rights_status": "reviewed_reusable" if asset.get("public_use_allowed") else "review_required",
            "public_use_allowed": bool(asset.get("public_use_allowed")),
            "license_name": asset.get("license_name"),
            "license_url": asset.get("license_url"),
            "creator_name": asset.get("creator"),
            "attribution_text": asset.get("attribution_text") or (
                f"{asset.get('creator')} — {asset.get('license_name')}" if asset.get("creator") else asset.get("license_name")
            ),
            "rights_evidence_url": asset["description_page_url"],
            "rights_basis": asset.get("rights_basis"),
            "identity_match_state": asset.get("identity_match_state"),
            "requires_attribution": asset.get("requires_attribution"),
            "share_alike": asset.get("share_alike"),
            "camera_latitude": asset.get("camera_latitude"),
            "camera_longitude": asset.get("camera_longitude"),
            "commons_title": asset.get("commons_title"),
        })

    write_jsonl(output_dir / "sources.jsonl", sources)
    write_jsonl(output_dir / "raw-records.jsonl", raw_records)
    write_jsonl(output_dir / "staging-candidates.jsonl", candidates)
    write_jsonl(output_dir / "reviewed-media.jsonl", media_assets)

    manifest = {
        "schema_version": 1,
        "built_at": built_at,
        "purpose": "EDU-DATA-2 provenance-safe import preparation",
        "sources": len(sources),
        "raw_records": len(raw_records),
        "staging_candidates": len(candidates),
        "reviewed_media_assets": len(media_assets),
        "canonical_institutions_created": 0,
        "identity_merges_performed": 0,
        "public_projection_rows_created": 0,
        "checksums": {},
    }
    for filename in ("sources.jsonl", "raw-records.jsonl", "staging-candidates.jsonl", "reviewed-media.jsonl"):
        path = output_dir / filename
        manifest["checksums"][filename] = hashlib.sha256(path.read_bytes()).hexdigest()
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("artifacts/international/authoritative-source-candidates.jsonl"))
    ap.add_argument("--media-seed", type=Path, default=SEED_DIR / "wikimedia-media-verified-2026-09-14.json")
    ap.add_argument("--output-dir", type=Path, default=Path("artifacts/international/import-package"))
    args = ap.parse_args()
    build(args.input, args.media_seed, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
