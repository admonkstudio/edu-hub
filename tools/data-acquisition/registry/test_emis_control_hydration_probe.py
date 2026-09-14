#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1]
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))

MODULE_PATH = DATA_DIR / "emis_control_hydration_probe.py"
spec = importlib.util.spec_from_file_location("emis_control_hydration_probe", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

HTML = r"""
<html><body>
<form id="form1" method="post" action="./search_schSpecialEdu.aspx">
<input type="hidden" name="__VIEWSTATE" value="STATE" />
<input type="hidden" name="__EVENTVALIDATION" value="VALID" />
<input type="radio" id="r0" name="ctl00$ContentPlaceHolder1$RadioButtonList1" value="0" checked="checked" />
<label for="r0">من فضلك اختر النوع</label>
<input type="radio" id="r1" name="ctl00$ContentPlaceHolder1$RadioButtonList1" value="1"
 onclick="javascript:setTimeout('__doPostBack(\'ctl00$ContentPlaceHolder1$RadioButtonList1$1\',\'\')', 0)" />
<label for="r1">تربية فكرية</label>
<select name="ctl00$ContentPlaceHolder1$DDList_mud" id="ContentPlaceHolder1_DDList_mud"></select>
<input type="text" name="ctl00$ContentPlaceHolder1$TextBox1" value="do-not-submit" />
<input type="submit" name="ctl00$ContentPlaceHolder1$Button1" value="بحث" />
</form>
</body></html>
"""


class EmisControlHydrationProbeTests(unittest.TestCase):
    def test_selects_first_non_placeholder_whitelisted_postback_control(self):
        from bs4 import BeautifulSoup

        form = BeautifulSoup(HTML, "html.parser").find("form")
        control = mod.hydration_control(form)
        self.assertIsNotNone(control)
        self.assertEqual(control["value"], "1")
        self.assertEqual(control["label"], "تربية فكرية")
        self.assertEqual(
            control["event_target"],
            "ctl00$ContentPlaceHolder1$RadioButtonList1$1",
        )

    def test_submission_contains_only_hidden_state_event_and_selected_radio(self):
        action, payload, control = mod.build_hydration_submission(HTML)
        self.assertEqual(action, "https://search.emis.gov.eg/search_schSpecialEdu.aspx")
        self.assertEqual(payload["__VIEWSTATE"], "STATE")
        self.assertEqual(payload["__EVENTVALIDATION"], "VALID")
        self.assertEqual(payload["__EVENTTARGET"], control["event_target"])
        self.assertEqual(payload["__EVENTARGUMENT"], "")
        self.assertEqual(payload[control["name"]], "1")
        self.assertNotIn("ctl00$ContentPlaceHolder1$TextBox1", payload)
        self.assertNotIn("ctl00$ContentPlaceHolder1$Button1", payload)

    def test_off_origin_form_action_is_refused(self):
        bad_html = HTML.replace(
            'action="./search_schSpecialEdu.aspx"',
            'action="https://example.com/search.aspx"',
        )
        with self.assertRaises(ValueError):
            mod.build_hydration_submission(bad_html)

    def test_source_page_must_be_reachable_navigation_form_with_postback_radio(self):
        report = {
            "pages": [
                {
                    "request_kind": "root_button_navigation",
                    "ok": True,
                    "button_name": "ctl00$ContentPlaceHolder1$Button4",
                    "button_value": "مدارس التربية الخاصة",
                    "forms": [
                        {
                            "fields": [
                                {"tag": "select", "name": "gov"},
                                {
                                    "tag": "input",
                                    "type": "radio",
                                    "name": "type",
                                    "attrs": {"onclick": "__doPostBack('x','')"},
                                },
                            ]
                        }
                    ],
                }
            ]
        }
        page = mod.choose_source_page(report)
        self.assertEqual(page["button_name"], "ctl00$ContentPlaceHolder1$Button4")


if __name__ == "__main__":
    unittest.main()
