# EDU-DATA-2 dataset layers

The international registry deliberately keeps source/evidence, identity, campus, division and publication layers separate. Counts in this document are never interchangeable with unique-institution counts.

## Foundational and historical layers

`build_authoritative_seed.py` preserves the deterministic **96-row** foundational source layer from IB, UK DfE BSO, French homologation, German KMK, SCU foreign branches and AUC/MSCHE evidence.

Reviewed CIS/Cognia milestone evidence expands the independently reproducible historical strong-source layer to **106 rows**. Its four Cognia milestone rows remain provenance but are superseded by the complete current Cognia registry for current-universe counting only.

## British Council discovery layer

Seven checked-in September 2026 browser-review batches contain **226 Partner School source rows**: 12 have separate qualifying primary/recognized evidence and 214 remain supporting candidates. Partner School status itself grants no international eligibility and no source row creates or merges a canonical identity.

## Complete Cognia Egypt registry

Accepted Cognia run `34977754806` extracted **256 official Egypt registry rows** across 11 result pages. Two duplicate normalized-name groups remain separate source evidence. The four historical Cognia milestone rows are deterministically superseded for current counting, yielding **252 additional current Cognia rows** beyond the older subset. Cognia presence alone does not grant eligibility.

## Canadian offshore-school authorization layer

The current Canadian family contains **6 authorized Egypt source rows** across British Columbia, Manitoba, New Brunswick, Ontario and Prince Edward Island. Cross-source overlap and provider/campus topology remain D2.2 review work.

## German Schools Abroad layer

The current ZfA directory contributes **7 Egypt DAS source rows**. DAS membership is distinct from current credential/exam authorization. Deutsche Schule Hurghada remains current DAS evidence while the checked KMK Sek-I lifecycle states the exam was last conducted in **2024/2025** and does not assert a later authorization.

## Substantive international higher-education review layer

The 2026-09-15 higher-education review adds **5 explicitly qualified source/evidence rows**: GIU, GUC, UFE, BUE and AASTMT. Eligibility rests on substantive binational/intergovernmental/transnational/international-organizational status supported by current evidence; Egyptian legal form is not by itself decisive, while foreign branding/partnership/validation/dual degree alone is insufficient.

These are source/evidence additions, not a claim of five new unique canonical institutions.

## Mansoura College provider/school topology review

The accepted 2026-09-15 Mansoura review establishes a provider/campus umbrella with four school units without materializing that umbrella as a canonical institution.

- `Mansoura College Language School` — national, provider context only.
- `Modern Mansoura College Language School` — national, provider context only; the existing British Council row remains separate supporting provenance.
- `Mansoura College British School` — **eligible reviewed source/evidence row**, supported by current primary evidence plus Pearson centre `92720` lifecycle evidence.
- `Mansoura College 2 International American School` — **eligible reviewed source/evidence row**, supported by current primary evidence plus current recognized Cognia/ACT evidence; original Cognia provenance remains separate.

The Overture row `Mansoura College International Schools` is a reviewed provider-umbrella alias, not a separate institution. Overture, Cognia and British Council Partner status grant no eligibility by themselves.

Review contract: `tools/data-acquisition/international/seeds/mansoura-college-topology-review-2026-09-15.json`.

## Current expanded D2.1 source/evidence universe

Accepted `EDU-DATA-2 D2.1 Universe Checkpoint` run **`35024492612`** at head `e1c554e61c9f9fc0c8185182a37a33f13ab78ce4` proves:

- **604 total source/evidence rows**;
- **135 eligible source/evidence rows**;
- **466 supporting candidates**;
- **3 excluded source rows**;
- 226 British Council rows;
- 256 current Cognia registry rows;
- 6 Canadian authorized offshore-school rows;
- 7 current ZfA German Schools Abroad rows;
- 5 reviewed substantive-international higher-education rows;
- 2 reviewed eligible Mansoura College international-school rows.

`604` is **not** a unique-institution count. A source row may later reconcile to an institution, campus, division, provider/group, cross-source overlap, lifecycle evidence or an out-of-scope entity.

The checkpoint performs zero fuzzy matching, zero automatic identity merges, zero canonical institution creation, zero runtime database mutation and zero public projection.

## Overture supporting discovery and gap review

Current Overture Places release: `2026-08-19.0`. Overture remains supporting discovery/geography evidence only.

Current Egypt-filtered acquisition:

- 1,121 rectangular-bbox candidates;
- 79 non-Egypt rows rejected using Overture address-country evidence;
- **1,042 Egypt-only supporting rows**;
- 42 duplicate normalized-name groups retained.

Against the **604-row** universe, deterministic exact normalized-name comparison remains:

- **141 exact overlap rows**;
- **901 unmatched supporting rows**;
- **865 unmatched normalized names**;
- **266 high-signal pre-university rows**;
- **70 higher-education review rows**;
- **565 lower-priority supporting rows**.

### High-signal school review

Six checked-in school-review batches now cover **64 of the 266** high-signal pre-university rows:

- **62 resolved/explained** as existing authoritative coverage, explicit source aliases, or provider/division cases requiring D2.2 topology review;
- **2 reviewed-but-unresolved** supporting leads;
- **202 high-signal rows remain unreviewed**;
- **204 rows remain outstanding** in the school-review artifact.

The two reviewed unresolved rows remain `Kada Modern British School` and `M.S.G International British School`.

Batch 6 explicitly reviewed AlMaaly International School, Sun of Knowledge British International School, British Modern School - BMS, Lycée International Balzac, International Schools of Kenana, Norwich International College - HR, Future International Schools Sadat City Branch, Nordic international school in Cairo, and British City College - IGCSE. Kenana, Future Sadat and British City remain provider/division/branch topology work rather than flattened identities. Lycée International Balzac resolves through the current French homologation family. Cognia and British Council Partner status remain supporting evidence only and grant no eligibility.

### Higher-education review — complete

The full **70-row post-overlay Overture higher-ed queue is explicitly reviewed** and has **0 outstanding HE rows**: 14 existing eligible HE aliases/subunits; 21 out-of-scope Egyptian HE rows/subunits; 33 supporting-only ambiguous academy/training/language/institute leads; 1 EBIS school category error; and 1 Mansoura provider category error closed by the topology review above.

Overture grants zero eligibility, performs zero fuzzy matching and creates zero canonical identities.

## OSM diagnostic layer

OpenStreetMap remains a permitted supporting source, but all public Overpass mirrors were inaccessible from hosted GitHub Actions across the 12-tile Egypt diagnostic. Accepted run `34997269459` records `environment_blocked_all_tiles`. Failed CI coverage is **diagnostic state, never negative evidence or a zero-candidate claim**.

## V7, Edarabia and primary-source gap checks

D2.1 remains open for:

- continued explicit review of the **204 outstanding high-signal school rows** in small deterministic batches;
- read-only comparison against the owned **24,916-row V7** archive, with useful unmatched leads re-sourced from current permitted evidence before use;
- controlled Edarabia reference-only discovery under `docs/SOURCE-USAGE-POLICY.md`;
- institution/operator primary-source exhaustion for remaining likely gaps and topology ambiguity.

## Canonical boundary

No layer may silently collapse source rows into canonical institutions. Institution, provider, campus, division and parent/branch relationships are created only through explicit reviewed D2.2 decisions. Counts for source rows, reviewed identities, memberships, campuses and divisions remain separate CI contracts.

The canonical project status, decision log, continuation file and GitHub Issue #8 are the source of truth for the accepted checkpoint and exact next cursor.
