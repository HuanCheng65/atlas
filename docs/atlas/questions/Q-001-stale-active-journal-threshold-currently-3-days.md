---
id: Q-001
title: Stale active journal threshold (currently 3 days)
date: 2026-05-27
status: open
tags: [journal, atlas-compact]
related: [D-006]
source: bootstrap
source-journal: null
severity: low
answered-by: null
---

# Stale active journal threshold (currently 3 days)

## Why this matters

Active journal entries accumulate as parallel work happens (see D-006). Without
a "looks stale" signal, the journal index drifts into a long list of dead
entries. Choose too short a threshold and atlas-compact nags about work that
is genuinely paused but not abandoned; too long and the signal is useless.

## Context

Design.md currently states "3 days no update" as the heuristic for proposing
closure during atlas-compact. This value was picked by intuition during the
initial design and has not yet been validated against real usage.

## Investigation needed

- Dogfood through phase 2; record how often the 3-day threshold flags a
  genuinely stale entry vs. paused-but-active work.
- Consider whether the threshold should adapt to entry age or tag.
- Possibly resolve into a D-NNN once a defensible value is found.

Evidence: `docs/design.md` "Open design questions" → "Stale active entry threshold".
