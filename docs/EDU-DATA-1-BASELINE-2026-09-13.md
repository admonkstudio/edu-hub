# EDU-DATA-1 Verified Baseline — 2026-09-13

This baseline records what Edu Hub has actually verified at the start of the Egypt National Education Registry milestone. It deliberately distinguishes acquired row-level evidence from aggregate targets and unacquired datasets.

## Verified executable sources

### Supreme Council of Universities (SCU)

Live refresh executed successfully in GitHub Actions on 2026-09-13.

Result: **327 / 327 expected category entries acquired**.

| Category | Expected | Acquired |
| --- | ---: | ---: |
| Government universities | 28 | 28 |
| National / non-profit universities | 33 | 33 |
| Government technological universities | 12 | 12 |
| Private universities | 39 | 39 |
| Foreign university branches | 9 | 9 |
| Universities of special nature | 2 | 2 |
| International/framework institutions | 9 | 9 |
| Government-supervised institutions | 4 | 4 |
| Accredited private institutes | 181 | 181 |
| Accredited military colleges/academies | 8 | 8 |
| Private technological universities | 2 | 2 |
| **Total** | **327** | **327** |

This is a source/category acquisition count. Staging must still reconcile category overlap, identity relationships and differences between SCU accreditation views and MOHESR sector lists before producing canonical counts.

### Al-Azhar Institute Guide

The existing full official acquisition remains the best current row-level pre-university official source in the repository, with **7,674 source records** from the official institute guide.

A new live smoke test on 2026-09-13 verified that the adapter still works:

- all 27 governorates were exposed by the live form;
- first tested governorate: Cairo;
- first tested administration: North Cairo Azhar Educational Administration;
- 25 public filter combinations queried;
- 73 unique institute IDs discovered in that one administration;
- bounded sample wrote 5 profiles;
- 5/5 had names;
- 5/5 had useful location evidence.

The sample limit was deliberate. It proves the adapter remains healthy; it does not replace the prior full acquisition.

## Official national targets not yet acquired row-by-row

### Ministry of Education / EMIS

Official 2025/26 target: **62,690 schools**.

Current official Egyptian Schools Directory: `https://search.emis.gov.eg/`.

Known public school-directory paths include:

- `https://search.emis.gov.eg/`
- `https://search.emis.gov.eg/sch_data.aspx`
- `https://search.emis.gov.eg/search_schpriv.aspx`

The current directory is still publicly referenced in 2026 as the Ministry's school-search service. However, all of the above endpoints time out from the current GitHub-hosted/web acquisition environment.

Status: **official universe confirmed; row-level national acquisition blocked by network reachability from hosted runners**.

Accepted paths to resolve:

1. run the prepared local capture/probe from an Egypt-reachable network and implement the public form enumeration against the captured current contract; or
2. receive a current machine-readable export from MOE/EMIS.

No secondary school directory may be relabelled as 62,690-school official coverage.

### Ministry of Social Solidarity nursery census

Current official target: **48,225 nurseries**. The Ministry's website still reports 48,225 nurseries in its current facts/figures section.

The Ministry has stated that a national row-level database exists behind the comprehensive census and that a public nursery map/platform is being developed. The currently public material does not expose a complete row-level national export.

Status: **official universe confirmed; row-level national dataset not publicly downloadable in the current acquisition pass**.

Accepted paths to resolve:

1. obtain a machine-readable census/registry extract from MOSS;
2. acquire the row-level public data if/when the official nursery map is launched;
3. use secondary nursery directories only for discovery/enrichment, never as a substitute for census coverage.

## Current national-registry state

| Family/source | Row-level evidence | Coverage status |
| --- | --- | --- |
| SCU higher education | yes | current category acquisition complete: 327/327 |
| Al-Azhar institutes | yes | 7,674 previously acquired; adapter revalidated |
| MOHESR private/technical lists | partial/available in existing acquisition work | requires staging reconciliation with SCU |
| MOE/EMIS schools | no national row-level extract yet | blocked from hosted runners; target 62,690 |
| MOSS nurseries | no national row-level extract yet | official export/public map required; target 48,225 |
| OSM | yes, secondary | geospatial/discovery only |
| Secondary directories | yes, partial | discovery/enrichment only |

## Workflow evidence

GitHub Actions run: `34735562363`

- `Validate registry contract` — success
- `Probe accessible official registries` — success

Artifacts:

- `edu-data-1-contract-report` — source contract validation
- `edu-data-1-official-source-smoke` — current SCU snapshot/report + bounded Al-Azhar sample

## Decision

The national identity registry should continue in this order:

1. lock the existing 327 SCU and 7,674 Al-Azhar source evidence into the new staging/core pipeline;
2. reconcile MOHESR higher-education views;
3. solve MOE/EMIS through an Egypt-reachable acquisition environment and/or official export;
4. obtain MOSS row-level nursery data through an official data-sharing/export route or the future public map;
5. only then run broad institution enrichment and completeness improvement.

This baseline must be updated whenever a national coverage blocker is resolved.