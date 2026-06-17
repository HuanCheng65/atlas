---
name: atlas-entity
description: Manages structured entities under docs/atlas/ — decisions (D-NNN), experiments (E-NNN), and open questions (Q-NNN). Invoke proactively WHENEVER a long-term architectural / framework choice gets settled in conversation (the user usually won't explicitly label it — recognition is on you), an unresolved question surfaces that won't be answered this session, an experiment produces a citable result, or a previous decision needs to be superseded / a question closed. Also use when the user asks to list, search, or audit any of these entities. Always run scripts/validate.py and scripts/reindex.py after structural changes.
---

# Atlas Entity Management

Three kinds of structured entries live under `docs/atlas/`:

- **D-NNN — Decisions**: long-term architectural or strategic choices
- **E-NNN — Experiments**: research runs with hypothesis, config, result
- **Q-NNN — Questions**: open questions awaiting resolution

Schemas: `reference/schemas.md`. Lifecycle (status state machines): `reference/lifecycle.md`. Read those before structural changes.

## Naming: title is the menu signal

The title is what `atlas-orient` shows in its summary. The agent decides whether to fetch the body based on the title alone, so titles must do real work — they cannot be topic labels.

**Universal rules:**
- **State the answer / question / claim, not the topic.** Topic-label titles ("Logging strategy", "Naming things", "Database stuff") fail — the reader still has to fetch the body to know what was decided.
- **Self-contained.** Readable without prior context. Don't refer to other entity IDs in the title ("Refinement of D-007"); restate the substance.
- **One sentence-fragment, ≤70 chars at the slug.** If `new.py` produces a slug longer than ~70 chars, the title is too long — tighten before filling the body.

**Type-specific:**

| Type | Title shape | Good | Bad |
|---|---|---|---|
| **D** | An answer / a chosen position | "Plain text + git as the data layer" / "Event-driven skill activation, not session-phase" / "Translate framework vocab in chat; keep file paths in announces" | "Data layer choice" / "Skill activation" / "Transparency rule" |
| **Q** | A question, ending in `?` (or implied) | "Stale active-journal threshold (3 days?)" / "How should multi-machine sync handle divergent state?" | "Sync stuff" / "Journal staleness" |
| **E** | A testable claim or comparison | "Does Split-K beat dense GEMM on small batch?" / "FlashAttention vs FlexAttention on Kuairand seq lengths" | "GEMM experiment" / "Attention benchmark" |

**Test your title:** read it cold, without the body. Do you know what was decided / asked / tested? If no — rewrite.

## Section conventions: first section is one sentence, self-contained

The first content section of each type must be **one sentence, independently readable**. `atlas-orient` pulls this sentence into its summary, so the agent gets the call without fetching the full file:

- **D** — `## Decision` is one sentence. State what was chosen. Multi-clause OK; multi-paragraph not.
- **Q** — `## Why this matters` first sentence is the impact statement. State what's at stake if unresolved.
- **E** — `## Hypothesis` is one falsifiable claim sentence. State what's being tested.

If you find yourself writing two paragraphs into the first section, move the extra into the next one (Rationale for D, Context for Q, Setup for E).

## When to create what

### Decision (D-NNN)
The core test (also in `using-atlas`, where you make this call before invoking this skill): a decision is a *constraint on future choices*, not *important work*. If three months from now you'd need to dig up the rationale to proceed on related work, it's a D; if it ends with this work unit, it's a journal note.

Concretely, a journal note becomes a Decision when at least two are true:
- It would be confusing to a future you without rationale
- It affects how future work in this project will be done
- It has alternatives that were considered and rejected
- It will likely be referenced from other entities

Examples: "use Split-K decomposition", "Kuairand-1K as primary benchmark", "Compose Navigation 3 over Navigation 2".

### Experiment (E-NNN)
Any run that produces a result you might cite later. SLA-style benchmark with hypothesis, or an eval run for an LLM app.

### Question (Q-NNN)
Concrete unresolved question that won't be answered in this session. Don't create one for things you'll figure out in the next 30 minutes — those are journal notes.

## Scripts

All scripts assume CWD is the project root (where `docs/atlas/` lives).

### `new.py --type D|E|Q "<title>"`
Creates the next entity. Reads `docs/atlas/_templates/<type>.md`, assigns next available ID, fills placeholders, reindexes its type, prints the new file path. Open it and fill in the body sections.

```bash
python3 ~/.claude/skills/atlas-entity/scripts/new.py --type D "use CUDA graphs for dispatch"
# -> docs/atlas/decisions/D-012-use-cuda-graphs-for-dispatch.md
```

### `supersede.py <old> <new>`
Bidirectional supersedes between two decisions. Sets `old.status=superseded`, appends `new` to `old.superseded-by`, appends `old` to `new.supersedes`.

### `close_question.py <q-id> --by <ref> | --wontfix`
Closes a question. `<ref>` is an entity id (e.g. D-012) or journal filename. Status becomes `answered`, `merged-into-D`, or `wontfix`.

### `reindex.py [--type D|E|Q]`
Rebuilds `_index.md` from entity frontmatter. Safe to run unconditionally. Auto-run by `new.py`; run manually after supersede/close_question or hand-edits to frontmatter (e.g. status changes).

### `validate.py`
Checks orphan refs, bidirectional consistency, status legality, required fields. Run before committing entity changes. Exits non-zero on errors.

## Standard workflows

### Long-term decision made
1. Confirm with the user it meets the criteria above — propose at a natural seam (work wrap-up, before close, a user pause), not mid-flow; the exception is a conflict with a Working rule / active decision, which surfaces immediately
2. `new.py --type D "<title>"`
3. Open the returned path; fill Context / Decision / Rationale / Consequences / Alternatives
4. Set `status: active` (template defaults to `planned`, which means "documented but not yet adopted" — most newly-recorded decisions are immediately in effect)
5. Leave `triage: pending` (template default) — it keeps the decision in orient's menu until reviewed; promotion into PROJECT.md's Working rules happens at a review pass (atlas-compact or the user), not at creation
6. If supersedes existing: `supersede.py <old-id> <new-id>` — if the old decision was promoted, update or remove its Working rules line in PROJECT.md too; `validate.py` fails until the pair is consistent
7. If answers an open question: `close_question.py <q-id> --by <new-id>`
8. `reindex.py` then `validate.py`

**Legal status values** (validated by `validate.py`):
- **D**: `planned | active | superseded | rejected` — *not* `accepted`/`adopted`/`approved`; atlas uses `active`
- **E**: `planned | running | completed | abandoned`
- **Q**: `open | answered | wontfix | merged-into-D`

Full state machines: `reference/lifecycle.md`.

### Experiment lifecycle
1. `new.py --type E "<title>"` at planning time, fill Hypothesis + Setup
2. When run starts, edit status to `running`, append Run log entries
3. When done, fill Result + Conclusion, edit status to `completed`
4. `reindex.py` then `validate.py`

### Question raised
1. `new.py --type Q "<question>"`
2. Fill Why-this-matters / Context / Investigation-needed
3. `reindex.py`

### Reference an entity by id ("see D-007")
Read directly: glob `docs/atlas/decisions/D-007-*.md`.

## Out of scope for this skill
- Writing journal entries → `atlas-log` skill
- Proposing entity promotions from journal → `atlas-compact` skill
- Loading session context → `atlas-orient` skill
- Brainstorming requirements → `grill-me` skill
