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

Status: **ACTIVE — 604-ROW UNIVERSE STABLE; 193 HIGH-SIGNAL SCHOOL ROWS REMAIN OUTSTANDING**

### Accepted checkpoint

`EDU-DATA-2 D2.1 Universe Checkpoint` run **35025758910** is green at head `7a1654aae28de18cdbc5d0273294187008ec7c35` and proves:

- **604 source/evidence rows**;
- **135 eligible**;
- **466 supporting candidates**;
- **3 excluded**;
- 266 high-signal pre-university Overture rows;
- **75 explicitly reviewed school rows**;
- **73 resolved/explained**;
- **2 reviewed-but-unresolved**;
- **191 unreviewed**;
- **193 outstanding**;
- zero fuzzy automatic merges;
- zero canonical identities created;
- zero runtime database mutation;
- zero public projection.

### Completed major source/review families

The current D2.1 checkpoint includes the 226-row British Council layer, complete 256-row Cognia Egypt registry, 6-row Canadian offshore-school authorization family, 7-row ZfA DAS Egypt family, the 5-row substantive-international HE review package, and the explicit Mansoura College provider/school topology review.

### Overture supporting-gap state

Current Overture Places release: `2026-08-19.0`. Overture remains supporting discovery only.

- **1,042 Egypt-only supporting rows**;
- **141 exact normalized-name overlaps** with the 604-row universe;
- **266 high-signal pre-university rows**;
- **70 post-overlay higher-ed review rows — complete**;
- **565 lower-priority supporting rows**.

#### High-signal schools — active cursor

Eight school-resolution batches now cover **75 of 266** rows:

- 73 resolved/explained;
- 2 reviewed but unresolved (`Kada Modern British School`, `M.S.G International British School`);
- 191 unreviewed;
- **193 outstanding**.

Batch 8 explicitly reviewed Delta College International School, Riada American School, Tiba International School - American Division, Egyptian English Language School / American Division, The Modern American School of Egypt and Victory College American Department. Provider/division/campus distinctions remain explicit: Delta College, EELS and Victory are topology cases, while MASE retains its current multi-campus evidence instead of being flattened into one address.

AIA International School, Delta American School and the two Sunrise International School Hurghada place rows remain held back pending stronger evidence.

### OSM diagnostic

Accepted OSM diagnostic run **34997269459** remains green as a diagnostic. Hosted Overpass access failure is not treated as zero OSM coverage.

### V7 archive

`tools/data-acquisition/international/build_v7_international_gap_review.py` remains ready for read-only exact-name comparison against the owned **24,916-row V7** archive. Useful unmatched leads must be re-sourced from current permitted evidence before altering the accepted universe.

### Remaining D2.1 work — exact order

1. **Continue the 193 outstanding high-signal school rows** in small checked-in batches.
2. **Execute the V7 read-only comparison** against all 24,916 owned rows when filesystem access is available.
3. **Run controlled Edarabia reference-only discovery**; do not bulk store or reproduce Edarabia content.
4. **Run institution/operator primary-source exhaustion** for remaining likely gaps and topology ambiguity.
5. Rebuild final D2.1, synchronize canonical docs/Issue #8, and record explicit D2.1 closure before making D2.2 the sole active cursor.

## D2.2 — Clean identities/providers/campuses/divisions

Status: **PARTIALLY BUILT / SECONDARY WHILE D2.1 REMAINS OPEN**

Current accepted review state remains 30 reviewed institution drafts, 10 reviewed school-division drafts, 51 reviewed source/lead memberships, 67 original strong-source rows in the explicit identity-review queue, and 17 reviewed current-campus drafts across 15 institutions. New D2.1 evidence may not auto-materialize into canonical identities.

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

- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35025758910** — green — 604 rows / 135 eligible / 466 supporting / 3 excluded; 75 school rows reviewed; 193 outstanding.
- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35025256648** — green — batch 7 baseline; 69 reviewed; 199 outstanding.
- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35024492612** — green — batch 6 baseline; 64 reviewed; 204 outstanding.
- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35022596202** — green — batch 5 baseline; 55 reviewed; 213 outstanding.
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
