# Edu Hub owned acquisition storage

This layer keeps the acquisition database and media files under Edu Hub control.
Provider URLs are retained only as provenance and re-acquisition references.

## Safety boundaries

- Existing `raw_records` remain unchanged.
- No canonical institution matching or cross-source deduplication is performed.
- A downloaded file is not public-use approved unless `public_reuse_allowed = 1`.
- Binary files use SHA-256 content-addressed paths, so identical images are stored once.
- Every source-to-file relationship remains in `raw_media`, even when several URLs resolve to the same file.

## Commands

```bash
python3 owned_storage.py --db ../edu-hub-egypt-raw-v5.sqlite init
python3 owned_storage.py --db ../edu-hub-egypt-raw-v5.sqlite import-media media.jsonl
python3 owned_storage.py --db ../edu-hub-egypt-raw-v5.sqlite fetch-media --store ../media --limit 100
python3 owned_storage.py --db ../edu-hub-egypt-raw-v5.sqlite report
```

Each media-manifest line is JSON. The minimum fields are `raw_id` and
`original_url`. Optional fields include `media_type`, `alt_text`,
`source_page_url`, `rights_status`, `license_name`, `copyright_owner`,
`credit_text`, `public_reuse_allowed`, and `metadata`.

```json
{"raw_id": 42, "original_url": "https://example.edu/logo.png", "media_type": "logo"}
```

