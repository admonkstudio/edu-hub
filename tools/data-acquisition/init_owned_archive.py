#!/usr/bin/env python3
"""Initialize the source-neutral owned SQLite acquisition archive.

This creates only the raw/source/media holding layer. It intentionally does not
create the final canonical/public institution schema.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def setup(db: sqlite3.Connection) -> None:
    db.executescript(
        """
        PRAGMA journal_mode=WAL;
        PRAGMA foreign_keys=ON;

        CREATE TABLE IF NOT EXISTS sources (
          source_id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          url TEXT NOT NULL,
          source_type TEXT NOT NULL,
          authority TEXT NOT NULL,
          notes TEXT
        );

        CREATE TABLE IF NOT EXISTS acquisition_runs (
          run_id INTEGER PRIMARY KEY AUTOINCREMENT,
          source_id TEXT NOT NULL REFERENCES sources(source_id),
          started_at TEXT NOT NULL,
          finished_at TEXT,
          status TEXT NOT NULL,
          records_added INTEGER NOT NULL DEFAULT 0,
          error TEXT
        );

        CREATE TABLE IF NOT EXISTS raw_records (
          raw_id INTEGER PRIMARY KEY AUTOINCREMENT,
          source_id TEXT NOT NULL REFERENCES sources(source_id),
          source_record_id TEXT,
          entity_family TEXT NOT NULL,
          entity_type_raw TEXT,
          name_raw TEXT,
          name_ar_raw TEXT,
          name_en_raw TEXT,
          location_raw TEXT,
          latitude REAL,
          longitude REAL,
          source_url TEXT,
          retrieved_at TEXT NOT NULL,
          raw_hash TEXT NOT NULL,
          payload_json TEXT NOT NULL,
          UNIQUE(source_id, raw_hash)
        );
        CREATE INDEX IF NOT EXISTS idx_raw_source ON raw_records(source_id);
        CREATE INDEX IF NOT EXISTS idx_raw_name ON raw_records(name_raw);
        CREATE INDEX IF NOT EXISTS idx_raw_family ON raw_records(entity_family);
        CREATE INDEX IF NOT EXISTS idx_raw_source_record ON raw_records(source_id, source_record_id);
        CREATE INDEX IF NOT EXISTS idx_raw_geo ON raw_records(latitude, longitude);

        CREATE TABLE IF NOT EXISTS field_inventory (
          source_id TEXT NOT NULL,
          field_path TEXT NOT NULL,
          populated_records INTEGER NOT NULL,
          distinct_sample_count INTEGER NOT NULL,
          example_values_json TEXT NOT NULL,
          PRIMARY KEY(source_id, field_path)
        );

        CREATE TABLE IF NOT EXISTS coverage_targets (
          target_id TEXT PRIMARY KEY,
          label TEXT NOT NULL,
          official_count INTEGER,
          target_basis TEXT NOT NULL,
          reference_url TEXT NOT NULL
        );
        """
    )
    db.commit()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    args = ap.parse_args()

    path = Path(args.db)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    setup(db)
    db.close()
    print(path)


if __name__ == "__main__":
    main()
