# EDU-DATA-2 dataset layers

The international registry deliberately maintains separate evidence layers until identity review is complete. Counts in this document describe source/evidence/review layers; they are never interchangeable with unique-institution, campus or division counts.

## Foundational authoritative seed

`build_authoritative_seed.py` rebuilds a deterministic source-shaped evidence set from the checked-in IB, UK DfE BSO, French homologation, German KMK, SCU foreign-branch and AUC/MSCHE snapshots. At the 2026-09-15 checkpoint this layer contains **96 source rows**.

The 96 rows are evidence/source records. They are not a claim of 96 unique institutions.

## Historical classified strong-source layer

Scope-reviewed CIS/Cognia milestone evidence and later reviewed source packages expand the reproducible strong/authoritative research universe without rewriting the foundational seed. The historical classified strong-source universe contains **106 source rows**.

This 106-row layer remains independently reproducible for provenance and regression checks. Its four Cognia milestone rows are retained as historical source evidence even though the complete current Cognia registry now supersedes that four-row subset for the current D2.1 universe count.

## British Council supporting discovery layer

The September 2026 British Council Partner Schools source is supporting discovery/contact evidence only. Seven checked-in browser-reviewed batches now contain **226 source rows**.

Separate primary/recognized-source review currently qualifies 12 of those rows; 214 remain supporting candidates. Partner School status itself grants no international eligibility and creates no canonical identity.

## Complete Cognia Egypt registry layer

The official Cognia Accreditation Registry was queried through its public registry UI and completely extracted for country `Egypt` in accepted run `34977754806`:

- **256 official Egypt registry rows**;
- 11 result pages;
- 2 duplicate normalized-name groups retained as source rows;
- zero automatic identity merges or eligibility decisions.

The four earlier Cognia milestone institutions occur as exact normalized-name matches in the complete registry. For the **current universe count only**, those four milestone rows are superseded by their registry rows while the already-reviewed scope decisions are carried forward through explicit same-publisher/exact-name source-family supersession. The other **252 Cognia registry rows remain supporting candidates** until separately qualified.

The historical milestone evidence is not deleted and remains provenance.

## Current expanded D2.1 source/lead universe

Accepted `EDU-DATA-2 D2.1 Universe Checkpoint` run `34995646409` rebuilds the current research universe from source and proves the following checkpoint:

- **584 total source/lead rows**;
- **115 eligible source/lead rows**;
- **466 supporting candidates**;
- **3 excluded source rows**;
- **226 British Council rows**;
- **256 current Cognia registry rows**;
- 4 Cognia milestone rows superseded for current counting, yielding 252 net new Cognia source rows beyond the earlier subset.

`584` is not a unique-institution count. A source row may later resolve to an institution, campus, division, provider/group, an overlap with another source, or an out-of-scope entity.

## Supporting gap-check sources

Overture/OSM, controlled Edarabia reference-only discovery, the owned V7 archive and institution/operator sites are supporting D2.1 gap-discovery inputs. They may discover candidate identities, aliases, campuses or geography, but they do not independently establish eligibility unless a separate permitted source-specific review does so.

D2.1 remains open while those gap checks are completed.

## Canonical boundary

No layer may silently collapse source rows into canonical institutions. Institution, provider, campus, division and parent/branch relationships are created only by explicit reviewed identity/topology decisions. Counts for source rows, reviewed identities, memberships and campuses therefore remain separate CI contracts.

The canonical project status and decision log are the source of truth for the current checkpoint and accepted CI run IDs.
