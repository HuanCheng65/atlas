---
id: 39
title: The store is validated by a post-write hook, not by the script that writes
date: 2026-09-03
type: decision
tags: [hooks, enforcement, data-model]
---

# The store is validated by a post-write hook, not by the script that writes

## Context

A link is resolved by filename and nothing else
([[032-relations-live-in-the-body-as-obsidian-wikilinks]]). A mistyped slug
therefore produces no error at all: it is a link that matches nothing, so the
supersede it was meant to express does not happen, and the index goes on
showing the superseded record as current. Since standing is computed from
edges rather than stored ([[030-a-record-s-truth-may-not-depend-on-a-future-edit]]),
a link that silently matches nothing is the one way that design can fail.

Nothing checked for it at write time. `validate.py` catches all of it, but
only when somebody runs it.

The obvious repair — check inside the script that creates records — guards the
wrong path. Most writes to the store are not that script: memory records are
rewritten in place, typed edges are appended to already-published records, and
consolidation rewrites the memory set wholesale. Each of those is an ordinary
file edit that no script owns, and each is more likely to go wrong than the
one path a script does own.

## Decision

A `PostToolUse` hook runs validate, then reindex, after any tool call that
changed the store. A failure exits 2, which returns the complaint to the agent
before the work reaches a commit.

A fingerprint of the record files short-circuits the unchanged case, and is
written even when validation fails, so one broken state is reported once
rather than after every subsequent command.

Regenerating the index moves from something a script remembers to do into the
same hook, which makes the index derived in fact and not only by convention.

## Rationale

- The rule this replaces was prose in a skill body, and the project's standing
  position is that a rule a mechanism can enforce should be the mechanism
  ([[028-mechanical-affordances-over-prose-constraints-for-agent-rules]]).
- Checking after the fact over the whole store is indifferent to which path
  wrote, which is the only property that covers writes no script owns.
- This became available only when hooks began shipping with the code
  ([[037-atlas-ships-as-a-plugin-one-install-unit]]). Before that, adding a
  hook meant asking the user to hand-edit their settings, which is exactly the
  step that silently never happened.

## Consequences

- Every write and every shell call in a project with a store pays a process
  start; the fingerprint keeps the unchanged case at roughly thirty
  milliseconds, and projects without a store exit in the shell guard.
- `_index.md` is rewritten as soon as the store changes, so its diff arrives
  in the same commit as the records rather than whenever someone reindexed.
- The store must be valid continuously rather than at commit time. A
  deliberate half-written state now produces a complaint on the next command.

## Alternatives considered

- Validating inside the record-writing script — rejected above.
- A `PreToolUse` hook that refuses the write — rejected for now. It would have
  to validate proposed content rather than a written store, and blocking an
  edit is a heavier instrument than returning the error for a fix.
- Validating at commit time via a git hook — rejected. It lands the complaint
  after the work is assembled rather than at the edit that caused it, and it
  is a second installation mechanism outside the plugin.
