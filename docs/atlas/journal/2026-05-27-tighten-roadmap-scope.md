---
date: 2026-05-27
slug: tighten-roadmap-scope
project: atlas
tags: [roadmap, skills, data-model, dogfood]
status: closed
opened: 2026-05-27 21:30
closed: 2026-05-27 23:10
verification-result: passed
related: [D-010]
---

# Tighten ROADMAP scope + plug the journal-bootstrap gap

## Context

*(retroactive — this entry was backfilled at the end of the session, after we
realized the work had been happening without journal coverage. The Work log
below reconstructs the timeline from conversation memory; timestamps are
approximate.)*

The conversation started as an exploratory question — "do we really need
`ROADMAP.md`, and if yes, who maintains it?" Discussion converged on
trimming the roadmap to a single section (Current milestone) because the
other sections duplicated state that already lived in D-NNN / Q-NNN /
closed journal entries / `git log`. Executing that change surfaced two
follow-on problems: (1) an `atlas-entity` UX bug that made me write an
illegal `status: accepted` on a new decision, and (2) a deeper flow bug —
this entire work session ran without ever opening a journal entry,
exposing a missing trigger between "exploration" and "action" in the
atlas skill set.

## Work log

### 2026-05-27 21:35 — Roadmap audit

Read `docs/atlas/ROADMAP.md`. Identified concrete duplication:
- Backlog item "Multi-machine sync" duplicates [[Q-003]]
- Backlog item "Topic-sealing flow" duplicates [[Q-002]]
- "Recently done" section duplicates closed journal entries + D index +
  `git log`
- "Up next" duplicates the Current milestone narrative phrased as bullets

Parallel-session angle (raised by user, sharpened together): a shared
ordered list is a merge-conflict hazard across parallel sessions, which
directly conflicts with [[D-006]] (multiple active journal entries
allowed). Per-entity files don't share a mutable list, so they don't
conflict. Removing the queue also removes the implicit serial-order
assumption.

### 2026-05-27 21:55 — D-010 created

Created `D-010 Roadmap holds only Current milestone — no Up next, Backlog,
or Recently done` via `atlas-entity new.py`. Filled Context / Decision /
Rationale / Consequences / Alternatives. Linked to [[D-006]], [[Q-002]],
[[Q-003]].

First attempt set `status: accepted` (ADR convention), which failed
`validate.py` with `illegal status 'accepted' for type D`. Corrected to
`active`. Noted as a skill-UX issue for follow-up.

### 2026-05-27 22:05 — ROADMAP.md trimmed

Rewrote `docs/atlas/ROADMAP.md` to one section (Current milestone), with
a top note pointing at D-010 for the rationale. Up next, Backlog,
Recently done all removed. Backlog ideas that weren't already real open
questions (`atlas-init --research/--dev`, `atlas-search`, schema
migration, plugin marketplace) were dropped, not promoted — per D-010,
"may do someday" doesn't earn durable storage.

`reindex.py` + `validate.py` clean. 15 entities check.

### 2026-05-27 22:20 — Skill-UX fix in atlas-entity

Tracked down why `status: accepted` happened:
- `SKILL.md` did not inline the legal status values — it deferred to
  `reference/lifecycle.md`, which the agent (me) didn't read first
- The "Long-term decision made" workflow had no step for flipping from
  `planned` (template default) to `active` (real state for new D-NNN),
  even though D-001..D-009 are all `active`

Fix: added a step "Set `status: active`" between filling the body and
running supersede/close-question. Inlined the legal status values for D /
E / Q with an explicit callout that atlas uses `active`, not
`accepted`/`adopted`/`approved`.

### 2026-05-27 22:40 — Downstream propagation cleanup

Audited where the old ROADMAP structure still propagated:
- `templates/ROADMAP.md` (installed into new atlas projects by
  `atlas-init`): rewrote to match D-010, with a top-comment guardrail
  warning future users not to re-introduce Up next / Backlog / Recently
  done
- `skills/atlas-orient/scripts/orient.py`: dropped "Up next" reporting;
  also fixed a case-sensitivity hazard (`roadmap.md` → `ROADMAP.md` —
  worked on macOS, would break on Linux)
- `skills/atlas-orient/SKILL.md`: updated the "what the summary contains"
  description to reflect the trimmed roadmap

Verified by re-running orient — output clean, Roadmap section now shows
only Current milestone.

`atlas-bootstrap` was checked too — it references ROADMAP.md only as a
file path, doesn't enumerate sections, so no change needed there.

### 2026-05-27 23:00 — Meta-bug: no journal entry for this work

User pointed out: all of the above happened without ever opening a
journal entry. Root-cause diagnosis:

- Conversation started as an exploratory question, which routes through
  the "exploratory → 2-3 sentence response" rule, not through `grill-me`
- When discussion converged on a concrete action ("可以,动手吧"), there
  was no skill trigger for the exploration → action transition
- Once `grill-me` was skipped, the rest of atlas (atlas-log, atlas-entity)
  had no recovery hook to retroactively bootstrap an entry. D-010 was
  created with `source-journal: null` and the skill didn't flag that as
  a smell.

User addressed this directly by inventing a new top-level skill,
**`using-atlas`**, as the canonical session-entry point:
- Auto-loaded at the start of every atlas session
- Runs `atlas-orient` silently, then enters "watching mode"
- When work intent becomes clear (concrete artifacts coming), bootstraps
  a journal entry
- Critically: if it deferred for several exchanges before bootstrapping,
  the Context section must include a `(retroactive — from earlier in
  this conversation)` paragraph so context isn't lost

Also touched up `atlas-orient` (no longer claims to be the session-entry
point — that's `using-atlas`'s job now) and `atlas-log` (now explicitly
has a fallback path to create an entry if `using-atlas` was skipped).

### 2026-05-27 23:08 — Backfill journal entry (this one)

Per `using-atlas`'s retroactive rule, this entry is the backfill for
the whole session. Written from conversation memory rather than live
logging; structure follows what would have existed if `using-atlas` had
been running from the start.

## Close

### Outcome
Roadmap scope tightened (single source of truth per concept), and the
underlying skill-flow gap that let this work happen un-journaled was
identified and patched in the same session.

### Verification result
`passed` — informal: `reindex.py` + `validate.py` clean across 15
entities + 1 journal entry; `orient.py` output matches the trimmed
ROADMAP; no broken references. No formal Verification criteria were
defined up front because this work skipped `grill-me`.

### Keepers (finalized)
- `D-010` — roadmap-scope decision with full rationale, including the
  parallel-session argument
- Trimmed `docs/atlas/ROADMAP.md`
- Trimmed `templates/ROADMAP.md` (with anti-rot guardrail comment)
- `atlas-entity/SKILL.md` — inline legal statuses + new "Set status:
  active" step
- `atlas-orient/scripts/orient.py` — Up next reporting removed,
  case-sensitivity fixed
- `atlas-orient/SKILL.md` — updated section description (user further
  refined to drop the "PROACTIVELY at session start" framing now that
  `using-atlas` owns that role)
- New `using-atlas/SKILL.md` — canonical session-entry point
- `atlas-log/SKILL.md` — fallback bootstrap path documented

### Throwaways (deleted)
- ROADMAP "Up next" / "Backlog" / "Recently done" sections
- Soft backlog items that weren't real open questions
  (`atlas-init --research/--dev` differentiation, `atlas-search` skill,
  schema migration tooling, plugin marketplace)

### Spawned entities
- `D-010` created
- No new Q raised in atlas itself for the journal-bootstrap gap — the
  fix landed in-session via `using-atlas`, so it's a closed issue, not
  an open one. If the new skill turns out to under-trigger in practice,
  a Q can be raised then.
