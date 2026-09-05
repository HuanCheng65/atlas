# Land intent spec plan as work units

## Intent

`docs/atlas/plan.md` is a single path overwritten by every work unit in turn.
It has been stale for ten commits — still describing the memory-model redesign
while the plugin, hook and bootstrap work landed around it — and the staleness
is structural, not neglect: a committed file whose truth holds only while one
particular piece of work is in flight will look authoritative in git forever.

Deleting the journal left this open on purpose. That decision's own closing
words were "where intent and specification should live is a separate problem
and remains open". This is that problem.

The second half of the intent is process. The framework has covered what a
project remembers and left how work gets done to one skill invoked by hand.
The known failure of a coding agent is not forgetting; it is crossing the gap
from intent to structure by guessing, because completion is what gets rewarded.
Nothing in the framework pushes back on that, and nothing sets a bar for the
checks it writes — which is why AI-written tests tend to assert the path the
code already takes.

## Spec

**Layout.** One file per work unit at `docs/atlas/work/<date>-<slug>.md`,
holding Intent, Spec and Plan, written once and not edited afterwards. The date
is in the filename and a script owns it. `plan.md` is deleted.

This is not the journal returning. The journal died of two things and neither
is present: a work log that grew by appending (317 appends, one entry at 155 KB)
and a `status` field that required someone to come back and change it (ten of
eleven entries never closed). There is no work log here and no status.

**The store keeps what a work unit file cannot carry.** A memory record for a
constraint nothing enforces, a decision record for a choice that is
architecturally significant, a question, an experiment. A choice that is only
how this task got done stays in the Spec section and is not a record.

**Process escalates on evidence, with no classification step.** The default is
nothing. Weight is added when a signal appears, and the level may change
mid-work, so judging a task small costs nothing when it turns out not to be.

- L1, whenever any check is written: it must name the source of its judgment.
  If that source is the code under test, say so — that is a characterization
  test, legitimate on code being refactored and wrong only when unacknowledged.
- L2, when the change touches something expensive to unmake: produce a
  representation before code, chosen from a named menu and justified.

**Verification.** Each check below names its judgment source.

| check | judgment source |
|---|---|
| `start.py` refuses an existing path, an invalid slug, and a store in an older format | the stated contract, asserted in `tests/test_work_unit.py` |
| session start names the work unit in hand and drops it once committed | the same git-derived rule already asserted for record drafts, which these tests mirror |
| the debt reading reports the files a change touched | a fixture repository with a known commit shape, so the expected numbers are counted by hand, not produced by the code |
| the store still validates and the suite is green | `validate.py` and the existing suite, neither of which this work changes |

The behavioural check has no mechanical source and is stated as what would
falsify the design: after ten work units, `work/` holds ten files nobody had to
go back and edit, and the always-loaded payload has not grown with them.

**Representation.** The menu entry is a schema: the work unit file's three
sections and the store's four record types are the whole vocabulary, and the
choice being made is which of the two any given piece of a plan lands in. That
choice has one test — does a future session need it, and can anything stop it
being violated — so the seam is placed there rather than at the boundary
between planning and implementation.

## Plan

1. `_lib.WORK` and `start.py`: the path, the date, the skeleton.
2. Rewrite `grill-me` around the three sections, the escalation levels, the
   judgment-source bar, and the keeper criterion.
3. Carry the two triggers into `using-atlas`, which is loaded every session —
   a trigger inside a skill body cannot fire the invocation of that skill.
4. `session_start.py`: name the work unit in hand, derived from git the way
   record drafts already are.
5. The debt reading in `atlas-compact`'s scan: how many files each recent
   change touched, and which files always change together.
6. Delete `plan.md`; update the layout in both READMEs.
7. Tests for the new behaviour.
8. Records for what is architecturally significant here, and memory records
   for the constraints nothing enforces.
