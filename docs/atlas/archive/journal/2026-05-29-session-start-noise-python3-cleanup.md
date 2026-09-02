---
date: 2026-05-29
slug: session-start-noise-python3-cleanup
project: Kairos
tags: [skills, dx, session-start]
status: closed
opened: 2026-05-29 17:58
closed: 2026-05-29 18:00
verification-result: passed
related: []
---

# Session start noise python3 cleanup

## Context

Two pieces of UX feedback on atlas session-start behavior. (1) The opening setup calls (using-atlas, then atlas-orient) emit chatty preamble ("I'll start by invoking...", "I'll first orient...") — the user wants the Skill call to be the first action with no acknowledgment text. (2) Several SKILL.md docs and bin/atlas-init invoke scripts via bare `python`, which doesn't exist on macOS (only python3), causing a command-not-found on first orient before retrying with python3. Fix: standardize all script invocations on python3; tighten no-preamble wording in the durable, version-controlled surfaces (CLAUDE.md + using-atlas body) and the local SessionStart hook.

## Work log

### 2026-05-29 17:59
python3 standardization: replaced bare `python` → `python3` in 7 sites (bin/atlas-init:86, atlas-entity/atlas-bootstrap/atlas-orient/grill-me SKILL.md). Repo-wide grep now clean; orient.py already runs under python3.

No-preamble wording added in three surfaces: CLAUDE.md managed block + its source in bin/atlas-init (governs the first using-atlas call), and using-atlas SKILL.md step 1 + anti-patterns (governs the atlas-orient call). Scoped to the setup sequence only — Layer-2 post-hoc announces remain allowed. Also tightened the local SessionStart hook in ~/.claude/settings.json (local-only, not installed by the framework — flagged to user).

The preamble fix is prompt-engineering: only observable next session start, not verifiable this session.

## Close

Standardized all script invocations on python3 (7 sites, grep clean). Added scoped no-preamble instructions to CLAUDE.md + bin/atlas-init, using-atlas body, and the local SessionStart hook. python3 fix verified; preamble fix is instruction-only (observable next session).
