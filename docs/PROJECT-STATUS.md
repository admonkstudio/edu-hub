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

The reference model is composed of:

- `001_raw_archive.sql` — owned source-shaped evidence archive;
- `004_national_registry_layers.sql` — staging/reconciliation and canonical identity foundations;
- `005_international_registry.sql` — international eligibility, providers, campuses, curricula, accreditation, contacts, fees/admissions and higher-ed structure;
- `006_bilingual_completion.sql` — EN/AR localization provenance, aliases, education levels, facilities, admission requirements, media localization, evidence assertions and independent completeness metrics;
- `007_school_divisions.sql` — first-class pre-university curriculum/language/phase divisions below institution/campus identity.

### School-division correction

Evidence from institutions such as Misr Language Schools and El Alsson proves that one canonical school/campus can contain separate British, American, French, IB or other sections with section-specific accreditation, admissions, fees and contacts.

Therefore a curriculum division is **not** automatically a separate institution and division-specific authorization must **not** be flattened onto the whole institution.

The reference hierarchy is now:

`provider -> institution -> campus -> school division`

`infra/owned-data/007_school_divisions.sql` passed clean-schema and idempotency CI in **EDU-DATA-2 School Division Schema run 34898999314**.

## Accepted source universe and eligibility state

### Deterministic authoritative/strong base — 96 source rows

- 54 IB Egypt rows;
- 11 UK DfE British Schools Overseas rows;
- 17 French homologation rows;
- 4 German KMK rows;
- 9 SCU foreign-university-branch rows;
- 1 AUC/MSCHE row.

Current accepted source-row states:

- **40 eligible**;
- **53 candidate**;
- **3 excluded**.

These are source records, not 96 claimed unique institutions.

### Accreditor-expanded D2.1 universe — 106 source rows

Separate current/recent accreditor evidence adds:

- 6 CIS Egypt accreditation rows;
- 4 Cognia 2026–2027 milestone rows.

Current accepted combined states:

- **40 eligible**;
- **63 candidate**;
- **3 excluded**.

English source-row naming evidence: **106/106**.
Arabic source-row naming evidence: **9/106**.
Source-row Arabic-name gaps before identity reconciliation: **97**.

No full-universe unique institution count is claimed and fuzzy matching never authorizes a merge.

## Major source-family progress

### International Baccalaureate

- 54 Egypt directory rows captured.
- IB country summary reported 55 on the same snapshot date; the discrepancy remains explicit.
- The accepted deterministic seed currently applies 12 detail/ownership decisions:
  - **9 PRIVATE / eligible**;
  - **3 STATE / excluded**.
- A second current verification batch was captured on 2026-09-15 for **5 additional PRIVATE schools**:
  - AIA School;
  - Al-Hoda International School;
  - American International School in Egypt;
  - American International School in Egypt West Campus;
  - Bedayia International School.
- That second batch is checked in as `ib-detail-evidence-2026-09-15-batch2.json` with `integration_state=captured_pending_deterministic_seed_integration`. It does **not** yet change the accepted 40/53/3 base counts; integration will occur as one dedicated deterministic-seed contract update.

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
- CIS/Cognia evidence strengthens international-model/accreditation evidence but does not bypass ownership/scope review.

### Higher education

- SCU: **9 recognized foreign university branches**.
- AUC: eligible through current MSCHE plus institutional evidence.
- SCU/MOHESR reconciliation and lifecycle review remain pending.

## D2.1 — Candidate universe completion

Status: **IN PROGRESS / PRINCIPAL AUTHORITATIVE-ACCREDITOR EXPANSION COMPLETE**

The deterministic builders produce both the 96-row base and 106-row accreditor-expanded discovery/reconciliation universe with zero canonical creation, zero automatic merge and zero public projection.

British Council Partner Schools is the next broad supporting discovery source. Its September 2026 Egypt PDF contains **19 pages**. The file is browser-accessible, while GitHub-hosted direct Python retrieval returns HTTP 403. The approved adapter accepts a browser/local file via `--pdf-path`; partner/attached-centre status remains discovery/contact evidence only.

## D2.2 — Identity, campus and division reconciliation

Status: **ACTIVE — FIRST REVIEWED GROUPS MATERIALIZED AS DETERMINISTIC DRAFTS**

The matcher remains proposal-only. Matcher v2 removes generic education/model words such as British, American, English and International from distinctive-token evidence, reducing false duplicate proposals.

The first source-backed review package contains:

- **9 reviewed identity groups**;
- **20 source rows** covered;
- **7 `same_institution` groups**;
- **2 `same_institution_with_division_scoped_evidence` groups**.

Reviewed groups include Narmer American College, The British International School Cairo, Cairo American College, Cairo English School, Modern English School Cairo, NCBIS, Evolution International School, El Alsson and Misr Language Schools.

El Alsson and Misr Language Schools resolve as one institutional identity each with division-scoped evidence rather than duplicate institutions.

### Deterministic reviewed-canonical draft materialization

`tools/data-acquisition/international/build_reviewed_canonical_artifacts.py` now converts only explicit D2.2 review decisions into portable build artifacts using deterministic UUIDv5 identifiers.

Current artifact result:

- **9 reviewed institution draft records**;
- **20 reviewed source memberships** preserved;
- **4 reviewed school-division draft records**:
  - El Alsson — American;
  - El Alsson — British;
  - Misr Language Schools — American;
  - Misr Language Schools — French;
- **9 campus review-state records**, all explicitly `not_yet_reviewed`;
- **0 resolved canonical campuses** — no campus is invented from institution identity evidence;
- **86 unreviewed source rows** retained in the D2.2 review queue;
- full-universe unique institution count remains intentionally unclaimed;
- eligibility selection is not performed by this identity materialization step;
- **0 automatic merges**;
- **0 canonical database rows written**;
- **0 runtime database mutation**;
- **0 public projection rows**.

Build outputs:

- `reviewed-institution-drafts.jsonl`
- `reviewed-school-division-drafts.jsonl`
- `campus-review-state.jsonl`
- `unreviewed-source-queue.jsonl`
- `reviewed-canonical-draft-summary.json`

**EDU-DATA-2 Identity Review run 34900009375 passed.** It compiled the builders, rebuilt the 106-row universe, validated the 9 relationship groups, materialized the deterministic drafts, asserted the 9/20/4/9/86 counts and uploaded the complete review artifact.

These artifacts are reviewed portable drafts, not runtime database writes or public records.

## D2.3 — EN/AR localization

Status: **ARCHITECTURE IMPLEMENTED / EVIDENCE COLLECTION STARTED**

A first institution-origin Arabic evidence package contains **4 names**:

- 2 current official Arabic-name evidence rows;
- 2 historical institution-origin rows explicitly flagged for current revalidation.

The localization workflow performs zero automatic translation/canonical mutation/public promotion. **Localization Evidence run 34897451220 passed.**

Do not mechanically add localization evidence rows to source-row Arabic counts; identity reconciliation happens first.

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

The first enrichment CI run correctly failed at 4/8 curriculum/programme coverage. The evidence set was improved with current first-party curriculum evidence rather than weakening the quality gate.

**Official Site Enrichment run 34898574887 passes.**

No current fee schedule is inferred. Historical fee documents are not promoted as current fees. The package performs zero canonical field mutation, automatic merge or publication.

## D2.5 — Media

Status: **STARTED**

A reviewed seed contains **5 publication-safe Wikimedia assets** with rights/attribution metadata. Institution/commercial-site imagery remains discovery-only unless a defensible reuse basis exists.

Every reviewed institution must eventually receive a terminal media state, including `placeholder_required` where no publication-safe asset exists.

## D2.6 — Completeness/conflict audit

Status: **ARCHITECTURE IMPLEMENTED / FULL RECONCILIATION-AWARE AUDIT PENDING**

Institution and division models can measure factual, EN, AR, media and unresolved-conflict completeness separately. Full reporting waits for broader D2.2 review and D2.4 enrichment.

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

- Core International Registry: **34899223939** — green for current accepted 96-row/40-53-3 base, source registry, matcher and import safety checks;
- Accreditor Expansion: **34898150474** — green for the accepted 106-row CIS/Cognia-expanded universe;
- Localization Evidence: **34897451220** — green;
- Official Site Enrichment: **34898574887** — green;
- School Division Schema: **34898999314** — green including clean apply and idempotent re-apply;
- Identity Review + deterministic draft materialization: **34900009375** — green for 9 institution drafts / 20 memberships / 4 division drafts / 9 unresolved campus states / 86 queued source rows.

## Immediate next actions

1. Integrate `ib-detail-evidence-2026-09-15-batch2.json` into the deterministic authoritative seed in one dedicated count/CI update; expected effect if unchanged by review is five IB rows moving from candidate to eligible.
2. Continue D2.2 source-backed identity review beyond the first 20 source memberships; prioritize obvious cross-source overlaps and parent/campus relationships.
3. Review campus structure for the 9 first materialized institutions instead of assuming one campus per identity.
4. Continue IB private/state detail checks for the remaining unresolved IB directory rows.
5. Acquire the 19-page British Council PDF through the permitted browser/local route and run the existing discovery adapter.
6. Expand official-site D2.4 enrichment from 8 institutions toward every eligible identity.
7. Add current fee schedules only from current official sources; preserve older schedules historically.
8. Expand official Arabic names and revalidate historical Arabic-name evidence.
9. Reconcile SCU/MOHESR foreign-university identities and lifecycle state.
10. Expand geography/coordinates using institution evidence plus Overture/OSM cross-checks.
11. Continue media rights review and assign a terminal media state per reviewed identity.
12. Produce the first canonicalization-aware factual/EN/AR/media completeness report.
13. Freeze a deterministic portable export only after those review gates are satisfied.

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
- no campus creation by assumption;
- keep EN/AR parity, provenance, portability and data-quality review active throughout.
