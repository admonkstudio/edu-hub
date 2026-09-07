# Edu Hub Project Decisions

Record durable decisions here. Do not use this file for temporary task notes.

## 2026-08-18 — Project ownership and brand relationship

**Decision:** Edu Hub is an Admonk-owned product venture presented as an independent brand rather than an Admonk-branded client service.

## 2026-08-18 — Initial market

**Decision:** Egypt is the first market. Global expansion is a future possibility, not a Phase 1 requirement.

## 2026-08-18 — Primary audience

**Decision:** Parents and students are the primary audience. Institution/commercial demand should follow user demand.

## 2026-08-18 — Phase boundary

**Decision:** Phase 1 focuses on directory + editorial authority, research/admin operations, bilingual SEO architecture and the data foundation. Monetization functions are deferred to Phase 2.

## 2026-08-18 — Platform

**Decision:** Astro + TypeScript is the approved frontend/application framework direction.

**Decision:** PostgreSQL is the operational source of truth.

**Decision:** Supabase is the approved initial backend platform direction for database/auth/storage, with PostGIS for geographic needs.

## 2026-08-18 — Bilingual architecture

**Decision:** Arabic and English launch together as first-class locales, initially `ar-EG` and `en-EG`.

## 2026-08-18 — Data trust

**Decision:** Official/primary sources are prioritized.

**Decision:** Factual/data verification is separate from commercial/payment status.

**Decision:** Important changing facts should preserve source provenance and history where practical.

## 2026-08-18 — SEO architecture

**Decision:** Database records do not automatically become indexable pages.

**Decision:** Arbitrary faceted/filter combinations do not automatically generate indexable SEO URLs.

**Decision:** Programmatic landing pages must be curated/rule-governed and justified by real user/search value.

**Decision:** Dynamic database-driven routes require a database-driven sitemap strategy.

## 2026-08-18 — Search

**Decision:** Start with PostgreSQL search + structured filters + PostGIS. Introduce a dedicated search engine only when measured requirements justify it.

## 2026-08-18 — AI boundary

**Decision:** AI can assist research, briefs, drafting, localization and refresh detection but must not initially publish unsupported factual content or silently overwrite verified canonical facts.

## 2026-08-18 — Reusability

**Decision:** Build Edu Hub cleanly but do not prematurely create a generic multi-vertical SaaS framework. Generalize only after another real vertical demonstrates reusable boundaries.

## 2026-09-06 — Owned data and runtime independence

**Decision:** Edu Hub must hold its own persistent copy of acquired institution records. Third-party directories, government sites and APIs are acquisition/refresh inputs only; they must never be required to render an institution already acquired by Edu Hub.

**Decision:** Public page rendering must use Edu Hub-controlled database projections rather than live source API calls.

**Decision:** Media is a first-class part of the acquisition corpus. Media candidates, their provenance and—where acquisition is permitted—the binary copies themselves must be preserved under Admonk-controlled storage. Published pages must not depend on source-site image hotlinks.

**Decision:** Operational possession/control of a media copy is separate from copyright/publication rights. Media rights state and public-use eligibility must be tracked explicitly, with public use disabled by default until a defensible reuse basis is established.

**Decision:** Database records and media storage must be portable and independently restorable. Provider accounts are infrastructure, not the only backup/source of truth.

**Decision:** Owned acquisition exports must be portable and independently verifiable with database and media checksum manifests.

**Decision:** Identical media binaries should be stored once by content hash while retaining every source-record-to-media provenance link.

**Decision:** Raw snapshot hashes must include source-record identity and the complete stored row, not payload content alone, so distinct records with identical payloads cannot be dropped by uniqueness constraints.

## 2026-09-07 — MadaresEgypt profile acquisition boundary

**Decision:** MadaresEgypt is treated as a listing-level source for the current acquisition phase. A deterministic 50-record sample spanning the complete owned ID range produced zero accepted profiles and 50 read timeouts under a five-second, no-retry diagnostic.

**Decision:** Do not scale MadaresEgypt profile or media crawling from the current `/ar/Item/{id}` route. Reconsider only if a materially different, validated source endpoint or acquisition path becomes available.

**Decision:** The existing 11,339 MadaresEgypt listing records remain part of the owned raw corpus with their source provenance. This limitation affects enrichment yield, not ownership or render independence.

## 2026-09-07 — V7 consolidated owned archive

**Decision:** V7 is the current complete portable acquisition archive. It consolidates V5 and V6 into 24,916 raw records across 13 sources, with explicit local ownership metadata for every record.

**Decision:** V7 preserves 2,101 media provenance references and 453 content-addressed media binaries. Publication remains disabled for all acquired media until rights review.

**Decision:** A release archive is accepted only after database integrity, foreign-key checks, record uniqueness checks, media hash verification, gzip/archive traversal, and the complete internal checksum manifest pass.

**Decision:** The damaged local V6 tarball is superseded and must not be used for restore. The complete extracted V6 database/media tree was the validated input to V7.

**Decision:** PostgreSQL/Supabase may become the operational serving database, but the portable V7 SQLite database, media tree, manifests, and checksums remain an independent owned restore source.

## Pending decisions

- final public brand name
- final domain
- final hosting provider/Astro adapter
- final visual identity
- final production design system/styling strategy
- final map provider
- final analytics/consent stack
- exact first public institution/data cohort
- final Admonk-controlled production object-storage/CDN implementation for media
