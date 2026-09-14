# Edu Hub Project Status

Last updated: 2026-09-14

## Current lifecycle

```text
00 Open                  APPROVED
01 Discover              APPROVED
02 Align + Audit         APPROVED FOR INTERNATIONAL SCOPE
03 Define                APPROVED — INTERNATIONAL EDUCATION ONLY
04 Content + Structure   IN PROGRESS — INTERNATIONAL REGISTRY
05 Creative Direction    DEFERRED DURING DATA FOUNDATION
06 Design + Systemize    DEFERRED DURING DATA FOUNDATION
07 Build + Connect       IN PROGRESS — EDU-DATA-2
08 Verify + Optimize     CONTINUOUS
09 Review + Launch       NOT STARTED
10 Handoff + Learn       NOT STARTED
```

## Current product state

Edu Hub is an Admonk-owned independent bilingual education discovery and knowledge platform focused initially on **international education in Egypt**.

Primary audience:

1. Parents
2. Students

Active Phase 1 includes private/independent international schools, private/independent IB World Schools, recognized foreign-national/international school models, recognized foreign university branches, internationally chartered/accredited independent higher-education institutions whose international status is substantive, and their campuses/eligible early-years sections.

Explicitly out of active scope:

- Egyptian public schools;
- Egyptian public universities;
- the 62,690-school EMIS national target;
- the 48,225-nursery MOSS national target;
- ordinary language schools/exam centres without sufficient international-status evidence;
- Egyptian universities whose only international dimension is a partnership, exchange, dual degree or validated programme.

Historical national-registry work remains preserved on `edu-data-1-national-registry` and in Git history. It is not an active product dependency.

## Active milestone

**EDU-DATA-2 — Egypt International Education Registry**

Status: **ACTIVE**

Branch: `edu-data-2-international-registry`

Canonical contract: `docs/EDU-DATA-2-INTERNATIONAL-REGISTRY.md`

Architecture:

`external source -> edu_raw -> edu_staging -> edu_core -> public projection -> website`

No public page may depend on a live third-party source after acquisition.

## Completed scope reset / cleanup

### Source of truth

- `README.md`, `docs/PROJECT-BRIEF.md`, `docs/PROJECT-DECISIONS.md`, `docs/PROJECT-STATUS.md` and the milestone contract now reflect the international-only scope.
- International scope states are explicit: `candidate`, `eligible`, `excluded`, `needs_review`.
- International eligibility must be evidenced; names/marketing language cannot establish eligibility.
- British Council attached/partner status, Overture, OSM, V7 and commercial directories are supporting/discovery evidence only.

### Clean relational database foundation

`infra/owned-data/005_international_registry.sql` extends the evidence architecture with:

- providers/groups;
- bilingual institution localizations;
- international eligibility + evidence;
- locations and campuses with PostGIS;
- curricula/certificates/languages;
- accreditation/authorization bodies and institution accreditations;
- contacts;
- academic-year fee schedules and fee items;
- admissions cycles;
- academic units and programmes;
- media license/creator/attribution/rights-evidence metadata.

CI applies migrations `001`, `004`, and `005` to a clean PostGIS PostgreSQL service and asserts the international schema contract.

## Authoritative evidence acquired / prepared

### International Baccalaureate

- Live Egypt-filtered IB directory snapshot contains **54 school rows** across three pages.
- The IB country summary reported **55 schools** on the same date; the 54/55 discrepancy is preserved as a review flag rather than fabricating a record.
- The checked-in snapshot preserves names, IB programmes and listed languages for all 54 rows.
- All 54 remain `candidate` until each school type/ownership is confirmed; public/state schools will be excluded from the active scope.
- A live acquisition adapter remains available, but IB blocks GitHub-hosted direct Python requests with HTTP 403; deterministic CI therefore validates dated source evidence rather than treating the hosted-runner response as source absence.

### French homologation

- Official French 2026–2027 homologation evidence is captured for **17 Egypt source rows** with UAI identifiers, city, levels, homologated classes and stream limitations.
- These rows are strong international-programme eligibility evidence, with any French-stream-only limitation retained explicitly.

### German recognition

- Official April 2026 KMK evidence is captured for **4 recognized German schools abroad in Egypt**, including recognition dates.

### Higher education

- Current SCU evidence is captured for **9 recognized foreign university branches**.
- AUC is independently captured as an `eligible` international independent university using current MSCHE institutional accreditation plus AUC's Egypt/US institutional framework evidence.
- MOHESR reconciliation remains to be completed; any branch present in one regulator source but absent in another remains review-only.

### Current deterministic authoritative seed

`tools/data-acquisition/international/build_authoritative_seed.py` currently builds **85 source rows**:

- 54 IB candidate source rows;
- 17 French eligible source rows;
- 4 German eligible source rows;
- 9 SCU foreign-branch eligible source rows;
- 1 AUC eligible source row.

Current source-row state before cross-source identity reconciliation:

- **31 eligible source rows**;
- **54 candidate source rows**;
- unique institution count intentionally not claimed yet because French/German/IB overlaps and campus relationships still require reconciliation.

## Import and identity safety

`tools/data-acquisition/international/prepare_import_package.py` now converts the deterministic seed into a provenance-safe package containing:

- source definitions;
- 85 source-shaped raw records with stable hashes;
- 85 staging candidates;
- reviewed media metadata;
- checksums/manifest.

The package creates **zero canonical institutions**, performs **zero merges** and creates **zero public projection rows**.

`tools/data-acquisition/international/plan_identity_reconciliation.py` creates cross-source duplicate/campus proposals using conservative name evidence. Every proposal is `needs_review`; auto-accept is prohibited.

## Media state

Media publication remains rights-aware.

Automatic Commons discovery records license/provenance candidates but never authorizes them automatically. A separate reviewed seed currently contains **5 publication-safe Wikimedia assets** whose Commons descriptions identify the institution/campus and whose reuse basis was recorded:

- American International School in Egypt — campus image — CC BY-SA 4.0;
- British International School, Cairo — image released to public domain;
- Cairo English School — CC BY-SA 4.0;
- AUC Tahrir/Downtown — CC BY-SA 3.0/compatible source declarations;
- AUC New Cairo — CC BY-SA 3.0.

Attribution/share-alike obligations are retained in the media metadata. Institution website/social media may be stored as discovery candidates but is not publication-safe without a defensible rights basis. When no safe image exists, the UI uses a designed placeholder with the institution's English name.

## Current CI state

The prior complete EDU-DATA-2 run at commit `3dfe62f5652001c51c87eda1bb1d1d9487657486` passed successfully.

The newest run for the import-package + review-only identity proposal contract is currently being validated. Do not treat it as green until all jobs finish.

## Infrastructure state / only provisioning blocker

A dedicated Edu Hub PostgreSQL/Supabase project still does **not** exist.

The connected Supabase organization currently exposes Ask Kalam projects only; those projects must not receive Edu Hub data.

The schema, authoritative seed, reviewed media metadata and import package are ready to move into a dedicated project after explicit organization selection and cost approval.

## Immediate next actions

1. Finish/repair the current EDU-DATA-2 CI run if needed.
2. Provision a **dedicated Edu Hub Supabase/PostgreSQL project** after the owner selects the Supabase organization and explicitly approves the reported provisioning cost.
3. Apply migrations `001`, `004`, `005` to that clean project.
4. Import the 85 raw/staging source rows and reviewed-media metadata; do not create canonical identities until reconciliation review.
5. Complete cross-source institution/campus reconciliation and resolve the IB public/private ownership gate.
6. Reconcile MOHESR foreign-university evidence against the SCU set.
7. Ingest the September 2026 British Council Partner Schools PDF as discovery/contact evidence only.
8. Add Cognia/other American accreditation evidence and verify the international-school model from official institution sources.
9. Enrich eligible institutions from official websites: campuses, coordinates, contacts, curricula, grades/ages, admissions, current fees, facilities, academic units/programmes and source-backed descriptions.
10. Match eligible/candidate identities to Overture/OSM/Wikidata/V7 for coordinates, aliases and supporting evidence without allowing those sources to establish eligibility alone.
11. Continue rights-safe media discovery/review and build the first representative public projection only after canonical identity review.

## Non-negotiable constraints

- Do not reintroduce full Egyptian public-school/university coverage without a new owner decision.
- Do not confuse exam-centre/partner status with international-school eligibility.
- Do not infer international status from branding words.
- Do not turn foreign partnerships into international-university identities.
- Do not invent institution facts, fees, rankings, accreditations or admissions data.
- Do not publish media without a recorded rights basis.
- Do not import Edu Hub data into Ask Kalam infrastructure.
- Do not publish directly from `edu_raw` or `edu_staging`.
- Keep Arabic/RTL, provenance, portability, performance and SEO requirements active.
