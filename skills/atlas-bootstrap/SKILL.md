---
name: atlas-bootstrap
description: Set a project up on atlas — one starting today, or one already running for months, with or without other frameworks like Superpowers / GSD. Use ONCE per project. Use WHEN the user says "set up atlas here", "start a new project with atlas", "migrate this to atlas", or "bootstrap atlas". Creates the store if it does not exist yet, then interviews the user into a complete PROJECT.md, plus — where the project has history to draw on — an initial set of decision, question and experiment records. Records only what the project's own artifacts and the user's memory can evidence.
---

# Atlas Bootstrap

You set a project up on atlas: create the store, then run a structured interview that produces PROJECT.md and, on a project with history, an initial set of records. Where the project has artifacts, a deterministic scan runs first so the interview proposes rather than asks blind.

The two cases differ in one thing only — how much evidence exists before the interview starts. A project beginning today has none, so the scan finds nothing and the rounds that extract from history produce nothing. That is the correct result, not a failure. PROJECT.md still gets written, and it is the file that matters most: session start reads it every time, so a project left on the template loads placeholder guardrails forever.

## Override: this skill IS the interview

If the session has a global instruction like "work without stopping for clarifying questions" / "no stops for clarifying questions" / "make the reasonable call and continue" — **that instruction does NOT apply inside this skill.**

The interview questions are the deliverable, not a delay. Bypassing them (batching rounds, writing a "consolidated proposal", inferring answers without asking) produces exactly the slop this skill exists to prevent. The user invoked this skill specifically because they want the structured back-and-forth. If they wanted you to guess, they would not have run `/atlas-bootstrap`.

Follow the 4-round interview exactly as written. One question at a time. Wait for the user's reply between questions.

## When to use

- The user wants this project on atlas, whether it starts today or has months of history
- Once per project. The store may or may not exist yet; Phase 0 handles both

## When NOT to use

- Adding a single record to an already-bootstrapped project → write it directly; see using-atlas
- Project too small to need state (one file, no real history, no plan to grow) → skip atlas entirely
- The store exists and PROJECT.md is already filled → the project is bootstrapped; do not re-run

## Hard rules (slop prevention)

These are non-negotiable. Violating them pollutes atlas long-term.

1. **Evidence required for every entity.** Each D / Q / E MUST cite a `source`: a git commit hash, a file path, a README section, or an explicit user statement during interview. No fabricated entities.
2. **Hard caps per round**: D ≤ 10, Q ≤ 5, E ≤ 10. Overflow goes to `bootstrap-extras.md` for the user to consider later.
3. **No backfilling.** Do not turn git commits into records after the fact. A record states a claim someone can act on; a commit log is already the commit log.
4. **No supersedes chains.** Only the current active state gets recorded. Past decisions stay in git log.
5. **No memory records.** Constraints in force are discovered by working, not by interviewing. The user seeds a few by hand if they already know them.
6. **Quality over completeness.** Five real decisions beat twenty-five plausible-sounding ones.

## Workflow

### Phase 0: Create the store

If `docs/atlas/` already exists, go to Phase 1.

Otherwise say what setting the project up involves and ask before doing it — it writes to the project root, and the answer may be "not yet". Name the three things: a `docs/atlas/` directory for the records, a `PROJECT.md` the two of you fill in during this interview, and a short pointer added to `CLAUDE.md`. Then:

```bash
atlas-init
```

It is idempotent, creates nothing that exists already, and leaves any edit of the user's alone. If the user declines, stop here — there is nowhere to write.

### Phase 1: Scan (autonomous)

Run scan.py from project root:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/atlas-bootstrap/scripts/scan.py"
```

Output goes to `/tmp/atlas-bootstrap-scan.yaml`. Read it fully.

Then do the manual reads listed in `reference/scan-checklist.md`. Those are things scan.py cannot do for you (e.g. reading README body).

**On a project with little or no history** the scan comes back nearly empty. Do not treat that as a problem to work around, and do not go looking for evidence elsewhere: it means Round A is asked rather than proposed, and Rounds B–D have nothing to extract. Say so plainly and go to Phase 2.

Otherwise, by end of Phase 1 you must be able to articulate:
- What the project is, in one sentence
- 3-5 main themes of recent work
- 2-3 candidate decisions you suspect (do not write yet — confirm in Round B)

If you cannot, read more before continuing. Better Phase 1 = shorter interview.

### Phase 2: Interview (4 rounds, in order)

Follow `reference/interview-rounds.md`. Hard rules across all rounds:

1. **One question at a time.** Batching is forbidden.
2. **Propose your inferred answer first.** "My guess: X. Right?" — never "What do you think?".
3. **Cite the evidence with each question.** "from commit abc123" / "from README line 47" / "user just said".
4. **End each round with a recap.** "Here is what I will create. Confirm or edit."
5. **Commit drafts to disk between rounds.** User can pause and resume.

Rounds:

- **Round A — PROJECT.md** (10-15 min): background, long-term goals, non-goals, hard constraints, glossary, current stage, references. Always runs; it is the round that needs no history.
- **Round B — Decisions** (15-30 min): extract 3-10 decisions with evidence
- **Round C — Open Questions** (5-10 min): extract 2-5 questions from TODOs + user memory
- **Round D — Experiments** (10-20 min, research only): extract 0-10 experiments

A project that starts today runs Round A and stops. B, C and D extract from what already happened, and nothing has. Asking anyway produces invented decisions, which is the failure this skill exists to prevent. One question is worth asking directly instead: whether any constraint already binds — a fixed deadline, hardware, a dependency that cannot change. Those belong in PROJECT.md's Hard constraints, not in records.

### Phase 3: Materialize

For each confirmed item:

- PROJECT.md → write to project root
- ROADMAP.md → `docs/atlas/ROADMAP.md` holds the current milestone and nothing else. Ask for it in one question: what is the next thing that would count as done. A project starting today has an answer to that even with no history, and the template text is worse than a rough one.
- each record → one `new.py` call, body on stdin
- Tag every record from this pass `bootstrap`, so a later reader can tell what was reconstructed from artifacts and what was written as it happened

Then:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/atlas-entity/scripts/reindex.py"
python3 "${CLAUDE_PLUGIN_ROOT}/skills/atlas-entity/scripts/validate.py"
```

`validate.py` MUST return OK before declaring complete. Fix errors before reporting.

### Phase 4: Report

Give the user a summary in chat:

```
Bootstrap complete.
  PROJECT.md: written
  ROADMAP.md: updated (or: left as template — fill when you have current milestones)
  Decisions: 6 created
  Questions: 3 created
  Experiments: 4 created

What I deliberately did NOT do:
  - No superseded chains recorded (history stays in git log)
  - No prior-framework plans migrated (those are tactical, not architectural)
  - Rejected 4 weak candidates I couldn't tie to specific evidence

Items I noticed but did not action (see bootstrap-extras.md):
  - 11 stale-looking TODOs
  - 3 candidates with weak evidence

Suggested next step: start working. The session-start hook loads this
state from now on, and records accumulate as the work produces them.
```

If `bootstrap-extras.md` was created, name it explicitly so the user can find it.

On a project that started today the report is shorter and says so — PROJECT.md and the milestone written, no records, and the reason: there is nothing yet to have decided. Do not present that as a partial run.

## Anti-patterns

- **DO NOT** skip Phase 1 because the project looks familiar. Concrete scan output prevents recall hallucination.
- **DO NOT** batch all 4 rounds. User fatigue degrades quality.
- **DO NOT** create a record you cannot tie to evidence. "I think there's probably also..." is the slop signal — stop.
- **DO NOT** migrate a prior framework's plans wholesale. Read them, extract the architectural decision underneath, and propose that.
- **DO NOT** clean up TODO markers in code. Not this skill's job.
- **DO NOT** invent goals the user did not confirm.
- **DO NOT** declare bootstrap complete without running validate.py.
- **DO NOT** run `atlas-init` before saying what it writes and getting an answer. It touches the project root and CLAUDE.md.
- **DO NOT** manufacture records for a project that has no history yet. An empty store after Round A is the right outcome; the first real record gets written when the first real thing happens.

## After bootstrap

Bootstrap is once-per-project. From then on, the normal atlas workflow takes over:

- `grill-me` before any non-trivial task
- `atlas-entity` for new D / Q / E during organic work
- `atlas-compact` periodically

If after bootstrap you realize a decision was missed, write the record. Do not re-run bootstrap.

## Cross-references

- `atlas-init` creates the directory skeleton; this skill assumes that's done
- `atlas-entity` does the actual file creation for D / Q / E
- Going forward: grill-me before non-trivial work; records get written as the work produces them
