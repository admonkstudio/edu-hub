# EMIS Live Failure Evidence — 2026-09-14

Status: **SOURCE-SIDE LIVE ENUMERATION BLOCKER CONFIRMED**

Milestone: `EDU-DATA-1 / D1.3`

This note records the bounded Egypt-local evidence collected from the official Egyptian Schools Directory on 2026-09-14. It exists so the project does not repeatedly reverse-engineer or retry a source path that has already been exhausted without new evidence of source recovery.

## What was proven

The official root at `https://search.emis.gov.eg/` is reachable from an Egypt network and returns a valid ASP.NET form with the expected state fields including `__VIEWSTATE`, `__VIEWSTATEGENERATOR`, and `__EVENTVALIDATION`.

The live root exposes six school-category submit buttons. Fresh root state was obtained before each category submission, and each button was submitted through the root form rather than by guessing a direct URL.

Observed category results:

| Category | Live route | Result |
| --- | --- | --- |
| Government schools | `search_schgov.aspx` | HTTP 500 |
| Private schools | `search_schpriv.aspx` | HTTP 500 |
| Special Education | `search_schSpecialEdu.aspx` | HTTP 200 |
| Sports schools | `search_schSports.aspx` | HTTP 500 |
| Military schools | `search_schMilitary.aspx` | HTTP 500 |
| Experimental/language schools | `search_schLan.aspx` | HTTP 500 |

The Special Education route is therefore the only category that currently returns a search-form page. It exposes two dependent selects, governorate (`DDList_mud`) and stage (`DDList_stage`), and three non-placeholder school-type radio controls.

## Exhaustive bounded hydration result

Each of the three observed Special Education types was tested independently in a fresh session with fresh category navigation and fresh ASP.NET state:

1. `تربية فكرية`
2. `مكفوفين وضعاف بصر`
3. `صم وضعاف سمع`

For all three controls:

- the ASP.NET postback was accepted;
- the selected radio state was preserved in the response;
- the response returned HTTP 200;
- governorate remained empty;
- stage remained empty;
- the page displayed the ministry-side message `خطأ اثناء محاولة تحميل الصفحة`.

The final diagnostic summary recorded:

- `controls_discovered = 3`
- `controls_submitted = 3`
- `successful_hydration_pages = 3`
- `pages_with_populated_selects = 0`
- `populated_selects = 0`
- `pages_with_visible_errors = 3`
- `school_searches_submitted = 0`
- `result_pagination_followed = 0`
- `school_rows_enumerated = 0`

## Conclusion

The current blocker is not an unresolved client-side ASP.NET submission format. The root navigation contract and Special Education postback contract were both validated, while the ministry application failed to load the dependent data required to reach a school search.

The government route remains more severely blocked because valid root navigation currently ends in HTTP 500.

Therefore:

- do **not** repeat the same Special Education hydration diagnostic unless the source changes materially;
- do **not** build or run a government-school enumerator against the current route state;
- do **not** treat Special Education as evidence of government-school coverage;
- keep the official 62,690-school target as a coverage target only;
- pursue the official machine-readable MOE/EMIS export in parallel;
- use only a lightweight category health recheck to detect source recovery;
- if the government route becomes healthy, recapture the live government form before implementing a small bounded pilot.

## Safety boundary retained

No school-search button was submitted, no result pagination was followed, no school rows were enumerated, no `edu_core` records were mutated, and no public records were promoted while collecting this evidence.
