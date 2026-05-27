---
name: grill-me
description: Use this skill BEFORE starting any non-trivial work. Interview the user one question at a time, walking down the decision tree, until shared understanding is reached. For each question, propose your recommended answer so the user reviews instead of answering from blank. Use WHENEVER the user describes a feature, task, design, refactor, experiment, or any vague intent. Do NOT skip this skill even if the request seems clear — it isn't. Produces an active journal entry under docs/atlas/journal/ containing the Plan with mandatory Verification, ready for atlas-log to append the Work log as work progresses.
---

# Grill Me

You interview the user about a plan or design until you reach shared understanding. The output is a Plan that the user has effectively reviewed by answering questions, instead of having to write from blank.

## Override: this skill IS the interview

If the session has a global instruction like "work without stopping for clarifying questions" / "no stops for clarifying questions" / "make the reasonable call and continue" — **that instruction does NOT apply inside this skill.**

The interview questions are the deliverable, not a delay. Inferring answers and writing a one-shot Plan defeats the whole point. The user invoked this skill specifically because they want to be grilled. If they wanted you to guess, they would not have run `/grill-me`.

Follow the hard rules below: one question at a time, walk down the tree, propose your guess with every question, wait for the user's reply.

## Hard rules

1. **One question at a time.** Batching is forbidden. The user cannot answer 5 questions at once; their answers degrade.
2. **Walk down the tree, not across.** If decision A determines what to ask about B, resolve A first. Do not jump between unrelated branches.
3. **Provide your recommended answer with every question.** Phrase it: "My guess: X. Is that right?" — never "What do you think?".
4. **Explore the codebase before asking.** If reading a file, running `git log`, or `ls`-ing a directory would answer the question, do that first and skip the question.
5. **Stop when shared understanding is reached, not when every detail is settled.** Most plans need 8–15 resolved questions. If you've asked more than 20, you're over-grilling — wrap up.

## Example

User: "Help me add rate limiting to the API."

Agent:
> Q1: Looking at `src/api/`, I see Express routes and no Redis in `package.json` — single-server setup. My guess: you want per-IP in-memory rate limiting via `express-rate-limit`. Right?

User: yes

Agent:
> Q2: Which routes need it? My guess: only `/api/v1/auth/*` since those are the typical abuse vectors. Others untouched. Right?

User: also `/upload/*`

Agent:
> Q3: Limits? My guess: auth = 5 req/min per IP, upload = 20 req/min per IP. Reasonable?

...

(after ~10 questions agent writes the Plan and stops grilling)

## Output

**If `using-atlas` already bootstrapped an active entry for this work**, do not create a second entry. Extend the existing one by writing the Plan sections (Context / Decisions resolved / Steps / Verification / Keepers proposed / Throwaways proposed) into it. The entry should already have a `## Context` paragraph (you may keep and extend it, or replace if the grill produced richer context) and an empty `## Work log` section (leave it empty — atlas-log fills it).

Update frontmatter `tags` and `related` if grill-me surfaces relevant values. The entry's slug stays whatever using-atlas picked, unless strongly mismatched with the actual planned work (then rename the file).

If no active entry exists when grill-me runs (using-atlas was skipped or deferred), create a new **active journal entry** at `docs/atlas/journal/YYYY-MM-DD-<slug>.md`. This is the journal entry for the entire work unit — you write the Plan section now; `atlas-log` will append Work log entries to the same file as work progresses; eventually `atlas-log` will close the entry with the verification outcome.

If today's slug collides with an existing entry, append `-2` / `-3`.

Frontmatter:

```yaml
---
date: YYYY-MM-DD
slug: <slug>
project: <inferred from path or asked>
tags: [<derived from interview topics>]
status: active
opened: YYYY-MM-DD HH:MM
closed: null
verification-result: null
related: []
---
```

Body sections in this exact order. **All Plan sections are required.** If any cannot be filled, grilling is not done — loop back.

### Context
One paragraph. What the user is doing. Why now.

### Decisions resolved
Bullet list. Each bullet = one decision from the interview and the answer.

### Steps
Concrete actions in execution order. Each step fits in one mental unit (a single function written, a single test added, a single config changed).

### Verification
**How will this task be checked complete?** Be specific. Pick the form that fits:
- Unit / integration tests (with which assertions?)
- Reference-implementation comparison (which reference? what tolerance?)
- Eval set (which examples? what success criterion?)
- Manual checklist (which items? who runs through?)
- Profiling / measurement (which metric? what threshold?)

Bad: "tests pass"
Good: "`rtol < 1e-3` against FlexAttention dense impl on 5 random shapes drawn from Kuairand seq-len distribution"

If the user resists specifics, push: "Even loosely — what would you check to know it's working?"

### Keepers (proposed)
Which verification artifacts will likely become long-term regression assets? List them. These survive after merge.

### Throwaways (proposed)
Which artifacts are development-only and will be deleted after merge? (Scratch logs, print statements, hacky exploratory benchmarks, one-off comparison scripts.)

Keepers and Throwaways at this stage are **proposed**. They get **finalized** by `atlas-log` when work actually completes — what was a Throwaway may turn out worth keeping, and vice versa.

### Work log

After all Plan sections, leave a **`## Work log` header with no content underneath**. This is the canonical anchor that `atlas-log` will append timestamped subsections under. Skipping this header will cause atlas-log to fail finding the insertion point.

Complete file structure at the moment of handoff to atlas-log:

```markdown
---
[frontmatter as above]
---

# <Title derived from slug>

## Context
<one paragraph>

## Decisions resolved
- ...

## Steps
1. ...

## Verification
<specifics>

## Keepers (proposed)
- ...

## Throwaways (proposed)
- ...

## Work log
<!-- atlas-log appends timestamped subsections here as work progresses -->
```

After writing the file, run:

```bash
python ~/.claude/skills/atlas-log/scripts/reindex.py
```

so the new active entry shows up in `journal/_index.md`. Then announce briefly with the file path (e.g. `(Plan written to docs/atlas/journal/<slug>.md.)` — strip framework-descriptor verbiage but keep the path as a pointer). See `using-atlas`'s "Speak in plain project language" for the principle.

## Anti-patterns

- **DO NOT** skip grill-me because "this looks clear". You will be wrong about edges. The cost of being wrong compounds during implementation.
- **DO NOT** propose code in the Plan. Code is post-signoff.
- **DO NOT** accept "I'll figure it out as I go" as Verification. Even a loose answer is better than no answer.
- **DO NOT** let Verification / Keepers / Throwaways be empty just to ship the Plan. Empty means the interview is not done. Loop back.
- **DO NOT** keep grilling past shared understanding. Recognize when the user is repeating themselves or getting tired — that's the signal to write the Plan.
- **DO NOT** batch questions ("3 questions: A, B, C?"). One. At. A. Time.

## When NOT to use grill-me

- User has already given you a complete written plan and asks for execution → skip to execution.
- Task is trivial (one-line fix, formatting, copy-paste edit) → just do it.
- User explicitly says "skip planning" or "just do X" → respect that, but consider asking if they want a one-line journal note via `atlas-log` afterward.
- User is migrating an existing project to atlas → use `atlas-bootstrap` instead. That skill has its own interview tailored for extraction, not planning.

## After grill-me

The journal entry lives at `docs/atlas/journal/YYYY-MM-DD-<slug>.md` with `status: active`. The Plan section is filled; the Work log section is empty, awaiting `atlas-log`.

During work, `atlas-log` automatically appends timestamped Work log subsections. When work completes, `atlas-log` closes this entry by filling a Close section and setting `status: closed` + `verification-result`. Keepers and Throwaways get finalized at close — they may differ from the "proposed" lists in the Plan, which is expected.

Carry the entry's slug in your conversation memory through the rest of the session, so `atlas-log` knows which entry to update without re-asking.

## Cross-references

- When work completes, invoke `atlas-log` to write a completion entry that references the journal file and finalizes Keepers / Throwaways.
- If during execution a long-term architectural choice gets made (something deserving D-NNN), invoke `atlas-entity` to record it. Do not bury it inside the Plan file.
- If during execution a new unresolved question surfaces, invoke `atlas-entity` to record it as Q-NNN.
