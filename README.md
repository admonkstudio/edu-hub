# Edu Hub

Edu Hub is an independent, bilingual education discovery and knowledge platform owned by Admonk. Egypt is the initial market. The repository implements Milestones 0 and 1 plus the engineering and hosted-staging validation slices of Milestone 2. Milestone 2 remains in progress until the real 20–30 institution research cohort and workflow retrospective are complete. Public directory/profile functionality remains a later milestone.

## Architecture

- `apps/web` — static-first Astro public shell with `/en-eg/` and `/ar-eg/` route proofs
- `apps/control` — authenticated Astro staff application for bilingual institution CRUD, evidence review, conflict resolution, research tasks, freshness, and readiness
- `packages/config` — Egypt/locale constants, direction helpers, and environment validation
- `packages/domain` — foundation-only shell contracts
- `packages/database` — generated Supabase types, authenticated/server clients, and explicit institution repository functions
- `packages/seo` — tested canonical, locale-alternate, and path helpers
- `supabase` — migrations, RLS policies, Egypt/taxonomy seeds, pgTAP tests, and fictional representative fixtures
- `docs/RESEARCH-PROTOCOL.md` — binding source, conflict, review, localization, and readiness procedure for research work

The workspace uses pnpm without a separate monorepo orchestrator. The public app remains static-first; the control app uses Astro on-demand rendering and Supabase Auth/RLS.

## Requirements

- Node.js 22.12 or later
- pnpm 11.19.0
- Docker-compatible runtime only when running the local Supabase stack

## Setup

```bash
pnpm install --frozen-lockfile
cp .env.example .env
```

Keep `SUPABASE_SECRET_KEY` server-side. Actual `.env` files are ignored.

The control app requires `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY`. Create a Supabase Auth user, then insert the user's UUID into `public.staff_users` with an active role (`admin`, `researcher`, `editor`, `reviewer`, or `seo_manager`) before signing in. Never place the secret/service-role key in browser-accessible variables. Canonical writes and reviewed workflow transitions must use the audited command functions; direct authenticated table writes are intentionally revoked for protected records.

## Applications

```bash
pnpm dev:web       # http://localhost:4321
pnpm dev:control   # http://localhost:4322
```

## Quality gates

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build:web
pnpm build:control
pnpm test:browser
```

`pnpm build` builds both applications. CI runs all gates, installs Chromium, and runs the browser smoke suite.

## Supabase workflow

```bash
pnpm db:start
pnpm supabase migration new <descriptive-name>
pnpm db:reset
pnpm db:types
pnpm test:db
pnpm db:fixtures
pnpm db:stop
```

The local stack requires Docker. `db:reset` creates the canonical schema and deterministic seed data; `db:fixtures` adds 12 clearly fictional institutions for local validation only. Hosted staging uses the linked `edu-hub-staging` Supabase project in Frankfurt. Apply repository-owned migrations with `supabase db push --dry-run` followed by `supabase db push`; do not use production data or create a production project during Milestone 2.

## Deployment

Vercel hosts two staging projects from this monorepo: `edu-hub-web` rooted at `apps/web` and `edu-hub-control` rooted at `apps/control`. Their stable staging URLs are [edu-hub-web.vercel.app](https://edu-hub-web.vercel.app) and [edu-hub-control.vercel.app](https://edu-hub-control.vercel.app). Public and Control environment variables are scoped separately; no Supabase secret/service-role key is configured in Vercel.

Read [AGENTS.md](./AGENTS.md) and [docs/PROJECT-STATUS.md](./docs/PROJECT-STATUS.md) before substantial work.
