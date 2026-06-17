---
id: D-022
title: "atlas-compact: keep the store healthy, apply without confirmation"
date: 2026-06-12
status: active
triage: archival
tags: [skills, compact, agent-behavior, topics]
related: [D-017, D-020, D-021]
source-journal: 2026-06-12-implement-atlas-compact.md
supersedes: []
superseded-by: []
affects: [atlas-compact, atlas-orient, atlas-log, atlas-bootstrap]
---

# atlas-compact: keep the store healthy, apply without confirmation

## Context

Before any design existed, five duties had been informally assigned to compact across the docs: topic distillation, stale-entry detection, decision triage review, index regeneration, and bootstrap-extras follow-up — a junk-drawer trajectory. The design discussion found the real shape: two halves of one job (process the backlog of unhandled items; consolidate existing records that have gone stale, duplicated, or fragmented), with bootstrap-extras removed (a one-time onboarding leftover, not a recurring concern). On confirmation, the user observed that per-item confirmation degenerates into reflexive "没问题" replies — nobody actually reviews proposals in chat — and that compact differs from grill-me in kind: grill-me extracts information that exists only in the user's head, while compact reorganizes information already in the repo, where the user's sign-off adds nothing a git diff doesn't show better.

## Decision

atlas-compact keeps the memory store small, current, and true — processing backlog (stale active entries, pending-triage decisions, aging open questions) and consolidating existing records (merging/superseding overlapping decisions, closing implicitly-answered questions, distilling recurring journal themes into topics, refreshing Glossary and PROJECT.md wording) — and it runs end-to-end without per-item confirmation: a scan script finds candidates, the agent judges, existing scripts apply, validate must pass, and the whole run lands as one revertable atlas-only commit.

## Rationale

- Confirmation that always gets rubber-stamped is not a safety mechanism; the reviewable artifact is the diff, and post-hoc diff review carries more information at lower cost than pre-hoc proposal review.
- The information asymmetry that justifies grill-me's interview (the user knows things the agent cannot) is absent here: everything compact acts on is already in the repo.
- Mechanical guards replace social ones, consistent with the mechanisms-over-prose principle: scripts refuse illegal transitions, validate gates the commit, and a single commit makes the entire run atomically revertable.
- Consolidation never rewrites history: superseded decisions keep their text, closed journal entries stay frozen, distillation writes new topic files — so this composes with the decisions-are-ADR-events model.

## Consequences

- Bounded write set: new files (topics, merged decisions), status/triage flips, link and pointer edits, Glossary/PROJECT.md wording — never deleting files, never rewriting journal bodies or old decision texts.
- A compact run is an atlas-only commit, which the no-framework-events convention explicitly permits (atlas content is itself the work); the commit message names what was consolidated.
- Invoking compact authorizes its whole action class — the same logic as "an explicit close command is the confirmation" in atlas-log; the skill states this so the two rules don't appear to conflict.
- orient gains a backlog hint (stale actives + pending triage counts) so runs are prompted by visible debt instead of a calendar.
- No automatic topic-extraction heuristic (this answers the open question about it): the scan reports tag clusters as data; whether a cluster deserves a topic is a judgment call, which is exactly what prose/agent reasoning is reserved for.
- v1 is on-demand only; true background runs (scheduled, self-committing) become possible once unconfirmed application exists, but are deferred until multi-machine sync implications are thought through.
- bootstrap-extras.md is out of scope: the user processes or deletes it at leisure.

## Alternatives considered

- **Per-item confirmation (propose, wait, apply)** — rejected: degenerates into rubber-stamping; adds a human bottleneck without adding review.
- **Automatic topic-extraction heuristic** (N entries sharing a tag within K days → topic) — rejected: forces a judgment call into a mechanism, the inverse error of leaving deterministic work to prose.
- **Fixed weekly schedule** — rejected: becomes an ignored calendar item; orient's backlog hint ties runs to visible need.
- **Background auto-dream in v1** — deferred, not rejected: nothing blocks it after this design, but unattended commits on multi-machine setups need thought first.
