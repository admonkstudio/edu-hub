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

Phase 1 includes private/independent international schools, private/independent IB World Schools, recognized foreign-national/international school models, recognized foreign university branches and internationally chartered/accredited independent higher-education institutions whose international status is substantive.

Egyptian public schools/universities, the historical EMIS/MOSS national targets and ordinary language/exam-centre institutions without sufficient international-status evidence remain out of active scope.

Canonical contracts:

- `docs/EDU-DATA-2-INTERNATIONAL-REGISTRY.md`
- `docs/DATABASE-COMPLETION-PLAN.md`
- `docs/SOURCE-USAGE-POLICY.md`

Logical data path:

`external source -> raw evidence -> staging/reconciliation -> reviewed canonical data -> bilingual localization -> completeness/media audit -> portable export`

Supabase is not part of Edu Hub. Astro vs Instatic remains deferred until the database gate is complete.

## Canonical reference architecture

The reference model is now composed of:

- `001_raw_archive.sql` — owned source-shaped evidence archive;
- `004_national_registry_layers.sql` — staging/reconciliation and canonical identity foundations;
- `005_international_registry.sql` — international eligibility, providers, campuses, curricula, accreditation, contacts, fees/admissions and higher-ed structure;
- `006_bilingual_completion.sql` — EN/AR localization provenance, aliases, education levels, facilities, admission requirements, media localization, evidence assertions and independent completeness metrics;
- `007_school_divisions.sql` — first-class pre-university curriculum/language/phase divisions below institution/campus identity.

### School-division correction

Current evidence from institutions such as Misr Language Schools and El Alsson proved that the same canonical school/campus can contain separate British, American, French, IB or other sections with section-specific accreditation, admissions, fees and contacts.

Therefore a curriculum division is **not** automatically a separate institution and division-specific authorization must **not** be flattened onto the whole institution.

The reference model now supports:

`provider -> institution -> campus -> school division`

with bilingual division localizations plus division-scoped curricula, certificates, languages, accreditations, level/grade offerings, contacts, admissions, fees and completeness metrics.

`infra/owned-data/007_school_divisions.sql` passed clean-schema and idempotency CI in **EDU-DATA-2 School Division Schema run 34898999314**.

The durable architecture decision is recorded in `docs/PROJECT-DECISIONS.md`.

## Source universe and eligibility state

### Deterministic authoritative/strong base — 96 source rows

- 54 IB Egypt rows;
- 11 UK DfE British Schools Overseas rows;
- 17 French homologation rows;
- 4 German KMK rows;
- 9 SCU foreign-university-branch rows;
- 1 AUC/MSCHE row.

Current source-row states:

- **40 eligible**;
- **53 candidate**;
- **3 excluded**.

These are source records, not 96 claimed unique institutions.

### Accreditor-expanded D2.1 universe — 106 source rows

Separate current/recent accreditor evidence adds:

- 6 CIS Egypt accreditation rows;
- 4 Cognia 2026–2027 milestone rows.

Combined states:

- **40 eligible**;
- **63 candidate**;
- **3 excluded**.

English source-row naming evidence: **106/106**.
Arabic source-row naming evidence: **9/106**.
Source-row Arabic-name gaps before identity reconciliation: **97**.

No canonical identity count is claimed yet and no automatic merge occurs.

## Major source-family progress

### IB

- 54 Egypt directory rows captured.
- IB country summary reported 55 on the same snapshot date; conflict remains explicit.
- 12 detail/ownership decisions are now source-backed across dated snapshots:
  - **9 PRIVATE / eligible**;
  - **3 STATE / excluded**.
- New current private checks include Evolution International School - NewGiza, Narmer American College, Cairo American College, Cairo English School and New Cairo British International School.
- Incremental detail evidence keeps its own source date rather than overwriting the older snapshot.

### UK DfE / British Schools Overseas

- 11 current Egypt BSO records from the list updated 2026-08-26.
- All 11 have matched GIAS details with URNs, official names, open status and available address/age/contact/inspection fields.
- BSO is strong British/international-school-model evidence; the private/independent ownership gate remains separate.

### French and German

- French 2026–2027 homologation: **17 Egypt source rows** with UAI identifiers and scope details.
- German KMK: **4 recognized Egypt schools**.

### CIS and Cognia

- CIS seed: **6 current/recent Egypt accreditation rows**.
- Cognia 2026–2027 milestone seed: **4 Egypt rows** reaching a 25-year accreditation milestone.
- CIS/Cognia evidence strengthens international-model/accreditation evidence but does not bypass the ownership/scope review rules.

### Higher education

- SCU: **9 recognized foreign university branches**.
- AUC: eligible through current MSCHE plus institutional evidence.
- SCU/MOHESR reconciliation and lifecycle review remain pending.

## D2.1 — Candidate universe completion

Status: **IN PROGRESS / PRINCIPAL AUTHORITATIVE-ACCREDITOR EXPANSION COMPLETE**

The deterministic builders now produce both the 96-row base and 106-row accreditor-expanded discovery/reconciliation universe with zero canonical creation, zero automatic merge and zero public projection.

British Council Partner Schools is the next broad supporting discovery source. Its September 2026 Egypt PDF contains **19 pages**. The file is browser-accessible, while GitHub-hosted direct Python retrieval returns HTTP 403. The approved adapter accepts a browser/local file via `--pdf-path`; the hosted 403 is not treated as source absence.

Partner/attached-centre status remains discovery/contact evidence only.

## D2.2 — Identity, campus and division reconciliation

Status: **ACTIVE — FIRST EXPLICIT REVIEW SET COMPLETED**

The matcher remains proposal-only. Matcher v2 removes generic education/model words such as British, American, English and International from distinctive-token evidence, preventing false duplicate proposals.

The first source-backed D2.2 review package now contains:

- **9 reviewed identity groups**;
- **20 source rows** covered;
- **7 `same_institution` groups**;
- **2 `same_institution_with_division_scoped_evidence` groups**.

Reviewed groups include Narmer American College, The British International School Cairo, Cairo American College, Cairo English School, Modern English School Cairo, NCBIS, Evolution International School, El Alsson and Misr Language Schools.

El Alsson and Misr Language Schools are explicitly resolved as one institutional identity with division-scoped evidence rather than duplicated institutions. Their British/American/French/IB source evidence remains attached to the relevant division scope.

Artifacts:

- `tools/data-acquisition/international/seeds/identity-review-decisions-2026-09-15.json`
- `tools/data-acquisition/international/validate_identity_review_decisions.py`

**EDU-DATA-2 Identity Review run 34899245102 passed CI.** It validates all 20 source memberships against the current 106-row universe and performs zero canonical merges/database mutation/public promotion.

The next D2.2 step is converting these reviewed relationships into deterministic canonical identity/campus/division records while continuing to queue unresolved candidates rather than silently merging them.

## D2.3 — EN/AR localization

Status: **ARCHITECTURE IMPLEMENTED / EVIDENCE COLLECTION STARTED**

A first institution-origin Arabic evidence package contains **4 names**:

- 2 current official Arabic-name evidence rows;
- 2 historical institution-origin rows explicitly flagged for current revalidation.

The localization workflow performs zero automatic translation/canonical mutation/public promotion. **Localization Evidence run 34897451220 passed.**

Do not mechanically add these four localization evidence rows to the 9 Arabic names already present in the 106 source rows; identity reconciliation must happen first.

## D2.4 — First-party profile enrichment

Status: **STARTED / FIRST HIGH-PRIORITY BATCH GREEN**

A current official-site/regulator enrichment package covers **8 high-priority institutions**.

Measured evidence coverage:

- official website: 8/8;
- location/address: 7/8;
- contact: 6/8;
- admissions: 6/8;
- curriculum/programme: 6/8;
- education range: 4/8;
- facilities: 2/8;
- provider/group: 1/8;
- founding history: 1/8;
- regulatory identifier/status: 2/8.

The first enrichment CI run correctly failed because curriculum/programme coverage was only 4/8. The evidence set was improved with current first-party curriculum evidence for NCBIS and GEMS British School Al Rehab rather than weakening the quality gate.

**Official Site Enrichment run 34898574887 now passes.**

No current fee schedule is inferred. Historical fee documents are not promoted as current fees. The package performs zero canonical field mutation, automatic merge or publication.

## D2.5 — Media

Status: **STARTED**

A reviewed seed currently contains **5 publication-safe Wikimedia assets** with rights/attribution metadata. Institution/commercial-site imagery remains discovery-only unless a defensible reuse basis exists.

Every reviewed institution must eventually receive a terminal media state, including `placeholder_required` where no publication-safe asset exists.

## D2.6 — Completeness/conflict audit

Status: **ARCHITECTURE IMPLEMENTED / FULL RECONCILIATION-AWARE AUDIT PENDING**

Institution and division models can now measure factual, EN, AR, media and unresolved-conflict completeness separately. Full reporting waits for broader D2.2 canonicalization and D2.4 enrichment.

## D2.7 — Portable export freeze

Status: **NOT STARTED**

The final portable package will contain canonical entities, bilingual localizations, source/evidence references, admissions/fee history, curriculum/accreditation relationships, division scope, media/rights, conflicts and completeness metrics without requiring Astro, Instatic or Supabase.

## Source-use boundaries

- **Edarabia:** reference-only discovery index under current terms; no systematic copying/import. Re-source facts from permitted primary/authoritative sources.
- **British Council:** supporting discovery/contact evidence only; local/browser PDF route approved when GitHub-hosted retrieval is blocked.
- **CIS/Cognia:** recognized accreditor evidence; scope/ownership gates remain separate.
- **Institution websites:** primary enrichment/localization evidence; factual extraction does not imply media-republication rights.
- **Wikimedia Commons:** asset-by-asset identity and rights review required.
- **OSM/Overture:** geography/support evidence only, with applicable licensing/attribution.

## Current CI gates

Key accepted runs:

- Core International Registry: **34899223939** — green after current 96-row/40-53-3 base, source registry, matcher and import safety checks;
- Accreditor Expansion: **34898150474** — green for the 106-row CIS/Cognia-expanded universe;
- Localization Evidence: **34897451220** — green;
- Official Site Enrichment: **34898574887** — green;
- School Division Schema: **34898999314** — green including clean apply and idempotent re-apply;
- Identity Review: **34899245102** — green for 9 reviewed groups / 20 source rows.

## Immediate next actions

1. Materialize the 9 reviewed D2.2 groups into deterministic canonical identity/campus/division **build artifacts**, still without writing a runtime database or publishing.
2. Continue IB private/state detail checks for the remaining unresolved IB directory rows.
3. Acquire the 19-page British Council PDF through the permitted browser/local route and run the existing discovery adapter.
4. Expand official-site D2.4 enrichment from 8 institutions toward every eligible identity.
5. Add current fee schedules only from current official sources; preserve older schedules historically.
6. Expand official Arabic names and revalidate historical Arabic-name evidence.
7. Reconcile SCU/MOHESR foreign-university identities and lifecycle state.
8. Expand geography/coordinates using institution evidence plus Overture/OSM cross-checks.
9. Continue media rights review and assign a terminal media state per reviewed identity.
10. Produce the first canonicalization-aware factual/EN/AR/media completeness report.
11. Freeze a deterministic portable export only after those review gates are satisfied.

## Deferred during database completion

- Astro vs Instatic selection;
- final website architecture/UI/search/filter design;
- public CMS mapping;
- visual design system;
- frontend deployment;
- public SEO page generation.

## Non-negotiable constraints

- no public-school/university scope expansion without a new owner decision;
- no exam-centre/partner-status shortcut to international eligibility;
- no eligibility inference from branding words;
- no commercial-directory override of authoritative evidence;
- no unsupported facts, fees, rankings, accreditations or admissions data;
- no publication of media without recorded rights basis;
- no Supabase for Edu Hub and no Ask Kalam infrastructure/data mixing;
- no raw/staging publication;
- no automatic identity merge from fuzzy matching;
- keep EN/AR parity, provenance, portability and data-quality review active throughout.
