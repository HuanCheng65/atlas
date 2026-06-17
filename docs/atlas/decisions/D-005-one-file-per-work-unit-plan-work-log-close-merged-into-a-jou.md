---
id: D-005
title: 'One file per work unit: plan, work log, close merged into a journal entry'
date: 2026-05-27
status: active
triage: archival
tags: [journal, data-model]
related: [D-006, D-007]
source: bootstrap
source-journal: null
supersedes: []
superseded-by: []
affects: []
---

# One file per work unit: plan, work log, close merged into a journal entry

## Context

A single piece of work has a plan, an execution log, and a close-out. Earlier
designs split these across separate files (plan.md vs. journal.md) or treated
journal as append-only daily notes. Both fragment context for one work unit
across multiple places.

## Decision

A journal entry is one work unit end-to-end. The same file contains Context
(from grill-me), Decisions resolved, Steps, Verification, Keepers,
Throwaways, Work log (appended by atlas-log), and Close. File path:
`docs/atlas/journal/YYYY-MM-DD-<slug>.md`. Frontmatter tracks status (`active`
or `closed`), open/close timestamps, and verification result.

## Rationale

- Plan and execution describe the same unit of work; co-locating them keeps
  the narrative readable.
- Active entries are mutable; closed entries are frozen — a single lifecycle
  is simpler than two coupled lifecycles across files.
- Pairs naturally with the event-driven activation model (see D-007).

## Consequences

- `atlas-log` reads and appends to one journal entry at a time.
- Searching for "what happened on task X" lands in one file, not two.
- The body structure is conventional but flexible — sections may be empty or
  skipped when not relevant.

## Alternatives considered

- Plan and journal as separate files — rejected; they describe the same work unit.
- `type` field in journal frontmatter (e.g. `log` vs `plan`) — rejected;
  redundant when a single file already represents the full lifecycle.

Evidence: `docs/design.md` "Journal" section and rejected
"Plan and journal as separate files" / "type field in journal frontmatter" bullets.
