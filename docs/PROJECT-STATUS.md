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
07 Build + Connect       MILESTONE 2 IN PROGRESS
08 Verify + Optimize     MILESTONE 2 PARTIALLY VERIFIED
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

**Milestone 2 — Trust, Provenance & Research Foundation (in progress)**

Milestone 1 added the canonical relational institution foundation without entering public directory/profile work or later editorial/commercial milestones.

Implemented and verified: provider/institution/localization/campus models; controlled taxonomies and relationships; PostGIS locations; all 27 Egyptian governorates; publication/data lifecycle states; generated TypeScript types; explicit repository functions; RLS and grants; minimal staff roles; authenticated bilingual control CRUD; 12 fictional validation fixtures; pgTAP, unit, build, and browser coverage.

The local Milestone 2 implementation now includes atomic audited institution commands; direct-write protection for canonical facts and reviewed workflow state; renewable HttpOnly sessions; active-role revalidation and sign-out; expanded staff roles; sources/snapshots; field assertions; conflict detection and reviewer resolution; task assignment/status transitions; freshness state; readiness evaluation; and complete Control screens for the implemented workflows. The research protocol is recorded in `docs/RESEARCH-PROTOCOL.md`.

Verified locally on 2026-08-18: clean migration reset; 36 pgTAP checks; database advisory/lint review (only extension-owned PostGIS findings plus one harmless project variable warning); lint; typecheck; 5 unit tests; both production builds; and 7 Chromium browser tests. Browser coverage includes bilingual LTR/RTL shells, four representative widths, console/network sanity, bilingual institution CRUD, researcher evidence/conflict flow, reviewer resolution, task completion, suspended staff denial, invalid-access-token refresh, logout, anonymous API denial, and role-denial database checks.

Milestone 2 is not complete. Hosted Supabase/Vercel staging, staging migrations and auth/RLS reruns, the 20–30 real source-backed cohort, and the workflow retrospective remain outstanding. A stale active session changed to suspended after login still needs a dedicated browser case; current-request staff status is revalidated in application code, and suspended-login behavior is verified.

## Immediate next actions

1. Create/link hosted Supabase and two Vercel staging projects and migrate/configure them.
2. Rerun the complete auth, RLS, rollback, workflow, responsive, RTL, console, and network matrix on staging, including a live stale-role/session transition.
3. Only after staging trust gates pass, research the approved 20–30 real institution cohort under `docs/RESEARCH-PROTOCOL.md`.
4. Record the retrospective and model/workflow changes before approving Milestone 3.

The governing research procedure is now documented in `docs/RESEARCH-PROTOCOL.md` and must be used before any real cohort record is added.

## Blockers / unresolved decisions

These do not block the local Milestone 2 build, but hosted account access is required for its staging acceptance criteria:

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
