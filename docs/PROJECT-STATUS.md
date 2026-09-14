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
- GitHub-hosted/web acquisition environments still time out against the directory, but Egypt-local runs on 2026-09-14 proved `https://search.emis.gov.eg/` is reachable with valid ASP.NET state fields.
- Direct GETs to `search_schgov.aspx`, `search_schpriv.aspx` and `sch_data.aspx` do not expose a usable contract.
- The root page exposes six ASP.NET submit buttons for government, private, special-education, sports, military and experimental/language schools; category navigation therefore depends on root-form POST state.
- Fresh root state was used before every category submission. Government, private, sports, military and experimental/language category navigations currently end in HTTP 500 responses.
- Special Education is the only category that currently reaches a search-form page, at `search_schSpecialEdu.aspx`.
- That form exposes dependent governorate (`DDList_mud`) and stage (`DDList_stage`) selects plus exactly three non-placeholder school-type radio postbacks.
- A final bounded Egypt-local diagnostic submitted **all three** observed school-type postbacks independently with fresh sessions and fresh ASP.NET state: `تربية فكرية`, `مكفوفين وضعاف بصر`, and `صم وضعاف سمع`.
- All three postbacks were technically accepted and returned HTTP 200 with the selected radio state preserved, but all three left governorate/stage empty and displayed the ministry-side message `خطأ اثناء محاولة تحميل الصفحة`.
- Final hydration result: 3 controls discovered, 3 submitted, 3 HTTP-success responses, 0 pages with populated selects, 0 populated selects, and 3 pages with visible EMIS load errors.
- This exhausts the current safe client-side contract diagnostic. The blocker is classified as a live source/application data-loading failure, not an unresolved postback-format issue.
- `docs/EMIS-LIVE-FAILURE-EVIDENCE-2026-09-14.md` is the canonical evidence note for this state.
- Do not repeat the same Special Education hydration diagnostic unless the source changes materially.
- `emis_health_recheck.py` is now the lightweight recovery detector. It checks only the root and top-level category routes and can recommend a fresh contract capture if the government route returns cleanly; it never authorizes enumeration itself.
- Government-school enumeration remains blocked. A healthy government route must first be freshly recaptured and reviewed before any small pilot can be implemented.
- The official machine-readable MOE/EMIS export request is now the primary D1.3 acquisition path while the live route is unhealthy.
- No school search, result pagination, school-row enumeration, `edu_core` mutation or public promotion was performed during these diagnostics.
- Secondary directories must not be relabelled as complete MOE coverage.

### MOSS nurseries — D1.4

- Official national target remains 48,225 nurseries.
- MOSS continues to publish the 48,225 national count from the comprehensive nursery census.
- Official ministry material states that a digital early-childhood platform/nursery map is being developed from the census database and is intended to expose family-facing fields including nearest nursery, licensing status, capacity and fees.
- That row-level public map/export is not yet present in the current acquisition pipeline, so D1.4 remains an official data-sharing/export track rather than a secondary-directory substitution.
- `docs/requests/MOSS-NURSERY-DATA-REQUEST-AR.md` remains the prepared official request for the row-level registry and associated code/data dictionary.

## Infrastructure state

- No dedicated Edu Hub Supabase project is currently visible in the connected Supabase organization.
- The two visible Supabase projects belong to Ask Kalam and must not receive Edu Hub data.
- Database provisioning is therefore still required before the national registry can become an operational hosted PostgreSQL dataset; this does not block source acquisition and contract work in Git/GitHub Actions.

## Immediate next actions

1. Treat D1.2 higher-education acquisition/reconciliation plumbing as implemented and keep unresolved identity decisions review-only.
2. Stop repeating the exhausted Special Education hydration diagnostic. Use `python tools/data-acquisition/emis_health_recheck.py` only as a lightweight periodic recovery check.
3. Pursue the official machine-readable MOE/EMIS export using `docs/requests/MOE-EMIS-DATA-REQUEST-AR.md`; preserve any received file unchanged with provenance and checksum before staging.
4. If the government EMIS route becomes cleanly reachable, perform a fresh contract capture and review it before implementing only a small governorate/administration pilot.
5. Validate unique official school-source coverage against the 62,690-school 2025/26 target; do not substitute Special Education or secondary-directory counts.
6. Advance D1.4 through the prepared MOSS request while monitoring the announced official nursery-map platform for row-level access.
7. Validate any future MOSS row-level source against the 48,225-nursery national target and preserve licensing/location provenance.
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
