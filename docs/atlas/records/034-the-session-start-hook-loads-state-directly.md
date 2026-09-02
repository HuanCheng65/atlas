---
id: 34
title: The session-start hook loads state directly
date: 2026-09-02
type: decision
tags: [hooks, session-lifecycle, skills]
---

# The session-start hook loads state directly

## Context

Loading state at session start took four steps. A hook printed a paragraph
asking the agent to invoke a skill; that skill instructed the agent to invoke a
second skill; the second skill instructed the agent to run a script; the script
printed the state. Three of the four steps only relayed a request, each one a
round trip, and the first three depended on the agent complying with prose that
had to be written in capital letters to be obeyed.

The hook was already running a command. It could have run the script.

This (supersedes:: [[009-using-atlas-re-injects-per-context-window-resume-only-re-orients]])
and (supersedes:: [[027-orient-scans-frontmatter-index-md-demoted-to-deterministic-human-view]]).

## Decision

The SessionStart hook runs the state script and its output lands in context
directly. `atlas-orient` is deleted. `using-atlas` remains, and holds what a
hook cannot: the rules for what earns a record and when to write one.

The hook command is a stable one-liner naming a script that ships with atlas,
so changing what gets injected never again requires editing a user's
`settings.json`.

The split between the two follows ownership. Atlas's own operating rules ship
and version with atlas, which is why they stay in the skill rather than moving
into the user's `CLAUDE.md`; the project's own rules stay in the project's
files, where an atlas upgrade never touches them.

## Consequences

State loading cannot be skipped, and costs no round trips. On the dogfood store
the injected payload is a third of what the old chain produced, because the
triage section is gone and the index-derived material was never needed.

Every matcher runs the same script. Resume passes `--resume`, which ships the
state without the line asking for the skill: on resume the conversation context
survives, so the skill body is already loaded and asking again would only cost
a round trip, while the store may genuinely have moved meanwhile.

`_index.md` remains a generated human browse view that the agent does not read,
which was the durable half of the superseded decision.
