# EDU-DATA-2 Continuation Roadmap

Last updated: 2026-09-15

This file is the **durable continuation cursor for active Edu Hub work**. A new agent must be able to resume correctly from this file even if prior chat context is unavailable.

Read it after `AGENTS.md`, `docs/PROJECT-STATUS.md`, and `docs/PROJECT-DECISIONS.md` before changing code or data.

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

Do not skip ahead to website implementation.

## 2. Last accepted checkpoint

Current accepted D2.1 checkpoint:

- Workflow: `EDU-DATA-2 D2.1 Universe Checkpoint`
- Accepted run: **35010912245**
- Accepted head: **`020b223368fc0fd4dcc1b148bfa61461c92e493a`**
- Conclusion: **green**
- General `EDU-DATA-2 International Registry` Mansoura implementation run immediately preceding the integration commit: **35010762392 — green**

Accepted source/evidence universe:

- **604 total source/evidence rows**
- **135 eligible**
- **466 supporting candidates**
- **3 excluded**

`604` is **not** a unique-institution count.

Current construction:

- 332 pre-Cognia-current reviewed source/lead rows after British Council expansion;
- complete 256-row Cognia registry replaces the four historical milestone rows for current counting → 584;
- +6 current Canadian offshore-school authorization rows → 590;
- +7 current ZfA German Schools Abroad Egypt rows → 597;
- +5 reviewed substantive-international higher-education rows → 602;
- +2 reviewed eligible Mansoura College international-school evidence rows → **604**.

Historical source snapshots remain preserved.

## 3. Completed/frozen major source and review families

- 96-row foundational deterministic seed;
- 106-row historical classified strong-source layer;
- 226-row British Council September 2026 discovery layer;
- 256-row complete Cognia Egypt registry;
- 6 current Canadian offshore-school authorization rows;
- 7 current ZfA DAS Egypt rows;
- 9 current SCU foreign-university branches with Ryerson/TMU kept as lifecycle conflict only;
- AUC substantive international/accreditation evidence;
- 5-row reviewed substantive-international HE package: GIU, GUC, UFE, BUE and AASTMT;
- Mansoura College provider/school topology review.

### Higher-education scope rule

Egyptian incorporation, private-university classification or national legal form does not automatically exclude an institution when separate current evidence establishes substantive **binational, intergovernmental, transnational or international-organizational status**. A foreign name, partnership, validated programme or dual degree alone remains insufficient.

Checked-in review package:

`tools/data-acquisition/international/seeds/substantive-international-higher-ed-review-2026-09-15.json`

### Mansoura College topology — COMPLETE

Checked-in review package:

`tools/data-acquisition/international/seeds/mansoura-college-topology-review-2026-09-15.json`

Current first-party provider/admissions evidence establishes one Mansoura College educational campus/group with four school units. The accepted review does **not** materialize the umbrella as a canonical institution.

- Mansoura College Language School — national, provider context only.
- Modern Mansoura College Language School — national, provider context only; British Council Partner row preserved as separate supporting provenance.
- Mansoura College British School — eligible reviewed evidence row; current primary evidence plus Pearson centre `92720` lifecycle evidence.
- Mansoura College 2 International American School — eligible reviewed evidence row; current primary evidence plus recognized Cognia/ACT evidence; original Cognia row preserved separately.

The Overture row `Mansoura College International Schools` (`9e34fa47-a93e-4c90-a902-9a8181834ec2`) is reviewed as a provider-umbrella alias, not a separate school institution.

No automatic source-row merge, canonical institution creation, runtime DB mutation or public projection occurred.

## 4. Current Overture state

Overture Places release: `2026-08-19.0`.

Current Egypt-only acquisition:

- 1,121 bbox candidates;
- 79 non-Egypt rows rejected by Overture address country;
- **1,042 Egypt-only rows**;
- **141 exact normalized-name overlaps** with the 604-row universe;
- **901 unmatched rows**;
- **865 unmatched normalized names**;
- **266 high-signal pre-university rows**;
- **70 post-overlay higher-ed review rows**;
- **565 lower-priority supporting rows**.

The two Mansoura additions do not alter these Overture comparison counts. Overture remains supporting discovery only and grants zero eligibility.

### Higher-education Overture review — COMPLETE

The complete 70-row HE queue has **0 outstanding rows**:

- 14 existing eligible HE aliases/departments/subunits;
- 21 out-of-scope Egyptian HE rows/subunits without sufficient substantive-international status;
- 33 supporting-only academy/training/institute leads with no qualifying current HE evidence;
- 1 school category error resolving to existing Egypt British International School BSO evidence;
- 1 school/provider category error (`Mansoura College International Schools`) now closed by the explicit topology review above.

Do not restart this review.

### High-signal school review — ACTIVE NEXT CURSOR

Builder:

`tools/data-acquisition/international/apply_overture_gap_resolutions.py`

Accepted school decision batches:

- `overture-gap-resolution-2026-09-15-batch1.json`
- `overture-gap-resolution-2026-09-15-batch2.json`

Current school artifact:

- 266 input rows;
- 30 explicitly reviewed;
- 28 resolved/explained;
- 2 reviewed-but-unresolved;
- 236 not yet reviewed;
- **238 outstanding**.

Reviewed unresolved rows:

- `Kada Modern British School`
- `M.S.G International British School`

The separately rerouted Mansoura provider case is now complete and is not an extra outstanding row beyond this artifact.

## 5. Exact resume cursor — START HERE

### Task A — continue the 238 outstanding high-signal school rows

Work in small deterministic checked-in batches. Preferred outcome order:

1. exact/current authoritative family coverage;
2. explicit source alias;
3. provider/campus/division topology requiring later D2.2 review;
4. genuinely new candidate with current permitted primary/recognized-source evidence;
5. unresolved supporting-only lead.

Current research already isolated several strong next-batch candidates, including American City International Schools, Cairo West International School, British International School Madinaty, Cairo British School, International Liberty School, Nefertari October/Cairo variants, and other exact/near-exact current source-family aliases. Every row still requires explicit evidence-backed review by exact Overture ID. Do not convert fuzzy similarity into an automatic merge.

### Task B — execute V7 read-only comparison

Matcher:

`tools/data-acquisition/international/build_v7_international_gap_review.py`

Owned V7 contract:

- **24,916 raw rows**;
- read-only;
- exact normalized-name overlap only;
- unmatched international-signal leads only;
- zero eligibility and zero canonical identities from V7 itself.

The matcher is ready but has not yet been run against the live owned V7 filesystem in this D2.1 pass. Any useful V7 unmatched lead must be re-sourced from current permitted evidence.

### Task C — Edarabia reference-only gap pass

Use Edarabia only as a discovery/reference index. Do not bulk scrape, systematically store or reproduce Edarabia content. Re-source every useful lead from institution-primary/regulatory/accreditor evidence.

### Task D — primary-source exhaustion pass

Use institution/operator primary sites and recognized source families to close remaining likely gaps and provider/campus/division ambiguity.

## 6. OSM status

Accepted OSM diagnostic run: **34997269459 — green diagnostic**.

All 12 tiled public-Overpass attempts were blocked from GitHub-hosted CI. The pipeline records `environment_blocked_all_tiles`. Failed source access must never be interpreted as zero OSM candidates.

Do not repeatedly retry the same public Overpass approach unless the runtime/network method changes materially.

## 7. Current D2.2 state — not the primary cursor yet

Current accepted review artifacts contain:

- 30 reviewed institution drafts;
- 10 reviewed division drafts;
- 51 reviewed source/lead memberships;
- 67 original strong-source rows still queued;
- 17 reviewed current campuses across 15 institutions;
- two reviewed institutions with multiple current campuses.

D2.2 remains secondary until D2.1 is explicitly closed. New Cognia, Canadian, ZfA, substantive-HE, Mansoura, Overture and V7 evidence may not auto-materialize into canonical identities.

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
- `PROJECT-STATUS.md`, `PROJECT-DECISIONS.md`, `DATASET-LAYERS.md`, this file and Issue #8 agree;
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
5. update this continuation file with the accepted run and exact next cursor;
6. update GitHub Issue #8;
7. never leave the next agent dependent on chat history.

This file and Issue #8 must describe the **last verified accepted state**, never merely planned or in-progress work.
