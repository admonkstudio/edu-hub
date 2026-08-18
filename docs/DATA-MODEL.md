# Edu Hub Data Model

This document defines the approved conceptual data model for Milestone 1. Exact SQL can evolve during implementation only when the reason is recorded in `PROJECT-DECISIONS.md`.

## Core principles

- PostgreSQL is the operational source of truth.
- Important searchable concepts use explicit relational structures, not free-text tags.
- Canonical facts and source/evidence records are separate concerns.
- Historical values such as fees/admission cycles should be versioned rather than overwritten where practical.
- Payment/plan state is separate from factual verification.
- Entity lifecycle/publication state is separate from SEO indexability.

## Identity

### `providers`

Represents a group/organization behind one or more institutions.

Suggested fields:

- `id uuid primary key`
- `provider_type`
- `official_name`
- `website_url`
- `status`
- timestamps

### `provider_localizations`

- `provider_id`
- `locale`
- `name`
- `description`
- `slug`

### `institutions`

Canonical institution identity.

Suggested fields:

- `id uuid primary key`
- `provider_id nullable`
- `institution_type_id`
- `ownership_type_id nullable`
- `education_model_id nullable`
- `official_name`
- `official_website_url`
- `founded_year nullable`
- `publication_status`
- `data_status`
- `claim_status`
- `commercial_status`
- `merged_into_id nullable`
- timestamps

### `institution_localizations`

- `institution_id`
- `locale`
- `name`
- `short_name`
- `alternate_names`
- `summary`
- `description`
- `slug`
- `seo_title`
- `seo_description`

Initial locales: `ar-EG`, `en-EG`.

## Campuses

### `campuses`

- `id`
- `institution_id`
- `location_id`
- `name`
- `is_main`
- address fields
- PostGIS point/geography coordinates
- contact convenience fields only where justified
- `status`
- timestamps

Create a GiST index for geographic coordinates.

## Geography

### `locations`

Recursive hierarchy:

- `id`
- `parent_id nullable`
- `country_code`
- `location_type`
- `official_code nullable`
- `name_en`
- `name_ar`
- `slug_en`
- `slug_ar`
- coordinates nullable
- `status`

Initial location types:

- country
- governorate
- city
- district
- area
- neighborhood

Seed Egypt and all 27 governorates during Milestone 1.

## Controlled taxonomies

Initial tables:

- `institution_types`
- `ownership_types`
- `education_models`
- `education_levels`
- `curricula`
- `certificates`
- `languages`
- `accreditation_bodies`
- `facilities`

Common fields should generally include:

- `id`
- stable `code`
- Arabic and English labels
- Arabic and English slugs where public routing may need them
- `status`
- `sort_order`

## Education relationships

Relationship tables may include:

- `institution_education_levels`
- `institution_curricula`
- `institution_certificates`
- `institution_languages`
- `institution_accreditations`
- `campus_facilities`

Where historical validity matters, support `valid_from`, `valid_to`, and source/evidence references.

## Higher education

### `academic_units`

Recursive academic hierarchy:

- faculty
- college
- school
- institute
- department
- center

Fields:

- `id`
- `institution_id`
- `parent_id nullable`
- `unit_type`
- `official_name`
- `status`
- timestamps

### `academic_unit_localizations`

Localized name/description/slug.

### `programs`

Suggested fields:

- `id`
- `institution_id`
- `academic_unit_id nullable`
- `campus_id nullable`
- `program_type_id`
- `subject_area_id`
- `degree_level_id`
- duration fields
- `study_mode`
- `credit_system nullable`
- `application_url nullable`
- `status`
- timestamps

### `program_localizations`

Localized name, summary, description, admissions notes, slug.

## Fees

### `fee_schedules`

Version by academic year.

- `id`
- `institution_id`
- `campus_id nullable`
- `academic_year`
- `currency_code`
- `valid_from nullable`
- `valid_to nullable`
- `source_id nullable`
- `verification_status`
- timestamps

### `fee_items`

- `fee_schedule_id`
- `education_level_id nullable`
- `program_id nullable`
- `fee_type_id`
- amount exact/min/max
- `frequency`
- `mandatory`
- `notes`

Do not overwrite old academic-year schedules.

## Admissions

### `admission_cycles`

- institution/campus
- academic year
- open/close dates
- application status
- application URL
- optional age limits
- source
- verification timestamp

### `admission_requirements`

Requirement type, localized description, mandatory flag, sort order.

## Contacts

Prefer one `entity_contacts` model over many arbitrary social columns.

Contact types may include phone, mobile, email, website, admissions URL, Facebook, Instagram, LinkedIn, YouTube, TikTok and WhatsApp.

Track whether the contact is primary/official and its source where appropriate.

## Sources and evidence

### `sources`

Suggested fields:

- `id`
- `source_type`
- `publisher`
- `title`
- `url`
- `language`
- `authority_level`
- `published_at nullable`
- `retrieved_at`
- `status`
- timestamps

Source priority starts with government/regulator and official institution sources.

### `source_snapshots`

Optional metadata/extract snapshots where legally and operationally justified.

### `entity_assertions`

Preserve sourced candidate facts independently from canonical values.

Suggested fields:

- entity type/id
- `field_key`
- `value_jsonb`
- source/snapshot
- confidence
- assertion status
- observed/valid dates
- creator/timestamps

Conflicting assertions must be reviewable instead of silently overwriting canonical data.

## Research and freshness — Milestone 2 target

The following are defined now but should not be implemented in Milestone 1 unless an explicit dependency requires a minimal stub:

- `research_tasks`
- `freshness_policies`
- `field_freshness`
- `import_batches`
- `import_records`
- `import_matches`
- `change_sets`
- `entity_revisions`
- future `change_requests`

## Status values

Prefer text columns with CHECK constraints/application constants when that preserves migration flexibility.

### Data status

- candidate
- researching
- sourced
- reviewed
- officially_sourced
- institution_confirmed
- conflicting
- stale
- disputed

### Publication status

- draft
- public_noindex
- index_ready
- published
- archived
- redirected

### Claim status

- unclaimed
- claim_requested
- verification_pending
- claimed
- suspended

### Commercial status

- free
- premium
- sponsored
- partner

Phase 1 uses free only; other values are future-ready concepts, not implemented features.

## Indexes

Milestone 1 should add appropriate indexes for:

- foreign keys
- locale + slug uniqueness
- publication/data statuses used in queries
- institution type
- locations
- common relationship-table lookups
- PostGIS coordinates

Do not add speculative indexes without a query need, but do not leave obvious FK/filter paths unindexed.

## Representative data validation

After Milestone 1, validate the schema against approximately 20–30 deliberately varied Egyptian institutions, including multi-campus/group cases and multiple higher-education structures, before bulk ingestion begins.
