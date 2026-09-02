---
id: 25
title: Distributed skill bodies cite reasoning inline, never this project's entity IDs
date: 2026-05-28
type: decision
tags: [skills, distribution, hygiene]
---

# Distributed skill bodies cite reasoning inline, never this project's entity IDs

## Context
The skills under `skills/` ship as a generic framework to other projects. Atlas's own entity IDs ([[001-plain-text-git-as-the-data-layer]], [[024-triggers-live-where-the-agent-always-sees-them-not-in-skill]], ...) are meaningless — or actively wrong — in a project that installs atlas, since their entity space is different. Citing "(per [[024-triggers-live-where-the-agent-always-sees-them-not-in-skill]])" as the authority for an instruction leaked atlas's dogfood state into the distributable, caught during review of the D-recognition heuristic edit.

## Decision
A skill body that ships in `skills/` must state its reasoning self-contained inline and never cite this project's real entity IDs (D/Q/E-NNN) as the rationale for an instruction; placeholder IDs used to teach syntax or as command-usage examples are fine.

## Rationale
The distributable must read correctly in any installing project. Inline reasoning is also strictly better even for us — a reader understands the "why" without chasing a cross-reference. The placeholder carve-out preserves the ability to teach the ID syntax (e.g. "see [[013-event-driven-skill-activation-not-session-phase-driven]]" as a glob example) without coupling to real state.

## Consequences
- Reviewing skill edits includes a grep for `[DQE]-NNN` authority-style citations before commit.
- Reasoning that previously leaned on a decision ID must be restated in-body; this slightly lengthens some skill text but removes a coupling.
- The boundary requires judgment: an ID used as *authority* ("per [[024-triggers-live-where-the-agent-always-sees-them-not-in-skill]]") is banned; an ID used as a *teaching placeholder* ("suppose a decision [[013-event-driven-skill-activation-not-session-phase-driven]]") is allowed. The test: would the sentence still make sense in a project whose [[013-event-driven-skill-activation-not-session-phase-driven]] is something unrelated? If it depends on *our* [[013-event-driven-skill-activation-not-session-phase-driven]], it leaks.

## Alternatives considered
- **Allow ID citations, rely on readers to ignore them** — rejected: silently wrong in distributed copies, and erodes trust in the framework's polish.
- **Ban all D/Q/E-NNN tokens including placeholders** — rejected: over-broad; placeholder IDs are a legitimate way to document the reference/glob syntax and have no coupling to real state.
