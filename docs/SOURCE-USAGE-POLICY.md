# Edu Hub Source Usage Policy

Status: **ACTIVE**

This policy supplements `tools/data-acquisition/international/source_registry.json` and the data-completion contract. It exists to prevent a useful discovery source from silently becoming an unauthorized bulk-copy source.

## Principle

A source can be useful for **discovery** without being permitted for systematic storage or republication.

For every source distinguish:

1. discovery permission / practical usefulness;
2. factual authority;
3. storage/reproduction rights;
4. media reuse rights;
5. eligibility authority.

These are independent.

## Edarabia

Edarabia is useful for discovering international-school candidates and identifying possible missing fields such as curriculum, location, website and fee information.

However, Edarabia's published terms state that, without prior written permission, its content may not be systematically stored, reproduced, transmitted to another site/server/archive, commercially exploited or otherwise reused beyond the limited personal-use permissions in those terms.

Therefore Edu Hub's active rule is:

- **no bulk scraping/copying of Edarabia content into the Edu Hub database**;
- **no systematic retention of Edarabia descriptions, fees, addresses, reviews, photos or other page content** unless written permission/license is obtained;
- Edarabia may be used as a **research/discovery index** to identify a school or a field that needs investigation;
- once a lead is identified, the factual value must be re-sourced from an official institution website, regulator, accreditor, awarding body or another source whose terms permit our intended use;
- an Edarabia URL may be retained as a research reference/lead, but it does not establish a canonical fact or international eligibility;
- Edarabia ratings/reviews are not imported into the canonical database;
- Edarabia images are not copied or published unless independent rights are established;
- if Edarabia grants written reuse permission in the future, record the permission/license before changing this policy.

Terms reference: `https://www.edarabia.com/privacy-policy/` (section titled "Use of edarabia content").

## British Council Partner Schools

Use the September 2026 Partner Schools list as discovery/contact/supporting evidence. Partner/attached-centre status does not automatically establish that an institution is an international school under Edu Hub scope.

The current PDF is browser-accessible and contains 19 pages, but direct Python retrieval from GitHub-hosted runners currently returns HTTP 403. Do not interpret that hosted 403 as source absence. The approved adapter supports a browser/local PDF supplied with `--pdf-path`; source rows remain candidate/discovery rows with zero automatic eligibility, merge or public promotion.

## Council of International Schools (CIS)

CIS International Accreditation is strong evidence that a school delivers international education under an internationally benchmarked accreditation framework.

Active rule:

- CIS accreditation may establish strong international-school-model/accreditation evidence;
- Edu Hub still applies the private/independent ownership scope gate separately;
- accreditation announcements are source evidence, not authorization to auto-create or auto-merge canonical identities;
- recent/current accreditation evidence is preferred;
- old accreditation announcements without current revalidation remain historical evidence and must not silently be treated as current accreditation.

## Cognia

Cognia is a recognized accreditation source. Cognia accreditation is useful for accreditation evidence and American/international-school candidate discovery.

Active rule:

- Cognia accreditation does **not** by itself prove that an Egyptian institution fits Edu Hub's international-school scope;
- separately verify the international-school model and private/independent ownership;
- dated official Cognia milestone/current-status evidence may be retained with provenance;
- do not infer a curriculum, ownership model or active international-school classification from the Cognia name alone.

## Overture Maps

Use according to the applicable Overture dataset license and preserve required provenance/attribution. Geography/identity support does not establish international eligibility by itself.

## OpenStreetMap

Use subject to ODbL obligations. Keep OSM-derived data/attribution traceable and do not treat OSM as an accreditation or international-eligibility source.

## Wikimedia Commons

Asset-by-asset rights review is required. Store creator, license, license URL and attribution. A search result is only a media candidate until both identity match and rights are reviewed.

## Official institution websites

Primary source for institution-controlled facts such as current contacts, campus details, admissions, fees, curriculum descriptions and programmes. Website publication does not automatically grant image/content republication rights; factual extraction and media reuse are separate issues.

Official institution-origin Arabic and English names may be retained as localization evidence. Historical official names must retain their source date/recency state and should be revalidated before being treated as current where practical.

## Commercial directories generally

Before adding another commercial directory to an automated acquisition pipeline:

1. inspect its current terms/robots/access constraints;
2. record the intended role and storage policy;
3. use it only for discovery if systematic reuse is not clearly permitted;
4. never allow a commercial directory alone to establish eligibility/accreditation;
5. never assume that visible images can be republished.
