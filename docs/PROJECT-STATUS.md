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

Logical data architecture:

`external source -> raw evidence -> staging/reconciliation -> reviewed canonical data -> public projection -> Astro or Instatic`

No public page may depend on a live third-party source after acquisition.

## Platform correction — 2026-09-14

Supabase is **not** part of the Edu Hub architecture.

Approved implementation choices are now:

- **Astro-first** for a coded, SEO-sensitive directory/application; or
- **Instatic-first** for a self-hosted CMS/static-publishing implementation.

A hybrid Astro + Instatic architecture is not the default and should only be introduced if there is a demonstrated product need and one canonical data owner is defined.

The existing relational SQL schema remains the canonical reference model. Physical runtime storage may be Instatic SQLite, directly attached PostgreSQL, or owned static/generated data for Astro. No Supabase database/auth/storage/RLS/function dependency is allowed.

## Completed scope reset / cleanup

### Source of truth

- `README.md`, `AGENTS.md`, `docs/PLATFORM.md`, `docs/PROJECT-BRIEF.md`, `docs/PROJECT-DECISIONS.md`, `docs/PROJECT-STATUS.md` and the milestone contract reflect the international-only scope and no-Supabase platform direction.
- International scope states are explicit: `candidate`, `eligible`, `excluded`, `needs_review`.
- International eligibility must be evidenced; names/marketing language cannot establish eligibility.
- British Council attached/partner status, Overture, OSM, V7 and commercial directories are supporting/discovery evidence only.

### Clean relational data foundation

`infra/owned-data/005_international_registry.sql` extends the evidence architecture with:

- providers/groups;
- bilingual institution localizations;
- international eligibility + evidence;
- locations and campuses;
- curricula/certificates/languages;
- accreditation/authorization bodies and institution accreditations;
- contacts;
- academic-year fee schedules and fee items;
- admissions cycles;
- academic units and programmes;
- media license/creator/attribution/rights-evidence metadata.

CI applies migrations `001`, `004`, and `005` to a clean PostgreSQL/PostGIS test service as a schema/reference validation gate. This does not imply PostgreSQL/Supabase is required by the final runtime.

## Authoritative evidence acquired / prepared

### International Baccalaureate

- Live Egypt-filtered IB directory snapshot contains **54 school rows** across three pages.
- The IB country summary reported **55 schools** on the same date; the 54/55 discrepancy is preserved as a review flag.
- Checked-in evidence preserves names, IB programmes and listed languages.
- Ownership/school-type evidence is being resolved; public/state rows are excluded from active scope.

### French homologation

- Official French 2026–2027 homologation evidence is captured for **17 Egypt source rows** with UAI identifiers, city, levels, homologated classes and stream limitations.

### German recognition

- Official April 2026 KMK evidence is captured for **4 recognized German schools abroad in Egypt**.

### Higher education

- Current SCU evidence is captured for **9 recognized foreign university branches**.
- AUC is independently captured as an eligible international independent university using current MSCHE accreditation plus institutional evidence.
- MOHESR reconciliation remains review-only where regulator sources disagree.

### Current deterministic authoritative seed

The deterministic authoritative seed currently contains **85 source rows** before further ownership filtering and cross-source deduplication:

- 54 IB source rows;
- 17 French rows;
- 4 German rows;
- 9 SCU foreign-branch rows;
- 1 AUC row.

The project does not claim these are 85 unique institutions.

## Supporting discovery/enrichment sources

### Edarabia

Edarabia is now registered as an approved **commercial directory supporting source**.

Its Egypt school pages expose useful discovery/enrichment fields such as institution names, addresses, curriculum labels, listed tuition fees, location information, photos/videos and reviews.

Policy:

- use for candidate discovery and missing-field leads;
- use for cross-checking addresses/websites/curricula/fee leads;
- do not let it establish international eligibility, accreditation or regulatory status;
- corroborate important facts with regulator/accreditor/official institution sources before canonical promotion;
- ratings/reviews are not canonical facts;
- images remain discovery-only unless independent reuse rights are established.

## Import and identity safety

`tools/data-acquisition/international/prepare_import_package.py` builds a provenance-safe package containing source definitions, source-shaped raw records, staging candidates, reviewed-media metadata and checksums.

The package creates zero canonical institutions, performs zero automatic merges and creates zero public projection rows.

`tools/data-acquisition/international/plan_identity_reconciliation.py` creates review-only duplicate/campus proposals. Auto-accept is prohibited.

## Media state

Automatic Commons discovery records license/provenance candidates but never authorizes them automatically.

A reviewed seed currently contains **5 publication-safe Wikimedia assets** for AIS Egypt, British International School Cairo, Cairo English School and two AUC campus views, with reuse basis and attribution metadata recorded.

Institution websites, social channels and commercial directories may provide media discovery leads, but their images are not publication-safe by default.

If no safe image exists, the public UI uses a designed placeholder containing the institution's English name.

## Current CI state

The core EDU-DATA-2 contract, import package, review-only identity proposal pipeline and clean relational schema reference have passed CI in prior runs. New source/platform documentation changes continue to use the same validation branch.

## Runtime / infrastructure state

There is **no Supabase provisioning task** for Edu Hub.

The project already has an Instatic self-hosted direction available, and Astro remains the coded frontend alternative.

The next runtime step is not database provisioning. It is to decide whether the real product should be **Instatic-first or Astro-first**, then create the narrow import/publication adapter for that target.

## Immediate next actions

1. Audit the existing Instatic deployment against the required institution collection model, bilingual content, media handling, search/filter needs and static publication workflow.
2. Decide Instatic-first vs Astro-first using that audit; do not introduce both without a clear need.
3. Build the target-specific import adapter from the clean EDU-DATA-2 package.
4. Continue IB private/state ownership verification and cross-source institution/campus reconciliation.
5. Reconcile MOHESR foreign-university evidence against SCU.
6. Ingest British Council Partner Schools as discovery/contact evidence only.
7. Add Cognia/other American accreditation evidence and verify school models from primary sources.
8. Use Edarabia systematically as a discovery/completeness source to find missing institutions and profile fields, then corroborate them against primary sources.
9. Enrich eligible institutions from official websites: campuses, coordinates, contacts, curricula, grades/ages, admissions, current fees, facilities, programmes and source-backed descriptions.
10. Continue rights-safe media discovery/review and prepare the first reviewed public projection for the chosen Astro/Instatic runtime.

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
- Keep Arabic/RTL, provenance, portability, performance and SEO requirements active.
