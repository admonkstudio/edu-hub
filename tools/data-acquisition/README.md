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

## V7 PostgreSQL/Supabase import

V7 is the consolidated owned archive: 24,916 raw records across 13 sources,
2,101 media provenance rows, and 453 unique locally held media files.

The operational import remains deliberately separate from public rendering:

1. Apply `infra/owned-data/001_raw_archive.sql`.
2. Apply `infra/owned-data/002_v7_import_hardening.sql`.
3. Run a non-mutating archive check:

   ```bash
   python tools/data-acquisition/import_v7_postgres.py \
     --sqlite /path/to/edu_hub_owned_archive_v7.sqlite \
     --archive /path/to/edu-hub-egypt-owned-v7.tar.gz \
     --report /path/to/V7-POSTGRES-IMPORT-DRY-RUN.json
   ```

4. Install the pinned importer dependency from
   `tools/data-acquisition/requirements-postgres-import.txt`.
5. Perform the live import from a trusted server environment by adding
   `--database-url "$EDU_HUB_DATABASE_URL"`.

The database URL is never committed. The importer is resumable and idempotent:
records use `(source_id, raw_hash)`, media uses its source identity, and imported
acquisition runs retain their V7 archive identity. The `edu_raw` schema is not a
public read API: anonymous and authenticated roles receive no access.
