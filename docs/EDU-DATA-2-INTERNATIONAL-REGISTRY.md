# EDU-DATA-2 — Egypt International Education Registry

Status: ACTIVE

Branch: `edu-data-2-international-registry`

## Product scope

Edu Hub now focuses on **international education in Egypt** rather than attempting to represent the complete Egyptian public education system.

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
- commercial school directories;
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

The existing evidence architecture remains valid:

`external source -> edu_raw -> edu_staging -> edu_core -> public projection`

But EDU-DATA-2 narrows what may be promoted into `edu_core` and adds a richer relational international profile.

### Core identity

One institution identity may have multiple campuses. A campus is never silently duplicated as a separate institution unless the source establishes it as a legally/academically separate institution.

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

### Tier C — discovery/geospatial evidence

- British Council Partner Schools
- Overture Maps
- OpenStreetMap / Wikidata
- retained V7 records
- commercial directories used only when their terms permit the intended use

Tier C alone cannot establish a factual claim that requires stronger evidence.

## Media policy

Media is collected separately from factual identity.

Permitted publication sources include:

1. institution-provided media with explicit reuse permission;
2. Wikimedia Commons or other openly licensed media with license/creator/attribution preserved;
3. media later supplied through a verified institution claim;
4. original Edu Hub/Admonk-created media.

Official institution website/social images may be stored as **discovery candidates and provenance references**, but public reuse is disabled unless a defensible rights basis exists.

If no publication-safe photo exists, the public UI uses the institution's English name on a designed placeholder rather than scraping or hotlinking copyrighted imagery.

## Initial source acquisition order

1. IB Egypt — complete 54-school country set; exclude state/public schools from active scope.
2. SCU foreign university branches — current regulator list.
3. MOHESR international/foreign branches — reconcile against SCU.
4. French 2026–2027 homologated institutions — Egypt subset.
5. German KMK/ZfA recognized schools — Egypt subset.
6. Cognia / relevant US accreditation evidence.
7. British Council September 2026 Partner Schools — discovery and contact enrichment, not automatic eligibility.
8. official institution websites — contacts, campuses, admissions, fees, curricula, programmes and media candidates.
9. Overture/OSM/Wikidata — coordinates and identity cross-checking.
10. Wikimedia Commons — licensed media discovery.

## Quality gates

Before an institution becomes public:

- scope state = `eligible`;
- at least one strong identity/international-scope evidence source;
- canonical name established;
- institution vs campus relationship reviewed;
- no unresolved high-risk identity conflict;
- every published fact has source provenance;
- media either has `public_use_allowed=true` with rights metadata or the generated placeholder is used.

## Legacy cleanup rule

Do not delete the old national-registry evidence or raw archive. Preserve it as historical work, but:

- do not run EMIS/MOSS acquisition as part of the active milestone;
- do not import the 62,690-school or 48,225-nursery coverage targets into the new scope;
- do not auto-promote legacy V7 records into the international registry;
- only reuse a legacy record when it matches an EDU-DATA-2 eligible institution and the specific source terms/provenance remain valid.

## Definition of done

EDU-DATA-2 foundation is complete when:

- the dedicated Edu Hub PostgreSQL/Supabase project exists;
- the international relational schema is migrated;
- authoritative source acquisition jobs are repeatable;
- the candidate universe has been deduplicated into institution/campus identities;
- every included institution has an explicit eligibility evidence trail;
- media rights/publication status is explicit;
- an initial representative public projection can be generated without reading live third-party sources at page-render time.
