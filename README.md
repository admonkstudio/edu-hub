# Edu Hub

Edu Hub is an Admonk-owned, independent bilingual education discovery and knowledge platform focused initially on **international education in Egypt**.

Phase 1 combines a structured directory of private/independent international schools and internationally scoped higher-education institutions with an editorial knowledge platform designed for useful discovery, trustworthy research, strong organic search visibility and AI-search discoverability.

## Active Phase 1 scope

Included:

- private/independent international schools in Egypt;
- private/independent IB World Schools;
- recognized British, American, French, German, Canadian and comparable international-school models;
- recognized foreign university branches in Egypt;
- internationally chartered/accredited independent higher-education institutions where international status is substantive;
- campuses and early-years sections belonging to eligible institutions.

Excluded from the active registry:

- Egyptian public schools;
- Egyptian public universities;
- the national nursery universe;
- ordinary language schools or exam centres without sufficient international-status evidence;
- Egyptian universities that only have foreign partnerships, dual degrees or exchange agreements.

Historical broader Egypt registry work is preserved in Git for possible future expansion, but it is not an active product dependency.

## Core product thesis

```text
Trustworthy structured international-education information
→ useful discovery and comparison
→ search visibility and authority
→ qualified parent/student audience
→ intent
→ future monetization
```

Phase 1 is data quality, authority and traffic. Phase 2 may add claimed profiles, premium plans, advertising, leads, applications, consultants and related commercial functions only after the core information product proves useful.

## Primary audience

1. Parents researching international education options for their children.
2. Students researching internationally scoped universities, programmes, admissions, costs and pathways.

Institutions and commercial participants are secondary audiences attracted by parent/student demand.

## Platform direction

- Astro + TypeScript
- PostgreSQL as source of truth
- Supabase as the initial database/auth/storage platform
- PostGIS for geographic capability
- Arabic and English from launch (`ar-EG`, `en-EG`)
- evidence-first international eligibility
- field/source provenance for important facts
- rights-aware media acquisition
- curated programmatic SEO, never unrestricted filter-index generation

## Data architecture

```text
external source
→ edu_raw
→ edu_staging
→ edu_core
→ public projection
→ website
```

Public pages never depend on live third-party source APIs after acquisition, and raw/staging evidence is never published directly.

## Project control

Read `AGENTS.md` before substantial work.

Current source of truth:

- `docs/PROJECT-STATUS.md`
- `docs/PROJECT-DECISIONS.md`
- `docs/EDU-DATA-2-INTERNATIONAL-REGISTRY.md`

Core supporting definition:

- `docs/PROJECT-BRIEF.md`
- `docs/PRODUCT-ARCHITECTURE.md`
- `docs/DATA-MODEL.md`
- `docs/SEO-ARCHITECTURE.md`
- `docs/CONTENT-STRATEGY.md`
- `docs/PLATFORM.md`

Reusable Admonk studio intelligence remains maintained in `admonkstudio/admonk`; do not copy the entire studio agent system into this repository.
