---
id: 41
title: Work units land as one file each; plan.md is deleted
date: 2026-09-03
type: decision
tags: [data-model, workflow]
---

# Work units land as one file each; plan.md is deleted

Deleting the journal left one thing open on purpose: its own closing words
were that plans no longer have a home in the store, that `docs/atlas/plan.md`
holds the plan for the work in hand, and that where intent and specification
should live "is a separate problem and remains open"
([[033-the-journal-is-deleted-findings-become-records]]). This settles it.

## Decision

One file per work unit at `docs/atlas/work/<date>-<slug>.md`, holding Intent,
Spec and Plan. A script owns the date and writes the skeleton. The file is
written once and not edited afterwards. `plan.md` is deleted.

## Rationale

The defect in `plan.md` was the reuse of one path, not the keeping of plans.
A single file overwritten by every work unit in turn is committed state whose
truth holds only while one particular piece of work is in flight, and which
looks authoritative in git forever — this repository's copy had been stale for
ten commits, still describing the memory-model redesign while the plugin, hook
and bootstrap work landed around it. One file per unit removes that without
removing the plan: each is a dated account of what was undertaken, which stays
true however the code moves, so it violates nothing about a record's truth not
depending on a future edit ([[030-a-record-s-truth-may-not-depend-on-a-future-edit]]).

It is not the journal returning. The journal died of two things and neither is
present: a work log that grew by appending, and a `status` field that was only
true while somebody maintained it. There is no work log here and nothing to
close.

## Consequences

- The store keeps what outlives the work unit — a constraint nothing enforces,
  an architecturally significant choice, a measurement, an open question. A
  choice that is only how this task got done stays in the Spec section and is
  not a record, because the code it produced already enforces it.
- Switching machines mid-work now carries the intent and spec with the repo,
  which `plan.md` also did; what is lost is nothing, since the file is
  committed like any other.
- `session_start.py` names the newest work unit and whether it is committed.
  It deliberately does not say which is "active": a field that says so is only
  true while maintained, and the date in the filename lets the reader judge.
