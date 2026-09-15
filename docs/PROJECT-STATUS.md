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

**Durable continuation file:** `docs/EDU-DATA-2-CONTINUATION.md`

Edu Hub is an Admonk-owned independent bilingual education discovery and knowledge product focused first on international education in Egypt for parents and students.

The project is currently a **data/research system before a website system**. Database completion, identity reconciliation, bilingual architecture, evidence, enrichment, media rights and portable export are the gate. Final Astro/Instatic selection, profile templates, filter UX, visual design and public-page architecture remain deferred.

Canonical execution order remains D2.1 → D2.2 → D2.3 → D2.4 → D2.5 → D2.6 → D2.7.

Logical data path:

`external source -> raw evidence -> staging/reconciliation -> reviewed canonical data -> bilingual localization -> completeness/media audit -> portable export`

Supabase is not part of Edu Hub.

## Dataset layer model

Evidence/source counts and reviewed identity counts are deliberately separate.

- **96 rows — foundational deterministic seed:** IB, UK DfE BSO, French homologation, German KMK, SCU foreign branches and AUC/MSCHE.
- **106 rows — historical classified strong-source layer:** foundational research universe after CIS/Cognia milestone expansion and scope review; preserved as provenance.
- **226 rows — British Council September 2026 discovery layer:** seven browser-reviewed batches; 12 have separate qualifying evidence and 214 remain supporting candidates.
- **256 rows — complete current Cognia Egypt registry layer:** official registry extraction across 11 pages; four rows supersede the older Cognia milestone subset for current universe counting only.
- **6 rows — current Canadian-authorized offshore-school source family.**
- **7 rows — current ZfA German Schools Abroad Egypt source family.**
- **597 rows — current accepted D2.1 source/evidence universe:** 128 eligible, 466 supporting candidates and 3 excluded.
- **30 reviewed institutions — current D2.2 identity layer.**
- **10 reviewed school divisions — current D2.2 division layer.**
- **51 reviewed source/lead memberships — current D2.2 membership layer.**
- **17 reviewed current-campus drafts across 15 reviewed institutions — current campus layer.**

`597` is a source/evidence count, **not** a claim of 597 unique institutions.

Reference: `tools/data-acquisition/international/DATASET-LAYERS.md` and `docs/EDU-DATA-2-CONTINUATION.md`.

## D2.1 — Complete the institution/source universe

Status: **ACTIVE — 597 SOURCE/EVIDENCE ROW CHECKPOINT VERIFIED; SUPPORTING GAP EXHAUSTION REMAINS**

### Current accepted checkpoint

Accepted `EDU-DATA-2 D2.1 Universe Checkpoint` run **35001371492** is green and proves:

- **597 source/evidence rows total**;
- **128 eligible**;
- **466 supporting candidates**;
- **3 excluded**;
- **226 British Council rows**;
- **256 Cognia registry rows**;
- **6 Canadian-authorized offshore-school rows**;
- **7 ZfA German Schools Abroad rows**;
- 4 historical Cognia milestone rows explicitly superseded for current counting;
- 252 net-new Cognia rows beyond that earlier subset;
- zero canonical identities created;
- zero automatic identity merges;
- zero database mutation;
- zero public projection.

Accepted validation head: `f3ddc06ed85193d251dfd7c02fcba032bfe54944`.

### Canadian offshore schools

The current checked-in Canadian source family contains six authorized Egypt offshore-school rows across provincial systems. These rows are authoritative source evidence, not six unique-institution claims. Cross-source overlap and BCCIS East/West topology remain D2.2 review work.

### ZfA German Schools Abroad

The current checked-in ZfA source family contains seven Egypt DAS schools. Current DAS membership is intentionally modeled separately from current exam authorization. Deutsche Schule Hurghada remains a current DAS school while KMK Sek-I lifecycle evidence records the last conducted school year as `2024/2025`; no post-2024/25 current Sek-I exam authorization is asserted.

### Overture supporting-gap review

Current Overture release: `2026-08-19.0`.

Accepted Egypt-only supporting layer:

- 1,121 bbox candidates;
- 79 non-Egypt rows rejected using Overture address country;
- **1,042 Egypt-only supporting rows**;
- 136 exact normalized-name overlaps with the 597-row checkpoint;
- 906 unmatched supporting rows / 869 unmatched normalized names;
- **266 high-signal pre-university rows**;
- **75 higher-education scope-review rows**;
- **565 lower-priority supporting rows**.

Two explicit high-signal review batches currently cover 30 rows:

- **28 resolved/explained** as existing source coverage, explicit aliases or provider/division cases;
- **2 reviewed but unresolved supporting-only leads**;
- **236 high-signal rows not yet reviewed**;
- **238 total high-signal rows still outstanding**.

The two reviewed-but-unresolved rows are `Kada Modern British School` and `M.S.G International British School`.

Overture never grants eligibility and never auto-creates or auto-merges identities.

### OSM diagnostic

Accepted OSM diagnostic run **34997269459** is green as a diagnostic. All 12 tiled public-Overpass requests were blocked from the GitHub-hosted CI environment. The pipeline records `environment_blocked_all_tiles` and does not misinterpret failed coverage as zero OSM candidates.

Do not repeatedly retry public Overpass without a materially different network/runtime approach.

### V7 archive

`tools/data-acquisition/international/build_v7_international_gap_review.py` is ready for read-only matching against the owned **24,916-row** V7 archive. It performs exact normalized-name overlap only, emits unmatched international-signal leads, and does not grant eligibility or create/merge identities.

It has not yet been executed against the live owned V7 filesystem in the current pass. Any useful V7 lead must be re-sourced from current permitted evidence before it can alter the accepted universe.

### Higher education reconciliation

Current SCU foreign-branch evidence lists 9 recognized branches. MOHESR lists those nine plus Ryerson/Toronto Metropolitan University. Ryerson/TMU is preserved as a lifecycle conflict rather than promoted as a currently active branch.

Accepted Higher-Ed Branch Reconciliation run: **34973583179**.

### Remaining D2.1 work — exact current order

1. **Triage the 75 Overture higher-education rows**: classify ordinary Egyptian HE institutions out of scope, resolve aliases to SCU/AUC where exact, and re-source plausible missing international HE candidates.
2. **Continue the 238 outstanding high-signal school rows** in small explicit checked-in batches; never fuzzy-auto-merge.
3. **Execute the V7 read-only comparison** against all 24,916 owned rows when the filesystem is available; re-source every useful unmatched lead.
4. **Run controlled Edarabia reference-only discovery**; do not bulk store/reproduce Edarabia content.
5. **Run an institution/operator primary-site exhaustion pass** for remaining likely gaps and provider/campus/division ambiguity.
6. Rebuild the final D2.1 universe, update all canonical docs, and record an explicit D2.1 closure decision before moving the sole active cursor to D2.2.

Detailed resume instructions and exact files are in `docs/EDU-DATA-2-CONTINUATION.md`.

## D2.2 — Clean identities, providers, campuses and divisions

Status: **PARTIALLY BUILT / SECONDARY WHILE D2.1 REMAINS OPEN**

Current verified reviewed identity state:

- **30 reviewed institution drafts**;
- **10 reviewed school-division drafts**;
- **51 reviewed source/lead memberships**;
- **67 original strong-source rows** remain in the explicit identity-review queue;
- zero automatic merges;
- zero canonical/runtime database writes;
- zero public projection.

New Cognia, Canadian, ZfA, Overture and V7 evidence stays outside reviewed identity materialization until explicit scope and D2.2 decisions exist.

Accepted Discovery Identity Review run after British Council batch 7: **34994994433**.

### Campus state

- **17 reviewed current-campus drafts**;
- **15 of 30 reviewed institutions** have at least one reviewed current campus;
- **2 institutions** currently have multiple reviewed campuses: Capital International Schools and Mount International School Community;
- **15 reviewed institutions** still require current-campus review;
- no campus topology is declared exhaustive;
- zero inferred campuses, canonical campus writes or public projection.

Accepted aggregate Campus Review run: **34972560009**.

## D2.3 — Complete EN + AR architecture

Status: **ARCHITECTURE IMPLEMENTED / CONTENT INCOMPLETE**

English and Arabic are first-class localizations over one factual entity graph. Official Arabic names are preferred; transliteration/editorial Arabic remains explicitly labeled non-official. Localization completion waits on broader D2.2 reconciliation.

## D2.4 — Enrich every eligible institution

Status: **STARTED / FIRST HIGH-PRIORITY PACKAGE GREEN / BROADER COVERAGE PENDING**

Existing reviewed enrichment covers a first high-priority set with source-backed website, location, contacts, admissions, curriculum/programme, education range and selected facility/provider/history/regulatory facts. Broader enrichment attaches only after identity/campus/division scope is understood.

## D2.5 — Complete media references and rights

Status: **STARTED**

The reviewed seed contains publication-safe Wikimedia assets with creator/license/attribution metadata. Institution/commercial-site imagery is discovery-only unless a defensible reuse basis exists. Every final institution must receive a terminal media state; `placeholder_required` is valid.

## D2.6 — Audit completeness

Status: **ARCHITECTURE IMPLEMENTED / FULL CANONICAL AUDIT PENDING**

Completeness will be measured independently across factual coverage, EN, AR, media, provenance/freshness and unresolved conflicts.

## D2.7 — Freeze portable master database

Status: **NOT STARTED**

The final presentation-neutral export will contain reviewed providers/institutions/campuses/divisions, EN/AR localizations and aliases, evidence, curriculum/certificates/accreditation, admissions/versioned fees, higher-education programmes/units, contacts/geography/facilities, rights-aware media, conflicts/review state and completeness metrics. It must not require Astro, Instatic or Supabase.

## Current accepted CI checkpoint

- `EDU-DATA-2 D2.1 Universe Checkpoint` — **35001371492** — green — 597 source/evidence rows; 128 eligible / 466 supporting / 3 excluded; two explicit Overture high-signal review batches integrated;
- `EDU-DATA-2 OSM Supporting Discovery` — **34997269459** — green diagnostic — public Overpass blocked across all 12 CI tiles, recorded without false zero-coverage inference;
- `EDU-DATA-2 Cognia Egypt Registry` — **34977754806** — green — complete 256-row Egypt registry;
- `EDU-DATA-2 British Council Discovery` — **34994994601** — green — 226 discovery rows / 12 qualified / 214 supporting;
- `EDU-DATA-2 Discovery Identity Review` — **34994994433** — green — 30 reviewed institutions / 10 divisions / 51 memberships;
- `EDU-DATA-2 Higher-Ed Branch Reconciliation` — **34973583179** — green — 9 SCU current branches plus one MOHESR lifecycle conflict;
- aggregate `EDU-DATA-2 Campus Review` — **34972560009** — green — 17 reviewed current campuses across 15 institutions;
- `EDU-DATA-2 International Registry` — **34994994608** — green — foundational contracts and reference-schema validation.

## Non-negotiable constraints

- no frontend/CMS architecture decision before database completion;
- no Supabase and no Ask Kalam infrastructure/data mixing;
- no public-school/university scope expansion without owner decision;
- no eligibility inference from branding words, Cognia accreditation alone, British Council Partner status, OSM/Overture, V7 or commercial directories;
- no unsupported facts, fees, rankings, accreditations or admissions data;
- no Edarabia bulk storage/reproduction without permission;
- no publication of media without recorded rights basis;
- no raw/staging publication;
- no automatic identity merge from fuzzy matching;
- no automatic uniqueness assumption for unmatched source rows;
- no exhaustive campus claim from a known address;
- preserve EN/AR parity, provenance, portability and review state throughout.
