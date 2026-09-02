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

- Plain text + git only; no databases, no external services ([[001-plain-text-git-as-the-data-layer]])
- Python + pyyaml + bash as the only runtime dependencies
- Skills are user-level (cross-project); data is project-level (lives with the repo) ([[002-skills-user-level-data-project-level-via-symlink-install]])
- Maintenance overhead must stay low enough for one person to sustain indefinitely

## Working rules

<!-- Rules in force that no mechanism enforces. A rule belongs here exactly
     when nothing stops the agent from violating it: if a script, hook or
     validator can catch it, write the check instead. One line per rule,
     ending with a link to the record that justifies it. Authored by hand —
     nothing is promoted here automatically. -->

- Skills activate on events, never on session phases ([[013-event-driven-skill-activation-not-session-phase-driven]])
- Every plan declares Verification; artifacts are classified Keepers vs Throwaways ([[006-verification-keepers-throwaways-instead-of-enforced-tdd]])
- One skill per cognitive domain; deterministic operations live in scripts ([[007-one-skill-per-cognitive-domain-deterministic-ops-live-in-scr]])
- Title is the menu: every record title carries the claim; bodies load on demand ([[023-progressive-disclosure-data-layer-title-is-the-menu-body-loa]])
- Triggers live in persistently-loaded surfaces, never only in skill bodies ([[024-triggers-live-where-the-agent-always-sees-them-not-in-skill]])
- Distributed skill bodies never cite this project's record numbers; reasoning stated inline ([[025-distributed-skill-bodies-cite-reasoning-inline-never-this-pr]])
- PROJECT.md is authored for extraction: first sentences self-contained; mutable status lives in ROADMAP ([[008-author-project-md-for-orient-extraction-mutable-status-lives]])
- A record's truth may not depend on a future edit: state is derived, links point backwards, and a published record is superseded rather than changed
- Agent rules become mechanisms (script defaults/refusals, hooks, validators) wherever possible; prose is for judgment calls ([[028-mechanical-affordances-over-prose-constraints-for-agent-rules]])
- Atlas changes ride the work unit's own commits; atlas-only commits only when atlas content is itself the work ([[029-framework-generates-no-events-silent-ops-records-ride-work-commits]])

## Glossary

- **atlas** — this project's name; also the per-project data directory `docs/atlas/`
- **Record** — one file at `docs/atlas/records/NNN-slug.md`, on one counter shared by every type; frontmatter carries identity, the body carries the prose and every relation
- **Memory** — a record holding a constraint currently in force; its title is loaded into every session, and it is rewritten in place rather than superseded
- **Decision** — a record of a choice and the alternative it beat, in ADR form: context, decision, consequences
- **Experiment** — a record of a measurement: hypothesis, setup, result, conclusion
- **Question** — a record of something unresolved; answered when a later record declares an `answers` edge
- **Typed edge** — a relation written into a body sentence as `(supersedes:: [[NNN-slug]])`; changes how the target renders, and always points at a lower number
- **Derived state** — superseded, refuted, answered: computed from the edges pointing at a record, never stored in it
- **Publication boundary** — the commit: an uncommitted record is a draft and may be rewritten, a committed one is superseded instead
- **Compact** — maintenance pass in two jobs: rewriting the memory set within its budget, and reviewing script-computed candidates for records that stopped being true; runs without per-item confirmation, lands as one revertable commit
- **Keeper / Throwaway** — classification of verification artifacts as long-term regression vs development-time scaffold
- **Working rules** — the constitution section of PROJECT.md: rules in force that no mechanism enforces, one line each, linking to the record that justifies it

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