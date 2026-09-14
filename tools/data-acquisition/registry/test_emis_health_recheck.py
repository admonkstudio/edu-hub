#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1]
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))

MODULE_PATH = DATA_DIR / "emis_health_recheck.py"
spec = importlib.util.spec_from_file_location("emis_health_recheck", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


class EmisHealthRecheckTests(unittest.TestCase):
    def test_http_500_government_route_is_unhealthy(self):
        row = {
            "ok": False,
            "status_code": 500,
            "final_url": "https://search.emis.gov.eg/search_schgov.aspx",
            "visible_load_error": False,
        }
        self.assertFalse(mod.government_route_healthy(row))

    def test_http_200_with_visible_load_error_is_unhealthy(self):
        row = {
            "ok": True,
            "status_code": 200,
            "final_url": "https://search.emis.gov.eg/search_schgov.aspx",
            "visible_load_error": True,
        }
        self.assertFalse(mod.government_route_healthy(row))

    def test_clean_http_200_government_route_triggers_recapture_only(self):
        row = {
            "ok": True,
            "status_code": 200,
            "final_url": "https://search.emis.gov.eg/search_schgov.aspx",
            "visible_load_error": False,
        }
        self.assertTrue(mod.government_route_healthy(row))

    def test_known_arabic_load_error_is_detected(self):
        self.assertTrue(mod.page_has_visible_load_error("خطأ اثناء محاولة تحميل الصفحة"))
        self.assertFalse(mod.page_has_visible_load_error("دليل المدارس المصرية"))


if __name__ == "__main__":
    unittest.main()
