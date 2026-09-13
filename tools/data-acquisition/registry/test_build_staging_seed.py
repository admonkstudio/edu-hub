#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("build_staging_seed.py")
spec = importlib.util.spec_from_file_location("build_staging_seed", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


class RegistrySeedTests(unittest.TestCase):
    def test_secondary_and_historical_never_count_as_current(self):
        registry = {
            "sources": [
                {"source_id": "moe", "name": "MOE", "authority_class": "primary_official_registry", "entity_family": "pre_university", "coverage_target": {"count": 100}, "row_level_status": "pending"},
                {"source_id": "azhar", "name": "Azhar", "authority_class": "primary_official_registry", "entity_family": "pre_university", "coverage_target": {"count": 5}, "row_level_status": "acquired"},
            ]
        }
        aliases = {
            "old_emis": {"registry_source_id": "moe", "coverage_credit": "historical"},
            "azhar_raw": {"registry_source_id": "azhar", "coverage_credit": "current"},
            "secondary": {"registry_source_id": None, "coverage_credit": "none"},
        }
        raw = mod.Counter({"old_emis": 10, "azhar_raw": 5, "secondary": 50})
        report = mod.build_report(registry, aliases, raw, raw, "abc")
        by_id = {row["source_id"]: row for row in report["sources"]}
        self.assertEqual(by_id["moe"]["current_coverage_rows"], 0)
        self.assertEqual(by_id["moe"]["historical_evidence_rows"], 10)
        self.assertEqual(by_id["azhar"]["current_coverage_rows"], 5)
        self.assertEqual(report["current_official_seed_rows"], 5)
        self.assertEqual(report["canonical_entities_created"], 0)
        self.assertFalse(report["core_promotion_performed"])

    def test_arabic_normalization_is_deterministic(self):
        self.assertEqual(mod.normalize_arabic("  مَدْرَسَة   الأمل  "), "مدرسة الامل")
        self.assertEqual(mod.normalize_latin("  Cairo   University "), "cairo university")


if __name__ == "__main__":
    unittest.main()
