# Edu Hub Project Status

Last updated: 2026-08-18

## Current lifecycle

```text
00 Open                  APPROVED
01 Discover              APPROVED
02 Align + Audit         APPROVED FOR CURRENT SCOPE
03 Define                APPROVED
04 Content + Structure   IN PROGRESS
05 Creative Direction    NOT STARTED
06 Design + Systemize    NOT STARTED
07 Build + Connect       READY FOR MILESTONE 0
08 Verify + Optimize     NOT STARTED
09 Review + Launch       NOT STARTED
10 Handoff + Learn       NOT STARTED
```

## Current project state

Edu Hub is an Admonk-owned independent education discovery and knowledge platform.

Initial market: Egypt.

Primary audience:

1. Parents
2. Students

Phase 1 combines:

- structured education-provider directory
- bilingual public experience
- editorial/knowledge platform
- internal research/admin system
- source provenance and freshness workflows
- technical SEO and AI-search discoverability foundation

Phase 2 commercial functionality is intentionally deferred.

## Approved architecture direction

- Astro + TypeScript
- monorepo with public app and control/admin app
- PostgreSQL as source of truth
- Supabase as initial database/auth/storage platform
- PostGIS for geographic capability
- Arabic + English from launch
- country-aware locales beginning with `ar-EG` and `en-EG`
- official-source-first data collection
- explicit source/evidence model
- deterministic indexability rules
- curated programmatic SEO only
- PostgreSQL search first; dedicated search infrastructure only after evidence justifies it

## Current implementation milestone

**Milestone 0 — Foundation**

Milestone 0 should create the trustworthy engineering foundation only. It must not implement the canonical institution data model from Milestone 1 beyond minimal connectivity/schema tooling required to prove the stack.

Milestone 1 begins only after Milestone 0 acceptance criteria pass.

## Immediate next actions

1. Implement GitHub Issue #1 — Milestone 0 foundation.
2. Verify lint, typecheck, tests/configuration, production builds and rendered app shells.
3. Record actual deployment/runtime decisions in `docs/PLATFORM.md` and `docs/PROJECT-DECISIONS.md`.
4. Then implement Issue #2 — canonical data foundation.
5. Build a representative 20–30 institution test cohort after the core schema exists.

## Blockers / unresolved decisions

These do not block Milestone 0:

- final public brand name and domain
- final hosting/adapter selection
- final visual identity
- final production design system
- final map provider
- final analytics implementation
- exact initial search-demand prioritization by location/curriculum

They must be resolved before the relevant downstream milestone.

## Non-negotiable project constraints

- Do not build monetization during Phase 1 foundation work.
- Do not equate paid status with verification.
- Do not auto-index every database entity or filter combination.
- Do not allow AI to silently overwrite verified factual data.
- Do not commit secrets.
- Keep Arabic/RTL and performance requirements active from the beginning.
