---
date: 2026-05-28
slug: sharpen-decision-recognition-criteria
project: Atlas
tags: [skills, using-atlas, atlas-entity, decisions, recognition]
status: closed
opened: 2026-05-28 14:56
closed: 2026-05-28 14:57
verification-result: passed
related: [D-013, D-014]
---

# Sharpen decision recognition criteria

## Context

Sharpen the D-NNN recognition criteria and put them where the agent actually sees them. The judgment "does this rise to a decision or stay in the journal?" happens before atlas-entity is invoked, so the criteria must live in a persistently-loaded surface (using-atlas body trigger row), not in atlas-entity's body — this is a direct application of D-013. Add the mental model "a decision is a constraint on future choices, not just important work" plus the three-month test to the using-atlas D/Q/E trigger row; make atlas-entity's "When to create what" echo the same model as a backstop without rewriting it.

## Work log

### 2026-05-28 14:57
Added a focused "Is it a D, or just a journal note?" heuristic to using-atlas's trigger section (right after the failure-mode note): a decision is a constraint on future choices, not important work; the three-month test; expensive-to-reverse and real-rejected-alternatives as the two pushing signals. Stated explicitly why it lives there rather than in atlas-entity's body (the call happens before atlas-entity is invoked — D-013). Echoed the same core test as a one-line lead-in to atlas-entity's "Decision (D-NNN)" section so the two surfaces stay consistent, leaving the existing "at least two are true" checklist as the fuller backstop. No new entity — this is an application of D-013, not a new decision.

## Close

Shipped: the D-recognition heuristic now lives in using-atlas's trigger section (persistently loaded), with the three-month test and the constraint-vs-work framing; atlas-entity's Decision section echoes the core test as a backstop. Verification (manual review): the new using-atlas paragraph reads cleanly between the failure-mode note and the operational-detail handoff; the cross-reference to D-013 is accurate; the two surfaces now state the same core test without contradiction. No new entity created — this is a direct application of D-013 (recognition belongs on persistently-loaded surfaces), not itself a new decision.
