import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "build_staging_candidates.py"
spec = importlib.util.spec_from_file_location("build_staging_candidates", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


class NormalizationTests(unittest.TestCase):
    def row(self, **overrides):
        base = {
            "raw_id": 1,
            "source_id": "directory",
            "source_record_id": "abc",
            "entity_family": "school",
            "entity_type_raw": "private school",
            "name_raw": "Cairo International School",
            "name_ar_raw": None,
            "name_en_raw": "Cairo International School",
            "location_raw": "Cairo",
            "latitude": 30.04,
            "longitude": 31.23,
            "source_url": "https://directory.example/school/abc",
            "retrieved_at": "2026-09-01T00:00:00Z",
            "raw_hash": "a" * 64,
            "payload_json": {"website": "https://school.example", "phone": "+20 2 1234567", "email": "INFO@SCHOOL.EXAMPLE"},
        }
        base.update(overrides)
        return base

    def test_ready_school(self):
        candidate = mod.normalize_row(self.row())
        self.assertEqual(candidate["candidate_status"], "ready")
        self.assertEqual(candidate["entity_type_normalized"], "school")
        self.assertEqual(candidate["website_url"], "https://school.example")
        self.assertEqual(candidate["email"], "info@school.example")

    def test_aggregate_is_suppressed(self):
        candidate = mod.normalize_row(self.row(entity_family="statistics", entity_type_raw="aggregate"))
        self.assertEqual(candidate["candidate_status"], "suppressed")
        self.assertIn("aggregate_not_institution", candidate["review_reasons"])

    def test_bad_coordinates_need_review(self):
        candidate = mod.normalize_row(self.row(latitude=52.5, longitude=13.4))
        self.assertEqual(candidate["candidate_status"], "needs_review")
        self.assertIn("coordinates_outside_egypt", candidate["review_reasons"])

    def test_missing_name_is_invalid(self):
        candidate = mod.normalize_row(self.row(name_raw=None, name_en_raw=None, name_ar_raw=None))
        self.assertEqual(candidate["candidate_status"], "invalid")
        self.assertIn("missing_name", candidate["review_reasons"])

    def test_directory_url_not_promoted_to_official_website(self):
        candidate = mod.normalize_row(self.row(payload_json={"website": "https://directory.example/school/abc"}))
        self.assertIsNone(candidate["website_url"])
        self.assertIn("directory_url_not_official_website", candidate["review_reasons"])


if __name__ == "__main__":
    unittest.main()
