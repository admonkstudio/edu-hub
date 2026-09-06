# Edu Hub Data Ownership & Runtime Contract

Status: **locked project principle**

## Core requirement

Edu Hub must be the operational holder of the records and media it renders.

The public website must **not** depend on live third-party education directories, government search pages, scraping endpoints, or source APIs at request/render time.

Source systems are acquisition/evidence inputs only.

```text
PUBLIC / OFFICIAL SOURCES
        ↓ acquisition
OWNED RAW ARCHIVE
        ↓ matching + review
OWNED CANONICAL DATABASE
        ↓ projection
OWNED PUBLIC READ MODEL
        ↓
WEBSITE / INSTATIC
```

If an external source disappears, becomes slow, blocks traffic, changes markup, or removes a record, the Edu Hub website must continue rendering from our stored copy until our own freshness/review rules decide otherwise.

## What “owned” means operationally

For every acquired text/data record, Edu Hub stores:

- source identity
- source record ID when available
- source URL
- retrieval timestamp
- content hash
- complete source payload / raw fields
- promoted convenience fields only where useful for research

For every acquired media candidate, Edu Hub stores:

- source record relationship
- source page URL
- original media URL
- image bytes in Edu Hub-controlled storage when acquisition is permitted
- content hash
- storage key
- MIME type
- byte size
- width / height
- acquisition timestamp
- raw alt/title/role hints
- rights / publication status

The original URL remains **provenance**, not the runtime asset URL.

## Runtime rule

Production rendering must read only from Edu Hub-controlled storage:

1. canonical/public data from our database;
2. media from our own media storage/domain;
3. no hotlinking source images;
4. no live third-party directory calls;
5. no source API needed for normal page rendering.

Third-party services may still be used as infrastructure providers, but the data itself must be stored under an Admonk/Edu Hub-controlled account and must be exportable without loss.

## Raw archive vs production database

Raw acquisition and the final production schema are intentionally separate concerns.

### Raw archive

The raw archive is source-shaped and immutable-by-default. It answers: “What did the source actually contain?”

Current source-neutral tables:

- `sources`
- `acquisition_runs`
- `raw_records`
- `field_inventory`
- `coverage_targets`
- `media_assets`
- `media_files`

The raw record payload remains intact even after later canonical mapping.

### Canonical / public database

The canonical schema is **not locked yet**. It will be designed only after acquisition, field census, media census, and identity matching expose the real data universe.

This avoids designing the production schema around a small early sample.

## Media ownership vs copyright

Operational possession of a mirrored file is not the same thing as having publication rights.

Therefore media has two independent states:

```text
mirrored / archived
        ≠
cleared for public publication
```

Default for discovered media:

- `rights_status = unknown`
- `public_use_allowed = false`

The raw archive may retain a research copy where permitted, while the public projection must only expose media that has passed the rights/publication gate.

## Performance contract

The future public read model must be designed for direct fast rendering:

- no cross-source joins at request time;
- no source scraping at request time;
- no live enrichment at request time;
- denormalized read projection where useful;
- indexed slug/type/location/filter fields;
- image derivatives generated ahead of time;
- stable local media URLs;
- caching/CDN may accelerate delivery, but the source of truth remains our stored data.

## Backup / portability contract

The raw archive and canonical database must be exportable.

Required backups:

- database dump / SQLite snapshot
- raw JSONL/CSV source snapshots when available
- media manifest
- media binary archive
- SHA-256 checksums
- source registry and acquisition reports

No vendor should be the only holder of the data.

## Immediate acquisition rule

During DA1 / DA1-M, every crawler should attempt to preserve:

- complete raw source payloads;
- source identifiers and URLs;
- all useful institution media references;
- mirrored image files into Edu Hub-controlled storage where permitted;
- media hashes and metadata;
- source-specific fields without forcing them into the final schema.

This contract remains in force when Edu Hub expands beyond Egypt or when the Vertical Engine is reused for other Admonk industry sites.
