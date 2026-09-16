# Deployment

## Astro

The repository contains a small Astro frontend with English and Arabic routes.

Environment variable:

- `PUBLIC_WEB_ORIGIN` — production public website origin used for canonical and language-alternative URLs.

The current Astro config uses the Vercel adapter. It can be changed later if the final hosting target changes.

## Instatic CMS

Instatic CMS remains a separate CMS service. The current public service endpoint previously used for the project is:

`https://admonk-instatic-cms.up.railway.app/`

Do not populate it from the removed database-research material. The project owner will provide final tables/content and then the CMS mapping/import can be designed from those approved files.

## Separation

Astro = public frontend.

Instatic CMS = content management/publishing service.

No Supabase or separate research database is part of the current scope.