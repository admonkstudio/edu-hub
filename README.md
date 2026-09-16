# Edu Hub

Edu Hub is an Admonk-owned bilingual education platform for Egypt.

## Current project scope

This repository is intentionally limited to three things:

1. the **Astro public-site foundation and deployment**;
2. the **Instatic CMS deployment/integration**;
3. **English/Arabic bilingual support**.

The previous database-research project is no longer part of the repository. Do not rebuild, scrape, deduplicate, enrich, migrate, or maintain institution data here.

The final institution/content tables will be supplied by the project owner when they are ready. Until then, the application must remain data-neutral.

## Languages

- English (Egypt): `en-EG` at `/en-eg/`
- Arabic (Egypt): `ar-EG` at `/ar-eg/`

Arabic pages use RTL layout. English pages use LTR layout. Language alternatives and canonical URLs are handled in the Astro layout.

## Deployment

- Astro is the public frontend foundation.
- Instatic CMS is maintained as a separate CMS service and will receive the final approved tables later.
- No Supabase dependency.
- No local SQL schema.
- No data-acquisition workflows.

See `docs/DEPLOYMENT.md` and `docs/BILINGUAL.md`.