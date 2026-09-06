# Egypt Raw Education Data Acquisition

This workspace exists to answer one question before Edu Hub changes its production schema:

> What institution records, fields, and media actually exist in the public source universe?

It deliberately does **not** normalize sources into the production database.

## Locked ownership principle

Edu Hub/Admonk must be the operational holder of the records and media it renders.

External directories, government search pages, and source APIs are **acquisition inputs only**. The public site must not depend on them at render time.

For data, preserve the complete source payload in our owned raw archive. For images, preserve the source URL for provenance and mirror permitted image bytes into Edu Hub-controlled storage. Production must use our own database/read model and our own media URL/storage key rather than hotlinking the source.

See `docs/DATA-OWNERSHIP-AND-RUNTIME.md`.

## Output

The acquisition workflow creates `edu_hub_egypt_raw.sqlite` with:

- `sources`
- `acquisition_runs`
- `raw_records`
- `field_inventory`
- `coverage_targets`

Media acquisition adds source-neutral media tables to the same owned archive database when the same `--db` path is used:

- `media_assets`
- `media_files`

Every source row is preserved independently. Cross-source duplicates are intentional.

Additional reports include:

- `source_counts.csv`
- `field_inventory.csv`
- `coverage.csv`
- `acquisition_summary.json`
- `media_coverage.csv`
- media archive checksums/manifests where generated

## Media pipeline

`discover_media.py` discovers image candidates from already-acquired public profile pages without making a publication-rights decision.

`archive_media.py` mirrors discovered image bytes into an Edu Hub-controlled folder and stores content hashes, storage keys, MIME type, byte size and dimensions in the owned archive database.

Important:

- mirrored/archived does **not** mean cleared for public use;
- default rights state is `unknown`;
- default `public_use_allowed` is false;
- original source URLs remain provenance only;
- the production website must never hotlink source images.

## Trust model

- Official registry: identity/category evidence.
- OSM: discovery/geospatial evidence, not regulatory verification.
- Public directories: secondary discovery evidence.
- Historical official scrape: old primary-source snapshot, never proof of current status.

No source is silently promoted to canonical truth.

## Known completeness gaps

The current official Ministry of Education aggregate reports 62,690 schools for 2025/26, but the row-level public school directory is not currently exposed as a bulk export in this acquisition pass.

The Ministry of Social Solidarity reports 48,225 nurseries and states that the national census/database exists; the ministry is developing a public early-childhood map. Until row-level data becomes publicly available or is supplied by MOSS, no acquisition job should claim complete nursery coverage.

These are acquisition gaps, not fields to fill with guesses.

## Next gate

Do not map the raw database into production yet.

First:
1. finish source acquisition,
2. finish media discovery/mirroring coverage,
3. inspect `field_inventory.csv`,
4. inspect `media_coverage.csv`,
5. measure source coverage,
6. match/deduplicate institution identities,
7. select canonical fields,
8. map canonical → public projection → Instatic,
9. then import.

The source systems must never be required for normal website rendering after import.
