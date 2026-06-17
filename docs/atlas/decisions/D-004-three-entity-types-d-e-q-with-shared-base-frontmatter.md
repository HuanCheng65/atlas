---
id: D-004
title: Three entity types D/E/Q with shared base frontmatter
date: 2026-05-27
status: active
triage: archival
tags: [data-model]
related: [D-001]
source: bootstrap
source-journal: null
supersedes: []
superseded-by: []
affects: []
---

# Three entity types D/E/Q with shared base frontmatter

## Context

Atlas tracks several distinct kinds of long-lived knowledge: architectural
decisions, research experiments, and open questions awaiting resolution. Each
has its own lifecycle and required fields, but they share enough metadata that
a single base schema makes tooling (indexing, validation, retrieval) simpler.

## Decision

Three entity types — Decision (D), Experiment (E), Question (Q) — each with
its own directory and lifecycle, sharing a common base frontmatter
(`id`, `title`, `date`, `status`, `tags`, `related`, `source-journal`) plus
per-type extensions. Each has its own template and state machine.

## Rationale

- One shared base means `validate.py` and `reindex.py` work uniformly.
- Per-type extensions capture domain specifics (`supersedes` for D,
  `hypothesis/config/result` for E, `answered-by` for Q).
- Three types cover the observed kinds of long-lived state without
  proliferating sub-types.
- Separate directories give browsable, focused listings.

## Consequences

- Adding a new entity type requires updating templates, lifecycle reference,
  and validate.py. The base schema discourages doing this lightly.
- Experiments stay in their own directory rather than as journal sub-entries,
  improving discoverability for paper writing.

## Alternatives considered

- Experiments as a journal sub-type (`type: experiment`) — rejected; separate
  `experiments/` directory gives better browse experience.
- One unified entity type with a `kind` field — rejected; loses per-type
  lifecycle semantics and directory-level browsing.

Evidence: `docs/design.md` "Entities (D / E / Q)" section and rejected
"Experiments as journal sub-type" bullet; `skills/atlas-entity/reference/lifecycle.md`.
