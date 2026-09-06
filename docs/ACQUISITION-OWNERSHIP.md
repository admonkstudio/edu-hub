# Acquisition ownership and media storage

Last updated: 2026-09-06

## Purpose

Edu Hub must hold its acquisition records and media in infrastructure it controls. External APIs, websites, directories and crawlers are ingestion mechanisms and provenance sources; they are not the runtime database or permanent image delivery layer.

## Acquisition flow

```text
external source
→ raw source record
→ Edu Hub-owned database
→ discovered media reference
→ rights classification
→ Edu Hub-owned binary storage
→ later canonical review and public projection
```

## Current checkpoint

The V5 acquisition checkpoint extends the V4 SQLite research corpus without changing its 13,452 existing raw records.

It adds:

- an ownership ledger and SHA-256 verification for every raw payload
- media discovery records linked to raw source records
- content-addressed binary storage using SHA-256 keys
- one stored binary for identical images discovered through multiple URLs
- download-attempt history and failure status
- source, attribution, copyright and license metadata
- private-by-default public reuse controls
- per-source media coverage reporting

SQLite is the portable acquisition checkpoint format. PostgreSQL/Supabase remains the approved operational source of truth for the production platform.

## Rights boundary

Storing an internally acquired image does not grant publication rights.

`public_reuse_allowed` remains false unless an open license, explicit permission or institution-supplied right is recorded. Unknown or restricted media may be retained for internal research and provenance but must not enter the public projection.

## Frozen boundaries

Until the acquisition corpus and audits are complete, this layer must not:

- merge cross-source institution identities
- choose canonical facts
- import bulk records into Instatic or the public application
- make every database record indexable
- publish unsupported or rights-unknown images

## Crawler integration contract

Every source adapter should emit:

1. the complete raw payload and source identity
2. zero or more media discoveries with original URL and source page
3. a media type where detectable
4. rights metadata where explicitly available
5. download status and locally owned storage key after acquisition

The MadaresEgypt adapter is the next integration target. Its live crawler source must be restored or connected before that adapter can be modified.
