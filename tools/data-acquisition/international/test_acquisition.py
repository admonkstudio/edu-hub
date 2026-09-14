#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def load(name: str):
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


ib = load("acquire_ib_egypt")
scu = load("acquire_scu_foreign_branches")


class InternationalAcquisitionTests(unittest.TestCase):
    def test_ib_result_links_and_private_scope(self):
        search_html = """
        <html><body><h2>Found 1 matching school(s)</h2>
        <table><tr><td><a href="/school/000654/">American International School in Egypt</a></td>
        <td></td><td></td><td>✔</td><td></td><td><ul><li>English</li></ul></td></tr></table>
        </body></html>
        """
        total, rows = ib.result_links(search_html)
        self.assertEqual(total, 1)
        self.assertEqual(rows[0]["ib_school_code"], "000654")
        self.assertTrue(rows[0]["programmes_from_list"]["dp"])

        detail_html = """
        <html><body><h1>American International School in Egypt</h1>
        <div>Type:</div><div>PRIVATE</div>
        <div>Head of school:</div><div>Test Head</div>
        <div>IB School since:</div><div>06 April 1992</div>
        <div>Region:</div><div>IB Africa, Europe, Middle East</div>
        <div>IB School code:</div><div>000654</div>
        <div>Website:</div><div>www.example.edu</div>
        <div>Phone:</div><div>+202000000</div>
        <h2>Our coordinator</h2><h3>Test Coordinator</h3><div>New Cairo</div>
        <a>Contact coordinator</a>
        </body></html>
        """
        record = ib.parse_detail(detail_html, rows[0])
        self.assertEqual(record["scope_state"], "eligible")
        self.assertEqual(record["ownership_scope"], "private_independent")
        self.assertEqual(record["ib_school_code"], "000654")

    def test_ib_state_school_is_retained_but_excluded(self):
        seed = {
            "name": "State Example",
            "ib_school_code": "123456",
            "detail_url": "https://ibo.org/school/123456/",
            "programmes_from_list": {},
            "languages_from_list": [],
        }
        detail_html = "<html><body><h1>State Example</h1><div>Type:</div><div>STATE</div><div>IB School code:</div><div>123456</div></body></html>"
        record = ib.parse_detail(detail_html, seed)
        self.assertEqual(record["scope_state"], "excluded")
        self.assertEqual(record["ownership_scope"], "public")

    def test_scu_parser_deduplicates_branch_headings(self):
        html = """
        <html><body>
        <h4>فرع جامعة كوفنتري البريطانية</h4>
        <h4>فرع جامعة جزيرة الأمير إدوارد</h4>
        <a>فرع جامعة كوفنتري البريطانية</a>
        </body></html>
        """
        rows = scu.parse_branches(html)
        self.assertEqual(rows, ["فرع جامعة كوفنتري البريطانية", "فرع جامعة جزيرة الأمير إدوارد"])


if __name__ == "__main__":
    unittest.main()
