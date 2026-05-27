---
id: Q-002
title: Topic auto-promotion heuristic for atlas-compact
date: 2026-05-27
status: open
tags: [atlas-compact, topics]
related: []
source: bootstrap
source-journal: null
severity: medium
answered-by: null
---

# Topic auto-promotion heuristic for atlas-compact

## Why this matters

Topics are free-form distilled knowledge notes that emerge from journal
patterns. They are *never* bootstrapped — they only appear when several
journal entries warrant distillation. Without a working heuristic for "this
cluster should be sealed into a topic", atlas-compact either nags too often
or misses the moment, and topics never form organically.

## Context

Candidate heuristics considered so far:

- Shared tag across N consecutive entries within K days.
- Cross-references to a tag exceeding a threshold count.
- LLM-judged clustering of entry titles/bodies.

None has been tried in practice yet — atlas-compact itself is still to be
designed and built.

## Investigation needed

- Wait for a meaningful journal corpus (after phase-2 dogfooding).
- Try the simplest heuristic (tag co-occurrence) first; measure precision /
  recall against manual classification.
- Decide whether to keep the heuristic deterministic or let an LLM make the call.

Evidence: `docs/design.md` "Open design questions" → "Topic auto-promotion heuristic".
