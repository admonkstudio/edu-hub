# Egypt Raw Education Data Acquisition

This workspace exists to answer one question before Edu Hub changes its production schema:

> What institution records and fields actually exist in the public source universe?

It deliberately does **not** normalize sources into the production database.

## Output

The workflow creates `edu_hub_egypt_raw.sqlite` with:

- `sources`
- `acquisition_runs`
- `raw_records`
- `field_inventory`
- `coverage_targets`

Every source row is preserved independently. Cross-source duplicates are intentional.

Additional reports:

- `source_counts.csv`
- `field_inventory.csv`
- `coverage.csv`
- `acquisition_summary.json`

## First-pass sources

1. Live Supreme Council of Universities category pages.
2. Current OpenStreetMap Egypt education features from Geofabrik.
3. Public GitHub Excel snapshot scraped from EgyptSchools.info for Cairo/Giza.
4. Historical 2022 scrape of the former official EMIS school directory published by GetData.io.

## Trust model

- Official registry: identity/category evidence.
- OSM: discovery/geospatial evidence, not regulatory verification.
- Public directories: secondary discovery evidence.
- Historical EMIS scrape: old primary-source snapshot, never proof of current status.

No source is silently promoted to canonical truth.

## Known completeness gaps

The current official Ministry of Education aggregate reports 62,690 schools for 2025/26, but the row-level public school directory is not currently exposed as a bulk export in this acquisition pass.

The Ministry of Social Solidarity reports 48,225 nurseries and states that the national census/database exists; the ministry is developing a public early-childhood map. Until row-level data becomes publicly available or is supplied by MOSS, no acquisition job should claim complete nursery coverage.

Al-Azhar has a separate searchable institute directory and requires a dedicated extractor.

These are acquisition gaps, not fields to fill with guesses.

## Next gate

Do not map the raw database into production yet.

First:
1. finish source acquisition,
2. inspect `field_inventory.csv`,
3. measure source coverage,
4. select canonical fields,
5. map canonical → public projection → Instatic,
6. then import.
