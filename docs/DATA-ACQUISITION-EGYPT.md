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

Cross-source duplicates, conflicting values, historical records, alternate names, sector-list repetitions and different campus representations are intentionally preserved until the matching/review layer.

## Raw acquisition database

Current raw schema:

- `sources`
- `acquisition_runs`
- `raw_records`
- `field_inventory`
- `coverage_targets`

Each raw record keeps source identity, source record ID when available, source URL, retrieved time, raw hash, raw type/name/location, coordinates when available and the original structured payload.

### V4 pre-Madares snapshot — 2026-09-06

The latest assembled local raw snapshot contains:

- **13,452 raw source records**
- **12,243 named raw source records**
- **806 source-field inventory rows**

Entity-family raw totals:

- pre-university: 12,277
- higher education: 1,111
- early education: 64

These figures are raw-source totals only and must not be interpreted as unique institution counts.

## Source classes

### Primary / official

#### Supreme Council of Universities

Purpose: current higher-education identity discovery by official category.

Current snapshot: **327 source records**.

Treatment: primary registry evidence. The source still does not imply that every scraped field is complete or that category overlap can be naively totalled.

#### Ministry of Higher Education — private higher institutes

Official source: `https://dportal.mohesr.gov.eg/index.php?id=193&option=com_sppagebuilder&view=page`

The current page claims **208 private higher institutes** across eight sectors. The rendered source currently exposes **189 numbered sector occurrences** across seven visible sectors:

- engineering: 55
- commercial: 71
- computer science / information systems: 16
- languages / media: 19
- social work: 16
- applied health sciences / nursing: 10
- agriculture: 2

The tourism/hotels sector is named in the 208 headline but is absent from the rendered official HTML. Current 2026 Ministry-list republications identify the missing tourism/hotels sector as **19 institutes**. Those 19 are retained separately as `secondary_republication_of_primary`; they are not silently presented as rows downloaded from the MOHESR HTML.

Important: the 208 sector-list total must not be treated automatically as 208 unique canonical institutions because some institute names occur in more than one academic-sector list. Sector occurrences are preserved raw until matching.

#### Ministry of Higher Education — technological colleges and technical institutes

Official source: `https://mohesr.gov.eg/index.php?id=190&option=com_sppagebuilder&view=page`

Verified current source structure:

- **8 technological colleges**
- **44 technical/commercial/industrial/hotel institutes** beneath them

Both the 8 parent college headings and the 44 institute rows are retained as raw records. Relationship modelling is deferred to the canonical phase.

#### Al-Azhar official institute guide

Source: `https://azhar.gov.eg/IDSC/InstGuide/Guide_Search.aspx`

Current acquisition: **7,674 official institute records**, all named and carrying source location/context.

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

The current `https://emis.gov.eg/` homepage and its live `main.js` were inspected on 2026-09-06. The current official JavaScript explicitly advertises:

- `https://schools.emis.gov.eg/` as **المدرسة**
- `https://search.emis.gov.eg/` as **دليل المدارس المصرية** (Egyptian Schools Directory)

This establishes that `search.emis.gov.eg` is still the current official directory endpoint; it is not merely a historical URL.

However, the record-level directory repeatedly times out from GitHub-hosted acquisition runners even while `emis.gov.eg` and `main.js` remain reachable. Direct requests to both the directory root and the historical `search_schpriv.aspx` path time out from hosted runners. No alternate public row-level API was exposed by the current homepage JavaScript.

Historical snapshots may be retained for discovery/matching but must never be treated as current verification. A separate NCEEE endpoint diagnostic was also attempted; the candidate public endpoints returned 404 and are not currently a viable school-registry substitute.

Status: **current official directory confirmed; current row-level bulk acquisition unresolved because the directory host is unreachable from the hosted acquisition environment**.

Preferred next acquisition paths, in order:

1. test the official directory from an Egypt/local browser or Egypt-hosted runner;
2. if reachable, inspect its public requests and export/enumerate the public directory at a conservative rate;
3. request a current CSV/XLSX database export directly from MOE/EMIS;
4. retain secondary directories and historical data only as discovery evidence until an official current extract is obtained.

#### Ministry of Social Solidarity — nursery census

Official current universe: **48,225 nurseries** from the national comprehensive nursery census.

The current MOSS website exposes a public 2025 census PDF covering all **27 directorates**. The published census is aggregate rather than row-level. Current published headline facts include:

- 48,225 nurseries
- 1,764,881 enrolled children
- 133,375 classes
- 254,322 employees

A direct public-platform diagnostic was run against `www.moss.gov.eg` and `digital.moss.gov.eg`. No public row-level nursery API/map endpoint was found in the obvious public pages or JavaScript assets.

MOSS currently states that it is working with the Ministry of Communications to develop a digital early-childhood platform and nursery map intended to expose information including the nearest nursery, licensing status, capacity and fees. This indicates that the row-level public map is **planned/in development rather than currently exposed as a downloadable public registry**.

Authenticated nursery-licensing/service flows on the digital platform are private service functionality and are explicitly outside the acquisition scope.

Status: **official national universe confirmed; public row-level database not currently exposed**.

Preferred next acquisition paths:

1. request the census row-level CSV/XLSX/database export directly from MOSS;
2. monitor the planned public nursery map/platform and acquire only its public data after launch;
3. use MadaresEgypt and other public directories as secondary discovery coverage in the meantime, without calling them official census coverage.

### Secondary discovery sources

#### OpenStreetMap / Geofabrik Egypt

Current snapshot: **3,104 raw education features**.

Purpose: discovery, coordinates, alternate names and geographic hints.

Treatment: secondary open geodata. OSM does not prove regulatory status.

#### MasrSchools

Current snapshot: **462 raw profile records**.

Purpose: school discovery and field census.

Treatment: secondary directory snapshot only.

#### EgyptSchools.info

Current direct-directory snapshot: **807 records**.

Additional public GitHub snapshot: **805 records**.

Purpose: school discovery and field census, especially Cairo/Giza coverage.

Treatment: secondary directory snapshot only. Reviews/comments/media are excluded.

#### MadaresEgypt

Purpose: broad school and nursery discovery.

Treatment: secondary discovery source only.

Acquisition strategy is deliberately **listing-first** rather than exhaustively copying every profile. Listing records preserve source item ID, name, category, source URL and bounded nearby listing context. Profile enrichment should be selective and justified later.

The source's live paginator currently exposes:

- schools through page **1,388**
- nurseries through page **584**

The source is slow and intermittently times out. The crawler is therefore sharded into bounded school/nursery page ranges, retries transient failures and performs a repair pass before a shard is accepted. The broad MadaresEgypt run is **not included in the V4 pre-Madares totals above until its merged report passes**.

At the latest checkpoint, the first eight school shards had completed successfully. For example, school pages 1–100 produced **1,003 named unique source IDs**, and a transient page-56 timeout was recovered by the repair pass with zero unresolved pages.

No review/comment/media corpus is collected.

#### Current Ministry-list republications

Where a government HTML source explicitly claims a category/count but omits its row-level section, a current reputable republication of that Ministry list may be retained as a **separate secondary source**. It must never be merged into the official source identity or upgraded to primary authority.

Current use: the 19 tourism/hotel private higher institutes missing from the rendered MOHESR 208-institute page.

## Coverage targets

Coverage is measured against official universes where a defensible official count exists. A target is not considered met merely because raw-source totals are numerically similar.

Current headline targets include:

- MOE schools: 62,690 official 2025/26 aggregate
- MOSS nurseries: 48,225 national census universe; do not add naively to MOE school totals
- Al-Azhar institutes: separate official directory; 7,674 rows acquired from the official guide
- private higher institutes: official headline 208 sector-list occurrences; source-level overlap must be resolved later
- technical higher education: 8 technological colleges + 44 institutes acquired from MOHESR
- higher education generally: measure per official category/registry because categories can overlap

## Acquisition workflow

### Base sources

The base acquisition gathers:

1. SCU higher-education lists
2. MasrSchools discovery snapshot
3. EgyptSchools discovery snapshot
4. Al-Azhar official directory snapshot
5. current Egypt OpenStreetMap extract
6. historical EMIS discovery snapshot where available

Additional official higher-education acquisition now includes:

7. MOHESR private higher-institute sector list
8. MOHESR technological colleges / technical institutes

Current official-access diagnostics also cover:

9. EMIS homepage/current school-directory route discovery
10. MOSS national nursery census/public-platform endpoint discovery

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
11. Sector-list occurrence counts are not automatically unique institution counts.
12. A secondary republication used to recover a missing official section remains a separate secondary source record.
13. A public aggregate count is a coverage target, not proof that its row-level records were acquired.
14. Authenticated government service systems are not scraped to obtain private/non-public records.

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
