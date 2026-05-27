---
id: Q-003
title: Multi-machine sync strategy for divergent atlas state
date: 2026-05-27
status: open
tags: [sync, journal]
related: [D-001]
source: bootstrap
source-journal: null
severity: medium
answered-by: null
---

# Multi-machine sync strategy for divergent atlas state

## Why this matters

Atlas state lives in the project's git repo (see D-001), so multi-machine
sync is, in principle, normal git. In practice, two machines that worked
in parallel produce divergent journal entries, possibly distinct entity IDs
(D-007 created on both machines), and `_index.md` conflicts. Manual
resolution is fine occasionally but tedious as a default.

## Context

Likely friction points:

- ID collisions when both machines `new.py` an entity simultaneously.
- `_index.md` files are derived but committed — they collide on merge.
- Journal entries are independent files, so they usually merge cleanly.

No multi-machine scenario has been encountered yet; this is anticipatory.

## Investigation needed

- Wait until a real multi-machine workflow appears.
- Possible mitigations: gitignore `_index.md` and always regenerate; lock
  entity ID assignment behind a script that fetches latest before allocating;
  switch IDs to timestamps or hashes to make collisions impossible.

Evidence: `docs/design.md` "Open design questions" → "Multi-machine sync"; also
`_index.md` git-tracking trade-off in the same section.
