# Edu Hub Research Protocol

## Purpose

This protocol governs human research and any future assisted research before a fact becomes canonical. It applies to every real institution record. It does not authorize automated publication.

## Core rule

> A canonical fact must be explainable through a field-level assertion, a retained source, an accountable actor, and a review decision appropriate to its risk.

Unknown information is preferable to an unsupported claim. Conflicting evidence must remain visible until a reviewer resolves it.

## Source priority

Use the strongest source that directly supports the specific field:

1. Government ministry, regulator, or official legal register
2. Official institution website or document
3. Accreditation or curriculum authority
4. Verified official institutional social account
5. Trusted authoritative publication
6. Secondary source

Authority is a priority signal, not automatic truth. A current, field-specific lower-ranked source may be more useful than an outdated higher-ranked page. Record both when they disagree.

## What counts as official

A source is official only when its ownership or publication authority can be reasonably established. Domain appearance alone is insufficient. Researchers should check the publisher identity, page context, document issuer, dates, and links from known official properties.

Official social posts may support time-sensitive announcements but should not silently supersede durable regulator or institution records. Search snippets, scraped directories, AI answers, and unattributed reposts are not official sources.

## Field-level assertions

Attach evidence to the smallest stable fact that can be reviewed independently, such as:

- `official_website_url`
- `founded_year`
- `curricula`
- `education_levels`
- campus address
- accreditation relationship
- localized name

Do not use one generic “institution source” to justify unrelated fields. Store the observed value, observation date, source, confidence, and locale where relevant.

## Missing information

Do not invent a value, infer absence from silence, or use filler text. Record the field as unknown in workflow notes and create a verification task when the field is required. “Not available,” “not applicable,” and “not found” are distinct conclusions and require reviewer-approved conventions before becoming canonical display values.

## Outdated sources and freshness

Record the observation and retrieval dates. An outdated source may remain valid for stable facts but should not be treated as current evidence for changeable facts. Apply the configured freshness policy and create a refresh task when evidence is due, stale, or seasonally inappropriate.

Never overwrite historical evidence merely because a newer source exists. Supersede the assertion and retain both observations.

## Conflicts

When two credible sources disagree:

1. Preserve both assertions.
2. Mark the field as conflicting.
3. Create or link a conflict-resolution task.
4. Check publication dates, validity periods, entity/campus identity, and source authority.
5. Have an authorized reviewer record the resolution and rationale.
6. Change the canonical value only through an audited transactional command.

Last-write-wins is prohibited.

## Acceptance and reviewer approval

Researchers and editors may create unreviewed assertions. Reviewers, admins, or super administrators may accept, reject, or supersede them.

Reviewer approval is required for:

- conflicting evidence
- publication or index-readiness decisions
- accreditation and regulatory claims
- material identity changes
- merges/duplicates
- a source being treated as explicitly unavailable
- any exceptional departure from this protocol

An assertion may be accepted only when its source directly supports the field, the entity/campus identity is clear, the value format is valid, the observation is sufficiently current, and no unresolved stronger contradiction remains.

## Arabic and English naming

Arabic and English are independent editorial records tied to the same entity.

- Prefer the institution’s own official spelling in each language.
- Preserve meaningful official alternatives separately.
- Do not mechanically transliterate when an official localized name exists.
- Do not machine-translate legal names, accreditations, or claims without review.
- Keep Arabic text RTL and preserve canonical display spelling; search normalization belongs to search processing.
- A useful English record does not make the Arabic record complete, or vice versa.

## Publication readiness


### `public_noindex`

An institution may be publicly visible but non-indexable only after it has, where applicable:

- canonical name and institution type
- governorate and at least one active campus/address
- at least one accepted official or authoritative assertion
- education levels
- official website/contact or a reviewed explicit unavailable state
- no critical unresolved identity conflict

### `index_ready`

Index readiness additionally requires:

- meaningful reviewed English and Arabic content
- source-backed key facts
- relevant curriculum or education model
- no critical open conflict
- no critical required field that is stale or unknown
- useful unique information beyond a thin database row
- explicit reviewer approval

Database existence never implies public visibility or indexability.

## Snapshot and copyright restraint

Record URL, retrieval time, content hash, and the minimum extracted metadata needed for verification. Do not archive entire websites by default. Retain screenshots or documents only when lawful, necessary, and stored privately with deliberate access control. Never capture credentials, tokens, private correspondence, or unnecessary personal data.

## Research completion checklist

- The correct institution and campus were identified.
- Required facts are supported or explicitly unresolved.
- Assertions are field-level and use the strongest practical sources.
- Observation/retrieval dates are recorded.
- Conflicts and outdated evidence are preserved.
- Arabic and English records were reviewed independently.
- Required reviewer decisions are complete.
- Freshness and research tasks reflect remaining work.
- Publication/indexability state matches the completeness evaluation.

## AI boundary

AI may not autonomously accept assertions, resolve conflicts, alter canonical facts, or publish records in Milestone 2. Future assistance must follow this protocol and remain attributable to a human-reviewed workflow.
