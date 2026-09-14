# EDU-DATA-1 — Egypt National Education Registry

Status: active implementation milestone

Branch: `edu-data-1-national-registry`

## Purpose

Build Edu Hub's national education identity registry for Egypt before any further public-directory expansion.

This milestone changes the acquisition goal from "find complete profiles" to:

> Every legitimate education institution should be represented once in Edu Hub, with source-backed identity, explicit provenance, measurable completeness, and no invented fields.

A record is allowed to exist even when contact, fee, media, or enrichment fields are not yet available. Missing information is represented as unknown/not-applicable and is improved later through enrichment, verification, and institution claims.

## Hard architecture boundary

The data path is:

`external source -> edu_raw -> edu_staging -> edu_core -> public projection -> website/CMS`

Rules:

1. External websites are acquisition inputs only.
2. `edu_raw` preserves source-shaped evidence and duplicates.
3. `edu_staging` performs normalization, identity matching, conflict detection, and review.
4. `edu_core` stores one canonical institution identity plus provenance-backed field assertions.
5. Public rendering must use a dedicated public projection and owned media only.
6. No raw record is published directly.
7. No source value becomes canonical without retaining its evidence link.
8. No model or enrichment process may invent a value for a missing field.

## National coverage universe

The current registry contract uses official counts as coverage targets, not as promises that row-level data is already acquired.

| Family | Official source | Current target / evidence | Acquisition state |
| --- | --- | ---: | --- |
| Pre-university schools | Ministry of Education / EMIS | 62,690 schools (2025/26) | Official directory confirmed; row-level bulk acquisition unresolved from GitHub-hosted runners |
| Al-Azhar institutes | Al-Azhar Institute Guide | 7,674 source records acquired in prior official run | Row-level official acquisition available |
| Nurseries | Ministry of Social Solidarity | 48,225 nurseries (2025 national census) | Official universe confirmed; public row-level export not yet exposed |
| Higher education | Supreme Council of Universities | 327 current category entries in the SCU acquisition contract | Public official category pages available |
| Private higher institutes | Ministry of Higher Education | 208 ministry headline count | Preserve separately from SCU accreditation count; reconcile in staging |
| Geospatial validation | OSM + official addresses | coverage support, not regulatory identity | Secondary evidence only |

Counts from different authorities may describe different universes or accreditation states. They must not be silently added, substituted, or treated as canonical identity counts until reconciled.

## Institution families

The registry must support at least:

- `early_education`
  - nursery
  - preschool / kindergarten where institutionally distinct
- `pre_university`
  - school
  - technical school
  - special education school
  - international/private language school
  - Al-Azhar institute
  - other regulated school families
- `higher_education`
  - university
  - higher institute
  - academy
  - technological university
  - technical institute / technological college
  - foreign university branch
  - institution established by international/framework agreement
- future regulated education families without schema replacement

Higher education must later support hierarchy:

`institution -> campus -> academic unit/faculty -> department -> program -> degree/qualification`

## Canonical identity contract

Every `edu_core.institutions` row must have:

- immutable `edu_hub_id`
- institution family
- institution type
- canonical Arabic and/or English name when known
- lifecycle status
- registry/data status
- created/updated timestamps
- at least one linked source record

A source identifier remains a source identifier. It never replaces `edu_hub_id`.

## Evidence and provenance contract

Every canonical field that comes from an external source must be traceable through a field assertion containing:

- `edu_hub_id`
- field name
- value
- `raw_id` evidence record
- source authority class
- retrieval time inherited from raw evidence
- confidence/review state
- whether it is currently selected as canonical

Conflicting source values are retained as competing assertions until resolved.

## Completeness model

Completeness is a profile-quality property, not an identity-existence requirement.

### Level 1 — Registered

Official or sufficiently strong identity evidence exists.

### Level 2 — Verified identity

Identity, type and useful location/stage/category evidence are verified.

### Level 3 — Enriched

Useful contact, education, website and/or geospatial fields are populated.

### Level 4 — Complete profile

Relevant fees/admissions/facilities/curriculum/accreditation and descriptive profile fields are substantially populated where applicable.

### Level 5 — Verified media

At least one publication-cleared owned media asset is attached, or another explicit publication-safe media arrangement is recorded.

### Level 6 — Claimed

The institution has verified ownership/control of its Edu Hub profile and can maintain approved fields/media.

A field that is genuinely not applicable must not reduce completeness as if it were missing.

## Matching contract

Identity resolution is evidence-based. Matching signals can include:

- official source ID
- normalized Arabic name
- normalized English name
- aliases/famous names
- phone
- verified domain
- coordinates and distance
- address / governorate / city / district
- education administration
- institution family/type
- parent organization/campus relationships

No single fuzzy-name score may auto-merge high-risk records.

All automated merges must retain their score/evidence and be reversible. Ambiguous pairs create review tasks instead of forced merges.

## Source authority classes

1. `primary_official_registry` — government/regulator identity registry.
2. `primary_official_institution` — institution's own official website/channel.
3. `primary_accreditation` — regulator/accreditor/qualifications authority.
4. `secondary_open_data` — e.g. OSM for geospatial evidence.
5. `secondary_directory` — discovery/enrichment only.
6. `historical_official` — historical primary evidence, not current verification.

Authority affects matching and field-selection confidence but does not make every field from a source automatically correct or current.

## Acquisition order

### D1.1 — Registry architecture and source contract

- freeze national source registry
- add staging/core identity layers
- define provenance and completeness contracts
- add automated contract validation

### D1.2 — Accessible official identity sources

- refresh SCU/higher-education categories
- preserve existing Al-Azhar official acquisition and refresh only where needed
- reconcile MOHESR private/technical institute official lists
- produce coverage reports against official target counts

### D1.3 — MOE / EMIS school identity universe

- run the official directory acquisition from an Egypt/local or otherwise reachable environment
- enumerate public records conservatively
- preserve official IDs, classifications, geographic/administration context and source payload
- alternatively obtain a current machine-readable export from MOE/EMIS
- validate final unique-source coverage against the 62,690 official 2025/26 target

No secondary school directory may be labelled as complete MOE coverage.

### D1.4 — MOSS nursery identity universe

Two tracks run in parallel:

- request a machine-readable row-level extract/data-sharing arrangement for the 48,225-record national census;
- monitor the announced public nursery map/platform and acquire only data made public there.

Secondary nursery directories remain discovery evidence, not national-census substitutes.

### D1.5 — Enrichment

After identity coverage stabilizes:

- official institution website discovery
- contacts
- curriculum/stages/programs
- fees/admissions
- accreditation/qualification data
- coordinates/address validation
- facilities and descriptive information
- media discovery, rights review and institution-supplied media

## Media contract

Mirrored bytes are not automatically publication-cleared.

A public asset requires explicit `public_use_allowed=true` or another documented publication basis. Preferred long-term source is institution-supplied media through profile claiming.

When no publication-safe image exists, the UI should render a designed placeholder using the English institution name when available instead of copying an unlicensed image.

## Coverage and QA metrics

Every acquisition release must report:

- raw source record count
- source IDs populated
- named records
- duplicate source IDs
- candidate canonical identities
- auto-matches
- ambiguous matches
- rejected/invalid records
- institution family/type distribution
- governorate coverage where available
- completeness level distribution
- fields with conflicts
- records with coordinates
- records with contacts
- records with publication-safe media
- official target coverage ratio where a target exists

Raw-record count must never be presented as canonical institution count.

## EDU-DATA-1 acceptance criteria

This milestone is complete only when:

1. The four data layers are explicitly defined and enforced: raw, staging, core, public.
2. Official source coverage targets are versioned in Git.
3. Every canonical institution has an immutable Edu Hub ID and source evidence.
4. Field-level provenance is supported.
5. Matching decisions are explainable and reversible.
6. Missing fields are represented honestly; no synthetic facts are inserted.
7. Completeness levels are computed separately from identity validity.
8. Higher-education hierarchy can be represented without flattening faculties/programs into unrelated institutions.
9. MOE and MOSS coverage gaps are explicit and cannot be hidden by secondary-source counts.
10. Public publication cannot read from `edu_raw` or `edu_staging`.
11. Dataset/version and source-coverage reports can be generated for every release.
12. A representative QA cohort is tested before any large public migration.

## Non-goals for this milestone

- redesigning the public website
- republishing every acquired image
- claiming national completeness before official row-level coverage is obtained
- auto-merging every duplicate
- filling missing facts with AI
- importing raw records directly into Instatic or another CMS

## Decision

EDU-DATA-1 is the prerequisite for future directory rebuilding. UI work may use a small controlled public projection, but the national dataset itself is built from the registry pipeline defined here.