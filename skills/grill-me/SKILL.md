---
name: grill-me
description: Use this skill BEFORE starting non-trivial work. Interview the user in rounds — each round asking together every question whose prerequisites are already settled — until shared understanding is reached; propose your recommended answer with every question so the user reviews instead of answering from blank. Use WHENEVER the user describes a feature, task, design, refactor, or experiment — seeming clarity is not a skip reason; underspecified edges are. Use ALSO mid-work, whenever it emerges that the change touches something expensive to unmake — a stored data shape, an interface others call, an assumption that there is exactly one of something. SKIP only when the task is trivial (one-line fix, formatting, copy-paste edit), when the user hands over a complete written plan for execution, when the user explicitly says "skip planning" / "just do it", or when the project is being onboarded (atlas-bootstrap has its own interview). Writes one design document per round under docs/atlas/design/: what the round decided, and what it left open.
---

# Grill Me

You interview the user about a plan or design until you reach shared
understanding. The output is a document the user has effectively reviewed by
answering questions, instead of having to write from blank.

## Override: this skill IS the interview

If the session carries a global instruction like "work without stopping for
clarifying questions" — **that does not apply inside this skill.** The questions
are the deliverable, not a delay. Inferring the answers and writing a one-shot
plan defeats the point; the user invoked this skill because they want to be
grilled.

## Hard rules

1. **Questions in one round must be mutually independent.** If a question
   depends on the answer to another question in the same round, it belongs to
   the next round. What degrades an answer is being asked something that
   depends on an answer not yet given; asking independent questions together
   costs nothing. The bound is independence, not count.
2. **Walk down the tree, not across.** If A determines what to ask about B,
   resolve A first.
3. **Propose your answer with every question.** "My guess: X. Is that right?",
   never "What do you think?".
4. **Finding facts is your job, never the user's.** If reading a file, running
   `git log`, or listing a directory would answer it, do that instead of asking.
5. **Stop at shared understanding, not at exhaustive detail.** Most plans need
   8–15 resolved questions. Past 20 you are over-grilling.
6. **Grill against what the project has already settled.** The session-start
   state is in your context — the guardrails, the constraints in force, the open
   questions. Check each answer against them as it lands.

## Ask in rounds, and go and find the facts yourself

The interview is a decision tree. A round asks every question whose
prerequisites are already settled — the ones answerable now without guessing at
an answer you have not heard. The user answers the round, the tree grows, and
the next round is whatever that opened up. A question that depended on another
in the round just asked belongs to the next one.

Number each question, give it a short title, and put your recommended answer on
its own line:

```
❓ **Q1** — **<title>**: <the question, and the choices if there are any>

➡️ <your recommended answer, and why>

---

❓ **Q2** — **<title>**: …

➡️ …
```

A question answerable from the filesystem, the git history or a tool is never
put to the user. Dispatch a sub-agent to find out, and do not wait on it: a
running exploration is an unsettled prerequisite, so only the questions
downstream of it move to a later round while the rest of this one is asked now.

Three properties bound the dispatch:

- **Read-only, and the smallest model that can do the job.** Locating a file,
  reading a fragment, listing a directory — that is retrieval, not judgment.
  Move up only when the task genuinely needs judgment.
- **It must not be able to dispatch sub-agents of its own.** Where the harness
  offers an agent kind without that capability, pick that kind, so the limit
  holds mechanically rather than by instruction.
- **No more than three or four at once**, and that is a ceiling judged against
  the round, not a number to fill. Wanting more usually means the round was not
  separated properly, and something that should have been put to the user is
  being looked up instead.

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

So each thing the round decided names the source of the judgment on it:

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

The first round, after a sub-agent has reported what is in `src/api/`. The two
questions are independent — neither answer changes what the other is asking —
so they go together:

> ❓ **Q1** — **Where the counter lives**: `src/api/` is Express routes with no
> Redis in `package.json`, so this is a single server. My guess: per-IP
> in-memory rate limiting via `express-rate-limit`.
>
> ➡️ In-process counter. A shared store is only worth it once there is a second
> server, and adding it later is a config change.
>
> ---
>
> ❓ **Q2** — **Which routes**: every route, or only the ones worth protecting?
>
> ➡️ Only `/api/v1/auth/*`, the usual abuse vector. The rest untouched.

What the limit should be belongs to the next round: it depends on which routes
are covered. After roughly ten resolved questions, write the document and stop
grilling.

## Output

One round of grilling produces one design document. Before the interview
starts, `ls docs/atlas/design/` — each filename carries a date and a topic, so
the listing is the whole menu — and see whether this round continues an earlier
one.

Open the file with the script, which owns the date and writes the skeleton.
Exactly one of `--from` or `--new` is required:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/grill-me/scripts/start.py" \
    --slug <kebab-case-slug> --from 2026-09-05-product-form.md
```

Then fill the two sections with Edit. **The file is written once and not edited
afterwards.** It is a dated account of one round of thinking, which stays true;
that is why it can be committed without going stale. There is no work log, no
status, and nothing to come back and close.

**A grill crosses one gap, and the gaps do not come in a fixed set.** Clarifying
a vague requirement, settling a product's form, settling how one module is
built, ordering the implementation steps — each is one round, and which one this
is depends on where the interview started, not on a schema. Name the level in
the title. Do not manufacture a level the round never reached: a round that
settled a design and reached no implementation is complete without a plan in it.

There is no separate Spec and no separate design. They are the same content seen
from two sides — what one round chose among alternatives is what the next round
must satisfy.

### Decided
What the round settled. Each item carries how it is judged right or wrong and
where that verdict comes from, per the bar above.

Bad: "tests pass". Good: "`rtol < 1e-3` against the dense reference on five
shapes drawn from the production sequence-length distribution" — the dense
reference being the source. An item whose only source is the user's preference
says so. An item that cannot yet be judged says that, rather than being left
blank.

If the user resists specifics, push: "Even loosely — what would you check to
know it is working?"

When the round reached implementation steps, they go here too, in execution
order, each a single unit of work — and so does the Keepers and Throwaways
split, which only means something once there is scaffolding to classify.
**A Keeper records a specific failure that occurred, or an invariant stated
somewhere. Everything else is a Throwaway by default** — a check corresponding
to no named failure or invariant is deleted with the scaffolding.

### Still open
What this round did not settle, **as of today**. It is not a live TODO list:
nothing closes these entries, and nobody comes back to tick them off. The test
for an entry is that it could seed the next round of grilling; anything that
could not is not an entry, and an empty section is the right answer for a round
that settled everything in front of it.

Present the file to the user: give the path and walk through the substance,
keeping to the document's content.

## What belongs in the store instead

The design document holds what one round settled. Three things outlive it and
are written as records during the work, not collected at the end:

- a constraint **nothing stops the agent from violating** — a `memory` record,
  because it must be restated every session
- a choice that is **architecturally significant** — a `decision` record, whose
  value is the rationale when someone revisits it
- a measurement, or a question left open

A choice that is only how this task got done stays in the Decided section. The
code enforces it, so violating it requires rewriting that code rather than
drifting.

## Anti-patterns

- **DO NOT** skip grill-me because the task "looks clear". You will be wrong
  about the edges, and being wrong compounds during implementation.
- **DO NOT** propose code in the document. Code is post-signoff.
- **DO NOT** deliver a representation and its implementation in the same turn.
  The design becomes a preamble hurried past on the way to the code.
- **DO NOT** accept "I'll figure it out as I go", or a check with no named
  source.
- **DO NOT** put a question in the same round as the question it depends on.
  Independence is the bound, not the number of questions.
- **DO NOT** ask the user for a fact you could look up.
- **DO NOT** pad Still open. An entry that could not seed the next round is not
  an entry, and hedging on something the round actually settled belongs in
  Decided.
- **DO NOT** keep grilling past shared understanding. When the user repeats
  themselves or tires, write the document.
- **DO NOT** edit a design document after the round moves on. It said what that
  round settled; a later change is a later round.
