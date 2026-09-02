---
id: 28
title: Mechanical affordances over prose constraints for agent rules
date: 2026-06-12
type: decision
tags: [skills, agent-behavior, enforcement, design-principle]
---

# Mechanical affordances over prose constraints for agent rules

## Context

The project's own dogfood history shows two diverging trajectories for agent behavioral rules. Rules that became mechanisms stabilized: timestamps stopped being fabricated once scripts owned them; session-start setup stopped being skipped once a blocking hook demanded it. Rules that stayed prose decayed and required escalating emphasis: the "don't narrate the setup sequence" instruction was patched with stronger wording for the third time during the 2026-06 design review. The same review found the journal's `project:` field spelled three ways across one repo (`Atlas` / `atlas` / `Kairos`) — the measured cost of a flag the script could derive — and a rule collision (grill-me telling the agent to Edit `tags`/`related` while atlas-log's prose banned all frontmatter edits) caused by a rule stated broader than its actual intent.

## Decision

When an agent behavioral rule can be enforced or made unnecessary by a mechanism — a script default, a script refusal, a hook, a validator check — atlas builds the mechanism, and prose instructions are reserved for genuine judgment calls rather than used as the default enforcement layer.

## Rationale

- Prose decays: agents drift, emphasis escalates with shrinking marginal returns, and overlapping prose rules collide; a mechanism enforces the same way on the thousandth session as on the first.
- Mechanisms make the correct path the cheap path (open.py vs hand-written frontmatter), so compliance stops competing with convenience.
- When prose is genuinely needed, precision beats volume: narrowing a rule to its true scope (script-owned *fields*, not all frontmatter) resolves collisions that repetition cannot.

## Consequences

- First applications: (1) `open.py` derives the project name from PROJECT.md's H1, with `--project` demoted to an explicit override — eliminating the spelling drift at the root; (2) atlas-log's frontmatter-edit ban narrows to the script-owned fields (`opened`, `closed`, `status`, `verification-result`, and `### YYYY-MM-DD HH:MM` Work log headers), with `tags`/`related` explicitly editable — dissolving the grill-me/atlas-log collision.
- Every future skill patch for an agent failure mode starts with "can this be a mechanism?"; adding louder prose is the fallback, not the reflex.
- Under the [[026-decisions-stay-adr-events-standing-rules-promote-into-project-md]] promotion test this rule is a constitution candidate of the archetypal kind: violating it produces no visible resistance, so it must live in the always-loaded surface.
- Accepted limitation: this decision is itself prose; its enforcement point is the review moment ("can this be a mechanism?"), which cannot itself be mechanized.

## Alternatives considered

- **Keep escalating prose emphasis** — rejected: the third escalation of the same instruction was already observed; the trend line is the argument.
- **Mechanize everything via hooks/validators** — rejected: judgment calls (when to log, what qualifies as a decision, when grilling is done) genuinely require reasoning; mechanisms cover the deterministic subset only.
