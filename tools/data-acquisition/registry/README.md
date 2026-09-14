# EDU-DATA-1 Registry Workspace

This folder contains the machine-readable acquisition contract, staging-seed builder and validation utilities for the Egypt National Education Registry.

The national goal is **100,000+ canonical educational entities**. The current MOE school universe (62,690) plus the MOSS nursery census (48,225) already defines 110,915 official target rows before Al-Azhar and higher education are added. Coverage targets are never treated as acquired rows or canonical entities.

## Layers

- `edu_raw` — source-shaped evidence, duplicates preserved.
- `edu_staging` — normalized candidates, match proposals, conflicts and review.
- `edu_core` — canonical Edu Hub identities and provenance-backed field assertions.
- `public` — later read-optimized projection; deliberately not created in EDU-DATA-1 yet.

## Source contract

`source_registry.json` is the versioned source/coverage contract. It distinguishes official row-level registries, official aggregate coverage sources, accreditation sources and secondary discovery/geospatial sources.

`source_aliases.json` maps historical raw-source identifiers into that registry contract. Its `coverage_credit` field is intentionally strict:

- `current` — may contribute row-level evidence toward the current official source target.
- `historical` — retained as evidence but must not satisfy current national coverage.
- `none` — enrichment/discovery only; never official coverage.

Validate the source contract before any acquisition run:

```bash
python tools/data-acquisition/registry/validate_registry.py
```

The validator intentionally refuses to let a secondary source define an official national coverage target.

## Recover an owned archive into staging candidates

The staging builder reads an owned raw SQLite archive in immutable/read-only mode and writes deterministic review candidates plus coverage reports. It does **not** write to `edu_core`, accept identity matches, or publish data.

```bash
python tools/data-acquisition/registry/build_staging_seed.py \
  --sqlite /path/to/edu_hub_egypt_raw.sqlite \
  --out-dir artifacts/edu-data-1/registry-seed
```

Outputs:

- `staging_candidates.jsonl` — one normalized candidate per raw record; still evidence, not a canonical institution.
- `coverage_report.json` — official targets versus current/historical source rows plus safety flags.
- `coverage_report.csv` — source-level coverage table.

The verified `edu-hub-egypt-base-v3` seed currently produces 13,192 staging candidates. Only 8,001 rows are credited as current official seed evidence before identity resolution: 7,674 Al-Azhar rows and 327 SCU rows. The 13 legacy EMIS rows are historical evidence only and do not reduce the current 62,690-school acquisition gap.

The checksum/source-count evidence for that recovery point is stored in `../recovery/verified_base_v3_seed_manifest.json`. It is deliberately labeled a verified base-v3 seed, **not** the exact historical V7 archive.

Run staging safety tests with:

```bash
python tools/data-acquisition/registry/test_build_staging_seed.py
```

## Plan canonical identities without writing to `edu_core`

`plan_core_seed.py` consumes staging candidates and creates deterministic **identity proposals only**. It currently supports the two recovered official identity sources whose source-specific keys are understood well enough to plan safely:

- Al-Azhar — official institute identifier is the proposal key. Two institutes with the same name but different official IDs remain separate.
- SCU — normalized institution type + normalized name forms a review proposal key. Repeated SCU rows under the same key are grouped for review, never accepted automatically.

```bash
python tools/data-acquisition/registry/plan_core_seed.py \
  --candidates artifacts/edu-data-1/registry-seed/staging_candidates.jsonl \
  --out-dir artifacts/edu-data-1/core-seed-plan
```

Outputs:

- `core_identity_proposals.jsonl` — deterministic proposed identities; not canonical rows.
- `identity_review_tasks.jsonl` — duplicate/ambiguous groups requiring review.
- `core_seed_plan_report.json` — proposal counts plus hard safety flags.

A verified planning pass against the checksum-pinned `edu-hub-egypt-base-v3` archive produced:

- 13,192 staging candidates seen;
- 8,001 current primary-source rows considered;
- 8,000 identity proposals: 7,674 Al-Azhar + 326 SCU;
- 7,999 singleton proposals;
- 1 ambiguous SCU proposal, grouping `SCU-LIVE-0033` and `SCU-LIVE-0052` for the two Arabic spellings of Alexandria National University;
- 0 automatic identity acceptances;
- 0 `edu_core` rows created;
- no public/live promotion.

This 8,000 figure is a **proposal count, not an accepted canonical institution count**. The one ambiguous SCU group remains an open identity review. MOHESR is intentionally excluded until cross-registry reconciliation rules are defined.

Run identity-planning safety tests with:

```bash
python tools/data-acquisition/registry/test_plan_core_seed.py
```

## First acquisition sequence

1. Preserve and stage the verified owned seed without automatic identity acceptance.
2. Produce review-only Al-Azhar/SCU identity proposals; do not promote them automatically.
3. Refresh accessible SCU/higher-education official registries.
4. Reuse/refresh the successful Al-Azhar official institute acquisition.
5. Reconcile MOHESR private/technical lists in staging rather than concatenating counts.
6. Acquire MOE/EMIS from a network environment where the official directory is reachable, or obtain an official export.
7. Obtain MOSS nursery rows through an official export/data-sharing route or the announced public nursery map when released.
8. Resolve canonical identities and hierarchy under review before any `edu_core` promotion.
9. Only then begin broad profile enrichment and later public projection.

## Non-negotiable safety rules

- A raw record is not a canonical institution.
- An identity proposal is not a canonical institution.
- An official aggregate count is not an acquired row set.
- Historical records do not masquerade as current official coverage.
- Secondary sources cannot satisfy official national coverage targets.
- Zero identity matches are accepted automatically in this recovery gate.
- No `edu_core` or live/public promotion occurs from the staging builder or identity planner.
- A missing fee, photo, email or website does not invalidate an institution identity; profile completeness is separate from identity validity.
- AI may structure source evidence, but it may never create a fact that does not exist in source evidence.
