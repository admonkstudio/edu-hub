#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("analyze_emis_capture.py")
spec = importlib.util.spec_from_file_location("analyze_emis_capture", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

HANDOFF_PATH = MODULE_PATH.parent.parent / "run_emis_local_capture.py"
handoff_spec = importlib.util.spec_from_file_location("run_emis_local_capture", HANDOFF_PATH)
handoff = importlib.util.module_from_spec(handoff_spec)
assert handoff_spec and handoff_spec.loader
handoff_spec.loader.exec_module(handoff)


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

    def test_handoff_discovers_only_bounded_same_origin_school_endpoints(self):
        report = {
            "pages": [
                {
                    "candidate_links": [
                        {"href": "https://search.emis.gov.eg/search_school_current.aspx#top"},
                        {"href": "https://evil.example/search_school.aspx"},
                        {"href": "javascript:alert(1)"},
                    ],
                    "inline_endpoint_refs": [
                        "https://search.emis.gov.eg/ajax_school.ashx",
                        "https://search.emis.gov.eg/assets/site.css",
                    ],
                    "forms": [
                        {"action": "https://search.emis.gov.eg/search_schgov.aspx"},
                    ],
                }
            ]
        }
        targets = handoff.discover_targets(report, seeds=["https://search.emis.gov.eg/"], limit=5)
        self.assertEqual(targets[0], "https://search.emis.gov.eg/")
        self.assertIn("https://search.emis.gov.eg/search_school_current.aspx", targets)
        self.assertIn("https://search.emis.gov.eg/ajax_school.ashx", targets)
        self.assertIn("https://search.emis.gov.eg/search_schgov.aspx", targets)
        self.assertFalse(any("evil.example" in value for value in targets))
        self.assertLessEqual(len(targets), 5)

    def test_shareable_bundle_excludes_raw_html(self):
        with tempfile.TemporaryDirectory() as td:
            output_dir = Path(td) / "emis-local-capture"
            output_dir.mkdir()
            (output_dir / "index.redacted.html").write_text(
                '<input type="hidden" value="[REDACTED]">', encoding="utf-8"
            )
            (output_dir / "index.raw.html").write_text(
                '<input type="hidden" value="secret-state">', encoding="utf-8"
            )
            (output_dir / "capture-report.json").write_text(
                json.dumps(
                    {
                        "pages": [
                            {
                                "saved_html": "index.redacted.html",
                                "saved_raw_html_local": "index.raw.html",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (output_dir / "enumerator-contract.json").write_text("{}", encoding="utf-8")

            archive = handoff.build_shareable_bundle(output_dir)
            with zipfile.ZipFile(archive) as zf:
                names = set(zf.namelist())

        self.assertIn("emis-local-capture/capture-report.json", names)
        self.assertIn("emis-local-capture/enumerator-contract.json", names)
        self.assertIn("emis-local-capture/index.redacted.html", names)
        self.assertFalse(any("raw.html" in name for name in names))


if __name__ == "__main__":
    unittest.main()
