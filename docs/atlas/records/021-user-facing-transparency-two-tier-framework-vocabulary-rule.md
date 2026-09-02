---
id: 21
title: 'User-facing transparency: two-tier framework vocabulary rule'
date: 2026-05-28
type: decision
tags: [skills, ux, agent-behavior, transparency]
---

# User-facing transparency: two-tier framework vocabulary rule

## Context

Atlas is operational memory for the agent — its job is to give the user the *effect* of memory (continuity, conflict-detection, decision recall) without making them context-switch into "the framework". An incident surfaced when the agent, mid-discussion of a separate project's UX design, said "和 atlas 里 [[013-event-driven-skill-activation-not-session-phase-driven]] 冲突" — referencing a framework artifact ID in a conversation that was otherwise about Inbox / Item / Capture Log semantics. The user flagged it as a UX leak: atlas vocabulary had bled out of the agent's internal layer into the substantive conversation.

A first-pass fix overshot — it stripped *all* framework signals from user-facing output, including operational announces like `(opened docs/atlas/journal/2026-...md)`. The user pushed back: those announces are useful, because the journal is plain text + git ([[001-plain-text-git-as-the-data-layer]]), the file *is* the durable artifact, and a path is a concrete pointer rather than implementation detail.

## Decision

User-facing communication is split into two layers, with different vocabulary rules:

**Layer 1 — Substantive conversation** (the meat of the discussion): translate framework vocabulary into content-level language. No `D-NNN` / `Q-NNN` / `E-NNN` references, no journal filenames cited as references, no "active entry" / "atlas" abstractions.

**Layer 2 — Operational announces** (one-line, parenthetical, post-hoc, at lifecycle events: open / append / close / Plan written): file paths are fine and useful; strip framework-descriptor verbiage ("to track this work", "this active journal entry", "I'll keep a log") around them.

Exceptions where direct naming IS appropriate: user explicitly asks to see / list / audit framework items; user is editing atlas itself (skills, scripts, templates); during `atlas-bootstrap` (the moment the framework is introduced).

The rule is documented as the foundational section of `using-atlas/SKILL.md`; the other atlas skills cross-reference it for their specific announce conventions.

## Rationale

The two-tier split resolves the conflict between "user shouldn't context-switch" and "concrete pointers are useful":

- Substantive conversation is where context-switching costs are real — a `[[013-event-driven-skill-activation-not-session-phase-driven]]` reference forces the user to mentally jump into the framework to understand what was meant. Translation is mandatory there.
- Operational announces are bounded, parenthetical, post-hoc. They run in a separate channel from the substantive discussion. A file path inside `()` is a pointer the user can choose to follow (`git log`, `cat`, edit) or ignore — it doesn't pollute the surrounding conversation.

The v1 over-strict version ("strip all paths and framework words") failed a real use case: the user wants vague awareness ("大概有个感知") that work is being tracked AND the option to find the record concretely later. Content-only announces ("I'll keep a log") gave awareness but not the pointer.

[[001-plain-text-git-as-the-data-layer]] (plain text + git as the data layer) makes file paths legitimate first-class artifacts, not "implementation detail" — supports keeping them in announces. [[013-event-driven-skill-activation-not-session-phase-driven]] (event-driven skill activation) frames lifecycle events as the natural moments for a brief signal — supports the announce convention.

## Consequences

**Positive:**
- Future skills (atlas-compact, atlas-init, anything new) inherit the principle by default if they cross-reference `using-atlas`'s foundational section.
- The rationale for "why we don't say D-NNN in chat" is recorded — without this D, future maintainers would only see the implementation in SKILL files and might revert it.
- Distinction between "what's framework noise" and "what's a useful pointer" is now explicit, preventing future over-corrections (or under-corrections) toward either extreme.

**Negative:**
- Adds a tier-distinction that the agent has to remember each time it emits user-facing text. Some borderline cases will land ambiguously (e.g. "should I mention which decision I'm referring to by name if the user previously asked to see decision indexes earlier in the same session?").
- The exceptions list (working on atlas itself; user explicit request; bootstrap) is a judgment call — easy to err on either side. Future drift likely if not reinforced.

## Alternatives considered

- **No rule (v0)**: agent freely names `D-NNN`, journal filenames, "active entries" whenever convenient. Rejected — caused the original UX leak.
- **Strip everything (v1, over-strict)**: no file paths, no framework words anywhere in user-facing chat. Rejected after one round — lost concrete pointers without gain; the user explicitly wanted "感知 + handle" not "感知 alone".
- **Hide everything by default, expose on user opt-in (`/atlas-verbose`)**: tempting but adds a configuration surface and a new mode for the user to manage. Not justified at current scale — the two-tier rule already gives 90% of the benefit with no surface.
- **Encode the rule per-skill without a foundational source**: tried initially. Created drift risk — each skill could phrase the rule slightly differently, and bootstrap-only exceptions would be re-derived per skill. The single-source-of-truth in `using-atlas` with cross-references is cheaper to maintain.
