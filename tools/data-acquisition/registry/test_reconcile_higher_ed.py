#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("reconcile_higher_ed.py")
spec = importlib.util.spec_from_file_location("reconcile_higher_ed", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


class HigherEdReconciliationTests(unittest.TestCase):
    def test_mohesr_sector_duplicates_group_before_matching(self):
        scu = [{"seed_id": "SCU-1", "name_ar": "المعهد العالي للهندسة والتكنولوجيا", "higher_ed_category": "accredited_private_institute"}]
        mohesr = [
            {"source_record_id": "M-1", "name_raw": "المعهد العالي للهندسة والتكنولوجيا", "normalized_name_ar": "المعهد العالي للهندسة والتكنولوجيا", "payload": {"category_raw": "engineering"}},
            {"source_record_id": "M-2", "name_raw": "المعهد العالي للهندسة والتكنولوجيا", "normalized_name_ar": "المعهد العالي للهندسة والتكنولوجيا", "payload": {"category_raw": "computer_science"}},
        ]
        exact, review, report = mod.reconcile(scu, mohesr)
        self.assertEqual(len(exact), 1)
        self.assertEqual(review, [])
        self.assertEqual(report["mohesr_sector_occurrences"], 2)
        self.assertEqual(report["mohesr_distinct_normalized_names"], 1)
        self.assertEqual(report["mohesr_duplicate_sector_occurrences"], 1)
        self.assertEqual(report["mohesr_unresolved_after_exact"], 0)
        self.assertEqual(report["automatic_identity_acceptances"], 0)
        self.assertFalse(exact[0]["automatic_acceptance"])

    def test_fuzzy_candidate_never_auto_accepts_or_reduces_unresolved_count(self):
        scu = [{"seed_id": "SCU-1", "name_ar": "المعهد العالي للحاسبات ونظم المعلومات", "higher_ed_category": "accredited_private_institute"}]
        mohesr = [{"source_record_id": "M-1", "name_raw": "معهد عالي للحاسبات و نظم المعلومات", "payload": {"category_raw": "computer_science"}}]
        exact, review, report = mod.reconcile(scu, mohesr, fuzzy_threshold=0.5)
        self.assertEqual(exact, [])
        self.assertEqual(len(review), 1)
        self.assertFalse(review[0]["automatic_acceptance"])
        self.assertEqual(report["mohesr_unresolved_after_exact"], 1)
        self.assertEqual(report["unmatched_mohesr_distinct_names"], 1)
        self.assertEqual(report["mohesr_without_fuzzy_suggestion"], 0)
        self.assertEqual(report["edu_core_rows_created"], 0)
        self.assertFalse(report["core_mutation_performed"])

    def test_scu_private_filter_contract(self):
        rows = [
            {"seed_id": "SCU-1", "name_ar": "جامعة", "higher_ed_category": "private_university"},
            {"seed_id": "SCU-2", "name_ar": "معهد", "higher_ed_category": "accredited_private_institute"},
        ]
        filtered = [row for row in rows if row.get("higher_ed_category") == "accredited_private_institute"]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["seed_id"], "SCU-2")


if __name__ == "__main__":
    unittest.main()
