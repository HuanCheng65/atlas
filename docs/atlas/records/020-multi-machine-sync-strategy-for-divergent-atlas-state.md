---
id: 20
title: Multi-machine sync strategy for divergent atlas state
date: 2026-05-27
type: question
tags: [sync, journal]
---

# Multi-machine sync strategy for divergent atlas state

## Why this matters

Atlas state lives in the project's git repo (see [[001-plain-text-git-as-the-data-layer]]), so multi-machine
sync is, in principle, normal git. In practice, two machines that worked
in parallel produce divergent journal entries, possibly distinct entity IDs
([[013-event-driven-skill-activation-not-session-phase-driven]] created on both machines), and `_index.md` conflicts. Manual
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
