---
id: 29
title: 'Framework generates no events: silent ops, records ride work commits'
date: 2026-06-12
type: decision
tags: [skills, ux, transparency, git, agent-behavior]
---

# Framework generates no events: silent ops, records ride work commits

## Context

Even with the two-tier vocabulary rule in force, dogfood showed atlas still surfacing on the user's two primary surfaces: chat (a one-line operational announce after every open / append / close, plus mid-flow D/Q proposals) and git history (standalone "update atlas docs" commits). The unified diagnosis: the framework was generating events of its own instead of riding inside work events. Decomposing the announces showed the category is hollow — their content is either work content (a benchmark result belongs unwrapped in the normal reply) or pure bookkeeping (which has no action value for the user in the moment).

## Decision

Atlas generates no events of its own: operations run silently and chat mentions atlas only when user input is needed (entity confirmation, plan review, ambiguity resolution — batched at natural seams; conflict alerts — surfaced immediately), while atlas file changes ride the work unit's own commits; atlas-only commits are legitimate only when atlas content is itself the work, with messages naming the content, never the framework.

## Rationale

- Announce content is either work content or bookkeeping; the first belongs in the normal reply unwrapped, the second belongs nowhere in chat — the announce category collapses.
- Binary rules resist agent drift better than calibrated ones (the [[028-mechanical-affordances-over-prose-constraints-for-agent-rules]] logic): "say nothing" outlasts "say one line in the right register", which needed three repair rounds in three weeks.
- The accountability channel moves from chat to commit review: the work diff carries its own record — a stronger audit point than a transient chat line, and one the user already attends to.
- Extending the vocabulary principle to commit messages keeps git history readable as a work narrative: messages say what was decided or built, not that the framework was updated.

## Consequences

- using-atlas / atlas-log / grill-me announce instructions are rewritten: silence by default; speak only when a user decision is needed. The two-tier vocabulary rule survives unchanged as the how-to-speak rule; this decision narrows the when-to-speak.
- D/Q/E proposals batch at natural seams (work wrap-up, close, a user pause); conflict surfacing stays immediate — it is the framework's first-order reason to exist.
- The commit convention (atlas changes ride work commits; atlas-only commits only for atlas-content work) lands in using-atlas and in atlas-init's CLAUDE.md block so user-driven commits learn it too.
- This reverses an explicitly recorded early trade-off ("post-hoc one-line announces achieve accountability") on dogfood evidence; the reversal is safe because the commit-ride policy replaces the audit channel that announces provided.
- Accepted cost: user-driven partial commits (e.g. `git add src/`) leave atlas changes dangling until the next commit — a tolerable timeline misalignment, since journal files are per-unit and git blame on them is not load-bearing.
- Constitution candidate under the [[026-decisions-stay-adr-events-standing-rules-promote-into-project-md]] test: violating it produces no visible resistance.

## Alternatives considered

- **Keep one-line post-hoc announces (status quo)** — rejected: dogfood shows persistent framework presence in chat, and announce content decomposes into duplicated work content or pure bookkeeping.
- **Separate branch / git notes for atlas data** — rejected: violates plain-text-plus-git simplicity and tool portability (GitHub browsing, plain clones).
- **Mechanically splitting or squashing commits via hooks** — rejected: history rewriting is riskier than the noise it removes; a stated convention plus the existing review moment suffices.
