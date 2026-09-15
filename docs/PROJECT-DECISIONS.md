# Edu Hub Project Decisions

This file contains the **active durable decisions** for the current Edu Hub scope. Detailed historical decision text remains preserved in Git history and on the historical national-registry branch where applicable. If an older chat or document conflicts with this file, `AGENTS.md`, the latest verified `PROJECT-STATUS.md`, and `EDU-DATA-2-CONTINUATION.md`, use the newer verified repository state.

Last consolidated: 2026-09-15.

## 1. Ownership, audience and product model

**Decision:** Edu Hub is an Admonk-owned product venture presented as an independent brand. Egypt is the first market; parents and students are the primary audience. Phase 1 is a trustworthy bilingual discovery/knowledge product and data foundation; monetization is deferred.

## 2. Database-first execution gate

**Decision:** Active milestone is `EDU-DATA-2 — Egypt International Education Registry` on branch `edu-data-2-international-registry`.

**Decision:** Binding order is `D2.1 universe → D2.2 identities/providers/campuses/divisions → D2.3 EN/AR → D2.4 enrichment → D2.5 media → D2.6 completeness audit → D2.7 portable freeze`.

**Decision:** Astro/Instatic selection, public-page architecture, filters, visual design and production frontend work are deferred until D2.7 is frozen.

**Decision:** Supabase is not part of Edu Hub. Ask Kalam infrastructure/data must remain unrelated. The research/data layer must remain portable and presentation-neutral.

## 3. Evidence architecture and source of truth

**Decision:** Logical path remains `external source → raw evidence → staging/reconciliation → reviewed canonical data → public projection → website`.

**Decision:** Raw/staging layers are private and never published directly. Official/regulatory/accreditation/institution-primary evidence is preferred over secondary directories. Conflicting assertions remain explicit review work; missing facts never justify invented values. Current changing facts preserve lifecycle/history.

**Decision:** AI may assist research, matching, localization and drafting but may not invent unsupported facts or silently promote review hints to canonical truth.

## 4. Active international-education scope

**Decision:** Active Phase 1 scope covers international education in Egypt, including private/independent international schools, private/independent IB World Schools, recognized foreign-national/international school models, recognized foreign university branches, and substantive internationally chartered/accredited/binational/transnational institutions.

**Decision:** Egyptian public schools and ordinary Egyptian public universities are not active Phase 1 targets. Historical national-registry work is retained as evidence/history only.

## 5. International eligibility standard

**Decision:** Every candidate has an explicit scope/review state. International branding never establishes eligibility by itself.

**Decision:** Strong school evidence may include active IB authorization, official French homologation, recognized German foreign-school evidence, BSO/recognized foreign-national status, or comparable current regulatory/accreditation evidence combined with the relevant scope rule.

**Decision:** British Council Partner status, Cognia presence, Overture/OSM, V7 and commercial directories are discovery/support evidence only and do not independently grant international eligibility.

## 6. Higher-education boundary — substantive international status

**Decision:** Recognized current foreign university branches are eligible. AUC is eligible as an internationally chartered/accredited independent institution when backed by current evidence.

**Decision:** Egyptian incorporation/private/national legal form is not automatically exclusionary when separate current evidence establishes substantive **binational, intergovernmental, transnational or international-organizational status**.

**Decision:** Foreign branding, partnership, exchange, franchise, validation or dual degree alone remains insufficient.

**Decision:** The 2026-09-15 reviewed HE package qualifies GIU, GUC, UFE, BUE and AASTMT under this standard. These are source/evidence additions, not five automatically created unique institutions.

Reference: `tools/data-acquisition/international/seeds/substantive-international-higher-ed-review-2026-09-15.json`.

## 7. Overture higher-education review boundary

**Decision:** Overture category/name signals are triage inputs only; every HE decision is explicit and source-backed.

**Decision:** The full 70-row post-overlay HE queue has **0 outstanding rows**: 14 existing eligible aliases/subunits, 21 out-of-scope Egyptian HE rows/subunits, 33 supporting-only academy/training/institute leads, 1 EBIS school-category error and 1 Mansoura provider/school category error closed through explicit topology review.

**Decision:** Rerouting a category error does not create or merge an identity. Do not restart this review unless current evidence changes or a regression is found.

## 8. Source-family and layer-count semantics

**Decision:** Source/evidence counts, reviewed identity counts, campus counts and division counts are separate contracts and must never be conflated.

**Decision:** The 96-row foundational seed and 106-row historical classified strong-source layer remain independently reproducible provenance layers.

**Decision:** A complete current same-publisher source family may supersede an older subset for current counting only when deterministic and explicit; historical evidence remains preserved.

**Decision:** The four historical Cognia milestone rows are superseded for current counting by the complete 256-row Cognia Egypt registry. Canadian offshore-school and ZfA DAS evidence are additive source families, not automatic unique-institution additions.

**Decision:** Current ZfA DAS membership is distinct from current exam authorization. Deutsche Schule Hurghada retains current DAS evidence while the checked KMK Sek-I lifecycle records last conducted year `2024/2025`; no later Sek-I authorization is asserted.

**Decision:** Accepted D2.1 run **`35021835175`** establishes the current **604 source/evidence row** checkpoint: **135 eligible / 466 supporting / 3 excluded**. `604` is not a unique-institution count.

## 9. Supporting discovery qualification is evidence-separated

**Decision:** Supporting discovery may expand research coverage without rewriting historical strong-source layers. Discovery rows remain supporting candidates until separate explicit review supplies qualifying current evidence.

**Decision:** Primary re-sourcing is additive; discovery provenance records how a lead was found and is not automatically its eligibility basis. No unmatched row is assumed unique merely because no duplicate has yet been found.

## 10. Identity, provider, campus and division boundaries

**Decision:** Institution, provider/group, physical campus and curriculum/language/phase division are distinct concepts.

**Decision:** A British, American, French, IB or other section inside the same school/provider must not be silently duplicated as a separate institution merely because one source lists it independently. Division-scoped evidence remains division-scoped unless broader evidence supports promotion.

**Decision:** Cross-source reconciliation may conclude `same institution, different division` or `same provider, distinct school/campus` without forcing duplication or broad merge.

**Decision:** A reviewed institution does not imply complete campus topology. One known address never proves one-campus completeness; historical locations are not current campuses unless current evidence supports them.

### Mansoura College topology decision

**Decision:** Current first-party Mansoura College evidence establishes a provider/campus umbrella with four school units. The umbrella is not materialized as a separate canonical institution during D2.1.

**Decision:** Mansoura College Language School and Modern Mansoura College Language School are national/provider context and are not added to the active international source universe. The British Council `Mansoura College Modern` row remains separate supporting provenance.

**Decision:** `Mansoura College British School` and `Mansoura College 2 International American School` are the only two eligible reviewed source/evidence additions. Their supporting Pearson/Cognia/ACT and prior-source evidence remains separately preserved.

**Decision:** Overture `Mansoura College International Schools` is a reviewed provider-umbrella alias, not a separate institution.

Reference: `tools/data-acquisition/international/seeds/mansoura-college-topology-review-2026-09-15.json`.

## 11. Review artifacts are not runtime database writes

**Decision:** D2.2 may materialize deterministic reviewed draft artifacts before runtime storage is selected if provenance/review boundaries are preserved. Deterministic draft IDs do not themselves create canonical runtime rows or publication rights.

**Decision:** Identity review and eligibility remain separate. Incremental review batches are checked in, exact-source-key based, additive and may not retarget already-reviewed rows or auto-merge identities.

## 12. Name matching and automation safety

**Decision:** Normalized-name or fuzzy similarity may generate review hints only; it never authorizes a canonical merge.

**Decision:** No pipeline may auto-create canonical institutions, auto-merge source identities, auto-infer campus completeness or auto-publish raw/staging data. Exact source keys/Overture IDs are required for checked-in gap-resolution decisions.

**Decision:** Duplicate Overture place rows are not automatically deduplicated. When current evidence shows they describe the same provider/campus area, each place row remains explicit review evidence until D2.2 makes a topology decision.

## 13. OSM and geospatial discovery

**Decision:** OSM remains a permitted supporting source. Hosted CI Overpass failure is diagnostic state, not negative evidence. Accepted diagnostic run `34997269459` recorded all 12 Egypt tiles blocked as `environment_blocked_all_tiles`; this must never be reported as zero OSM candidates.

**Decision:** Overture is the current functioning broad geospatial supporting layer and still cannot grant eligibility.

## 14. V7 owned archive

**Decision:** Legacy V7 is not bulk-promoted. The owned 24,916-row archive may be queried read-only for exact overlap/missing-name discovery. Useful unmatched leads must be re-sourced from current permitted evidence before altering D2.1. V7 performs no fuzzy merge, eligibility decision or canonical creation.

## 15. Edarabia policy

**Decision:** Edarabia is reference-only discovery. Do not bulk scrape, systematically store, reproduce or publish Edarabia content without written permission/license. Re-source every useful lead/fact from permitted current sources. Edarabia ratings/reviews/images are not imported without independent lawful basis.

Reference: `docs/SOURCE-USAGE-POLICY.md`.

## 16. EN/AR localization

**Decision:** Arabic and English are first-class locales tied to one factual graph. Language-neutral facts are stored once; localized text retains origin/status. Prefer official Arabic; transliteration/editorial Arabic must be explicitly marked.

## 17. Fees, admissions and temporal facts

**Decision:** Fees/admissions are versioned by academic year/cycle. Lifecycle-sensitive regulatory/accreditation facts retain dates/status and are not silently presented as current after expiry/supersession.

## 18. Media rights and publication boundary

**Decision:** Media discovery/provenance does not imply publication rights. Official-site/social images remain `public_use_allowed=false` unless a defensible reuse basis exists. Valid publication bases include institution permission/claim, verified open/Wikimedia licensing with attribution, or original Edu Hub/Admonk production. `placeholder_required` is a valid terminal state.

## 19. SEO/publication boundary

**Decision:** A database record does not automatically become an indexable page and arbitrary filter combinations do not automatically generate SEO pages. Only reviewed public projections may be published/indexed.

## 20. Durable continuation and handoff

**Decision:** `docs/EDU-DATA-2-CONTINUATION.md` is the durable execution cursor and GitHub Issue #8 is the visible roadmap.

**Decision:** Every substantial continuation agent reads `AGENTS.md`, `PROJECT-STATUS.md`, this file, the continuation file, Issue #8 and `DATASET-LAYERS.md`, then inspects actual branch state/latest green CI before resuming.

**Decision:** After each material accepted checkpoint, commit deterministic evidence/review decisions, obtain green CI, and synchronize durable docs/Issue #8 so the next agent never depends on chat history.

## 21. Current exact cursor

**Decision:** Overture higher-education review and Mansoura College topology are complete and must not be restarted absent changed evidence/regression.

**Decision:** Four high-signal school batches are accepted. Run **35021835175** proves **50 reviewed / 48 resolved-explained / 2 unresolved / 216 unreviewed / 218 outstanding** from the 266-row high-signal school queue.

**Decision:** Batch 4 preserves provider/division distinctions for El Alsson, Forsan and Manhattan; treats the two Manhattan Overture rows separately rather than auto-deduplicating; preserves Choueifat New Cairo and 6 October as distinct branch-level aliases; and resolves Royal British and DSBK through current government-authoritative source families.

**Decision:** The exact next D2.1 task is the remaining **218 high-signal school rows**, processed in small deterministic evidence-backed batches, followed by V7 read-only gap comparison, Edarabia reference-only pass and institution/operator primary-source exhaustion.

**Decision:** AIA International School is not currently mapped to the known Alexandria AIA source identity because the Overture row is located in New Cairo while current authoritative AIA evidence is in Alexandria. It remains separate research work unless current evidence resolves the discrepancy.

**Decision:** D2.1 remains open until gap-exhaustion criteria are satisfied and an explicit closure decision hands the sole active cursor to D2.2.
