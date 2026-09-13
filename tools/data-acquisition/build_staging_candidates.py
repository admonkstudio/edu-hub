#!/usr/bin/env python3
"""Build deterministic private staging candidates from edu_raw.

This script intentionally cannot write canonical/public institution tables.
It snapshots canonical row counts before and after the staging transaction and
fails if those counts change.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

NORMALIZATION_VERSION = 1
EGYPT_BOUNDS = (22.0, 31.8, 24.5, 37.2)
AGGREGATE_MARKERS = {
    "aggregate", "aggregates", "statistics", "statistic", "summary", "coverage",
    "census_total", "official_total", "report_total", "governorate_total",
}
TYPE_RULES = (
    ("nursery", ("nursery", "kindergarten", "kg", "حضان", "روضة")),
    ("university", ("university", "جامعة")),
    ("college", ("college", "faculty", "كلية")),
    ("institute", ("institute", "academy", "معهد", "اكاديمية", "أكاديمية")),
    ("school", ("school", "مدرس", "azhar", "أزهر", "ازهر")),
)
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_RE = re.compile(r"[+\d][\d\s()./-]{6,}")
URL_RE = re.compile(r"^https?://", re.I)


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = unicodedata.normalize("NFKC", str(value)).strip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def normalize_name(value: str | None) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    text = text.lower().replace("ـ", "")
    text = re.sub(r"[\u064b-\u065f\u0670]", "", text)
    text = text.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي"}))
    text = re.sub(r"[^\w\u0600-\u06ff]+", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip() or None


def iter_scalars(value: Any, path: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, item in value.items():
            key_path = f"{path}.{key}" if path else str(key)
            yield from iter_scalars(item, key_path)
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            yield from iter_scalars(item, f"{path}[{idx}]")
    elif value is not None:
        yield path.lower(), value


def extract_alias(payload: dict[str, Any], aliases: tuple[str, ...]) -> str | None:
    aliases = tuple(a.lower() for a in aliases)
    for path, value in iter_scalars(payload):
        leaf = re.sub(r"\[\d+\]$", "", path.rsplit(".", 1)[-1])
        if leaf in aliases:
            text = clean_text(value)
            if text:
                return text
    return None


def host(url: str | None) -> str | None:
    if not url or not URL_RE.match(url):
        return None
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    return hostname[4:] if hostname.startswith("www.") else hostname or None


def extract_website(payload: dict[str, Any], source_url: str | None) -> tuple[str | None, str | None]:
    website = extract_alias(payload, ("official_website", "officialwebsite", "website_url", "website", "site_url"))
    if not website:
        return None, None
    if not URL_RE.match(website):
        website = "https://" + website.lstrip("/")
    website_host, source_host = host(website), host(source_url)
    if not website_host:
        return None, "invalid_website"
    if source_host and website_host == source_host:
        return None, "directory_url_not_official_website"
    return website, None


def normalize_phone(payload: dict[str, Any]) -> str | None:
    raw = extract_alias(payload, ("phone", "phone_number", "telephone", "tel", "mobile", "contact_phone"))
    if not raw:
        return None
    match = PHONE_RE.search(raw)
    return clean_text(match.group(0)) if match else None


def normalize_email(payload: dict[str, Any]) -> str | None:
    raw = extract_alias(payload, ("email", "email_address", "contact_email", "mail"))
    if not raw:
        return None
    raw = raw.strip().lower()
    return raw if EMAIL_RE.match(raw) else None


def classify_type(entity_family: str, entity_type_raw: str | None, name: str | None) -> str | None:
    haystack = normalize_name(" ".join(x for x in (entity_family, entity_type_raw or "", name or "") if x)) or ""
    for normalized, markers in TYPE_RULES:
        if any((normalize_name(marker) or "") in haystack for marker in markers):
            return normalized
    if entity_family.lower() in {"education", "institution", "educational_institution"}:
        return "other_education"
    return None


def is_aggregate(entity_family: str, entity_type_raw: str | None, payload: dict[str, Any]) -> bool:
    markers = {entity_family.lower(), (entity_type_raw or "").lower()}
    if any(marker in AGGREGATE_MARKERS for marker in markers):
        return True
    kind = extract_alias(payload, ("record_type", "kind", "row_type", "data_type"))
    return bool(kind and kind.lower() in AGGREGATE_MARKERS)


def normalize_coordinates(latitude: Any, longitude: Any) -> tuple[float | None, float | None, list[str]]:
    reasons: list[str] = []
    if latitude is None and longitude is None:
        return None, None, reasons
    try:
        lat = float(latitude) if latitude is not None else None
        lon = float(longitude) if longitude is not None else None
    except (TypeError, ValueError):
        return None, None, ["invalid_coordinates"]
    if lat is None or lon is None:
        return None, None, ["partial_coordinates"]
    south, north, west, east = EGYPT_BOUNDS
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None, None, ["invalid_coordinates"]
    if not (south <= lat <= north and west <= lon <= east):
        reasons.append("coordinates_outside_egypt")
    return lat, lon, reasons


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    payload = row.get("payload_json") or {}
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"_unparsed_payload": payload}
    if not isinstance(payload, dict):
        payload = {"_payload": payload}

    name_ar = clean_text(row.get("name_ar_raw"))
    name_en = clean_text(row.get("name_en_raw"))
    name_primary = clean_text(row.get("name_raw")) or name_ar or name_en
    entity_family = clean_text(row.get("entity_family")) or "unknown"
    entity_type_raw = clean_text(row.get("entity_type_raw"))
    reasons: list[str] = []

    lat, lon, coord_reasons = normalize_coordinates(row.get("latitude"), row.get("longitude"))
    reasons.extend(coord_reasons)

    website_url, website_reason = extract_website(payload, clean_text(row.get("source_url")))
    if website_reason:
        reasons.append(website_reason)

    normalized_type = classify_type(entity_family, entity_type_raw, name_primary)
    if not normalized_type:
        reasons.append("unclassified_entity_type")

    if not name_primary:
        status = "invalid"
        reasons.append("missing_name")
    elif is_aggregate(entity_family, entity_type_raw, payload):
        status = "suppressed"
        reasons.append("aggregate_not_institution")
    elif any(reason in {"invalid_coordinates", "partial_coordinates", "coordinates_outside_egypt", "unclassified_entity_type"} for reason in reasons):
        status = "needs_review"
    else:
        status = "ready"

    return {
        "raw_id": row["raw_id"],
        "source_id": row["source_id"],
        "source_record_id": clean_text(row.get("source_record_id")),
        "entity_family": entity_family,
        "entity_type_raw": entity_type_raw,
        "entity_type_normalized": normalized_type,
        "name_primary": name_primary,
        "name_ar": name_ar,
        "name_en": name_en,
        "normalized_name": normalize_name(name_primary),
        "location_raw": clean_text(row.get("location_raw")),
        "governorate_guess": extract_alias(payload, ("governorate", "governorate_name", "province")),
        "latitude": lat,
        "longitude": lon,
        "source_url": clean_text(row.get("source_url")),
        "website_url": website_url,
        "phone": normalize_phone(payload),
        "email": normalize_email(payload),
        "candidate_status": status,
        "review_reasons": sorted(set(reasons)),
        "normalized_payload": {
            "source_payload": payload,
            "source_raw_hash": row.get("raw_hash"),
            "retrieved_at": str(row.get("retrieved_at")) if row.get("retrieved_at") else None,
        },
    }


def canonical_counts(conn) -> dict[str, int]:
    targets = ("edu_core.institutions", "public.institutions")
    counts: dict[str, int] = {}
    with conn.cursor() as cur:
        for target in targets:
            cur.execute("select to_regclass(%s)", (target,))
            if cur.fetchone()[0] is None:
                continue
            cur.execute(f"select count(*) from {target}")
            counts[target] = cur.fetchone()[0]
    return counts


def candidate_fields(candidate: dict[str, Any]) -> Iterable[tuple[str, str | None, Any, str, float]]:
    fields = (
        ("name.primary", candidate["name_primary"], None, "normalized", 1.0),
        ("name.ar", candidate["name_ar"], None, "source_observed", 1.0),
        ("name.en", candidate["name_en"], None, "source_observed", 1.0),
        ("entity.type", candidate["entity_type_normalized"], None, "normalized", 0.8),
        ("location.raw", candidate["location_raw"], None, "source_observed", 1.0),
        ("location.governorate", candidate["governorate_guess"], None, "source_observed", 0.9),
        ("contact.website", candidate["website_url"], None, "source_observed", 1.0),
        ("contact.phone", candidate["phone"], None, "source_observed", 1.0),
        ("contact.email", candidate["email"], None, "source_observed", 1.0),
    )
    for field_path, value_text, value_json, status, confidence in fields:
        if value_text is not None or value_json is not None:
            yield field_path, value_text, value_json, status, confidence
    if candidate["latitude"] is not None and candidate["longitude"] is not None:
        yield "location.coordinates", None, {"lat": candidate["latitude"], "lon": candidate["longitude"]}, "normalized", 1.0


def build(database_url: str, report_path: Path | None = None, batch_size: int = 500) -> dict[str, Any]:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise SystemExit("Install psycopg[binary]==3.2.10 before a live staging build") from exc

    conn = psycopg.connect(database_url, autocommit=False)
    run_id = uuid.uuid4()
    started = datetime.now(timezone.utc)
    source_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    try:
        before = canonical_counts(conn)
        with conn.cursor() as cur:
            cur.execute("select count(*) from edu_raw.raw_records")
            raw_count = cur.fetchone()[0]
            cur.execute(
                """select batch_id from edu_raw.import_batches
                   where status='verified' order by finished_at desc nulls last, started_at desc limit 1"""
            )
            row = cur.fetchone()
            archive_batch_id = row[0] if row else None
            cur.execute(
                """insert into edu_staging.normalization_runs
                   (run_id,normalization_version,archive_batch_id,status,source_row_count)
                   values (%s,%s,%s,'started',%s)""",
                (run_id, NORMALIZATION_VERSION, archive_batch_id, raw_count),
            )
        conn.commit()

        with conn.cursor(row_factory=dict_row) as read_cur:
            read_cur.execute(
                """select raw_id,source_id,source_record_id,entity_family,entity_type_raw,
                          name_raw,name_ar_raw,name_en_raw,location_raw,latitude,longitude,
                          source_url,retrieved_at,raw_hash,payload_json
                   from edu_raw.raw_records order by raw_id"""
            )
            while True:
                rows = read_cur.fetchmany(batch_size)
                if not rows:
                    break
                with conn.cursor() as write_cur:
                    for row in rows:
                        candidate = normalize_row(dict(row))
                        source_counts[candidate["source_id"]] += 1
                        status_counts[candidate["candidate_status"]] += 1
                        reasons.update(candidate["review_reasons"])
                        write_cur.execute(
                            """insert into edu_staging.entity_candidates
                               (raw_id,run_id,source_id,source_record_id,entity_family,entity_type_raw,
                                entity_type_normalized,name_primary,name_ar,name_en,normalized_name,
                                location_raw,governorate_guess,latitude,longitude,source_url,website_url,
                                phone,email,candidate_status,review_reasons,normalized_payload,normalization_version)
                               values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)
                               on conflict (raw_id) do update set
                                 run_id=excluded.run_id,source_id=excluded.source_id,
                                 source_record_id=excluded.source_record_id,entity_family=excluded.entity_family,
                                 entity_type_raw=excluded.entity_type_raw,entity_type_normalized=excluded.entity_type_normalized,
                                 name_primary=excluded.name_primary,name_ar=excluded.name_ar,name_en=excluded.name_en,
                                 normalized_name=excluded.normalized_name,location_raw=excluded.location_raw,
                                 governorate_guess=excluded.governorate_guess,latitude=excluded.latitude,
                                 longitude=excluded.longitude,source_url=excluded.source_url,website_url=excluded.website_url,
                                 phone=excluded.phone,email=excluded.email,candidate_status=excluded.candidate_status,
                                 review_reasons=excluded.review_reasons,normalized_payload=excluded.normalized_payload,
                                 normalization_version=excluded.normalization_version,normalized_at=now()
                               returning candidate_id""",
                            (
                                candidate["raw_id"], run_id, candidate["source_id"], candidate["source_record_id"],
                                candidate["entity_family"], candidate["entity_type_raw"], candidate["entity_type_normalized"],
                                candidate["name_primary"], candidate["name_ar"], candidate["name_en"], candidate["normalized_name"],
                                candidate["location_raw"], candidate["governorate_guess"], candidate["latitude"], candidate["longitude"],
                                candidate["source_url"], candidate["website_url"], candidate["phone"], candidate["email"],
                                candidate["candidate_status"], candidate["review_reasons"],
                                json.dumps(candidate["normalized_payload"], ensure_ascii=False), NORMALIZATION_VERSION,
                            ),
                        )
                        candidate_id = write_cur.fetchone()[0]
                        for field_path, value_text, value_json, verification_status, confidence in candidate_fields(candidate):
                            write_cur.execute(
                                """insert into edu_staging.field_candidates
                                   (candidate_id,field_path,value_text,value_jsonb,source_url,confidence,verification_status)
                                   values (%s,%s,%s,%s::jsonb,%s,%s,%s)
                                   on conflict (candidate_id,field_path) do update set
                                     value_text=excluded.value_text,value_jsonb=excluded.value_jsonb,
                                     source_url=excluded.source_url,confidence=excluded.confidence,
                                     verification_status=excluded.verification_status""",
                                (
                                    candidate_id, field_path, value_text,
                                    json.dumps(value_json, ensure_ascii=False) if value_json is not None else None,
                                    candidate["source_url"], confidence, verification_status,
                                ),
                            )
                conn.commit()

        after = canonical_counts(conn)
        if before != after:
            raise RuntimeError(f"canonical row counts changed during staging build: before={before}, after={after}")

        report = {
            "ok": True,
            "run_id": str(run_id),
            "normalization_version": NORMALIZATION_VERSION,
            "started_at": started.isoformat(),
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "raw_records": sum(source_counts.values()),
            "status_counts": dict(status_counts),
            "source_counts": dict(sorted(source_counts.items())),
            "review_reason_counts": dict(reasons.most_common()),
            "canonical_guard_before": before,
            "canonical_guard_after": after,
        }
        with conn.cursor() as cur:
            cur.execute(
                """update edu_staging.normalization_runs set status='verified',
                     ready_count=%s,review_count=%s,suppressed_count=%s,invalid_count=%s,
                     finished_at=now(),report_json=%s::jsonb where run_id=%s""",
                (
                    status_counts["ready"], status_counts["needs_review"],
                    status_counts["suppressed"], status_counts["invalid"],
                    json.dumps(report, ensure_ascii=False), run_id,
                ),
            )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """update edu_staging.normalization_runs
                       set status='failed',finished_at=now(),error=%s where run_id=%s""",
                    (repr(exc), run_id),
                )
            conn.commit()
        except Exception:
            conn.rollback()
        raise
    finally:
        conn.close()

    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--batch-size", type=int, default=500)
    args = parser.parse_args()
    if args.batch_size < 1:
        raise SystemExit("--batch-size must be positive")
    report = build(args.database_url, args.report, args.batch_size)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
