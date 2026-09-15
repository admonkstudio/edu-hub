# Edu Hub Project Decisions

This file contains the **active durable decisions** for the current Edu Hub scope. Detailed historical decision text remains preserved in Git history and on the historical national-registry branch where applicable. If an older chat or document conflicts with this file, `AGENTS.md`, the latest verified `PROJECT-STATUS.md`, and `EDU-DATA-2-CONTINUATION.md`, use the newer verified repository state.

Last consolidated: 2026-09-16.

## 1. Ownership, audience and product model

**Decision:** Edu Hub is an Admonk-owned product venture presented as an independent brand. Egypt is the first market; parents and students are the primary audience. Phase 1 is a trustworthy bilingual discovery/knowledge product and data foundation; monetization is deferred.

## 2. Database-first execution gate

**Decision:** Active milestone is `EDU-DATA-2 — Egypt International Education Registry` on branch `edu-data-2-international-registry`.

**Decision:** Binding order is `D2.1 universe → D2.2 identities/providers/campuses/divisions → D2.3 EN/AR → D2.4 enrichment → D2.5 media → D2.6 completeness audit → D2.7 portable freeze`.

**Decision:** Astro/Instatic selection, public-page architecture, filters, visual design and production frontend work are deferred until D2.7 is frozen. Supabase is not part of Edu Hub.

## 3. Evidence architecture and source of truth

**Decision:** Logical path remains `external source → raw evidence → staging/reconciliation → reviewed canonical data → public projection → website`.

**Decision:** Raw/staging layers are private and never published directly. Official/regulatory/accreditation/institution-primary evidence is preferred over secondary directories. Conflicting assertions remain explicit review work; missing facts never justify invented values. AI may assist but may not silently promote review hints to canonical truth.

## 4. Active international-education scope

**Decision:** Active Phase 1 scope covers international education in Egypt, including private/independent international schools, recognized foreign-national/international school models, recognized foreign university branches, and substantively international/binational/transnational institutions. International branding never establishes eligibility by itself.

**Decision:** British Council Partner status, Cognia presence, Overture/OSM, V7 and commercial directories are discovery/support evidence only and do not independently grant international eligibility.

## 5. Higher-education boundary

**Decision:** Recognized current foreign university branches are eligible. Egyptian incorporation/private/national legal form is not automatically exclusionary where separate current evidence establishes substantive binational, intergovernmental, transnational or international-organizational status. Foreign branding, partnership, validation or dual degree alone remains insufficient.

**Decision:** GIU, GUC, UFE, BUE and AASTMT remain the explicit 2026-09-15 substantive-international HE additions. The full 70-row post-overlay Overture HE queue has **0 outstanding rows** and must not be restarted absent changed evidence/regression.

## 6. Source-family and layer-count semantics

**Decision:** Source/evidence counts, reviewed identity counts, campus counts and division counts are separate contracts and must never be conflated.

**Decision:** The four historical Cognia milestone rows are superseded for current counting by the complete 256-row Cognia Egypt registry. Historical evidence remains preserved.

**Decision:** Accepted D2.1 run **`35025758910`** establishes the current **604 source/evidence row** checkpoint: **135 eligible / 466 supporting / 3 excluded**. `604` is not a unique-institution count.

## 7. Identity, provider, campus and division boundaries

**Decision:** Institution, provider/group, physical campus and curriculum/language/phase division are distinct concepts. A British, American, French, IB or other section inside the same school/provider must not be silently duplicated as a separate institution merely because one source lists it independently.

**Decision:** One known address never proves campus completeness. Historical/current campus relationships and provider/division relationships require explicit reviewed D2.2 topology decisions.

**Decision:** Duplicate Overture place rows are not automatically deduplicated. Location mismatches block automatic aliasing. A demonstrable discovery-coordinate defect also does not override exact current address/name/contact evidence; preserve the defect explicitly rather than silently repair it.

### Mansoura College topology

**Decision:** Mansoura College Language School and Modern Mansoura College Language School remain national/provider context. `Mansoura College British School` and `Mansoura College 2 International American School` are the two eligible reviewed source/evidence additions. The provider umbrella remains non-canonical and old Cognia/British Council rows remain separate provenance.

## 8. Name matching and automation safety

**Decision:** Normalized/fuzzy similarity generates review hints only. No pipeline may auto-create canonical institutions, auto-merge source identities, auto-infer campus completeness or auto-publish raw/staging data. Exact source keys/Overture IDs are required for checked-in gap-resolution decisions.

## 9. OSM, V7 and Edarabia

**Decision:** OSM remains supporting discovery; hosted CI Overpass failure is diagnostic state, not zero coverage.

**Decision:** V7 may be queried read-only for exact-name overlap/missing-name discovery across the owned 24,916-row archive; useful unmatched leads must be re-sourced before altering D2.1.

**Decision:** Edarabia is reference-only discovery. Do not bulk scrape/store/reproduce its content; re-source useful leads from permitted current sources.

## 10. Localization, temporal facts and media

**Decision:** EN and AR are first-class locales over one factual graph. Fees/admissions and lifecycle-sensitive facts retain academic-year/date/status provenance. Media discovery does not imply publication rights; `placeholder_required` is a valid terminal media state.

## 11. Durable continuation and handoff

**Decision:** `docs/EDU-DATA-2-CONTINUATION.md` is the durable execution cursor and GitHub Issue #8 is the visible roadmap. After each material accepted checkpoint, obtain green CI and synchronize all durable trackers.

## 12. Current exact cursor

**Decision:** Eight high-signal school batches are accepted. Run **35025758910** proves **75 reviewed / 73 resolved-explained / 2 unresolved / 191 unreviewed / 193 outstanding** from the 266-row high-signal school queue.

**Decision:** Batch 8 reconciles Delta College International School as provider/programme topology; Riada American School to the current American-division source identity; Tiba International School - American Division to the current Alexandria American-division source identity; EELS American Division as division-scoped topology under the current EELS source identity; Modern American School of Egypt as explicit institution/campus topology preserving the 2000 and 2017 campus evidence; and Victory College American Department as division topology under the current Victory College provider identity.

**Decision:** The exact next D2.1 task is the remaining **193 high-signal school rows**, processed in small deterministic evidence-backed batches, followed by V7 read-only gap comparison, Edarabia reference-only pass and institution/operator primary-source exhaustion.

**Decision:** AIA International School, Delta American School and the two Sunrise International School Hurghada place rows remain held back pending stronger current evidence. Weak evidence must remain unresolved rather than be forced into an existing identity.

**Decision:** D2.1 remains open until gap-exhaustion criteria are satisfied and an explicit closure decision hands the sole cursor to D2.2.
