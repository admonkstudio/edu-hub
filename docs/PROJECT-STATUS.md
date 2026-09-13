# Edu Hub Project Status

Last updated: 2026-09-13

## Current lifecycle

```text
00 Open                  APPROVED
01 Discover              APPROVED
02 Align + Audit         APPROVED FOR CURRENT SCOPE
03 Define                APPROVED
04 Content + Structure   IN PROGRESS
05 Creative Direction    NOT STARTED
06 Design + Systemize    NOT STARTED
07 Build + Connect       ACTIVE — DATA RECONSTRUCTION
08 Verify + Optimize     ACTIVE FOR DATA BOUNDARY
09 Review + Launch       NOT STARTED
10 Handoff + Learn       NOT STARTED
```

## Current project state

Edu Hub is an Admonk-owned independent education discovery and knowledge platform.

Initial market: Egypt.

Primary audience:

1. Parents
2. Students

Phase 1 combines:

- structured education-provider directory
- bilingual public experience
- editorial/knowledge platform
- internal research/admin system
- source provenance and freshness workflows
- technical SEO and AI-search discoverability foundation

Phase 2 commercial functionality is intentionally deferred.

## Approved architecture direction

- Astro + TypeScript
- monorepo with public app and control/admin app
- PostgreSQL as source of truth
- Supabase as initial database/auth/storage platform
- PostGIS for geographic capability
- Arabic + English from launch
- country-aware locales beginning with `ar-EG` and `en-EG`
- official-source-first data collection
- explicit source/evidence model
- deterministic indexability rules
- curated programmatic SEO only
- PostgreSQL search first; dedicated search infrastructure only after evidence justifies it

## Current reconstruction milestone

**EDU-DATA-1 — Egypt National Education Registry**

The data path is now explicitly separated into:

```text
external / official sources
→ edu_raw
→ edu_staging
→ identity matching + review
→ canonical core
→ public read model
→ website / CMS
```

Raw data is evidence. Staging data is a candidate/matching surface. Neither is public canonical data.

## Data acquisition and recovery status — 2026-09-13

- Egypt raw acquisition remains active; canonical modelling, cross-source deduplication and public projections remain gated by matching/review.
- MadaresEgypt bounded acquisition repair is complete: 11,339 listing-level records with zero unresolved crawl pages. Profile crawling remains disabled on the current route after the deterministic 50-record viability test produced 50 timeouts and zero accepted profiles.
- V7 is the current complete portable owned archive: 24,916 raw records across 13 sources and 24,916 ownership rows.
- V7 retains 2,101 AlexSchools media provenance references and 453 unique content-addressed binaries. Public-use eligibility remains false for every acquired asset pending rights review.
- V7 has zero duplicate `(source_id, raw_hash)` groups, zero duplicate non-empty `(source_id, source_record_id)` groups, zero foreign-key errors and SQLite `integrity_check=ok`.
- V7 archive SHA-256 is `fb4e6c332bdf1c0c9505ee78ad2d720d6d96d67241431a6a21ffc79ef8f6408a`.
- The PostgreSQL `edu_raw` import package remains hardened, private, resumable and idempotent.
- A new private `edu_staging` layer now exists on branch `reconstruction/edu-data-1` with normalization runs, entity candidates, field candidates, identity-match evidence and review-task structures.
- The deterministic raw→staging normalizer classifies each source row as `ready`, `needs_review`, `suppressed` or `invalid`; aggregate/statistical rows are suppressed rather than promoted as institutions.
- The normalizer performs conservative Arabic/English name normalization, basic education-type classification, Egypt coordinate validation, source-aware website extraction, contact extraction and provenance-preserving field candidate generation.
- The staging build is atomic. Canonical institution row counts are checked before and after; a change causes the operation to fail rather than silently crossing the boundary.
- A checksum-gated manual V7 recovery workflow exists. It accepts only the exact pinned V7 archive and only the dedicated `EDU_DATABASE_URL`; it has no Ask Kalam/generic database fallback.
- PostgreSQL integration CI run `34738829590` passed on 2026-09-13. It proved schema creation, unit normalization tests, two consecutive idempotent staging builds, expected candidate-state classification, source/website safeguards and canonical-row immutability.
- No live V7→staging recovery has been claimed yet because the exact preserved V7 Actions artifact/run still needs to be identified and a dedicated Edu Hub database credential must be available.
- No canonical/public promotion has occurred from this reconstruction branch.

## National registry acquisition target

Edu Hub must cover the national identity universe rather than only institutions with rich commercial profiles.

Current official control totals identified for acquisition auditing include:

- Ministry of Education / EMIS: 62,690 pre-university schools for 2025/26.
- Ministry of Social Solidarity: 48,225 nurseries from the national nursery census.
- Higher-education registries from MOHESR/SCU, plus Al-Azhar and other official institution classes.

The working acquisition target is therefore 120,000+ canonical education entities, with progressive completeness rather than rejecting legitimate institutions because optional profile fields are missing.

## Immediate next actions

1. Implement the first identity-resolution pass in `edu_staging`: deterministic exact signals first, then scored fuzzy proposals with review evidence.
2. Locate the exact preserved V7 Actions artifact and verify its tarball against the pinned SHA-256 before any live recovery.
3. Connect/create a dedicated Edu Hub PostgreSQL/Supabase database and configure `EDU_DATABASE_URL`; never use either Ask Kalam project.
4. Run the V7 recovery workflow into `edu_raw` and `edu_staging`, then inspect source-by-source candidate/review distributions before canonical promotion.
5. Start/repair the official MOE/EMIS row-level adapter and measure acquired school identities against the 62,690 official control total.
6. Continue Al-Azhar and higher-education official registry adapters; pursue MOSS nursery row-level/public-data access or institutional data-sharing in parallel.
7. Design the canonical promotion command only after identity matching quality is measured. Promotion must be explicit, reviewable and reversible.
8. Rejoin the application/runtime reconstruction only after the data contract and public projection are stable enough for the frontend to consume.

## Current blockers / unresolved dependencies

- exact historical V7 Actions artifact/run/path has not yet been identified
- dedicated live Edu Hub database/`EDU_DATABASE_URL` is not currently verifiable through the GitHub connector
- MOSS national nursery census row-level public export is not yet confirmed
- MOE/EMIS row-level extraction must be validated against the current official directory implementation
- final public brand/domain, hosting adapter, visual identity, map provider, analytics stack and production media CDN remain downstream decisions

## Non-negotiable project constraints

- Do not publish directly from raw or staging data.
- Do not use Ask Kalam databases for Edu Hub.
- Do not invent missing institution facts; unknown remains unknown.
- Do not equate paid status with verification.
- Do not auto-index every database entity or filter combination.
- Do not allow AI to silently overwrite verified canonical facts.
- Do not commit secrets.
- Keep Arabic/RTL, provenance, performance and media-rights requirements active from the beginning.
