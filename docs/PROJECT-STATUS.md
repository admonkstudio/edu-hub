# Edu Hub Project Status

Last updated: 2026-09-14

## Current lifecycle

```text
00 Open                  APPROVED
01 Discover              APPROVED
02 Align + Audit         REOPENED / APPROVED FOR NEW SCOPE
03 Define                APPROVED — INTERNATIONAL EDUCATION ONLY
04 Content + Structure   IN PROGRESS — INTERNATIONAL REGISTRY
05 Creative Direction    DEFERRED DURING DATA FOUNDATION
06 Design + Systemize    DEFERRED DURING DATA FOUNDATION
07 Build + Connect       IN PROGRESS — EDU-DATA-2
08 Verify + Optimize     CONTINUOUS
09 Review + Launch       NOT STARTED
10 Handoff + Learn       NOT STARTED
```

## Current product state

Edu Hub is an Admonk-owned independent education discovery and knowledge platform for Egypt.

Primary audience:

1. Parents
2. Students

The product scope changed materially on 2026-09-14. **Edu Hub is no longer attempting to build Egypt's complete public education registry.** The active product now focuses on high-quality international education in Egypt.

### Active Phase 1 institution scope

- private/independent international schools;
- private/independent IB World Schools;
- recognized British, American, French, German, Canadian and comparable international-school models;
- foreign university branch campuses recognized in Egypt;
- internationally chartered/accredited independent institutions such as AUC when international status is substantively evidenced;
- campuses and early-years sections belonging to eligible institutions.

### Explicitly out of active scope

- Egyptian public schools;
- Egyptian public universities;
- the 62,690-school national EMIS coverage objective;
- the 48,225-nursery MOSS coverage objective;
- ordinary Egyptian private/language schools without sufficient international-status evidence;
- Egyptian universities that only have foreign partnerships/dual degrees/exchanges;
- commercial-directory-only identities.

The old national-registry work is preserved as historical evidence and optional future expansion material. It is not deleted, but it is no longer allowed to drive the current roadmap.

## Active milestone

**EDU-DATA-2 — Egypt International Education Registry**

Status: **ACTIVE**

Branch: `edu-data-2-international-registry`

Canonical contract: `docs/EDU-DATA-2-INTERNATIONAL-REGISTRY.md`

Architecture remains:

`external source -> edu_raw -> edu_staging -> edu_core -> public projection`

No source is read live at page-render time after acquisition.

## Work completed for the scope reset

### Clean branch / source-of-truth reset

- Created `edu-data-2-international-registry` from the completed national-registry evidence branch.
- The old `edu-data-1-national-registry` branch remains available as historical work.
- EDU-DATA-2 eligibility rules now distinguish `candidate`, `eligible`, `excluded`, and `needs_review` institutions.
- International eligibility is based on source evidence rather than institution naming or marketing language.

### Clean relational database foundation

`infra/owned-data/005_international_registry.sql` now extends the existing evidence architecture with explicit international-registry structures for:

- provider/group identity;
- bilingual institution localizations;
- international eligibility and eligibility evidence;
- geography and campuses with PostGIS;
- curricula and certificates;
- languages of instruction;
- accreditation/authorization bodies and institution accreditations;
- contacts;
- academic-year fee schedules and fee items;
- admissions cycles;
- higher-education academic units and programmes;
- media rights/license metadata.

The schema preserves field/source evidence instead of overwriting facts without provenance.

### Authoritative source registry

`tools/data-acquisition/international/source_registry.json` defines the active acquisition universe and whether each source is strong eligibility evidence or supporting evidence.

Current priority sources include:

- International Baccalaureate (IB);
- SCU foreign university branches;
- MOHESR international/foreign branches;
- French Ministry homologation list;
- German KMK/ZfA recognized schools;
- Cognia and MSCHE where applicable;
- British Council Partner Schools as discovery/support evidence;
- official institution websites;
- Overture/OSM for geography;
- Wikimedia Commons for licensed media;
- V7 only as retained supporting/discovery evidence for matching eligible entities.

### Initial repeatable acquisition

New tools:

- `tools/data-acquisition/international/acquire_ib_egypt.py`
  - acquires the complete current Egypt IB World School set;
  - current official source count is expected to be 54;
  - private schools become strong international-scope candidates;
  - public/state IB schools are retained as excluded evidence, not deleted;
  - stores programme/language/contact/source metadata and source hashes;
  - performs no database/public mutation.

- `tools/data-acquisition/international/acquire_scu_foreign_branches.py`
  - acquires the current SCU foreign-university branch set;
  - current SCU count is expected to be 9;
  - treats SCU recognition as strong eligibility evidence;
  - performs no database/public mutation.

- `.github/workflows/edu-data-2-international-registry.yml`
  - validates the source registry and parser safety contract;
  - acquires the IB and SCU authoritative seed;
  - uploads the resulting JSONL/summary artifact;
  - explicitly verifies zero database mutation and zero public promotion during acquisition.

## Data/media policy

### Facts

- Missing information remains unknown/null.
- Fees/admissions are versioned by academic year rather than overwritten.
- Curriculum/accreditation status must retain source and validity evidence.
- British Council Partner School status alone does not prove that a school belongs in the active international registry.

### Media

Publication-safe media priority:

1. institution-supplied media with permission;
2. Wikimedia Commons/openly licensed media with license/creator/attribution stored;
3. verified institution-claim uploads in a later phase;
4. original Edu Hub/Admonk media.

Institution website/social images can be retained as media candidates/provenance, but public reuse remains disabled until rights are established.

If no safe photo exists, the public interface uses the institution's English name on a designed placeholder instead of copyrighted hotlinks or scraped images.

## Infrastructure state

A dedicated Edu Hub PostgreSQL/Supabase project still does **not** exist in the connected Supabase organization.

The two connected projects are Ask Kalam projects and must not receive Edu Hub data.

All EDU-DATA-2 migrations/acquisition contracts are therefore being prepared and validated in Git first. Creating the dedicated project requires explicit organization/cost confirmation before provisioning.

## Immediate next actions

1. Validate the new EDU-DATA-2 CI run and inspect the first authoritative IB + SCU artifact.
2. Add/reconcile MOHESR foreign-university branch evidence with the SCU set.
3. Acquire the Egypt subset of the French 2026–2027 homologation list.
4. Acquire the current German KMK/ZfA Egypt school set.
5. Add Cognia/US accreditation evidence for American/international schools where available.
6. Ingest the September 2026 British Council Partner Schools PDF as discovery/contact evidence, but do not automatically promote every attached centre.
7. Match the resulting authoritative candidates against V7/Overture/OSM to fill coordinates, alternate names and known websites without allowing those supporting sources to establish eligibility alone.
8. Enrich each eligible institution from its official website: campuses, contacts, curricula, grades/ages, admissions, fees, programmes and official media candidates.
9. Discover publication-safe media from Wikimedia Commons/open licenses; retain other institution-site media only as rights-unreviewed candidates.
10. Provision a dedicated Edu Hub Supabase/PostgreSQL project, apply migrations `001` through `005`, and import only EDU-DATA-2 evidence/candidates into the clean operational environment.
11. Deduplicate institution vs campus identities and review `needs_review` records before generating the first public projection.

## Non-negotiable constraints

- Do not reintroduce full Egyptian public-school/university coverage without a new owner decision.
- Do not confuse exam-centre/partner status with international-school eligibility.
- Do not infer international status from a name containing `International`, `British`, `American`, etc.
- Do not silently turn foreign partnerships into international-university identities.
- Do not invent institution facts, fees, rankings, accreditations or admission details.
- Do not publish media without a recorded rights basis.
- Do not import Edu Hub data into Ask Kalam infrastructure.
- Do not publish directly from `edu_raw` or `edu_staging`.
- Keep Arabic/RTL, provenance, portability, performance and SEO requirements active.
