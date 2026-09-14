#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("analyze_emis_capture.py")
spec = importlib.util.spec_from_file_location("analyze_emis_capture", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


class EmisCaptureAnalyzerTests(unittest.TestCase):
    def test_successful_capture_unblocks_adapter_design_without_bulk_authorization(self):
        report = {
            "tool": "emis_local_capture",
            "version": 2,
            "captured_at": "2026-09-14T12:00:00+00:00",
            "pages": [
                {
                    "ok": True,
                    "requested_url": "https://search.emis.gov.eg/sch_data.aspx",
                    "final_url": "https://search.emis.gov.eg/sch_data.aspx",
                    "saved_html": "sch_data.aspx.html",
                    "sha256": "abc",
                    "aspnet_detected": True,
                    "forms": [
                        {
                            "index": 0,
                            "id": "form1",
                            "method": "post",
                            "action": "https://search.emis.gov.eg/sch_data.aspx",
                            "aspnet_state_fields": ["__VIEWSTATE", "__EVENTVALIDATION"],
                            "postback_targets": ["ctl00$ContentPlaceHolder1$ddlGov"],
                            "fields": [
                                {
                                    "tag": "select",
                                    "name": "ctl00$ContentPlaceHolder1$ddlGov",
                                    "id": "ddlGov",
                                    "label": "المحافظة",
                                    "options_count": 28,
                                    "autopostback": True,
                                    "options": [
                                        {"value": "", "text": "اختر المحافظة"},
                                        {"value": "1", "text": "القاهرة"},
                                    ],
                                },
                                {
                                    "tag": "select",
                                    "name": "ctl00$ContentPlaceHolder1$ddlAdmin",
                                    "id": "ddlAdmin",
                                    "label": "الإدارة التعليمية",
                                    "options_count": 2,
                                    "autopostback": True,
                                    "options": [
                                        {"value": "", "text": "اختر الإدارة"},
                                        {"value": "10", "text": "إدارة شمال القاهرة"},
                                    ],
                                },
                                {"tag": "input", "type": "submit", "name": "btnSearch", "id": "btnSearch"},
                            ],
                        }
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            capture_dir = Path(td)
            (capture_dir / "sch_data.aspx.html").write_text("<html></html>", encoding="utf-8")
            result = mod.analyze(report, capture_dir)

        self.assertTrue(result["adapter_design_unblocked"])
        self.assertFalse(result["bulk_enumeration_authorized_by_this_tool"])
        self.assertEqual(result["safety"]["school_rows_enumerated"], 0)
        self.assertIn("governorate", result["inferred_control_roles"])
        self.assertIn("administration", result["inferred_control_roles"])
        self.assertFalse(result["safety"]["edu_core_mutated"])
        self.assertFalse(result["safety"]["public_promotion_performed"])

    def test_unreachable_capture_keeps_adapter_blocked(self):
        report = {
            "tool": "emis_local_capture",
            "version": 2,
            "pages": [
                {
                    "ok": False,
                    "requested_url": "https://search.emis.gov.eg/",
                    "error": "timeout",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            result = mod.analyze(report, Path(td))
        self.assertFalse(result["adapter_design_unblocked"])
        self.assertEqual(result["candidate_forms"], 0)
        self.assertTrue(result["warnings"])

    def test_missing_saved_html_blocks_adapter_design(self):
        report = {
            "tool": "emis_local_capture",
            "version": 2,
            "pages": [
                {
                    "ok": True,
                    "saved_html": "missing.html",
                    "forms": [
                        {
                            "index": 0,
                            "method": "post",
                            "aspnet_state_fields": ["__VIEWSTATE"],
                            "fields": [
                                {
                                    "tag": "select",
                                    "name": "gov",
                                    "id": "gov",
                                    "label": "المحافظة",
                                    "options_count": 3,
                                    "autopostback": True,
                                    "options": [{"value": "1", "text": "القاهرة"}],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            result = mod.analyze(report, Path(td))
        self.assertFalse(result["adapter_design_unblocked"])
        self.assertTrue(any("HTML evidence file is missing" in warning for warning in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
