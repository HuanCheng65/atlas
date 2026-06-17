---
id: D-019
title: using-atlas re-injects per context window; resume only re-orients
date: 2026-06-12
status: active
triage: archival
tags: [skills, activation, hooks, session-lifecycle]
related: [D-007]
source-journal: 2026-06-12-resolve-design-review-findings.md
supersedes: []
superseded-by: []
affects: [using-atlas, atlas-orient]
---

# using-atlas re-injects per context window; resume only re-orients

## Context

The SessionStart hook demands a using-atlas invocation on every start, resume, clear, and compact, while using-atlas's own anti-pattern list forbids re-invoking it mid-session ("once per session"). Both texts use "session" as the counting unit — the same soft concept the project already rejected once, when "session-end as an explicit step" was discarded in the original design. The design review surfaced the conflict: after a compact, the hook says "you must" while the skill says "you must not", and the agent has to guess.

## Decision

The counting unit for session-start setup is the context window, not the session: whenever the context is rebuilt (startup, clear, compact) the hook demands a fresh using-atlas invocation; within an intact window re-invocation stays forbidden; on resume — where the conversation context survives but project state may have moved — the hook asks only for an atlas-orient state refresh.

## Rationale

- using-atlas's entire value (the trigger table, watching mode, vocabulary rules) lives *in context*. The correct re-injection condition is therefore "the context was rebuilt", not any notion of session boundary.
- "Session" is a soft concept — the same reasoning that rejected an explicit session-end step applies to counting activations by session.
- Resume is the asymmetric case: instructions are still in context (no re-injection needed) but other sessions or machines may have advanced the project meanwhile; atlas-orient is cheap and idempotent, so a state refresh is the precisely-matching remedy.

## Consequences

- The SessionStart hook differentiates by matcher: startup / clear / compact → demand using-atlas; resume → ask for an atlas-orient refresh instead.
- using-atlas's wording changes from "once per session" to "once per context window"; the mid-window re-invocation ban stays.
- Skill-authoring gains a precise concept: persistent surfaces are per-context-window artifacts, and any "invoke once" rule must name the window, not the session.

## Alternatives considered

- **Re-invoke using-atlas on resume as well** — rejected: the skill body is still in context, so re-injection is pure noise and would contradict the once-per-window ban the same way the current texts contradict each other.
- **Keep "session" wording and carve out compact/resume exceptions in prose** — rejected: preserves the ambiguous unit that produced the conflict; the fix is naming the right unit, not patching cases.
