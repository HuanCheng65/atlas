---
date: 2026-05-28
slug: script-driven-journal-writes
project: atlas
tags: [skills, scripts, journal, dogfood, agent-ergonomics]
status: closed
opened: 2026-05-28 01:06
closed: 2026-05-28 01:15
verification-result: passed
related: [enforce-orient-and-interview-skills]
---

# Script-driven journal writes (eliminate timestamp fabrication)

## Context

Immediately after closing `enforce-orient-and-interview-skills`, two new
problems surfaced. (1) The `closed:` field I wrote was fabricated — I
guessed `01:30` instead of calling `date`, and the user caught it.
(2) The close flow generated a lot of chat noise: drafting the Close
section as visible markdown, pre-confirming, narrating each step.

Decided fix: move all timestamp-bearing journal mutations behind scripts
under `atlas-log/scripts/`, so the agent cannot fabricate times even if
it tries. This generalizes the principle already in D-001 / D-009
(deterministic ops live in scripts) to journal writes, which until now
relied on `Edit` tool + agent discipline.

Scope:
- Three new scripts: `open.py`, `append.py`, `close.py`
- Auto-reindex baked in (agent no longer has to remember)
- Content via stdin (avoids shell quoting hell for multi-line markdown)
- stdout = machine-parseable result; stderr + non-zero exit on error
- `--at <YYYY-MM-DD HH:MM>` only as explicit backfill flag
- `atlas-log/SKILL.md` + `using-atlas/SKILL.md` updates so all writes go
  through scripts; remove "always confirm before closing" friction when
  the user has explicitly commanded close
- Atomic writes (tmpfile + rename) so an interrupted script can't leave
  half-written frontmatter

## Work log

### 2026-05-28 01:08
Wrote `_lib.py` + `open.py` + `append.py` + `close.py` under
`~/.claude/skills/atlas-log/scripts/`. First pass used a hand-rolled
YAML scalar emitter to match existing frontmatter style (unquoted
timestamps, flow-style lists); user pushed back that hand-rolling was
fragile.

### 2026-05-28 01:12
Replaced hand-rolled YAML with a PyYAML SafeLoader/SafeDumper subclass
pair that drops the timestamp implicit resolver on both ends and forces
flow-style lists. This keeps `YYYY-MM-DD HH:MM` strings as plain scalars
on round-trip without us reimplementing YAML escaping rules.
Smoke-tested open/append/close + failure modes (missing slug, bad slug
format, duplicate file, append-to-closed, bad --at, bad --result): all
exit non-zero with `ERROR:` prefix on stderr.

## Close

**Outcome**: 3 scripts (open/append/close) + _lib.py landed under
atlas-log/scripts/; all journal frontmatter mutations now go through
PyYAML-driven scripts that generate timestamps from datetime.now(). SKILL.md
docs updated on both atlas-log and using-atlas.

**Verification result**: smoke tests cover happy paths and failure modes
on a throwaway slug; the active entry itself was appended to twice via
the new append.py (dogfood); SKILL.md edits inspected.

**Keepers (finalized)**:
- `~/.claude/skills/atlas-log/scripts/{_lib,open,append,close}.py`
- `atlas-log/SKILL.md` rewritten for script-driven flow
- `using-atlas/SKILL.md` bootstrap path switched to `open.py`
- memory: `feedback_never_handroll_serialization`, `feedback_no_fabricated_timestamps`

**Throwaways (deleted)**: hand-rolled YAML scalar emitter (replaced before commit); `script-smoke-test` throwaway entry (cleanup)

**Spawned entities**: none. This work is a corollary of D-009 (deterministic ops in scripts); could justify a D-011 making the journal-mutations-via-scripts rule explicit, but not creating without user say-so.
