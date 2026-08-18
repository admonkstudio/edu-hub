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
- final visual identity
- final production design system/styling strategy
- final map provider
- final analytics/consent stack
- exact first public institution/data cohort

## 2026-08-18 — Milestone 0 workspace and tooling

**Decision:** Use pnpm workspaces without Turborepo/Nx. The current dependency graph and quality gates do not justify a separate orchestration layer.

**Decision:** Keep `apps/web` and `apps/control` as independent Astro applications and create only `database`, `domain`, `seo`, and `config` shared packages. `research` and `ui` wait for a concrete milestone responsibility.

**Decision:** Pin Node.js 22.12+, pnpm 11.19.0, Astro 7.2.2, and TypeScript 6.0.3. TypeScript 7 was evaluated but rejected because the current Astro language-server check explicitly requires the TypeScript 6 programmatic API.

**Decision:** Use Vitest for shared helper tests and Playwright for rendered shell smoke tests. CI installs Chromium and runs browser smoke tests after the build gates.

## 2026-08-18 — Supabase foundation boundary

**Decision:** Commit the current CLI-generated local Supabase configuration and an empty migration convention. Do not create a placeholder domain table or canonical directory schema in Milestone 0.

**Decision:** Use local ports `55320`–`55329` for Edu Hub so its stack can coexist with another Supabase project using the CLI defaults.

**Decision:** Provide only a server-side Supabase client boundary using a secret key and validated environment. No browser client exists until a real public-client use case and RLS policy are approved.

## 2026-08-18 — Initial deployment direction

**Decision:** Configure Astro's official Vercel adapter for both apps. Vercel is the initial hosting direction because it supports Astro on-demand rendering, pull-request previews, environment/secrets management, cache controls, and simple operations for two independently deployed monorepo apps.

**Constraint:** Both Milestone 0 shells remain statically prerendered. On-demand routes are enabled only when later data-driven requirements justify them.

**Resolution:** Milestone 2 staging now uses one Frankfurt Supabase project plus two Vercel projects rooted at `apps/web` and `apps/control`. Production infrastructure remains intentionally uncreated.

## 2026-08-18 — Milestone 1 canonical data foundation

**Decision:** Model providers, institutions, localized editorial records, campuses, hierarchical locations, and controlled education taxonomies relationally. Keep campuses separate from institutions and use explicit join tables for searchable many-to-many concepts.

**Decision:** Use stable codes plus bilingual labels/slugs for controlled vocabularies. Seed Egypt and its 27 governorates using CAPMAS's official governorate set and ISO 3166-2 subdivision codes; do not treat local fixtures as factual institution data.

**Decision:** Store geography with PostGIS `geography(Point, 4326)` and GiST indexes. Install extensions in the `extensions` schema rather than `public`.

**Decision:** Separate editorial/data readiness from publication/indexability. Anonymous access is restricted to intentional public states; an active Supabase Auth user mapped through `staff_users` is required for canonical writes and draft visibility.

**Decision:** Use explicit GRANTs in addition to RLS for Data API access, operation-specific staff policies, generated Supabase types, and named repository functions instead of scattering table access through the applications.

**Decision:** Keep Milestone 1 control writes server-rendered with HttpOnly access-token cookies. A refresh-token/session-renewal workflow and atomic multi-table write RPC are deferred and recorded as risks before higher-volume operations.

**Decision:** Maintain 12 clearly fictional representative institution fixtures outside deterministic seeds. They cover independent/group, single/multi-campus, nursery/school/university, curriculum, and ownership shapes without making unsupported real-world claims.

## 2026-08-18 — Milestone 2 trust foundation

**Decision:** Canonical multi-table institution writes use authenticated public invoker wrappers calling an explicitly granted private `SECURITY DEFINER` transaction function. The private function uses an empty search path, fully qualified objects, server-derived `auth.uid()`, active-role checks, and atomic audit writes.

**Decision:** Audit history is append-only ordinary operational data, not event sourcing. Canonical tables remain the source of current truth.

**Decision:** Evidence is field-level through reusable sources, restrained snapshots, assertions, and preserved conflicts. Source authority is priority context, never automatic truth.

**Decision:** Staff sessions use access and rotating refresh tokens in HttpOnly strict-same-site cookies. Protected requests verify the Auth user and current active staff row; stale JWT role claims are not authorization inputs.

**Decision:** Initial readiness evaluation separates record existence, public readiness, and index readiness. Open conflicts or missing accepted evidence prevent readiness.

**Decision:** Revoke authenticated direct mutation grants for canonical institution records and reviewed workflow state. Audited command functions are the only supported mutation boundary for those operations; RLS remains necessary but is not treated as sufficient authorization or audit enforcement.

**Decision:** Research work is governed by `docs/RESEARCH-PROTOCOL.md`. Official-source priority does not mean automatic acceptance; conflicts remain explicit, reviewer rationale is required, Arabic and English naming are independently reviewed, and AI cannot accept or publish factual assertions autonomously.

**Decision:** Milestone 2 cannot close on local correctness alone. Hosted Supabase plus separate Vercel public/control staging, the deliberate 20–30 real-institution cohort, and a recorded workflow/model retrospective are exit criteria before Milestone 3.

## 2026-08-18 — Hosted Milestone 2 staging

**Decision:** Use one Free-plan Supabase staging project, `edu-hub-staging`, in `eu-central-1` (Frankfurt), and do not create a production project before the real cohort and retrospective are complete.

**Decision:** Use two Vercel projects from the same repository, with `apps/web` and `apps/control` as independent roots. Scope public and Control variables separately and deploy no Supabase secret/service-role credential.

**Decision:** Treat server-side staff-row revalidation as the authority boundary. Hosted testing proved that suspending an already-authenticated researcher invalidates the next privileged request without waiting for access-token expiry.

**Decision:** Keep the hosted workflow fixture as draft staging data for operational inspection. Real cohort records remain staging-only until Milestone 2 closes.

**Risk:** Supabase's hosted advisor reports leaked-password protection disabled on the Free staging project. Generated QA passwords remain high entropy; enable the protection before production if plan support permits. Informational missing-FK-index findings will be evaluated against the cohort's actual query patterns instead of adding indexes blindly.

## 2026-08-18 — Pending localization in the real-institution cohort

**Decision:** Do not invent or transliterate a canonical Arabic institution name to satisfy Control validation. When an institution-owned Arabic form cannot be established, preserve that uncertainty explicitly and treat any required-localization block as a cohort workflow/readiness finding.

**Evidence:** The Small Talk Nursery staging attempt used the researcher workflow with `draft` / `candidate`, supplied only the established English identity, and left Arabic identity pending. Control prevented submission at the required Arabic-name field, and a post-attempt database query confirmed that no institution record was created.

**Consequence:** The first cohort record remains blocked rather than being created with unsupported data. The pilot must decide how pending localization is represented before N1 can proceed through sources, assertions, and research tasks.
