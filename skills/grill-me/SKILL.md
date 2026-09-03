---
name: grill-me
description: Use this skill BEFORE starting non-trivial work. Interview the user one question at a time, walking down the decision tree, until shared understanding is reached; propose your recommended answer with every question so the user reviews instead of answering from blank. Use WHENEVER the user describes a feature, task, design, refactor, or experiment — seeming clarity is not a skip reason; underspecified edges are. Use ALSO mid-work, whenever it emerges that the change touches something expensive to unmake — a stored data shape, an interface others call, an assumption that there is exactly one of something. SKIP only when the task is trivial (one-line fix, formatting, copy-paste edit), when the user hands over a complete written plan for execution, when the user explicitly says "skip planning" / "just do it", or when the project is being onboarded (atlas-bootstrap has its own interview). Writes intent, spec and plan to one file per work unit under docs/atlas/work/.
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

## Ask for a representation before asking for steps

A plan is usually split along the order the user described it in, and the code
is then split the same way. That order rarely matches where change arrives.
Adding a second campus to a schema with no campus column is hard because the
module boundaries are in the wrong place, not because the code is bad.

**When the change touches something expensive to unmake, settle a
representation before writing steps.** Four tells, any one is enough:

- data is already stored in the shape being changed
- callers already depend on the interface being changed
- the design assumes there is exactly one of something
- it crosses to a side you do not control — an external API, a file format, a
  vendor, an OS

**When none of them holds, pick an implementation and move on.** An abstraction
added for a change that never arrives costs more to remove than a late one
costs to add.

Propose the representation the way you propose everything else, as a guess to be
corrected, and name which kind it is:

| kind | fits when |
|---|---|
| intermediate representation | the same computation must exist in two forms, and the risk is in translating between them |
| reference implementation | a slow, obviously-correct version can exist, and the real one is checked against it |
| schema or type | data will accumulate in this shape and outlive any one version of the code |
| state machine | the thing has modes, and some transitions must be impossible |
| protocol or interface | two sides must agree and are written separately |
| invariant list | correctness is a property that must hold, not an output to compare |

Then check the concrete proposal with three questions that need no architectural
taste to answer:

1. **What does this assume** — exactly one of something, always this format,
   this ordering, never empty? Which of those assumptions would need a data
   migration or a change to callers to unmake?
2. **How many places state the same fact?** If one constant changes, how many
   edits is that?
3. **When the result is wrong, what tells you which part is wrong?** If the
   answer is "run the whole thing and see it fail", the parts are not yet
   separable.

Answer with the artifact, not with a claim: the operators the representation
has, the columns the schema has. "It is modular" is satisfiable by assertion,
so it will be satisfied by assertion.

**Splitting work across parallel agents is itself an architectural decision.**
The division of tasks becomes the division of the code. Settle the module
boundaries first, then split the work along them.

## Every check names where its verdict comes from

A test written after the code, from the code, asserts what the code does rather
than what was required. That is a **characterization test**: legitimate when the
subject is code being refactored and the point is to detect change, and wrong
only when it is unacknowledged and read as a correctness check.

So the Verification section names, for each check, the source of its judgment:

- a reference implementation — the verdict comes from another program
- a property or invariant — `decode(encode(x)) == x`
- real data whose answers are known independently
- a failure that actually happened and is now recorded
- values the user specified

**If the source is the code under test, say so and say why that is what you
want.** Anything with no source named is not a check; it is decoration.

The bar is on the source, not the form. Tests, a reference comparison, an eval
set, a manual checklist and a measured threshold all qualify once the source is
named. Writing the test first is one way to keep the source independent of the
implementation; any other way serves as well.

## Example

> Q1: Looking at `src/api/`, I see Express routes and no Redis in
> `package.json` — single-server setup. My guess: per-IP in-memory rate limiting
> via `express-rate-limit`. Right?

> Q2: Which routes? My guess: only `/api/v1/auth/*`, the usual abuse vector.
> Others untouched. Right?

...and after roughly ten questions, write the plan and stop grilling.

## Output

Open the file with the script, which owns the date and writes the skeleton:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/grill-me/scripts/start.py" \
    --slug <kebab-case-slug>
```

Then fill the three sections with Edit. **The file is written once and not
edited afterwards.** It is a dated account of what was undertaken, which stays
true; that is why it can be committed without going stale. There is no work log,
no status, and nothing to come back and close.

### Intent
What the user is doing, and why now. One or two paragraphs.

### Spec
What the result must satisfy. The representation, when the work called for one,
and why that kind. Then Verification — each check with the source of its verdict
named, per the bar above.

Bad: "tests pass". Good: "`rtol < 1e-3` against the dense reference on five
shapes drawn from the production sequence-length distribution" — the dense
reference being the source.

If the user resists specifics, push: "Even loosely — what would you check to
know it is working?"

Close the Spec with Keepers and Throwaways. **A Keeper records a specific
failure that occurred, or an invariant stated somewhere. Everything else is a
Throwaway by default** — a check corresponding to no named failure or invariant
is deleted with the scaffolding.

### Plan
Concrete actions in execution order, each a single unit of work: a function
written, a test added, a config changed.

Present the file to the user: give the path and walk through the substance,
keeping to the plan's content.

## What belongs in the store instead

The work unit file holds what was undertaken. Three things outlive it and are
written as records during the work, not collected at the end:

- a constraint **nothing stops the agent from violating** — a `memory` record,
  because it must be restated every session
- a choice that is **architecturally significant** — a `decision` record, whose
  value is the rationale when someone revisits it
- a measurement, or a question left open

A choice that is only how this task got done stays in the Spec section. The code
enforces it, so violating it requires rewriting that code rather than drifting.

## Anti-patterns

- **DO NOT** skip grill-me because the task "looks clear". You will be wrong
  about the edges, and being wrong compounds during implementation.
- **DO NOT** propose code in the plan. Code is post-signoff.
- **DO NOT** deliver a representation and its implementation in the same turn.
  The design becomes a preamble hurried past on the way to the code.
- **DO NOT** accept "I'll figure it out as I go" as Verification, or a check
  with no named source.
- **DO NOT** batch questions. One. At. A. Time.
- **DO NOT** keep grilling past shared understanding. When the user repeats
  themselves or tires, write the plan.
- **DO NOT** edit a work unit file after the work moves on. It said what was
  undertaken; a later change is a later work unit.
