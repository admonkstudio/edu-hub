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

Status: **ACTIVE — CORE 106-ROW UNIVERSE FULLY CLASSIFIED; SUPPORTING DISCOVERY EXPANSION IN PROGRESS**

### Reproducible strong/authoritative source universe

The current accepted 106-row source universe contains:

- 54 IB Egypt rows;
- 11 UK DfE British Schools Overseas rows;
- 17 French 2026–2027 homologation rows;
- 4 German KMK recognized-school rows;
- 9 SCU recognized foreign-university-branch rows;
- 1 AUC/MSCHE higher-education row;
- 6 CIS accreditation rows;
- 4 Cognia milestone rows.

Current classification of those 106 rows:

- **103 eligible**;
- **0 candidate**;
- **3 excluded**.

All 54 captured IB rows have direct current PRIVATE/STATE review: 51 PRIVATE/eligible and 3 STATE/excluded. All 11 BSO rows have a separate private/independent ownership review. All CIS/Cognia expansion rows have a separate scope/ownership review.

These are **source records, not unique institutions**.

### British Council September 2026 discovery layer

The current British Council Partner Schools PDF is a **19-page discovery/contact source**. Partner School or attached-centre status does **not** establish international eligibility.

A first browser-reviewed discovery batch adds **35 supporting leads** that were not part of the 106-row strong-source universe. The batch preserves PDF page references and available website references while performing zero automatic eligibility, canonical identity creation, merges, database writes or public projection.

The raw expanded D2.1 discovery universe is therefore:

- **141 source/lead rows** total;
- 103 eligible strong-source rows;
- 3 excluded strong-source rows;
- 35 British Council supporting candidates.

This is **not** a claim of 141 institutions and is not yet a complete extraction of every row in the 19-page PDF.

`EDU-DATA-2 British Council Discovery` run **34909183019** passed the browser-discovery safety contract.

### British Council primary re-sourcing — batch 1

The first primary/recognized-evidence review qualifies only two exact British Council leads:

- **King's School The Crown** — current first-party private-school identity, Egyptian Ministry license to operate and teach the British National Curriculum, plus a current Independent Schools Inspectorate BSO institution record;
- **The International School of Choueifat, Cairo** — current first-party independent international-school identity plus a current five-year Cognia re-accreditation record published by the school following Cognia review.

After that explicit review, the expanded discovery universe is:

- **105 eligible source/lead rows**;
- **33 supporting candidates** still requiring primary/recognized qualification;
- **3 excluded rows**;
- **141 total source/lead rows**.

The historical 106-row classified universe remains independently reproducible and unchanged. Eligibility for the two new rows comes from separately recorded primary/recognized evidence, never from British Council Partner School status.

`EDU-DATA-2 British Council Discovery` run **34909421938** passed the primary re-sourcing and reviewed-candidate-universe safety contract.

### D2.1 remains open

Remaining discovery work includes:

- continue extracting/reviewing the September 2026 British Council PDF beyond the first 35-lead batch;
- primary-source qualification of the remaining British Council candidates;
- controlled Edarabia reference-only gap discovery followed by primary re-sourcing;
- additional operator/institution/regulator/accreditor discovery;
- relevant legacy/V7 leads only when re-sourced to current permitted evidence;
- supporting geography discovery through Overture/OSM under applicable license/attribution rules.

Supporting discovery evidence may expand the research universe but may not independently create eligibility.

## D2.2 — Identity, campus and division reconciliation

Status: **ACTIVE IN PARALLEL WITH OPEN D2.1 DISCOVERY — ORIGINAL AND QUALIFIED-DISCOVERY IDENTITY GATES OPERATIONAL**

Current accepted chain:

`scope-reviewed universe -> cross-source identity review -> explicit single-source review -> hierarchy review -> known-distinct safeguards -> incremental original-source identity batches -> qualified-discovery identity review -> incremental campus review`

### Current reviewed identity state

Current D2.2 materialization now contains:

- **26 reviewed institution drafts**;
- **10 reviewed school-division drafts**;
- **37 reviewed source-or-lead memberships**;
  - 35 memberships from the original 106-row source universe;
  - 2 memberships from separately qualified British Council discoveries;
- **71 original source rows** remain in the explicit identity-review queue;
- **33 British Council discovery leads** remain unqualified at D2.1 and therefore do not enter D2.2;
- **2 explicit known-distinct pair decisions** protect against reviewed false merges;
- 0 automatic merges;
- 0 canonical/runtime database writes;
- 0 public projection.

Reviewed original-source coverage includes all 11 BSO rows, all 6 CIS rows, all 4 Cognia rows, 9 IB rows participating in reviewed cross-source identities, 1 French homologation row for Misr Language Schools, and all 4 German KMK rows.

Remaining original-source identity queue:

- 45 IB rows;
- 16 French homologation rows;
- 9 SCU foreign-university-branch rows;
- 1 AUC/MSCHE row.

The two qualified British Council discoveries now pass the same explicit D2.2 identity boundary:

- King's School The Crown;
- The International School of Choueifat - Cairo.

Their qualification did not create canonical identities automatically. Explicit checked-in identity decisions produced stable review-draft IDs only after D2.1 eligibility had already been established independently.

`EDU-DATA-2 Discovery Identity Review` run **34909694279** passed with 26 institution drafts and zero automatic merges/database/public writes.

### Single-source and incremental identity rules

Explicit single-source identities require high-confidence primary/authoritative evidence. Absence of a duplicate proposal is never uniqueness proof.

The original accepted base contains 9 cross-source reviewed identities, 10 original explicit single-source identities and the Port Said Schools first-party parent/hierarchy review. The first additive original-source batch resolves all four KMK German-school rows without rewriting the earlier historical decision package. Qualified discoveries use a separate identity-review layer so discovery provenance and strong-source provenance remain distinguishable.

`EDU-DATA-2 Incremental Identity Review` run **34908639710** passed.

### Known-distinct safeguards

Two explicit negative identity decisions currently prevent false merges:

- `Europa Schule Neu Kairo` is distinct from `Europaschule Kairo` despite current collaboration;
- `Lycée Molière (International School of Egypt)` in Alexandria is distinct from `The International School of Egypt` in New Cairo.

Negative identity evidence is reviewed explicitly; non-matches are not inferred automatically.

### Institution/division hierarchy

The reviewed hierarchy contains 10 curriculum-division drafts. Important modeled cases include El Alsson, Misr Language Schools, Modern Education Schools and Port Said Schools.

Curriculum/accreditation evidence scoped to a British, American, French, IB or other division is not generalized to the whole institution, and a division is not automatically duplicated as a separate institution.

### Campus review

Current campus evidence now covers **11 of the 26 reviewed institution drafts**:

- the original 9 cross-source identities;
- King's School The Crown at The Crown, 6 October City;
- The International School of Choueifat - Cairo at its current New Cairo / District 5 location.

Current campus-review state:

- **11 reviewed current-campus drafts**;
- **11 campus-structure review records**;
- **15 reviewed institutions still require current-campus review**;
- **0 campus structures declared exhaustive/complete**;
- **0 additional current campuses inferred or ruled out automatically**;
- **0 canonical campus rows/database writes/public projection**.

Every reviewed current location therefore remains in state `at_least_one_current_campus_reviewed_structure_not_exhaustive`.

`EDU-DATA-2 Incremental Campus Review` run **34909846766** passed.

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
- British Council browser discovery batch: **34909183019** — green;
- British Council primary qualification batch 1: **34909421938** — green;
- Qualified Discovery Identity Review: **34909694279** — green;
- Incremental Campus Review: **34909846766** — green.

## Immediate next actions

1. Continue D2.1 British Council extraction and primary re-sourcing; keep ambiguous ownership/accreditation cases in candidate state.
2. Continue controlled gap discovery from Edarabia, operator sites, legacy/V7 and other permitted discovery sources without bulk-copying commercial-directory content.
3. Extend D2.2 identity review across the remaining 71 original source rows, prioritizing French homologation, standalone IB and higher-education identities.
4. Extend campus review to the remaining 15 reviewed institutions; only mark campus topology complete when affirmative evidence is exhaustive enough.
5. Expand D2.3 official Arabic-name evidence; explicitly mark transliteration/editorial Arabic where official forms cannot be sourced.
6. Expand D2.4 first-party enrichment toward every reviewed eligible identity, including current fees/admissions only from current official sources and with academic-year history preserved.
7. Reconcile SCU/MOHESR foreign-university identities, parent/branch relationships and lifecycle state.
8. Expand coordinates/geography with first-party evidence plus permitted Overture/OSM cross-checks.
9. Continue media-rights review and assign a terminal media state to every reviewed identity.
10. Produce the first canonicalization-aware EN/AR/factual/media completeness report after substantially broader identity coverage.
11. Freeze the deterministic portable export only after identity, localization, enrichment, conflict and media gates are satisfied.

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
- no exhaustive campus claim from one known address;
- preserve EN/AR parity, provenance, portability and data-quality review throughout.
