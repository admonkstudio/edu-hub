# EDU-DATA-2 dataset layers

The international registry deliberately maintains separate evidence layers until identity review is complete. Counts in this document describe source/evidence/review layers; they are never interchangeable with unique-institution, campus or division counts.

## Foundational authoritative seed

`build_authoritative_seed.py` rebuilds the deterministic source-shaped base from checked-in IB, UK DfE BSO, French homologation, German KMK, SCU foreign-branch and AUC/MSCHE evidence. The foundational layer remains **96 source rows** and is preserved as historical provenance.

## Historical classified strong-source layer

Reviewed CIS/Cognia milestone evidence expands the reproducible historical strong-source research layer to **106 source rows**. This layer remains independently reproducible. Its four Cognia milestone rows are preserved as historical evidence but are superseded by the complete current Cognia registry for current-universe counting only.

## British Council supporting discovery layer

Seven checked-in September 2026 browser-review batches contain **226 British Council Partner School source rows**.

- 12 have separate qualifying primary/recognized evidence;
- 214 remain supporting candidates;
- Partner School status itself grants no international eligibility;
- no source row creates a canonical identity or authorizes an automatic merge.

## Complete Cognia Egypt registry layer

Accepted Cognia run `34977754806` completely extracted the official Egypt registry:

- **256 official Egypt registry rows**;
- 11 result pages;
- 2 duplicate normalized-name groups retained as source evidence;
- four earlier Cognia milestone rows deterministically superseded for current-universe counting;
- **252 additional current Cognia source rows** beyond the milestone subset;
- zero automatic identity merges or eligibility decisions for those 252 rows.

## Canadian offshore-school authorization layer

The current Canadian offshore-school source family contains **6 authorized Egypt rows** across British Columbia, Manitoba, New Brunswick, Ontario and Prince Edward Island. These rows are supported by current CICIC/provincial authorization evidence and retain private/independent scope evidence.

The six rows are source evidence, not six newly claimed unique institutions. Known cross-source overlap, including Royal Canadian School Cairo, and BCCIS East/West topology remain D2.2 review work.

## German Schools Abroad layer

The current ZfA German Schools Abroad directory contains **7 Egypt DAS source rows**. Current DAS membership is treated as recognized German foreign-national/international-model evidence, but it is distinct from current examination/credential authorization.

The Hurghada row therefore preserves its KMK lifecycle explicitly: the Sek-I exam was last conducted in **2024/2025**, and no post-2024/2025 current Sek-I authorization is asserted. Cross-source overlap for the other DAS rows remains D2.2 identity review work.

## Current expanded D2.1 source/lead universe

Accepted `EDU-DATA-2 D2.1 Universe Checkpoint` run **`35001371492`** proves the current checkpoint:

- **597 total source/lead rows**;
- **128 eligible source/evidence rows**;
- **466 supporting candidates**;
- **3 excluded source rows**;
- **226 British Council rows**;
- **256 current Cognia registry rows**;
- **6 Canadian authorized offshore-school rows**;
- **7 current ZfA German Schools Abroad rows**.

`597` is not a unique-institution count. A source row may resolve to an institution, campus, division, provider/group, overlap with another source, lifecycle evidence, or an out-of-scope entity.

## Overture supporting discovery and gap-resolution layer

The official Overture Places `2026-08-19.0` release is supporting discovery/geography evidence only. The accepted Egypt-filtered acquisition contains:

- 1,121 rectangular-bbox candidates;
- 79 non-Egypt rows rejected using Overture's own address-country data;
- **1,042 Egypt-only supporting rows**;
- 42 duplicate normalized-name groups retained.

Against the current 597-row universe, deterministic exact-name comparison currently yields:

- **136 exact normalized-name overlap rows**;
- **906 unmatched supporting rows** / 869 unmatched normalized names;
- **266 high-signal pre-university rows**;
- **75 higher-education review rows**;
- **565 lower-priority supporting rows**.

Two explicit checked-in Overture review batches have reviewed **30 high-signal rows**:

- 28 are resolved from the unknown-gap queue as already-covered authoritative evidence, existing-source aliases, or existing provider/division cases requiring D2.2 topology review;
- 2 remain reviewed-but-unresolved supporting leads;
- 236 high-signal rows remain unreviewed;
- **238 high-signal rows remain outstanding in total**.

These review decisions are discovery triage only. They perform zero fuzzy merges, zero automatic universe additions, zero canonical identity creation and zero public projection.

## OSM diagnostic layer

OpenStreetMap remains a permitted supporting geography/identity source, but all public Overpass mirrors were inaccessible from the hosted GitHub Actions environment across the 12-tile Egypt diagnostic. The workflow records this as `environment_blocked_all_tiles` rather than treating failed access as zero OSM candidates.

OSM unavailability in CI is therefore **diagnostic state, never negative evidence**.

## V7, Edarabia and primary-source gap checks

D2.1 remains open for:

- read-only comparison against the owned 24,916-row V7 raw archive; unmatched legacy leads require current re-sourcing before use;
- controlled Edarabia reference-only discovery under the project source-use policy;
- continued institution/operator primary-source confirmation;
- remaining Overture high-signal and higher-education triage.

## Canonical boundary

No layer may silently collapse source rows into canonical institutions. Institution, provider, campus, division and parent/branch relationships are created only through explicit reviewed D2.2 decisions. Counts for source rows, reviewed identities, memberships, campuses and divisions remain separate CI contracts.

The canonical project status and decision log are the source of truth for accepted checkpoint run IDs and durable project rules.
