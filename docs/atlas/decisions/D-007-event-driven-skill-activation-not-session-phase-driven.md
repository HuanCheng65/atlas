---
id: D-007
title: Event-driven skill activation, not session-phase-driven
date: 2026-05-27
status: active
tags: [skills, activation]
related: [D-005, D-009]
source: bootstrap
source-journal: null
supersedes: []
superseded-by: []
affects: []
---

# Event-driven skill activation, not session-phase-driven

## Context

A common workflow shape is "session start → work → session end", with skills
hooked to those boundaries. In practice, sessions are a soft concept: agent
windows open and close at arbitrary moments, parallel windows blur "start"
and "end", and explicit phase steps tend to get missed or fragmented.

## Decision

Skills activate on events, not phases. There is no "session start" or "session
end" moment. Triggers: a new task is described (grill-me), existing context is
needed (atlas-orient), work progresses (atlas-log appends), a decision /
question / experiment is born (atlas-entity), periodic distillation is due
(atlas-compact).

## Rationale

- Sessions are too soft to anchor lifecycle steps to reliably.
- Events are observable and unambiguous, so each skill can describe its own
  triggers in its SKILL.md.
- Pairs cleanly with the "multiple active journal entries" model (see D-006).

## Consequences

- No `atlas-session-start` or `atlas-session-end` skill; their concerns are
  absorbed into atlas-orient and atlas-log respectively.
- Each skill is responsible for stating its own activation conditions clearly.

## Alternatives considered

- Session-end as an explicit step — rejected; session is a soft concept,
  explicit boundaries get missed or fragmented.
- Phase-driven workflow (Superpowers-style) — rejected; too rigid for the
  variety of tasks atlas serves.

Evidence: `docs/design.md` "Event-driven, not phase-driven" principle and
rejected "Session-end as an explicit step" bullet.
