import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "match_staging_identities.py"
spec = importlib.util.spec_from_file_location("match_staging_identities", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


class IdentityMatchingTests(unittest.TestCase):
    def candidate(self, candidate_id, source_id, **overrides):
        base = {
            "candidate_id": candidate_id,
            "source_id": source_id,
            "normalized_name": "cairo international school",
            "entity_type_normalized": "school",
            "phone": None,
            "email": None,
            "website_url": None,
            "governorate_guess": "Cairo",
            "location_raw": "Cairo",
            "latitude": 30.04,
            "longitude": 31.23,
        }
        base.update(overrides)
        return base

    def test_phone_formatting_plus_exact_name_is_high_confidence_proposal(self):
        left = self.candidate(1, "source_a", phone="+20 10 12345678")
        right = self.candidate(2, "source_b", phone="01012345678")
        score, status, evidence = mod.score_pair(left, right)
        self.assertEqual(status, "proposed")
        self.assertGreaterEqual(score, 0.85)
        self.assertIn("exact_phone", {item[0] for item in evidence})

    def test_name_only_collision_stays_reviewable(self):
        left = self.candidate(1, "source_a", latitude=None, longitude=None, location_raw="Nasr City")
        right = self.candidate(2, "source_b", latitude=None, longitude=None, location_raw="Heliopolis")
        score, status, _ = mod.score_pair(left, right)
        self.assertEqual(status, "needs_review")
        self.assertGreaterEqual(score, 0.60)

    def test_same_source_records_are_never_paired(self):
        left = self.candidate(1, "source_a")
        right = self.candidate(2, "source_a")
        pairs, _ = mod.generate_candidate_pairs([left, right])
        self.assertEqual(pairs, set())

    def test_different_name_without_strong_evidence_is_not_persisted(self):
        left = self.candidate(1, "source_a", normalized_name="cairo school", latitude=None, longitude=None)
        right = self.candidate(2, "source_b", normalized_name="alexandria academy", latitude=None, longitude=None)
        _, status, _ = mod.score_pair(left, right)
        self.assertIsNone(status)

    def test_large_shared_block_is_skipped(self):
        candidates = [
            self.candidate(index, f"source_{index}", normalized_name="generic school", latitude=None, longitude=None)
            for index in range(1, 6)
        ]
        pairs, skipped = mod.generate_candidate_pairs(candidates, max_block_size=4)
        self.assertEqual(pairs, set())
        self.assertTrue(any(item["block"] == "normalized_name" for item in skipped))


if __name__ == "__main__":
    unittest.main()
