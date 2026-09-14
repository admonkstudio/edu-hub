# Edu Hub Database Completion Plan

Status: **ACTIVE / PRIMARY PROJECT GATE**

Scope: Egypt international education registry, bilingual English + Arabic.

## Objective

Complete the **data universe, canonical architecture, bilingual content model, provenance, identity reconciliation, enrichment and media references** before making any final decision about how the product is displayed.

Astro vs Instatic is intentionally deferred until the database is complete enough to expose the real presentation requirements.

The active work sequence is therefore:

```text
source discovery
→ source acquisition
→ raw evidence
→ identity reconciliation
→ canonical institution/campus model
→ bilingual EN/AR localization
→ profile enrichment
→ media references + rights
→ completeness audit
→ portable export
→ presentation/runtime decision later
```

## Completion principle

Database completion does **not** mean every possible field must have a value. It means:

1. the target institution universe has been systematically discovered;
2. every candidate is classified as `eligible`, `excluded`, `needs_review`, or unresolved with a known reason;
3. eligible institutions have one canonical identity and correct campus relationships;
4. every stored factual value has provenance or an explicit editorial/derived origin;
5. English and Arabic are modeled as first-class representations of the same facts;
6. important missing fields are explicit rather than silently omitted or invented;
7. media candidates and publication rights are tracked separately;
8. the dataset can be exported without depending on Astro, Instatic, Supabase or another presentation platform.

## Canonical database architecture

### 1. Source and evidence layer

Every source record retains:

- `source_id`
- publisher/source name
- source authority class
- source URL
- source record ID where available
- retrieval/snapshot date
- raw payload or source-shaped record
- content hash
- source language
- acquisition method
- terms/rights notes when relevant

Primary sources, regulators, accreditors, official institution sources and supporting/commercial directories remain distinguishable.

### 2. Canonical identity layer

Primary entities:

- provider/group
- institution
- campus/branch
- academic unit
- programme

Institution and campus are always separate concepts. One school group may have multiple institutions; one institution may have multiple campuses.

### 3. International eligibility layer

Each institution/campus carries:

- scope state: `candidate`, `eligible`, `excluded`, `needs_review`
- scope class
- eligibility evidence
- evidence authority
- review state
- review note
- valid-from / valid-to where relevant

No name or commercial directory entry can establish eligibility by itself.

### 4. Bilingual localization layer

Language-neutral facts are stored once. Localized text is stored separately.

For every localizable entity support:

- `locale`: `en-EG` or `ar-EG`
- display name
- short name
- alternate names
- description / profile copy
- address display text when a localized official form exists
- SEO/title text later, outside the canonical factual core
- localization source/origin
- localization status

Localization status should distinguish at least:

- `official_source`
- `institution_source`
- `verified_translation`
- `editorial_translation`
- `transliteration`
- `needs_review`

Arabic names must not be fabricated through casual translation. Prefer official Arabic naming. Where no official Arabic form exists, store a clearly marked transliteration/editorial form rather than pretending it is official.

### 5. Geography and campuses

Store:

- country
- governorate
- city
- district/area
- street/address
- latitude/longitude
- map/geospatial source
- campus type
- campus lifecycle status

Coordinates and map facts may be supported by Overture/OSM but must remain source-attributed.

### 6. Education model

For schools:

- curricula
- certificates/qualifications
- education levels
- grades/years
- age ranges
- languages of instruction
- gender model
- day/boarding model
- special educational programmes where relevant

For higher education:

- faculties/schools/academic units
- programmes
- degree levels
- awarding institution
- parent foreign university where relevant
- regulatory/accreditation status

### 7. Accreditation and authorization

Track separately:

- accreditation/authorization body
- programme or institution scope
- identifier where available
- status
- issue/recognition date
- expiry/review date where available
- evidence source

IB authorization, French homologation, German recognition, Cognia/MSCHE and Egyptian regulator recognition are not flattened into a single boolean.

### 8. Contacts and digital presence

Store normalized and source-backed:

- official website
- admissions URL
- application URL
- phone(s)
- email(s)
- social profiles
- contact purpose
- campus association
- verification/source date

### 9. Admissions and fees

These are time-sensitive and must be versioned.

Store:

- academic year
- admissions cycle
- application dates/deadlines
- requirements
- application fee
- tuition/annual fees
- registration/enrolment fees
- transport/other fees where sourced
- currency
- fee basis/unit
- source document/page
- effective date

Never overwrite an old fee schedule with a new one.

### 10. Facilities and profile attributes

Facilities and amenities should use a controlled taxonomy where practical, with source evidence. Examples:

- laboratories
- library
- sports facilities
- swimming pool
- theatre/auditorium
- transport
- cafeteria
- clinic
- boarding
- SEN/support services

Commercial-directory claims remain supporting evidence until corroborated when the fact is important.

### 11. Media reference architecture

For every media candidate store:

- related institution/campus
- source page
- original asset URL/reference
- media type
- role: logo / cover / campus / facility / gallery / other
- creator
- license
- license URL
- attribution text
- rights basis
- identity-match state
- `public_use_allowed`
- local/owned storage reference when legally acquired
- content hash where file is held
- EN caption/alt
- AR caption/alt

Media identity and media rights are separate gates.

### 12. Provenance and field assertions

Important facts must preserve their evidence instead of being silently overwritten.

For a canonical field retain:

- value
- source/evidence record
- authority class
- confidence/review state
- valid-from / valid-to
- selected-canonical state
- conflict state

Conflicts remain explicit review work.

## Source universe for completion

### Tier A — eligibility / regulatory / accreditation

- IB
- French Ministry homologation
- German KMK/ZfA
- SCU
- MOHESR
- Cognia
- MSCHE and equivalent recognized accreditors
- other foreign-government/authorizer sources where relevant

### Tier B — institution-primary enrichment

- official institution websites
- official admissions pages
- official fee PDFs/pages
- official curriculum/programme pages
- official campus/contact pages
- official institution media/press pages as media references

### Tier C — discovery/supporting enrichment

- British Council Partner Schools
- Edarabia
- Overture Maps
- OpenStreetMap/Wikidata
- historical V7 archive
- other commercial directories only when their terms permit the intended use

Tier C can discover or suggest fields but cannot independently establish high-risk eligibility/accreditation facts.

## Work packages

### D2.1 — Candidate universe completion

- collect all likely international schools/universities in Egypt from the source universe;
- compare source lists;
- identify missing candidates;
- create explicit discovery coverage report;
- stop only when new-source searches produce diminishing unique identities and all major curriculum/accreditation families have been covered.

### D2.2 — Identity + campus reconciliation

- normalize EN/AR names;
- deduplicate cross-source records;
- separate institution vs campus;
- resolve provider/group relationships;
- preserve aliases;
- create review queue for ambiguous matches;
- prohibit silent auto-merges.

### D2.3 — Bilingual canonical architecture

- establish official English and Arabic names where available;
- create Arabic display/transliteration only with explicit status when no official form exists;
- localize descriptions and parent/student-facing explanatory text separately from factual fields;
- validate Arabic search-normalization fields without altering canonical Arabic display strings.

### D2.4 — Profile enrichment

For every eligible institution systematically attempt:

- address + coordinates
- website/contact
- curricula/certificates
- grades/ages
- languages
- admissions
- fees
- facilities
- accreditation
- programmes for higher education
- founding/history facts where useful

Every attempted-but-missing field remains a measurable completeness gap.

### D2.5 — Media completion

- discover logos, campus images and useful facilities media;
- identify publication-safe open/permission-based media;
- preserve non-publishable media only as references where permitted;
- produce per-institution media coverage status;
- use placeholder requirement where no safe media exists.

### D2.6 — Completeness and conflict audit

Produce metrics by institution and field:

- identity complete
- EN name complete
- AR name complete
- location complete
- coordinates complete
- contact complete
- curriculum complete
- accreditation complete
- admissions complete
- fees current
- facilities coverage
- programme coverage
- media candidate present
- publication-safe media present
- unresolved conflicts
- last review date

### D2.7 — Portable database/export freeze

Before choosing Astro or Instatic, generate a presentation-neutral package containing:

- canonical entities
- localized EN/AR content
- source/evidence references
- admissions/fees history
- curricula/accreditation relationships
- media manifest
- rights metadata
- completeness report
- conflict/review report
- stable IDs and slugs/aliases where appropriate

The package must be exportable to JSON/JSONL/CSV plus a relational representation. No presentation framework is allowed to become the only holder of the data.

## Definition of database complete

The database phase is complete when all of the following are true:

- the candidate universe has been systematically covered across the approved source families;
- every candidate has an explicit scope decision or documented unresolved reason;
- eligible entities have reviewed canonical institution/campus identities;
- cross-source duplicates are reconciled or queued explicitly;
- every eligible institution has EN and AR naming coverage, with localization origin/status recorded;
- every core factual field has provenance;
- fees/admissions are versioned by year/cycle;
- higher-education programme/parent relationships are represented correctly;
- every institution has a media status, even when the result is `placeholder_required`;
- conflicts and stale facts are explicit;
- completeness can be measured independently for facts, English localization, Arabic localization and media;
- a deterministic portable export can be generated without Astro/Instatic;
- no public rendering decision is required to understand or operate the dataset.

## Deferred until after database completion

Do **not** spend current milestone time on:

- final Astro vs Instatic choice;
- card/page UI design;
- filtering UX;
- profile templates;
- visual design system;
- public SEO page generation;
- final CMS collection mapping;
- frontend deployment.

Those decisions will be made from the completed data architecture instead of forcing the database to fit a premature UI.
