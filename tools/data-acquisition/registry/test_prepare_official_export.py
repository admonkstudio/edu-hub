#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "prepare_official_export.py"


class OfficialExportIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.registry = self.root / "registry.json"
        self.registry.write_text(json.dumps({
            "schema_version": 1,
            "sources": [
                {
                    "source_id": "moe",
                    "name": "MOE",
                    "authority_class": "primary_official_registry",
                    "coverage_target": {"count": 2}
                },
                {
                    "source_id": "secondary",
                    "name": "Secondary",
                    "authority_class": "secondary_directory",
                    "coverage_target": null
                }
            ]
        }), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, source_id: str, input_path: Path):
        out = self.root / "out"
        return subprocess.run([
            "python", str(SCRIPT),
            "--source-id", source_id,
            "--input", str(input_path),
            "--id-field", "id",
            "--registry", str(self.registry),
            "--out-dir", str(out),
        ], capture_output=True, text=True)

    def test_official_rows_emit_raw_evidence_only(self):
        p = self.root / "rows.jsonl"
        p.write_text('{"id":"A","name":"School A"}\n{"id":"B","name":"School B"}\n', encoding="utf-8")
        result = self.run_tool("moe", p)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["rows_seen"], 2)
        self.assertEqual(report["unique_source_ids"], 2)
        self.assertEqual(report["coverage_percent_before_identity_resolution"], 100.0)
        self.assertEqual(report["canonical_entities_created"], 0)
        self.assertFalse(report["core_promotion_performed"])

    def test_secondary_source_is_rejected(self):
        p = self.root / "rows.jsonl"
        p.write_text('{"id":"A"}\n', encoding="utf-8")
        result = self.run_tool("secondary", p)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only accepts primary_official_registry", result.stderr)

    def test_duplicate_ids_fail_closed(self):
        p = self.root / "rows.jsonl"
        p.write_text('{"id":"A"}\n{"id":"A"}\n', encoding="utf-8")
        result = self.run_tool("moe", p)
        self.assertEqual(result.returncode, 5)


if __name__ == "__main__":
    unittest.main()
