---
date: 2026-05-28
slug: grill-me-cross-check-decisions-glossary
project: Atlas
tags: [skills, grill-me, glossary, decisions, grill-with-docs]
status: closed
opened: 2026-05-28 14:41
closed: 2026-05-28 14:45
verification-result: passed
related: []
---

# Grill me cross check decisions glossary

## Context

Enhance grill-me to borrow the one behavior grill-with-docs (Matt Pocock, same author as grill-me) has that atlas lacks: during the interview, cross-check the plan against active D-NNN decisions and the PROJECT.md glossary, cite conflicts in plain language, and propose glossary/decision updates as terms and choices crystallize. We are NOT importing the external skill — atlas already covers ADRs (D-NNN), glossary (PROJECT.md), and inline doc updates (atlas-entity/atlas-log). The gap is that grill-me currently interrogates a plan in isolation; conflict-detection only fires at session start in atlas-orient, not mid-grill. (retroactive — from earlier in this conversation: user asked what grill-with-docs is and whether it's useful; we concluded skip the import, borrow the cross-check-during-interview behavior.)

## Work log

### 2026-05-28 14:44
Added hard rule #6 and a new "Grill against what's already decided" section to skills/grill-me/SKILL.md (the version-controlled source for the grill-me skill). The section defines two per-answer moves: (1) surface conflicts with active decisions in plain content language and route any supersede through atlas-entity — grill-me never edits decision records itself; (2) propose newly-coined or sharpened terms inline and, on confirmation, edit the PROJECT.md Glossary directly. Noted complementarity with orient's session-start conflict pass so future readers don't consolidate the two. Updated Cross-references with the supersede-routing link. Left the rate-limiting example untouched; the new section carries its own mini-examples.

## Close

Shipped: hard rule #6 + "Grill against what's already decided" section in skills/grill-me/SKILL.md, plus a Cross-references entry routing supersedes to atlas-entity. Recorded the responsibility shift as D-014 (active). Verification (manual review + validate.py): the new section reads coherently in the rules→section→example flow; no D-NNN IDs leak into user-facing dialogue snippets (D-011 respected); validate.py passes on 19 entities. Did not import the external grill-with-docs skill — atlas already covers ADRs, glossary, and inline updates; only the cross-check-during-interview behavior was borrowed.
