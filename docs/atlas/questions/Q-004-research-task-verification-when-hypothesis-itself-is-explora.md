---
id: Q-004
title: Research task verification when hypothesis itself is exploratory
date: 2026-05-27
status: open
tags: [verification, research, grill-me]
related: [D-008]
source: bootstrap
source-journal: null
severity: medium
answered-by: null
---

# Research task verification when hypothesis itself is exploratory

## Why this matters

D-008 requires every task plan to declare a Verification approach. For
engineering tasks this is straightforward (tests, eval set, reference
comparison). For research tasks where the question itself is "does X work?",
the completion bar is harder to state up-front — by definition, the team
doesn't yet know what success looks like.

## Context

If grill-me forces a verification standard that can't be honestly chosen,
either the user invents a fake one ("we will visually inspect plots") or
skips the requirement entirely. Both erode the discipline D-008 is meant to
provide.

## Investigation needed

- Collect examples of research-task verifications during dogfooding.
- Consider verification modes specific to research: "decision criterion
  document" (what observation would change our mind?), "baseline comparison",
  "ablation completed".
- Possibly relax the requirement for E-NNN-driven tasks: the experiment's
  `result` + `conclusion` may already be the verification.

Evidence: `docs/design.md` "Open design questions" → "Research task verification".
