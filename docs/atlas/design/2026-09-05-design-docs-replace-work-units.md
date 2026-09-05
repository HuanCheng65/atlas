# Design docs replace work units

Starts a new line.

## Decided

`grill-me` currently ends one way: open `docs/atlas/work/<date>-<slug>.md` and
fill Intent, Spec and Plan. That fixed shape is the defect. A grill crosses one
gap — from something vague to something more decided — and the gaps do not come
in a fixed set of three. Settling a product's form is design at one depth; how
each module is built is design one depth lower, and neither is Intent, Spec or
Plan. Demanding all three from every interview forces the agent to fabricate the
levels the round did not reach.

Spec and design are not two kinds of thing either. They are the same content
seen from two sides: what one round chose among alternatives is what the next
round must satisfy. So the level names are labels a document carries, not a
schema it fills.

**One document per grill round.** `docs/atlas/work/` becomes
`docs/atlas/design/`; each file is one round of thinking, written once and not
edited afterwards. The skeleton the script writes is:

```markdown
# <title>

Continues `docs/atlas/design/<file>`.

## Decided

## Still open
```

The check on the skeleton is a test asserting the exact file contents for
`--new` and for `--from`, and a non-zero exit when neither or both are given —
this document being the source of the expected text.

- The level — Intent, Spec, design, Plan — goes in the title. It is not a
  field; a required field would rebuild the schema this change removes.
- The continuation line is written by the script, which requires exactly one of
  `--from <filename>` or `--new`. This link is the structure's only spine, and
  a spine maintained by prose reminders is not maintained. `--from` also checks
  that the named file exists, and exits non-zero when it does not — the
  invariant being that the link resolves.
- There is no Verification section. Verification attaches to each Decided item:
  how that item is judged right or wrong, and where the verdict comes from. An
  item whose only source is the user's preference says so. An item that cannot
  yet be judged says that instead of leaving it blank.
- **Still open means "as of this date."** It is not a live TODO list, nothing
  closes items in it, and nobody returns to tick them off. Its test is that
  each entry could seed the next grill; anything that could not is not an entry.

Files stay flat. Rounds branch — one product-form document leaves five modules
open, and each of those branches again — and a later round may draw on two
earlier documents at once. That shape is a graph, and a directory tree cannot
hold it. Flat files with a backward link is what the record store already does.

**Nothing computes which documents are still open.** The mechanism considered
first — number the Still open entries, have each new document claim the entry it
continues, and derive "resolved" from the claims — was rejected. Entry numbers
are positional and shift if a draft's list is reordered, leaving a valid claim
pointing at the wrong entry. One round rarely maps to one entry: it settles two
at once, or half of one, or discovers the entry was the wrong question. Worst,
an entry stops being open for reasons that produce no document at all — settled
in conversation, made moot by a change of direction, abandoned. The derivation
would not compute "still undecided" but "nobody opened a file for it," and those
coincide only in the ideal case. That is the journal's `status` field again,
with the maintenance disguised as derivation
([[033-the-journal-is-deleted-findings-become-records]]).

**Design documents leave the session-start payload entirely.** The section
naming the newest work unit is deleted from `session_start.py`. Which line of
thinking is being picked up today has nothing to do with which file is newest,
so any fixed number of recent files is mostly noise, paid for every session. The
records already carry the conclusions; the design documents are the working
material behind them, and are fetched when a specific one is wanted.

The trigger moves to `using-atlas`, which every session loads, so it is a
persistently visible surface rather than a rule buried in a skill body
([[024-triggers-live-where-the-agent-always-sees-them-not-in-skill]]):
`ls docs/atlas/design/` is the whole menu, since each filename carries its date
and topic; grep reaches content. `grill-me` checks the directory before an
interview starts, to see whether this round continues an earlier one.

**Keepers and Throwaways stop being a fixed section** and become guidance inside
`grill-me` for implementation-level rounds, which is the only level at which
scaffolding exists to classify. The rule itself is unchanged
([[006-verification-keepers-throwaways-instead-of-enforced-tdd]]).

**Migration.** `VERSION` goes from 2 to 3 with a `migrate_v2_to_v3.py` that only
renames the directory. Existing files keep their three sections untouched: they
are dated accounts of what was undertaken, and rewriting them into the new shape
would fabricate a history that did not happen. The version check already refuses
an unmigrated store loudly, so no reader needs a branch for the old shape. The
check is the migration run against a copy of this repository's store: the
resulting `docs/atlas/design/` holds files byte-identical to the old `work/`
ones and `VERSION` reads 3, the old files being their own source. That every
script then refuses a v2 store is the existing version check, already tested.

### What changes

- `skills/grill-me/scripts/start.py` — the skeleton, and `--from` / `--new`.
- `skills/atlas-entity/scripts/_lib.py` — `WORK` becomes `DESIGN`, with its
  comment.
- `skills/atlas-entity/scripts/migrate_v2_to_v3.py` — new.
- `docs/atlas/VERSION` and the `STORE_VERSION` constant — 2 to 3.
- `skills/using-atlas/scripts/session_start.py` — the work-unit section is
  deleted. Its `section` and `first_sentence` helpers stay; PROJECT.md and
  ROADMAP extraction still call them.
- `skills/grill-me/SKILL.md` — the Output section, the Keepers and Throwaways
  guidance, and the frontmatter description, which still promises intent, spec
  and plan under `docs/atlas/work/`.
- `skills/using-atlas/SKILL.md` — the section describing work units.
- `docs/atlas/README.md` — the layout tree, the "Work units" section, and the
  Operations table.
- `tests/test_work_unit.py` — rewritten, not patched: it asserts the old
  skeleton and the session-start section being deleted.
- This document and the one continuing it were written by hand in the new
  shape while `start.py` still wrote the old one, and are moved by the
  migration like any other file. Their continuation lines already name
  `docs/atlas/design/`, which is where they live once the rename runs.
- A decision record superseding [[041-work-units-land-as-one-file-each-plan-md-is-deleted]].
  Half of 041 survives — written once, dated, `plan.md` gone — and half is
  overturned: the three sections, the work unit as the unit, and session start
  naming the latest file.

Whether the reshaped `grill-me` actually stops forcing depth cannot be checked
mechanically. Its source is use: the next design-level round either ends with a
document that has no Plan and reads as complete, or it does not.

## Still open

- `grill-me` asks one question at a time on the ground that batched answers
  degrade. Matt Pocock's original batches every question whose prerequisites are
  already settled, which is a different claim: those questions are independent
  by construction, so batching them costs nothing. Which is right here is
  unsettled and was deliberately not folded into this round.
- The same original dispatches sub-agents to find facts without blocking the
  questions that do not depend on them. `grill-me` explores inline and blocks.
