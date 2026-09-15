# EDU-DATA-2 Continuation Roadmap

Last updated: 2026-09-16

This file is the **durable continuation cursor for active Edu Hub work**. Read it after `AGENTS.md`, `docs/PROJECT-STATUS.md`, and `docs/PROJECT-DECISIONS.md` before changing code or data.

Visible tracker: **GitHub Issue #8 — `EDU-DATA-2 Continuation Roadmap — D2.1 → D2.7`**.

## 1. Active scope

- Repository: `admonkstudio/edu-hub`
- Branch: `edu-data-2-international-registry`
- Milestone: `EDU-DATA-2 — Egypt International Education Registry`
- Active stage: `D2.1 — Complete the institution/source universe`
- Frontend/CMS choice: **deferred until D2.7**
- Supabase: **not part of Edu Hub**

Canonical sequence:

`D2.1 universe → D2.2 identities → D2.3 EN/AR → D2.4 enrichment → D2.5 media → D2.6 audit → D2.7 portable freeze → Astro/Instatic decision → public product build`

## 2. Last accepted checkpoint

- Workflow: `EDU-DATA-2 D2.1 Universe Checkpoint`
- Accepted run: **35025758910**
- Accepted head: **`7a1654aae28de18cdbc5d0273294187008ec7c35`**
- Conclusion: **green**

Accepted source/evidence universe remains:

- **604 total source/evidence rows**
- **135 eligible**
- **466 supporting candidates**
- **3 excluded**

`604` is **not** a unique-institution count.

## 3. Completed/frozen major source and review families

- 96-row foundational deterministic seed;
- 106-row historical classified strong-source layer;
- 226-row British Council September 2026 discovery layer;
- 256-row complete Cognia Egypt registry;
- 6 current Canadian offshore-school authorization rows;
- 7 current ZfA DAS Egypt rows;
- 9 current SCU foreign-university branches with Ryerson/TMU lifecycle conflict preserved;
- AUC substantive international/accreditation evidence;
- 5-row reviewed substantive-international HE package: GIU, GUC, UFE, BUE and AASTMT;
- Mansoura College provider/school topology review.

The 70-row Overture higher-education queue is complete with zero outstanding rows. Mansoura College topology is complete. Do not restart either absent changed evidence/regression.

## 4. Current Overture state

Overture Places release: `2026-08-19.0`.

Current Egypt-only acquisition remains:

- 1,121 bbox candidates;
- 79 non-Egypt rows rejected;
- **1,042 Egypt-only rows**;
- **141 exact normalized-name overlaps** with the 604-row universe;
- **901 unmatched rows / 865 unmatched normalized names**;
- **266 high-signal pre-university rows**;
- **70 post-overlay higher-ed review rows**;
- **565 lower-priority supporting rows**.

Overture remains supporting discovery only and grants zero eligibility.

### High-signal school review — ACTIVE NEXT CURSOR

Builder: `tools/data-acquisition/international/apply_overture_gap_resolutions.py`.

Accepted decision batches:

- `overture-gap-resolution-2026-09-15-batch1.json`
- `overture-gap-resolution-2026-09-15-batch2.json`
- `overture-gap-resolution-2026-09-15-batch3.json`
- `overture-gap-resolution-2026-09-15-batch4.json`
- `overture-gap-resolution-2026-09-15-batch5.json`
- `overture-gap-resolution-2026-09-15-batch6.json`
- `overture-gap-resolution-2026-09-16-batch7.json`
- `overture-gap-resolution-2026-09-16-batch8.json`

Accepted run `35025758910` proves:

- **266 input rows**;
- **75 explicitly reviewed**;
- **73 resolved/explained**;
- **2 reviewed-but-unresolved**;
- **191 unreviewed**;
- **193 outstanding**.

Reviewed unresolved rows remain `Kada Modern British School` and `M.S.G International British School`.

Batch 8 explicitly reconciled:

- `Delta College International School` → Quesna provider/international-school topology requiring D2.2;
- `Riada American School` → current Cognia American-division source identity in Smouha, Alexandria;
- `Tiba International School - American Division` → current Cognia American-division source identity in Alexandria;
- `Egyptian English Language School (E.E.L.S.) / American Division` → current EELS provider identity with American division preserved for D2.2;
- `The Modern American School Of Egypt` → current MASE identity with 2000/2017 campus context preserved for D2.2;
- `Victory College American Department` → current Victory College provider identity with American department preserved for D2.2.

No canonical institution was created and no eligibility was granted by Overture, Cognia, ACT recognition or British Council Partner status.

### Held back

- `AIA International School`: New Cairo Overture row vs Alexandria authoritative school evidence.
- `Delta American School`: insufficient current evidence for a safe mapping.
- two `Sunrise International School` Hurghada Overture rows: insufficient first-party evidence connecting both place rows to the accepted `New Sunrise International School` source row; do not auto-deduplicate them.

## 5. Exact resume cursor — START HERE

### Task A — continue the 193 outstanding high-signal school rows

Work in small deterministic checked-in batches. Preferred outcome order:

1. exact/current authoritative family coverage;
2. explicit source alias;
3. provider/campus/division topology requiring later D2.2 review;
4. genuinely new candidate with current permitted primary/recognized-source evidence;
5. unresolved supporting-only lead.

Continue from the unreviewed artifact produced by accepted run `35025758910`. Exact Overture IDs are mandatory; fuzzy similarity is research triage only.

The next evidence-rich group already isolated includes Beverly Hills American division, Cadmus International School New Administrative Capital, Cairo British College, Capital International School / Hadayek October, Dome/Genius Dome, Pioneers IGCSE, Thebes, Kaumeya American Department, Mount International branch rows, Noor/NILS Damietta, Port Said International School and Kenana American division. Preserve provider/division/campus distinctions and leave ambiguous rows unresolved rather than forcing aliases.

### Task B — execute V7 read-only comparison

Matcher: `tools/data-acquisition/international/build_v7_international_gap_review.py`.

Owned V7 contract: **24,916 raw rows**, read-only, exact normalized-name overlap only, unmatched international-signal leads only, zero eligibility and zero canonical identities from V7 itself.

Any useful V7 unmatched lead must be re-sourced from current permitted evidence.

### Task C — Edarabia reference-only gap pass

Use Edarabia only as a discovery/reference index. Do not bulk scrape, systematically store or reproduce Edarabia content. Re-source every useful lead from institution-primary/regulatory/accreditor evidence.

### Task D — primary-source exhaustion pass

Use institution/operator primary sites and recognized source families to close remaining likely gaps and provider/campus/division ambiguity.

## 6. OSM status

Accepted OSM diagnostic run: **34997269459 — green diagnostic**. All 12 tiled public-Overpass attempts were blocked from GitHub-hosted CI. `environment_blocked_all_tiles` is diagnostic state and must never be interpreted as zero OSM candidates.

## 7. Current D2.2 state — not the primary cursor yet

Current accepted review artifacts remain 30 reviewed institution drafts, 10 reviewed division drafts, 51 reviewed source/lead memberships, 67 original strong-source rows queued, and 17 reviewed current campuses across 15 institutions. New D2.1 evidence may not auto-materialize into canonical identities.

## 8. D2.1 exit criteria

D2.1 may close only when:

- Overture HE queue is complete — **DONE**;
- Mansoura provider/school topology follow-up is complete — **DONE**;
- high-signal school review is substantially exhausted and residual unresolved rows are explicitly documented;
- OSM limitation remains documented without a false zero-coverage claim — **DONE**;
- V7 comparison is executed or explicitly blocked with durable evidence;
- controlled Edarabia reference-only gap review is complete;
- useful archive/directory leads are re-sourced from permitted current sources;
- major authoritative Egypt source families are checked;
- final source/evidence universe rebuilds reproducibly with green CI;
- source-row counts are never labeled as unique institutions;
- zero fuzzy auto-merge, unsupported eligibility, runtime DB mutation or public projection occurred;
- canonical docs and Issue #8 agree;
- an explicit closure decision hands the sole cursor to D2.2.

## 9. Non-negotiable rules

- source/discovery rows never automatically become canonical institutions;
- source-row counts are not unique-institution counts;
- no international eligibility from branding alone;
- no fuzzy identity merge;
- no campus inference from one address;
- no institution-wide assertion from division-scoped evidence;
- preserve lifecycle/historical status explicitly;
- British Council Partner status, Cognia, Overture/OSM, V7 and commercial directories do not independently establish eligibility;
- no Edarabia bulk storage/reproduction without permission;
- no raw/staging publication;
- no frontend/runtime work before the database completion gate;
- preserve EN/AR, provenance, portability, rights and review state.

## 10. Startup files for every continuation agent

1. `AGENTS.md`
2. `docs/PROJECT-STATUS.md`
3. `docs/PROJECT-DECISIONS.md`
4. `docs/EDU-DATA-2-CONTINUATION.md`
5. GitHub Issue #8
6. `tools/data-acquisition/international/DATASET-LAYERS.md`
7. `.github/workflows/edu-data-2-universe-checkpoint.yml`
8. relevant builders/seeds for the current task

Inspect actual branch state and latest green CI before trusting historical conversation counts.

## 11. Handoff discipline

After every material accepted checkpoint:

1. commit deterministic code/evidence/review decisions;
2. obtain green CI;
3. update `DATASET-LAYERS.md` if counts changed;
4. update `PROJECT-STATUS.md` and `PROJECT-DECISIONS.md` when status/contracts changed;
5. update this continuation file with accepted run/counts and exact next cursor;
6. update GitHub Issue #8;
7. never leave the next agent dependent on chat history.

This file and Issue #8 describe the **last verified accepted state**, never merely planned or in-progress work.
