---
name: grill-me
description: Interview the user before non-trivial work until you reach shared understanding, then write down what was settled. Use WHENEVER the user describes a feature, task, design, refactor or experiment — seeming clarity is not a skip reason, underspecified edges are — and ALSO mid-work, when the change reaches something expensive to unmake: a stored data shape, an interface others call, an assumption that there is exactly one of something. SKIP for trivial tasks, a complete plan handed over to execute, "just do it", and onboarding (atlas-bootstrap has its own interview). Writes one design document per round under docs/atlas/design/.
---

# Grill Me

You interview the user until you reach shared understanding. The output is a
document they reviewed by answering questions, rather than wrote from blank.

A session instruction like "work without stopping for clarifying questions"
does not apply here. The questions are the deliverable.

## Rules

1. **Questions in one round must be mutually independent.** What degrades an
   answer is depending on an answer not yet given; independent questions cost
   nothing together. The bound is independence, not count.
2. **Propose your answer with every question.** "My guess: X. Right?", never
   "What do you think?".
3. **Finding facts is your job, never the user's.**
4. **Stop at shared understanding, not exhaustive detail.** Most rounds need
   8–15 resolved questions. Past 20 you are over-grilling.
5. **Check each answer against what the project has already settled** as it
   lands — the guardrails, constraints and open questions already in context.

## Rounds

The interview is a decision tree. A round asks every question whose
prerequisites are settled; the user answers, the tree grows, and the next round
is what that opened up. A first round, after a sub-agent reported what is in
`src/api/`:

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

What the limit should be waits for the next round: it depends on which routes
are covered.

Dispatch a sub-agent for anything answerable from the filesystem, the git
history or a tool, and do not wait on it — only the questions downstream of a
running exploration move to a later round. Read-only, on the smallest model
that can do the job. It must not dispatch sub-agents of its own; where the
harness offers an agent kind that cannot, pick that kind, so the limit holds
mechanically. Three or four at once is a ceiling: wanting more usually means
something that should have been put to the user is being looked up instead.

## Grill against what is already settled

- **An answer contradicts a constraint in force.** Say so immediately, in plain
  language — what was settled and why, never the record number: "That cuts
  against something we settled: skills activate on events, not session phases,
  because phase triggers did not fire reliably. Revisiting it, or does the plan
  fit it?" If the user overturns it, finish the grill first; the supersession is
  a record written during the work, not an edit made mid-interview.
- **A term gets coined or sharpened.** Fold it into a question: "This needs a
  name — my guess: 'shadow-replay' = replaying captured production traffic
  against a candidate build. Add it to the glossary?" On confirmation, edit
  PROJECT.md's Glossary directly — definitions only.

## Ask for a representation before asking for steps

A plan split along the order the user described it in produces code split the
same way, and that order rarely matches where change arrives. Adding a second
campus to a schema with no campus column is hard because the module boundaries
are wrong, not because the code is bad.

Settle a representation first when any one of these holds: data is already
stored in the shape being changed; callers already depend on the interface
being changed; the design assumes there is exactly one of something; it crosses
to a side you do not control. Otherwise pick an implementation and move on — an
abstraction added for a change that never arrives costs more to remove than a
late one costs to add.

Propose it as a guess to be corrected, and name which kind:

| kind | fits when |
|---|---|
| intermediate representation | one computation must exist in two forms, and translating between them is the risk |
| reference implementation | a slow, obviously-correct version can exist to check the real one against |
| schema or type | data will accumulate in this shape and outlive the code |
| state machine | the thing has modes, and some transitions must be impossible |
| protocol or interface | two sides must agree and are written separately |
| invariant list | correctness is a property that holds, not an output to compare |

Then check it: what does it assume — exactly one of something, always this
format, this ordering, never empty — and which of those needs a migration or a
change to callers to unmake? How many places state the same fact? When the
result is wrong, what tells you which part is wrong? Answer with the artifact,
the operators and the columns. "It is modular" is satisfiable by assertion, so
it will be.

Splitting work across parallel agents is itself an architectural decision: the
division of tasks becomes the division of the code.

## Every check names where its verdict comes from

A test written after the code, from the code, asserts what the code does rather
than what was required — a characterization test, legitimate for detecting
change in code being refactored, misleading when read as a correctness check.
So name the source of each judgment: a reference implementation, a property
(`decode(encode(x)) == x`), real data whose answers are known independently, a
failure that actually happened, or values the user specified. If the source is
the code under test, say so and why. With no source named it is not a check.

The bar is on the source, not the form. Tests, a reference comparison, an eval
set, a manual checklist and a measured threshold all qualify once it is named.

## Output

**A grill crosses one gap, and the gaps do not come in a fixed set.** Clarifying
a vague requirement, settling a product's form, settling how one module is
built, ordering the implementation steps — each is one round. Name the level in
the title, and do not manufacture a level the round never reached: a round that
settled a design and reached no implementation is complete without a plan in it.
Spec and design are the same content from two sides — what one round chose among
alternatives is what the next must satisfy.

`ls docs/atlas/design/` first: the filenames carry date and topic, so the
listing is the menu, and it says whether this round continues an earlier one.
Then open the file with the script, which owns the date and writes the skeleton.
Exactly one of `--from` or `--new` is required:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/grill-me/scripts/start.py" \
    --slug <kebab-case-slug> --from 2026-09-05-product-form.md
```

Fill the two sections with Edit. **The file is written once and not edited
afterwards** — a dated account of one round, which stays true. There is no work
log, no status, nothing to close.

**Decided.** What the round settled, each item naming how it is judged and
where that verdict comes from. Bad: "tests pass". Good: "`rtol < 1e-3` against
the dense reference on five shapes drawn from the production sequence-length
distribution". An item whose only source is the user's preference says so; one
that cannot yet be judged says that. If the user resists specifics, push: "Even
loosely — what would you check to know it is working?" Implementation steps go
here too when the round reached them, in execution order, and so does the
Keepers and Throwaways split: **a Keeper records a specific failure that
occurred, or an invariant stated somewhere; everything else is a Throwaway** and
is deleted with the scaffolding.

**Still open.** What this round did not settle, as of today. Not a live TODO
list: nothing closes these entries and nobody ticks them off. An entry must be
able to seed the next round — an empty section is the right answer for a round
that settled everything in front of it.

Then give the user the path and walk them through the substance.

## What belongs in the store instead

Three things outlive the document and are written as records during the work,
not collected at the end: a constraint **nothing stops the agent from
violating** (a `memory` record, since it must be restated every session); a
choice that is **architecturally significant** (a `decision` record, whose value
is the rationale when someone revisits it); a measurement, or a question left
open. A choice that is only how this task got done stays in Decided — the code
enforces it, so violating it means rewriting that code rather than drifting.

## Anti-patterns

- **DO NOT** skip grill-me because the task "looks clear". You will be wrong
  about the edges, and being wrong compounds during implementation.
- **DO NOT** propose code. Code is post-signoff.
- **DO NOT** deliver a representation and its implementation in the same turn.
  The design becomes a preamble hurried past on the way to the code.
- **DO NOT** keep grilling past shared understanding. When the user repeats
  themselves or tires, write the document.
