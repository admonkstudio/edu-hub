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

Edu Hub is an Admonk-owned independent bilingual education discovery and knowledge product focused first on international education in Egypt for parents and students.

The project is currently a **data/research system before a website system**. Database completion, identity reconciliation, bilingual architecture, evidence, enrichment, media rights and portable export are the gate. Final Astro/Instatic selection, profile templates, filter UX, visual design and public-page architecture remain deferred.

Canonical execution order remains D2.1 → D2.2 → D2.3 → D2.4 → D2.5 → D2.6 → D2.7.

Logical data path:

`external source -> raw evidence -> staging/reconciliation -> reviewed canonical data -> bilingual localization -> completeness/media audit -> portable export`

Supabase is not part of Edu Hub.

## Dataset layer model

Evidence/source counts and reviewed identity counts are deliberately separate.

- **96 rows — foundational deterministic seed:** IB, UK DfE BSO, French homologation, German KMK, SCU foreign branches and AUC/MSCHE.
- **106 rows — historical classified strong-source layer:** the foundational research universe after CIS/Cognia milestone expansion and scope review. It remains reproducible as historical provenance.
- **226 rows — British Council September 2026 discovery layer:** seven browser-reviewed batches; 12 have separate qualifying evidence and 214 remain supporting candidates.
- **256 rows — complete current Cognia Egypt registry layer:** official registry extraction across 11 pages; four rows supersede the older Cognia milestone subset for current universe counting only.
- **584 rows — current accepted D2.1 source/lead universe:** 115 eligible, 466 supporting candidates and 3 excluded. This is a source/evidence count, not a unique-institution count.
- **30 reviewed institutions — current D2.2 identity layer.**
- **10 reviewed school divisions — current D2.2 division layer.**
- **51 reviewed source/lead memberships — current D2.2 membership layer.**
- **17 reviewed current-campus drafts across 15 reviewed institutions — current campus layer.**

Reference: `tools/data-acquisition/international/DATASET-LAYERS.md`.

## D2.1 — Complete the institution/source universe

Status: **ACTIVE — 584 SOURCE/LEAD ROW CHECKPOINT VERIFIED; SUPPORTING GAP CHECKS REMAIN**

### Foundational and strong evidence

The historical 106-row classified strong-source layer contains:

- 54 IB Egypt rows;
- 11 UK DfE British Schools Overseas rows;
- 17 French 2026–2027 homologation rows;
- 4 German KMK recognized-school rows;
- 9 SCU recognized foreign-university-branch rows;
- 1 AUC/MSCHE higher-education row;
- 6 CIS accreditation rows;
- 4 Cognia milestone rows.

Its accepted classification was 103 eligible and 3 excluded. The four Cognia milestone rows remain preserved as provenance but are superseded by the complete Cognia registry for current-universe counting.

### British Council September 2026

Seven checked-in browser-reviewed batches contain **226 Partner School source rows**. Partner School status remains discovery/contact evidence only.

- 12 rows have separate high-confidence primary/recognized qualification;
- 214 remain supporting candidates;
- 138 rows include website references;
- zero eligibility decisions come from Partner School status itself;
- zero automatic identities, merges, database writes or public projection.

Accepted British Council Discovery run: **34994994601**.

### Complete Cognia Egypt registry

The official public Cognia Accreditation Registry now has a complete Egypt extraction:

- **256 registry rows**;
- **11 pages**;
- **2 duplicate normalized-name groups** retained rather than silently merged;
- 9 of the earlier 24 institution-primary verification candidates are deterministic exact-name matches; 15 remain identity/division-scope review cases.

The four old Cognia milestone institutions are exact same-publisher normalized-name matches in the complete registry. Current-universe counting therefore replaces the four-row milestone subset with all 256 current registry rows while preserving milestone provenance. Only the four already-reviewed scope decisions are carried forward; the other 252 registry rows remain supporting candidates.

Accepted Cognia full-registry run: **34977754806**.

### Current D2.1 checkpoint

Accepted `EDU-DATA-2 D2.1 Universe Checkpoint` run **34995646409** rebuilds the current universe from source and proves:

- **584 source/lead rows total**;
- **115 eligible**;
- **466 supporting candidates**;
- **3 excluded**;
- **226 British Council rows**;
- **256 Cognia registry rows**;
- 4 historical Cognia milestone rows explicitly superseded for current counting;
- 252 net-new Cognia rows beyond that earlier subset;
- zero canonical identities created;
- zero automatic identity merges;
- zero database mutation;
- zero public projection.

`584` must never be described as 584 unique institutions.

### Higher education reconciliation

Current SCU foreign-branch evidence lists 9 recognized branches. MOHESR source evidence lists those nine plus Ryerson/Toronto Metropolitan University. Ryerson/TMU is preserved as a lifecycle conflict rather than promoted as a currently active branch. No MOHESR-only current-active branch was automatically added.

Accepted Higher-Ed Branch Reconciliation run: **34973583179**.

### Remaining D2.1 gap checks

D2.1 remains open for:

1. Overture/OpenStreetMap supporting identity/geography gap discovery;
2. read-only matching against the owned V7 raw archive, with all useful legacy leads re-sourced before canonical use;
3. controlled Edarabia **reference-only** gap discovery, with no bulk storage of Edarabia content;
4. institution/operator primary-site gap confirmation and current identity/campus/provider checks.

OpenStreetMap is being queried as a supporting-only tiled Egypt scan; it cannot establish eligibility. Overture remains a separate supporting-source check.

## D2.2 — Clean identities, providers, campuses and divisions

Status: **ACTIVE IN PARALLEL; BULK NEW DISCOVERY DOES NOT AUTO-MATERIALIZE IDENTITIES**

Current verified reviewed identity state:

- **30 reviewed institution drafts**;
- **10 reviewed school-division drafts**;
- **51 reviewed source/lead memberships**;
- **67 original strong-source rows** remain in the explicit identity-review queue;
- current qualified British Council discoveries processed through explicit review;
- zero automatic merges;
- zero canonical/runtime database writes;
- zero public projection.

New Cognia/OSM/V7 discovery rows stay outside reviewed identity materialization until scope qualification and explicit D2.2 decisions exist.

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

- `EDU-DATA-2 D2.1 Universe Checkpoint` — **34995646409** — green — 584 source/lead rows; 115 eligible / 466 supporting / 3 excluded;
- `EDU-DATA-2 Cognia Egypt Registry` — **34977754806** — green — complete 256-row Egypt registry;
- `EDU-DATA-2 British Council Discovery` — **34994994601** — green — 226 discovery rows / 12 qualified / 214 supporting;
- `EDU-DATA-2 Discovery Identity Review` — **34994994433** — green — 30 reviewed institutions / 10 divisions / 51 memberships;
- `EDU-DATA-2 Higher-Ed Branch Reconciliation` — **34973583179** — green — 9 SCU current branches plus one MOHESR lifecycle conflict;
- aggregate `EDU-DATA-2 Campus Review` — **34972560009** — green — 17 reviewed current campuses across 15 institutions;
- `EDU-DATA-2 International Registry` — **34994994608** — green — foundational contracts and reference-schema validation.

## Immediate next actions

1. Complete OSM/Overture supporting gap checks and compare them to the 584-row checkpoint without auto-promoting rows.
2. Match the owned V7 archive read-only against the current international universe; re-source any useful unmatched leads from current permitted sources.
3. Conduct controlled Edarabia reference-only gap discovery and re-source every useful lead.
4. Run institution/operator primary-site confirmation for remaining high-signal gaps.
5. When likely universe coverage is substantially exhausted, close D2.1 and make D2.2 the sole active workstream.
6. Expand explicit D2.2 identity/provider/campus/division review; then D2.3–D2.5 completion, D2.6 audit and D2.7 freeze.

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
