#!/usr/bin/env python3
"""Build the deterministic CIS/Cognia EDU-DATA-2 source expansion.

The expansion adds current accreditor evidence to the D2.1 research universe
without creating canonical identities or granting scope eligibility by itself.
CIS establishes strong international-school-model/accreditation evidence; the
private/independent ownership gate remains separate. Cognia accreditation is
stored as accreditation/candidate-discovery evidence and still requires an
independent international-school-model check.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED_DIR = HERE / "seeds"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_id(source_id: str, name: str) -> str:
    digest = hashlib.sha256(f"{source_id}\0{name.casefold()}".encode("utf-8")).hexdigest()[:20]
    return f"{source_id}:{digest}"


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def cis_rows(data: dict) -> list[dict]:
    source_id = data["source_id"]
    rows = []
    for source in data["records"]:
        name = " ".join(source["name"].split())
        rows.append(
            {
                "source_id": source_id,
                "source_record_id": stable_id(source_id, name),
                "source_snapshot_date": data["snapshot_date"],
                "source_url": source["source_url"],
                "entity_family": "pre_university",
                "institution_type": "international_school",
                "name_en": name,
                "scope_state": source["scope_state"],
                "scope_class": source["scope_class"],
                "strong_evidence": "cis_international_accreditation",
                "accreditation_body_code": "cis",
                "accreditation_event": source["accreditation_event"],
                "accreditation_event_date": source["accreditation_event_date"],
                "eligibility_pending": source["eligibility_pending"],
                "auto_eligibility": False,
                "canonical_identity_created": False,
                "automatic_merge_performed": False,
                "public_promotion_performed": False,
            }
        )
    return rows


def cognia_rows(data: dict) -> list[dict]:
    source_id = data["source_id"]
    rows = []
    for source in data["records"]:
        name = " ".join(source["name"].split())
        rows.append(
            {
                "source_id": source_id,
                "source_record_id": stable_id(source_id, name),
                "source_snapshot_date": data["snapshot_date"],
                "source_url": data["source_url"],
                "entity_family": "pre_university",
                "institution_type": "international_school_candidate",
                "name_en": name,
                "scope_state": source["scope_state"],
                "scope_class": source["scope_class"],
                "strong_evidence": "cognia_accreditation_milestone",
                "accreditation_body_code": "cognia",
                "accreditation_milestone_years": source["accreditation_milestone_years"],
                "accreditation_milestone_school_year": data["milestone_school_year"],
                "eligibility_pending": source["eligibility_pending"],
                "auto_eligibility": False,
                "canonical_identity_created": False,
                "automatic_merge_performed": False,
                "public_promotion_performed": False,
            }
        )
    return rows


def build(seed_dir: Path, output_dir: Path, base: Path | None) -> dict:
    cis = load_json(seed_dir / "cis-egypt-accreditation-evidence-2026-09-15.json")
    cognia = load_json(seed_dir / "cognia-egypt-milestones-2026-2027.json")

    assert cis["records_count"] == len(cis["records"]) == 6
    assert cognia["records_count"] == len(cognia["records"]) == 4
    assert all(row["scope_state"] == "candidate" for row in cis["records"])
    assert all(row["scope_state"] == "candidate" for row in cognia["records"])

    expansion = cis_rows(cis) + cognia_rows(cognia)
    output_dir.mkdir(parents=True, exist_ok=True)
    expansion_path = output_dir / "accreditor-source-candidates.jsonl"
    write_jsonl(expansion_path, expansion)

    base_rows: list[dict] = []
    combined_path = None
    if base and base.exists():
        base_rows = [
            json.loads(line)
            for line in base.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        combined_path = output_dir / "authoritative-source-candidates-with-accreditors.jsonl"
        write_jsonl(combined_path, base_rows + expansion)

    source_counts: dict[str, int] = {}
    for row in expansion:
        source_counts[row["source_id"]] = source_counts.get(row["source_id"], 0) + 1

    summary = {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "work_package": "D2.1_accreditor_expansion",
        "source_rows": len(expansion),
        "source_counts": source_counts,
        "candidate_rows": sum(1 for row in expansion if row["scope_state"] == "candidate"),
        "base_source_rows": len(base_rows) if base_rows else None,
        "combined_source_rows": len(base_rows) + len(expansion) if base_rows else None,
        "unique_institutions_claimed": None,
        "international_eligibility_granted_by_expansion": 0,
        "canonical_institutions_created": 0,
        "automatic_merges_performed": 0,
        "public_projection_rows_created": 0,
        "database_mutation_performed": False,
        "outputs": {
            "expansion": expansion_path.name,
            "combined": combined_path.name if combined_path else None,
        },
    }
    (output_dir / "accreditor-expansion-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-dir", type=Path, default=SEED_DIR)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/international/accreditor-expansion"),
    )
    parser.add_argument(
        "--base",
        type=Path,
        default=Path("artifacts/international/authoritative-source-candidates.jsonl"),
    )
    args = parser.parse_args()
    build(args.seed_dir, args.output_dir, args.base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
