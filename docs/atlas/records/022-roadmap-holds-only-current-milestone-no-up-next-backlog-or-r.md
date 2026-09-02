---
id: 22
title: Roadmap holds only Current milestone — no Up next, Backlog, or Recently done
date: 2026-05-27
type: decision
tags: [roadmap, data-model, concurrency]
---

# Roadmap holds only Current milestone — no Up next, Backlog, or Recently done

## Context

`docs/atlas/ROADMAP.md` previously had four sections: Current milestone, Up
next, Backlog, Recently done. Auditing the file surfaced three problems:

1. **Backlog duplicated open questions.** "Multi-machine sync" repeated
   [[[[020-multi-machine-sync-strategy-for-divergent-atlas-state]]]]; "Topic-sealing flow" repeated [[[[015-topic-auto-promotion-heuristic-for-atlas-compact]]]]. Two sources of truth
   for the same item is the classic document-rot setup.
2. **Recently done duplicated derivable state.** It restated facts already
   captured by closed journal entries, the D-NNN index, and `git log` on
   `docs/atlas/`.
3. **Up next duplicated Current milestone's narrative.** The milestone
   prose already named the four skills to ship; Up next just re-listed them
   as bullets. Two phrasings of the same commitment, free to drift.

## Decision

`ROADMAP.md` contains exactly one section: **Current milestone** (goal
narrative + exit criteria). No Up next, no Backlog, no Recently done.

## Rationale

- **Single source of truth per concept.** Open questions live in Q-NNN.
  Committed designs live in D-NNN. Finished work lives in closed journal
  entries + git history. The roadmap's unique contribution is forward
  narrative — what we're trying to achieve right now — which has no other
  home.
- **Parallel-session friendly.** A shared ordered list (Up next, Backlog)
  is a merge-conflict hazard when multiple sessions run concurrently —
  directly at odds with [[[[005-multiple-active-journal-entries-allowed-no-single-active-con]]]]. Per-entity files (journal entries,
  Q-NNN) don't share a mutable list, so they don't conflict. Removing the
  queue also removes the implicit "I take item 1, you take item 2"
  serialization that a list invites; work selection becomes "look at the
  milestone goal, look at active journal entries, grill-me something
  un-claimed."
- **Forces promotion.** Items that previously lived in Backlog as soft
  TODOs must now either become Q-NNN (real open questions) or be dropped.
  No purgatory tier.

## Consequences

- "What should I do next?" requires reading Current milestone + active
  journal entries + open Q-NNN. Slightly more synthesis than scanning a
  bullet list, but the inputs are all single-source.
- Soft "we might do this someday" ideas no longer have a durable home in
  atlas. That is intentional — if it matters, it becomes a Q; otherwise
  it shouldn't survive a session.
- One less surface for cross-machine merge conflicts ([[[[020-multi-machine-sync-strategy-for-divergent-atlas-state]]]]).

## Alternatives considered

- **Keep Up next as a pre-grill queue.** Rejected: the milestone narrative
  already enumerates the same work at the right granularity; two phrasings
  drift. If finer-grained sequencing is needed within a milestone, the
  milestone description itself can carry it.
- **Keep Backlog as an idea bin.** Rejected: it competes with Q-NNN for
  the same role and accumulates stale entries. Promote real questions to
  Q; let stale ideas die.
- **Keep Recently done as a changelog.** Rejected: derivable from closed
  journal entries + D index + `git log`. Maintaining a hand-curated copy
  is pure rot risk.
