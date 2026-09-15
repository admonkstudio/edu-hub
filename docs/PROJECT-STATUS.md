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

## Active milestone and gate

**Active milestone:** `EDU-DATA-2 — Egypt International Education Registry`

**Active branch:** `edu-data-2-international-registry`

**Current execution cursor:** `D2.1 — Complete the institution/source universe`

**Durable continuation:** `docs/EDU-DATA-2-CONTINUATION.md` and GitHub Issue #8.

Edu Hub remains a **data/research system before a website system**. Database completion, identity reconciliation, bilingual architecture, enrichment, media rights, completeness audit and portable export are the gate. Final Astro/Instatic selection, public templates, filter UX, visual design and public-page architecture remain deferred.

Canonical order remains:

`D2.1 universe → D2.2 identities → D2.3 EN/AR → D2.4 enrichment → D2.5 media → D2.6 audit → D2.7 portable freeze`

Supabase is not part of Edu Hub.

## Current dataset-layer state

Evidence/source counts and reviewed identity counts are deliberately separate.

- **96** foundational deterministic source rows.
- **106** historical classified strong-source rows.
- **226** British Council September 2026 discovery rows: 12 separately qualified, 214 supporting.
- **256** complete current Cognia Egypt registry rows.
- **6** current Canadian-authorized offshore-school rows.
- **7** current ZfA German Schools Abroad Egypt rows.
- **5** reviewed substantive-international higher-education rows: GIU, GUC, UFE, BUE and AASTMT.
- **2** reviewed eligible Mansoura College international-school evidence rows.
- **604** current accepted D2.1 source/evidence rows: **135 eligible / 466 supporting / 3 excluded**.
- **30** reviewed D2.2 institution drafts.
- **10** reviewed school-division drafts.
- **51** reviewed source/lead memberships.
- **17** reviewed current-campus drafts across 15 institutions.

`604` is **not** a unique-institution count.

Reference: `tools/data-acquisition/international/DATASET-LAYERS.md`.

## D2.1 — Complete institution/source universe

Status: **ACTIVE — 604-ROW MANSOURA CHECKPOINT VERIFIED; HIGH-SIGNAL SCHOOL/V7/REFERENCE GAP EXHAUSTION REMAINS**

### Accepted checkpoint

`EDU-DATA-2 D2.1 Universe Checkpoint` run **35010912245** is green at head `020b223368fc0fd4dcc1b148bfa61461c92e493a` and proves:

- **604 source/evidence rows**;
- **135 eligible**;
- **466 supporting candidates**;
- **3 excluded**;
- zero fuzzy automatic merges;
- zero canonical identities created;
- zero runtime database mutation;
- zero public projection.

The general `EDU-DATA-2 International Registry` validation immediately preceding the integration commit is green at run **35010762392** for the Mansoura topology overlay implementation.

### Completed major source/review families

The current D2.1 checkpoint includes the 226-row British Council layer, complete 256-row Cognia Egypt registry, 6-row Canadian offshore-school authorization family, 7-row ZfA DAS Egypt family, 9 current SCU foreign-university branches/AUC evidence retained in historical layers, the 5-row substantive-international HE review package, and the explicit Mansoura College provider/school topology review.

The five reviewed HE additions remain GIU, GUC, UFE, BUE and AASTMT under the evidence-based substantive-international rule. Egyptian incorporation or private/national legal form is not by itself exclusionary when separate current evidence establishes substantive binational, intergovernmental, transnational or international-organizational status. Foreign branding, partnership, validation or dual-degree arrangements alone remain insufficient.

### Mansoura College topology — COMPLETE

The rerouted Overture row `Mansoura College International Schools` has been reconciled against current first-party provider/admissions evidence without automatic merging.

The provider/campus umbrella currently presents four school units:

- Mansoura College Language School — national, provider context only;
- Modern Mansoura College Language School — national, provider context only; existing British Council row preserved as supporting provenance;
- Mansoura College British School — added as an eligible reviewed evidence row, with current primary evidence plus Pearson centre `92720` lifecycle evidence;
- Mansoura College 2 International American School — added as an eligible reviewed evidence row, with current primary evidence plus recognized Cognia/ACT evidence; original Cognia row preserved separately.

The provider umbrella is not materialized as a separate institution. The two national units are not added to the active international universe. British Council Partner, Cognia and Overture evidence do not independently grant eligibility.

Contract: `tools/data-acquisition/international/seeds/mansoura-college-topology-review-2026-09-15.json`.

### Overture supporting-gap state

Current Overture Places release: `2026-08-19.0`.

Egypt-filtered layer remains:

- 1,121 bbox candidates;
- 79 non-Egypt rows rejected;
- **1,042 Egypt-only supporting rows**;
- **141 exact normalized-name overlaps** with the 604-row universe;
- **901 unmatched supporting rows / 865 unmatched normalized names**;
- **266 high-signal pre-university rows**;
- **70 post-overlay higher-ed review rows**;
- **565 lower-priority supporting rows**.

The Mansoura additions do not alter those Overture comparison counts.

#### Higher education — complete

The entire 70-row post-overlay HE queue has explicit checked-in decisions and **0 outstanding HE rows**: 14 existing eligible HE aliases/subunits; 21 out-of-scope Egyptian HE rows/subunits; 33 supporting-only ambiguous academy/training/institute leads; 1 school category error resolving to existing EBIS evidence; and the Mansoura provider row now closed through the explicit topology review.

#### High-signal schools — active next cursor

The existing two school-resolution batches cover 30 of 266 high-signal pre-university rows:

- 28 resolved/explained;
- 2 reviewed but unresolved (`Kada Modern British School`, `M.S.G International British School`);
- 236 unreviewed;
- **238 outstanding in the current school-review artifact**.

The separately rerouted Mansoura case is complete and no longer adds an extra follow-up outside those 238 rows.

Overture never grants eligibility or creates/merges identities.

### OSM diagnostic

Accepted OSM diagnostic run **34997269459** remains green as a diagnostic. All 12 public-Overpass Egypt tiles were blocked from hosted CI. The pipeline records `environment_blocked_all_tiles`; failed access is not treated as zero OSM candidates.

### V7 archive

`tools/data-acquisition/international/build_v7_international_gap_review.py` is ready for read-only matching against the owned **24,916-row** V7 archive. It performs exact normalized-name overlap only and cannot grant eligibility or create identities. It has not yet been executed against the live owned V7 filesystem in this D2.1 pass.

Any useful V7 unmatched lead must be re-sourced from current permitted evidence before altering the accepted universe.

### Remaining D2.1 work — exact order

1. **Continue the 238 outstanding high-signal school rows** in small checked-in batches; prioritize authoritative coverage, explicit aliases, provider/campus/division topology, then genuinely new re-sourced candidates.
2. **Execute the V7 read-only comparison** against all 24,916 owned rows when filesystem access is available; re-source every useful unmatched lead.
3. **Run controlled Edarabia reference-only discovery**; do not bulk store or reproduce Edarabia content.
4. **Run the institution/operator primary-source exhaustion pass** for remaining likely gaps and topology ambiguity.
5. Rebuild final D2.1, synchronize all canonical docs/Issue #8, and record explicit D2.1 closure before making D2.2 the sole active cursor.

## D2.2 — Clean identities/providers/campuses/divisions

Status: **PARTIALLY BUILT / SECONDARY WHILE D2.1 REMAINS OPEN**

Current accepted review state:

- 30 reviewed institution drafts;
- 10 reviewed school-division drafts;
- 51 reviewed source/lead memberships;
- 67 original strong-source rows remain in the explicit identity-review queue;
- 17 reviewed current-campus drafts across 15 institutions;
- two reviewed institutions currently have multiple reviewed campuses;
- zero automatic merges, runtime DB writes or public projection.

New Cognia, Canadian, ZfA, substantive-HE, Mansoura, Overture and V7 evidence must pass explicit D2.2 reconciliation after D2.1 closure.

Accepted Discovery Identity Review run: **34994994433**. Accepted aggregate Campus Review run: **34972560009**.

## D2.3 — Complete EN + AR architecture

Status: **ARCHITECTURE IMPLEMENTED / CONTENT INCOMPLETE**

English and Arabic remain first-class localizations over one factual entity graph. Official Arabic forms are preferred; transliteration/editorial Arabic must remain explicitly labeled.

## D2.4 — Enrich every eligible institution

Status: **STARTED / BROADER COVERAGE PENDING**

Enrichment must attach only after identity/campus/division scope is understood and must retain source/lifecycle/academic-year provenance.

## D2.5 — Media and rights

Status: **STARTED**

Every final institution must reach a terminal media state. `placeholder_required` is valid when no publication-safe image exists.

## D2.6 — Completeness audit

Status: **ARCHITECTURE IMPLEMENTED / FULL CANONICAL AUDIT PENDING**

Audit factual coverage, EN, AR, media, provenance/freshness and unresolved conflicts independently.

## D2.7 — Portable master freeze

Status: **NOT STARTED**

Freeze a deterministic presentation-neutral master export before choosing Astro-first vs Instatic-first or beginning public product implementation.

## Current accepted CI

- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35010912245** — green — 604 rows / 135 eligible / 466 supporting / 3 excluded; Mansoura topology complete; Overture comparison unchanged.
- `EDU-DATA-2 International Registry` — **35010762392** — green — Mansoura topology implementation/schema/acquisition/import safety contracts prior to the final universe integration commit.
- `EDU-DATA-2 OSM Supporting Discovery` — **34997269459** — green diagnostic — hosted Overpass blocked, no false zero-coverage claim.
- `EDU-DATA-2 Cognia Egypt Registry` — **34977754806** — green — complete 256-row Egypt registry.
- `EDU-DATA-2 British Council Discovery` — **34994994601** — green — 226 rows / 12 qualified / 214 supporting.
- `EDU-DATA-2 Discovery Identity Review` — **34994994433** — green — 30 institutions / 10 divisions / 51 memberships.
- `EDU-DATA-2 Higher-Ed Branch Reconciliation` — **34973583179** — green — 9 SCU current foreign branches plus Ryerson/TMU lifecycle conflict.
- `EDU-DATA-2 Campus Review` — **34972560009** — green — 17 current campuses across 15 reviewed institutions.

## Non-negotiable constraints

- no frontend/CMS architecture decision before database completion;
- no Supabase and no Ask Kalam infrastructure/data mixing;
- no eligibility inference from branding, Cognia alone, British Council Partner status, OSM/Overture, V7 or commercial directories;
- no unsupported facts, fees, rankings, accreditations or admissions claims;
- no Edarabia bulk storage/reproduction without permission;
- no publication of media without recorded rights basis;
- no raw/staging publication;
- no fuzzy automatic identity merge;
- no automatic uniqueness assumption for unmatched source rows;
- no exhaustive campus claim from one known address;
- no institution-wide claim from division-scoped evidence;
- preserve EN/AR parity, provenance, portability, lifecycle and review state throughout.
