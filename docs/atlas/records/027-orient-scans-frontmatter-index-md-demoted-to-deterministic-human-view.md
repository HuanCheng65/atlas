---
id: 27
title: Orient scans frontmatter; _index.md demoted to deterministic human view
date: 2026-06-12
type: decision
tags: [orient, data-model, indexes, determinism]
---

# Orient scans frontmatter; _index.md demoted to deterministic human view

## Context

atlas-orient currently regex-parses `_index.md` files, which are themselves regex-generated from frontmatter — a derived view of a derived view. Entity status changes are hand-edits that don't auto-reindex, so a stale index makes orient silently underreport (empty sections render as "(none)"), exactly the silent-failure class the project's own principles forbid. The supposed IO benefit doesn't exist: orient already opens every listed entity file to pull headline sentences. Separately, the committed index content depends on the run date — the "Recent closed (last 14 days)" section is computed from `datetime.now()`, so a reindex on any later day produces diffs unrelated to the actual change (observed concretely during the 2026-06-12 bug-fix batch, when all late-May entries slid out of the window at once). The design notes already flagged index merge conflicts as an open concern.

## Decision

atlas-orient (and any agent-facing read) sources state directly from entity and journal frontmatter instead of `_index.md`, and `_index.md` files are demoted to deterministic human-only browse views whose content depends solely on frontmatter — never on the run date; time-dependent rendering such as the 14-day recency window moves into orient's render-time logic.

## Rationale

- Agent behavior should read facts, not derived views: removing the index from the agent path eliminates the staleness/silent-underreport failure mode structurally rather than by adding freshness checks.
- Time-dependent filtering belongs in the layer that is recomputed on every use (orient), not in a committed artifact; a deterministic index means identical data always yields an identical file — clean diffs, much smaller merge-conflict surface across machines.
- The index keeps its genuine value — browsable state without running a script — so it stays git-tracked; the `.gitignore` + always-regenerate fallback from the design notes remains available if conflicts persist anyway.

## Consequences

- orient.py is reworked to scan `decisions/`, `questions/`, `experiments/`, and `journal/` frontmatter directly; this lands together with the [[026-decisions-stay-adr-events-standing-rules-promote-into-project-md]] menu changes so orient is rebuilt once.
- Both reindex scripts drop run-date-dependent sections (journal's 14-day window); by-status / by-tag / by-month full listings remain.
- Index staleness is no longer detected by any consumer — accepted, because the index is now human-only and a day of staleness is harmless; atlas-compact can regenerate indexes as part of its periodic run.
- [[023-progressive-disclosure-data-layer-title-is-the-menu-body-loa]]'s "title is the menu" principle is unchanged; what narrows is who reads the rendered menu file: derived views are for humans, the agent reads the facts they derive from.

## Alternatives considered

- **`.gitignore` + always-regenerate** — rejected for now: loses browsability without running a script (e.g. reading the repo on GitHub); kept as the documented fallback if index merge conflicts persist even after determinism.
- **Keep orient on `_index.md` but add a staleness check** (compare index mtime against entity files) — rejected: adds machinery to defend an indirection that buys nothing, since orient opens the entity files anyway.
