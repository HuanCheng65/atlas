---
date: 2026-05-28
slug: strip-project-entity-refs-from-distributed-skills
project: Atlas
tags: [skills, distribution, hygiene, using-atlas]
status: closed
opened: 2026-05-28 15:01
closed: 2026-05-28 15:02
verification-result: passed
related: []
---

# Strip project entity refs from distributed skills

## Context

The skills under skills/ ship as a generic framework to other projects, so citing atlas's own entity IDs (D-001, D-013) as the *authority* for an instruction is a leak — those IDs are meaningless or wrong in a distributed copy. Caught in using-atlas: the "(per D-013)" added earlier this session and a pre-existing "(D-001)". Fix: state the underlying reasoning self-contained, drop the ID. Placeholder uses (D-007/D-012 as "suppose a decision called X" to teach syntax or in command examples) are kept — they're foo/bar-style teaching tokens, not references to atlas's real decisions. Surfaces a general hygiene rule worth recording: distributed skill bodies must not cite this project's real entity IDs as rationale.

## Work log

### 2026-05-28 15:02
Removed two authority-style entity-ID citations from using-atlas: the "(per D-013)" I added when sharpening the D-recognition heuristic, and a pre-existing "the journal is plain text + git (D-001)". Both rewritten to state the reasoning inline (the body-loads-after-invocation point; "plain text + git") so a distributed copy reads correctly. Audited all of skills/ via grep for [DQE]-NNN: the remaining hits are placeholders (D-007/D-012 as syntax examples, command-usage samples, schema field examples) and reverse-examples teaching agents NOT to say IDs in chat — those are fine, kept. The atlas-entity backstop line I added references only the skill name using-atlas, no ID — fine. Open item to raise with user: grill-me's plain-language example reuses the *content* of a real decision (event-driven activation) without the ID — teaching value vs project-specificity tradeoff.

## Close

Removed the two authority-style entity-ID citations from using-atlas (D-013, D-001), rewrote both inline. Audited all of skills/ — remaining [DQE]-NNN hits are placeholders/teaching tokens, kept. Recorded the general rule as D-015 (active). Verification: grep over skills/ shows no remaining authority-style ID citations (only placeholders, command examples, and the reverse-examples that teach agents not to say IDs in chat); validate.py passes. Left open for the user: grill-me's plain-language example reuses a real decision's content (without an ID) — judged teaching-value-positive, but flagged.
