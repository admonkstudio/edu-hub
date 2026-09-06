# Edu Hub Data Ownership Architecture

Status: **locked project principle** for acquisition, media and public rendering.

## Core principle

Edu Hub must be the **holder/controller of its own acquired record copy**. The public website must not depend on third-party education directories or government APIs at request/render time.

External sources are used only for:

1. acquisition;
2. refresh/research;
3. provenance and verification.

They are **not** the runtime datastore.

> Source -> acquire -> preserve locally -> review/normalize -> publish from Edu Hub-owned storage.

## What “owned” means here

For database records, Edu Hub keeps its own persistent copy of the public facts and raw source payloads under Admonk-controlled infrastructure.

For media, Edu Hub keeps its own persistent binary copy whenever acquisition is permitted and records the source/rights state. Holding a copy does **not** automatically transfer copyright or grant public redistribution rights. Rights and publication eligibility remain separate fields.

This distinction lets Edu Hub be operationally independent without pretending that third-party intellectual-property rights disappeared during acquisition.

## Runtime rule

The production rendering path is:

```text
Browser
  -> Edu Hub application / Instatic
  -> Edu Hub public projection database
  -> Edu Hub-controlled media storage/CDN
```

It is never:

```text
Browser
  -> third-party school API
  -> third-party directory API
  -> third-party image host
```

Third-party downtime therefore cannot make an already-published Edu Hub institution profile disappear.

## Storage layers

### 1. Raw records

Persistent source-level facts:

- source identity
- source record ID
- source URL
- retrieval timestamp
- raw hash
- original structured payload
- promoted convenience fields

Cross-source duplicates are deliberately preserved.

### 2. Raw media registry

Every discovered media candidate receives a row containing:

- source ID
- source record ID
- source page URL
- original media URL
- raw media role / alt / title
- discovery timestamp
- rights status
- public-use flag
- mirror/acquisition status

### 3. Owned media files

When a public media candidate is mirrored, the binary is stored under an Admonk-controlled storage key and addressed by SHA-256.

Required metadata:

- SHA-256
- storage key
- MIME type
- byte size
- pixel width/height when detectable
- acquired timestamp

The public site later serves only the Admonk-controlled copy, never the source URL.

### 4. Canonical database

Created only after field census and identity matching. It contains Edu Hub’s chosen institution/campus/program/contact/taxonomy model.

### 5. Public projection

A compact, read-optimized layer for Instatic/site rendering. The projection contains only fields needed by public pages, search, filters, maps and SEO.

## Media rights states

Raw acquisition uses an explicit rights state:

- `unknown`
- `open_license`
- `institution_permission`
- `admonk_owned`
- `government_reuse_confirmed`
- `restricted`
- `do_not_publish`

`public_use_allowed` defaults to **false** until a defensible reuse basis exists.

The acquisition pipeline may preserve a candidate and its metadata without automatically publishing it.

## Performance principle

Fast rendering comes from pre-owned/precomputed data:

- no third-party API calls during page render;
- no remote-source image hotlinking for published assets;
- indexed local/public database queries;
- image variants generated once and served through the project’s own CDN/storage layer;
- canonical/public projections separated from research payloads;
- source refresh jobs happen asynchronously.

## Portability principle

Database records and media storage keys must remain portable. The acquisition layer must not hard-code a single SaaS provider as the source of truth.

The eventual production implementation may use Postgres plus S3-compatible/object storage, Instatic media storage or another Admonk-controlled deployment, but exportability of both records and media is mandatory.

## Backup requirement

At production stage the following must be independently restorable:

- canonical database dump;
- raw acquisition database/archive;
- media bucket/files;
- media metadata/rights manifest;
- source/provenance manifests.

A provider account is not the backup.

## Acquisition exit rule

Before mass import, Edu Hub must be able to produce both:

1. a field-coverage report; and
2. a media-coverage report.

For each institution family we should know at minimum:

- records discovered;
- records with names;
- records with location;
- records with coordinates;
- records with media candidates;
- records with mirrored media;
- records with at least one public-eligible image;
- records with logo candidate;
- records with featured-image candidate.

## Locked consequence

No future product architecture should require a source API to render an institution already acquired by Edu Hub. APIs may improve acquisition/refresh speed, but they remain replaceable ingestion inputs rather than runtime dependencies.
