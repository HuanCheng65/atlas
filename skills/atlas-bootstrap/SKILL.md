---
name: atlas-bootstrap
description: Onboard an EXISTING project (already running for weeks or months, with or without other frameworks like Superpowers / GSD) to atlas. Use ONCE per project, never for fresh starts. Use WHEN the user says "set up atlas here", "migrate this to atlas", "bootstrap atlas", or right after running atlas-init on an existing project. Produces PROJECT.md and an initial set of D / Q / E entities by combining a deterministic project scan with a 4-round interview. Does NOT create journal entries — journal is forward-only.
---

# Atlas Bootstrap

You onboard an existing project to atlas by combining (1) a deterministic scan of the project's artifacts and (2) a structured interview that produces PROJECT.md plus an initial set of entities.

## When to use

- Project has code, git history, README, possibly other framework artifacts
- atlas-init has been run (skeleton exists at `docs/atlas/`)
- User explicitly wants to onboard, not start from scratch

## When NOT to use

- Brand new empty project → atlas-init alone is enough
- Adding a single D-NNN to an already-bootstrapped project → use atlas-entity directly
- Project too small to need state (one file, no real history) → skip atlas entirely

## Hard rules (slop prevention)

These are non-negotiable. Violating them pollutes atlas long-term.

1. **Evidence required for every entity.** Each D / Q / E MUST cite a `source`: a git commit hash, a file path, a README section, or an explicit user statement during interview. No fabricated entities.
2. **Hard caps per round**: D ≤ 10, Q ≤ 5, E ≤ 10. Overflow goes to `bootstrap-extras.md` for the user to consider later.
3. **No journal entries.** Journal is for events going forward. DO NOT backfill git commits as fake journal entries.
4. **No supersedes chains.** Only the current active state gets recorded. Past decisions stay in git log.
5. **No topics.** Topics emerge from journal patterns; bootstrap has no journal to derive from.
6. **Quality over completeness.** 5 real D-NNN beats 25 plausible-sounding ones.

## Workflow

### Phase 0: Prerequisites

If `docs/atlas/` does not exist, ask the user to run atlas-init first. Do not proceed without it.

### Phase 1: Scan (autonomous)

Run scan.py from project root:

```bash
python ~/.claude/skills/atlas-bootstrap/scripts/scan.py
```

Output goes to `/tmp/atlas-bootstrap-scan.yaml`. Read it fully.

Then do the manual reads listed in `reference/scan-checklist.md`. Those are things scan.py cannot do for you (e.g. reading README body).

By end of Phase 1 you must be able to articulate:
- What the project is, in one sentence
- 3-5 main themes of recent work
- 2-3 candidate D-NNN you suspect (do not write yet — confirm in Round B)

If you cannot, read more before continuing. Better Phase 1 = shorter interview.

### Phase 2: Interview (4 rounds, in order)

Follow `reference/interview-rounds.md`. Hard rules across all rounds:

1. **One question at a time.** Batching is forbidden.
2. **Propose your inferred answer first.** "My guess: X. Right?" — never "What do you think?".
3. **Cite the evidence with each question.** "from commit abc123" / "from README line 47" / "user just said".
4. **End each round with a recap.** "Here is what I will create. Confirm or edit."
5. **Commit drafts to disk between rounds.** User can pause and resume.

Rounds:

- **Round A — PROJECT.md** (10-15 min): background, long-term goals, non-goals, hard constraints, glossary, current stage, references
- **Round B — Decisions** (15-30 min): extract 3-10 active D-NNN with evidence
- **Round C — Open Questions** (5-10 min): extract 2-5 Q-NNN from TODOs + user memory
- **Round D — Experiments** (10-20 min, research only): extract 0-10 E-NNN

### Phase 3: Materialize

For each confirmed item:

- PROJECT.md → write to project root
- ROADMAP.md → update `docs/atlas/ROADMAP.md` if user has current milestones (else leave the template as-is)
- D / Q / E → call `atlas-entity` new.py for each
- Set `source: bootstrap` in each entity's frontmatter to mark as backfilled

Then:

```bash
python ~/.claude/skills/atlas-entity/scripts/reindex.py
python ~/.claude/skills/atlas-entity/scripts/validate.py
```

`validate.py` MUST return OK before declaring complete. Fix errors before reporting.

### Phase 4: Report

Give the user a summary in chat:

```
Bootstrap complete.
  PROJECT.md: written
  ROADMAP.md: updated (or: left as template — fill when you have current milestones)
  Decisions: 6 created (D-001 to D-006)
  Questions: 3 created (Q-001 to Q-003)
  Experiments: 4 created (E-001 to E-004)

What I deliberately did NOT do:
  - No journal entries created (journal is forward-only)
  - No superseded chains recorded (history stays in git log)
  - No prior-framework plans migrated as D-NNN (those are tactical, not architectural)
  - Rejected 4 weak D-NNN candidates I couldn't tie to specific evidence

Items I noticed but did not action (see bootstrap-extras.md):
  - 11 stale-looking TODOs
  - 3 D-NNN candidates with weak evidence

Suggested next step: at your next work session, run atlas-orient to load
the new context. Use atlas-log throughout work to start the journal organically.
```

If `bootstrap-extras.md` was created, name it explicitly so the user can find it.

## Anti-patterns

- **DO NOT** skip Phase 1 because the project looks familiar. Concrete scan output prevents recall hallucination.
- **DO NOT** batch all 4 rounds. User fatigue degrades quality.
- **DO NOT** create D-NNN you can't tie to evidence. "I think there's probably also..." is the slop signal — stop.
- **DO NOT** migrate prior framework's plans / specs wholesale. Read them, extract the architectural decision underneath, propose THAT as D-NNN.
- **DO NOT** clean up TODO markers in code. Not this skill's job.
- **DO NOT** invent goals the user did not confirm.
- **DO NOT** declare bootstrap complete without running validate.py.

## After bootstrap

Bootstrap is once-per-project. From then on, the normal atlas workflow takes over:

- `atlas-orient` at start of each session
- `grill-me` before any non-trivial task
- `atlas-log` throughout work
- `atlas-entity` for new D / Q / E during organic work
- `atlas-compact` periodically

If after bootstrap you realize a D-NNN was missed, just use atlas-entity to create it. Do not re-run bootstrap.

## Cross-references

- `atlas-init` creates the directory skeleton; this skill assumes that's done
- `atlas-entity` does the actual file creation for D / Q / E
- Going forward: grill-me + atlas-log + atlas-entity for organic work
