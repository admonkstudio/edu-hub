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

## 2026-09-09 — Private Supabase raw archive boundary

**Decision:** The Supabase `edu_raw` schema is an internal evidence/archive surface, not a browser-facing Data API. Anonymous and authenticated roles receive no schema, table, sequence, or function access.

**Decision:** Raw acquisition data will not be imported into either Ask Kalam Supabase project. Edu Hub requires a dedicated project/account boundary.

**Decision:** V7 imports are archive-addressed, resumable and idempotent. The import ledger uses the archive version and SHA-256; records retain source hashes, media retains source identity and file hashes, and acquisition runs retain archive-local identity.

**Decision:** The raw JSON payload does not receive a speculative GIN index. Public search and fast rendering will use a later purpose-built canonical/public read model rather than querying source-shaped evidence payloads.

## 2026-09-13 — Egypt National Education Registry

**Decision:** EDU-DATA-1 replaces broad scraped-directory expansion as the active data milestone. Edu Hub will first build Egypt's canonical education identity registry, then enrich known entities progressively.

**Decision:** The enforced data path is `external source -> edu_raw -> edu_staging -> edu_core -> public projection -> website/CMS`. Raw/staging evidence may never be published directly.

**Decision:** Institution identity validity is separate from profile completeness. A legitimate institution remains valid even when fees, contacts, websites, media or other optional fields are unknown or not applicable.

**Decision:** Every externally sourced canonical fact must retain provenance. Conflicts remain competing assertions/review work until resolved; AI and enrichment processes may not invent missing facts.

**Decision:** Official national totals are coverage targets, not acquired-row counts. Secondary directories cannot be used to claim complete MOE or MOSS national coverage.

**Decision:** MOE/EMIS is the required primary identity source for the national school universe. If hosted runners cannot reach it, acquisition must run from an Egypt-reachable environment or use an official machine-readable export rather than substituting a secondary directory.

**Decision:** MOSS nursery coverage must come from an official row-level export/data-sharing route or the ministry's public nursery platform when such data is exposed; secondary nursery directories are discovery/enrichment only.

## 2026-09-14 — Higher-education hierarchy reconciliation

**Decision:** MOHESR technical institutions preserve the official hierarchy of 8 technological-college parents and 44 technical institutes instead of flattening all rows into unrelated institutions.

**Decision:** Source-declared parent/child relationships enter staging as source-backed relationship proposals. They are not automatically accepted into `edu_core`, and CI must enforce zero automatic identity/relationship acceptance and zero public promotion.

## 2026-09-14 — EMIS live-route availability and pilot scope

**Decision:** A category-specific EMIS form may be used to validate reusable ASP.NET state/postback mechanics only within the scope actually observed. A healthy Special Education form does not unlock or count as government-school acquisition coverage.

**Decision:** Government-school enumeration remains blocked whenever the government category route returns a server-side failure, even if the EMIS root or another category is healthy. The 62,690-school national target may only be evaluated against source rows acquired from the required official government-school identity source or an official export.

**Decision:** Bounded EMIS contract probes may submit top-level category navigation and one explicit non-search dependent-control postback when necessary to reveal the search contract. They may not submit a school-search button, follow result pagination, enumerate school rows, mutate `edu_core`, or promote public records until a separately reviewed pilot gate is satisfied.

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
