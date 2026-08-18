# Edu Hub SEO Architecture

SEO is a core product constraint. The platform must deliberately decide which URLs exist, which are crawlable, and which are indexable.

## Core principles

- Database scale does not equal SEO scale.
- A stored institution record does not automatically deserve an indexable page.
- Arbitrary filter combinations must not create unrestricted indexable URLs.
- Search and AI visibility should come from useful, source-backed, internally connected information.
- Verify current search behavior against primary search-engine documentation before changing version-sensitive rules.

## Locale routing

Initial country/locale prefixes:

```text
/en-eg/
/ar-eg/
```

Use equivalent locale relationships with `hreflang` and correct canonicals.

Do not redirect solely based on inferred IP/language in a way that prevents crawlers/users from reaching alternate locales.

## Public route families

Conceptual route map:

```text
/{locale}/
/{locale}/nurseries/
/{locale}/schools/
/{locale}/universities/
/{locale}/institutes/

/{locale}/nursery/{slug}/
/{locale}/school/{slug}/
/{locale}/university/{slug}/
/{locale}/institute/{slug}/

/{locale}/locations/{slug}/
/{locale}/curricula/{slug}/
/{locale}/programs/{slug}/

/{locale}/guides/
/{locale}/guides/{slug}/
/{locale}/articles/
/{locale}/articles/{slug}/

/{locale}/compare/
```

Exact user-facing route labels/slugs may change during content/UX work, but the stable canonical entity concept must remain.

## Default indexability matrix

| Page type | Default policy |
|---|---|
| Homepage | Index |
| Main directory hub | Index |
| Institution profile | Conditional |
| Campus-specific page | Conditional |
| Governorate/location hub | Conditional/index when useful |
| Curriculum hub | Index when useful |
| Curated location + curriculum landing | Conditional |
| Arbitrary filters | Noindex / crawl-controlled |
| Internal search results | Noindex |
| Sort parameters | Noindex / crawl-controlled |
| Dynamic compare UI | Noindex |
| Editorial comparison article | Index |
| Candidate/incomplete entity | Noindex |
| Admin/control routes | Authenticated + noindex |
| Duplicate/merged entity | Redirect/canonical as appropriate |

## Index readiness

Build a deterministic index-readiness layer rather than manually relying on editors.

A profile should generally require:

- resolved entity identity
- valid classification
- useful geographic information where applicable
- authoritative/official source coverage
- meaningful unique content/data
- no unresolved duplicate
- no critical factual conflict
- correct locale relationship

A public profile can exist as `public_noindex` before it becomes `index_ready`.

Future `indexability` records may track source, content, freshness and uniqueness quality dimensions with explicit failure reasons.

## Programmatic SEO

Allowed pattern:

```text
real demand
+ sufficient inventory
+ meaningful unique page value
+ intentional editorial approval
→ indexable landing page
```

Rejected pattern:

```text
every filter combination
→ automatic page
→ automatic sitemap
```

Create a first-class `seo_landings` concept for approved combinations such as:

- schools in Cairo
- British schools in New Cairo
- universities in Egypt
- computer science programs/universities where enough structured data and value exist

## Filters and faceting

Users may combine many filters. Those combinations are product functionality, not automatically SEO pages.

Define canonical handling for query parameters and prevent crawling/indexation traps.

## Sitemap architecture

The sitemap must be database-driven for dynamic routes.

Use a sitemap index and segment by content class/volume, for example:

```text
/sitemap.xml
/sitemaps/schools-1.xml
/sitemaps/schools-2.xml
/sitemaps/nurseries-1.xml
/sitemaps/universities.xml
/sitemaps/institutes.xml
/sitemaps/locations.xml
/sitemaps/curricula.xml
/sitemaps/editorial-1.xml
```

Only index-ready canonical URLs belong in SEO sitemaps.

## Structured data

Generate JSON-LD from canonical database values and visible page content.

Candidate types include:

- `Organization` / `WebSite` for Edu Hub
- `EducationalOrganization`
- `School`
- `Preschool`
- `CollegeOrUniversity`
- `Article`
- `BreadcrumbList`

Do not fabricate ratings, prices, reviews, accreditations, or other structured facts.

## Internal linking

Directory and editorial content should form a knowledge graph.

Examples:

- curriculum guide → curriculum hub → matching schools
- institution → location page → nearby institutions
- university → academic units/programs → relevant guides
- fee/admission guide → relevant institution profiles

Internal links should reflect useful relationships, not keyword stuffing.

## Redirects

Maintain a redirect registry for renamed/merged routes. Do not casually change institution URLs once indexed.

## AI-search discoverability

Ensure public, indexable content remains accessible to relevant search crawlers according to the approved robots policy. Track AI referral/citation signals where measurable, but do not create a separate low-quality content strategy for AI systems.

## Phase 1 measurements

- submitted/discovered URLs
- crawled/indexed URLs
- impressions
- clicks
- queries
- CTR
- ranking/position where useful
- organic landing-page performance
- internal data quality/index-readiness counts
- AI referrals/citations where observable
