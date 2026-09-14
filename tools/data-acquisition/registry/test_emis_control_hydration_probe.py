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
<input type="radio" id="r2" name="ctl00$ContentPlaceHolder1$RadioButtonList1" value="2"
 onclick="javascript:setTimeout('__doPostBack(\'ctl00$ContentPlaceHolder1$RadioButtonList1$2\',\'\')', 0)" />
<label for="r2">مكفوفين وضعاف بصر</label>
<input type="radio" id="r3" name="ctl00$ContentPlaceHolder1$RadioButtonList1" value="3"
 onclick="javascript:setTimeout('__doPostBack(\'ctl00$ContentPlaceHolder1$RadioButtonList1$3\',\'\')', 0)" />
<label for="r3">صم وضعاف سمع</label>
<select name="ctl00$ContentPlaceHolder1$DDList_mud" id="ContentPlaceHolder1_DDList_mud"></select>
<input type="text" name="ctl00$ContentPlaceHolder1$TextBox1" value="do-not-submit" />
<input type="submit" name="ctl00$ContentPlaceHolder1$Button1" value="بحث" />
</form>
</body></html>
"""


class EmisControlHydrationProbeTests(unittest.TestCase):
    def test_discovers_only_three_non_placeholder_whitelisted_postback_controls(self):
        from bs4 import BeautifulSoup

        form = BeautifulSoup(HTML, "html.parser").find("form")
        controls = mod.hydration_controls(form)
        self.assertEqual([row["value"] for row in controls], ["1", "2", "3"])
        self.assertEqual(controls[0]["label"], "تربية فكرية")
        self.assertTrue(
            all(row["event_target"].startswith(mod.ALLOWED_EVENT_PREFIX) for row in controls)
        )

    def test_backward_compatible_first_control_helper(self):
        from bs4 import BeautifulSoup

        form = BeautifulSoup(HTML, "html.parser").find("form")
        control = mod.hydration_control(form)
        self.assertIsNotNone(control)
        self.assertEqual(control["value"], "1")

    def test_submission_contains_only_hidden_state_event_and_selected_radio(self):
        from bs4 import BeautifulSoup

        form = BeautifulSoup(HTML, "html.parser").find("form")
        requested = mod.hydration_controls(form)[1]
        action, payload, control = mod.build_hydration_submission(HTML, requested)
        self.assertEqual(action, "https://search.emis.gov.eg/search_schSpecialEdu.aspx")
        self.assertEqual(payload["__VIEWSTATE"], "STATE")
        self.assertEqual(payload["__EVENTVALIDATION"], "VALID")
        self.assertEqual(payload["__EVENTTARGET"], control["event_target"])
        self.assertEqual(payload["__EVENTARGUMENT"], "")
        self.assertEqual(payload[control["name"]], "2")
        self.assertNotIn("ctl00$ContentPlaceHolder1$TextBox1", payload)
        self.assertNotIn("ctl00$ContentPlaceHolder1$Button1", payload)

    def test_requested_control_must_still_exist_on_fresh_form(self):
        stale = {
            "name": "ctl00$ContentPlaceHolder1$RadioButtonList1",
            "value": "9",
            "event_target": "ctl00$ContentPlaceHolder1$RadioButtonList1$9",
        }
        with self.assertRaises(ValueError):
            mod.build_hydration_submission(HTML, stale)

    def test_off_origin_form_action_is_refused(self):
        bad_html = HTML.replace(
            'action="./search_schSpecialEdu.aspx"',
            'action="https://example.com/search.aspx"',
        )
        with self.assertRaises(ValueError):
            mod.build_hydration_submission(bad_html)

    def test_visible_server_error_message_is_captured(self):
        html = '<span id="ContentPlaceHolder1_Labelerror">خطأ اثناء محاولة تحميل الصفحة</span>'
        self.assertEqual(mod.visible_error_messages(html), ["خطأ اثناء محاولة تحميل الصفحة"])

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
