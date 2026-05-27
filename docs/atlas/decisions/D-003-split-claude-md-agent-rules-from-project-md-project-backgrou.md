---
id: D-003
title: Split CLAUDE.md (agent rules) from PROJECT.md (project background)
date: 2026-05-27
status: active
tags: [docs, agent-onboarding]
related: []
source: bootstrap
source-journal: null
supersedes: []
superseded-by: []
affects: []
---

# Split CLAUDE.md (agent rules) from PROJECT.md (project background)

## Context

A common pattern is to dump everything an AI agent should know into a single
CLAUDE.md. That conflates two things with different audiences, lengths, and
change frequencies: agent operating rules vs. the project's standing
constitution (background, goals, constraints).

## Decision

Keep two files at the project root:

- `CLAUDE.md` — agent operating rules; short, frequently amended; managed
  additively by `atlas-init` via a marker-delimited block.
- `PROJECT.md` — project constitution; longer, stable, edited by humans.

## Rationale

- Different audiences read each file: agents read CLAUDE.md every session;
  PROJECT.md is the human-authored "why we exist".
- Different change frequency means mixing them creates noisy diffs.
- `atlas-init` can safely touch CLAUDE.md (marker block) without risking
  user-authored PROJECT.md content.

## Consequences

- `atlas-init` is idempotent on CLAUDE.md and only creates PROJECT.md when missing.
- Onboarding skills (`atlas-orient`) can load PROJECT.md once per session as background context.

## Alternatives considered

- Single CLAUDE.md as both rules and background — rejected; different
  audiences, lengths, and change frequencies.

Evidence: `docs/design.md` "Single CLAUDE.md as both agent rules and project background" bullet; Architecture diagram footnote.
