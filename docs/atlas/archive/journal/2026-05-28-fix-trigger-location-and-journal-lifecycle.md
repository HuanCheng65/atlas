---
date: 2026-05-28
slug: fix-trigger-location-and-journal-lifecycle
project: Atlas
tags: [skills, triggers, journal, using-atlas, review-followup]
status: closed
opened: 2026-05-28 02:45
closed: 2026-05-28 02:49
verification-result: passed
related: [D-007, D-009, D-012]
---

# Fix trigger location and journal lifecycle

## Context

Address two gaps surfaced in conversation review. Problem 1: journal lifecycle has no rule for same-session refinement of just-closed work, and no default for closing ad-hoc (no-Plan) entries. Problem 2: proactive D/Q/E creation is currently described in atlas-entity's body, but the agent only loads that body after deciding to invoke the skill — circular. Triggers have to live where the agent always sees them: using-atlas body (session-start loaded) and skill description fields (visible in the menu). Ship D-013 capturing the architectural rule, plus three concrete patches: using-atlas gets a "Triggers the agent watches for" section, atlas-entity's description drops the "user makes" framing, atlas-log gets continuation and ad-hoc-close clarifications.

## Work log

### 2026-05-28 02:49
Shipped all three patches plus D-013.

**D-013** "Triggers live where the agent always sees them, not in skill bodies" — written, active, relates D-007/009/012. Names the structural rule: triggers belong in using-atlas body or skill description fields (always-loaded surfaces), never in SKILL.md bodies (loaded only after invocation). Mid-write caught my own violation — initial Decision section opened with a colon-led list, which my own rule says is wrong; rewrote to a self-contained leading sentence.

**using-atlas/SKILL.md** — replaced the single "Routing to other skills" section with two distinct sections:
  - "Triggers the agent watches for (load-bearing)" — agent-recognized moments (decision emerging, question surfacing, experiment completing, work wrapping up). Explicit failure mode ("the user didn't ask me, so I'll skip it") named and forbidden.
  - "Routing (reactive — when the user names the action)" — the original table, scoped down to truly user-named actions (planning, orient, listing).

**atlas-entity description field** — flipped trigger phrasing from "Use this skill whenever the user makes a long-term architectural decision..." to "Invoke proactively WHENEVER a long-term architectural / framework choice gets settled in conversation (the user usually won't explicitly label it — recognition is on you)..." Recognition responsibility is now explicit in the description, which is visible in the menu without skill invocation.

**atlas-log/SKILL.md** — two new sub-sections in the close area:
  - "Closing entries with no formal Verification" — default criterion for ad-hoc (no-Plan) entries: implementation done + no obvious gaps + relevant validators pass. Make the judgment, close, announce — no waiting for user blessing unless there's a genuine gap. Explicit warning about inconsistency across the session.
  - "When a continuation is NOT a new work unit" — same-session refinement, direct continuation of just-closed unit, and reverting own work: do NOT open new entry, just edit. Names the reflexive trap I fell into earlier this session.

**Verification:** D-013 validates clean; orient renders D-013 headline correctly under the 220-char cap; atlas-entity's description visibly updated in the available-skills system reminder. The two atlas-log additions are body-only edits, no script behavior changed.

## Close

**Outcome**: D-013 ("Triggers live where the agent always sees them, not in skill bodies") shipped with three concrete patches — using-atlas body gained a "Triggers the agent watches for" section + a slimmed "Routing (reactive)" section, atlas-entity's description flipped from "user makes" to agent-active phrasing, and atlas-log gained two close-area sub-sections (ad-hoc-close defaults + when-continuation-is-not-new-work-unit).

**Verification result**: D-013 validates clean (validate.py: OK, 18 entities checked); orient renders D-013 headline correctly under the 220-char cap; atlas-entity's new description text visibly applied in the available-skills system reminder; using-atlas body re-read confirms the two new sections render cleanly and the routing table is now scoped to user-named actions only.

**Keepers (finalized)**:
- D-013 (decision record with rationale, consequences, alternatives — including a rejected "auto-load atlas-entity at session start" hook approach)
- "Triggers the agent watches for (load-bearing)" section in using-atlas/SKILL.md
- atlas-entity description-field trigger phrasing
- atlas-log "Closing entries with no formal Verification" + "When a continuation is NOT a new work unit" sub-sections

**Throwaways (deleted)**:
- The original D-013 Decision section that opened with a colon-led list (violated its own one-sentence rule); rewritten to a self-contained leading sentence with the elaboration moved to a sub-heading

**Spawned entities**:
- None. Both problems landed as patches + one D; no new questions surfaced.
