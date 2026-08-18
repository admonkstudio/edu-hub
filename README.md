# Edu Hub

Edu Hub is an Admonk-owned, independent bilingual education discovery and knowledge platform.

The first market is Egypt. Phase 1 combines a structured directory of education providers with an editorial knowledge platform designed for useful discovery, trustworthy research, strong organic search visibility, and AI-search discoverability.

## Core product thesis

```text
Useful structured information
→ search visibility
→ authority
→ audience
→ intent
→ monetization
```

Phase 1 is authority and traffic. Phase 2 may add claimed profiles, premium plans, advertising, leads, applications, consultants, and related commercial functions only after the core information product proves useful.

## Primary audience

1. Parents
2. Students

Institutions, universities, advertisers, consultants, and other commercial participants are secondary audiences attracted by parent/student demand.

## Initial platform direction

- Astro + TypeScript
- PostgreSQL as source of truth
- Supabase as the initial database/auth/storage platform
- Arabic and English from launch
- country-aware locale routes (`ar-EG`, `en-EG`)
- official-source-first research
- source/evidence provenance for important facts
- curated programmatic SEO, never unrestricted filter-index generation

## Project control

Read `AGENTS.md` before substantial work.

Current project state: `docs/PROJECT-STATUS.md`

Core definition:

- `docs/PROJECT-BRIEF.md`
- `docs/PRODUCT-ARCHITECTURE.md`
- `docs/DATA-MODEL.md`
- `docs/SEO-ARCHITECTURE.md`
- `docs/CONTENT-STRATEGY.md`
- `docs/PLATFORM.md`
- `docs/PROJECT-DECISIONS.md`

Reusable Admonk studio intelligence remains maintained in `admonkstudio/admonk`; do not copy the entire studio agent system into this repository.
