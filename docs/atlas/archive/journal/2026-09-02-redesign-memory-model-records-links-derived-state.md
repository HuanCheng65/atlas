---
date: 2026-09-02
slug: redesign-memory-model-records-links-derived-state
project: Atlas
tags: [memory-model, schema, links, migration, compact, obsidian]
status: active
opened: 2026-09-02 21:37
closed: null
verification-result: null
related: []
---

# Redesign the memory model: numbered records, wikilinks, derived state

## Context

The session began with a question about whether the journal layer is necessary at all, and whether an agent could simply grep Claude Code's own transcripts instead. An audit of the quiver dogfood store answered it with data: the journal is an under-priced inbox — 317 work-log appends against 49 promoted experiment records, with 49 of those appends empty; 10 of 11 active entries were never closed, the oldest untouched since 2026-07-16; one entry reached 155 KB across 93 appends over six days and is still marked active a month later. Transcripts cannot substitute: quiver's oldest surviving transcript is from 2026-08-10 while the store covers work from May onward, and the transcripts are per-machine and outside git. The deeper diagnosis is that a record rots when its truth depends on a future edit — E-021's title still asserts a QPS deficit that E-022 refuted the same day, because `refuted-by` was a field the agent invented, unvalidated and one-directional. Meanwhile 1163 of the store's 1268 entity references live in prose where nothing can derive from them, 57% of experiment file bytes are frontmatter duplicating the body, and 131 of 236 tags are used exactly once. This work replaces the journal with cheap numbered records, derives state instead of storing it, moves links into the prose using Obsidian-compatible wikilinks, and adds an agent-maintained set of operating-constraint records whose one-line summaries are always loaded.

## Decisions resolved

- **Everything is a numbered record in one flat counter.** `047-slug.md`, with `type` as a mutable frontmatter field rather than an ID prefix. Type is a judgment made at the moment of least information; identity must not encode a mutable property. A single monotonic counter also makes "links point backward only" a mechanical assertion (`target < source`), which per-type counters cannot express.
- **Record types are decision, experiment, question, and memory.** No catch-all type: a catch-all would absorb the 317 appends unchanged and reproduce the inbox under new numbers.
- **Memory records hold operating constraints** — a limit or prohibition that stays in force ("the register cliff is at 128; check `cuobjdump` REG before touching the estimator"). They are ordinary numbered records, shaped like Claude Code's own memory files: a one-line summary in frontmatter, evidence in the body, a wikilink to the measurement that produced the constraint. Only the one-line summaries are always loaded.
- **Experiment results and operating constraints are written at different moments, neither of which is "session end".** A result is written when the measurement completes — an observable event. A constraint is rewritten in place whenever understanding changes. "Session end" is not observable and would reintroduce the dependency on a future event that this redesign exists to remove.
- **The commit is the publication boundary.** An uncommitted record is a draft and may be rewritten freely; a committed record is superseded, never edited. E-021 and E-022 were produced hours apart on the same uncommitted day and should have been one record. The one exception: adding a backward-pointing typed edge to a committed record is permitted, since it alters no claim the record makes.
- **State is derived, never stored.** The `status`, `related`, `supersedes`, `superseded-by`, `refuted-by`, `triage`, and `source-journal` frontmatter fields are deleted. "Superseded", "refuted", "answered", and "in flight" are computed from typed edges and git.
- **Links live in the body, in Obsidian-compatible syntax.** Plain reference is `[[047-slug]]`; a typed edge is `(refutes:: [[047-slug]])`, written in the sentence that carries the reasoning. Frontmatter link fields are deleted. The wikilink inside a typed edge resolves natively, so Obsidian's graph and backlink panes work without plugins. Obsidian does not resolve wikilinks through frontmatter aliases, so the link text must equal the filename and renames are handled by a script that rewrites all references.
- **The journal is deleted.** Its Context half is redundant with the transcript, whose retention window (about 20 days) covers the only period in which "what am I in the middle of" matters. Its Work-log half held experiment results and operating constraints, both of which now have record types. `docs/atlas/journal/`, `open.py`, `append.py`, and `close.py` are removed.
- **Existing journals are frozen, not migrated.** Quiver's 25 entries and atlas's 19 move to an archive directory unchanged and remain grep-able. No bulk extraction: the always-loaded budget admits at most a few dozen lines, so an AI pass over 268 appends would produce candidates that the eviction mechanism immediately discards. The user seeds the initial memory records by hand.
- **The session-start hook runs the state script directly.** The current chain is hook → prose asking the agent to invoke `using-atlas` → `atlas-orient` → `orient.py`; three of four steps only relay a request. The hook becomes a stable one-liner invoking an atlas-shipped script, so future changes never touch `settings.json`. `atlas-orient` is deleted; `using-atlas` remains and carries atlas's own operating rules, which ship and version with atlas rather than living in the user's `CLAUDE.md`.
- **PROJECT.md and CLAUDE.md are unchanged.** Working rules stay where they are. A Working rule is the residue of a decision that could not be mechanized, and moving it to `CLAUDE.md` would add a second always-loaded mechanism to do what the hook script already does. Working rules and memory records are the same kind of thing — constraints no mechanism enforces, which must therefore be restated every session — and remain two artifacts only because of authorship and editing ergonomics: the user maintains a list and edits it in bulk, the agent writes one record at a time.
- **compact splits into two jobs.** Consolidating the memory records when they exceed budget or a session count, and reviewing the store for implicitly answered questions, overlapping records, and decisions whose subject no longer exists. Candidates for the second job are computed by script — no inbound links plus no activity, high link-graph overlap, referenced paths absent from the repo — so the agent judges a shortlist rather than reading the store. Neither job asks for confirmation.
- **Duplicate detection uses the link graph, not tags.** 131 of 236 tags in quiver are used exactly once, and one tag is literally `d-002`, an entity ID the agent used because the body had no link mechanism. Tags survive for grouping records that do not reference each other, but the creation script prints the existing vocabulary with usage counts and a new tag requires an explicit flag.
- **Titles carry a length cap.** `validate.py` has no title check today; quiver's longest experiment title is 254 characters and joins two separate findings with a semicolon. A cap forces the split without requiring judgment. The cap bounds record size from above; the lower bound remains "would someone who does not know this plausibly do the opposite".

## Steps

1. Extend `validate.py`: unified ID format, the four types, deletion of the removed frontmatter fields, title length cap with a separate count for CJK, rejection of unknown typed-edge verbs, and the `target < source` direction assertion.
2. Write the link parser: extract `[[047-slug]]` and `(verb:: [[047-slug]])` from bodies, resolve targets, report dangling links.
3. Move derived state into `reindex.py`: backlinks, superseded, refuted, answered, and in-flight computed from the link graph and git rather than read from frontmatter.
4. Write the record-creation script: one call takes a title, a type, and a body on stdin; assigns the next number; prints the tag vocabulary with counts; requires an explicit flag for a new tag; reindexes.
5. Write the rename script: change a file's slug and rewrite every `[[old-slug]]` in the store.
6. Write `session_start.py`: emit live state only — records in flight, open questions, recent records by title, and the memory records' one-line summaries. Replace the hook command in `settings.json` with a stable one-liner.
7. Delete `atlas-orient`, `orient.py`, and the journal scripts. Rewrite `using-atlas` to carry atlas's operating rules and the record-writing triggers.
8. Rewrite the entity templates for the four types, and `schemas.md` to match.
9. Write the migration script: renumber into one counter, rename files, rewrite prose `[DEQ]-NNN` references as wikilinks, convert the invented `refuted-by` and `correction_*` fields into typed edges on the newer record, delete the removed fields, move journals to the archive directory.
10. Run the migration on the atlas store; fix what validate reports.
11. Rewrite `atlas-compact` as the two jobs, with the candidate computation in a script.
12. Migrate the quiver store: run the script on a copy first, diff the result against the original, and only then apply it in place as a separate commit in that repository. Quiver is on a remote machine and under active work for a FAST'26 submission, so a failed migration costs real work. Clear its 31 outstanding validate errors.
13. Seed the initial memory records: the user names the constraints currently in force, from working knowledge rather than by reading the frozen journals.

## Verification

**Mechanical, checked by script:**

- The full pytest suite is green, including new cases for unified numbering, wikilink and typed-edge parsing, derived status, the direction assertion, the title cap, and rejection of unknown verbs.
- The migration script runs on both stores and `validate.py` reports no errors, including quiver's 31 pre-existing failures.
- Migration invariants hold on both stores: record count before equals record count after; every one of the 1163 prose `[DEQ]-NNN` references in quiver resolves to exactly one existing file after conversion; no dangling wikilinks; every typed edge satisfies `target < source`.
- The session-start hook emits state without any skill invocation, and its output is smaller than the current 13 KB on quiver.

**Behavioural, observed over real use:**

After ten working sessions on quiver, three things hold: the memory records' summaries are within budget; none of them describes a constraint that no longer applies; and the number of records created over that period is non-zero, with every title identifiable on its own in the index. The third check covers both failure modes at once — the agent writing nothing, and the agent writing many records with unusable titles.

## Keepers (proposed)

- The pytest suite, including the new cases.
- `validate.py`, the link parser, `reindex.py`, the record-creation script, the rename script, `session_start.py`.
- The migration script, retained as the record of how the stores were converted.
- The migration invariant checks, as a reusable consistency audit over any atlas store.

## Throwaways (proposed)

- The one-off analysis commands used during this discussion: the tag histogram, the frontmatter-versus-body byte split, the append size distribution, the transcript prose-share measurement.
- Any scratch output written under the session scratchpad.

## Work log

### 2026-09-02 21:50
Built the new record layer under `skills/atlas-entity/scripts/`. Records are flat files at `docs/atlas/records/NNN-slug.md` on one monotonic counter; frontmatter carries only id, title, date, type, tags (plus five one-line summaries for experiments). `_lib.py` rewritten around a `Record` object keyed by integer id, with `display_width` counting CJK as two columns for the title cap. New `links.py` parses the two body forms — `[[NNN-slug]]` and `(verb:: [[NNN-slug]])` — after stripping fenced and inline code so documentation quoting the syntax does not register as a relation; it resolves targets by filename exactly as Obsidian does, inverts mentions into backlinks, and derives standing (superseded / refuted / answered) from incoming typed edges. `validate.py` rewritten: identity agreement between filename and frontmatter, duplicate-number detection from filenames (load_all keys by id and would otherwise drop the second file silently), rejection of the ten now-derived fields by name, the four legal types, a 90-column title cap, dangling links, unknown verbs, and the direction rule (`target < source`) with memory records exempt because they are rewritten in place. `reindex.py` emits one `records/_index.md` grouped by type with derived standing and citation counts, retired records sorted last. `new.py` is the pricing fix: one call takes title, type, tags and the body on stdin; a tag outside the store's vocabulary aborts and prints the vocabulary with counts, so reusing is free and introducing requires `--new-tag`. Slugify now normalises through NFKD and refuses an empty slug rather than emitting `NNN-.md`, which a CJK-only title would have produced. Added `rename.py` (rewrites `[[old]]` and `[[old|display]]` across the store, not a substring replace). Deleted `supersede.py` and `close_question.py` — both are typed edges now. Smoke-tested end to end in a throwaway store: creation, vocabulary gate, typed-edge parsing, derived "answered by 002", index generation, and four failure paths (unknown tag, forward reference, unknown verb, overlong title) all behave.

### 2026-09-02 22:00
Added `migrate.py` and `session_start.py`, and 26 pytest cases covering the record layer. Migration numbers records by a topological sort of the reference graph with (date, old id) breaking ties, because a record must be numbered above everything it cites or the direction rule fails on arrival; only prose mentions and the two convertible relation fields constrain the order, since `related` and the reverse halves of supersedes are dropped rather than converted and would otherwise invent cycles. On the atlas store the sort is acyclic except for one genuine forward reference — D-009 cited Q-005, an older record edited to point at a newer one, exactly the pattern being removed — so that pointer was deleted from the source; Q-005 still cites D-009 backwards and the index shows the relationship as "cited by". Migration also normalises slugs (the old slugifier truncated at a character count and left trailing hyphens, which the new filename grammar rejects), rewrites PROJECT.md's twelve `(D-NNN)` constitution pointers into wikilinks, drops the unread `source:` field, and removes `_templates` (new.py writes the file itself) and the empty `topics/`. Verified on a copy: 29 entities became records 001–029, frontmatter reduced to exactly id/title/date/type/tags, validate clean. `session_start.py` replaces orient.py and lives in using-atlas, importing the record layer from its sibling skill rather than adding a third copy of the loader. Its output on the migrated store is 4.6 KB against orient's 13 KB on quiver, with the triage section gone and a "constraints in force" section in its place. Two fixes fell out of running it for real: `load_all` now skips unparseable filenames instead of raising, since validate reports them separately and every other caller wants the store it can read; and slugify refuses a title whose ASCII residue has no letters, which is what a CJK title leaves behind.
