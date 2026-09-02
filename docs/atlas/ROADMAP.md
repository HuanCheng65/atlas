# Roadmap

> Short-term goals. For long-term goals see PROJECT.md.
>
> Scope is intentionally minimal. Open questions and committed designs are
> records; finished work is in `git log`. This file holds only the current
> milestone.

## Current milestone

**Phase 3: prove the record model under sustained real use**

The journal, the status fields and the triage step are gone. What replaced
them is a flat store of numbered records whose standing is derived from the
links between them, loaded at session start by a hook rather than by a chain
of skill invocations. The design is argued from dogfood evidence and enforced
by `validate.py`; what it has not yet had is use.

Exit criteria:

- The quiver store migrates: run on a copy, diff, then apply as a separate
  commit in that repository. Its 31 outstanding validate errors clear, and
  every one of its 1163 prose references resolves after conversion.
- The user seeds the initial memory records from constraints they know are
  currently in force — not by reading the archived journal.
- Ten working sessions on a real project, after which three things hold: the
  memory summaries are within budget, none describes a constraint that no
  longer applies, and the records written in that period each carry a title
  that identifies them on its own in the index. The last check catches both
  failure modes at once — writing nothing, and writing many unusable records.
- `atlas-compact` runs once for real, and its memory rewrite is inspected to
  see whether the eviction default holds up without the feedback signal the
  published version of the idea trains against.
