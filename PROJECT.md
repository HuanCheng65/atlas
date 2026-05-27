# Project: Atlas

<!--
This file is the project's constitution. Read by agents at session start
(via CLAUDE.md). Keep stable — short-term plans go in docs/atlas/ROADMAP.md.
-->

## Background

Long-running AI-assisted projects (research, app dev) suffer from three
recurring failure modes:

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

- Plain text + git only; no databases, no external services
- Python + pyyaml + bash as the only runtime dependencies
- Skills are user-level (cross-project); data is project-level (lives with the repo)
- Maintenance overhead must stay low enough for one person to sustain indefinitely

## Glossary

- **atlas** — this project's name; also the per-project data directory `docs/atlas/`
- **Entity** — structured record with frontmatter and lifecycle; one of D-NNN / E-NNN / Q-NNN
- **D-NNN (Decision)** — long-term architectural or strategic choice
- **E-NNN (Experiment)** — research run with hypothesis, config, result
- **Q-NNN (Question)** — open question awaiting resolution
- **Journal** — append-only time-ordered event log at `docs/atlas/journal/`
- **Topic** — free-form derived knowledge note at `docs/atlas/topics/`; emerges from journal patterns
- **Compact** — periodic operation that proposes entity promotions and topic distillations
- **Keeper / Throwaway** — classification of verification artifacts as long-term regression vs development-time scaffold
- **Supersedes chain** — audit trail of decision evolution (D-A → D-B → D-C)

## Collaborators & stakeholders

- **Echo** — primary user, designer, dogfooder; brings the research use case and the dev use case
- **Claude** — co-designer via chat; the design conversations are themselves atlas-relevant artifacts

## Current stage

prototype — phase 1 (atlas-entity skill + data templates + install/init scripts) is
implemented and ready to dogfood; phase 2 (session-lifecycle skills + grill-me port +
verification enforcement) being designed.

## References

- Anthropic Agent Skills documentation
- obra/superpowers (skills framework; heavy TDD-enforced workflow)
- Rick Hightower's GSD (context-rot focused, spec-driven)
- Matt Pocock's grill-me (reverse-interrogation brainstorm)
- zachswift615/workshop (auto-captured cross-session memory)
- Architecture Decision Records (ADR) — https://adr.github.io
- Event sourcing pattern (append-only log + derived views)