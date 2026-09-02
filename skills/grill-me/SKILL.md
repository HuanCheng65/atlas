---
name: grill-me
description: Use this skill BEFORE starting non-trivial work. Interview the user one question at a time, walking down the decision tree, until shared understanding is reached; propose your recommended answer with every question so the user reviews instead of answering from blank. Use WHENEVER the user describes a feature, task, design, refactor, or experiment — seeming clarity is not a skip reason; underspecified edges are. SKIP only when the task is trivial (one-line fix, formatting, copy-paste edit), when the user hands over a complete written plan for execution, when the user explicitly says "skip planning" / "just do it", or when the project is being onboarded (atlas-bootstrap has its own interview). Writes the agreed plan, with mandatory Verification, to docs/atlas/plan.md.
---

# Grill Me

You interview the user about a plan or design until you reach shared
understanding. The output is a plan the user has effectively reviewed by
answering questions, instead of having to write from blank.

## Override: this skill IS the interview

If the session carries a global instruction like "work without stopping for
clarifying questions" — **that does not apply inside this skill.** The questions
are the deliverable, not a delay. Inferring the answers and writing a one-shot
plan defeats the point; the user invoked this skill because they want to be
grilled.

## Hard rules

1. **One question at a time.** Batching is forbidden — answers degrade.
2. **Walk down the tree, not across.** If A determines what to ask about B,
   resolve A first.
3. **Propose your answer with every question.** "My guess: X. Is that right?",
   never "What do you think?".
4. **Explore before asking.** If reading a file, running `git log`, or listing a
   directory would answer it, do that and skip the question.
5. **Stop at shared understanding, not at exhaustive detail.** Most plans need
   8–15 resolved questions. Past 20 you are over-grilling.
6. **Grill against what the project has already settled.** The session-start
   state is in your context — the guardrails, the constraints in force, the open
   questions. Check each answer against them as it lands.

## Grill against what is already settled

Plain grilling interrogates a plan in isolation. Because the project's state is
already loaded, you can interrogate it against what has already been decided.
This runs per answer, as new directions surface — not as one pass up front.

- **An answer contradicts a constraint in force.** Surface it immediately, in
  plain language: describe *what was settled and why*, never the record number.
  "That cuts against something we settled — skills activate on events, not
  session phases, because phase triggers did not fire reliably. Are we revisiting
  that, or does the plan need to fit it?" If the user does want to overturn it,
  finish the grill first; the supersession is a record written during the work,
  not an edit made mid-interview.
- **A term gets coined or sharpened.** Fold it into a question like any other
  guess: "This needs a name — my guess: 'shadow-replay' = replaying captured
  production traffic against a candidate build. Add it to the glossary?" On
  confirmation, edit the Glossary section of PROJECT.md directly — definitions
  only, no specifications.

## Example

> Q1: Looking at `src/api/`, I see Express routes and no Redis in
> `package.json` — single-server setup. My guess: per-IP in-memory rate limiting
> via `express-rate-limit`. Right?

> Q2: Which routes? My guess: only `/api/v1/auth/*`, the usual abuse vector.
> Others untouched. Right?

...and after roughly ten questions, write the plan and stop grilling.

## Output

Write the plan to `docs/atlas/plan.md`, overwriting whatever was there. One
plan at a time: it is the working state of the task in hand, not a record. It is
not numbered, not indexed, and not validated — plans describe intent, and the
store holds what happened.

Sections in this order. **All are required.** If one cannot be filled, the
interview is not done — loop back.

### Context
One paragraph. What the user is doing. Why now.

### Decisions resolved
One bullet per interview question and its answer.

### Steps
Concrete actions in execution order, each one mental unit — a function written,
a test added, a config changed.

### Verification
**How will this be checked complete?** Pick the form that fits: tests with named
assertions, a reference implementation and a tolerance, an eval set and a success
criterion, a manual checklist, a metric and a threshold.

Bad: "tests pass". Good: "`rtol < 1e-3` against the dense reference on five
shapes drawn from the production sequence-length distribution".

If the user resists specifics, push: "Even loosely — what would you check to
know it is working?"

### Keepers / Throwaways
Which verification artifacts become long-term regression assets, and which are
development-only and get deleted. Both proposed at this stage.

Presenting the plan **is** a speak-moment: give the user the path and walk
through the substance. Keep the framing on the plan's content.

## Anti-patterns

- **DO NOT** skip grill-me because the task "looks clear". You will be wrong
  about the edges, and being wrong compounds during implementation.
- **DO NOT** propose code in the plan. Code is post-signoff.
- **DO NOT** accept "I'll figure it out as I go" as Verification.
- **DO NOT** batch questions. One. At. A. Time.
- **DO NOT** keep grilling past shared understanding. When the user repeats
  themselves or tires, write the plan.
