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

The primary gate is database completion and bilingual data architecture before presentation. UI, profile templates, filters, SEO-page generation, visual design and Astro/Instatic selection remain deferred until the portable database gate is satisfied.

Current Phase 1 scope includes private/independent international schools, private/independent IB World Schools, recognized foreign-national/international school models, recognized foreign university branch campuses, and internationally chartered/accredited independent higher-education institutions whose international status is substantive.

Canonical contracts:

- `docs/EDU-DATA-2-INTERNATIONAL-REGISTRY.md`
- `docs/DATABASE-COMPLETION-PLAN.md`
- `docs/SOURCE-USAGE-POLICY.md`
- `docs/PROJECT-DECISIONS.md`

Logical data path:

`external source -> raw evidence -> staging/reconciliation -> reviewed canonical data -> bilingual localization -> completeness/media audit -> portable export`

## D2.1 — Institution/source universe

Status: **CURRENT 106-ROW SOURCE UNIVERSE FULLY SCOPE-CLASSIFIED / DISCOVERY REMAINS OPEN**

Current source universe:

- 54 IB Egypt rows;
- 11 UK DfE British Schools Overseas rows;
- 17 French 2026–2027 homologation rows;
- 4 German KMK recognized-school rows;
- 9 SCU recognized foreign-university-branch rows;
- 1 AUC/MSCHE higher-education row;
- 6 CIS accreditation rows;
- 4 Cognia milestone rows.

Current accepted classification:

- **103 eligible source rows**;
- **0 candidate source rows**;
- **3 excluded source rows**.

All 54 captured IB identities have direct current type review: 51 PRIVATE/eligible and 3 STATE/excluded. All 11 BSO rows have separate private/independent ownership review. All 10 CIS/Cognia expansion rows have separate ownership/international-model review. Source records remain evidence rows, not unique-institution counts.

D2.1 is not closed merely because the current 106 rows are classified. Discovery still includes the British Council September 2026 Partner Schools PDF, additional primary/operator sources, controlled Edarabia reference-only gap discovery followed by primary re-sourcing, relevant legacy/V7 leads that can be re-sourced, and supporting geography discovery. Supporting discovery evidence never establishes international eligibility by itself.

## D2.2 — Identity, campus and division reconciliation

Status: **ACTIVE IN PARALLEL WITH OPEN D2.1 DISCOVERY — EXPLICIT REVIEW GATES OPERATIONAL**

The accepted reconciliation chain is:

`scope-reviewed source universe -> cross-source identity review -> explicit single-source review -> institution/division hierarchy review -> known-distinct safeguards -> incremental explicit identity batches`

### Current reviewed identity state

After the accepted German/KMK incremental identity batch:

- **24 reviewed institution drafts**;
- **35 reviewed unique source rows**;
- **10 reviewed school-division drafts**;
- **71 source rows remain in the explicit identity-review queue**;
- **2 explicit known-distinct source-pair decisions** block reviewed false merges;
- **0 automatic merges**;
- **0 canonical/runtime database writes**;
- **0 public projection**.

The reviewed 35 source rows currently cover all 11 BSO rows, all 6 CIS rows, all 4 Cognia rows, 9 IB rows participating in reviewed cross-source identities, 1 French homologation row for Misr Language Schools, and all 4 German KMK rows.

Remaining explicit identity-review queue:

- **45 IB rows**;
- **16 French homologation rows**;
- **9 SCU foreign-university-branch rows**;
- **1 AUC/MSCHE row**.

No full-universe unique-institution count is claimed yet.

### Explicit single-source identity architecture

The earlier D2.2 limitation that only supported two-or-more-source duplicate groups has been corrected. Explicit single-source identities are permitted only when checked-in review decisions provide high-confidence primary/authoritative evidence. Absence of a duplicate proposal is never treated as uniqueness proof.

The accepted base contains 9 reviewed cross-source identities, 10 original explicit single-source identities, and the Port Said Schools first-party parent/hierarchy review. The first additive identity batch resolves the four KMK German-school rows without rewriting the accepted historical decision package.

`EDU-DATA-2 Incremental Identity Review` run **34908639710** passed the full rebuild and safety contract.

### Known-distinct safeguards

Two explicit negative identity decisions are recorded so similar naming cannot create future false merges:

- `Europa Schule Neu Kairo` is distinct from `Europaschule Kairo` despite current collaboration;
- `Lycée Molière (International School of Egypt)` in Alexandria is distinct from `The International School of Egypt` in New Cairo.

Negative identity evidence is explicit and reviewed; the system does not infer non-matches automatically.

### Institution/division hierarchy

The reviewed hierarchy currently includes 10 curriculum-division drafts. Important modeled examples include El Alsson, Misr Language Schools, Modern Education Schools and Port Said Schools, where source/accreditation evidence may apply to one division rather than the whole institution.

A curriculum division is not automatically a separate institution, and division-scoped accreditation must not be generalized institution-wide.

### Current-campus review

At least one current operating location has been source-reviewed for the original 9 cross-source institutional identities:

- 9 current-campus drafts;
- 9 campus-structure review records;
- 0 campus structures marked exhaustive/complete;
- 0 inferred additional campuses;
- 0 canonical campus database writes.

State: `at_least_one_current_campus_reviewed_structure_not_exhaustive`.

The additional reviewed institution drafts created after the first campus pass still require campus review. A known current location is not proof of a complete campus topology.

## D2.3 — English/Arabic architecture

Status: **ARCHITECTURE IMPLEMENTED / CONTENT INCOMPLETE**

English and Arabic are first-class localizations of one factual entity graph. Language-neutral facts exist once; localized names/descriptions/display text carry their own language, source/origin and review status. Official Arabic names are preferred. Transliteration/editorial Arabic is explicitly marked and is never represented as institution-sourced.

Source-row Arabic coverage remains a research queue and must not be confused with canonical institution localization completeness after reconciliation.

## D2.4 — First-party profile enrichment

Status: **STARTED / FIRST HIGH-PRIORITY BATCH GREEN**

The first reviewed enrichment package covers 8 high-priority institutions with source-backed website, location, contact, admissions, curriculum/programme, education range and selected facility/provider/history/regulatory facts. Missing values remain missing; historical fee documents are not promoted as current fees.

Broader enrichment remains gated by identity review so profile facts attach to the correct institution/campus/division.

## D2.5 — Media and rights

Status: **STARTED**

The reviewed seed contains 5 publication-safe Wikimedia assets with recorded creator/license/attribution metadata. Institution/commercial-site imagery remains discovery-only unless a defensible reuse basis exists.

Every reviewed institution must eventually receive a terminal media state, including `placeholder_required` where no publication-safe asset exists.

## D2.6 — Completeness and conflict audit

Status: **ARCHITECTURE IMPLEMENTED / FULL CANONICAL AUDIT PENDING**

Completeness is measured independently across factual coverage, English localization, Arabic localization, media, provenance/freshness and unresolved conflicts. The first meaningful full audit remains gated by broader identity reconciliation.

## D2.7 — Portable export freeze

Status: **NOT STARTED**

The final presentation-neutral export must include reviewed providers/institutions/campuses/divisions, EN/AR localizations and aliases, source/evidence references, curricula/certificates/accreditation, admissions and versioned fees, higher-education programmes/units, contacts/geography/facilities, media rights/attribution, conflicts/review state and completeness metrics.

It must not require Astro, Instatic or Supabase.

## Accepted CI gates

- Foundational Core International Registry: **34900305899** — green;
- Foundational Accreditor Expansion: **34900289955** — green;
- Complete direct IB ownership review: **34901947722** — green;
- BSO private/independent scope review: **34905472533** — green;
- CIS/Cognia scope review and 106-row classification: **34905794670** — green;
- Localization Evidence: **34897451220** — green;
- Official Site Enrichment: **34898574887** — green;
- School Division Schema: **34898999314** — green;
- Identity Review + reviewed canonical draft materialization: **34900009375** — green;
- Current Campus Review: **34901485863** — green;
- Incremental Identity Review (German KMK batch): **34908639710** — green.

## Immediate next actions

1. Continue **D2.1 discovery** with the British Council September 2026 Partner Schools PDF through the permitted browser/local route, then re-source any new candidates from primary/authoritative evidence before eligibility decisions.
2. Continue controlled gap discovery from Edarabia, operator sites, legacy/V7 and other permitted sources without bulk-copying commercial directory content.
3. Extend D2.2 explicit identity review across the remaining 71 source rows, prioritizing French homologation, standalone IB and higher-education identities while preserving division/campus/provider scope.
4. Extend campus topology review to the institution drafts added after the first 9-campus pass; only mark structures complete when evidence is exhaustive enough.
5. Expand D2.3 official Arabic-name evidence and explicitly mark transliteration/editorial Arabic where official forms cannot be sourced.
6. Expand D2.4 first-party enrichment toward every reviewed eligible identity, including current fees/admissions only from current official sources and with academic-year history preserved.
7. Reconcile SCU/MOHESR foreign-university identities, parent/branch relationships and lifecycle state.
8. Expand coordinates/geography with first-party evidence plus permitted Overture/OSM cross-checks.
9. Continue media-rights review and assign a terminal media state to every reviewed identity.
10. Produce the first canonicalization-aware EN/AR/factual/media completeness report after substantially broader identity coverage.
11. Freeze the deterministic portable export only after identity, localization, enrichment, conflicts and media gates are satisfied.

## Non-negotiable constraints

- no frontend/CMS architecture decision before the database-completion gate;
- no public-school/university scope expansion without a new owner decision;
- no exam-centre/partner-status shortcut to international eligibility;
- no eligibility inference from branding words;
- no commercial-directory override of authoritative evidence;
- no unsupported facts, fees, rankings, accreditations or admissions data;
- no publication of media without recorded rights basis;
- no Supabase and no Ask Kalam infrastructure/data mixing;
- no raw/staging publication;
- no automatic identity merge from fuzzy matching;
- no automatic uniqueness assumption for unmatched source rows;
- no exhaustive campus claim from one known address;
- keep EN/AR parity, provenance, portability and data-quality review active throughout.
