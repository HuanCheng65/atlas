---
name: atlas-compact
description: Maintenance pass over the atlas store under docs/atlas/ — clears backlog (stale active entries, decisions pending triage, aging open questions) and consolidates existing records (merge/supersede overlapping decisions, close implicitly-answered questions, distill recurring journal themes into topics, refresh Glossary/PROJECT.md wording). Use WHEN the user asks to run compact / clean up / review the store, or accepts orient's backlog hint. Runs end-to-end WITHOUT per-item confirmation — invocation is the authorization; safety comes from bounded writes, validate gating, and landing the whole run as one revertable commit. Not for onboarding (atlas-bootstrap) and never run in the background.
---

# Atlas Compact

You run a maintenance pass over the project's atlas store. The job: keep the store **small, current, and true**. Two halves:

- **Backlog** — things nobody handled yet: active journal entries gone quiet, decisions still pending triage, open questions aging without progress.
- **Consolidation** — things recorded once and degraded since: overlapping decisions that should merge, questions that later work answered implicitly, recurring journal themes worth distilling into a topic, Glossary or PROJECT.md wording that drifted from actual usage.

## Authorization model (read this first)

**Invoking compact authorizes the whole run.** Do not pause for per-item confirmation — the user invoking this skill is the confirmation, the same way an explicit close command is the confirmation in atlas-log. Confirmation prompts here degenerate into reflexive approval; the real review artifact is the git diff of the run's single commit, which the user inspects (or doesn't) on their own time, and reverts atomically if they disagree.

What replaces confirmation is **bounded writes**. A compact run may only:

- create new files (topics, merged decision records)
- flip statuses and triage values through the existing scripts (`close.py`, `close_question.py`, `supersede.py`, frontmatter triage edits)
- add or fix links, `related` refs, and `(D-NNN)` pointers
- reword Glossary entries and PROJECT.md lines (including Working rules)

A compact run **never**:

- deletes a file
- rewrites journal bodies or the text of superseded decisions (history is frozen; consolidation writes *new* summaries and flips statuses)
- runs in the background or on a schedule — the judgment half needs a live agent in a session the user started

## Run procedure

1. **Scan.** From project root:

   ```bash
   python3 ~/.claude/skills/atlas-compact/scripts/scan.py
   ```

   Optional: `--stale-days N` (default 3), `--cluster-min N` (default 3). The output is an agenda of candidates — data, not verdicts.

2. **Check the tree.** `git status docs/atlas PROJECT.md` — if those paths already carry uncommitted changes, you cannot give the run its own clean commit. Finish the run but **skip the commit step and tell the user why**; do not mix unrelated changes into a compact commit.

3. **Judge each agenda item** against the actual files (open bodies as needed):
   - *Stale active entry* — work clearly finished? Close it via `close.py` with an honest `--result` (not reflexively `passed`). Genuinely unfinished? Leave it; note it in the report.
   - *Pending triage decision* — apply the promotion test (*does violating it produce visible resistance?*): behavioral rule → set `triage: promoted` and add the one-line rule with its `(D-NNN)` pointer to PROJECT.md's Working rules; embodied event → `triage: archival`.
   - *Possibly-answered question* — read the question and the later work; if actually answered, `close_question.py Q-NNN --by <ref>`. A tag overlap is a hint, not an answer.
   - *Decision overlap pair* — only merge when the records genuinely state one rule in two places: create the merged decision via `new.py`, then `supersede.py` both old ones onto it, and update any Working rules lines. Different-but-related decisions just get `related` links.
   - *Tag cluster* — a topic is worth writing when the cluster contains reusable knowledge a future session would otherwise re-derive from multiple journal bodies. Write `docs/atlas/topics/<name>.md`, free form, linking the source entries. Volume alone is not a reason.
   - *Glossary / PROJECT.md drift* — fix wording where the store's own usage has moved on.

4. **Validate.** `validate.py` must exit clean; fix anything it flags before committing. Re-run `reindex.py` (both) if any frontmatter changed outside the scripts.

5. **Journal the run.** Open an entry via `open.py` with tag `compact` (the scan uses it to date the last run), one paragraph on what the agenda was; close it with what was done. This is the run's own record.

6. **Commit.** Stage exactly the files this run touched (`docs/atlas/`, `PROJECT.md`) and commit with a message naming the content — what was merged, closed, distilled — never "update atlas docs". One run, one commit.

7. **Report.** Tell the user in a few sentences what changed and what was deliberately left alone (e.g. "left the X entry open — looks unfinished"). This is work content, not a framework announce; plain language.

## Judgment defaults

- When unsure whether an entry is done, whether a question is answered, or whether two decisions are really one — **leave it and say so in the report**. A false merge or false close costs more than another cycle of waiting; "no action" is always a legitimate verdict.
- Honesty over streaks: a stale entry whose verification never ran closes as `partial` or `failed`, not `passed`.
- Working rules line count is a budget. If promotion would push it past ~15 lines, look for rules to merge or demote first.

## Cross-references

- `atlas-orient` surfaces the backlog hint that usually triggers this skill
- `atlas-log` / `atlas-entity` scripts do all the actual writing
- `atlas-bootstrap` is for onboarding — compact assumes the store already exists
