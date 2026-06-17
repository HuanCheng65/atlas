---
id: {{ID}}
# Title rules:
#   - Title states the ANSWER, not the topic. "Use X over Y" / "Adopt X" / "Reject X" — not "Logging" / "Strategy for X".
#   - Self-contained: readable from the index alone, no need to fetch the body.
#   - Specific: scanning the orient summary should tell the agent what was decided.
#   - If the slug ends up >70 chars, the title is too long — tighten.
title: {{TITLE}}
date: {{DATE}}
status: planned
# triage: pending → shows in orient's menu until reviewed; promoted → one-line rule
# in PROJECT.md Working rules with a (D-NNN) pointer (validate enforces the pair);
# archival → reviewed, stays an event record consulted on demand.
triage: pending
tags: []
related: []
source-journal: null
supersedes: []
superseded-by: []
affects: []
---

# {{TITLE}}

## Context
<!-- 这个决策出现的背景：观察到了什么问题、什么约束触发了思考 -->

## Decision
<!-- ONE SENTENCE, self-contained. This sentence gets pulled into the orient summary.
     It must state what was chosen, without needing Context to be intelligible.
     Multi-clause is fine; multi-paragraph is not. -->

## Rationale
<!-- 为什么是这个选择，关键的 trade-off -->

## Consequences
<!-- 这个决策意味着接下来会发生什么，正面和负面 -->

## Alternatives considered
<!-- 想过但没选的方案，简短说明为什么排除 -->