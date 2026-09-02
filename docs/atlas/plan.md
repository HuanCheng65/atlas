# Plan — redesign the memory model

> Working state for the task in hand, written by grill-me and overwritten per
> work unit. Not a record: a plan describes intent, and the store holds what
> happened.

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

> Steps 1–11 landed in this repository. 12–13 (the quiver store) are
> pending and belong to a separate commit in that repository.

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
