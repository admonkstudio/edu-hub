# Edu Hub Project Status

Last updated: 2026-09-15

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

## Product and active milestone

Edu Hub is an Admonk-owned independent bilingual education discovery and knowledge platform focused initially on **international education in Egypt** for parents and students.

**Active milestone:** `EDU-DATA-2 — Egypt International Education Registry`

**Branch:** `edu-data-2-international-registry`

Phase 1 includes private/independent international schools, private/independent IB World Schools, recognized foreign-national/international-school models, recognized foreign university branches and internationally chartered/accredited independent higher-education institutions whose international status is substantive.

Egyptian public schools/universities, the historical EMIS/MOSS national targets and ordinary language/exam-centre institutions without sufficient international-status evidence remain out of active scope.

Canonical contracts:

- `docs/EDU-DATA-2-INTERNATIONAL-REGISTRY.md`
- `docs/DATABASE-COMPLETION-PLAN.md`
- `docs/SOURCE-USAGE-POLICY.md`

Logical data path:

`external source -> raw evidence -> staging/reconciliation -> reviewed canonical data -> bilingual localization -> completeness/media audit -> portable export`

Supabase is not part of Edu Hub. Astro vs Instatic remains deferred until the database gate is complete.

## Canonical reference architecture

Reference migrations:

- `001_raw_archive.sql` — source-shaped evidence archive;
- `004_national_registry_layers.sql` — staging/reconciliation and identity foundations;
- `005_international_registry.sql` — international eligibility, providers, campuses, curricula, accreditation, contacts, fees/admissions and higher-ed structure;
- `006_bilingual_completion.sql` — EN/AR provenance, aliases, levels, facilities, admissions requirements, media localization, evidence assertions and completeness metrics;
- `007_school_divisions.sql` — first-class pre-university curriculum/language/phase divisions below institution/campus identity.

The reviewed hierarchy is:

`provider -> institution -> campus -> school division`

Division-specific accreditation, curriculum, admissions, fees and contacts are not flattened onto an entire institution. `007_school_divisions.sql` passed clean-schema and idempotency CI in School Division Schema run **34898999314**.

## Current accepted source universe

### Foundational source universe — 96 rows

Source families remain:

- 54 IB Egypt rows;
- 11 UK DfE British Schools Overseas rows;
- 17 French homologation rows;
- 4 German KMK rows;
- 9 SCU foreign-university-branch rows;
- 1 AUC/MSCHE row.

The original deterministic foundational builder remains reproducibly **40 eligible / 53 candidate / 3 excluded**.

Four accepted incremental IB detail batches (`batch2` through `batch5`) overlay **20 exact existing IB source rows** without changing source IDs or ordering.

**Current accepted 96-row state after all incremental IB overlays:**

- **60 eligible**;
- **33 candidate**;
- **3 excluded**.

These are source records, not a claim of 96 unique institutions.

### Accreditor-expanded D2.1 universe — 106 rows

Supporting strong accreditor evidence adds:

- 6 CIS Egypt accreditation rows;
- 4 Cognia 2026–2027 milestone rows.

**Current accepted combined state after all incremental IB overlays:**

- **60 eligible**;
- **43 candidate**;
- **3 excluded**.

English source-row naming evidence: **106/106**.
Arabic source-row naming evidence: **9/106**.
Pre-reconciliation Arabic-name gaps: **97**.

No full-universe unique institution count is claimed. Fuzzy matching never authorizes a canonical merge.

## International Baccalaureate progress

The captured Egypt directory contains **54 source rows**.

The historical 2026-09-14 country-summary snapshot reported 55 while the directory returned 54; that discrepancy remains preserved as historical evidence. A current 2026-09-15 observation of the official IB Egypt country page reports **54 IB World Schools**, matching the captured directory count. Historical source observations are preserved rather than rewritten.

**Accepted IB ownership/detail decisions: 32 of 54 source rows**

- **29 PRIVATE / eligible**;
- **3 STATE / excluded**;
- **22 remain unresolved by direct ownership/detail review**.

Foundational detail snapshots account for 12 decisions. Incremental batches 2–5 add 20 further exact-row PRIVATE decisions.

The scalable incremental path is implemented in `tools/data-acquisition/international/apply_ib_detail_batches.py`. It:

- discovers checked-in `ib-detail-evidence-*-batch*.json` files in deterministic filename order;
- requires exact identities already present in the 54-row IB directory snapshot;
- rejects the same identity appearing in multiple incremental batches;
- upgrades only unresolved candidate rows using reviewed current detail evidence;
- preserves every `source_record_id` and source ordering;
- keeps the foundational snapshot independently reproducible;
- performs zero identity merge, canonical database write or public promotion.

Incremental IB Details run **34901104277** passed with batches 2–5 and revalidated the upgraded 96-row universe, 106-row accreditor-expanded universe, D2.2 identity decisions and reviewed-canonical draft safety contract.

## Other authoritative/source-family progress

### UK DfE / British Schools Overseas

- 11 current Egypt BSO records from the list updated 2026-08-26.
- All 11 have matched GIAS details with URNs, official names, open status and available address/age/contact/inspection fields.
- BSO is strong British/international-school-model evidence; private/independent ownership remains a separate gate.

### French and German

- French 2026–2027 homologation: **17 Egypt source rows** with UAI identifiers and scope details.
- German KMK: **4 recognized Egypt schools**.

### CIS and Cognia

- CIS: **6 current/recent Egypt accreditation rows**.
- Cognia: **4 Egypt 2026–2027 milestone rows**.
- Accreditor evidence strengthens international-model evidence but does not bypass identity/ownership review.

### Higher education

- SCU: **9 recognized foreign university branches**.
- AUC: eligible through current MSCHE plus institutional evidence.
- SCU/MOHESR lifecycle/identity reconciliation remains pending.

## D2.1 — Candidate universe completion

Status: **IN PROGRESS / PRINCIPAL AUTHORITATIVE-ACCREDITOR EXPANSION COMPLETE**

The pipeline keeps the foundational 96-row build independently reproducible while applying source-dated ownership/detail evidence as exact-identity overlays. The accepted upgraded source state is currently 96 rows at **60/33/3** and 106 rows at **60/43/3**.

British Council Partner Schools remains the next broad supporting discovery source. The September 2026 Egypt PDF is **19 pages** and is browser-accessible. GitHub-hosted direct Python retrieval returns HTTP 403, so the approved adapter supports a browser/local PDF path. Partner/attached-centre status remains discovery/contact evidence only and never grants international eligibility by itself.

## D2.2 — Identity, campus and division reconciliation

Status: **ACTIVE — FIRST REVIEWED IDENTITIES, DIVISIONS AND CURRENT CAMPUS EVIDENCE MATERIALIZED AS DRAFTS**

Current identity package:

- **9 reviewed identity groups**;
- **20 source memberships**;
- **7 `same_institution` groups**;
- **2 `same_institution_with_division_scoped_evidence` groups**;
- **4 reviewed curriculum-division drafts**;
- **86 source rows remain in the explicit identity-review queue**.

Reviewed institutional groups currently cover Narmer American College, The British International School Cairo, Cairo American College, Cairo English School, Modern English School Cairo, NCBIS, Evolution International School, El Alsson and Misr Language Schools.

El Alsson and Misr Language Schools are one institutional identity each with separately scoped curriculum divisions instead of duplicated institutions.

`build_reviewed_canonical_artifacts.py` produces deterministic UUIDv5 reviewed drafts only:

- 9 institution drafts;
- 20 source memberships;
- 4 division drafts;
- 0 automatic merges;
- 0 canonical database writes;
- 0 runtime mutation;
- 0 public projection.

### Current-campus review

A separate source-backed campus package now reviews **at least one current operating location for all 9 reviewed institutional identities**.

`tools/data-acquisition/international/build_reviewed_campus_artifacts.py` uses the same deterministic UUIDv5 namespace as the identity draft builder and emits:

- **9 reviewed current-campus draft records**;
- **9 campus-structure review records**;
- exact alignment with all 9 reviewed institution draft IDs;
- **0 campus structures marked complete**;
- **0 records claiming that additional current campuses have been ruled out**;
- **0 inferred additional campuses**;
- **0 canonical campus rows written**;
- **0 runtime database mutation**;
- **0 public projection**.

The campus structure state is deliberately `at_least_one_current_campus_reviewed_structure_not_exhaustive`. This replaces the earlier blanket `not_yet_reviewed` state with positive current-location evidence while still refusing to pretend the full campus topology is known.

Current campus evidence includes the NewGiza campus for El Alsson, the shared Cairo-El Fayoum Desert Road campus evidence for Misr Language Schools, and source-backed current locations for the other seven first-reviewed identities. Historical locations such as El Alsson's pre-2017 site are not silently presented as current campuses.

Campus Review run **34901485863** passed the complete campus evidence/alignment/safety contract.

## D2.3 — EN/AR localization

Status: **ARCHITECTURE IMPLEMENTED / CONTENT INCOMPLETE**

A first institution-origin Arabic evidence package contains 4 names: 2 current official Arabic-name rows and 2 historical institution-origin rows requiring current revalidation. Localization Evidence run **34897451220** passed.

Official Arabic names are preferred. Transliteration/editorial Arabic may be used only with explicit non-official origin/status.

## D2.4 — First-party profile enrichment

Status: **STARTED / FIRST HIGH-PRIORITY BATCH GREEN**

Current evidence package covers 8 high-priority institutions:

- website 8/8;
- location 7/8;
- contact 6/8;
- admissions 6/8;
- curriculum/programme 6/8;
- education range 4/8;
- facilities 2/8;
- provider/group 1/8;
- founding history 1/8;
- regulatory identifiers/status 2/8.

Official Site Enrichment run **34898574887** passes. No current fee schedule is inferred and historical fee documents are not promoted as current fees.

## D2.5 — Media

Status: **STARTED**

A reviewed seed contains 5 publication-safe Wikimedia assets with rights/attribution metadata. Institution/commercial-site imagery remains discovery-only unless a defensible reuse basis exists. Every reviewed institution must eventually receive a terminal media state, including `placeholder_required` when needed.

## D2.6 — Completeness/conflict audit

Status: **ARCHITECTURE IMPLEMENTED / FULL RECONCILIATION-AWARE AUDIT PENDING**

Factual, EN, AR, media and unresolved-conflict completeness are modeled independently. Full reporting follows broader identity/campus review and enrichment.

## D2.7 — Portable export freeze

Status: **NOT STARTED**

The final portable package will contain canonical identities, campuses/divisions, bilingual localizations, source/evidence references, time-sensitive admissions/fee history, media/rights, conflict state and completeness metrics without requiring Astro, Instatic or Supabase.

## Source-use boundaries

- **Edarabia:** reference-only discovery under current terms; no systematic copying/import.
- **British Council:** discovery/contact evidence only; browser/local PDF route approved where hosted retrieval is blocked.
- **CIS/Cognia:** recognized accreditor evidence; ownership/scope gates remain separate.
- **Institution websites:** primary factual/localization evidence; no automatic media-republication rights.
- **Wikimedia Commons:** asset-by-asset identity and rights review.
- **OSM/Overture:** geography/support evidence with applicable licensing/attribution.

## Current CI gates

Key accepted runs:

- Foundational Core International Registry: **34900305899** — green;
- Foundational Accreditor Expansion: **34900289955** — green;
- IB Batch2 compatibility pipeline: **34900583919** — green;
- Scalable Incremental IB Details through batches 2–5: **34901104277** — green; current 96-row state **60/33/3**, current 106-row state **60/43/3**;
- Localization Evidence: **34897451220** — green;
- Official Site Enrichment: **34898574887** — green;
- School Division Schema: **34898999314** — green;
- Identity Review + deterministic draft materialization: **34900009375** — green;
- Current Campus Review: **34901485863** — green for 9 reviewed current-campus evidence drafts with 0 exhaustive campus claims.

## Immediate next actions

1. Continue direct IB PRIVATE/STATE verification for the remaining **22** unresolved IB directory rows through the scalable incremental overlay pipeline.
2. Continue D2.2 cross-source identity review beyond the first 20 memberships, prioritizing obvious overlaps and true parent/campus relationships.
3. Continue campus-structure research beyond the first evidenced location per reviewed identity; only mark topology complete when sources support that conclusion.
4. Acquire/process the 19-page British Council PDF through the permitted browser/local path; keep its rows at discovery/contact evidence level.
5. Expand official-site D2.4 enrichment from 8 institutions toward every eligible reviewed identity.
6. Add current fee schedules only from current official sources and retain older schedules historically.
7. Expand official Arabic names and revalidate historical Arabic evidence.
8. Reconcile SCU/MOHESR foreign-university identities and lifecycle state.
9. Expand geography/coordinates using institution evidence plus Overture/OSM cross-checks.
10. Continue media-rights review and assign terminal media state per reviewed identity.
11. Produce the first canonicalization-aware factual/EN/AR/media completeness report.
12. Freeze deterministic portable export only after those review gates are satisfied.

## Deferred during database completion

- Astro vs Instatic selection;
- final website architecture/UI/search/filter design;
- public CMS mapping;
- visual design system;
- frontend deployment;
- public SEO page generation.

## Non-negotiable constraints

- no public-school/university scope expansion without a new owner decision;
- no exam-centre/partner shortcut to international eligibility;
- no eligibility inference from branding words;
- no commercial-directory override of authoritative evidence;
- no unsupported facts, fees, rankings, accreditations or admissions data;
- no publication of media without recorded rights basis;
- no Supabase for Edu Hub and no Ask Kalam infrastructure/data mixing;
- no raw/staging publication;
- no automatic identity merge from fuzzy matching;
- no exhaustive campus claim from one known address;
- keep EN/AR parity, provenance, portability and data-quality review active throughout.
