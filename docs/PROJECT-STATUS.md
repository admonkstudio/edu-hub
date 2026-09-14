# Edu Hub Project Status

Last updated: 2026-09-15

## Current lifecycle

```text
00 Open                  APPROVED
01 Discover              APPROVED
02 Align + Audit         APPROVED FOR INTERNATIONAL SCOPE
03 Define                APPROVED — INTERNATIONAL EDUCATION ONLY
04 Content + Structure   ACTIVE — DATABASE COMPLETION
05 Creative Direction    DEFERRED
06 Design + Systemize    DEFERRED
07 Build + Connect       DEFERRED UNTIL DATABASE GATE
08 Verify + Optimize     CONTINUOUS DATA QA
09 Review + Launch       NOT STARTED
10 Handoff + Learn       NOT STARTED
```

## Current product state

Edu Hub is an Admonk-owned independent bilingual education discovery and knowledge platform focused initially on **international education in Egypt**.

Primary audience:

1. Parents
2. Students

Active Phase 1 includes private/independent international schools, private/independent IB World Schools, recognized foreign-national/international school models, recognized foreign university branches, internationally chartered/accredited independent higher-education institutions whose international status is substantive, and their campuses/eligible early-years sections.

Explicitly out of active scope:

- Egyptian public schools;
- Egyptian public universities;
- the historical 62,690-school EMIS national target;
- the historical 48,225-nursery MOSS national target;
- ordinary language schools/exam centres without sufficient international-status evidence;
- Egyptian universities whose only international dimension is a partnership, exchange, dual degree or validated programme.

Historical national-registry work remains preserved on `edu-data-1-national-registry` and in Git history. It is not an active product dependency.

## Active milestone

**EDU-DATA-2 — Egypt International Education Registry**

Status: **ACTIVE — DATABASE COMPLETION GATE**

Branch: `edu-data-2-international-registry`

Canonical contracts:

- `docs/EDU-DATA-2-INTERNATIONAL-REGISTRY.md`
- `docs/DATABASE-COMPLETION-PLAN.md`
- `docs/SOURCE-USAGE-POLICY.md`

Logical data architecture:

`external source -> raw evidence -> staging/reconciliation -> reviewed canonical data -> bilingual localization -> completeness/media audit -> portable export`

The final public presentation layer is intentionally deferred until this gate is complete.

## Platform boundary

Supabase is **not** part of the Edu Hub architecture.

Astro and Instatic remain possible later presentation/publishing choices, but no current work package should optimize the database for either one yet.

The database/research layer must remain presentation-neutral, exportable and able to feed either implementation later.

## Current database completion objective

We are finishing the **complete source-backed bilingual data architecture first**.

The target dataset contains canonical institution/provider/campus identities, English and Arabic localizations, international eligibility evidence, curricula/certificates, education stages and age/grade ranges, languages, accreditation, geography, contacts, admissions, versioned fees, facilities, higher-education programmes, media/rights, field-level provenance, completeness, freshness and explicit conflict state.

Missing information remains explicit. No value is invented to make a profile look complete.

## Bilingual architecture progress

`infra/owned-data/006_bilingual_completion.sql` extends the reference schema with source/review metadata for localizations, aliases, bilingual campus/programme/media structures, controlled education-level and facilities taxonomies, admissions requirements, fee localization, universal evidence assertions, and independent factual/English/Arabic/media completeness metrics.

Official Arabic institution names are preferred. If no official Arabic form exists, transliteration/editorial localization must be explicitly marked instead of being treated as official.

A first D2.3 institution-origin Arabic evidence package is now checked in for **4 institutions**:

- 2 current official Arabic-name evidence rows;
- 2 historical institution-origin Arabic-name rows that remain explicitly flagged for current revalidation.

The localization workflow performs zero automatic translation, zero canonical mutation and zero public promotion. Its first validation run passed CI.

## Authoritative / strong source evidence acquired

### International Baccalaureate

- Egypt-filtered IB directory snapshot contains **54 source rows** across three pages.
- The IB country summary reported **55** on the same date; that discrepancy remains a review flag.
- **12 current/detail ownership decisions** are now source-backed across dated snapshots:
  - 9 PRIVATE / in-scope IB source rows;
  - 3 STATE / out-of-scope source rows.
- The newest verified private rows include Evolution International School - NewGiza, Narmer American College, Cairo American College, Cairo English School and New Cairo British International School.
- Incremental IB detail evidence retains its own source date and supplements rather than rewrites the earlier snapshot.

### UK Department for Education — British Schools Overseas

- Current UK DfE BSO evidence contains **11 Egypt source rows** from the list updated 2026-08-26.
- All 11 have matched DfE/GIAS detail evidence with URNs, official names, open status and available address/age/contact/inspection fields.
- BSO establishes strong British/international-school-model evidence; private/independent ownership remains a separate scope gate.

### French homologation

- Official French 2026–2027 evidence is captured for **17 Egypt source rows** with UAI identifiers, city, levels, homologated classes and stream limitations.

### German recognition

- Official April 2026 KMK evidence is captured for **4 recognized German schools abroad in Egypt**.

### Council of International Schools

- A dated CIS accreditation evidence seed contains **6 current/recent Egypt school rows**.
- CIS is treated as strong international-school-model/accreditation evidence, while the private/independent ownership gate remains separate.

### Cognia

- The current source registry includes Cognia accreditation as a recognized-accreditor source.
- The 2026–2027 Cognia Member Milestones evidence currently contributes **4 Egypt candidate rows** reaching a 25-year accreditation milestone.
- Cognia accreditation is not treated as automatic proof of Edu Hub international-school eligibility; school model and ownership are reviewed separately.

### Higher education

- Current SCU evidence is captured for **9 recognized foreign university branches**.
- AUC is captured as an eligible international independent university using current MSCHE accreditation plus institutional evidence.
- MOHESR reconciliation remains review-only where regulator evidence differs or needs lifecycle reconciliation.

## Deterministic source-universe state

### Core authoritative/strong base

The deterministic base contains **96 source rows** before cross-source identity reconciliation:

- 54 IB;
- 11 UK DfE BSO;
- 17 French homologation;
- 4 German KMK;
- 9 SCU foreign-university branches;
- 1 AUC/MSCHE.

Current source-row states:

- **40 eligible**;
- **53 candidate**;
- **3 excluded**.

These are source rows, not a claim of 96 unique institutions.

### Accreditor-expanded D2.1 universe

Adding the separate CIS and Cognia evidence packages produces a **106-source-row** combined discovery/reconciliation universe:

- **40 eligible**;
- **63 candidate**;
- **3 excluded**.

English naming evidence is present for all 106 source rows. Arabic naming exists directly on 9 of those source rows, leaving 97 source-row Arabic-name gaps before reconciliation. The separate D2.3 official-Arabic evidence package is not mechanically added to that count because it must first be reconciled to canonical identities.

No unique-institution count is claimed yet. No automatic merge or canonical creation occurs in this expansion.

## D2.1 — Candidate universe completion progress

`tools/data-acquisition/international/build_candidate_universe.py` creates a presentation-neutral discovery package containing:

- `candidate-universe.jsonl`;
- source/state/family and bilingual coverage metrics;
- explicit bilingual-name gaps;
- cross-source overlap hints for review.

The combined 106-row universe now covers IB, UK BSO, French, German, SCU, AUC/MSCHE, CIS and Cognia evidence families. British Council Partner Schools remains the next broad supporting discovery expansion after browser/local acquisition.

Safety contract remains:

- no canonical institution creation;
- no automatic merge;
- no public projection;
- normalized names are review hints only;
- unique institution count remains unclaimed until D2.2 review.

## British Council Partner Schools acquisition boundary

The current September 2026 British Council Egypt Partner Schools PDF is a **19-page** discovery/contact source.

Direct Python retrieval from GitHub-hosted runners currently returns HTTP 403 while the PDF remains browser-accessible. The approved adapter therefore supports `--pdf-path` after a browser/local download instead of treating hosted 403 as source absence.

Partner/attached-centre status remains supporting discovery/contact evidence only and grants zero automatic international eligibility.

## D2.2 — Identity reconciliation progress

`tools/data-acquisition/international/plan_identity_reconciliation.py` remains review-only and never auto-accepts a merge.

Matcher v2 removes generic education/model words such as British, American, English and International from distinctive-token evidence so unrelated international schools are not proposed merely because of their model labels.

The 96-row base currently produces **5 review proposals** after this tightening. All remain `needs_review`; zero canonical merges are performed.

The 106-row expanded universe is now available for the next D2.2 review pass.

## D2.4 — First-party profile enrichment progress

A first official-site enrichment package now covers **8 high-priority institutions** from current institution-controlled websites plus regulator/authorizer evidence.

Current measured evidence coverage in that package:

- official website: 8/8;
- location/address: 7/8;
- contact: 6/8;
- admissions: 6/8;
- curriculum/programme evidence: 6/8;
- education-range evidence: 4/8;
- facilities evidence: 2/8;
- provider/group evidence: 1/8;
- founding-history evidence: 1/8;
- regulatory identifier/status evidence: 2/8.

The initial CI gate correctly failed because curriculum/programme coverage was only 4/8. Rather than weakening the threshold, current first-party curriculum evidence was added for NCBIS and GEMS British School Al Rehab. The repaired workflow is now green.

No current fee schedule is asserted in this package. Historical fee documents are not silently treated as current fees. The enrichment package performs zero canonical mutation, zero fee inference, zero automatic merge and zero publication.

## Supporting source policy

### Edarabia

Edarabia remains a reference/discovery index only under its current published terms:

- no bulk scraping/systematic import into Edu Hub;
- use it to identify a candidate or possible missing field;
- re-source the actual fact from an institution, regulator, accreditor or other permitted source;
- do not import ratings/reviews;
- do not republish images without independent rights.

### Other supporting sources

- British Council Partner Schools;
- Overture Maps;
- OpenStreetMap/Wikidata;
- historical V7 archive;
- official institution websites as the primary enrichment source once identity is established.

## Media state

Automatic Commons discovery records license/provenance candidates but never authorizes them automatically.

A reviewed seed currently contains **5 publication-safe Wikimedia assets** for selected institutions, with reuse basis and attribution metadata recorded.

Institution websites, social channels and commercial directories may provide discovery leads, but their images are not publication-safe by default. Every eligible institution must eventually have an explicit terminal media state, including `placeholder_required` where appropriate.

## Current CI state

Important accepted gates include:

- **EDU-DATA-2 International Registry**, run `34898121932`: green for the 96-row deterministic base, 40/53/3 state model, review-only identity pipeline and clean bilingual PostgreSQL/PostGIS reference migrations;
- **EDU-DATA-2 Accreditor Expansion**, run `34898150474`: green for the 106-row CIS/Cognia-expanded discovery universe;
- **EDU-DATA-2 Localization Evidence**, run `34897451220`: green for the first official-Arabic evidence package;
- **EDU-DATA-2 Official Site Enrichment**, run `34898574887`: green after adding current first-party curriculum evidence instead of weakening the coverage gate.

The repository continues to validate deterministic evidence packages without requiring a final Astro/Instatic runtime decision.

## Database completion work packages

### D2.1 — Candidate universe completion — **IN PROGRESS / MATERIAL EXPANSION COMPLETE**

Current combined source universe: 106 source rows across the principal authoritative/accreditor families. British Council broad discovery and remaining candidate-source searches are still pending.

### D2.2 — Identity and campus reconciliation — **STARTED / REVIEW-ONLY**

Deduplicate cross-source identities, separate institutions from campuses, resolve provider/group relationships, preserve aliases and queue ambiguous cases. No silent auto-merges.

### D2.3 — EN/AR canonical localization — **ARCHITECTURE IMPLEMENTED / EVIDENCE COLLECTION STARTED**

Four institution-origin Arabic names are now captured as a first package; broad EN/AR parity remains incomplete.

### D2.4 — Profile enrichment — **STARTED**

First 8-institution official-site evidence package is green. Systematic expansion to every eligible/candidate institution remains required.

### D2.5 — Media completion — **STARTED**

Publication-safe media evidence exists for a small reviewed set; broad terminal media-state coverage remains incomplete.

### D2.6 — Completeness/conflict audit — **ARCHITECTURE IMPLEMENTED / DATA AUDIT PENDING**

The schema supports independent factual/EN/AR/media completeness, but full per-institution audit waits for D2.2 reconciliation and broader D2.4 enrichment.

### D2.7 — Portable database/export freeze — **NOT STARTED**

Produce presentation-neutral canonical exports plus provenance, media manifest, review/conflict report and completeness report only after identity/enrichment review is sufficiently complete.

## Immediate next actions

1. Continue IB detail/ownership verification for the remaining directory candidate rows.
2. Acquire the 19-page British Council September 2026 PDF through the permitted browser/local route and run the existing adapter for broad discovery/contact leads.
3. Run D2.2 review against the 106-row combined universe and convert reviewed relationships into explicit institution/campus/provider decisions without auto-merging.
4. Expand first-party D2.4 enrichment from 8 institutions toward every eligible entity, prioritizing official websites and primary documents.
5. Add current fee schedules only where an official current-year source exists; preserve older schedules as historical versions.
6. Expand official Arabic-name evidence and revalidate the two historical institution-origin Arabic names.
7. Reconcile SCU and MOHESR foreign-university evidence and lifecycle state.
8. Expand coordinates/geography from institution sources plus Overture/OSM cross-checks.
9. Continue media discovery/rights review and assign a terminal media state to every reviewed institution.
10. Produce the first reconciliation-aware factual/EN/AR/media completeness report.
11. Generate the deterministic portable export only after those review gates are satisfied.

## Explicitly deferred during database completion

- Astro vs Instatic selection;
- final website architecture;
- card/listing/profile UI;
- filters/search UX;
- public CMS collection mapping;
- visual design system;
- frontend deployment;
- public SEO page generation.

## Non-negotiable constraints

- Do not reintroduce full Egyptian public-school/university coverage without a new owner decision.
- Do not confuse exam-centre/partner status with international-school eligibility.
- Do not infer international status from branding words.
- Do not let a commercial directory establish eligibility or override stronger evidence.
- Respect source storage/reuse terms before systematic acquisition.
- Do not invent institution facts, fees, rankings, accreditations or admissions data.
- Do not publish media without a recorded rights basis.
- Do not use Supabase for Edu Hub.
- Do not import Edu Hub data into Ask Kalam infrastructure.
- Do not publish raw/staging evidence directly.
- Do not let Astro or Instatic limitations distort the canonical database during the database-completion gate.
- Keep English/Arabic parity, provenance, portability and data quality active throughout.
