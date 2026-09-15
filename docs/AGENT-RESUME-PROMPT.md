# Edu Hub — Reusable Agent Resume Prompt

Copy/paste the prompt below into a new agent/chat whenever continuity is lost.

---

Work from the `edu-data-2-international-registry` branch of the `admonkstudio/edu-hub` repository.

This is a continuation of the active Edu Hub database-first project. Do **not** restart the project from historical chat context and do **not** jump ahead to frontend/CMS work.

Before making any changes:

1. Read the root `AGENTS.md` and follow its authority order.
2. Read `docs/PROJECT-STATUS.md`.
3. Read `docs/PROJECT-DECISIONS.md`.
4. Read `docs/EDU-DATA-2-CONTINUATION.md` in full. Treat it as the durable continuation cursor for the active EDU-DATA-2 milestone.
5. Read GitHub Issue #8: `EDU-DATA-2 Continuation Roadmap — D2.1 → D2.7` and use its checklist as the visible tracking roadmap.
6. Read `tools/data-acquisition/international/DATASET-LAYERS.md`.
7. Inspect the actual current branch implementation, relevant builders/seeds/workflows, and the latest accepted GitHub Actions runs before assuming any count from an old conversation.

Important continuation rule:

- Resume from the **exact next cursor** recorded in `docs/EDU-DATA-2-CONTINUATION.md` and Issue #8.
- Do not redo already accepted source acquisition/review work unless current evidence shows a regression or source change.
- If historical chat text conflicts with a newer verified repository checkpoint, trust the current explicit user instruction plus the repository's latest verified continuation/status state.

Current architecture/data rules remain binding:

- source/discovery rows do not automatically become canonical institutions;
- source-row counts are never unique-institution counts;
- no fuzzy automatic identity merge;
- no unsupported international eligibility inference;
- British Council Partner status, Cognia presence, Overture/OSM, V7 and commercial directories do not independently establish eligibility;
- preserve campus/division/provider distinctions and lifecycle evidence;
- no Edarabia bulk scraping/storage/reproduction without permission;
- no raw/staging publication;
- no runtime/public frontend work before D2.7/database completion;
- no Supabase for Edu Hub;
- preserve EN/AR parity, provenance, portability, media rights and review state.

Proceed autonomously with the next D2 task. For research that depends on current sources, verify against current official/primary evidence. Commit deterministic evidence/review decisions, run the relevant CI, and do not call a checkpoint accepted until the validation is green.

After material accepted progress, update all continuity surfaces so another fresh agent can resume without this chat:

- `tools/data-acquisition/international/DATASET-LAYERS.md` if layer counts changed;
- `docs/PROJECT-STATUS.md`;
- `docs/PROJECT-DECISIONS.md` when decisions/contracts changed;
- `docs/EDU-DATA-2-CONTINUATION.md` with the new accepted run/counts and exact next cursor;
- GitHub Issue #8 checklist/status.

Then continue to the next unchecked task unless blocked by an external dependency that cannot be resolved from the repository or available tools.

---

The prompt intentionally does not hard-code the current row count. The canonical continuation file and Issue #8 should always hold the latest verified checkpoint.