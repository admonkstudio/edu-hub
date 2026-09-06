# Egypt Data Acquisition

Status: **active research/acquisition workstream**. This document describes the raw-source layer only. It does not authorize canonical publishing, indexing, verification badges, or cross-source merging.

## Objective

Build a broad, explainable source inventory for Egyptian education institutions before deciding how each source maps into Edu Hub canonical entities.

The acquisition layer answers:

- What public records can we obtain?
- Which source produced each record?
- What fields does that source expose?
- How current and authoritative is the source?
- What coverage gaps remain?

It does **not** answer whether two records are the same institution or whether a fact is ready to publish.

## Core rule

> Raw record count is not unique-institution count.

Cross-source duplicates, conflicting values, historical records, alternate names and different campus representations are intentionally preserved until the matching/review layer.

## Raw acquisition database

Current raw schema:

- `sources`
- `acquisition_runs`
- `raw_records`
- `field_inventory`
- `coverage_targets`

Each raw record keeps source identity, source record ID when available, source URL, retrieved time, raw hash, raw type/name/location, coordinates when available and the original structured payload.

## Source classes

### Primary / official

#### Supreme Council of Universities

Purpose: current higher-education identity discovery by official category.

Treatment: primary registry evidence. The source still does not imply that every scraped field is complete or that category overlap can be naively totalled.

#### Al-Azhar official institute guide

Source: `https://azhar.gov.eg/IDSC/InstGuide/Guide_Search.aspx`

Purpose: official Al-Azhar institute identity and detail records.

Live directory search dimensions verified during acquisition:

- governorate
- educational administration
- education type
- stage
- gender
- institute name

The directory requires governorate + educational administration + education type + stage. Gender can remain unfiltered. Result IDs are stable source identifiers and are preserved.

Verified detail controls currently include:

- institute name
- famous/known name
- educational administration
- stage
- education type
- student gender
- address
- telephone when populated
- public map URL when present

These controls are copied into convenient raw fields but remain source-specific evidence, not canonical Edu Hub mappings.

#### Ministry of Education / EMIS

Known official 2025/26 aggregate target: **62,690 schools**.

The current record-level directory at `search.emis.gov.eg` is not yet reliably reachable from the acquisition runner. Historical snapshots may be retained for discovery/matching but must never be treated as current verification.

Status: **current record-level acquisition unresolved**.

### Secondary discovery sources

#### OpenStreetMap / Geofabrik Egypt

Purpose: discovery, coordinates, alternate names and geographic hints.

Treatment: secondary open geodata. OSM does not prove regulatory status.

#### MasrSchools

Purpose: school discovery and field census.

Treatment: secondary directory snapshot only.

#### EgyptSchools.info

Purpose: school discovery and field census, especially Cairo/Giza coverage.

Treatment: secondary directory snapshot only. Reviews/comments/media are excluded.

#### MadaresEgypt

Purpose: broad school and nursery discovery.

Treatment: secondary discovery source only.

Acquisition strategy is deliberately **listing-first** rather than exhaustively copying every profile. Listing records preserve source item ID, name, category, source URL and bounded nearby listing context. Profile enrichment should be selective and justified later.

No review/comment/media corpus is collected.

## Coverage targets

Coverage is measured against official universes where a defensible official count exists. A target is not considered met merely because raw-source totals are numerically similar.

Current headline targets include:

- MOE schools: 62,690 official 2025/26 aggregate
- MOSS nurseries: separate national nursery universe; do not add naively to MOE school totals
- Al-Azhar institutes: separate official directory; derive record coverage from the official directory
- Higher education: measure per official category/registry because categories can overlap

## Acquisition workflow

### Base sources

The base acquisition gathers:

1. SCU higher-education lists
2. MasrSchools discovery snapshot
3. EgyptSchools discovery snapshot
4. Al-Azhar official directory snapshot
5. current Egypt OpenStreetMap extract
6. historical EMIS discovery snapshot where available

### Sharding

Long public directories are acquired in bounded shards to improve observability and prevent one slow source from invalidating all work.

Current sharded acquisition:

- MadaresEgypt schools by page ranges
- MadaresEgypt nurseries by page ranges
- Al-Azhar by governorate-index ranges

Shard output is merged by **source record ID only**. This is source-level deduplication, not institution-level canonical deduplication.

## Source-use rules

1. Official source beats secondary source for authority, but conflicts are preserved rather than silently overwritten.
2. Secondary directories are discovery inputs, not verification authorities.
3. Historical official snapshots must be explicitly labelled historical/stale.
4. Missing values stay missing; do not infer unsupported facts during acquisition.
5. Source IDs and URLs must survive downstream processing.
6. Do not copy reviews, user comments, media libraries or authenticated/private content.
7. Respect access controls, public robots/content signals and reasonable request rates.
8. Do not publish a raw record merely because it exists in the acquisition database.
9. Money/commercial status never upgrades factual credibility.
10. Canonical matching, assertions, conflict review and index readiness happen after raw acquisition.

## Exit criteria for this workstream

Raw acquisition is ready for matching/schema retrospective when:

- major official registries have been exhausted or explicitly marked blocked/unavailable;
- broad secondary discovery sources have been sampled/acquired enough to expose taxonomy and field gaps;
- source counts and field inventory are generated;
- every raw record remains attributable to a source;
- current vs historical sources are distinguishable;
- acquisition failures and inaccessible sources are documented;
- no canonical cross-source merge has been performed prematurely.

Only then should the project move into deterministic matching/deduplication and canonical review rules.
