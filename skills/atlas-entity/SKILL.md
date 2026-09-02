---
name: atlas-entity
description: Operations on the record store under docs/atlas/records/ — listing, searching and auditing records, renaming one, running validate and reindex, and the one-time migration from the old D/E/Q layout. Writing a single record needs no skill; the trigger conditions and the new.py call live in using-atlas, which is always loaded. Use this skill when the user asks to see or audit records, when validate reports something you need to interpret, or when a change touches many records at once.
---

# Atlas Records

The store is `docs/atlas/records/`, one flat directory, one counter. Everything
about writing a single record — the four types, the triggers, the new.py call —
is in `using-atlas`, which is always in context. This skill covers the
operations you reach for less often.

## Reading the store

`records/_index.md` is generated: one line per record, grouped by type, showing
each record's standing and how many records cite it. It is a browse view for a
human. When you need facts, read the record files; when you need to find
something, ripgrep the store — every relation is prose, so it greps.

Derived standing never lives in a file. A record is superseded, refuted or
answered because a *later* record says so with a typed edge; `reindex.py`
recomputes that on every run.

## Scripts

```bash
S=~/.claude/skills/atlas-entity/scripts

python3 $S/validate.py            # identity, schema, links, direction
python3 $S/reindex.py             # regenerate records/_index.md
python3 $S/new.py --help          # create one record (usually called from using-atlas)
python3 $S/rename.py 047 new-slug # change a slug and rewrite every link to it
python3 $S/migrate.py --dry-run   # one-time D/E/Q conversion; report first
```

`new.py` and `rename.py` reindex on their own. Run `validate.py` after any edit
you made by hand, and always before committing.

## What validate enforces

- **Identity**: the filename is `NNN-slug`, `id` agrees with it, no two files
  claim a number. Numbers are never reused — a retired number keeps old links
  meaningful.
- **Schema**: `id`, `title`, `date`, `type`, `tags` present; experiments also
  carry `hypothesis`, `config`, `result`, `conclusion`, `artifacts` as one-line
  machine summaries capped at 300 characters, with the full prose in the body.
  A body that says "see frontmatter" instead of stating its content is an error.
- **Deleted fields**: `status`, `related`, `supersedes`, `superseded-by`,
  `refuted-by`, `answered-by`, `triage`, `affects`, `source-journal` and
  `severity` are rejected by name. Each is derived now, and a field nothing
  reads is a field that drifts.
- **Titles**: at most 90 columns, counting CJK as two. The cap is not
  cosmetic — it is the mechanical half of "one record, one claim", because two
  findings do not fit in one line.
- **Links**: every `[[NNN-slug]]` resolves to a file, every typed edge uses a
  known verb, and both point at lower numbers. Memory records may point
  forwards; they are rewritten in place rather than superseded.

## Renaming

A slug is part of the link graph — Obsidian resolves wikilinks by filename and
ignores frontmatter aliases — so renaming is a whole-store rewrite. Always use
`rename.py`; it rewrites `[[old]]` and `[[old|display text]]` and leaves prose
that merely quotes the stem alone.

## Auditing

When the user asks what state the store is in, answer from `validate.py` plus
the index rather than from reading every file. Useful shapes:

- records nothing cites and nothing has acted on — candidates for consolidation
- questions with no answering edge, sorted by age
- tags used once, which are usually a synonym for one already in the store

`atlas-compact` computes these systematically; do it by hand only for a
one-off question.

## Migration

`migrate.py` converts a pre-record store: it renumbers by a topological sort of
the reference graph so every record outranks what it cites, rewrites prose
`D-007` references as wikilinks, turns `supersedes` and `answered-by` into typed
edges, drops the derived fields, rewrites PROJECT.md's constitution pointers,
and moves the journal to `docs/atlas/archive/` untouched.

Run `--dry-run` first and read the report. Two things it cannot fix on its own,
because both need judgment: a title over the budget, and a forward reference —
an older record edited to cite a newer one, which is the pattern the store now
prevents. Resolve those in the source, then run it for real.
