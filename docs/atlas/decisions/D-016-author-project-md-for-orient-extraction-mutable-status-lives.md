---
id: D-016
title: Author PROJECT.md for orient extraction; mutable status lives in ROADMAP
date: 2026-05-28
status: active
triage: promoted
tags: [project-md, orient, data-model, authoring, progressive-disclosure]
related: [D-003, D-010, D-012]
source-journal: 2026-05-28-orient-coverage-and-project-authoring.md
supersedes: []
superseded-by: []
affects: [atlas-orient, atlas-bootstrap]
---

# Author PROJECT.md for orient extraction; mutable status lives in ROADMAP

## Context

orient renders PROJECT.md as a session-start summary by slicing sections, so
how PROJECT.md is written directly determines what the agent learns. Two
failures showed up together: the old renderer truncated prose by line count
(dangling "...is" / "...failure modes:" fragments), and it surfaced only
Background + Stage + a glossary count — leaving Non-goals and Hard constraints
*entirely invisible*, so the agent never knew the guardrails existed to read
them. Separately, the "Current stage" field had drifted into a multi-phase
narrative that duplicated and then contradicted ROADMAP's Current milestone —
a mutable status sitting in a file whose own header says "keep stable".

## Decision

PROJECT.md is authored for extraction: each prose section leads with a
self-contained first sentence (what orient shows as the headline), the
guardrail sections (Non-goals, Hard constraints) stay short bullet lists that
orient inlines in full, and "Current stage" is a single lifecycle word —
forward/mutable status lives only in ROADMAP's Current milestone.

## Rationale

- **Guardrails must be visible, not just present.** Progressive disclosure
  (title-is-the-menu) only works if the menu names what matters; constraints
  the agent could violate are worth inlining, not hiding behind a second read.
- **A stable file can't hold a moving field.** PROJECT.md is the constitution
  (per the CLAUDE/PROJECT split) and ROADMAP owns forward state (single source
  of truth per concept). A status field in PROJECT.md is structurally destined
  to go stale — the drift here proved it isn't self-enforcing.
- **Source written for the extractor beats a cleverer extractor.** Sentence-
  aware slicing still fails on colon-led or header-only sections; fixing the
  authoring convention is the durable fix.

## Consequences

- orient inlines Non-goals + Hard constraints and lists remaining section
  names under "More in PROJECT.md"; truncation is sentence-aware.
- The PROJECT.md template documents the convention so new projects inherit it.
- atlas-bootstrap interviews should produce PROJECT.md sections that obey this
  (extractable first sentence; one-word stage).

## Alternatives considered

- **Delete "Current stage" entirely** — rejected; the template intends it as a
  one-word lifecycle marker that is genuinely orthogonal to a milestone
  narrative, so collapsing (not deleting) preserves a useful, low-churn signal.
- **Only fix the extractor (sentence-aware everywhere)** — insufficient alone;
  colon-led and header-only sections still extract poorly, and invisible
  sections stay invisible regardless of slicing.
