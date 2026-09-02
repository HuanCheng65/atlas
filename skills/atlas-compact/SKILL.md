---
name: atlas-compact
description: Maintenance pass over the record store under docs/atlas/records/. Two jobs — consolidating the memory records, whose one-line titles are loaded into every session and therefore have a budget, and reviewing the store for records that have quietly stopped being true. Use WHEN the user asks to clean up or review the store, or when the memory budget is exceeded. Runs end-to-end WITHOUT per-item confirmation; safety comes from bounded writes, validate gating, and landing the run as one revertable commit. Not for onboarding. Never run in the background.
---

# Atlas Compact

You keep the store small, current and true. Invocation is the authorization —
work through the run without asking per item. The safety net is that everything
lands as one commit the user can revert.

Start with the shortlist:

```bash
python3 ~/.claude/skills/atlas-compact/scripts/scan.py
```

It computes every mechanical signal. Read what it points at; do not read the
whole store.

## Job one: consolidate memory

Memory records hold the constraints currently in force, and their titles are
loaded into every session. That is a budget, and the store grows past it the way
any working set does.

Consolidation is a **rewrite, not a review**. Take the memory records the scan
flags — over budget, untouched for a year, or overlapping — and write the set
that should be in force now. What you do not carry into the rewrite stops being
preloaded. That is the point: eviction is the default, and rescuing a constraint
takes a deliberate act rather than deleting one taking a decision.

Eviction is cheap because it loses nothing. The experiment or decision that
established a constraint is still in the store; only the always-loaded summary
goes away.

Three things to look for:

- **Overlap.** Two constraints saying the same thing at different precision:
  keep the precise one, cite the evidence from both.
- **Expiry.** The constraint's subject is gone — the file it names no longer
  exists, the code path was deleted. The scan lists records citing dead paths.
- **Absorption.** A constraint that has become how the code works, enforced by
  a check or impossible to violate. It is no longer a constraint; it is a fact
  about the artifact, and the artifact says it.

Memory records are rewritten in place. Git keeps what they used to say.

## Job two: review the store

The scan surfaces three candidate sets. Each needs judgment, which is why they
are candidates and not actions.

- **Questions with no answering record.** An old question that nothing cites is
  usually one that got answered in passing. Find the record that answered it and
  add `(answers:: [[NNN-slug]])` to *that* record — adding a typed edge to a
  published record is permitted, because it changes nothing the record claims.
  If the question stopped mattering rather than being answered, say so in a new
  record and answer it there.
- **Records sharing most of their neighbourhood.** Same type, cited by and
  citing mostly the same records: often two measurements of one thing, or a
  decision restated. Merge by writing one record that supersedes both, not by
  editing either.
- **Tags used once.** Usually a synonym for a tag already in the store. Fold
  them into the existing vocabulary; leave a genuinely distinct one alone.

## Finishing

```bash
python3 ~/.claude/skills/atlas-entity/scripts/validate.py
python3 ~/.claude/skills/atlas-entity/scripts/reindex.py
```

Commit the run as one commit whose message says what changed in the store's
content — which constraints are now in force, which questions closed — not that
compact ran.

## Anti-patterns

- **DO NOT** ask the user to approve each item. Invocation authorized the run.
- **DO NOT** edit a published record's claims to bring it up to date. Write a
  newer record with a typed edge; adding an edge is the only permitted touch.
- **DO NOT** keep a memory record because deleting it feels lossy. The evidence
  survives in the store; only the preloaded line goes.
- **DO NOT** run in the background. The run rewrites files and must be visible.
