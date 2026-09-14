# Edu Hub Platform

## Approved direction

Edu Hub does **not** use Supabase.

The project must remain deployable through either:

1. **Astro + TypeScript** as the public application/site layer; or
2. **Instatic CMS** as the self-hosted CMS/publisher when its visual/content workflow is the better fit.

The data-acquisition and domain model must remain portable between these presentation/runtime choices. No current product requirement may depend on Supabase-specific database, auth, storage, RLS, functions or APIs.

## Core stack direction

- Astro + TypeScript for the SEO-sensitive public application when a coded frontend is required
- Instatic CMS as the preferred self-hosted visual CMS/publishing option when an editorial/admin workflow is required
- owned structured data and evidence artifacts
- relational data model for institutions, campuses, curricula, accreditations, fees, admissions, programmes and media provenance
- Zod or equivalent validation at application/import boundaries
- server-side/background jobs only where justified
- owned media storage; never operational hotlinks to third-party images

### Runtime database choice

The domain model is relational, but the runtime database is intentionally not locked to Supabase.

Acceptable implementations include:

- Instatic's own self-hosted database/storage stack;
- SQLite for a compact self-hosted Instatic deployment when the active corpus and concurrency make it appropriate;
- PostgreSQL attached directly to the self-hosted Instatic/Railway deployment when scale, querying or operational requirements justify it;
- an owned local/server database or generated static data layer consumed by Astro.

The current SQL migrations remain a canonical relational reference and validation target. They must not force the public product to adopt a separate managed database service when the selected Astro/Instatic architecture does not need one.

## Recommended product architecture

### Option A — Instatic-first

Use Instatic as the operational CMS and publishing layer when its collections, visual editor, media library and static publishing can represent the required institution/profile model cleanly.

```text
external sources
→ acquisition/evidence artifacts
→ normalization + reconciliation
→ reviewed canonical data
→ Instatic import/collections + owned media
→ published website
```

This is the preferred low-complexity route if the existing Instatic deployment proves capable of the registry, bilingual content and structured profile requirements.

### Option B — Astro-first

Use Astro when the directory/search/filtering/SEO architecture needs more control than Instatic provides.

```text
external sources
→ acquisition/evidence artifacts
→ normalization + reconciliation
→ reviewed canonical data/static export
→ Astro build/server routes
→ published website
```

In this model, use build-time/static data wherever possible and add a server database only when measured product needs require it.

### Hybrid use

Do not create a hybrid Astro + Instatic architecture by default. Use both only if Instatic clearly improves editorial operations while Astro is demonstrably needed for the public directory/search experience. If both are used, one canonical data owner must be defined so content is not duplicated or allowed to drift.

## Repository architecture

For an Astro implementation, prefer:

```text
apps/
  web/       Astro public platform

packages/
  domain/
  data/
  seo/
  research/
  ui/
  config/

tools/
  data-acquisition/
```

If Instatic is selected, keep acquisition/reconciliation tooling in this repository and add a narrow export/import adapter rather than duplicating the research system inside the CMS.

Do not create a generic multi-vertical product framework yet.

## Rendering policy

Default principle:

> Keep static content static; add runtime only where the experience earns it.

For Astro:

### Prerender/static where suitable

- homepage
- stable marketing/legal pages
- editorial content
- institution profiles whose data changes infrequently
- selected major directory/topic hubs

### Server/on-demand + caching only where justified

- high-volume browse/search
- complex faceted filtering
- comparison
- authenticated admin functions if Astro eventually owns them

### Client islands only where justified

- filtering
- autocomplete
- maps
- comparison
- future account-specific interaction

Do not add React/Svelte/Vue islands by default.

For Instatic, prefer its native static publishing and media pipeline. Do not add a separate frontend framework solely to reproduce what Instatic already publishes well.

## Data ownership

Edu Hub owns a persistent copy of the data required to operate the product.

The enforced logical path remains:

```text
external source
→ raw evidence
→ staging/reconciliation
→ reviewed canonical data
→ publication projection
→ Astro or Instatic
```

Public pages must never depend on a live third-party directory/API after acquisition.

The current `edu_raw`, `edu_staging`, and `edu_core` SQL schemas describe this logical separation. Physical implementation may be adapted for Instatic/SQLite/static artifacts as long as the evidence, review and publication boundaries remain intact.

## Media

- store owned copies only when rights permit possession/reuse;
- preserve source URL, creator, license and attribution metadata;
- institution-site/social images may be discovery candidates but are not public-use assets by default;
- publication-safe media should be stored in the selected self-hosted runtime/media layer;
- if no safe photo exists, use the institution's English name on the designed placeholder.

## Security

- never expose admin/database credentials to public browser code;
- admin/research operations require authenticated access in the selected platform;
- public reads expose only reviewed publication data;
- future institution users submit reviewed change requests rather than unrestricted canonical edits;
- perform security review before public user data, uploads, claims, payments or lead/application workflows.

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

Start as simply as the selected runtime allows.

For the current international-only corpus, prefer static/generated indexes or lightweight local queries before adding a dedicated search service. Add a more complex search engine only after measured corpus/query requirements justify it.

## Performance

Performance is continuous, not a launch-only task.

Track:

- server/build response behavior
- client JavaScript/island cost
- image/media delivery
- fonts
- third-party scripts
- layout stability
- interaction responsiveness
- directory/search query behavior
- mobile runtime

## QA

Minimum implementation checks where configured:

```text
lint
→ typecheck
→ tests
→ production build/publish
→ browser QA
→ responsive/RTL QA
→ console/network review
```

## Environment handling

Provide `.env.example` with non-secret variable names only when the selected runtime needs environment variables.

Never commit actual credentials/secrets.

## Current platform decision still to resolve

The remaining choice is **Astro-first vs Instatic-first**, based on the real directory/CMS requirements and the capabilities of the existing self-hosted Instatic instance.

Supabase is not a candidate for Edu Hub.
