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

## Active milestone and product boundary

Edu Hub is an Admonk-owned independent bilingual education discovery and knowledge product focused first on **international education in Egypt** for parents and students.

**Active milestone:** `EDU-DATA-2 — Egypt International Education Registry`

**Active branch:** `edu-data-2-international-registry`

Current Phase 1 scope includes:

- private/independent international schools;
- private/independent IB World Schools;
- recognized foreign-national/international school models;
- recognized foreign university branch campuses;
- internationally chartered/accredited independent higher-education institutions whose international status is substantive.

Out of scope for the active milestone:

- Egyptian public schools and public universities;
- the historical nationwide EMIS/MOSS registry targets;
- ordinary language schools or exam centres without sufficient international-status evidence;
- frontend/CMS selection and public presentation work until the database-completion gate is satisfied.

Canonical contracts:

- `docs/EDU-DATA-2-INTERNATIONAL-REGISTRY.md`
- `docs/DATABASE-COMPLETION-PLAN.md`
- `docs/SOURCE-USAGE-POLICY.md`
- `docs/PROJECT-DECISIONS.md`

Logical data path:

`external source -> raw evidence -> staging/reconciliation -> reviewed canonical data -> bilingual localization -> completeness/media audit -> portable export`

Supabase is not part of Edu Hub. Astro vs Instatic remains deferred until database completion exposes the actual runtime requirements.

## Canonical data architecture

Reference migrations:

- `001_raw_archive.sql` — source-shaped evidence archive;
- `004_national_registry_layers.sql` — staging/reconciliation and identity foundations;
- `005_international_registry.sql` — international eligibility, providers, campuses, curricula, accreditation, contacts, fees/admissions and higher-ed structure;
- `006_bilingual_completion.sql` — EN/AR provenance, aliases, levels, facilities, admission requirements, media localization, evidence assertions and independent completeness metrics;
- `007_school_divisions.sql` — first-class pre-university curriculum/language/phase divisions below institution/campus identity.

Canonical hierarchy where applicable:

`provider -> institution -> campus -> school division`

A curriculum division is not automatically a separate institution. British, American, French, IB or other division-specific accreditation, curriculum, admissions, fees and contacts remain scoped to that division instead of being flattened onto the whole institution.

## D2.1 — Current source universe and scope classification

Status: **CURRENT 106-ROW SOURCE UNIVERSE FULLY SCOPE-CLASSIFIED / DISCOVERY REMAINS OPEN**

### Foundational authoritative/strong source universe — 96 source rows

Current source families:

- 54 IB Egypt rows;
- 11 UK DfE British Schools Overseas rows;
- 17 French 2026–2027 homologation rows;
- 4 German KMK recognized-school rows;
- 9 SCU recognized foreign-university-branch rows;
- 1 AUC/MSCHE international higher-education row.

The historical foundational builder remains reproducible at its original 40 eligible / 53 candidate / 3 excluded state. Current accepted state is produced through dated, auditable exact-row review overlays rather than rewriting that historical snapshot.

### IB ownership/type review — complete

All 54 captured IB Egypt source identities now have direct current PRIVATE/STATE review:

- **51 PRIVATE / eligible**;
- **3 STATE / excluded**;
- **0 unresolved**.

Eight incremental IB evidence batches update 42 exact existing IB rows while preserving source IDs and source ordering. Combined with the earlier detail seed, direct ownership review covers 54/54 IB directory rows.

`EDU-DATA-2 Incremental IB Details` run **34901947722** passed the complete build and downstream safety contract.

### UK DfE British Schools Overseas scope review — complete

All 11 current Egypt BSO source rows have now passed a separate non-public/private/independent ownership gate rather than being promoted merely because they are BSO-accredited.

Reviewed rows include:

- The British School of Alexandria;
- El Alsson British International School;
- Egypt British International School;
- Gulf English School Cairo;
- Maadi British International School;
- Modern English School Cairo;
- The British International School, Cairo;
- New Cairo British International School;
- Repton School Cairo;
- The Royal British International School, Cairo;
- Uppingham Cairo.

Evidence patterns include direct private-school history, independent/not-for-profit governance, proprietor/company evidence, current private-provider relationships, and already-reviewed same-institution links to PRIVATE IB identities. BSO accreditation and ownership remain separate assertions.

After the BSO review, the current 96-row foundational source universe is:

- **93 eligible**;
- **0 candidate**;
- **3 excluded**.

`EDU-DATA-2 BSO Scope Review` run **34905472533** passed and performs zero source-ID changes, identity merges, canonical database writes, runtime mutation or public projection.

### CIS/Cognia expansion scope review — complete

The supporting accreditor expansion contributes:

- 6 CIS current/recent Egypt accreditation rows;
- 4 Cognia 2026–2027 milestone rows.

All 10 supporting rows have now received a separate ownership/international-model review. The review uses already-reviewed identity links where applicable and first-party provider/institution evidence for standalone rows.

Important modeling outcomes include:

- CIS evidence for Evolution, Cairo English School, NCBIS and Cairo American College remains a separate accreditation assertion under identities already reviewed as PRIVATE through IB;
- CIS rows for British School Al Rehab and British School Madinaty are supported by current GEMS school membership plus GEMS's current private-education-provider identity;
- Cognia evidence for Misr Language Schools remains American-division scoped;
- Modern Education Schools is treated as a private-company-operated institution with National, British and American divisions; Cognia evidence must be scoped to the relevant American context rather than every division;
- Port Said American School is treated as the American section of a non-profit educational-cooperative/national-institute school structure, not as an Egyptian state-school identity; section-level evidence must remain division-scoped.

Current accepted 106-row source universe:

- **103 eligible source rows**;
- **0 candidate source rows**;
- **3 excluded source rows**.

These 106 rows are **source records, not 106 unique institutions**. Cross-source identity reconciliation remains active and must reduce duplicates before a canonical institution count is claimed.

`EDU-DATA-2 Accreditor Scope Review` run **34905794670** passed the complete foundational -> IB -> BSO -> CIS/Cognia -> candidate-universe -> D2.2 safety pipeline.

### Bilingual source-row coverage

- English naming evidence: **106/106** source rows;
- Arabic naming evidence: **9/106** source rows;
- pre-reconciliation Arabic-name evidence gaps: **97**.

These source-row counts must not be mistaken for canonical institution localization counts. EN/AR completeness is evaluated after identity reconciliation.

### Discovery still open

Completing scope classification for the current 106 rows does **not** mean the Egypt international-education universe is complete. Remaining discovery work includes:

- British Council Partner Schools September 2026 PDF as discovery/contact evidence;
- additional primary-source school/operator discovery;
- controlled Edarabia reference-only gap discovery followed by primary-source re-sourcing;
- reconciliation of relevant legacy/V7 leads only when they map to in-scope evidence;
- supporting geography discovery via Overture/OSM under applicable license/attribution rules.

No supporting discovery source may establish international eligibility by itself.

## D2.2 — Identity, campus and division reconciliation

Status: **ACTIVE — FIRST REVIEWED IDENTITIES/DIVISIONS/CAMPUSES MATERIALIZED AS PORTABLE DRAFTS**

Current reviewed identity package:

- **9 reviewed identity groups**;
- **20 source memberships**;
- **7 `same_institution` groups**;
- **2 `same_institution_with_division_scoped_evidence` groups**;
- **4 reviewed curriculum-division drafts**;
- **86 source rows remain outside the first explicit identity-review package**.

Reviewed institutional groups currently cover:

- Narmer American College;
- The British International School, Cairo;
- Cairo American College;
- Cairo English School;
- Modern English School Cairo;
- New Cairo British International School;
- Evolution International School;
- El Alsson;
- Misr Language Schools.

El Alsson and Misr Language Schools resolve as one institutional identity each with separately scoped curriculum divisions rather than duplicated institutions.

`build_reviewed_canonical_artifacts.py` produces stable UUIDv5 **review drafts only**. It performs zero automatic merge, canonical runtime database write or public projection.

### Current-campus review

At least one current operating location has been source-reviewed for all 9 currently reviewed institutional identities.

The campus builder emits:

- 9 reviewed current-campus draft records;
- 9 campus-structure review records;
- 0 campus structures marked exhaustive/complete;
- 0 inferred additional campuses;
- 0 canonical campus database writes;
- 0 public projection.

State: `at_least_one_current_campus_reviewed_structure_not_exhaustive`.

Current-campus evidence must never be interpreted as proof that an institution has only one campus.

Campus Review run **34901485863** passed.

### Immediate identity-model correction now required

The existing D2.2 review package was designed around cross-source duplicate groups and therefore expects two or more source memberships per reviewed group. That is insufficient for database completion because many legitimate French/German/standalone international institutions may have only one current authoritative source row.

The next D2.2 architecture step is to support **explicit reviewed single-source identities** backed by primary/official evidence, while still preventing the system from silently treating every unmatched row as unique. A single-source canonical draft must require explicit review and evidence; absence of a duplicate proposal is not enough.

## D2.3 — English/Arabic localization

Status: **ARCHITECTURE IMPLEMENTED / CONTENT INCOMPLETE**

English and Arabic are first-class localizations of one factual entity graph. Official Arabic names are preferred. Transliteration/editorial Arabic is allowed only with explicit non-official origin/status.

Current institution-origin Arabic evidence package contains:

- 2 current official Arabic-name evidence rows;
- 2 historical institution-origin Arabic rows requiring current revalidation.

Localization Evidence run **34897451220** passed.

The current 97 source-row Arabic gaps are a research queue, not permission to fabricate Arabic names.

## D2.4 — First-party profile enrichment

Status: **STARTED / FIRST HIGH-PRIORITY BATCH GREEN**

Current first-party/regulator enrichment package covers 8 high-priority institutions:

- official website 8/8;
- location/address 7/8;
- contact 6/8;
- admissions 6/8;
- curriculum/programme 6/8;
- education range 4/8;
- facilities 2/8;
- provider/group 1/8;
- founding history 1/8;
- regulatory identifier/status 2/8.

Official Site Enrichment run **34898574887** passed. Missing data remains explicitly missing. Historical fee documents are not promoted as current fees.

## D2.5 — Media and rights

Status: **STARTED**

Current reviewed seed contains **5 publication-safe Wikimedia assets** with recorded creator/license/attribution metadata.

Institution/commercial-site imagery remains discovery-only unless a defensible reuse basis exists. Every reviewed institution must eventually receive a terminal media state, including `placeholder_required` when no safe asset is available.

## D2.6 — Completeness and conflict audit

Status: **ARCHITECTURE IMPLEMENTED / FULL CANONICAL AUDIT PENDING**

The model measures separately:

- factual completeness;
- English localization completeness;
- Arabic localization completeness;
- media completeness;
- provenance/freshness;
- unresolved conflicts.

A full report is intentionally deferred until broader D2.2 canonical identity review prevents source-row duplicates from distorting completeness metrics.

## D2.7 — Portable export freeze

Status: **NOT STARTED**

The eventual presentation-neutral export will include:

- canonical providers/institutions/campuses/divisions;
- EN/AR localizations and aliases;
- source/evidence references;
- curricula/certificates/accreditation;
- admissions and historical/current fee schedules;
- programmes/academic units for higher education;
- contacts/geography/facilities;
- media manifest and rights/attribution;
- conflict/review state;
- completeness metrics.

It must not require Astro, Instatic or Supabase.

## Higher education

Status: **FOUNDATIONAL SOURCE CAPTURED / RECONCILIATION PENDING**

- SCU currently contributes 9 recognized foreign-university-branch source rows;
- AUC is included through current MSCHE plus institution evidence;
- SCU/MOHESR identity/lifecycle reconciliation remains pending;
- ordinary Egyptian universities with only foreign partnerships are not automatically in scope.

## Key source-use boundaries

- **Edarabia:** reference-only discovery under current terms; no systematic copying/import.
- **British Council Partner Schools:** discovery/contact evidence only; attached-centre/partner status is not international eligibility.
- **IB / French Ministry / German KMK / SCU / recognized accreditors:** strong evidence, but evidence scope must remain accurate.
- **CIS/Cognia:** accreditation evidence; ownership and identity are separately reviewed.
- **Institution websites:** primary factual/localization evidence; no automatic media-republication rights.
- **Wikimedia Commons:** asset-by-asset identity and rights review.
- **OSM/Overture:** supporting geography with required license/attribution handling.

## Accepted CI gates

- Foundational Core International Registry: **34900305899** — green;
- Foundational Accreditor Expansion: **34900289955** — green;
- Complete direct IB ownership review: **34901947722** — green;
- BSO private/independent scope review: **34905472533** — green;
- CIS/Cognia scope review and full current 106-row classification: **34905794670** — green;
- Localization Evidence: **34897451220** — green;
- Official Site Enrichment: **34898574887** — green;
- School Division Schema: **34898999314** — green;
- Identity Review + reviewed canonical draft materialization: **34900009375** — green;
- Current Campus Review: **34901485863** — green.

## Immediate next actions

1. Extend D2.2 to support **explicit reviewed single-source identities** without weakening the no-auto-merge rule.
2. Expand canonical identity review across the remaining source universe, including French, German, standalone BSO, CIS/Cognia and higher-education identities.
3. Add new division relationships where primary evidence shows one institution operating distinct curriculum sections, especially Modern Education Schools and Port Said Schools.
4. Continue campus topology review; only mark campus structure complete when evidence is exhaustive enough.
5. Acquire/process the 19-page British Council September 2026 PDF through the permitted browser/local path and use it strictly for discovery/contact leads.
6. Continue source discovery until no material gaps remain across authoritative and permitted supporting sources.
7. Expand first-party D2.4 profile enrichment toward every reviewed eligible identity.
8. Expand official Arabic-name evidence and revalidate historical Arabic forms.
9. Add current fee schedules only from current official sources, preserving historical schedules rather than overwriting them.
10. Reconcile SCU/MOHESR foreign-university identities and lifecycle state.
11. Expand coordinates/geography with first-party evidence plus Overture/OSM cross-checks.
12. Continue media-rights review and assign a terminal media state to every reviewed identity.
13. Produce the first canonicalization-aware EN/AR/factual/media completeness report.
14. Freeze the deterministic portable export only after identity, localization, enrichment, conflict and media gates are satisfied.

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
- no Supabase and no Ask Kalam infrastructure/data mixing;
- no raw/staging publication;
- no automatic identity merge from fuzzy matching;
- no automatic uniqueness assumption for an unmatched source row;
- no exhaustive campus claim from one known address;
- keep EN/AR parity, provenance, portability and data-quality review active throughout.
