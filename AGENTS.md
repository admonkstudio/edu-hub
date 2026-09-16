# Edu Hub Agent Instructions

## Current scope

Work only on:

- Astro frontend setup, maintenance, and deployment;
- Instatic CMS deployment and integration;
- English/Arabic bilingual behavior, routing, RTL/LTR, and bilingual SEO.

## Database boundary

The project owner will provide the final tables later.

Do not:

- scrape or collect institution data;
- create a database research plan;
- deduplicate, reconcile, enrich, or verify institution records;
- create SQL schemas or migrations for institution data;
- reintroduce Supabase;
- recreate historical EDU-DATA workflows or documents;
- archive the removed database work inside this repository.

When final tables are supplied, map them into the chosen runtime/CMS without changing their contents unless the owner explicitly asks.

## Bilingual requirements

- Support `en-EG` and `ar-EG`.
- English is LTR; Arabic is RTL.
- Preserve separate language URLs.
- Keep canonical and `hreflang` signals correct.
- Do not fabricate translations of user-supplied institution content.

## Deployment principle

Keep Astro and Instatic responsibilities simple and explicit. Avoid adding infrastructure until it is required for the supplied final tables.