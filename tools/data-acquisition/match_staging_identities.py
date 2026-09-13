#!/usr/bin/env python3
"""Generate private cross-source identity-match proposals from edu_staging.

Version 1 is intentionally conservative. It blocks on exact normalized names,
contacts/domains and very-near coordinates, scores corroborating evidence, and
never writes canonical/public institution tables. No proposal is automatically
accepted; high-confidence pairs are `proposed` and ambiguous pairs are
`needs_review` until a later explicit review/promotion step.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

MATCHING_VERSION = 1
MAX_BLOCK_SIZE = 200


def canonical_phone(value: Any) -> str | None:
    if not value:
        return None
    digits = re.sub(r"\D", "", str(value))
    if digits.startswith("0020"):
        digits = "0" + digits[4:]
    elif digits.startswith("20") and len(digits) >= 10:
        digits = "0" + digits[2:]
    return digits if len(digits) >= 8 else None


def canonical_email(value: Any) -> str | None:
    if not value or "@" not in str(value):
        return None
    return str(value).strip().lower()


def website_domain(value: Any) -> str | None:
    if not value:
        return None
    try:
        hostname = (urlparse(str(value)).hostname or "").lower()
    except ValueError:
        return None
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname or None


def normalize_location(value: Any) -> str | None:
    if not value:
        return None
    text = str(value).lower().replace("ـ", "")
    text = re.sub(r"[\u064b-\u065f\u0670]", "", text)
    text = text.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي"}))
    text = re.sub(r"[^\w\u0600-\u06ff]+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def haversine_m(a: dict[str, Any], b: dict[str, Any]) -> float | None:
    if any(a.get(k) is None for k in ("latitude", "longitude")) or any(
        b.get(k) is None for k in ("latitude", "longitude")
    ):
        return None
    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [a["latitude"], a["longitude"], b["latitude"], b["longitude"]],
    )
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6_371_000 * 2 * math.asin(math.sqrt(h))


def name_similarity(a: dict[str, Any], b: dict[str, Any]) -> float:
    left = a.get("normalized_name") or ""
    right = b.get("normalized_name") or ""
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    sequence = SequenceMatcher(None, left, right).ratio()
    left_tokens, right_tokens = set(left.split()), set(right.split())
    token_similarity = (
        len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
        if left_tokens | right_tokens
        else 0.0
    )
    return max(sequence, token_similarity)


def score_pair(a: dict[str, Any], b: dict[str, Any]) -> tuple[float, str | None, list[tuple[str, str, float]]]:
    evidence: list[tuple[str, str, float]] = []
    exact_name = bool(a.get("normalized_name") and a.get("normalized_name") == b.get("normalized_name"))
    similarity = name_similarity(a, b)

    if exact_name:
        evidence.append(("exact_name", a["normalized_name"], 0.40))
    elif similarity >= 0.85:
        evidence.append(("name_similarity", f"{similarity:.4f}", 0.30 if similarity >= 0.92 else 0.20))

    left_type = a.get("entity_type_normalized")
    right_type = b.get("entity_type_normalized")
    same_type = bool(left_type and left_type == right_type)
    if same_type:
        evidence.append(("same_type", left_type, 0.10))
    elif left_type and right_type:
        evidence.append(("type_conflict", f"{left_type}!={right_type}", -0.20))

    left_phone, right_phone = canonical_phone(a.get("phone")), canonical_phone(b.get("phone"))
    left_email, right_email = canonical_email(a.get("email")), canonical_email(b.get("email"))
    left_domain, right_domain = website_domain(a.get("website_url")), website_domain(b.get("website_url"))
    exact_phone = bool(left_phone and left_phone == right_phone)
    exact_email = bool(left_email and left_email == right_email)
    exact_domain = bool(left_domain and left_domain == right_domain)

    if exact_phone:
        evidence.append(("exact_phone", left_phone, 0.50))
    if exact_email:
        evidence.append(("exact_email", left_email, 0.55))
    if exact_domain:
        evidence.append(("exact_domain", left_domain, 0.35))

    left_gov = normalize_location(a.get("governorate_guess"))
    right_gov = normalize_location(b.get("governorate_guess"))
    if left_gov and left_gov == right_gov:
        evidence.append(("same_governorate", left_gov, 0.10))

    left_location = normalize_location(a.get("location_raw"))
    right_location = normalize_location(b.get("location_raw"))
    if left_location and left_location == right_location:
        evidence.append(("exact_location", left_location, 0.15))

    distance = haversine_m(a, b)
    if distance is not None:
        if distance <= 75:
            evidence.append(("geo_within_75m", f"{distance:.1f}", 0.35))
        elif distance <= 250:
            evidence.append(("geo_within_250m", f"{distance:.1f}", 0.20))

    score = max(0.0, min(1.0, sum(weight for _, _, weight in evidence)))
    strong_corroborator = exact_phone or exact_email or exact_domain or (distance is not None and distance <= 75)

    # Version 1 never marks a pair accepted. `proposed` means high confidence but
    # still reviewable. Canonical promotion remains a separate future command.
    if exact_name and strong_corroborator and same_type and score >= 0.85:
        status = "proposed"
    elif (exact_phone or exact_email) and similarity >= 0.92 and same_type and score >= 0.85:
        status = "proposed"
    elif score >= 0.60 and similarity >= 0.85:
        status = "needs_review"
    else:
        status = None
    return score, status, evidence


def candidate_blocks(candidates: list[dict[str, Any]]) -> list[dict[Any, list[int]]]:
    indexes: list[dict[Any, list[int]]] = [defaultdict(list) for _ in range(5)]
    for candidate in candidates:
        values: list[Any] = [
            candidate.get("normalized_name"),
            canonical_phone(candidate.get("phone")),
            canonical_email(candidate.get("email")),
            website_domain(candidate.get("website_url")),
            None,
        ]
        if candidate.get("latitude") is not None and candidate.get("longitude") is not None:
            # ~111 m latitude cells; scoring still uses exact Haversine distance.
            values[4] = (round(float(candidate["latitude"]), 3), round(float(candidate["longitude"]), 3))
        for index, value in enumerate(values):
            if value:
                indexes[index][value].append(candidate["candidate_id"])
    return indexes


def generate_candidate_pairs(
    candidates: list[dict[str, Any]], max_block_size: int = MAX_BLOCK_SIZE
) -> tuple[set[tuple[int, int]], list[dict[str, Any]]]:
    by_id = {candidate["candidate_id"]: candidate for candidate in candidates}
    pairs: set[tuple[int, int]] = set()
    skipped_blocks: list[dict[str, Any]] = []
    block_names = ("normalized_name", "phone", "email", "domain", "geo_cell")

    for block_name, index in zip(block_names, candidate_blocks(candidates)):
        for key, candidate_ids in index.items():
            if len(candidate_ids) > max_block_size:
                skipped_blocks.append({"block": block_name, "key": str(key), "size": len(candidate_ids)})
                continue
            for position, left_id in enumerate(candidate_ids):
                for right_id in candidate_ids[position + 1 :]:
                    left, right = by_id[left_id], by_id[right_id]
                    if left["source_id"] == right["source_id"]:
                        continue
                    pairs.add(tuple(sorted((left_id, right_id))))
    return pairs, skipped_blocks


def canonical_counts(conn) -> dict[str, int]:
    targets = ("edu_core.institutions", "public.institutions")
    counts: dict[str, int] = {}
    with conn.cursor() as cursor:
        for target in targets:
            cursor.execute("select to_regclass(%s)", (target,))
            if cursor.fetchone()[0] is None:
                continue
            cursor.execute(f"select count(*) from {target}")
            counts[target] = cursor.fetchone()[0]
    return counts


def match(database_url: str, report_path: Path | None = None, max_block_size: int = MAX_BLOCK_SIZE) -> dict[str, Any]:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise SystemExit("Install psycopg[binary]==3.2.10 before a live matching run") from exc

    if max_block_size < 2:
        raise SystemExit("--max-block-size must be at least 2")

    conn = psycopg.connect(database_url, autocommit=False)
    run_id = uuid.uuid4()
    started = datetime.now(timezone.utc)
    try:
        before = canonical_counts(conn)
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """select candidate_id,source_id,source_record_id,entity_type_normalized,
                          normalized_name,location_raw,governorate_guess,latitude,longitude,
                          website_url,phone,email,candidate_status
                   from edu_staging.entity_candidates
                   where candidate_status in ('ready','needs_review')
                   order by candidate_id"""
            )
            candidates = [dict(row) for row in cursor.fetchall()]
            cursor.execute(
                """select run_id from edu_staging.normalization_runs
                   where status='verified' order by finished_at desc nulls last, started_at desc limit 1"""
            )
            row = cursor.fetchone()
            normalization_run_id = row["run_id"] if row else None

        with conn.cursor() as cursor:
            cursor.execute(
                """insert into edu_staging.matching_runs
                   (run_id,matching_version,normalization_run_id,status,candidate_count)
                   values (%s,%s,%s,'started',%s)""",
                (run_id, MATCHING_VERSION, normalization_run_id, len(candidates)),
            )
        conn.commit()

        by_id = {candidate["candidate_id"]: candidate for candidate in candidates}
        candidate_pairs, skipped_blocks = generate_candidate_pairs(candidates, max_block_size)
        status_counts: Counter[str] = Counter()
        evidence_counts: Counter[str] = Counter()
        persisted_pairs = 0

        with conn.cursor() as cursor:
            for left_id, right_id in sorted(candidate_pairs):
                left, right = by_id[left_id], by_id[right_id]
                score, status, evidence = score_pair(left, right)
                if status is None:
                    continue

                cursor.execute(
                    """insert into edu_staging.identity_matches
                       (left_candidate_id,right_candidate_id,match_status,score,method,run_id,matching_version)
                       values (%s,%s,%s,%s,'deterministic_scored_v1',%s,%s)
                       on conflict (left_candidate_id,right_candidate_id) do update set
                         run_id=excluded.run_id,
                         matching_version=excluded.matching_version,
                         score=excluded.score,
                         method=excluded.method,
                         match_status=case
                           when edu_staging.identity_matches.match_status in ('accepted','rejected')
                             then edu_staging.identity_matches.match_status
                           else excluded.match_status
                         end
                       returning match_id,match_status""",
                    (left_id, right_id, status, round(score, 4), run_id, MATCHING_VERSION),
                )
                match_id, persisted_status = cursor.fetchone()
                persisted_pairs += 1
                status_counts[persisted_status] += 1

                for evidence_type, evidence_value, weight in evidence:
                    evidence_counts[evidence_type] += 1
                    cursor.execute(
                        """insert into edu_staging.identity_match_evidence
                           (match_id,evidence_type,evidence_value,weight)
                           values (%s,%s,%s,%s)
                           on conflict (match_id,evidence_type,(coalesce(evidence_value,'')))
                           do update set weight=excluded.weight""",
                        (match_id, evidence_type, evidence_value, weight),
                    )

                reason = "high_confidence_proposal" if status == "proposed" else "ambiguous_identity_proposal"
                cursor.execute(
                    """insert into edu_staging.review_tasks(match_id,task_type,reason,status)
                       values (%s,'identity_match_review',%s,'open')
                       on conflict (coalesce(candidate_id,0),coalesce(match_id,0),task_type,reason)
                       do nothing""",
                    (match_id, reason),
                )

        after = canonical_counts(conn)
        if before != after:
            raise RuntimeError(f"canonical row counts changed during identity matching: before={before}, after={after}")

        report = {
            "ok": True,
            "run_id": str(run_id),
            "matching_version": MATCHING_VERSION,
            "started_at": started.isoformat(),
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "candidate_count": len(candidates),
            "blocked_pair_count": len(candidate_pairs),
            "persisted_pair_count": persisted_pairs,
            "status_counts": dict(status_counts),
            "evidence_counts": dict(evidence_counts),
            "skipped_block_count": len(skipped_blocks),
            "skipped_blocks": skipped_blocks[:100],
            "canonical_guard_before": before,
            "canonical_guard_after": after,
        }
        with conn.cursor() as cursor:
            cursor.execute(
                """update edu_staging.matching_runs set
                     status='verified',pair_count=%s,proposed_count=%s,review_count=%s,
                     skipped_block_count=%s,finished_at=now(),report_json=%s::jsonb
                   where run_id=%s""",
                (
                    persisted_pairs,
                    status_counts["proposed"],
                    status_counts["needs_review"],
                    len(skipped_blocks),
                    json.dumps(report, ensure_ascii=False),
                    run_id,
                ),
            )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """update edu_staging.matching_runs
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
    parser.add_argument("--max-block-size", type=int, default=MAX_BLOCK_SIZE)
    args = parser.parse_args()
    report = match(args.database_url, args.report, args.max_block_size)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
