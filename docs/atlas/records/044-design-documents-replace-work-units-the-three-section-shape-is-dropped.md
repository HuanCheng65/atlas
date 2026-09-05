---
id: 44
title: Design documents replace work units; the three-section shape is dropped
date: 2026-09-05
type: decision
tags: [data-model, workflow]
---

# Design documents replace work units; the three-section shape is dropped

`grill-me` had one exit: open `docs/atlas/work/<date>-<slug>.md` and fill
Intent, Spec and Plan. A grill crosses one gap — from something vague to
something more decided — and the gaps do not come in a fixed set of three.
Settling a product's form is design at one depth; how each module is built is
design one depth lower, and neither is Intent, Spec or Plan. Demanding all
three from every interview forces the levels the round never reached to be
invented.

## Decision

One document per grill round at `docs/atlas/design/<date>-<slug>.md`, holding
**Decided** and **Still open**, written once and not edited afterwards. The
level is a label in the title, not a field. Each document names the one it
continues, written by the script, which requires exactly one of `--from` or
`--new`. `docs/atlas/work/` is gone; the store goes to v3.

This (supersedes:: [[041-work-units-land-as-one-file-each-plan-md-is-deleted]])
in part. What survives is the file written once, dated, with no status and
nothing to close, and `plan.md` staying deleted. What is overturned is the
three-section shape, the work unit as the unit, and session start naming the
latest file.

## Rationale

Spec and design are not two kinds of thing. They are the same content seen from
two sides: what one round chose among alternatives is what the next round must
satisfy. A schema that separates them therefore has to guess which side the
author is standing on, and forces a choice where there is no fact.

**Still open means "as of this date."** Nothing closes an entry. The mechanism
considered first — number the entries, have each new document claim the one it
continues, derive "resolved" from the claims — was rejected: entry numbers are
positional and shift if a draft is reordered; one round rarely maps to one
entry, settling two at once or half of one or finding the entry was the wrong
question; and an entry stops being open for reasons that produce no document at
all, being settled in conversation, made moot, or abandoned. That derivation
computes "nobody opened a file for it," not "still undecided" — the journal's
`status` field again with the maintenance disguised as derivation
([[033-the-journal-is-deleted-findings-become-records]]).

## Consequences

- Design documents leave the session-start payload. Which line of thinking is
  being picked up has nothing to do with which file is newest, so any fixed
  number of recent files is noise paid for every session. The trigger moves to
  `using-atlas`, which every session loads
  ([[024-triggers-live-where-the-agent-always-sees-them-not-in-skill]]):
  `ls docs/atlas/design/` is the menu, since each filename carries date and
  topic.
- Files stay flat. Rounds branch and a later round may draw on two earlier
  ones; that is a graph, and a directory tree cannot hold it.
- Keepers and Throwaways stop being a fixed section and become guidance for
  implementation-level rounds, the only level at which scaffolding exists to
  classify. The rule is unchanged
  ([[006-verification-keepers-throwaways-instead-of-enforced-tdd]]).
- The v1 migration stamped `STORE_VERSION` rather than the literal 2, so
  bumping the constant made it claim to produce a v3 store. Each migration now
  stamps its own step's number, and only the last in the chain rebuilds the
  index — every script refuses a store mid-chain, reindex included.
