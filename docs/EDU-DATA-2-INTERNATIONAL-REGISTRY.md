# EDU-DATA-2 — Egypt International Education Registry

Status: **ACTIVE — DATABASE COMPLETION GATE**

Branch: `edu-data-2-international-registry`

Canonical completion plan: `docs/DATABASE-COMPLETION-PLAN.md`

## Product scope

Edu Hub focuses on **international education in Egypt** rather than attempting to represent the complete Egyptian public education system.

Phase 1 registry scope includes:

1. private/independent schools in Egypt delivering a recognized international curriculum or foreign national curriculum;
2. private/independent IB World Schools in Egypt;
3. recognized British, American, French, German, Canadian and other international-school models where the international status can be evidenced;
4. foreign university branch campuses recognized in Egypt;
5. internationally chartered/accredited independent higher-education institutions in Egypt when the international status is substantive, not merely a partnership claim;
6. campuses and early-years sections that belong to an eligible institution.

Explicitly excluded from the active Phase 1 registry:

- Egyptian public schools;
- Egyptian public universities;
- public international-school initiatives unless the project owner later re-adds them;
- ordinary language schools that merely offer some foreign examinations but lack evidence of an international-school model;
- Egyptian universities that only have foreign partnerships, dual degrees or exchange agreements;
- the national nursery universe;
- entities whose only evidence is a commercial directory listing.

Historical national-registry work is retained for provenance and future optional expansion, but it is no longer an active product dependency.

## Current execution priority

The active objective is **database completion and bilingual EN/AR architecture before presentation**.

Do not select or optimize for Astro vs Instatic during this gate. The finished database must be portable enough to feed either one later.

Current sequence:

`source discovery -> raw evidence -> identity reconciliation -> canonical institution/campus data -> EN/AR localization -> enrichment -> media/reference completion -> completeness audit -> portable export`

## International eligibility contract

An institution receives one of four scope states:

- `candidate` — discovered but international eligibility is not yet proven;
- `eligible` — sufficient evidence exists for inclusion;
- `excluded` — evidence proves it falls outside the current scope;
- `needs_review` — evidence is conflicting or incomplete.

### Strong eligibility evidence

Any of the following may independently establish international eligibility when the entity is private/independent and the evidence applies to the institution/campus being listed:

- active IB World School authorization;
- inclusion in an official French homologation list;
- inclusion in an official German/KMK recognized overseas-school list;
- recognized foreign-university branch status from SCU/MOHESR;
- current recognized international institutional accreditation plus an official institution source demonstrating the international model;
- another foreign-government, awarding-body or regulator source of comparable authority.

### Supporting evidence only

The following are useful but do not automatically establish eligibility by themselves:

- British Council Partner School / attached-centre status;
- Cambridge/Pearson examination delivery alone;
- Edarabia and other commercial school directories;
- Overture/OSM/Wikidata place records;
- the historical V7 archive;
- an institution name containing `international`, `American`, `British`, `German`, etc.;
- a foreign partnership or exchange agreement.

## Included higher-education rule

Include:

- foreign university branches recognized by Egyptian higher-education authorities;
- institutions such as The American University in Cairo where international institutional status is evidenced by the institution plus a recognized foreign accreditor/regulator.

Do not include an Egyptian university merely because it offers a foreign validated degree, exchange, dual-degree or partnership programme. Those relationships may later be represented as programme-level facts without making the university itself internationally scoped.

## Data architecture

The evidence architecture remains:

`external source -> edu_raw -> edu_staging -> edu_core -> portable/public projection`

The SQL schemas are a canonical relational/reference model. They are not a commitment to Supabase or a final runtime database.

### Core identity

Primary entities:

- provider/group;
- institution;
- campus/branch;
- academic unit;
- programme.

A campus is never silently duplicated as a separate institution unless evidence establishes it as legally/academically separate.

### Bilingual localization

English and Arabic are first-class representations of the same canonical factual entity.

Language-neutral facts are stored once. Localized text is modeled separately with locale and origin/status.

Required localizable domains include, where applicable:

- official/display institution name;
- short/alternate names;
- address display text;
- descriptions/profile copy;
- programme/academic-unit display names where needed.

Localization status must distinguish official/institution-source text from verified/editorial translation and transliteration.

Prefer official Arabic names. If an official Arabic form cannot be found, a transliteration/editorial Arabic display form may be stored only with an explicit non-official status.

### Required profile domains

For each eligible institution collect, when source-backed and available:

- Arabic and English names;
- provider/group;
- institution type;
- campuses and coordinates;
- curriculum(s) and certificates;
- accreditation/authorization bodies and identifiers;
- education levels / ages / grades;
- languages of instruction;
- gender model and boarding/day model where relevant;
- website, phone, email, admissions links and social channels;
- admissions dates and requirements;
- academic-year fee schedules;
- facilities;
- founding year;
- higher-education faculties, programmes, degree levels and awarding institution;
- source-backed descriptive/editorial facts;
- media candidates and publication rights metadata.

Missing fields remain null/unknown. They are never invented.

### Time-sensitive facts

Fees and admissions must be versioned by academic year/cycle.

Do not overwrite historical values when new values arrive.

### Provenance and conflicts

Every important canonical fact retains source/evidence, authority class, review/confidence state and validity period where relevant.

Conflicting values remain explicit review work rather than being silently overwritten.

## Source priority

### Tier A — authoritative international/regulatory evidence

- International Baccalaureate (IB)
- Supreme Council of Universities (SCU)
- Ministry of Higher Education and Scientific Research (MOHESR)
- French Ministry / official homologation system
- German KMK / ZfA recognized-school evidence
- recognized institutional accreditors such as MSCHE/Cognia where applicable

### Tier B — official institution evidence

- institution website
- official admissions/fees pages and PDFs
- official institution-controlled social/media channels when needed for current public contact facts

### Tier C — discovery/geospatial/supporting evidence

- British Council Partner Schools
- Edarabia
- Overture Maps
- OpenStreetMap / Wikidata
- retained V7 records
- other commercial directories used only when their terms permit the intended use

Tier C alone cannot establish a factual claim that requires stronger evidence.

## Media policy

Media is collected separately from factual identity.

For each media candidate preserve:

- institution/campus relation;
- source page and original reference;
- media role;
- creator/license/attribution where known;
- identity-match state;
- rights basis;
- public-use flag;
- owned/local storage reference and content hash when acquisition is permitted;
- EN/AR caption/alt where appropriate.

Publication-safe sources include institution-provided permission, Wikimedia/open-license media, verified institution claims, or original Edu Hub/Admonk production.

If no publication-safe image exists, the institution receives an explicit `placeholder_required` media state.

## Data-completion work packages

1. **D2.1 Candidate universe completion** — exhaust approved source families and measure discovery coverage.
2. **D2.2 Identity/campus reconciliation** — deduplicate institutions, campuses, providers and aliases.
3. **D2.3 EN/AR canonical localization** — complete bilingual naming/localized fields with origin/status.
4. **D2.4 Profile enrichment** — systematically attempt core profile fields for every eligible institution.
5. **D2.5 Media completion** — discover/reference/review media and establish terminal media state per institution.
6. **D2.6 Completeness/conflict audit** — measure factual, EN, AR, freshness/conflict and media coverage.
7. **D2.7 Portable database/export freeze** — emit deterministic presentation-neutral canonical exports plus evidence and media manifests.

## Quality gates before canonical completion

For an eligible institution:

- scope state = `eligible`;
- at least one strong identity/international-scope evidence source;
- canonical institution identity established;
- institution/campus relationship reviewed;
- no unresolved high-risk identity conflict;
- EN and AR naming coverage exists with localization origin/status;
- every stored important fact has provenance;
- fees/admissions retain academic-year/cycle history;
- media status is explicit even if no publishable image exists.

## Legacy cleanup rule

Do not delete the old national-registry evidence or raw archive. Preserve it as historical work, but:

- do not run EMIS/MOSS acquisition as part of the active milestone;
- do not import the 62,690-school or 48,225-nursery coverage targets into the new scope;
- do not auto-promote legacy V7 records into the international registry;
- only reuse a legacy record when it matches an EDU-DATA-2 eligible institution and the specific source terms/provenance remain valid.

## Definition of database complete

EDU-DATA-2's database gate is complete when:

- the approved candidate-source universe has been systematically covered;
- every candidate has an explicit scope decision or documented unresolved reason;
- eligible institutions/campuses have reviewed canonical identities;
- cross-source duplicates are reconciled or explicitly queued;
- every eligible institution has EN and AR naming coverage with localization origin/status;
- every core factual field that is present has source provenance;
- important changing facts preserve history/versioning;
- higher-education parent/programme relationships are represented correctly;
- every institution has an explicit media status;
- factual completeness, English completeness, Arabic completeness, freshness/conflicts and media completeness are measurable;
- a deterministic portable export can be generated without Astro, Instatic or Supabase;
- no final frontend/CMS decision is required to understand or operate the dataset.

Only after this definition is satisfied do we decide how to display the database publicly.
