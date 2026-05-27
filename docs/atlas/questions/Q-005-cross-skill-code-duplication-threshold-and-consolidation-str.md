---
id: Q-005
title: Cross-skill code duplication threshold and consolidation strategy
date: 2026-05-27
status: open
tags: [skills, refactor]
related: [D-009]
source: bootstrap
source-journal: null
severity: low
answered-by: null
---

# Cross-skill code duplication threshold and consolidation strategy

## Why this matters

Each skill ships its own `scripts/` to stay self-contained (D-009). Some
helpers (frontmatter parsing, path discovery) already appear in more than
one skill. Self-containment makes each skill movable and installable on its
own; DRY would reduce maintenance cost but couple skills to a shared library.
At some point duplication tips from "fine" into "painful".

## Context

Current state:

- `atlas-entity/scripts/_lib.py` has frontmatter parsing.
- Future skills (atlas-log, atlas-compact) will need the same primitives.

Open question: at what point do we extract a shared library, and where does
it live? Options: a sibling top-level `lib/` dir; a Python package installed
alongside skills; per-skill duplication tolerated indefinitely.

## Investigation needed

- Wait until phase 2 skills are written and duplication is concrete.
- Compare the diff between sibling `_lib.py` files to see if they actually drift.
- Decide based on real friction, not anticipated friction.

Evidence: `docs/design.md` "Open design questions" → "Cross-skill code sharing".
