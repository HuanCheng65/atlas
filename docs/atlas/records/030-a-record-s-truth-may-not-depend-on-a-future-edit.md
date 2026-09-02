---
id: 30
title: A record's truth may not depend on a future edit
date: 2026-09-02
type: decision
tags: [data-model, design-principle]
---

# A record's truth may not depend on a future edit

## Context

Dogfooding produced two failures with one shape. Ten of eleven journal entries
were never closed, the oldest untouched for seven weeks, because `status:
active` is only true if somebody comes back and changes it. An experiment
refuted the same day it was written kept asserting its result in every index
for a month, because the pointer to the refutation was a field the agent
invented on the older record — unvalidated, one-directional, and requiring an
edit to a record nobody had reason to reopen.

Both are the same bug: the record stored a claim whose truth depended on a
future action. Everything that stayed current in the store was either
hand-curated (the roadmap) or script-enforced (validate); everything that
depended on the agent remembering to do bookkeeping had rotted.

## Decision

A record states what was true when it was written, and nothing else. Anything
that can change afterwards is computed from the records written since.

Concretely: no `status` field, no reverse links, no triage flag. Superseded,
refuted and answered are derived from typed edges declared on the *newer*
record. Links point backwards, which validate asserts as `target < source`, so
a published record never needs reopening. Memory records are the one exception
— they hold what is currently in force rather than what happened — and are
rewritten in place, with git keeping the history.

## Consequences

The class of maintenance that dogfooding proved does not happen is gone: there
is nothing to close, nothing to mark, nothing to go back and correct.

The cost is that standing is no longer visible in the file. Reading a record
alone will not tell you it was refuted; that shows in a generated index or a
backlink query. This is the trade accepted: a marker in the file would be
accurate only as long as somebody maintained it, which is the failure being
removed.

Two mechanical rules fall out, both enforced rather than written down: links
point backwards, and every derived field name is rejected in frontmatter so a
half-finished migration fails loudly instead of leaving a field nothing reads.
