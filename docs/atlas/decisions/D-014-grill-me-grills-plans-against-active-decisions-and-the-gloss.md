---
id: D-014
title: grill-me grills plans against active decisions and the glossary
date: 2026-05-28
status: active
triage: archival
tags: [skills, grill-me, glossary, decisions]
related: []
source-journal: 2026-05-28-grill-me-cross-check-decisions-glossary.md
supersedes: []
superseded-by: []
affects: [grill-me, atlas-entity, atlas-orient]
---

# grill-me grills plans against active decisions and the glossary

## Context
grill-me previously interrogated a plan in isolation. A separate author's grill-with-docs variant (Matt Pocock, same lineage as grill-me) interrogates the plan against the project's existing domain docs instead. Atlas already owns the pieces that variant writes to — decisions (D-NNN), the PROJECT.md glossary, inline updates via atlas-entity/atlas-log — but nothing cross-checked the plan against them *during* the interview; conflict-detection only fired once at session start in atlas-orient.

## Decision
grill-me cross-checks each answer against the active decisions and the PROJECT.md glossary as the interview proceeds, surfaces decision conflicts in plain content language, edits the glossary inline as terms resolve, and routes any decision supersede through atlas-entity rather than editing decision records itself.

## Rationale
The cross-check-during-interview behavior is the one thing grill-with-docs does that atlas lacked, and it is the move that separates a deep grill from a shallow one. Keeping the *write* boundary clean — glossary edits yes, decision-record edits no — preserves one-skill-per-cognitive-domain (D-009): grill-me writes plans, atlas-entity owns decision lifecycle.

## Consequences
- grill-me now edits the Glossary section of PROJECT.md directly (plain markdown, definitions only) on user confirmation during the interview.
- Decision conflicts surfaced mid-grill route to atlas-entity for supersede; grill-me never mutates a D-NNN file.
- The per-answer cross-check is complementary to atlas-orient's one-shot session-start conflict pass — both exist on purpose; they should not be consolidated.
- Slight lengthening of the grill-me body (one hard rule + one section); no new scripts or machinery.

## Alternatives considered
- **Import grill-with-docs as-is** — rejected: duplicates machinery atlas already has (ADRs→D-NNN, glossary, inline updates) and writes to a conflicting CONTEXT.md/docs/adr layout that breaks the plain-text+git data layer (D-001) and entity model (D-004).
- **grill-me only proposes glossary terms, user edits PROJECT.md** — rejected: loses the inline-capture habit that makes the doc-update side-effect valuable; the glossary is low-risk plain markdown.
- **Add a glossary script to atlas-entity** — rejected as scope creep; direct markdown edit needs no new tooling.
- **Also borrow codebase-as-source-of-truth contradiction-checking** — rejected: already covered by grill-me hard rule #4 ("explore the codebase before asking").
