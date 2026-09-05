---
id: 45
title: grill-me asks in rounds bounded by independence
date: 2026-09-05
type: decision
tags: [workflow, agent-behavior]
---

# grill-me asks in rounds bounded by independence

`grill-me` asked one question at a time and forbade batching, on the ground
that batched answers degrade. The skill it descends from batches instead: it
treats the interview as a decision tree and asks, in one round, every question
whose prerequisites are already settled.

## Decision

Questions in one round must be mutually independent. If a question depends on
the answer to another question in the same round, it belongs to the next round.
The bound is independence, not count.

Finding facts is the agent's job, never the user's. A question answerable from
the filesystem, the git history or a tool is dispatched to a sub-agent rather
than asked, and the dispatch does not block: only the questions downstream of a
running exploration wait. Three properties bound it — read-only and on the
smallest model that can do the job; unable to dispatch sub-agents of its own;
and no more than three or four at once, a ceiling judged against the round
rather than a number to fill.

## Rationale

Both rules aim at the same hazard and disagree only on the test. What degrades
an answer is being asked something that depends on an answer not yet given;
asking two independent questions together costs nothing. So the rule is kept
and its test replaced, which is why this is not a loosening.

The three properties are stated as properties rather than as a named agent kind
or model, because naming either couples the skill to one harness. Where the
harness offers an agent kind that cannot dispatch further sub-agents, picking
that kind makes the limit hold mechanically instead of by instruction, which is
the form to prefer
([[028-mechanical-affordances-over-prose-constraints-for-agent-rules]]).

The ceiling is low on purpose: a round wanting more explorations than that is
usually a round whose questions were not separated properly, and something that
should have been put to the user is being looked up instead.

## Consequences

- None of this is mechanically checkable. Whether a round was independent and
  whether an exploration was warranted are judgments made during an interview,
  and no test observes them. The source of the verdict is use: a round that was
  not independent shows up as the user answering a question and then being
  asked something that answer already settled.
- The record exists because the rule it replaces is the intuitive one. Without
  it, a later session reads "ask in rounds" as a lapse and restores
  one-at-a-time.
