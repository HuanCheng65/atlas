# Project: Atlas

<!--
This file is the project's constitution. Read by agents at session start
(via CLAUDE.md). Keep stable — short-term plans go in docs/atlas/ROADMAP.md.
-->

## Background

Atlas is an operational-memory framework for long-running AI-assisted projects,
research and dev alike. It counters three failure modes that compound over time:

1. **Context rot** — agent quality degrades as session length grows
2. **Cross-session amnesia** — each new session starts blank, decisions lost
3. **Decision drift** — past architectural choices get unintentionally reversed

Existing solutions each miss something. Superpowers enforces TDD and a six-phase
workflow even for trivial tasks. grill-me solves task-start ambiguity but
nothing afterwards. GSD targets context rot but not decision lifecycle. Workshop
captures decisions but lacks supersede semantics.

Atlas emerged from extended discussion (May 2026) between Echo and Claude, distilling a personal
AI-assisted workflow into reusable conventions and tooling.

## Long-term goals

- A small, learnable methodology that supports both research and dev projects
- Plain-text data layer that survives tool churn (no DB lock-in, no vector store)
- Skill layer that is genuinely reusable across projects via user-level install
- Dogfooded by its own development; never ship a feature atlas itself wouldn't use

## Non-goals

- Team-scale collaboration (locking, multi-user merge, permissions)
- Marketing or community building; this is a personal tool
- Comparative benchmarking against Superpowers / GSD / others
- Strict TDD or fixed-phase workflow enforcement
- Semantic retrieval via vector DB (ripgrep + frontmatter covers 80% at zero cost)
- Plugin marketplace distribution (deferred until there's a clear audience)

## Hard constraints

- Plain text + git only; no databases, no external services (D-001)
- Python + pyyaml + bash as the only runtime dependencies
- Skills are user-level (cross-project); data is project-level (lives with the repo) (D-002)
- Maintenance overhead must stay low enough for one person to sustain indefinitely

## Working rules

<!-- The constitution: standing rules currently in force, promoted from
     decisions. One line per rule, ending with its (D-NNN) pointer back to
     the full record. validate.py enforces the pairing both ways. -->

- Skills activate on events, never on session phases (D-007)
- Every plan declares Verification; artifacts are classified Keepers vs Throwaways (D-008)
- One skill per cognitive domain; deterministic operations live in scripts (D-009)
- Title is the menu: every entity/journal title carries the decision signal; bodies load on demand (D-012)
- Triggers live in persistently-loaded surfaces, never only in skill bodies (D-013)
- Distributed skill bodies never cite this project's entity IDs; reasoning stated inline (D-015)
- PROJECT.md is authored for extraction: first sentences self-contained; mutable status lives in ROADMAP (D-016)
- New decisions get triaged: standing rules promote here, events stay archival — test: does violating it produce visible resistance? (D-017)
- Agent rules become mechanisms (script defaults/refusals, hooks, validators) wherever possible; prose is for judgment calls (D-020)
- Atlas changes ride the work unit's own commits; atlas-only commits only when atlas content is itself the work (D-021)

## Glossary

- **atlas** — this project's name; also the per-project data directory `docs/atlas/`
- **Entity** — structured record with frontmatter and lifecycle; one of D-NNN / E-NNN / Q-NNN
- **D-NNN (Decision)** — long-term architectural or strategic choice
- **E-NNN (Experiment)** — research run with hypothesis, config, result
- **Q-NNN (Question)** — open question awaiting resolution
- **Journal** — append-only time-ordered event log at `docs/atlas/journal/`
- **Topic** — free-form derived knowledge note at `docs/atlas/topics/`; emerges from journal patterns
- **Compact** — maintenance pass that clears backlog (stale actives, pending triage, aging questions) and consolidates the store (merges, closes, topics, wording); runs without per-item confirmation, lands as one revertable commit
- **Keeper / Throwaway** — classification of verification artifacts as long-term regression vs development-time scaffold
- **Supersedes chain** — audit trail of decision evolution (D-A → D-B → D-C)
- **Working rules** — the constitution section of PROJECT.md: standing rules currently in force, one line each, pointing back to the decision that established it
- **Triage** — a decision's review state: pending (awaiting review, shown in orient's menu), promoted (one-line rule in Working rules), or archival (event record consulted on demand)

## Collaborators & stakeholders

- **Echo** — primary user, designer, dogfooder; brings the research use case and the dev use case
- **Claude** — co-designer via chat; the design conversations are themselves atlas-relevant artifacts

## Current stage

prototype — see docs/atlas/ROADMAP.md for the current milestone.

## References

- Anthropic Agent Skills documentation
- obra/superpowers (skills framework; heavy TDD-enforced workflow)
- Rick Hightower's GSD (context-rot focused, spec-driven)
- Matt Pocock's grill-me (reverse-interrogation brainstorm)
- zachswift615/workshop (auto-captured cross-session memory)
- Architecture Decision Records (ADR) — https://adr.github.io
- Event sourcing pattern (append-only log + derived views)