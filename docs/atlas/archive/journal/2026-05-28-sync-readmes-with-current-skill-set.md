---
date: 2026-05-28
slug: sync-readmes-with-current-skill-set
project: Atlas
tags: [docs, housekeeping]
status: closed
opened: 2026-05-28 02:51
closed: 2026-05-28 02:52
verification-result: passed
related: []
---

# Sync readmes with current skill set

## Context

Sync the three README files (root `README.md`, `docs/atlas/README.md`, `templates/README.md`) with the actual current state: 6 active skills (using-atlas, atlas-orient, atlas-log, atlas-entity, grill-me, atlas-bootstrap) instead of the old "atlas-entity + TODO atlas-session-start/end" listing, and journal lifecycle ownership now lives in atlas-log rather than the never-built atlas-session-end. Mechanical doc-reality alignment, no design changes.

## Work log

## Close

**Outcome**: Three README files updated to reflect the actual current state — 6 active skills listed (using-atlas, atlas-orient, atlas-log, atlas-entity, grill-me, atlas-bootstrap), journal lifecycle correctly attributed to atlas-log instead of the never-built atlas-session-end, and the project-facing READMEs now mention the using-atlas / CLAUDE.md auto-load mechanism.

**Verification result**: spot-checked `ls skills/` against the root README's "Skills shipped" table — all 6 present skills are listed as `ready`, `atlas-compact` remains correctly marked `planned`. The two project-facing READMEs (`docs/atlas/README.md` and `templates/README.md`) are now byte-identical (templates/README.md is what atlas-init copies into new projects, so they must stay in sync).

**Keepers (finalized)**:
- Updated root `README.md` with full skill list and one-line each
- Updated `docs/atlas/README.md` and `templates/README.md` (identical content; the latter is the init template)

**Throwaways (deleted)**:
- "atlas-session-start (TODO phase 2)" / "atlas-session-end (TODO phase 2)" references throughout — those skill names never shipped; the functionality lives under different names (`using-atlas`, `atlas-orient`, `atlas-log`)

**Spawned entities**:
- None.

**Follow-up surfaced (not actioned):** `docs/atlas/ROADMAP.md` still describes the current milestone as "Phase 2: ship atlas-session-start / atlas-session-end / atlas-compact / port grill-me" — three of those four are either shipped under different names (session-start/end → using-atlas + atlas-orient + atlas-log) or shipped as-is (grill-me). The roadmap likely needs a redefinition pass, but that's a milestone decision, not a doc-sync, so leaving for the user.
