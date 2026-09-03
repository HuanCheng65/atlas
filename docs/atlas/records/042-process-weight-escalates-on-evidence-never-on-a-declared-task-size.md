---
id: 42
title: Process weight escalates on evidence, never on a declared task size
date: 2026-09-03
type: decision
tags: [workflow, agent-behavior]
---

# Process weight escalates on evidence, never on a declared task size

The framework covered what a project remembers and left how work gets done to
one skill invoked by hand. The failure it needs to cover is not forgetting: a
coding agent crosses the gap from intent to structure by guessing, because
completion is what post-training rewards, and it decomposes a task along the
narrative it was described in rather than along the axes where change will
arrive.

The obvious fix — a pipeline every task walks — is the one already rejected
twice, for research code that does not fit strict TDD
([[006-verification-keepers-throwaways-instead-of-enforced-tdd]]) and for the
variety of tasks the framework serves
([[013-event-driven-skill-activation-not-session-phase-driven]]). A pipeline is
heavy because task size is declared at the start and every task pays for that
declaration, including the ones that were correctly judged small.

## Decision

There is no classification step. The default is that nothing happens. Weight is
added when a specific signal appears, and the level may change mid-work.

- Whenever any check is written, it names the source of its verdict.
- When the change touches something expensive to unmake — data already stored
  in that shape, callers already on that interface, an assumption that there is
  exactly one of something, a boundary the project does not control — `grill-me`
  is invoked even though work has started, and settles a representation before
  more code is written.

## Rationale

Removing the classification step is what makes this light: judging a task small
costs nothing when it turns out not to be, because the signal fires at the
moment it stops being true. A pipeline cannot do that — it has to be right at
the entrance.

The representation is asked for first because it is the decision with the
highest cost of reversal: data accumulates in its shape and callers are written
against it, while procedure code can be rewritten. Asking for it in the same
turn as the implementation does not work; the design becomes a preamble hurried
past on the way to the code.

## Consequences

- Both triggers live in `using-atlas`, which is loaded every session. A trigger
  inside a skill body cannot fire that skill's own invocation
  ([[024-triggers-live-where-the-agent-always-sees-them-not-in-skill]]).
- `grill-me` gains a named menu of representation kinds and three questions
  that check a proposed one without requiring architectural taste — what it
  assumes, how many places state the same fact, and what tells you which part
  is wrong. The model proposes and justifies the kind; the user checks the
  concrete artifact.
- Detecting a stuck agent in real time was considered and rejected: an exit
  code is a bad signal in both directions, the agent varies the command so
  textual repetition does not match, and making the signal readable would
  require the agent to shape its commands for the hook — a mechanism that only
  works if prose makes the agent conform, which inverts
  [[028-mechanical-affordances-over-prose-constraints-for-agent-rules]].
