# Edu Hub Project Status

Last updated: 2026-09-14

## Current lifecycle

```text
00 Open                  APPROVED
01 Discover              APPROVED
02 Align + Audit         APPROVED FOR CURRENT SCOPE
03 Define                APPROVED
04 Content + Structure   IN PROGRESS — NATIONAL DATA CONTRACT
05 Creative Direction    DEFERRED DURING DATA FOUNDATION
06 Design + Systemize    DEFERRED DURING DATA FOUNDATION
07 Build + Connect       IN PROGRESS — EDU-DATA-1
08 Verify + Optimize     CONTINUOUS FOR DATA PIPELINE
09 Review + Launch       NOT STARTED
10 Handoff + Learn       NOT STARTED
```

## Current project state

Edu Hub is an Admonk-owned independent education discovery and knowledge platform.

Initial market: Egypt.

Primary audience:

1. Parents
2. Students

The active priority is no longer broad public-directory expansion. The project is building the **Egypt National Education Registry** first so every legitimate institution can be represented once with source-backed identity, explicit provenance and measurable completeness.

Phase 1 still combines:

- structured education-provider directory
- bilingual public experience
- editorial/knowledge platform
- internal research/admin system
- source provenance and freshness workflows
- technical SEO and AI-search discoverability foundation

Phase 2 commercial functionality remains intentionally deferred.

## Approved architecture direction

- Astro + TypeScript remains the approved code-native application direction
- PostgreSQL is the operational source of truth
- Supabase is the approved initial database/auth/storage platform direction
- PostGIS for geographic capability
- Arabic + English from launch
- country-aware locales beginning with `ar-EG` and `en-EG`
- official-source-first data collection
- explicit source/evidence model
- deterministic indexability rules
- curated programmatic SEO only
- PostgreSQL search first; dedicated search infrastructure only after evidence justifies it
- national data path: `external source -> edu_raw -> edu_staging -> edu_core -> public projection -> website/CMS`

## Current implementation milestone

**EDU-DATA-1 — Egypt National Education Registry**

Status: **ACTIVE**

Branch: `edu-data-1-national-registry`

The milestone contract is defined in `docs/EDU-DATA-1-NATIONAL-REGISTRY.md`.

The goal is identity coverage before profile completeness. Missing fees, contacts, websites or media do not invalidate a legitimate institution. No missing factual field may be invented.

## Verified national-registry progress

### Owned raw archive

- V7 remains the complete portable owned acquisition archive from the pre-registry phase: 24,916 raw records across 13 sources.
- V7 preserves 2,101 media provenance references and 453 unique content-addressed media binaries.
- Media publication remains disabled by default until rights/public-use eligibility is established.
- The archive/import package remains independently restorable and checksum-verifiable.

### Registry/staging safety foundation

- `edu_raw`, `edu_staging`, `edu_core` and later public-projection boundaries are explicitly defined.
- Current/historical/no-coverage source aliases are machine-readable and validated.
- The verified base-v3 recovery seed produces 13,192 staging candidates.
- 8,001 rows receive current official-source coverage credit before identity resolution: 7,674 Al-Azhar + 327 SCU.
- Canonical planning remains proposal-only: zero automatic identity acceptances and zero public promotion.

### Higher education — D1.2

- SCU live acquisition is verified at 327/327 expected category entries.
- Al-Azhar full official evidence remains 7,674 source records; the live adapter continues to pass bounded smoke checks.
- MOHESR private-institute sector acquisition is active and reconciled against SCU as review-only identity proposals.
- MOHESR technical hierarchy acquisition is verified at **8 technological-college parents and 44 technical institutes**.
- The 44 technical institute parent links now flow into the reconciliation layer as source-backed relationship proposals.
- CI enforces zero automatic identity acceptance, zero automatic hierarchy acceptance, zero `edu_core` mutation and zero public promotion.

### MOE / EMIS — D1.3 live contract state

- Official 2025/26 target remains 62,690 schools.
- The official Egyptian Schools Directory remains the required primary identity source.
- GitHub-hosted/web acquisition environments still time out against the directory, but an Egypt-local run on 2026-09-14 proved `https://search.emis.gov.eg/` is healthy from an Egypt network with ASP.NET state fields present.
- The first local diagnostic established that direct GETs to `search_schgov.aspx`, `search_schpriv.aspx` and `sch_data.aspx` return HTTP 500 rather than exposing a usable search contract.
- The root page exposes six ASP.NET submit buttons for government, private, special-education, sports, military and experimental schools. Category navigation therefore depends on root-form POST state rather than ordinary anchor navigation.
- A second Egypt-local bundle proved all six category buttons can be submitted through the live root contract. Exactly one category currently reaches a healthy search page: **Special Education** at `search_schSpecialEdu.aspx`.
- Government, private, sports, military and experimental category navigations currently end at server-side HTTP 500 responses. These failures are now treated as source availability failures, not as missing scraper logic.
- The accessible Special Education page exposes the expected ASP.NET search architecture and two dependent selects: governorate (`DDList_mud`) and stage (`DDList_stage`). Both are initially empty and the page explicitly requires a school-type radio postback first.
- The analyzer now ranks this navigated search form above the root launcher, identifies its scope as `special_education`, and explicitly prevents that evidence from unblocking government-school enumeration.
- `emis_control_hydration_probe.py` now performs at most one whitelisted, non-placeholder radio-button `__doPostBack` on an already-reached search form in order to hydrate dependent selects. It does not submit the school-search button.
- The one-command local wrapper now runs GET capture -> category navigation -> optional dependent-control hydration -> offline analysis -> redacted shareable ZIP.
- Navigation diagnostics no longer retry away HTTP 500 statuses, so current category-route failures remain explicit evidence in `capture-report.json`.
- Escaped ASP.NET `__doPostBack` handlers are now recognized in captured field contracts.
- Dedicated CI enforces the navigation, hydration and category-scope safety boundaries. A healthy Special Education contract may be used to validate reusable ASP.NET mechanics, but it can never be relabelled as government-school coverage.
- No school search, result pagination, school-row enumeration, `edu_core` mutation or public promotion is authorized by the current EMIS tools.
- Secondary directories must not be relabelled as complete MOE coverage.

### MOSS nurseries — D1.4 blocker

- Official national target remains 48,225 nurseries.
- The national census universe is confirmed, but a complete row-level public export is not currently available in the acquisition pipeline.
- Accepted resolution paths are official data sharing/export or the announced public nursery map/platform when row-level data is exposed.

## Infrastructure state

- No dedicated Edu Hub Supabase project is currently visible in the connected Supabase organization.
- The two visible Supabase projects belong to Ask Kalam and must not receive Edu Hub data.
- Database provisioning is therefore still required before the national registry can become an operational hosted PostgreSQL dataset; this does not block source acquisition and contract work in Git/GitHub Actions.

## Immediate next actions

1. Treat D1.2 higher-education acquisition/reconciliation plumbing as implemented and keep unresolved identity decisions review-only.
2. Pull the current D1.3 branch and rerun `python tools/data-acquisition/run_emis_local_capture.py` from the proven Egypt-reachable machine. The wrapper will now attempt exactly one safe Special Education control-hydration postback after category navigation.
3. Review the regenerated `emis-local-capture-bundle.zip`. If the Special Education governorate/stage selects populate, use that evidence only to finalize a reusable ASP.NET state/postback engine; keep government national enumeration blocked.
4. Re-test the government category on every local capture. Only a healthy government search form may unlock the bounded government-school pilot.
5. Once government form access returns, implement only a small governorate/administration pilot and validate native source IDs, ASP.NET dependencies, pagination, failed combinations and duplicate IDs before any national run.
6. Validate unique official school-source coverage against the 62,690-school 2025/26 target without substituting Special Education or secondary-directory counts.
7. Continue D1.4 MOSS official data-request/public-map track for the 48,225-nursery universe.
8. Provision a dedicated Edu Hub PostgreSQL/Supabase environment before importing the national registry into an operational hosted database.
9. Only after identity coverage stabilizes, begin D1.5 broad enrichment and completeness improvement.

## Non-negotiable project constraints

- Do not build monetization during Phase 1 foundation work.
- Do not equate paid status with verification.
- Do not auto-index every database entity or filter combination.
- Do not allow AI to silently overwrite or invent verified factual data.
- Do not commit secrets.
- Do not publish directly from `edu_raw` or `edu_staging`.
- Keep Arabic/RTL, provenance, data portability and performance requirements active from the beginning.
