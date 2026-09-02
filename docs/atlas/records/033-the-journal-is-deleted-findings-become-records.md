---
id: 33
title: The journal is deleted; findings become records
date: 2026-09-02
type: decision
tags: [journal, data-model, dogfood]
---

# The journal is deleted; findings become records

## Context

The journal was an inbox nobody drained. In the dogfood store it held 317
work-log appends against 49 promoted experiment records, with 49 of the appends
empty; one entry reached 155 KB across 93 appends over six days and was still
marked active a month after its last edit.

The content in those appends was not narration. Sampling found measurements,
negative results, and constraints discovered mid-work — "the register cliff is
at 128, check REG before touching the estimator", "this knob is noise, stop
retrying it". None of it is recoverable from git, because rejected paths were
never committed.

It ended up there because of pricing, not discipline: appending cost nothing
and filing a record cost a ceremony — pick an id, fill a template, run validate,
run reindex. The cheap path absorbed the valuable content.

The other half of a journal entry, the Context paragraph, is what the agent's
own transcript already covers. Transcripts are pruned after a few weeks, but
"what am I in the middle of" has a horizon of days: the two windows coincide.

This (supersedes:: [[019-one-file-per-work-unit-plan-work-log-close-merged-into-a-jou]])
and (supersedes:: [[005-multiple-active-journal-entries-allowed-no-single-active-con]]).

## Decision

`docs/atlas/journal/` and its scripts are removed; existing entries move to
`docs/atlas/archive/` unchanged and stay grep-able. Nothing is bulk-extracted
from them.

What used to be an append is now a record: a measurement becomes an
`experiment`, a constraint becomes a `memory`. Writing one costs a single
command with the body on stdin, so there is no cheaper path for the content to
fall into.

Session context is not stored at all. The transcript covers the only window in
which it matters.

## Consequences

There is no "close the entry" step, and therefore no stale-active concept —
which (answers:: [[014-stale-active-journal-threshold-currently-3-days]]) by
removing what it asked about, and likewise
(answers:: [[011-does-verification-result-carry-signal-all-closes-are-passed]]):
the field is gone.

Plans no longer have a home in the store. `docs/atlas/plan.md` holds the plan
for the work in hand, overwritten per work unit and deliberately not a record —
a plan describes intent, and the store holds what happened. Where intent and
specification should live is a separate problem and remains open.

Losing the journal loses the grouping "what did this session do". That is
recovered from the commit, which groups exactly the records a work unit
produced.
