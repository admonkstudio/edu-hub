# Edu Hub Agent Rules

This repository contains an Admonk-owned product venture, not a client website.

Edu Hub is an independent brand. Admonk's reusable methods should improve the work, but Admonk's own visual identity, website copy, and company-specific decisions must not be applied to Edu Hub by default.

## 1. Authority order

Use this priority:

1. Current explicit user/project-owner instruction.
2. Edu Hub business/product strategy in this repository.
3. Approved Edu Hub brand and production design system.
4. Current project requirements and recorded decisions.
5. Reusable Admonk studio principles.
6. Relevant Admonk skills from `admonkstudio/admonk`.
7. Current official platform documentation.
8. Framework defaults and generic best practices.

If sources conflict materially, identify and record the decision rather than silently mixing them.

## 2. Lifecycle

Use the Admonk Project Lifecycle:

```text
00 Open
→ 01 Discover
→ 02 Align + Audit
→ 03 Define
→ 04 Content + Structure
→ 05 Creative Direction
→ 06 Design + Systemize
→ 07 Build + Connect
→ 08 Verify + Optimize
→ 09 Review + Launch
→ 10 Handoff + Learn
```

Read `docs/PROJECT-STATUS.md` before continuing substantial work.

Update `docs/PROJECT-STATUS.md` and `docs/PROJECT-DECISIONS.md` after material progress or architecture changes.

## 3. Reusable Admonk intelligence

The canonical reusable studio system remains in `admonkstudio/admonk`.

For relevant work, inspect the current canonical skill before implementation, especially:

- `.agents/skills/admonk-astro/SKILL.md`
- `.agents/skills/admonk-supabase/SKILL.md`
- `.agents/skills/admonk-seo/SKILL.md`
- `.agents/skills/admonk-localization/SKILL.md`
- `.agents/skills/admonk-performance/SKILL.md`
- `.agents/skills/admonk-security-review/SKILL.md`
- `.agents/skills/admonk-browser-qa/SKILL.md`
- `.agents/skills/admonk-ux-systems/SKILL.md`
- `.agents/skills/admonk-design-quality/SKILL.md`
- `.agents/skills/admonk-web-design/SKILL.md`

Do not duplicate the entire Admonk skill library into this repository.

## 4. Product principles

- Parents and students are the primary audience.
- Build a trustworthy information product before monetization.
- Official and primary sources take priority over secondary sources.
- Payment never determines factual verification.
- Structured facts should preserve source provenance where practical.
- Database scale does not equal SEO scale.
- A database record does not automatically deserve an indexable page.
- Curated useful landing pages are allowed; unrestricted faceted SEO generation is not.
- AI should accelerate research/editorial work, not autonomously publish unsupported facts.
- Arabic and English are first-class launch languages.
- Build Egypt well before generalizing globally.
- Build reusable architecture, but do not prematurely create a generic multi-vertical SaaS framework.

## 5. Phase boundaries

Phase 1 includes directory, editorial, research/admin, bilingual SEO architecture, source provenance, and the technical foundation required to scale them.

Do not implement Phase 2 commercial functions unless a later approved issue explicitly adds them. This includes subscriptions, premium listings, advertising marketplace, lead selling, institution dashboards, applications, consultant marketplace, and payment flows.

## 6. Astro

Use Astro because it fits the content-heavy, SEO-sensitive product.

Core rule:

> Keep static content static. Add runtime JavaScript only where the experience earns it.

Prefer `.astro` components and server-rendered HTML. Use client islands only for real interaction such as filters, map controls, comparison, autocomplete, or future account functionality.

Do not add React/Svelte/Vue merely by habit.

## 7. Database

PostgreSQL is the operational source of truth. Supabase is the approved initial platform direction.

- model institutions relationally
- preserve explicit taxonomies for important searchable concepts
- preserve provenance/evidence separately from canonical values
- use migrations
- design RLS deliberately for exposed data
- never expose service-role credentials in browser code
- do not weaken security policies to make development easier

## 8. SEO

SEO is a product requirement, not a final plugin.

Every public route must have an intentional indexability policy. Verify current search-engine guidance from primary sources before relying on version-sensitive behavior.

Important requirements include:

- stable descriptive URLs
- canonical policy
- `hreflang`
- robots/indexability rules
- database-driven segmented sitemaps
- structured data matching visible content
- internal linking
- crawl controls for filters/search
- redirects for changed/merged entities
- rendered HTML verification

## 9. Research and factual integrity

Never invent institution facts, fees, accreditations, admission dates, rankings, ratings, or claims.

When sources conflict, preserve the conflict and require review instead of silently choosing one.

Historical fee/admission records should be versioned where the data model supports it rather than overwritten.

Institution-submitted edits in future phases must go through a review/change-request boundary before becoming canonical data.

## 10. Localization

Arabic and English are independent editorial experiences tied to the same underlying factual entity.

Do not treat Arabic as an afterthought or merely machine-translated English. Test RTL layout, long text, navigation, forms, filters, metadata, structured data, and locale relationships.

## 11. Quality gates

For implementation work, verify at minimum:

```text
lint
→ typecheck
→ tests where configured
→ production build
→ rendered browser QA
→ responsive/RTL QA where relevant
→ console/network sanity
```

Performance, responsive behavior, accessibility, and SEO are continuous constraints.

## 12. Secrets

Never commit API keys, database passwords, tokens, service-role credentials, or private `.env` files.

## Final principle

> Build a useful, source-backed education reference first. Scale what proves valuable. Monetize trust without compromising it.
