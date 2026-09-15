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

The project is currently a **data/research system before a website system**. Database completion, bilingual architecture, evidence, reconciliation, enrichment, media rights and portable export are the primary gate. UI, cards, profile templates, filters, SEO-page generation, visual design and the final Astro/Instatic choice remain deferred.

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

## Dataset layer model

The project intentionally keeps evidence/source counts separate from reviewed identity counts.

- **96 rows — foundational deterministic seed:** checked-in IB, UK DfE BSO, French homologation, German KMK, SCU foreign-branch and AUC/MSCHE snapshots rebuilt by `build_authoritative_seed.py`.
- **106 rows — classified strong/authoritative universe:** the foundational research universe after reviewed CIS/Cognia expansion and scope review.
- **316 rows — current expanded D2.1 source/lead universe:** 106 strong/authoritative rows plus 210 British Council discovery rows.
- **30 reviewed institutions — current D2.2 identity layer:** explicit reviewed identities only; this is not inferred from the 316 source rows.
- **17 reviewed current-campus drafts across 15 institutions — current campus layer:** current-campus evidence only; topology is not yet exhaustive.

`96`, `106`, `316`, `30` and `17` describe different layers and must never be substituted for one another. Source/discovery rows are not unique-institution counts.

Reference: `tools/data-acquisition/international/DATASET-LAYERS.md`.

## D2.1 — Complete the institution universe

Status: **ACTIVE — 316 SOURCE/LEAD ROWS VERIFIED; DISCOVERY IS NOT YET EXHAUSTIVE**

### Strong/authoritative universe

The reproducible 106-row classified strong-source universe contains:

- 54 IB Egypt rows;
- 11 UK DfE British Schools Overseas rows;
- 17 French 2026–2027 homologation rows;
- 4 German KMK recognized-school rows;
- 9 SCU recognized foreign-university-branch rows;
- 1 AUC/MSCHE higher-education row;
- 6 CIS accreditation rows;
- 4 Cognia milestone rows.

Classification of these 106 source rows:

- **103 eligible**;
- **0 supporting candidates**;
- **3 excluded**.

All 54 captured IB rows have direct current PRIVATE/STATE review: 51 PRIVATE/eligible and 3 STATE/excluded. All 11 BSO rows have separate private/independent ownership review. CIS/Cognia evidence has separate scope/ownership review.

### British Council September 2026 discovery layer

The current British Council Partner Schools PDF is a discovery/contact source. Partner School or attached-centre status does **not** establish international eligibility.

Six browser-reviewed batches currently contain **210 British Council source rows**. The browser artifact records **126 rows with website references** and explicitly states that full PDF extraction is still incomplete.

Current primary re-sourcing state:

- **12 British Council rows** have separate high-confidence primary/recognized qualification;
- **198 British Council rows** remain supporting candidates;
- Partner School status itself contributes zero eligibility decisions;
- zero automatic identity creation;
- zero automatic merges;
- zero canonical/runtime database writes;
- zero public projection.

Current expanded D2.1 research classification:

- **115 eligible source/lead rows**;
- **198 supporting candidates**;
- **3 excluded rows**;
- **316 total source/lead rows**.

These are evidence/discovery records, not 316 unique institutions. A row may later resolve to an institution, campus, division, overlap with an existing identity or an out-of-scope entity.

Verified `EDU-DATA-2 British Council Discovery` run: **34923095404**.

### Source-family coverage and remaining D2.1 work

Already represented in the source registry and/or accepted evidence pipeline:

- IB;
- UK DfE BSO;
- British Council Partner Schools;
- French homologation;
- German KMK;
- CIS;
- Cognia milestone evidence;
- SCU foreign university branches;
- MOHESR foreign/international branch source registration;
- AUC/MSCHE;
- institution official websites;
- Wikimedia Commons;
- Overture Places;
- OpenStreetMap;
- Edarabia reference-only discovery;
- Edu Hub V7 owned archive.

D2.1 remains open until likely in-scope coverage is substantially exhausted. The next acquisition/reconciliation priorities are:

1. finish British Council PDF extraction beyond the current 210 reviewed rows and continue primary re-sourcing;
2. complete broader Cognia Egypt accredited-institution discovery beyond the four milestone rows, without treating accreditation alone as international eligibility;
3. reconcile SCU and MOHESR foreign-university-branch coverage, naming and lifecycle state;
4. use Edarabia only as controlled manual gap discovery, then re-source every useful lead from permitted primary/authoritative evidence;
5. use Overture/OSM as supporting identity/geography gap checks under their license/attribution rules;
6. reconcile useful V7 leads only after current re-sourcing;
7. use institution/operator websites to close discovery gaps and confirm current identity/campus/provider relationships.

## D2.2 — Clean identities, providers, campuses and divisions

Status: **ACTIVE IN PARALLEL WITH OPEN D2.1 DISCOVERY**

Current verified discovery-identity materialization:

- **30 reviewed institution drafts**;
- **10 reviewed school-division drafts**;
- **51 reviewed source-or-lead memberships**;
- **67 original strong-source rows** still in the explicit identity-review queue;
- **12 qualified British Council discovery rows** processed by discovery identity review;
- **198 unqualified British Council discovery rows** remain outside identity review;
- **0 qualified discovery rows pending an identity decision**;
- 0 automatic merges;
- 0 canonical/runtime database writes;
- 0 public projection.

The remaining original-source identity queue is currently:

- 41 IB rows;
- 16 French homologation rows;
- 9 SCU foreign-university-branch rows;
- 1 AUC/MSCHE row.

The current discovery identity model supports three explicit relationship types rather than collapsing provenance:

- a qualified discovery can create a new reviewed identity through an explicit checked-in decision;
- a qualified discovery can reconcile to an exact still-queued original source row through an explicit source-to-source decision;
- a qualified discovery can attach as an additional membership to an already-reviewed identity without creating another institution.

Verified `EDU-DATA-2 Discovery Identity Review` run: **34923122094**.

### Campus state

The campus model supports multiple explicitly evidenced current campuses while preserving non-exhaustive topology.

Current verified aggregate campus state:

- **17 reviewed current-campus drafts**;
- **15 of 30 reviewed institutions** have at least one reviewed current campus;
- **2 institutions** currently have multiple reviewed campuses:
  - Capital International Schools — Main Campus + Lotus Campus;
  - Mount International School Community — New Administrative Capital + Al-Shorouk;
- **15 reviewed institutions** still require current-campus review;
- **0 campus structures declared exhaustive/complete**;
- **0 additional campuses inferred or ruled out automatically**;
- **0 canonical campus rows/database writes/public projection**.

The aggregate Campus Review CI was repaired to rebuild the same current identity/campus chain used by the incremental workflow and to derive expected incremental totals from checked-in campus decision batches instead of validating only the historical first nine campuses.

Verified aggregate `EDU-DATA-2 Campus Review` run: **34972560009**.

## D2.3 — Complete EN + AR architecture

Status: **ARCHITECTURE IMPLEMENTED / CONTENT INCOMPLETE**

English and Arabic are first-class localizations of the same factual entity graph. Language-neutral facts exist once. Localized names, descriptions and display text carry language, source/origin and review status.

Official Arabic names are preferred. Transliteration/editorial Arabic is allowed only when explicitly labeled as non-official. Source-row Arabic gaps remain a research queue and must not be confused with canonical institution localization completeness after reconciliation.

## D2.4 — Enrich every eligible institution

Status: **STARTED / FIRST HIGH-PRIORITY PACKAGE GREEN / BROADER COVERAGE PENDING**

The existing reviewed enrichment package covers a first high-priority set with source-backed website, location, contact, admissions, curriculum/programme, education-range and selected facility/provider/history/regulatory facts.

Missing values remain missing. Current and historical facts are separated. Historical fee material is never promoted as current. Broader enrichment attaches only after identity/campus/division scope is understood.

## D2.5 — Complete media references and rights

Status: **STARTED**

The reviewed seed contains 5 publication-safe Wikimedia assets with creator/license/attribution metadata. Institution/commercial-site imagery is discovery-only unless a defensible reuse basis exists.

Every final reviewed institution must receive a terminal media state. `placeholder_required` is valid when no publication-safe image exists.

## D2.6 — Audit completeness

Status: **ARCHITECTURE IMPLEMENTED / FULL CANONICAL AUDIT PENDING**

Completeness will be measured independently across factual coverage, English localization, Arabic localization, media, provenance/freshness and unresolved conflicts. Conflicting assertions remain review work rather than being silently overwritten.

## D2.7 — Freeze portable master database

Status: **NOT STARTED**

The final presentation-neutral export must include reviewed providers/institutions/campuses/divisions, EN/AR localizations and aliases, source/evidence references, curricula/certificates/accreditation, admissions and versioned fees, higher-education programmes/units, contacts/geography/facilities, media rights/attribution, conflicts/review state and completeness metrics.

It must not require Astro, Instatic or Supabase.

## Current accepted CI checkpoint

Latest aggregate/current proofs:

- `EDU-DATA-2 British Council Discovery` — **34923095404** — green — 210 discovery rows / 12 qualified / 198 unresolved;
- `EDU-DATA-2 Discovery Identity Review` — **34923122094** — green — 30 reviewed institutions / 51 memberships;
- aggregate `EDU-DATA-2 Campus Review` — **34972560009** — green — 17 reviewed current campuses across 15 institutions;
- `EDU-DATA-2 International Registry` — **34972805842** — green — foundational registry, acquisition-contract and bilingual reference-schema validation.

Important earlier accepted gates remain preserved in Git history and workflow history, including foundational registry, accreditor expansion/scope review, complete IB ownership review, BSO scope review, localization evidence, official-site enrichment, division schema, incremental identity review and multi-campus review.

## Immediate next actions

1. Continue **D2.1**, not D2.3/D2.4 bulk completion yet: exhaust remaining likely institution sources and discovery gaps.
2. Finish British Council extraction/review beyond **210 rows** and prioritize high-signal candidates for current primary/recognized qualification.
3. Build the broader Cognia Egypt accreditation discovery set and keep accreditation evidence separate from international-model/private-ownership eligibility.
4. Reconcile SCU/MOHESR higher-education branch universes and parent/branch naming/lifecycle relationships.
5. Run controlled Edarabia reference-only gap discovery and re-source any leads from official/permitted sources.
6. Run Overture/OSM and V7 gap checks as supporting discovery only.
7. Continue D2.2 identity review across the remaining **67 original rows** and any newly qualified discoveries.
8. Continue campus review across the remaining **15 reviewed institutions** without asserting exhaustive topology prematurely.
9. Then expand D2.3 official Arabic evidence, D2.4 first-party enrichment and D2.5 rights-safe media toward every reviewed eligible identity.
10. Build D2.6 completeness metrics only after materially broader identity/enrichment coverage, then freeze D2.7.

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