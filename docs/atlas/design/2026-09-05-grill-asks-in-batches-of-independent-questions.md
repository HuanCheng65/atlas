# Grill asks in batches of independent questions

Continues `docs/atlas/design/2026-09-05-design-docs-replace-work-units.md`.

## Decided

`grill-me` asks one question at a time and forbids batching, on the ground that
batched answers degrade. Matt Pocock's `grilling`, which this skill descends
from, batches instead: it treats the interview as a decision tree and asks, in
one round, every question whose prerequisites are already settled — the ones
answerable now without guessing at answers not yet heard. The user answers the
round, the tree grows, the next round is computed.

Both rules are aimed at the same hazard and disagree only on the test. What
degrades an answer is being asked something that depends on an answer not yet
given; asking two independent questions together costs nothing. So the rule is
kept and its test replaced.

**Questions in one batch must be mutually independent.** If any question in the
batch depends on the answer to another question in the same batch, it belongs to
the next batch, not this one. The bound is independence, not count.

The presentation is taken from the original: each question numbered with a short
title, then its body, then the recommended answer on its own line, questions
separated by a rule. A round of several questions needs the visual separation,
and this layout has been in use long enough to have been shaped by that.

**Finding facts is the agent's job, never the user's.** A question answerable by
reading a file, listing a directory or running a tool is not put to the user; it
is dispatched to a sub-agent. Dispatch does not block the round: a running
exploration is an unsettled prerequisite, so only the questions downstream of it
wait, and the rest of the batch is asked now.

Three properties bound the dispatch, and they are stated as properties rather
than as a named agent type or model, because naming either couples this skill to
one harness:

- **The sub-agent is read-only and cheap.** Locating a file, reading a fragment,
  listing a directory: the smallest model that can do it is the right one. Move
  up only when a task genuinely needs judgment rather than retrieval.
- **It cannot dispatch sub-agents of its own.** Where the harness offers an
  agent kind without that capability, choosing that kind satisfies this
  mechanically rather than by instruction, which is the form to prefer
  ([[028-mechanical-affordances-over-prose-constraints-for-agent-rules]]).
- **No more than three or four run at once**, judged against the size of the
  round rather than filled up to. A round wanting more explorations than that is
  usually a round whose questions were not separated properly — something that
  should have been put to the user is being looked up instead.

None of this is mechanically checkable. Whether a batch was actually independent
and whether an exploration was actually warranted are judgments made during an
interview, and no test observes them. The source of the verdict is use: a batch
that was not independent shows up as the user answering a question and then
being asked something the answer already settled.

### What changes

- `skills/grill-me/SKILL.md` — hard rule 1 (one question at a time), hard rule 4
  (explore before asking, currently inline and blocking), and the example, which
  shows two sequential questions in the old format.
- The same file's frontmatter description, which is the surface routing reads
  and still promises an interview held one question at a time.

## Still open

