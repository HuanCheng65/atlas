---
id: D-008
title: Verification + Keepers/Throwaways instead of enforced TDD
date: 2026-05-27
status: active
tags: [verification, workflow]
related: []
source: bootstrap
source-journal: null
supersedes: []
superseded-by: []
affects: []
---

# Verification + Keepers/Throwaways instead of enforced TDD

## Context

Strict TDD works well for business logic but fits poorly with research code,
LLM applications, and exploratory work. Meanwhile AI-written tests tend to be
surface-level scaffolds that pass once, never catch regressions, and clutter
the repo forever. The problem is twofold: discipline (a clear completion bar)
and hygiene (knowing what stays vs. what goes).

## Decision

Every plan produced by grill-me must declare a Verification approach
(unit test, reference comparison, eval set, manual checklist, ...) and
classify verification artifacts as Keepers (long-term regression assets) or
Throwaways (development-time scaffolds to delete). Keepers/Throwaways are
proposed in the Plan section and finalized by atlas-log at Close.

## Rationale

- A declared verification standard prevents "shipped without a check" without
  prescribing a specific test style.
- Explicit Keeper/Throwaway classification stops one-shot scaffolds from
  accumulating in the repo.
- Verification form varies by task; the framework lets the agent and user
  pick what fits (eval set for LLM apps, reference-impl comparison for kernels,
  unit tests for business logic).

## Consequences

- grill-me output must include Verification and proposed Keepers/Throwaways.
- atlas-log Close confirms the final Keepers/Throwaways lists with the user.
- Lists may shift during work — what seemed throwaway may become a keeper, and vice versa.

## Alternatives considered

- Strict TDD enforcement (Superpowers-style) — rejected; too rigid for
  research code and LLM apps.

Evidence: `docs/design.md` "Verification: Keepers vs Throwaways" section and
rejected "Strict TDD enforcement" bullet.
