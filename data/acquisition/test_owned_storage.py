import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from owned_storage import init, register_media


class OwnedStorageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "test.sqlite"
        db = sqlite3.connect(self.db_path)
        db.executescript("""
          CREATE TABLE sources (source_id TEXT PRIMARY KEY, name TEXT, url TEXT, source_type TEXT, authority TEXT, notes TEXT);
          CREATE TABLE raw_records (
            raw_id INTEGER PRIMARY KEY, source_id TEXT, source_record_id TEXT, entity_family TEXT,
            entity_type_raw TEXT, name_raw TEXT, name_ar_raw TEXT, name_en_raw TEXT,
            location_raw TEXT, latitude REAL, longitude REAL, source_url TEXT,
            retrieved_at TEXT, raw_hash TEXT, payload_json TEXT
          );
        """)
        payload = json.dumps({"name": "مدرسة الاختبار"}, ensure_ascii=False)
        db.execute("INSERT INTO sources VALUES ('source', 'Source', 'https://example.test', 'directory', 'secondary', NULL)")
        db.execute("INSERT INTO raw_records VALUES (1, 'source', 'A1', 'school', NULL, 'Test', NULL, NULL, NULL, NULL, NULL, 'https://example.test/a1', '2026-09-06T00:00:00+00:00', 'raw', ?)", (payload,))
        db.commit()
        db.close()
        init(self.db_path, Path(__file__).with_name("schema.sql"))

    def tearDown(self):
        self.temp.cleanup()

    def test_existing_record_is_owned_and_media_defaults_to_private(self):
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        ownership = db.execute("SELECT * FROM record_ownership WHERE raw_id = 1").fetchone()
        self.assertEqual(ownership["owner_id"], "edu-hub")
        payload = db.execute("SELECT payload_json FROM raw_records WHERE raw_id = 1").fetchone()[0]
        self.assertEqual(ownership["payload_sha256"], hashlib.sha256(payload.encode()).hexdigest())
        media_id = register_media(db, {"raw_id": 1, "original_url": "https://example.test/logo.png", "media_type": "logo"})
        db.commit()
        media = db.execute("SELECT * FROM raw_media WHERE raw_media_id = ?", (media_id,)).fetchone()
        self.assertEqual(media["source_id"], "source")
        self.assertEqual(media["source_record_id"], "A1")
        self.assertEqual(media["rights_status"], "unknown")
        self.assertEqual(media["public_reuse_allowed"], 0)


if __name__ == "__main__":
    unittest.main()
