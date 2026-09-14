# Edu Hub Project Decisions

This file contains the **active durable decisions** for the current product scope.

Historical national-registry decisions remain preserved on branch `edu-data-1-national-registry` and in Git history. They are not active instructions unless explicitly carried forward below.

## 2026-08-18 — Ownership and product model

**Decision:** Edu Hub is an Admonk-owned product venture presented as an independent brand.

**Decision:** Egypt is the first market.

**Decision:** Parents and students are the primary audience.

**Decision:** Phase 1 focuses on trustworthy discovery/directory data, editorial authority, research/admin operations, bilingual SEO architecture and the data foundation. Monetization is deferred.

## 2026-08-18 — Platform

**Decision:** Astro + TypeScript remains the approved frontend/application direction.

**Decision:** PostgreSQL is the operational source of truth.

**Decision:** Supabase is the approved initial database/auth/storage platform direction, with PostGIS for geographic needs.

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

**Decision:** Identical media binaries should be content-addressed/deduplicated while preserving every source-to-media provenance link.

## 2026-09-13 — Evidence architecture retained

**Decision:** The enforced data path remains:

`external source -> edu_raw -> edu_staging -> edu_core -> public projection -> website`

**Decision:** `edu_raw` and `edu_staging` are private evidence/research layers and are never published directly.

**Decision:** Identity validity is separate from profile completeness. Missing fees, media or contact fields do not justify invented values.

**Decision:** Conflicting assertions remain review work until resolved.

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

**Decision:** The clean database extends the evidence layers with explicit providers, campuses, international eligibility, curricula, accreditations, contacts, fees, admissions, higher-education structures and rights-aware media metadata.

**Decision:** Legacy V7 data is not bulk-promoted into the clean registry. Only legacy rows matched to an EDU-DATA-2 eligible institution may contribute supporting assertions.

**Decision:** Edu Hub must use a dedicated Supabase/PostgreSQL project. Ask Kalam database projects may not receive Edu Hub data.

## 2026-09-14 — SEO/publication boundary retained

**Decision:** A database record does not automatically become an indexable page.

**Decision:** Arbitrary filter combinations do not automatically generate SEO pages.

**Decision:** Only reviewed public projections are eligible for publication/indexing.

## Pending decisions

- dedicated Edu Hub Supabase organization/project provisioning;
- final public brand name/domain;
- final hosting provider/Astro adapter;
- final visual identity/design system;
- final map provider;
- final analytics/consent stack;
- exact minimum profile completeness threshold for first public launch;
- institution media permission/claim workflow for Phase 2.
