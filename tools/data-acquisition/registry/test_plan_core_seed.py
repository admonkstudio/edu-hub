#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("plan_core_seed.py")
spec = importlib.util.spec_from_file_location("plan_core_seed", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def candidate(*, raw_id: int, source_record_id: str, registry_source_id: str,
              name_ar: str | None = None, normalized_name_ar: str | None = None,
              official_identifier: str | None = None, normalized_type: str = "university",
              status: str = "ready", coverage: str = "current",
              authority: str = "primary_official_registry") -> dict:
    return {
        "raw_id": raw_id,
        "source_record_id": source_record_id,
        "entity_family": "pre_university" if registry_source_id == "azhar_institute_guide" else "higher_education",
        "entity_type_raw": normalized_type,
        "normalized_type": normalized_type,
        "name_ar": name_ar,
        "name_en": None,
        "normalized_name_ar": normalized_name_ar,
        "normalized_name_en": None,
        "official_identifier": official_identifier,
        "candidate_status": status,
        "match_features": {
            "registry_source_id": registry_source_id,
            "authority_class": authority,
            "coverage_credit": coverage,
        },
    }


class CoreSeedPlannerTests(unittest.TestCase):
    def test_azhar_same_name_different_official_ids_stay_separate(self):
        rows = [
            candidate(raw_id=1, source_record_id="1001", registry_source_id="azhar_institute_guide",
                      name_ar="معهد النور", normalized_name_ar="معهد النور", official_identifier="1001",
                      normalized_type="azhar_institute"),
            candidate(raw_id=2, source_record_id="1002", registry_source_id="azhar_institute_guide",
                      name_ar="معهد النور", normalized_name_ar="معهد النور", official_identifier="1002",
                      normalized_type="azhar_institute"),
        ]
        proposals, reviews, report = mod.build_plan(rows)
        self.assertEqual(len(proposals), 2)
        self.assertEqual(reviews, [])
        self.assertEqual(report["identity_proposals_by_source"]["azhar_institute_guide"], 2)
        self.assertEqual(report["automatic_identity_acceptances"], 0)
        self.assertFalse(report["core_mutation_performed"])

    def test_scu_duplicate_normalized_identity_is_grouped_for_review_only(self):
        rows = [
            candidate(raw_id=33, source_record_id="SCU-LIVE-0033", registry_source_id="scu_institutions",
                      name_ar="جامعة الأسكندرية الأهلية", normalized_name_ar="جامعة الاسكندرية الاهلية"),
            candidate(raw_id=52, source_record_id="SCU-LIVE-0052", registry_source_id="scu_institutions",
                      name_ar="جامعة الإسكندرية الأهلية", normalized_name_ar="جامعة الاسكندرية الاهلية"),
        ]
        proposals, reviews, report = mod.build_plan(rows)
        self.assertEqual(len(proposals), 1)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(proposals[0]["decision"], "needs_review")
        self.assertFalse(proposals[0]["automatic_acceptance"])
        self.assertFalse(proposals[0]["core_mutation_allowed"])
        self.assertEqual(report["duplicate_rows_collapsed_by_source"]["scu_institutions"], 1)
        self.assertEqual(report["edu_core_rows_created"], 0)

    def test_non_current_secondary_and_unsupported_sources_are_excluded(self):
        rows = [
            candidate(raw_id=1, source_record_id="x", registry_source_id="scu_institutions",
                      name_ar="جامعة", normalized_name_ar="جامعة", coverage="historical"),
            candidate(raw_id=2, source_record_id="y", registry_source_id="scu_institutions",
                      name_ar="جامعة", normalized_name_ar="جامعة", authority="secondary_directory"),
            candidate(raw_id=3, source_record_id="z", registry_source_id="mohesr_private_higher_institutes",
                      name_ar="معهد", normalized_name_ar="معهد", normalized_type="higher_institute"),
        ]
        proposals, reviews, report = mod.build_plan(rows)
        self.assertEqual(proposals, [])
        self.assertEqual(reviews, [])
        self.assertEqual(report["ignored_rows"], 3)
        self.assertEqual(report["automatic_identity_acceptances"], 0)
        self.assertFalse(report["public_promotion_performed"])

    def test_missing_source_specific_identity_key_is_not_proposed(self):
        rows = [
            candidate(raw_id=1, source_record_id="", registry_source_id="azhar_institute_guide",
                      name_ar="معهد", normalized_name_ar="معهد", official_identifier=None,
                      normalized_type="azhar_institute")
        ]
        proposals, reviews, report = mod.build_plan(rows)
        self.assertEqual(proposals, [])
        self.assertEqual(reviews, [])
        self.assertEqual(report["missing_identity_key_rows"], 1)
        self.assertEqual(report["missing_identity_key_reasons"]["azhar_missing_official_identifier"], 1)


if __name__ == "__main__":
    unittest.main()
