# Edu Hub Project Status

Last updated: 2026-09-16

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

Status: **ACTIVE — 604-ROW UNIVERSE STABLE; 199 HIGH-SIGNAL SCHOOL ROWS REMAIN OUTSTANDING**

### Accepted checkpoint

`EDU-DATA-2 D2.1 Universe Checkpoint` run **35025256648** is green at head `7aa5f49ddf90cf5cf36f5fc55da80bf040f1ceda` and proves:

- **604 source/evidence rows**;
- **135 eligible**;
- **466 supporting candidates**;
- **3 excluded**;
- 266 high-signal pre-university Overture rows;
- **69 explicitly reviewed school rows**;
- **67 resolved/explained**;
- **2 reviewed-but-unresolved**;
- **197 unreviewed**;
- **199 outstanding**;
- zero fuzzy automatic merges;
- zero canonical identities created;
- zero runtime database mutation;
- zero public projection.

### Completed major source/review families

The current D2.1 checkpoint includes the 226-row British Council layer, complete 256-row Cognia Egypt registry, 6-row Canadian offshore-school authorization family, 7-row ZfA DAS Egypt family, the 5-row substantive-international HE review package, and the explicit Mansoura College provider/school topology review.

### Mansoura College topology — COMPLETE

The provider/campus umbrella currently presents four school units. Mansoura College Language School and Modern Mansoura College Language School remain national/provider context. Mansoura College British School and Mansoura College 2 International American School are the only two new eligible reviewed evidence rows. The provider umbrella is not a separate institution and old Cognia/British Council rows remain separate provenance.

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

Overture never grants eligibility or creates/merges identities.

#### Higher education — complete

The entire 70-row post-overlay HE queue has explicit checked-in decisions and **0 outstanding HE rows**.

#### High-signal schools — active next cursor

Seven school-resolution batches now cover **69 of 266** rows:

- 67 resolved/explained;
- 2 reviewed but unresolved (`Kada Modern British School`, `M.S.G International British School`);
- 197 unreviewed;
- **199 outstanding**.

Batch 7 explicitly reviewed City International Schools in Zamalek, St. Fatima International School Al Hegaz, Future British International School - Tanta, Producer of Life International School in Hurghada, and Summits International Schools. City International and Summits remain provider/division topology work; the Future British Overture coordinate defect is preserved and does not override the exact Tanta address/source evidence.

Sunrise International School Hurghada remains held back because two separate Overture rows still require stronger first-party evidence connecting them to the accepted `New Sunrise International School` source identity. AIA International School and Delta American School also remain unforced pending stronger evidence.

### OSM diagnostic

Accepted OSM diagnostic run **34997269459** remains green as a diagnostic. All 12 public-Overpass Egypt tiles were blocked from hosted CI. The pipeline records `environment_blocked_all_tiles`; failed access is not treated as zero OSM candidates.

### V7 archive

`tools/data-acquisition/international/build_v7_international_gap_review.py` remains ready for read-only matching against the owned **24,916-row V7** archive. It performs exact normalized-name overlap only and cannot grant eligibility or create identities. It has not yet been executed against the live owned V7 filesystem in this D2.1 pass.

Any useful V7 unmatched lead must be re-sourced from current permitted evidence before altering the accepted universe.

### Remaining D2.1 work — exact order

1. **Continue the 199 outstanding high-signal school rows** in small checked-in batches; prioritize authoritative coverage, explicit aliases, provider/campus/division topology, then genuinely new re-sourced candidates.
2. **Execute the V7 read-only comparison** against all 24,916 owned rows when filesystem access is available; re-source every useful unmatched lead.
3. **Run controlled Edarabia reference-only discovery**; do not bulk store or reproduce Edarabia content.
4. **Run the institution/operator primary-source exhaustion pass** for remaining likely gaps and topology ambiguity.
5. Rebuild final D2.1, synchronize all canonical docs/Issue #8, and record explicit D2.1 closure before making D2.2 the sole active cursor.

## D2.2 — Clean identities/providers/campuses/divisions

Status: **PARTIALLY BUILT / SECONDARY WHILE D2.1 REMAINS OPEN**

Current accepted review state remains 30 reviewed institution drafts, 10 reviewed school-division drafts, 51 reviewed source/lead memberships, 67 original strong-source rows in the explicit identity-review queue, and 17 reviewed current campuses across 15 institutions. New D2.1 evidence may not auto-materialize into canonical identities.

Accepted Discovery Identity Review run: **34994994433**. Accepted aggregate Campus Review run: **34972560009**.

## D2.3 — Complete EN + AR architecture

Status: **ARCHITECTURE IMPLEMENTED / CONTENT INCOMPLETE**.

## D2.4 — Enrich every eligible institution

Status: **STARTED / BROADER COVERAGE PENDING**.

## D2.5 — Media and rights

Status: **STARTED**.

## D2.6 — Completeness audit

Status: **ARCHITECTURE IMPLEMENTED / FULL CANONICAL AUDIT PENDING**.

## D2.7 — Portable master freeze

Status: **NOT STARTED**.

## Current accepted CI

- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35025256648** — green — 604 rows / 135 eligible / 466 supporting / 3 excluded; 69 school rows reviewed; 199 outstanding.
- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35024492612** — green — batch 6 baseline; 64 school rows reviewed; 204 outstanding.
- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35022596202** — green — batch 5 baseline; 55 school rows reviewed; 213 outstanding.
- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35021835175** — green — batch 4 baseline; 50 school rows reviewed; 218 outstanding.
- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35021093103** — green — batch 3 baseline; 41 school rows reviewed; 227 outstanding.
- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35010912245** — green — accepted Mansoura topology integration baseline.
- `EDU-DATA-2 OSM Supporting Discovery` — **34997269459** — green diagnostic.
- `EDU-DATA-2 Cognia Egypt Registry` — **34977754806** — green — complete 256-row Egypt registry.
- `EDU-DATA-2 British Council Discovery` — **34994994601** — green — 226 rows / 12 qualified / 214 supporting.
- `EDU-DATA-2 Discovery Identity Review` — **34994994433** — green — 30 institutions / 10 divisions / 51 memberships.
- `EDU-DATA-2 Higher-Ed Branch Reconciliation` — **34973583179** — green.
- `EDU-DATA-2 Campus Review` — **34972560009** — green.

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
