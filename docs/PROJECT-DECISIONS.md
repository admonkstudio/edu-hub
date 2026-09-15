# Edu Hub Project Decisions

This file contains the **active durable decisions** for the current Edu Hub scope. Detailed historical decision text remains preserved in Git history and on the historical national-registry branch where applicable. If an older chat or document conflicts with this file, `AGENTS.md`, the latest verified `PROJECT-STATUS.md`, and `EDU-DATA-2-CONTINUATION.md`, use the newer verified repository state.

Last consolidated: 2026-09-15.

## 1. Ownership, audience and product model

**Decision:** Edu Hub is an Admonk-owned product venture presented as an independent brand.

**Decision:** Egypt is the first market. Parents and students are the primary audience.

**Decision:** Phase 1 is a trustworthy bilingual discovery/knowledge product and data foundation. Monetization is deferred.

## 2. Database-first execution gate

**Decision:** The active project milestone is `EDU-DATA-2 — Egypt International Education Registry` on branch `edu-data-2-international-registry`.

**Decision:** Current execution order is binding:

`D2.1 universe → D2.2 identities/providers/campuses/divisions → D2.3 EN/AR → D2.4 enrichment → D2.5 media → D2.6 completeness audit → D2.7 portable freeze`.

**Decision:** Final Astro-first vs Instatic-first selection, public-page architecture, filter UX, visual design and production frontend work are deferred until D2.7 is frozen.

**Decision:** Supabase is not part of Edu Hub. Ask Kalam infrastructure/data must remain unrelated.

**Decision:** The data/research layer must remain portable and presentation-neutral. The relational SQL model is a domain/reference model; physical runtime storage is chosen later.

## 3. Evidence architecture and source of truth

**Decision:** The logical data path remains:

`external source → raw evidence → staging/reconciliation → reviewed canonical data → public projection → website`.

**Decision:** Raw and staging layers are private and never published directly.

**Decision:** Official/regulatory/accreditation/institution-primary evidence is preferred over secondary directories.

**Decision:** Conflicting assertions remain explicit review work. Missing facts never justify invented values.

**Decision:** Current changing facts should preserve lifecycle/history rather than silently overwrite older evidence.

**Decision:** AI may assist research, matching, localization and drafting but may not invent unsupported facts or silently promote review hints to canonical truth.

## 4. Active international-education scope

**Decision:** Active Phase 1 scope is international education in Egypt, including:

- private/independent international schools;
- private/independent IB World Schools;
- recognized foreign-national/international school models;
- recognized foreign university branch campuses;
- internationally chartered/accredited/binational/transnational institutions whose international status is substantive.

**Decision:** Egyptian public schools and ordinary Egyptian public universities are not active Phase 1 targets.

**Decision:** Historical national-registry work is retained as evidence/history and may support future expansion, but it does not drive current publication.

## 5. International eligibility standard

**Decision:** Every candidate has an explicit scope/review state. International branding words such as `International`, `American`, `British`, `German`, `Canadian`, etc. never establish eligibility by themselves.

**Decision:** Strong school evidence may include active IB authorization, official French homologation, recognized German foreign-school evidence, BSO/recognized foreign-national status, or comparable current regulatory/accreditation evidence combined with the relevant ownership/scope rule.

**Decision:** British Council Partner School/attached-centre status is discovery/support evidence only and does not itself grant eligibility.

**Decision:** Cognia registry presence is accreditation/support evidence and does not automatically establish Edu Hub international eligibility.

**Decision:** Overture, OpenStreetMap, V7 and commercial directories are supporting/discovery sources. They cannot grant international eligibility alone.

## 6. Higher-education boundary — substantive international status

**Decision:** Recognized current foreign university branches are eligible.

**Decision:** AUC is eligible as an internationally chartered/accredited independent institution when backed by current institutional and recognized accreditation evidence.

**Decision:** Egyptian incorporation, private-university classification or national legal form is **not automatically exclusionary** when separate current evidence establishes substantive **binational, intergovernmental, transnational or international-organizational status**.

**Decision:** A foreign partnership, exchange, franchise, validation, dual-degree arrangement or international-sounding name alone remains insufficient. Those relationships may later be represented at programme level without making the whole institution internationally scoped.

**Decision:** The 2026-09-15 reviewed substantive-international HE package qualifies the following source/evidence rows under this standard:

- German International University (GIU) — current German-Egyptian/transnational evidence;
- German University in Cairo (GUC) — current binational/transnational evidence;
- French University in Egypt (UFE) — Franco-Egyptian intergovernmental/dual-ministry evidence;
- The British University in Egypt (BUE) — Egypt–UK establishment basis plus substantive UK-validated institutional model;
- Arab Academy for Science, Technology and Maritime Transport (AASTMT) — League of Arab States specialized-organization status and SCU international/framework classification.

**Decision:** These five rows are source/evidence additions, not five automatically created unique canonical institutions.

**Reference:** `tools/data-acquisition/international/seeds/substantive-international-higher-ed-review-2026-09-15.json`.

## 7. Overture higher-education review boundary

**Decision:** Overture category/name signals are triage inputs only. Every HE decision must be explicit and source-backed; no row is promoted because Overture labels it `college_university`.

**Decision:** At the accepted 2026-09-15 checkpoint, the full 70-row post-overlay HE queue is explicitly reviewed with **0 HE rows outstanding**:

- 14 existing eligible HE aliases/subunits;
- 21 out-of-scope Egyptian HE rows/subunits without sufficient substantive-international status;
- 33 supporting-only academy/training/institute leads with no qualifying current HE evidence;
- 1 Overture category error resolving to existing Egypt British International School BSO evidence;
- 1 Overture category error (`Mansoura College International Schools`) rerouted to pre-university provider/division review.

**Decision:** Rerouting a category error does not create or merge an identity.

**References:** `overture-higher-ed-scope-review-2026-09-15-batch1.json` and `apply_overture_higher_ed_resolutions.py`.

## 8. Source-family and layer-count semantics

**Decision:** Source/evidence counts, reviewed identity counts, campus counts and division counts are separate contracts and must never be conflated.

**Decision:** The deterministic 96-row foundational seed and 106-row historical classified strong-source layer remain independently reproducible provenance layers.

**Decision:** Complete current source families may supersede an older same-publisher subset **for current universe counting only** when the supersession is deterministic and explicit. Historical evidence is preserved.

**Decision:** The four historical Cognia milestone rows are superseded for current counting by the complete 256-row Cognia Egypt registry; only their already-reviewed decisions carry forward through exact same-publisher/name logic. The other Cognia rows receive no automatic eligibility.

**Decision:** Canadian offshore-school and ZfA DAS evidence are additive source families, not automatic unique-institution additions.

**Decision:** Current ZfA DAS membership is distinct from current exam authorization. Deutsche Schule Hurghada retains current DAS evidence while the checked KMK Sek-I lifecycle records last conducted year `2024/2025`; no later Sek-I authorization is asserted.

**Decision:** Accepted D2.1 run `35009564541` establishes the current **602 source/evidence row** checkpoint: **133 eligible / 466 supporting / 3 excluded**. `602` is not a unique-institution count.

## 9. Supporting discovery qualification is evidence-separated

**Decision:** Supporting discovery may expand research coverage without rewriting historical strong-source layers.

**Decision:** Discovery rows remain supporting candidates until a separate explicit review supplies qualifying primary/regulatory/accreditation evidence.

**Decision:** Primary re-sourcing is additive. Discovery provenance records how a lead was found; it is not automatically the eligibility basis.

**Decision:** No unmatched row is assumed unique merely because no duplicate has yet been found.

## 10. Identity, provider, campus and division boundaries

**Decision:** Institution, provider/group, physical campus and curriculum/language/phase division are distinct concepts.

**Decision:** A British, American, French, IB or other section inside the same school/provider must not be silently duplicated as a separate institution merely because one source lists that section independently.

**Decision:** Division-scoped curriculum, accreditation, admissions, contacts, fees and programme evidence must stay division-scoped unless broader evidence supports institution-wide promotion.

**Decision:** Cross-source reconciliation may conclude `same institution, different division` or `same provider, distinct school/campus` without forcing either duplication or a broad merge.

**Decision:** A reviewed institution does not imply a complete campus topology. `current campus evidenced` and `campus structure complete` are separate states.

**Decision:** One known address never proves one-campus completeness. Historical locations are not current campuses unless current evidence supports them.

**Decision:** Multi-campus review is explicit and additive; absence of another known campus is not proof that none exists.

## 11. Review artifacts are not runtime database writes

**Decision:** D2.2 may materialize deterministic reviewed draft artifacts before runtime storage is selected, provided provenance and review boundaries are preserved.

**Decision:** Deterministic draft IDs do not by themselves create canonical runtime rows or publication rights.

**Decision:** Identity review and eligibility remain separate. Grouping source records does not automatically select institution-wide scope where evidence remains division-specific or conflicted.

**Decision:** Incremental explicit identity-review batches are additive, checked in and exact-source-key based. They may not retarget already-reviewed rows or auto-merge identities.

**Decision:** Incremental source overlays preserve the foundational snapshot. New current evidence is layered rather than destructively rewriting historical evidence.

## 12. Name matching and automation safety

**Decision:** Normalized-name or fuzzy similarity may generate review hints only. It never authorizes a canonical merge.

**Decision:** No pipeline may auto-create canonical institutions, auto-merge source identities, auto-infer campus completeness, or auto-publish raw/staging data.

**Decision:** Exact source keys/Overture IDs are required for checked-in gap-resolution decisions.

## 13. OSM and geospatial discovery

**Decision:** OSM remains a permitted supporting discovery/geography source.

**Decision:** Hosted CI Overpass failure is diagnostic state, not negative evidence. Accepted diagnostic run `34997269459` recorded all 12 Egypt tiles blocked as `environment_blocked_all_tiles`; this must never be reported as zero OSM candidates.

**Decision:** Overture is the current functioning broad geospatial supporting layer. It still cannot grant eligibility.

## 14. V7 owned archive

**Decision:** Legacy V7 is not bulk-promoted into the clean registry.

**Decision:** The 24,916-row V7 archive may be queried read-only for exact overlap and missing-name discovery. Useful unmatched legacy leads must be re-sourced from a current permitted source before altering accepted D2.1 evidence or eligibility.

**Decision:** V7 matching performs no fuzzy auto-merge and creates no canonical identities.

## 15. Edarabia policy

**Decision:** Edarabia is **reference-only discovery**, not a bulk acquisition source.

**Decision:** Do not bulk scrape, systematically store, reproduce or publish Edarabia content unless written permission/license is obtained.

**Decision:** Any useful Edarabia lead/fact must be re-sourced from an institution-primary, regulator, accreditor, awarding-body or otherwise permitted source before canonical use.

**Decision:** Edarabia ratings/reviews and images are not imported into canonical/public data without an independent lawful basis.

**Reference:** `docs/SOURCE-USAGE-POLICY.md`.

## 16. EN/AR localization

**Decision:** Arabic and English are first-class locales tied to one factual entity graph.

**Decision:** Language-neutral facts are stored once; localized names/descriptions/display text retain localization origin/status.

**Decision:** Prefer official Arabic names where available. Transliteration/editorial Arabic must be explicitly marked and never represented internally as official sourced Arabic.

## 17. Fees, admissions and temporal facts

**Decision:** Fees and admissions are versioned by academic year/cycle; new values do not overwrite historical values.

**Decision:** Lifecycle-sensitive regulatory/accreditation facts retain dates/status and are not silently presented as current after expiry or supersession.

## 18. Media rights and publication boundary

**Decision:** Edu Hub may retain media discovery/provenance without having publication rights.

**Decision:** Official institution website/social images remain `public_use_allowed=false` unless a defensible reuse basis exists.

**Decision:** Publication-safe media may come from institution permission/claim, verified open/Wikimedia licensing with attribution, or original Edu Hub/Admonk production.

**Decision:** If no safe image exists, a designed placeholder using the institution's English name is valid and preferable to scraping/hotlinking.

**Decision:** Every eligible final institution must reach a terminal media state, including `placeholder_required` where appropriate.

## 19. SEO/publication boundary

**Decision:** A database record does not automatically become an indexable page.

**Decision:** Arbitrary filter combinations do not automatically generate SEO pages.

**Decision:** Only reviewed public projections may be published/indexed.

## 20. Durable continuation and handoff

**Decision:** `docs/EDU-DATA-2-CONTINUATION.md` is the durable execution cursor and GitHub Issue #8 is the visible roadmap.

**Decision:** Every substantial continuation agent must read `AGENTS.md`, `PROJECT-STATUS.md`, this decision file, the continuation file, Issue #8 and `DATASET-LAYERS.md` before resuming.

**Decision:** After every material accepted checkpoint, update deterministic code/evidence, obtain green CI, then synchronize `DATASET-LAYERS.md`, `PROJECT-STATUS.md`, this file when contracts change, `EDU-DATA-2-CONTINUATION.md`, and Issue #8.

**Decision:** Do not leave the next agent dependent on chat history.

## 21. Current exact cursor

**Decision:** Overture higher-education review is complete and must not be restarted.

**Decision:** The next D2.1 task is the explicit `Mansoura College International Schools` provider/division reconciliation using current first-party evidence, followed by the remaining high-signal school queue, V7 read-only gap comparison, Edarabia reference-only pass and final primary-source exhaustion.

**Decision:** D2.1 remains open until those gap-exhaustion criteria are satisfied and an explicit closure decision hands the sole active cursor to D2.2.
