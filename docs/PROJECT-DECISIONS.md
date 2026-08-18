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

## Pending decisions

- final public brand name
- final domain
- final hosting provider/Astro adapter
- final visual identity
- final production design system/styling strategy
- final map provider
- final analytics/consent stack
- exact first public institution/data cohort
