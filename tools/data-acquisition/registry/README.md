# EDU-DATA-1 Registry Workspace

This folder contains the machine-readable acquisition contract and validation utilities for the Egypt National Education Registry.

## Layers

- `edu_raw` — source-shaped evidence, duplicates preserved.
- `edu_staging` — normalized candidates, match proposals, conflicts and review.
- `edu_core` — canonical Edu Hub identities and provenance-backed field assertions.
- `public` — later read-optimized projection; deliberately not created in EDU-DATA-1 yet.

## Source contract

`source_registry.json` is the versioned source/coverage contract. It distinguishes official row-level registries, official aggregate coverage sources, accreditation sources and secondary discovery/geospatial sources.

Validate it before any acquisition run:

```bash
python tools/data-acquisition/registry/validate_registry.py
```

The validator intentionally refuses to let a secondary source define an official national coverage target.

## First acquisition sequence

1. Refresh accessible SCU/higher-education official registries.
2. Reuse/refresh the successful Al-Azhar official institute acquisition.
3. Reconcile MOHESR private/technical lists in staging rather than concatenating counts.
4. Acquire MOE/EMIS from a network environment where the official directory is reachable, or obtain an official export.
5. Obtain MOSS nursery rows through an official export/data-sharing route or the announced public nursery map when released.
6. Only then begin broad profile enrichment.

## Important

A missing fee, photo, email or website does not invalidate an institution identity. Profile completeness is evaluated separately from identity validity.

AI may be used later to structure source evidence, but it may never create a fact that does not exist in source evidence.