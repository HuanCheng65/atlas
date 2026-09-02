---
id: 5
title: Multiple active journal entries allowed (no single-active constraint)
date: 2026-05-27
type: decision
tags: [journal, concurrency]
---

# Multiple active journal entries allowed (no single-active constraint)

## Context

Real work is parallel: separate windows on different sub-projects, an
exploratory branch resumed days later, a quick fix sandwiched between two
larger tasks. Enforcing one active journal entry at a time would either block
parallel work or force premature closing of entries.

## Consequences

Multiple active entries coexist freely. Each agent instance carries "which
entry am I working on" in its conversation memory; there is no single global
pointer. `journal/_index.md` lists all currently-active entries.

## Decision

No constraint on the number of active journal entries. Coordination is
per-agent-instance and per-skill-invocation, not enforced globally.

## Rationale

- Parallel work across topics and windows is the normal case, not an exception.
- A single-active model would force closing entries before work actually wraps,
  losing the "open work unit" semantics.
- Each agent already knows what task it is on; promoting that to a global
  invariant adds coordination cost without value.

## Alternatives considered

- One active journal entry per project at any time — rejected; parallel work
  across windows / topics is normal.

Evidence: `docs/design.md` "Multi-active by default" principle and rejected
"One active journal entry per project" bullet.
