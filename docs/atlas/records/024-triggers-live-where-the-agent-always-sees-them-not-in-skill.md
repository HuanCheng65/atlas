---
id: 24
title: Triggers live where the agent always sees them, not in skill bodies
date: 2026-05-28
type: decision
tags: [skills, triggers, agent-behavior, architecture]
---

# Triggers live where the agent always sees them, not in skill bodies

## Context

Atlas skills follow event-driven activation ([[013-event-driven-skill-activation-not-session-phase-driven]]) — they fire when the agent recognizes a trigger condition. Three artifact types want proactive creation by the agent: D-NNN when a long-term choice gets settled, Q-NNN when an unresolved question surfaces, E-NNN when an experiment produces a citable result. Plus journal lifecycle events (append on work progress, close on completion).

Initial design put trigger conditions inside each skill's `SKILL.md` body — e.g. atlas-entity body has a "When to create what" section. Reviewing the conversation that produced [[021-user-facing-transparency-two-tier-framework-vocabulary-rule]] and [[023-progressive-disclosure-data-layer-title-is-the-menu-body-loa]], every D was created downstream of the user prompting — "do you think this needs to be recorded?" Never agent-initiated.

Diagnosed cause: the trigger condition lives inside atlas-entity's body, but `SKILL.md` bodies only load into the agent's context **after** the agent has already decided to invoke that skill. The trigger that drives the invocation has to be visible *before* the invocation happens. So trigger conditions in skill bodies are functionally dead code — the agent can't see them at the moment that matters.

The user surfaced this directly: "如果那个 SKILL 压根就没被加载进来 那你写这些也没用啊."

## Decision

Trigger conditions for proactive agent actions live in persistently-loaded surfaces (using-atlas body and each skill's description field), not in `SKILL.md` bodies — because bodies only load after the agent invokes the skill, so any trigger inside them cannot drive the invocation.

### Where triggers live

1. **`using-atlas/SKILL.md` body** — loaded at session start via BLOCKING reminder, stays in context the whole session. The canonical home for cross-skill agent triggers ("watch for these moments and route").
2. **Each skill's `description` field** — visible in the available-skills menu at all times. Trigger language here must be agent-active ("whenever a decision *emerges*", not "whenever the user *makes* a decision").
3. **`CLAUDE.md`** — also always loaded, but reserved for project-level rules; atlas-specific triggers go through using-atlas.

`SKILL.md` bodies still carry the *operational details* of how to perform the action once invoked (which script to call, what frontmatter to fill, when to confirm vs proceed). Triggers in bodies are forbidden — they don't fire, and they create the illusion that the design covered something it didn't.

## Rationale

**Why bodies don't work for triggers:** the agent's dispatch decision happens against its current context. SKILL bodies are pulled in *as a result* of dispatch; they cannot inform it. Writing "trigger on X" inside a body is like leaving instructions inside a sealed envelope and asking the recipient to follow them before opening.

**Why description-field triggers also need active phrasing:** descriptions are visible but pattern-match against intent. "Use this skill whenever the user makes a long-term architectural decision" pattern-matches on "user makes" — passive on agent side, biases toward waiting for the user to label the moment. Decisions emerge implicitly; the user usually won't label. The description must phrase the trigger as something the agent recognizes, not something the user announces.

**Why using-atlas is the right cross-skill home:** it's already the framing layer that runs at session start. It already has a "Routing to other skills" table, which is the right *shape* — it just needs to flip from "user signal → skill" to "agent-recognized moment → skill", and be strong enough that the agent treats recognition as a load-bearing responsibility rather than a soft hint.

## Consequences

**Positive:**
- Proactive entity creation actually has a chance of firing, because the trigger is visible at the moment the agent could fire it.
- The design failure mode "trigger never fires because trigger lives behind the action it's supposed to trigger" is named and forbidden.
- Future skills inherit the rule: anything that wants agent-proactive behavior puts its trigger in using-atlas or in its own description, not in its body.

**Negative:**
- using-atlas grows. It already carries the transparency principle ([[021-user-facing-transparency-two-tier-framework-vocabulary-rule]]) and now carries triggers. Risk of becoming the "everything skill". Mitigation: keep each section narrowly scoped and cross-reference, don't expand prose.
- Description fields have limited length; trigger language has to be terse. Easy to under-specify and have the agent miss the moment anyway. Mitigation: pair description triggers with the expanded version in using-atlas.

## Alternatives considered

- **Keep triggers in skill bodies, hope agent invokes early enough**: rejected — that's the failing status quo. Empirically the agent doesn't speculatively invoke skills just to see their triggers.
- **Put all triggers in CLAUDE.md**: CLAUDE.md is for project-level rules, not framework-specific behavior. Mixing them creates drift when atlas evolves. Single delegation to using-atlas (current state) is cleaner.
- **Build a "trigger-watcher" sub-agent that runs continuously and dispatches**: massive overdesign for a problem that's solved by relocating text.
- **Add a hook that auto-loads atlas-entity body at session start**: turns a documentation-organization problem into a runtime-system change. Skill bodies are gated for a reason (token cost, attention dilution); bypassing the gate solves the symptom and recreates the problem elsewhere.
