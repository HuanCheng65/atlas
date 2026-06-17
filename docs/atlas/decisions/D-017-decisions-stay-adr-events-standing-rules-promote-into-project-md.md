---
id: D-017
title: Decisions stay ADR events; standing rules promote into PROJECT.md
date: 2026-06-12
status: active
triage: promoted
tags: [data-model, decisions, project-md, progressive-disclosure]
related: [D-012, D-013, D-016]
source-journal: 2026-06-12-resolve-design-review-findings.md
supersedes: []
superseded-by: []
affects: [atlas-orient, atlas-entity, atlas-compact, atlas-bootstrap]
---

# Decisions stay ADR events; standing rules promote into PROJECT.md

## Context

The active-decision list grows without bound (16 active Ds within the project's first weeks) while atlas-orient inlines every active D at session start. The root cause is a usage-model mismatch: atlas borrowed ADR's record format (Context / Decision / Rationale / Alternatives, supersede chains) but added a load-everything-every-session consumption pattern ADR practice never had — no team reads all ADRs each morning; they consult them on demand and keep in-force rules in a separate, curated principles document. The D list was silently serving both roles: archival event log and always-loaded rulebook. The split was already emergent in this repo: PROJECT.md's Hard constraints hand-duplicate the one-line forms of the two most foundational decisions.

## Decision

D-NNN records remain an ADR-style event log consulted on demand; any standing rule a decision establishes is promoted as a one-line statement with a `(D-NNN)` pointer into a curated constitution section of PROJECT.md (alongside Non-goals / Hard constraints), which orient inlines in full while the per-decision menu shrinks to recent, not-yet-reviewed entries.

## Rationale

- An agent has no enculturation. A human team absorbs in-force rules through review culture and rarely reopens the principles document; an agent is a newcomer every session, so standing rules need per-session injection — and the injection surface must be bounded and curated, which an append-forever log can never be.
- A decision is an *event* (its value is the rationale, consulted when revisiting); a principle is a *rule in force* (its value is the statement, needed during all future work). In git terms: `decisions/` is the commit log, the constitution is the checked-out working tree — you don't read every commit at session start.
- This is the data-layer application of the same insight already recorded for skills in D-013: what must influence behavior lives in an always-loaded surface; what is consulted on demand lives in bodies.
- A hand-curated constitution text beats a frontmatter query: deliberate editing is the quality source. The Hard constraints section already proved the form works.

## Consequences

- PROJECT.md gains a curated standing-rules section; the PROJECT.md template and atlas-bootstrap's Round A need to learn it.
- atlas-orient's decision menu shrinks to recent / not-yet-reviewed Ds; orient keeps inlining the constitution sections in full.
- atlas-compact gains a duty: review new Ds, propose promotion into the constitution or leave them archival.
- validate.py should check that constitution pointers reference existing, still-active Ds (mechanical drift guard between the two surfaces).
- Accepted cost: a promoted rule lives in two places (constitution line + D record); supersede must touch both — to be mechanized rather than left to agent discipline.
- Working promotion test, to harden during dogfood: *does violating the rule produce visible resistance?* A decision fully embodied in code resists violation on its own (you'd have to visibly rewrite things) and stays archival; a pure behavioral constraint produces no resistance when violated and must be promoted.
- Implementation is deferred until the remaining design-review findings about orient (direct frontmatter scan, deterministic index) settle, so the orient rework lands once.

## Alternatives considered

- **Tier/status field on D** ("embodied" / "core") with orient filtering — rejected: simulates curation through frontmatter, loses deliberate editing as the quality source, and keeps both roles mixed in one directory.
- **Separate Principle entity type (P-NNN)** — rejected: every recognition moment would carry a fuzzy D-vs-P classification burden, and a fourth entity type cuts against the small-learnable-methodology goal.
- **Relevance-filtering the D menu by session topic** — rejected: orient runs at session start, before work intent is known; it cannot know what is relevant yet.
