# EDU-DATA-2 dataset layers

The international registry deliberately maintains separate evidence layers until identity review is complete.

## Foundational authoritative seed

`build_authoritative_seed.py` rebuilds a deterministic source-shaped evidence set from the checked-in IB, UK DfE BSO, French homologation, German KMK, SCU foreign-branch and AUC/MSCHE snapshots. At the 2026-09-15 checkpoint this layer contains 96 source rows.

The 96 rows are evidence/source records. They are not a claim of 96 unique institutions.

## Strong-source expansion

Scope-reviewed CIS/Cognia accreditation evidence and later reviewed source packages expand the reproducible strong/authoritative research universe without rewriting the foundational seed. At the current checkpoint the classified strong-source universe contains 106 source rows.

## Supporting discovery expansion

British Council Partner Schools, controlled commercial-directory reference discovery, Overture/OSM, the owned V7 archive and institution/operator sites are supporting discovery inputs. They may discover identities, campuses or missing facts, but do not independently establish eligibility unless the source-specific scope rule allows it.

At the current checkpoint, the expanded discovery universe contains 316 source/lead rows, including 210 British Council discovery rows. These counts describe evidence/discovery rows, not unique institutions or campuses.

## Canonical boundary

No layer may silently collapse source rows into canonical institutions. Institution, provider, campus, division and parent/branch relationships are created only by explicit reviewed identity/topology decisions. Counts for source rows, reviewed identities, memberships and campuses therefore remain separate CI contracts.

The canonical project status and decision log are the source of truth for the current checkpoint and accepted CI run IDs.
