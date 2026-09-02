# Interview Rounds

Run rounds in order A → B → C → D. Save drafts to disk between rounds so the user can pause and resume.

## Style rules (all rounds)

- One question at a time
- Propose your inferred answer first ("My guess: X. Right?")
- Cite the evidence with each question ("from commit abc123" / "from README" / "user just said")
- End each round with a recap: "Here's what I'll create. Confirm or edit."
- Recognize fatigue: if the user is repeating themselves or giving terse answers, wrap up

---

## Round A — PROJECT.md (10-15 min)

Goal: produce a complete PROJECT.md with all sections filled.

### Question order

1. **Name + one-line description** — usually from README. Confirm.
2. **Background** — "From what I read, this project exists because X. Anything to add?"
3. **Long-term goals** — "I see Y as the goal. What time horizon? Months or years?"
4. **Non-goals** — "Are there things you've explicitly decided NOT to do?" (often highest-info question; users have strong opinions here)
5. **Hard constraints** — "What's non-negotiable? Hardware, deadlines, dependencies?"
6. **Glossary** — list every project-specific term seen in code. Ask user to define each in one sentence.
7. **Current stage** — prototype / research / writeup / shipping / maintenance. Propose based on activity pattern.
8. **References** — "Key papers / repos / prior art I should record?"

### Drafting

After the questions, write the complete PROJECT.md to project root. Show it to user. Accept or iterate once. Leave **Working rules** empty in this round; Round B fills it from confirmed decisions, and on a project with no history it stays empty.

### Round A hard rules

- Background MUST cite source (README section / commit / user statement)
- Glossary MUST cover every project-specific term seen in code (don't skip "obvious" ones; they're only obvious to existing contributors)
- DO NOT invent goals the user didn't confirm

---

## Round B — Decisions (15-30 min)

Goal: extract 3-10 currently-active architectural decisions. Quality over quantity.

### Approach

Go through scan output. For each strong signal, propose ONE decision:

- Directory choice diverging from convention → likely a D
- Library / framework choice mentioned in README → likely a D
- "rewrite" / "switch" / "migrate" commit from scan → likely a D
- Existing ADR in `docs/adr/` → definitely a D
- README statement like "we use X because Y" → likely a D

Phrasing template for each candidate:

> "Looking at <evidence>, I see you chose <X> over <Y>. My guess: this was deliberate, because of <Z>. Record this?"

If yes: draft frontmatter + body with concrete `source` field. User reviews and edits.

### Does the decision also need a working rule?

Most do not. A record is consulted when someone works near it; PROJECT.md's **Working rules** are loaded into every session, so that section is a budget.

One test: *if nothing here stopped an agent from violating this, would it get violated?* A decision embodied in the code, the directory layout or a script's refusal is already enforced — leave it as a record. A standing rule that only exists in someone's head is what the section is for.

Ask the user per candidate rather than promoting on your own judgement, and write the confirmed ones into PROJECT.md during this round: one line each, ending with a `([[NNN-slug]])` link to the record it comes from.

### Round B hard rules

- Cap: **10 decisions max**. Overflow → `bootstrap-extras.md`.
- DO NOT propose D you can't tie to evidence. "I think there's probably also..." is the slop signal — STOP.
- DO NOT migrate task-level plans / specs wholesale. Read the plan, extract the *architectural choice underneath*, propose THAT.
- DO NOT create supersedes chains for past decisions. Record current state only.

---

## Round C — Open Questions (5-10 min)

Goal: capture 2-5 currently-open questions worth tracking.

### Sources

- Top TODOs from scan output
- Code XXX / FIXME comments visible in scan
- User memory: "What's been bugging you that you haven't had time to figure out?"

### Approach

- Show the user the top 5-10 TODOs from scan
- For each: "Real open question, or stale marker?"
- Real → draft a question record
- Stale → ignore (DO NOT clean up the TODO marker; that's outside scope)
- Then open-ended: "What else is bugging you?" — capture 1-2 from user's memory

### Round C hard rules

- Cap: **5 questions max**
- DO NOT create a question that has an obvious known answer
- DO NOT create a question that duplicates a decision

---

## Round D — Experiments (10-20 min, RESEARCH PROJECTS ONLY)

Skip entirely if:
- scan shows no `bench/` or `experiments/` directory
- user says this is a dev project, not research
- user explicitly says not to record experiments

### Sources

- `bench/` or `benchmarks/` directories
- `experiments/` directory
- Result files (`*.csv`, `*.json`) in known locations
- Paper draft directories (`paper/`, `manuscript/`)
- User memory: "Which past experiments will you likely cite in a paper or follow-up?"

### Approach

- List candidate experiments from scan
- For each: "Record this? It gets a hypothesis, setup, result and conclusion."
- Backfilled E may have weaker `hypothesis` than newly-created ones. Mark as `hypothesis: <backfilled — approximate>`.

### Round D hard rules

- Cap: **10 experiments max**
- Only record experiments user will plausibly cite later. One-off exploratory runs are not worth it.
- `result` field MUST link to the actual artifact (CSV path, log file) — don't paraphrase inline.

---

## Materialization (Phase 3 checklist)

After all rounds, before declaring bootstrap complete:

- [ ] PROJECT.md written to project root
- [ ] `docs/atlas/ROADMAP.md` populated (or left as template if user has no current milestone)
- [ ] Each decision created via one `new.py` call, body on stdin
- [ ] Each question created similarly
- [ ] Each experiment created similarly
- [ ] `bootstrap-extras.md` written if any overflow / weak candidates were skipped
- [ ] `atlas-entity` reindex.py run on all entity dirs
- [ ] `atlas-entity` validate.py returns OK
- [ ] User given Phase 4 report

---

## Pacing

- Round A: 10-15 min
- Round B: 15-30 min
- Round C: 5-10 min
- Round D: 10-20 min (research only)

Total: 30 min (small dev project) to 1.5 hr (large research project).

If you've been going much longer, you're over-grilling. Recognize the user is done answering, wrap up, write what you have.
