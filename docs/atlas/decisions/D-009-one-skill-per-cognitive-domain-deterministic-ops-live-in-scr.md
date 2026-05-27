---
id: D-009
title: One skill per cognitive domain; deterministic ops live in scripts
date: 2026-05-27
status: active
tags: [skills, architecture]
related: [D-007]
source: bootstrap
source-journal: null
supersedes: []
superseded-by: []
affects: []
---

# One skill per cognitive domain; deterministic ops live in scripts

## Context

A skill per action (new-decision, supersede, reindex, ...) leads to a sprawl
of nearly-identical skill manifests and forces the agent to pick the right
one. Conversely, a single mega-skill mixes unrelated concerns. Both hurt
discoverability and maintenance.

## Decision

Each cognitive domain (managing entities, journaling, orienting, bootstrapping,
brainstorming) gets exactly one skill. Inside the skill, deterministic
mechanical operations (ID assignment, frontmatter edits, validation, indexing)
live in scripts under `scripts/`; the skill prompt handles judgment calls
(whether something deserves to be a D-NNN, whether to append, etc.).

## Rationale

- Skills are organized by what the agent reasons about, not by individual
  actions; this matches how the work actually flows.
- Scripts give deterministic, testable mechanics — no LLM tokens spent on
  string substitution or counter bumping.
- Each skill's reference/ subdirectory keeps domain knowledge close to where
  it's needed.

## Consequences

- atlas-entity owns D/E/Q creation, supersession, indexing, validation.
- atlas-log owns journal appends, closes, and lifecycle of journal entries.
- Cross-skill code sharing is currently low and intentional; revisit if
  duplication grows (see Q-005).

## Alternatives considered

- One skill per action — rejected; same cognitive domain belongs in one skill.

Evidence: `docs/design.md` "One domain, one skill" / "Scripts for the
deterministic, prompts for the judgment" principles; rejected
"One skill per action" bullet.
