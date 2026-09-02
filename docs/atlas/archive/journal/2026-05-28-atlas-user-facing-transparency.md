---
date: 2026-05-28
slug: atlas-user-facing-transparency
project: Atlas
tags: [skills, ux, agent-behavior, transparency]
status: closed
opened: 2026-05-28 02:10
closed: 2026-05-28 02:14
verification-result: passed
related: []
---

# Atlas user facing transparency

## Context

Make atlas transparent in user-facing chat. Principle: internally the agent reads/writes D/Q/journal with full framework vocabulary (clear and unambiguous), but externally to the user it translates into plain project language — the user feels the effect (continuity, conflict-detection, memory) without being asked to context-switch into "the framework". Surfaced by the user after a previous conversation where I said "和 atlas 里 D-007 冲突" instead of describing the decision in plain terms. Scope: audit all skill files for user-facing output conventions (announce lines, conflict-surfacing language, references to file paths / artifact IDs) and either silence them, soften them, or translate.

## Work log

### 2026-05-28 02:14
Audited all six skills for user-facing emissions. Four needed changes; two left as-is.

**Edited:**
- `using-atlas/SKILL.md`: added top-level "Speak in plain project language" section as the foundational rule (with Why, How to apply, Bad/Good examples, and three exceptions: explicit user request, working on atlas itself, atlas-bootstrap). Updated the post-`open.py` announce to drop the file path and the word "journal" — recommends "(I'll keep a log as we go.)" or silence. Added a new anti-pattern banning framework artifact names in chat.
- `atlas-log/SKILL.md`: rewrote the post-append announce to "(logged: …)" form, dropping the path and "journal". Added permission to skip the announce entirely when the user is mid-flow on heavy work. Softened the close announce similarly ("(closed — verification passed)"). Reworded the propose-close phrasing example into plain terms. Added an anti-pattern.
- `atlas-orient/SKILL.md`: rewrote step 2 of "After orient" to specify that conflicts must be surfaced in plain language (decision content, not D-NNN ID; what was done, not journal filename). Same softening on the "which entry?" disambiguation. Updated the relevant anti-pattern.
- `grill-me/SKILL.md`: changed the post-Plan-write announce from "Plan written to journal/<slug>.md. Ready to start." to "Plan's ready. Want to start?" — drops file path entirely.

**Left as-is:**
- `atlas-entity/SKILL.md`: contains no chat-output convention; using-atlas's foundational rule covers it.
- `atlas-bootstrap/SKILL.md`: Phase 4 Report intentionally names D-NNN/Q-NNN/E-NNN — bootstrap is the moment the user is being introduced to the framework, which is the explicit exception in the new principle.

Cross-references added in all four edited files pointing back to using-atlas's "Speak in plain project language" so the principle has a single source of truth.

## Close

**Outcome**: Four skill files updated to enforce user-facing transparency. `using-atlas` now carries the foundational rule; `atlas-log`, `atlas-orient`, and `grill-me` cross-reference it and have softened their respective announce / surface conventions. `atlas-entity` and `atlas-bootstrap` left as-is by design.

**Verification result**: grep confirms no remaining instances of "opened journal/" (outside the Bad/Good counterexample in the principle), "appended to journal/", or "Plan written to journal/" in the skill instructions. The single remaining match is intentional — it's the bad-example in the principle's How-to-apply section.

**Keepers (finalized)**:
- The "Speak in plain project language" section at the top of `using-atlas/SKILL.md` — single source of truth for the rule
- Updated announce conventions in `atlas-log` (append + close) and `grill-me` (post-Plan)
- "Speak in plain language" guidance added to `atlas-orient`'s conflict-surfacing step
- New anti-patterns in `using-atlas` and `atlas-log`

**Throwaways (deleted)**:
- A draft `feedback_atlas_transparent_to_user.md` memory file that was written before the user clarified this is a framework issue, not a user-memory issue. Removed.

**Spawned entities**:
- None. This was a behavior-rule update, not an architectural decision worth a D-NNN.
