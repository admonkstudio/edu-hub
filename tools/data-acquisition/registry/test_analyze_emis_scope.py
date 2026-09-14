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


def special_form(saved_html: str = "special.html") -> dict:
    return {
        "request_kind": "root_button_navigation",
        "ok": True,
        "button_name": "ctl00$ContentPlaceHolder1$Button4",
        "button_value": "مدارس التربية الخاصة",
        "requested_url": "https://search.emis.gov.eg/",
        "final_url": "https://search.emis.gov.eg/search_schSpecialEdu.aspx",
        "saved_html": saved_html,
        "sha256": "abc",
        "aspnet_detected": True,
        "forms": [
            {
                "index": 0,
                "id": "form1",
                "method": "post",
                "action": "https://search.emis.gov.eg/search_schSpecialEdu.aspx",
                "aspnet_state_fields": ["__VIEWSTATE", "__EVENTVALIDATION"],
                "fields": [
                    {
                        "tag": "input",
                        "type": "radio",
                        "name": "ctl00$ContentPlaceHolder1$RadioButtonList1",
                        "id": "type1",
                        "value": "1",
                        "label": "تربية فكرية",
                        "attrs": {"onclick": "__doPostBack('ctl00$ContentPlaceHolder1$RadioButtonList1$1','')"},
                    },
                    {
                        "tag": "select",
                        "name": "ctl00$ContentPlaceHolder1$DDList_mud",
                        "id": "ContentPlaceHolder1_DDList_mud",
                        "options_count": 0,
                        "options": [],
                    },
                    {
                        "tag": "select",
                        "name": "ctl00$ContentPlaceHolder1$DDList_stage",
                        "id": "ContentPlaceHolder1_DDList_stage",
                        "options_count": 0,
                        "options": [],
                    },
                ],
            }
        ],
    }


class EmisScopeAnalyzerTests(unittest.TestCase):
    def test_empty_special_ed_selects_recommend_hydration_not_government_pilot(self):
        report = {
            "tool": "emis_local_capture",
            "version": 3,
            "pages": [special_form()],
        }
        with tempfile.TemporaryDirectory() as td:
            capture_dir = Path(td)
            (capture_dir / "special.html").write_text("<html></html>", encoding="utf-8")
            result = mod.analyze(report, capture_dir)

        self.assertFalse(result["adapter_design_unblocked"])
        self.assertFalse(result["government_adapter_design_unblocked"])
        self.assertTrue(result["hydration_probe_recommended"])
        self.assertFalse(result["hydration_attempted"])
        self.assertEqual(result["primary_form_candidate"]["page"]["scope"], "special_education")
        self.assertIn("control-hydration", result["required_next_gate"])

    def test_populated_special_ed_contract_never_unblocks_government_enumeration(self):
        report = {
            "tool": "emis_local_capture",
            "version": 3,
            "pages": [
                {
                    "request_kind": "control_hydration",
                    "source_button_name": "ctl00$ContentPlaceHolder1$Button4",
                    "source_button_value": "مدارس التربية الخاصة",
                    "ok": True,
                    "requested_url": "https://search.emis.gov.eg/search_schSpecialEdu.aspx",
                    "final_url": "https://search.emis.gov.eg/search_schSpecialEdu.aspx",
                    "saved_html": "hydrated.html",
                    "sha256": "def",
                    "aspnet_detected": True,
                    "forms": [
                        {
                            "index": 0,
                            "id": "form1",
                            "method": "post",
                            "action": "https://search.emis.gov.eg/search_schSpecialEdu.aspx",
                            "aspnet_state_fields": ["__VIEWSTATE", "__EVENTVALIDATION"],
                            "fields": [
                                {
                                    "tag": "select",
                                    "name": "ctl00$ContentPlaceHolder1$DDList_mud",
                                    "id": "ContentPlaceHolder1_DDList_mud",
                                    "options_count": 28,
                                    "options": [{"value": "1", "text": "القاهرة"}],
                                },
                                {
                                    "tag": "select",
                                    "name": "ctl00$ContentPlaceHolder1$DDList_stage",
                                    "id": "ContentPlaceHolder1_DDList_stage",
                                    "options_count": 4,
                                    "options": [{"value": "1", "text": "ابتدائي"}],
                                },
                            ],
                        }
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            capture_dir = Path(td)
            (capture_dir / "hydrated.html").write_text("<html></html>", encoding="utf-8")
            result = mod.analyze(report, capture_dir)

        self.assertTrue(result["adapter_design_unblocked"])
        self.assertFalse(result["government_adapter_design_unblocked"])
        self.assertEqual(result["primary_form_candidate"]["page"]["scope"], "special_education")
        self.assertIn("government-school national enumeration blocked", result["required_next_gate"])

    def test_exhausted_hydration_stops_repeat_probe_recommendation(self):
        report = {
            "tool": "emis_local_capture",
            "version": 3,
            "pages": [
                special_form(),
                {
                    "request_kind": "control_hydration",
                    "source_button_name": "ctl00$ContentPlaceHolder1$Button4",
                    "source_button_value": "مدارس التربية الخاصة",
                    "ok": True,
                    "requested_url": "https://search.emis.gov.eg/search_schSpecialEdu.aspx",
                    "final_url": "https://search.emis.gov.eg/search_schSpecialEdu.aspx",
                    "saved_html": "hydrated-error.html",
                    "sha256": "err",
                    "aspnet_detected": True,
                    "visible_error_messages": ["خطأ اثناء محاولة تحميل الصفحة"],
                    "forms": special_form()["forms"],
                },
            ],
            "hydration_probe": {
                "performed": True,
                "controls_discovered": 3,
                "controls_submitted": 3,
                "populated_selects": 0,
            },
        }
        with tempfile.TemporaryDirectory() as td:
            capture_dir = Path(td)
            (capture_dir / "special.html").write_text("<html></html>", encoding="utf-8")
            (capture_dir / "hydrated-error.html").write_text("<html></html>", encoding="utf-8")
            result = mod.analyze(report, capture_dir)

        self.assertFalse(result["hydration_probe_recommended"])
        self.assertTrue(result["hydration_attempted"])
        self.assertTrue(result["hydration_exhausted_without_population"])
        self.assertEqual(result["hydration_error_pages"], 1)
        self.assertIn("Do not repeat", result["required_next_gate"])
        self.assertIn("official machine-readable MOE/EMIS export", result["required_next_gate"])


if __name__ == "__main__":
    unittest.main()
