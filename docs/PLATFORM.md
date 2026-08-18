# Edu Hub Platform

## Approved direction

Edu Hub is a code-native Astro project backed by PostgreSQL/Supabase.

### Core stack

- Astro + TypeScript
- PostgreSQL
- Supabase Database
- Supabase Auth
- Supabase Storage
- PostGIS
- Zod at application boundaries
- PostgreSQL search first
- server-side/background jobs only where justified

The initial deployment direction is Vercel with Astro's official `@astrojs/vercel` adapter. The public app is statically prerendered; the authenticated control app uses server rendering. Vercel server dependencies are bundled to keep pnpm-based output portable across hosts.

External setup remains: create two Vercel projects rooted at `apps/web` and `apps/control`, configure canonical origins/secrets, and verify preview and production deployments. No hosted deployment has been claimed.

## Repository architecture

Preferred monorepo direction:

```text
apps/
  web/       Astro public platform
  control/   Astro internal admin/research platform

packages/
  database/
  domain/
  seo/
  config/
```

`research` and `ui` packages were intentionally not created because Milestone 0 has no concrete responsibility for them.

Do not create a generic multi-vertical product framework yet. Extract shared infrastructure only after another real vertical demonstrates what is genuinely reusable.

## Rendering policy

Default principle:

> Keep static content static; use on-demand rendering for data-heavy/dynamic routes; hydrate only real interaction.

Likely policy:

### Prerender/static where suitable

- homepage
- stable marketing/legal pages
- selected major directory/topic hubs when appropriate

### Server/on-demand + caching where suitable

- institution profiles
- large location/category pages
- high-volume data-driven landing pages
- browse/search result experiences

### Client islands only where justified

- filtering
- autocomplete
- maps
- comparison
- future account-specific interaction

Do not add React/Svelte/Vue islands by default.

## Database

PostgreSQL is the source of truth.

Supabase is an implementation platform, not the domain model. Keep the schema portable enough that important product logic does not depend unnecessarily on proprietary abstractions.

Milestone 1 supplies migration-owned tables for providers, institutions, localized editorial fields, campuses, hierarchical locations, controlled taxonomies, and explicit many-to-many relationships. PostGIS geography columns and GiST indexes support future location queries. Generated database types and explicit repository functions are the application access boundary.

## Security

- Never expose service-role/secret credentials to public browser code.
- Enable/design RLS deliberately for exposed schemas.
- Anonymous reads expose active taxonomies/locations and only institutions in `public_noindex`, `index_ready`, or `published` states.
- Admin/research writes require a verified Supabase Auth user with an active `staff_users` row. Staff can read drafts; ordinary authenticated users cannot. Suspended staff are rejected even if an earlier token still exists.
- Every exposed table has RLS, explicit grants, and operation-specific policies. The service-role key is not used by the control browser or its normal request path.
- Authenticated direct inserts/updates/deletes are revoked for canonical institution records. Assertion review, conflict resolution, and task transitions are likewise command-only so authorization and audit recording cannot be bypassed through the Data API.
- Future institution users should submit change requests rather than receive unrestricted direct writes to canonical institution data.
- Perform security review before enabling public user data, uploads, claims, payments or lead/application workflows.

## Localization

Launch locales:

- `en-EG`
- `ar-EG`

Requirements:

- locale-aware routes
- correct HTML language/direction
- RTL layout support
- locale-specific metadata
- `hreflang`
- localized content validation
- Arabic search normalization without altering canonical display strings

## Search

Start with PostgreSQL full-text/trigram/structured filtering and PostGIS where relevant.

Do not add Algolia/Elasticsearch/Typesense or another dedicated search service until measured query latency, ranking needs, corpus size or product requirements justify it.

## Performance

Performance is continuous, not a launch-only task.

Track:

- server response/cache behavior
- client JavaScript/island cost
- image/media delivery
- fonts
- third-party scripts
- layout stability
- interaction responsiveness
- large-query/database behavior
- mobile runtime

## QA

Minimum implementation checks where configured:

```text
lint
→ typecheck
→ tests
→ production build
→ browser QA
→ responsive/RTL QA
→ console/network review
```

Use the canonical Admonk Astro, Supabase, performance, localization, browser-QA, security and SEO skills from `admonkstudio/admonk` for substantial work.

## Environment handling

Provide `.env.example` with non-secret variable names only.

Never commit actual credentials/secrets.

Validate required environment variables at startup/build boundaries.

Zod schemas validate public origins and Supabase configuration. Astro's server environment API supplies the control app's URL and publishable key at runtime; the staff access token remains in an HttpOnly, strict-same-site cookie. `SUPABASE_SECRET_KEY` remains server-only and is not required for normal control CRUD.

## Supabase development workflow

The repository contains CLI configuration, immutable migrations, deterministic foundation seeds, pgTAP tests, generated types, and optional fictional fixtures. Local development uses `pnpm db:start`, `pnpm db:reset`, `pnpm db:types`, `pnpm test:db`, and `pnpm db:fixtures`. Docker and a hosted project are external dependencies.

Edu Hub uses local ports `55320`–`55329` to coexist with other Supabase projects using the defaults. Clean migration reset, seeds, generated types, RLS tests, fixtures, and database advisors were verified on 2026-08-18.

## Milestone 2 trust operations

Canonical institution creation/update now crosses one PostgreSQL transaction and writes its change set/revisions atomically. The exposed RPC wrapper is an invoker; privileged mutation logic remains in the unexposed `private` schema with explicit execution grants, actor/role validation, and an empty search path.

The trust schema includes sources, restrained snapshots, field assertions, assertion conflicts, research tasks, freshness policies/state, completeness requirements, and readiness evaluation. Control exposes assertion/evidence entry, reviewer decisions, conflict resolution, task assignment/transitions, freshness, readiness, and canonical audit history.

Control authentication stores access and refresh tokens only in HttpOnly cookies, refreshes expired access tokens server-side, revalidates active staff roles per protected request, and supports explicit sign-out.

Local verification covers clean reset, 36 pgTAP tests, protected direct-write denial, role denial, rollback, suspended login, invalid-access-token refresh, logout, anonymous API denial, and the complete researcher-to-reviewer workflow. Hosted behavior is not yet verified.

## Deployment decision resolved in Milestone 0

Vercel + the official Astro adapter is configured as the initial direction. External account/project creation and deployed-preview verification remain outstanding.
