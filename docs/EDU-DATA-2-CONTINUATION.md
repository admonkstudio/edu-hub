# EDU-DATA-2 Continuation Roadmap

Last updated: 2026-09-15

This file is the **continuation cursor for the active Edu Hub work**. It exists so a new agent can resume correctly even when the previous chat is unavailable or truncated.

Read this file after `AGENTS.md`, `docs/PROJECT-STATUS.md`, and `docs/PROJECT-DECISIONS.md` before changing code or data.

## 1. Active scope

- Repository: `admonkstudio/edu-hub`
- Active branch: `edu-data-2-international-registry`
- Active milestone: `EDU-DATA-2 — Egypt International Education Registry`
- Current execution stage: `D2.1 — Complete the institution/source universe`
- Frontend/CMS decision: **deferred until D2.7 database freeze**
- Supabase: **not part of Edu Hub**

Canonical sequence remains:

`D2.1 universe → D2.2 identities → D2.3 EN/AR → D2.4 enrichment → D2.5 media → D2.6 audit → D2.7 portable freeze → Astro/Instatic decision → public product build`

Do not skip ahead because a website implementation appears easier than the data work.

## 2. Last accepted checkpoint

The current accepted D2.1 checkpoint is:

- Workflow: `EDU-DATA-2 D2.1 Universe Checkpoint`
- Accepted run: **35001371492**
- Accepted validation head: `f3ddc06ed85193d251dfd7c02fcba032bfe54944`
- Conclusion: **green**

The accepted source/evidence universe is:

- **597 source/evidence rows total**
- **128 eligible**
- **466 supporting candidates**
- **3 excluded**

`597` is **not** a unique-institution count. It is a source/evidence count. Cross-source duplicates, campuses, divisions and provider relationships remain explicit reconciliation work.

The current 597 rows are derived as follows:

- historical reviewed source/lead universe after British Council: 332 rows;
- replace the four historical Cognia milestone rows for current counting with the complete 256-row Cognia Egypt registry: 584 rows;
- add six current Canadian-authorized offshore-school source rows: 590 rows;
- add seven current ZfA German Schools Abroad Egypt source rows: 597 rows.

Historical source snapshots are preserved; source-family additions do not rewrite older evidence layers.

## 3. Source families already completed or frozen

### Foundational and historical layers

- 96-row foundational deterministic seed;
- 106-row historical classified strong-source layer;
- 226-row September 2026 British Council Partner Schools discovery layer;
- 256-row complete official Cognia Egypt registry;
- 9 current SCU foreign-university branches, with Ryerson/TMU preserved only as a lifecycle conflict from MOHESR.

### Canadian offshore schools

Checked-in source:

`tools/data-acquisition/international/seeds/canadian-offshore-schools-egypt-2026-09-15.json`

Current family: **6 authorized source rows** across Canadian provincial systems.

Important identity rule: these six rows are source evidence, not six new unique institutions. Cross-source overlap and BCCIS East/West topology remain D2.2 review work.

### German Schools Abroad / ZfA

Checked-in source:

`tools/data-acquisition/international/seeds/zfa-german-schools-abroad-egypt-2026-09-15.json`

Current family: **7 Egypt DAS source rows**.

Important lifecycle rule: current ZfA DAS membership is distinct from current KMK exam authorization. `Deutsche Schule Hurghada` is preserved as a current DAS school, while the checked KMK Sek-I evidence records the last conducted school year as `2024/2025`; the pipeline does **not** assert current Sek-I exam authorization after 2024/25.

## 4. Overture supporting-gap state

Official Overture Places release used: `2026-08-19.0`.

Acquisition script:

`tools/data-acquisition/international/acquire_overture_egypt_international_education.py`

The rectangular Egypt bbox initially returned 1,121 candidates. The acquisition now requires Overture address country `EG` and rejects neighboring-country leakage.

Accepted Overture state:

- 1,121 bbox candidates;
- 79 non-Egypt rows rejected;
- **1,042 Egypt-only supporting rows**;
- 136 exact normalized-name overlaps with the 597-row checkpoint;
- 906 unmatched supporting rows;
- 869 unmatched normalized names;
- **266 high-signal pre-university rows**;
- **75 higher-education scope-review rows**;
- **565 lower-priority supporting rows**.

Overture cannot establish eligibility and cannot create or merge identities.

### Explicit Overture review batches

Resolution builder:

`tools/data-acquisition/international/apply_overture_gap_resolutions.py`

Checked-in decisions:

- `tools/data-acquisition/international/seeds/overture-gap-resolution-2026-09-15-batch1.json`
- `tools/data-acquisition/international/seeds/overture-gap-resolution-2026-09-15-batch2.json`

Current high-signal result after the two batches:

- 266 high-signal input rows;
- **30 explicitly reviewed**;
- **28 resolved/explained** as existing authoritative coverage, exact source aliases, or provider/division cases requiring D2.2 topology review;
- **2 reviewed but unresolved supporting-only leads**;
- **236 not yet reviewed**;
- **238 total high-signal rows still outstanding**.

The two unresolved reviewed rows are:

- `Kada Modern British School`
- `M.S.G International British School`

No fuzzy matching is allowed to remove an Overture row from the gap queue. Every resolution must target the exact Overture ID and, when resolved to current evidence, an exact current source key.

## 5. OSM status

OSM is **not a successful acquisition source in the current hosted CI environment**.

Workflow: `EDU-DATA-2 OSM Supporting Discovery`

Accepted diagnostic run: **34997269459** — green diagnostic.

All 12 Egypt tiles were blocked across the bounded public Overpass mirrors from GitHub-hosted CI. The pipeline records `environment_blocked_all_tiles` rather than treating failed coverage as zero candidates.

Do not keep spending CI time retrying public Overpass unless the network/runtime approach changes materially. Overture is the current functioning geospatial/supporting layer.

## 6. V7 owned archive status

A read-only V7 gap matcher exists:

`tools/data-acquisition/international/build_v7_international_gap_review.py`

Its contract is deliberately conservative:

- expects exactly **24,916 raw V7 rows**;
- reads the owned archive only;
- performs deterministic exact normalized-name overlap only;
- emits unmatched international-signal leads for current re-sourcing;
- performs zero fuzzy auto-merge;
- grants zero eligibility;
- creates zero canonical identities;
- does not promote V7 rows into the current universe directly.

The matcher has not yet been executed against the live/owned V7 filesystem in the current D2.1 pass because that requires access to the existing Railway/Instatic V7 data location.

Any useful V7 unmatched lead must be re-sourced from a current permitted source before it can change the accepted D2.1 universe.

## 7. Current D2.2 state — do not confuse with D2.1 counts

D2.2 is partially built but is **not the current primary cursor** while D2.1 remains open.

Current reviewed identity state from the previously accepted D2.2 artifacts:

- 30 reviewed institution drafts;
- 10 reviewed division drafts;
- 51 reviewed source/lead memberships;
- 67 original strong-source rows still in the explicit identity-review queue;
- 17 reviewed current-campus drafts across 15 reviewed institutions;
- two reviewed institutions currently have multiple reviewed campuses.

New Canadian, ZfA, Cognia and Overture evidence must not be automatically materialized as institutions. D2.2 resumes as the sole active workstream only after D2.1 is explicitly closed.

## 8. Exact resume cursor

**Resume here. Do not restart completed acquisition work.**

### Next task A — triage the 75 Overture higher-education rows

Start with:

`artifacts/international/overture-gap-review/higher-ed-scope-review.jsonl`

Goal:

1. classify obvious ordinary Egyptian universities/colleges as out of the active international higher-education scope;
2. identify exact aliases/overlaps with the nine current SCU foreign branches and AUC evidence;
3. isolate genuinely plausible missing foreign/international higher-education institutions;
4. re-source plausible gaps from SCU, MOHESR, institution-primary or recognized accreditor evidence;
5. check in explicit decisions by exact Overture ID;
6. never grant international scope from Overture naming alone.

### Next task B — continue the 238 outstanding high-signal school rows

Work in small checked-in review batches. For each row, prefer this outcome hierarchy:

1. exact/current authoritative source family coverage;
2. explicit existing source alias;
3. explicit provider/campus/division relation requiring D2.2 review;
4. genuinely new candidate with current primary/recognized-source evidence;
5. unresolved supporting-only lead.

Do not introduce fuzzy auto-merge logic merely to reduce the queue faster.

### Next task C — execute the V7 read-only comparison

When the owned V7 filesystem is available, run the existing matcher against all 24,916 rows. Use V7 only to discover missing names/aliases. Re-source every useful unmatched lead from current permitted evidence before adding anything to the accepted universe.

### Next task D — controlled Edarabia reference-only gap discovery

Edarabia may identify a possible missing institution or field, but do not bulk scrape/store its content. Re-source every useful lead from primary/regulatory/accreditor evidence.

### Next task E — institution/operator primary-site exhaustion pass

Use primary school/operator websites and recognized source families to close remaining high-signal gaps and provider/campus/division ambiguity.

## 9. D2.1 exit criteria

D2.1 may be marked complete only when all of the following are true:

- Overture high-signal pre-university review is substantially exhausted and residual unresolved rows are explicitly documented;
- Overture higher-education review is completed;
- OSM limitation is documented and not misrepresented as coverage;
- V7 owned archive matching has been executed or explicitly blocked with a durable reason;
- controlled Edarabia reference-only gap discovery is complete;
- useful directory/archive leads have current permitted re-sourcing;
- current major authoritative source families have been checked for Egypt coverage;
- current source/lead universe is reproducibly rebuilt by green CI;
- source-row counts are not mislabeled as unique institutions;
- zero fuzzy auto-merge, zero unsupported eligibility, zero database mutation and zero public projection occurred;
- `PROJECT-STATUS.md`, `PROJECT-DECISIONS.md`, `DATASET-LAYERS.md` and this continuation file agree;
- an explicit decision records D2.1 closure and hands the cursor to D2.2.

## 10. Non-negotiable safety/data rules

- source/discovery rows never automatically become canonical institutions;
- accreditation/source membership does not automatically equal Edu Hub eligibility unless the source-specific scope rule says so;
- no identity merge from fuzzy similarity;
- no campus inference from one address;
- no institution-wide assertion from division-scoped evidence;
- historical/lifecycle evidence must not be silently presented as current;
- British Council Partner status, Cognia presence, Overture/OSM, V7 and commercial directories do not independently establish international eligibility;
- no Edarabia bulk storage/reproduction without permission;
- no raw/staging publication;
- no runtime database/public-page work before the D2 database-completion gate;
- preserve EN/AR, provenance, portability, review state and rights boundaries.

## 11. Files a continuation agent should inspect first

1. `AGENTS.md`
2. `docs/PROJECT-STATUS.md`
3. `docs/PROJECT-DECISIONS.md`
4. **this file** — `docs/EDU-DATA-2-CONTINUATION.md`
5. `tools/data-acquisition/international/DATASET-LAYERS.md`
6. `.github/workflows/edu-data-2-universe-checkpoint.yml`
7. `tools/data-acquisition/international/build_d2_1_universe_checkpoint.py`
8. `tools/data-acquisition/international/build_overture_gap_review.py`
9. `tools/data-acquisition/international/apply_overture_gap_resolutions.py`
10. the checked-in source/review seeds referenced by those builders.

Inspect current branch implementation before assuming a count from historical conversation text.

## 12. Handoff discipline for every future agent

After material progress:

1. update code/seeds/builders and CI;
2. obtain a green accepted workflow run;
3. update `tools/data-acquisition/international/DATASET-LAYERS.md` when layer counts change;
4. update `docs/PROJECT-STATUS.md` and `docs/PROJECT-DECISIONS.md` when status/architecture/count contracts change;
5. update **this continuation file** with the new accepted run, counts, completed batches and exact next cursor;
6. never leave a future agent dependent on chat history to know what happens next.

The continuation file should always describe the **last verified state**, not work that was merely planned or started.