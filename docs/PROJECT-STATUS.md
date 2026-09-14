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

### MOE / EMIS — D1.3 active acquisition

- Official 2025/26 target remains 62,690 schools.
- The official Egyptian Schools Directory is still the required primary identity source.
- GitHub-hosted/web acquisition environments still time out against the directory, but an Egypt-local run on 2026-09-14 **successfully reached `https://search.emis.gov.eg/`**, proving the blocker is environment/network locality rather than total source unavailability.
- The first Egypt-local evidence capture reached 1/3 initially probed routes, detected ASP.NET state (`__VIEWSTATE`, `__VIEWSTATEGENERATOR`, `__EVENTVALIDATION`) and preserved the contract safely, but the root page itself exposed no enumerable school-filter selects. Adapter design therefore correctly remained blocked.
- Recent Egyptian school/academic references identify `https://search.emis.gov.eg/search_schgov.aspx` as the government-school directory route. The one-command local handoff now probes that current route directly and performs bounded same-origin endpoint discovery from captured public HTML instead of relying only on historical route assumptions.
- `run_emis_local_capture.py` now performs public contract capture, bounded same-origin search-route discovery, offline contract analysis and emits a redacted ZIP handoff bundle even when adapter design remains blocked, so exact evidence can be reviewed without screenshots.
- `emis_local_capture.py` records form labels, public select options, ASP.NET state-field names, postback behavior, candidate endpoints and local raw HTML evidence while keeping hidden form-state values out of the JSON/shareable HTML.
- `registry/analyze_emis_capture.py` ranks candidate forms and determines whether bounded pilot-adapter design is unblocked; it performs no network requests or form submissions.
- CI tests enforce that endpoint discovery stays on `search.emis.gov.eg`, that raw hidden-state HTML is excluded from the shareable ZIP, that capture analysis cannot authorize bulk enumeration, cannot mutate `edu_core`, and cannot promote public data.
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
2. Pull the corrected D1.3 handoff and rerun `python tools/data-acquisition/run_emis_local_capture.py` from the proven Egypt-reachable machine so the current `search_schgov.aspx` route and any bounded same-origin school-search routes are captured.
3. Upload/use the resulting `emis-local-capture-bundle.zip`; a bundle is now emitted even when the analyzer remains blocked.
4. Implement a bounded governorate/administration pilot only when `enumerator-contract.json` reports `adapter_design_unblocked=true`.
5. Validate native source IDs, postback state, pagination, failed combinations and duplicate IDs before any national run.
6. Validate unique official school-source coverage against the 62,690-school 2025/26 target without substituting secondary-directory counts.
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
