#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1]
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))

MODULE_PATH = DATA_DIR / "emis_navigation_probe.py"
spec = importlib.util.spec_from_file_location("emis_navigation_probe", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

HTML = """
<html><body>
<form id="form1" method="post" action="./">
<input type="hidden" name="__VIEWSTATE" value="STATE" />
<input type="hidden" name="__EVENTVALIDATION" value="VALID" />
<input type="text" name="not_hidden" value="ignore-me" />
<input type="submit" id="ContentPlaceHolder1_Button1" name="ctl00$ContentPlaceHolder1$Button1" value="المــدارس الحـكـوميـة" />
<input type="submit" id="ContentPlaceHolder1_Button5" name="ctl00$ContentPlaceHolder1$Button5" value="المــدارس الخاصة" />
<input type="submit" id="OtherButton" name="other$Button" value="Do not probe" />
</form>
</body></html>
"""


class EmisNavigationProbeTests(unittest.TestCase):
    def test_only_whitelisted_root_navigation_buttons_are_discovered(self):
        buttons = mod.root_navigation_buttons(HTML)
        self.assertEqual(len(buttons), 2)
        self.assertEqual(buttons[0]["name"], "ctl00$ContentPlaceHolder1$Button1")
        self.assertEqual(buttons[1]["name"], "ctl00$ContentPlaceHolder1$Button5")
        self.assertTrue(all(row["name"].startswith(mod.ALLOWED_BUTTON_PREFIX) for row in buttons))

    def test_submission_preserves_only_hidden_state_plus_clicked_button(self):
        action, payload, value = mod.build_button_submission(
            HTML,
            "ctl00$ContentPlaceHolder1$Button1",
        )
        self.assertEqual(action, "https://search.emis.gov.eg/")
        self.assertEqual(payload["__VIEWSTATE"], "STATE")
        self.assertEqual(payload["__EVENTVALIDATION"], "VALID")
        self.assertEqual(payload["ctl00$ContentPlaceHolder1$Button1"], value)
        self.assertNotIn("not_hidden", payload)
        self.assertNotIn("ctl00$ContentPlaceHolder1$Button5", payload)
        self.assertNotIn("other$Button", payload)

    def test_non_navigation_button_is_refused(self):
        with self.assertRaises(ValueError):
            mod.build_button_submission(HTML, "other$Button")


if __name__ == "__main__":
    unittest.main()
