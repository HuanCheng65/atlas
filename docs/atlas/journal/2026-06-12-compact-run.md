---
date: 2026-06-12
slug: compact-run
project: Atlas
tags: [compact, maintenance]
status: closed
opened: 2026-06-12 18:31
closed: 2026-06-12 18:32
verification-result: passed
related: []
---

# Compact run

## Context

Maintenance pass over the store. Agenda from scan: 1 decision pending triage (D-022), 5 open questions (19 tag-overlap "possibly answered" hints), 17 decision pairs sharing >=2 tags, 7 tag clusters as topic candidates, 0 stale active entries. Judged each against the actual files.

## Work log

### 2026-06-12 18:31
Triaged D-022 as archival: its rule (compact runs unconfirmed, bounded writes, one commit) is embodied in the atlas-compact skill body itself — the mechanism per D-020 — and constrains only compact runs, not everyday work, so it fails the promotion test; matches the archival precedent of D-011/D-014 (skill-behavior decisions). Fixed Glossary drift: "Compact" still read "proposes entity promotions and topic distillations" — pre-D-022 wording; reworded to backlog + consolidation, unconfirmed, one commit. No question closes: all 19 scan hints were tag coincidences (Q-001 threshold still unvalidated, Q-003 sync explicitly deferred by D-022, Q-004 has no collected examples yet, Q-005 duplication not yet painful, Q-006 opened today). No decision merges: all 17 pairs are distinct rules; the highest-overlap pairs (D-007+D-019, D-011+D-021) already carry related links. No topics: the reusable knowledge in every cluster was already distilled into D-007..D-022 and Working rules; the journal bodies are work history, not re-derivable knowledge. Left the implement-design-review-decisions entry active — opened today, in flight. Reindexed both, validate OK (28 entities). Commit skipped: docs/atlas and PROJECT.md already carried uncommitted changes from in-flight work, so the run cannot land as its own clean commit.

## Close

Run complete: D-022 triaged archival, Glossary "Compact" entry refreshed, no closes/merges/topics (all judged not warranted), validate clean. Commit deliberately skipped — atlas paths were already dirty from in-flight work; changes ride the working tree for the user to commit with that work or separately.
