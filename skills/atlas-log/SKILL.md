---
name: atlas-log
description: Maintains the journal under docs/atlas/journal/. Use WHENEVER non-trivial work progresses on a project that has an active journal entry — code edits, refactors, bug fixes, benchmarks run, design decisions made, edits to atlas data files themselves, or conclusions reached after discussion. Append timestamped notes to the active entry's Work log automatically, without pre-confirmation; announce one line after appending. Also use to CLOSE an active entry (requires user confirmation). If no active entry exists (using-atlas was skipped or deferred), fall back to creating one — but using-atlas is the canonical bootstrap path.
---

# Atlas Log

You maintain the project journal at `docs/atlas/journal/`. The journal records the trajectory of work as it happens. One file equals one work unit: from plan (via grill-me) through execution to closure.

## Mental model

Each journal entry has a simple lifecycle:

- **Created** by grill-me (with the Plan section), OR by you directly if work starts ad-hoc without a grill-me session
- **Updated** by you as work progresses, by appending timestamped subsections under `## Work log`
- **Closed** by you when the work unit ends, by filling `## Close` and setting frontmatter `status: closed`

Multiple entries can be `active` at the same time — parallel work across windows / topics is normal. You hold "which entry am I currently working on" in your own conversation state. Do not assume there is only one.

## Trigger: when to APPEND (do automatically, no pre-confirmation)

Append a timestamped subsection under `## Work log` of the active entry whenever any of these happen:

- You completed a substantial unit of work (function written, bug fixed, refactor committed, benchmark run with a result)
- A non-trivial decision was made mid-work (then also consider invoking `atlas-entity` for a D-NNN if it qualifies)
- A new unresolved question surfaced (then also consider a Q-NNN)
- An experiment produced a result (then also consider an E-NNN)
- The user explicitly says "log this" / "记一下" / "write that down"

After appending, **announce in one line**:

> (appended to journal/2026-05-27-cuda-graphs-dispatch.md: "P99 30.9 → 27.4ms, target hit")

Post-hoc transparency. Pre-hoc confirmation is forbidden — it kills the flow.

## Trigger: when NOT to append

- Trivial conversational exchanges (yes/no, clarifying questions)
- Reading files without producing output
- Looking up information without acting on it
- The user is in rapid-fire question mode
- Tool calls that don't represent work progress (e.g. `ls`, `grep` for orientation)

When unsure, **lean toward NOT logging**. Over-logging is noise; the journal should read like a coherent narrative, not a tool-call log.

## How to APPEND

1. Identify the active entry (see "Identifying the active entry" below)
2. Open `docs/atlas/journal/<slug>.md` with your edit tool
3. Find the `## Work log` section. Insert a new subsection at its end:

   ```markdown
   ### 2026-05-27 16:20
   <one short paragraph: what happened, with concrete numbers / file paths>
   ```

   Use 24-hour `HH:MM` format. One short paragraph is enough — for longer narrative, write multiple subsections.

4. Run reindex:

   ```bash
   python ~/.claude/skills/atlas-log/scripts/reindex.py
   ```

5. Announce in chat (one line).

## Trigger: when to CLOSE (requires user confirmation)

Close an active entry when:

- The Verification criteria (from Plan section) have been checked and the result is known
- The user explicitly says "wrap this up" / "结束了" / "close this entry"
- Topic clearly switched and the previous entry will not be resumed
- The entry has been stale for >3 days and the user confirms it's done

Closing is **sticky** — once closed, the entry is frozen and append-only. If related work resurfaces later, open a new entry and link via `related` frontmatter.

**Always confirm before closing.** Append is automatic; close is not.

## How to CLOSE

1. Draft a Close section. It must include:

   - **Outcome** — did the work succeed? one sentence
   - **Verification result** — `passed | failed | partial`; refer to Plan's Verification criteria
   - **Keepers (finalized)** — what actually got into long-term regression. May differ from Plan's proposed Keepers.
   - **Throwaways (deleted)** — what was removed. May differ from proposed.
   - **Spawned entities** — new D / E / Q created during this work; existing Q closed

2. Show the draft to the user. Wait for confirmation or edits.

3. After confirmation:
   - Add the Close content under `## Close` section
   - Update frontmatter:
     ```yaml
     status: closed
     closed: 2026-05-27 17:00
     verification-result: passed
     ```

4. Run reindex.

## Identifying the active entry

Before appending or closing, you must know which active entry you are operating on. Sources, in priority order:

1. **Your conversation memory** — if grill-me was called earlier in this conversation, the slug is the entry it created. Hold it through the session.
2. **User reference** — user says "log to the cuda-graphs entry" or "close the bench entry"
3. **Active entries list** — run:
   ```bash
   grep -l "^status: active" docs/atlas/journal/*.md
   ```
   If exactly one matches, that's it. If multiple, ask the user once and carry the answer.

### Fallback: bootstrap an entry if none exists

The canonical bootstrap path is `using-atlas` at session start. If for some reason that didn't happen (using-atlas was skipped, or deferred indefinitely) and you reach a moment where an append is warranted, you must bootstrap an entry here as a fallback:

1. Pick a kebab-case slug from the work topic
2. Create `docs/atlas/journal/YYYY-MM-DD-<slug>.md` with the same template using-atlas uses (frontmatter with `status: active`, `## Context` paragraph, empty `## Work log`)
3. Append normally from there
4. Announce: "(opened journal/<slug>.md to track this work)"

This fallback exists for robustness. If you find yourself using it frequently, it likely means using-atlas isn't getting invoked at session start — that's worth surfacing.

## Anti-patterns

- **DO NOT** ask "would you like me to log this?" before every append. Just do it.
- **DO NOT** append a journal entry for every tool call. Tool calls are not work units.
- **DO NOT** close an entry without user confirmation, ever.
- **DO NOT** create a new entry when work is continuation of an already-active one — append to the existing one.
- **DO NOT** edit a closed entry's body. If new info comes up, open a new entry and use `related: [<old-slug>]` to link back.
- **DO NOT** skip `reindex.py` after a mutation. The index drifts otherwise.
- **DO NOT** assume only one active entry exists. Always check.

## Cross-references

- `grill-me` creates an entry with Plan section; this skill takes over from there
- `atlas-entity` is invoked when journal content warrants spawning a D / E / Q
- `atlas-orient` reads `_index.md` and active entries to load session context

## What this skill does NOT do

- Does not produce Plans — that's `grill-me`'s job
- Does not manage D / E / Q entities — that's `atlas-entity`
- Does not propose long-form topic distillation — that's `atlas-compact`
