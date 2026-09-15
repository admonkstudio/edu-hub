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

## Active milestone and primary gate

**Active milestone:** `EDU-DATA-2 — Egypt International Education Registry`

**Active branch:** `edu-data-2-international-registry`

Edu Hub is an Admonk-owned independent bilingual education discovery and knowledge product focused first on **international education in Egypt** for parents and students.

The project is currently treated as a **data/research system before a website system**. Database completion, bilingual architecture, evidence, reconciliation, enrichment, media rights and portable export are the primary gate. UI, cards, profile templates, filters, SEO-page generation, visual design and the final Astro/Instatic choice remain deferred.

Canonical execution order:

1. `D2.1` — complete the in-scope institution/source universe;
2. `D2.2` — reconcile institutions, providers, campuses, aliases and divisions;
3. `D2.3` — complete English/Arabic localization architecture and evidence;
4. `D2.4` — enrich every eligible reviewed identity from first-party/authoritative sources;
5. `D2.5` — complete media references, rights and terminal media state;
6. `D2.6` — measure factual/EN/AR/freshness/conflict/media completeness separately;
7. `D2.7` — freeze a deterministic presentation-neutral master export.

Logical data path:

`external source -> raw evidence -> staging/reconciliation -> reviewed canonical data -> bilingual localization -> completeness/media audit -> portable export`

Supabase is not part of Edu Hub. Astro vs Instatic remains deferred until the database-completion gate exposes actual runtime requirements.

## D2.1 — Institution/source universe

Status: **ACTIVE — CORE 106-ROW UNIVERSE FULLY CLASSIFIED; SUPPORTING DISCOVERY EXPANSION AND PRIMARY RE-SOURCING IN PROGRESS**

### Reproducible strong/authoritative source universe

The accepted 106-row strong/authoritative source universe contains:

- 54 IB Egypt rows;
- 11 UK DfE British Schools Overseas rows;
- 17 French 2026–2027 homologation rows;
- 4 German KMK recognized-school rows;
- 9 SCU recognized foreign-university-branch rows;
- 1 AUC/MSCHE higher-education row;
- 6 CIS accreditation rows;
- 4 Cognia milestone rows.

Classification of those 106 rows remains:

- **103 eligible**;
- **0 candidate**;
- **3 excluded**.

All 54 captured IB rows have direct current PRIVATE/STATE review: 51 PRIVATE/eligible and 3 STATE/excluded. All 11 BSO rows have a separate private/independent ownership review. All CIS/Cognia expansion rows have a separate scope/ownership review.

These are **source records, not unique institutions**.

### British Council September 2026 discovery layer

The current British Council Partner Schools PDF is a **19-page discovery/contact source**. Partner School or attached-centre status does **not** establish international eligibility.

Two browser-reviewed discovery batches currently contain **70 British Council source rows** beyond the 106-row strong-source universe. They preserve PDF page/source provenance while performing zero automatic eligibility, canonical identity creation, merges, database writes or public projection.

The expanded D2.1 research universe is currently **176 source/lead rows**. The 70 British Council rows are evidence/discovery records, not a claim of 70 additional unique institutions. A discovery row may later resolve to a distinct institution, a campus, a curriculum division, an overlap with an existing strong-source row, or an out-of-scope entity. The PDF extraction is still incomplete.

`EDU-DATA-2 British Council Discovery` run **34910562436** passed the 70-row discovery safety contract before the second qualification/reconciliation pass.

### British Council primary re-sourcing — accepted batches

Six exact British Council discovery rows have now passed separate primary/recognized-evidence qualification. British Council Partner School status itself is not part of the eligibility basis:

- **King's School The Crown**;
- **The International School of Choueifat, Cairo**;
- **Global Paradigm Baccalaureate School**;
- **Capital International Schools**;
- **Mount International School Community**;
- **The International School of Elite Education**.

The latter four are explicit British Council ↔ existing IB-source overlaps. Their qualification adds supporting provenance and does **not** create four additional institutions.

Current expanded D2.1 research classification:

- **109 eligible source/lead rows**;
- **64 supporting candidates** still requiring primary/recognized qualification;
- **3 excluded rows**;
- **176 total source/lead rows**.

The historical 106-row classified universe remains independently reproducible and unchanged. Supporting British Council discovery rows do not inflate authoritative localization/completeness metrics until the relevant evidence/identity boundary is passed.

### D2.1 remains open

Remaining discovery work includes:

- continue extracting/reviewing the September 2026 British Council PDF beyond the current 70-row browser snapshot;
- primary-source qualification of the remaining 64 British Council candidates;
- controlled Edarabia reference-only gap discovery followed by primary re-sourcing;
- additional operator/institution/regulator/accreditor discovery;
- relevant legacy/V7 leads only when re-sourced to current permitted evidence;
- supporting geography discovery through Overture/OSM under applicable license/attribution rules.

Supporting discovery evidence may expand the research universe but may not independently create eligibility.

## D2.2 — Identity, campus and division reconciliation

Status: **ACTIVE IN PARALLEL WITH OPEN D2.1 DISCOVERY — ORIGINAL, DISCOVERY-OVERLAP AND MULTI-CAMPUS GATES OPERATIONAL**

Current accepted chain:

`scope-reviewed universe -> cross-source identity review -> explicit single-source review -> hierarchy review -> known-distinct safeguards -> incremental original-source identity batches -> qualified-discovery identity reconciliation -> explicit campus review sets`

### Current reviewed identity state

Current D2.2 materialization contains:

- **30 reviewed institution drafts**;
- **10 reviewed school-division drafts**;
- **45 reviewed source-or-lead memberships**;
- **67 original strong-source rows** remain in the explicit identity-review queue;
- **64 British Council discovery rows** remain unqualified at D2.1 and therefore stay outside D2.2;
- **0 currently qualified British Council discoveries are waiting for an identity decision**;
- **2 explicit known-distinct pair decisions** protect against reviewed false merges;
- 0 automatic merges;
- 0 canonical/runtime database writes;
- 0 public projection.

The remaining original-source identity queue is currently:

- **41 IB rows**;
- **16 French homologation rows**;
- **9 SCU foreign-university-branch rows**;
- **1 AUC/MSCHE row**.

The four second-pass British Council qualifications were explicitly reconciled to exact queued IB source rows:

- Global Paradigm Baccalaureate School;
- Capital International Schools;
- Mount International School Community;
- The International School of Elite Education.

Each reconciliation names both source memberships and creates one reviewed institution draft, removing the matching IB row from the original identity queue instead of creating a duplicate institution. No name/domain/fuzzy automatic reconciliation is permitted.

`EDU-DATA-2 Discovery Identity Review` run **34911619429** passed after the queue-name normalization fix and accepts the current discovery↔original-source reconciliation model.

### Single-source and incremental identity rules

Explicit single-source identities require high-confidence primary/authoritative evidence. Absence of a duplicate proposal is never uniqueness proof.

The accepted base contains cross-source reviewed identities, explicit single-source identities and first-party parent/hierarchy review. Incremental original-source decisions remain additive rather than rewriting earlier historical decision packages. Qualified discoveries use a separate identity-review layer so discovery provenance and strong-source provenance remain distinguishable.

A qualified discovery may be reconciled to a still-queued original source row only through a checked-in exact source-to-source identity decision. Eligibility alone never forces canonicalization.

`EDU-DATA-2 Incremental Identity Review` run **34908639710** passed.

### Known-distinct safeguards

Two explicit negative identity decisions currently prevent false merges:

- `Europa Schule Neu Kairo` is distinct from `Europaschule Kairo` despite current collaboration;
- `Lycée Molière (International School of Egypt)` in Alexandria is distinct from `The International School of Egypt` in New Cairo.

Negative identity evidence is reviewed explicitly; non-matches are not inferred automatically.

### Institution/division hierarchy

The reviewed hierarchy contains **10 curriculum-division drafts**. Important modeled cases include El Alsson, Misr Language Schools, Modern Education Schools and Port Said Schools.

Curriculum/accreditation evidence scoped to a British, American, French, IB or other division is not generalized to the whole institution, and a division is not automatically duplicated as a separate institution.

### Campus review

The campus model now supports multiple explicitly evidenced current campuses for one reviewed institution while preserving a non-exhaustive topology state.

Current campus-review state:

- **17 reviewed current-campus drafts**;
- **15 of 30 reviewed institutions** have at least one reviewed current campus;
- **2 institutions** have multiple reviewed current campuses:
  - Capital International Schools — Main Campus + Lotus Campus;
  - Mount International School Community — New Administrative Capital + Al-Shorouk;
- **15 reviewed institutions** still require current-campus review;
- **0 campus structures declared exhaustive/complete**;
- **0 additional current campuses inferred or ruled out automatically**;
- **0 canonical campus rows/database writes/public projection**.

Multiple campuses can be accepted together only as an explicit reviewed set. A later campus addition to an institution that already has accepted campus evidence requires `review_mode=explicit_multi_campus_extension`. Multiple reviewed current campuses still do not prove exhaustive topology.

`EDU-DATA-2 Incremental Campus Review` run **34920248466** passed the current 30-identity / 17-campus / two-multi-campus safety contract.

British Council campus-specific rows may support topology discovery, but Partner School rows may not silently create new campuses or institutions.

## D2.3 — English/Arabic architecture

Status: **ARCHITECTURE IMPLEMENTED / CONTENT INCOMPLETE**

English and Arabic are first-class localizations of the same factual entity graph. Language-neutral facts exist once. Localized names, descriptions and display text carry language, source/origin and review status.

Official Arabic names are preferred. Transliteration/editorial Arabic is allowed only when explicitly labeled as non-official. Source-row Arabic gaps remain a research queue and must not be confused with canonical institution localization completeness after reconciliation.

## D2.4 — First-party profile enrichment

Status: **STARTED / FIRST HIGH-PRIORITY BATCH GREEN**

The first reviewed package covers 8 high-priority institutions with source-backed website, location, contact, admissions, curriculum/programme, education-range and selected facility/provider/history/regulatory facts.

Missing values remain missing. Current and historical facts are separated; historical fee material is never promoted as a current fee. Broader enrichment attaches only after identity/campus/division scope is understood.

## D2.5 — Media and rights

Status: **STARTED**

The reviewed seed contains 5 publication-safe Wikimedia assets with recorded creator/license/attribution metadata. Institution/commercial-site imagery is discovery-only unless a defensible reuse basis exists.

Every final reviewed institution must receive a terminal media state. `placeholder_required` is valid when no publication-safe image exists.

## D2.6 — Completeness and conflict audit

Status: **ARCHITECTURE IMPLEMENTED / FULL CANONICAL AUDIT PENDING**

Completeness is measured independently across factual coverage, English localization, Arabic localization, media, provenance/freshness and unresolved conflicts. Conflicting assertions remain review work instead of being silently overwritten.

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
- Incremental Identity Review (German KMK batch): **34908639710** — green;
- British Council initial browser discovery: **34909183019** — green;
- British Council primary qualification batch 1: **34909421938** — green;
- Qualified Discovery Identity Review: **34909694279** — green;
- British Council 70-row discovery expansion: **34910562436** — green;
- Discovery↔original-source reconciliation / current identity state: **34911619429** — green;
- Incremental Campus Review after identity reconciliation: **34911619392** — green;
- Explicit multi-campus topology review: **34920248466** — green.

## Immediate next actions

1. Continue D2.1 British Council extraction beyond the current 70 source rows and continue primary re-sourcing; keep ambiguous ownership/accreditation cases in candidate state.
2. Prioritize primary/recognized qualification and cross-source overlap detection of high-signal British Council discoveries before treating discovery volume as progress.
3. Continue controlled gap discovery from Edarabia, operator sites, legacy/V7 and other permitted discovery sources without bulk-copying commercial-directory content.
4. Extend D2.2 identity review across the remaining **67 original source rows**, prioritizing French homologation, standalone IB and higher-education identities.
5. Extend campus review to the remaining **15 reviewed institutions**; only mark campus topology complete when affirmative evidence is exhaustive enough.
6. Expand D2.3 official Arabic-name evidence; explicitly mark transliteration/editorial Arabic where official forms cannot be sourced.
7. Expand D2.4 first-party enrichment toward every reviewed eligible identity, including current fees/admissions only from current official sources and with academic-year history preserved.
8. Reconcile SCU/MOHESR foreign-university identities, parent/branch relationships and lifecycle state.
9. Expand coordinates/geography with first-party evidence plus permitted Overture/OSM cross-checks.
10. Continue media-rights review and assign a terminal media state to every reviewed identity.
11. Produce the first canonicalization-aware EN/AR/factual/media completeness report after substantially broader identity coverage.
12. Freeze the deterministic portable export only after identity, localization, enrichment, conflict and media gates are satisfied.

## Non-negotiable constraints

- no frontend/CMS architecture decision before database completion;
- no public-school/university scope expansion without a new owner decision;
- no exam-centre/Partner-School shortcut to international eligibility;
- no eligibility inference from branding words;
- no commercial-directory override of authoritative evidence;
- no unsupported facts, fees, rankings, accreditations or admissions data;
- no publication of media without recorded rights basis;
- no Supabase and no Ask Kalam infrastructure/data mixing;
- no raw/staging publication;
- no automatic identity merge from fuzzy matching;
- no automatic uniqueness assumption for unmatched source rows;
- no exhaustive campus claim from one known address or from a reviewed multi-campus set;
- preserve EN/AR parity, provenance, portability and data-quality review throughout.
