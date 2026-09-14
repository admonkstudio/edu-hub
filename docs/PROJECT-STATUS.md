# Edu Hub Project Status

Last updated: 2026-09-14

## Current lifecycle

```text
00 Open                  APPROVED
01 Discover              APPROVED
02 Align + Audit         APPROVED FOR INTERNATIONAL SCOPE
03 Define                APPROVED — INTERNATIONAL EDUCATION ONLY
04 Content + Structure   ACTIVE — DATABASE COMPLETION
05 Creative Direction    DEFERRED
06 Design + Systemize    DEFERRED
07 Build + Connect       DEFERRED UNTIL DATABASE GATE
08 Verify + Optimize     CONTINUOUS DATA QA
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

Status: **ACTIVE — DATABASE COMPLETION GATE**

Branch: `edu-data-2-international-registry`

Canonical contracts:

- `docs/EDU-DATA-2-INTERNATIONAL-REGISTRY.md`
- `docs/DATABASE-COMPLETION-PLAN.md`

Logical data architecture:

`external source -> raw evidence -> staging/reconciliation -> reviewed canonical data -> bilingual localization -> completeness/media audit -> portable export`

The final public presentation layer is intentionally deferred until this gate is complete.

## Platform correction — 2026-09-14

Supabase is **not** part of the Edu Hub architecture.

Astro and Instatic remain possible later presentation/publishing choices, but **no current work package should optimize the database for either one yet**.

The database/research layer must be presentation-neutral, exportable and able to feed either implementation later.

## Current database completion objective

We are now finishing the **complete source-backed bilingual data architecture first**.

The current target is not a website, CMS mapping or UI. It is a trustworthy portable dataset containing:

- canonical institution identities;
- provider/group relationships;
- campus relationships;
- English and Arabic localizations;
- international eligibility evidence;
- curricula and certificates;
- accreditation/authorization relationships;
- geography and coordinates;
- contacts and official digital presence;
- admissions history;
- academic-year fee history;
- facilities/profile attributes;
- higher-education academic units and programmes;
- media references, licenses and rights state;
- field/source provenance;
- completeness, freshness and conflict state.

Missing information remains explicit. No value is invented to make a profile look complete.

## Bilingual architecture

English and Arabic are first-class and attached to the same canonical entities.

Language-neutral facts are stored once. Localized text is separate.

For localizable fields, the database must distinguish the origin/status of the localized value, for example:

- official source;
- institution source;
- verified translation;
- editorial translation;
- transliteration;
- needs review.

Official Arabic institution names are preferred. If no official Arabic name is available, any transliteration/editorial form must be explicitly marked instead of being treated as official.

Database completeness is measured separately for factual completeness, English localization, Arabic localization and media completeness.

## Authoritative evidence acquired / prepared

### International Baccalaureate

- Live Egypt-filtered IB directory snapshot contains **54 school rows** across three pages.
- The IB country summary reported **55 schools** on the same date; the discrepancy is preserved as a review flag.
- Checked-in evidence preserves names, programmes and listed languages.
- Public/state ownership checks are being resolved; public/state rows are excluded from active scope.

### French homologation

- Official French 2026–2027 evidence is captured for **17 Egypt source rows** with UAI identifiers, city, levels, homologated classes and stream limitations.

### German recognition

- Official April 2026 KMK evidence is captured for **4 recognized German schools abroad in Egypt**.

### Higher education

- Current SCU evidence is captured for **9 recognized foreign university branches**.
- AUC is captured as an eligible international independent university using current MSCHE accreditation plus institutional evidence.
- MOHESR reconciliation remains review-only where regulator sources disagree.

### Current deterministic authoritative seed

The deterministic seed currently contains **85 source rows** before further ownership filtering and cross-source deduplication:

- 54 IB source rows;
- 17 French rows;
- 4 German rows;
- 9 SCU foreign-branch rows;
- 1 AUC row.

The project does **not** claim these are 85 unique institutions.

## Supporting discovery/enrichment sources

### Edarabia

Edarabia is registered as an approved supporting/commercial directory source.

Use it for:

- discovering institutions/campuses missing from stronger source lists;
- address/website/contact leads;
- curriculum and fee leads;
- profile-field coverage leads;
- media discovery leads.

Do not use it by itself to establish international eligibility, accreditation, regulatory status or final canonical fees. Important claims require stronger corroboration. Ratings/reviews are not canonical facts. Images remain discovery-only unless reuse rights are established independently.

### Other active supporting sources

- British Council Partner Schools;
- Overture Maps;
- OpenStreetMap/Wikidata;
- historical V7 archive;
- institution websites as primary enrichment sources once identity is established.

## Import and identity safety

`tools/data-acquisition/international/prepare_import_package.py` builds a provenance-safe package containing source definitions, source-shaped raw records, staging candidates, reviewed-media metadata and checksums.

The package creates zero canonical institutions, performs zero automatic merges and creates zero public projection rows.

`tools/data-acquisition/international/plan_identity_reconciliation.py` creates review-only duplicate/campus proposals. Auto-accept is prohibited.

## Media state

Automatic Commons discovery records license/provenance candidates but never authorizes them automatically.

A reviewed seed currently contains **5 publication-safe Wikimedia assets** for AIS Egypt, British International School Cairo, Cairo English School and two AUC campus views, with reuse basis and attribution metadata recorded.

Institution websites, social channels and commercial directories may provide media discovery leads, but their images are not publication-safe by default.

Every eligible institution must eventually have one explicit media state, such as publication-safe asset available, rights-unreviewed candidate only, no media found, or `placeholder_required`.

## Current CI state

The core EDU-DATA-2 contract, import package, review-only identity proposal pipeline and relational schema reference have passed CI in prior runs.

## Database completion work packages

### D2.1 — Candidate universe completion

Collect the widest defensible international-school/university candidate universe from authoritative and supporting sources and measure source overlap/gaps.

### D2.2 — Identity and campus reconciliation

Deduplicate cross-source identities, separate institutions from campuses, resolve provider/group relationships, preserve aliases and queue ambiguous cases.

### D2.3 — EN/AR canonical localization

Complete English and Arabic names and other localized profile text with source/origin/status metadata.

### D2.4 — Profile enrichment

Systematically attempt address, coordinates, website/contact, curricula, grades/ages, languages, accreditation, admissions, current/historical fees, facilities and higher-education programmes for every eligible institution.

### D2.5 — Media completion

Discover, reference and review useful logos/campus/facility media while preserving rights state and generating explicit placeholder requirements where necessary.

### D2.6 — Completeness/conflict audit

Measure field coverage, freshness, EN/AR localization coverage, unresolved conflicts and media state per institution.

### D2.7 — Portable database/export freeze

Produce presentation-neutral canonical exports plus provenance, media manifest, review/conflict report and completeness report. This is the gate before choosing Astro vs Instatic.

## Immediate next actions

1. Expand the candidate universe using Edarabia, British Council, Cognia/American accreditation sources, MOHESR and other approved source families.
2. Reconcile all authoritative and supporting identities into institution/campus candidates.
3. Complete the IB private/state ownership gate.
4. Complete SCU/MOHESR foreign-university reconciliation and lifecycle status.
5. Build the bilingual EN/AR canonical localization layer, including localization origin/status.
6. Enrich every eligible institution from its official site and primary documents.
7. Version admissions and fees by academic year/cycle rather than overwriting.
8. Expand geography and coordinates through institution sources plus Overture/OSM cross-checking.
9. Continue media discovery and rights review; record a terminal media state for every institution.
10. Produce the first full field-coverage, bilingual-coverage, freshness/conflict and media-coverage reports.
11. Generate a deterministic portable export.
12. Only after steps 1–11 are complete, evaluate Astro vs Instatic and design the public presentation.

## Explicitly deferred during database completion

- Astro vs Instatic selection;
- final website architecture;
- card/listing/profile UI;
- filters/search UX;
- public CMS collection mapping;
- visual design system;
- frontend deployment;
- public SEO page generation.

## Non-negotiable constraints

- Do not reintroduce full Egyptian public-school/university coverage without a new owner decision.
- Do not confuse exam-centre/partner status with international-school eligibility.
- Do not infer international status from branding words.
- Do not let a commercial directory establish eligibility or override stronger evidence.
- Do not invent institution facts, fees, rankings, accreditations or admissions data.
- Do not publish media without a recorded rights basis.
- Do not use Supabase for Edu Hub.
- Do not import Edu Hub data into Ask Kalam infrastructure.
- Do not publish raw/staging evidence directly.
- Do not let Astro or Instatic limitations distort the canonical database during the database-completion gate.
- Keep English/Arabic parity, provenance, portability and data quality active throughout.
