# Edu Hub Platform

## Approved direction

Edu Hub does **not** use Supabase.

The public presentation/runtime may eventually use:

1. **Astro + TypeScript**; or
2. **Instatic CMS**.

However, **the final platform choice is deferred until the database-completion gate is finished**.

The current milestone must therefore remain presentation-neutral. The data-acquisition, canonical model, bilingual localization, provenance and media layers must be complete and portable before the project decides how to render them.

## Current priority

The active stack is the **data/research system**, not the public website.

Current work focuses on:

- source acquisition;
- canonical identity reconciliation;
- English/Arabic localization architecture;
- profile enrichment;
- evidence/provenance;
- historical/versioned admissions and fees;
- media references and rights;
- completeness/conflict reporting;
- deterministic portable exports.

Do not spend the current milestone optimizing for CMS collections, Astro routes, UI components, filtering UX or page templates.

## Logical data architecture

The project retains:

```text
external source
→ raw evidence
→ staging/reconciliation
→ reviewed canonical data
→ bilingual localization
→ completeness/media audit
→ portable export
→ presentation platform later
```

The SQL migrations remain a canonical relational/reference model and validation target. They do **not** require Supabase or commit the project to a final production database technology.

## Presentation options after database completion

### Astro-first

Use Astro if the completed dataset shows a need for strong coded control over directory/search/filtering, programmatic SEO, comparison or custom profile experiences.

### Instatic-first

Use Instatic if the completed dataset maps cleanly to its collection/media/editorial model and the lower-complexity static publishing workflow is sufficient.

### Hybrid

Do not use Astro + Instatic together by default. A hybrid is permitted only after the database is complete and a clear division of responsibility is documented with one canonical data owner.

## Data ownership

Edu Hub owns/controls a persistent copy of the data required to operate the product.

Public rendering must never depend on live third-party directory/API calls after acquisition.

The physical storage implementation chosen later must preserve:

- raw source evidence;
- staging/reconciliation state;
- canonical identities;
- EN/AR localizations;
- source/field provenance;
- historical/versioned values;
- media rights/provenance;
- exportability and backup.

## Localization

Database locales:

- `en-EG`
- `ar-EG`

Language-neutral factual fields are stored once. Localized text is modeled separately.

Localization metadata should distinguish:

- official source;
- institution source;
- verified translation;
- editorial translation;
- transliteration;
- needs review.

Prefer official Arabic names. Transliteration/editorial Arabic must never be confused with an official sourced name.

## Media

The database must record media independently of the future public renderer.

Store/reference:

- source page/original media reference;
- related institution/campus;
- role;
- creator/license/attribution;
- rights basis;
- identity-match state;
- public-use flag;
- owned/local storage key and hash when acquisition is permitted;
- EN/AR caption/alt where relevant.

If no safe image exists, `placeholder_required` is a valid completed media state.

## Portability requirement

Before selecting Astro or Instatic, EDU-DATA-2 must be able to generate a deterministic presentation-neutral package containing:

- canonical institutions/campuses/providers;
- EN/AR localization;
- curricula/accreditations;
- geography/contacts;
- admissions/fees history;
- programmes/academic units;
- media manifest/rights;
- evidence/provenance;
- conflict/review state;
- completeness metrics.

No CMS or frontend framework may become the only holder of the database.

## Deferred platform decisions

Do not resolve these during the database-completion gate:

- Astro-first vs Instatic-first;
- final physical runtime database;
- final public collection/page architecture;
- search/filter implementation;
- hosting adapter;
- frontend deployment;
- visual component system.

The completed database will determine these requirements later.
