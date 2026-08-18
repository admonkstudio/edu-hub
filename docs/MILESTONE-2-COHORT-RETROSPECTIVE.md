# Milestone 2 Real-Institution Cohort Retrospective

## Status

Milestone 2 remains in progress. Hosted architecture validation is complete; the real-institution cohort and resulting corrections are the remaining product-development gate before Milestone 3.

The cohort runs in three controlled stages:

1. Five-institution nursery pilot
2. Ten-school batch after pilot review
3. Ten higher-education institutions after the second review, with up to five additional cases only where structural coverage requires them

All records must be researched and entered through Control. SQL and migration seeding are prohibited for cohort data. Assertions remain unreviewed until a human reviewer acts; AI assistance may not accept evidence, resolve real conflicts, or approve publication/index readiness.

## Measurement method

Timing starts when source discovery begins and ends when the researcher has entered the record, sources, assertions, conflicts, tasks, and current completeness/readiness result. Reviewer time is tracked separately.

For every institution record:

| Field | Measurement |
| --- | --- |
| Research time | Active researcher minutes |
| Review time | Active human reviewer minutes |
| Sources | Count and source types used |
| Primary-source quality | Strong, mixed, weak, or unavailable, with rationale |
| Unestablished fields | Required or useful facts left unknown |
| Conflicting fields | Field keys and source pairs in conflict |
| Taxonomy gaps | Missing, ambiguous, or incorrectly scoped vocabulary |
| Relationship gaps | Missing entity/campus/provider relationships |
| Control friction | Extra steps, unclear controls, failed validations, or inaccessible state |
| Localization | Arabic/English naming or content inconsistencies |
| Completeness | Rule result and unrealistic requirements |
| Readiness | Rule result and reviewer-dependent blockers |
| Reviewer interventions | Decisions requiring human authority |
| Workarounds | Any action outside the intended workflow |

## Finding classifications

- `MODEL` — database/domain structure is wrong or insufficient
- `TAXONOMY` — controlled vocabulary is missing, ambiguous, or incorrectly scoped
- `WORKFLOW` — Control makes correct research unnecessarily difficult
- `SOURCE` — the research protocol does not adequately handle source reality
- `READINESS` — completeness or indexability rules are unrealistic
- `UI` — the model works but Control represents it poorly
- `NO CHANGE` — reality is awkward but the current architecture handles it correctly

## Stage 1 — Five-nursery pilot

The candidates are provisional until official identity and source ownership are verified. Selection optimizes structural diversity, not prominence.

| Slot | Candidate | Intended stress case | Status | Research min | Review min | Sources | Primary-source quality | Completeness | Readiness |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| N1 | Small Talk Nursery | Independent nursery | Blocked at creation |  |  | 4 | Mixed | Not evaluated | Not evaluated |
| N2 | Fairytales International Academy | Multi-campus nursery | Candidate |  |  |  |  |  |  |
| N3 | First Class Nursery | Bilingual/international curriculum claims | Candidate |  |  |  |  |  |  |
| N4 | Themar Nursery | Weak official-source presence | Candidate |  |  |  |  |  |  |
| N5 | Heritage Nursery International | Ambiguous relationship with a larger school | Candidate |  |  |  |  |  |  |

### Institution notes

Add one subsection per institution while research is in progress. Record observations as they happen; do not reconstruct duration or friction afterward.

#### N1 — Small Talk Nursery

Status: source discovery complete; Control entry blocked before persistence.

Official sources identified:

- `https://www.smalltalknursery.com/` — official identity and founding story (2004)
- `https://www.smalltalknursery.com/contact-us.html` — Maadi address and contact details
- `https://www.smalltalknursery.com/mission--philosophy.html` — play-based approach and English/optional Arabic language context
- `https://www.smalltalknursery.com/information-pack` — British-government-recommended early-years curriculum claim

Current unresolved facts:

- No institution-owned Arabic spelling was found. Secondary Arabic directories use `حضانة سمول توك`, but this must not become canonical without reviewer approval.
- Legal ownership and licensing status were not established from the institution website.
- The current model has no explicit nursery age-range field.

Early friction observations:

| Classification | Observation | Action at pilot review |
| --- | --- | --- |
| `WORKFLOW` | Institution creation requires both localized names and slugs even when an official Arabic name is not established. | Measure recurrence across all five nurseries; evaluate an explicit pending-localization state. |
| `MODEL` | Field assertions currently cover only website, founding year, curricula, and education levels. They cannot directly evidence localized names, campus addresses, languages, contacts, ownership, or provider relationships. | Count blocked evidence fields across the pilot before changing assertion scope. |
| `UI` | The source selector is a global list with no institution association or filtering. | Measure selection friction as sources accumulate. |
| `TAXONOMY` | Nursery age ranges/program stages are not represented as structured values. | Compare age-range patterns across all five records before deciding whether this belongs in taxonomy or a nursery-specific model. |

Verified staging entry result (2026-08-18):

- The existing researcher identity was used with its role and status unchanged.
- Control was left at its default `draft` publication status and `candidate` data status.
- English name and slug were entered; Arabic name and slug were intentionally left empty because no institution-owned Arabic naming source was found.
- Browser validation focused the required Arabic-name field and prevented submission.
- A direct post-attempt database check returned zero institution records named `Small Talk Nursery`.
- No placeholder Arabic localization, direct SQL insert, reviewer action, assertion acceptance, conflict resolution, or readiness advancement was used.

This is a blocking `WORKFLOW` finding and a related `READINESS` design question: the intended researcher workflow cannot represent a real candidate whose Arabic localization is explicitly pending. N1 remains uncreated until the pilot decides how pending localization should be modeled and validated.

## Pilot review gate

Do not begin the ten-school batch until the five nursery records have been reviewed for:

- repeated field conflicts
- source types that proved reliable or unreliable
- missing taxonomy values and relationships
- required unsupported workarounds
- assertion granularity
- completeness/readiness realism
- fields that must never be AI-updated automatically
- nursery-specific model requirements
- median and range of research/reviewer time

Every finding must receive one classification and an explicit action or `NO CHANGE` rationale.

## Stage 2 — Ten-school batch

Not started. Select only after the nursery pilot review. Required structural coverage: independent private, school group, multi-campus, British, American, IB, mixed curriculum, national/language, government/special model, and difficult/conflicting-source case.

## Stage 3 — Higher-education batch

Not started. Select only after the school-batch review. Required structural coverage: public, private, national, technological, foreign branch, higher institute, multi-campus, complex faculty structure, bilingual-source inconsistency, and weak/incomplete official-source cases.

## Final Milestone 2 exit review

Milestone 2 closes only after the cohort is complete, findings are classified, approved corrections are implemented, affected tests and the full regression suite pass, PR #4 is updated and marked ready for review, and Issue #3 is closed after merge.
