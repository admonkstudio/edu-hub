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

Final deployment provider/adapter is not yet locked and should be decided during Milestone 0 based on current Astro support, runtime needs, caching, preview workflow, and operational simplicity.

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
  research/
  ui/
  config/
```

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

Use migrations and generated database types where appropriate.

## Security

- Never expose service-role/secret credentials to public browser code.
- Enable/design RLS deliberately for exposed schemas.
- Public reads should only expose intended publication states.
- Admin/research operations require authenticated roles.
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

## Deployment decision to resolve in Milestone 0

Record the chosen hosting/adapter and reason in `PROJECT-DECISIONS.md` after verifying current official Astro deployment guidance and required SSR/caching capabilities.
