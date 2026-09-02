---
id: 35
title: Working rules are un-mechanized constraints, authored not promoted
date: 2026-09-02
type: decision
tags: [project-md, decisions, agent-behavior]
---

# Working rules are un-mechanized constraints, authored not promoted

## Context

A decision could be marked `triage: promoted`, which required a matching
pointer in PROJECT.md's Working rules, with validate enforcing the pairing both
ways. The framing was that a rule is a status a decision earns.

That framing does not survive the question "why would a decision become a
rule?". A decision record is written for a reader asking why the code is like
this. A working rule is written for an agent about to act. Same choice, two
readers, two grammars — the second is a rewrite of the first, not a promotion.

The useful question is different and sharper: a rule belongs in the
always-loaded list exactly when nothing stops the agent from violating it. A
300-character frontmatter cap needs no rule because validate rejects it. "Skills
activate on events, not session phases" needs one because a phase-driven skill
compiles and runs.

This (supersedes:: [[026-decisions-stay-adr-events-standing-rules-promote-into-project-md]]).

## Decision

The triage field and the pairing check are removed. Working rules is a
hand-authored list: the user writes the rule they want followed and links the
record that justifies it. Nothing is promoted automatically, and no record
carries a flag saying it has been.

A rule earns its place by the test above — no mechanism enforces it. Where a
mechanism could exist, the mechanism gets written instead, which makes the list
partly a backlog of checks not yet written.

## Consequences

The always-loaded rule list stops tracking the decision log's shape and starts
tracking what genuinely cannot be enforced, which is a smaller and slower-moving
set.

The same test applies to memory records: both hold constraints nothing enforces
and both must be restated every session. They remain separate artifacts for a
reason that is only ergonomic — the user edits a list in one file, the agent
writes one record at a time — not because they are different in kind.

There is no longer a "decisions pending triage" backlog, which was one of the
two things the old session-start summary nagged about.
