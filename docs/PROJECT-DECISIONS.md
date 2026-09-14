# Edu Hub Project Decisions

This file contains the **active durable decisions** for the current product scope.

Historical national-registry decisions remain preserved on branch `edu-data-1-national-registry` and in Git history. They are not active instructions unless explicitly carried forward below.

## 2026-08-18 — Ownership and product model

**Decision:** Edu Hub is an Admonk-owned product venture presented as an independent brand.

**Decision:** Egypt is the first market.

**Decision:** Parents and students are the primary audience.

**Decision:** Phase 1 focuses on trustworthy discovery/directory data, editorial authority, research/admin operations, bilingual SEO architecture and the data foundation. Monetization is deferred.

## 2026-08-18 — Platform

**Decision:** Astro + TypeScript remains an approved frontend/application direction.

**Superseded:** The previous decision naming Supabase as the initial database/auth/storage platform is no longer active.

**Decision (2026-09-14):** Edu Hub will not use Supabase.

**Decision (2026-09-14):** The product should eventually be implemented as either Astro-first or Instatic-first. Instatic is the approved self-hosted CMS/publisher option. A hybrid Astro + Instatic stack is allowed only if there is a clear product need and one canonical data owner is defined.

**Decision (2026-09-14):** The final Astro vs Instatic presentation/runtime choice is deferred until the database-completion gate is satisfied. Current data architecture must not be bent around a premature frontend/CMS decision.

**Decision (2026-09-14):** The data/research layer must remain portable and independent of Supabase-specific database, auth, storage, RLS, Edge Functions or APIs.

**Decision (2026-09-14):** The relational SQL model remains a canonical domain/reference model, but physical runtime storage is a later implementation choice.

**Decision:** Arabic and English are first-class locales from launch, initially `ar-EG` and `en-EG`.

## 2026-08-18 — Data trust

**Decision:** Official, regulatory, accreditation and institution-primary evidence is preferred over secondary directories.

**Decision:** Factual verification is separate from commercial/payment status.

**Decision:** Important changing facts preserve source provenance and history where practical.

**Decision:** AI may assist research, matching, localization and drafting but may not invent unsupported institution facts or silently overwrite verified canonical values.

## 2026-09-06 — Owned data and media independence

**Decision:** Edu Hub retains its own persistent copy of acquired data needed to operate the product. Public pages do not depend on live third-party APIs after acquisition.

**Decision:** Media provenance and rights are separate from possession of a file. Public-use eligibility must be explicit.

**Decision:** Published pages must not hotlink source-site images as an operational dependency.

**Decision:** Identical media binaries should be content-addressed/deduplicated where the selected runtime supports it while preserving every source-to-media provenance link.

## 2026-09-13 — Evidence architecture retained

**Decision:** The enforced logical data path remains:

`external source -> edu_raw -> edu_staging -> edu_core -> public projection -> website`

**Decision:** `edu_raw` and `edu_staging` are private evidence/research layers and are never published directly.

**Decision:** Identity validity is separate from profile completeness. Missing fees, media or contact fields do not justify invented values.

**Decision:** Conflicting assertions remain review work until resolved.

**Decision:** If Instatic/SQLite/static artifacts are selected later, the logical raw/staging/core boundaries must still be preserved even if the physical storage implementation differs from the PostgreSQL reference schemas.

## 2026-09-14 — Scope reset to international education

**Decision:** EDU-DATA-2 supersedes the national all-institution registry as the active milestone.

**Decision:** Active Phase 1 coverage is limited to international education in Egypt:

- private/independent international schools;
- private/independent IB World Schools;
- recognized foreign-national/international school models;
- recognized foreign university branch campuses;
- internationally chartered/accredited independent higher-education institutions whose international status is substantive.

**Decision:** Egyptian public schools, Egyptian public universities, the 62,690-school EMIS target and the 48,225-nursery MOSS target are no longer active product requirements.

**Decision:** The national-registry work is retained historically rather than deleted. It may support future expansion but must not drive current acquisition or publication.

## 2026-09-14 — International eligibility standard

**Decision:** Every candidate has an explicit scope state: `candidate`, `eligible`, `excluded`, or `needs_review`.

**Decision:** International status must be evidenced. A name containing words such as `International`, `American`, `British`, `German`, etc. is never sufficient by itself.

**Decision:** Strong eligibility evidence can include active IB authorization, official French homologation, official German/KMK recognition, Egyptian regulator recognition of a foreign university branch, or comparable recognized regulatory/accreditation evidence.

**Decision:** British Council Partner School/attached-centre status is discovery/support evidence and does not automatically make an institution eligible. An exam centre can still be an ordinary Egyptian language/private school.

**Decision:** Overture, OpenStreetMap, commercial directories and the historical V7 archive are supporting/discovery sources. They cannot establish international eligibility alone.

**Decision:** Public/state international-school initiatives remain excluded unless the project owner later changes scope.

## 2026-09-14 — Edarabia source policy

**Decision:** Edarabia is an approved supporting/commercial directory source for discovery and enrichment leads.

**Decision:** Edarabia may contribute candidate names, addresses, websites, curriculum leads, fee leads, profile completeness hints and media discovery leads.

**Decision:** Edarabia does not establish international eligibility, accreditation, regulatory status or canonical fees by itself. Important Edarabia-derived facts must be corroborated by a regulator, accreditor or official institution source before canonical promotion.

**Decision:** Edarabia ratings/reviews are user-generated/editorial signals, not canonical factual evidence.

**Decision:** Edarabia images are discovery/provenance candidates only. They must not be republished unless an independent reuse right is established.

## 2026-09-14 — Higher-education boundary

**Decision:** Recognized foreign university branches are included.

**Decision:** The American University in Cairo is eligible as an internationally chartered/accredited independent institution when supported by current institutional and recognized accreditation evidence.

**Decision:** An Egyptian university is not classified as internationally scoped merely because it has a foreign partnership, exchange, dual degree, franchise or validated programme. Those relationships may later be represented at programme level.

## 2026-09-14 — Campus identity

**Decision:** Institution and campus identities are separate. Multiple campuses of the same school/university should not be silently represented as unrelated institutions.

**Decision:** Source-specific campus records are reconciled under one canonical institution where the evidence supports that relationship.

## 2026-09-14 — Media publication boundary

**Decision:** Official institution website/social images may be collected as media discovery candidates/provenance, but they remain `public_use_allowed=false` unless a defensible reuse basis exists.

**Decision:** Publication-safe media may come from institution-provided permission, a verified institution claim, Wikimedia Commons/open licenses with attribution preserved, or original Edu Hub/Admonk production.

**Decision:** When no safe media is available, the product uses a designed placeholder containing the institution's English name rather than Arabic initials, scraped imagery or hotlinks.

## 2026-09-14 — Database cleanup strategy

**Decision:** Create a new active branch `edu-data-2-international-registry` rather than destructively rewriting the historical national-registry branch.

**Decision:** The clean data model extends the evidence layers with explicit providers, campuses, international eligibility, curricula, accreditations, contacts, fees, admissions, higher-education structures and rights-aware media metadata.

**Decision:** Legacy V7 data is not bulk-promoted into the clean registry. Only legacy rows matched to an EDU-DATA-2 eligible institution may contribute supporting assertions.

**Superseded:** Edu Hub no longer requires a dedicated Supabase project.

**Decision:** Ask Kalam infrastructure remains unrelated and must not receive Edu Hub data.

## 2026-09-14 — Database-first completion gate

**Decision:** The current project priority is **database completion and bilingual data architecture before presentation**.

**Decision:** No final Astro/Instatic selection, profile template, filter UX, visual system or public-page architecture should drive the data model during this gate.

**Decision:** English and Arabic are modeled as first-class localizations of one canonical factual entity model. Language-neutral facts are stored once; localized names/descriptions/display text are stored separately with localization origin/status.

**Decision:** Prefer official Arabic names where available. Where no official Arabic form exists, transliteration/editorial localization must be explicitly marked and must never be presented internally as an official sourced name.

**Decision:** Database completeness is measured independently across factual coverage, English localization, Arabic localization, provenance/conflict state and media coverage.

**Decision:** Fees and admissions are versioned by academic year/cycle. New values do not overwrite historical values.

**Decision:** Every eligible institution must have an explicit media status even when no publishable image exists. `placeholder_required` is a valid completed media state.

**Decision:** The database-completion gate ends with a deterministic, presentation-neutral export containing canonical identities, EN/AR localization, source references, historical/time-sensitive facts, media manifest/rights, conflict state and completeness metrics.

**Canonical plan:** `docs/DATABASE-COMPLETION-PLAN.md`.

## 2026-09-14 — SEO/publication boundary retained

**Decision:** A database/content record does not automatically become an indexable page.

**Decision:** Arbitrary filter combinations do not automatically generate SEO pages.

**Decision:** Only reviewed public projections are eligible for publication/indexing.

## Deferred decisions until database completion

- Astro-first vs Instatic-first final implementation choice;
- if Instatic-first: physical database/storage choice based on real corpus/query requirements;
- final public profile/listing presentation architecture;
- final public brand name/domain;
- final Astro hosting adapter if Astro is selected;
- final visual identity/design system;
- final map provider;
- final analytics/consent stack;
- exact public-page completeness threshold;
- institution media permission/claim workflow for Phase 2.
