---
date: 2026-06-12
slug: implement-atlas-compact
project: Atlas
tags: [skills, compact, scripts, tests]
status: closed
opened: 2026-06-12 17:44
closed: 2026-06-12 17:51
verification-result: passed
related: []
---

# Implement atlas compact

## Context

Build atlas-compact, the last skill of the current milestone, to the design settled in this session: compact keeps the memory store small, current, and true — processing backlog (stale active entries, decisions pending triage, aging open questions) and consolidating existing records (merge/supersede overlapping decisions, close implicitly-answered questions, distill recurring journal themes into topics, refresh Glossary/PROJECT.md wording). It runs end-to-end without per-item confirmation: a scan script finds candidates, the agent judges, existing scripts apply the changes, validate must pass, and the whole run lands as one revertable atlas-only commit. bootstrap-extras follow-up was explicitly removed from its duties; topic detection uses no automatic heuristic (the scan reports tag clusters, judgment decides); v1 is on-demand with an orient backlog hint, background scheduled runs deferred.

## Decisions resolved

- Design recorded as D-022 (purpose, unconfirmed application, bounded writes, single-commit safety, orient-hint trigger); Q-002 closed by it (no automatic topic heuristic).
- Scan thresholds are parameters with defaults: stale active = 3 days (Q-001's current value, stays open for dogfood validation); tag clusters reported for all tags, flagged as topic candidates at ≥3 closed entries.
- Compact commits only the files it touched (docs/atlas/**, PROJECT.md); if those files carry unrelated uncommitted changes before the run, it reports and skips the commit instead of mixing.
- "Last compact run" is tracked by the compact run's own journal entry (tag: compact) — no extra state file.

## Steps

1. `skills/atlas-compact/scripts/scan.py`: print a markdown maintenance agenda — stale actives (latest work-log timestamp vs threshold), pending-triage decisions, open questions with ages, possibly-answered hints (open Q whose tags overlap journal entries closed after it), decision-overlap hints (active pairs sharing ≥2 tags), tag clusters over closed entries with existing topics listed, last compact run.
2. `skills/atlas-compact/SKILL.md`: run procedure (scan → judge → apply via existing scripts → validate → single commit → short report), invocation-is-authorization note, bounded-write list, what it never does, topic-writing guidance.
3. orient.py: append a backlog hint (counts of stale actives and pending triage) when nonzero.
4. Docs: README operations table and design.md drop "(planned)"; using-atlas routing row updated; roadmap exit criterion reworded (no heuristic).
5. Run install.sh to symlink the new skill; pytest coverage for scan.py; full suite + validate.

## Verification

- pytest: scan fixture asserts each agenda section — a 3-day-stale active is flagged while a fresh one isn't; pending-triage decisions listed; an open question whose tags overlap a later-closed entry appears as possibly-answered; two decisions sharing two tags appear as an overlap pair; a tag with 3 closed entries is flagged as a topic candidate; agenda is deterministic given a fixed --today.
- Real repo: scan runs clean and its agenda matches known state (pending triage = D-022, two active entries); validate OK; full suite green.

## Keepers (proposed)

- scan.py tests added to tests/.

## Throwaways (proposed)

- /tmp sandboxes.

## Work log

### 2026-06-12 17:51
Implementation complete. scan.py outputs the seven-section agenda (stale actives via latest work-log timestamp, pending triage, open questions with ages, possibly-answered hints, decision-overlap pairs, tag clusters with existing topics, last compact run dated by compact-tagged journal entries); --today flag makes it deterministic for tests. SKILL.md written around the authorization model (invocation authorizes the run; bounded writes; never deletes or rewrites history; never background), the seven-step run procedure (scan → dirty-tree check → judge → validate → journal the run → single commit → plain-language report), and judgment defaults (no-action is legitimate; honest results over passed-streaks; Working rules has a ~15-line budget). orient.py appends a maintenance-backlog hint when stale actives or pending-triage decisions exist. Docs updated everywhere compact was "(planned)"; roadmap exit criterion reworded; the two resolved open questions removed from design.md. install.sh linked the new skill. 9 new tests in tests/test_compact_scan.py; full suite 26 green; validate OK (28 entities).

Dry run on the real repo surfaced one tuning note for the dogfood week: hint sections weight all tags equally, so generic tags (skills, journal) produce noisy possibly-answered and overlap hints — 18 and 17 rows respectively, mostly weak. Acceptable for v1 since hints are data for judgment, but a frequency-based damping of overly-common tags is the obvious first tweak if it stays noisy.

## Close

**Outcome**: atlas-compact shipped to the agreed design — scan script, skill body, orient backlog hint, doc sync, and test coverage; the milestone's last skill now exists.

**Verification result**: All Plan verification items ran: pytest fixture asserts every agenda section including determinism under --today and the threshold flag (9 tests, full suite 26 green); real-repo dry run matches known state (1 pending triage = the compact design decision itself, 0 stale actives, hint sections populated); validate OK (28 entities).

**Keepers (finalized)**:
- tests/test_compact_scan.py (9 tests) joins the suite.

**Throwaways (deleted)**:
- None needed — fixture work lived entirely in pytest tmp_path.

**Spawned entities**:
- D-022 (compact design: keep the store healthy, apply without confirmation) — created at the start of this unit; deliberately left triage:pending so the first real compact run has something to triage.
- Q-002 closed (merged into D-022): no automatic topic heuristic.
