---
date: 2026-05-28
slug: formalize-progressive-disclosure-conventions
project: Atlas
tags: [skills, data-model, orient, naming, progressive-disclosure]
status: closed
opened: 2026-05-28 02:29
closed: 2026-05-28 02:40
verification-result: passed
related: [D-009, D-005, D-001]
---

# Formalize progressive disclosure conventions

## Context

Formalize "atlas = progressive disclosure for project state" as D-012, then ship its three derivatives: naming rules for D/Q/E titles (atlas-entity), naming rules for journal slugs (atlas-log), and a richer orient summary that pulls each entity's first-section sentence into the listing.

Surfaced when the user noticed atlas's structural similarity to skill design (description as menu, body on demand) and asked whether titles/slugs needed a principle. Holds off on a section-extract tool — wait for pain.

## Work log

### 2026-05-28 02:38
Shipped all three derivatives plus the meta-D.

**D-012** "Progressive-disclosure data layer: title is the menu, body loads on demand" — written, active, relates D-001/005/009, validates clean. Three commitments: title-as-menu-signal, first-section-is-one-sentence-self-contained, cross-references-over-inlining.

**Templates** (`docs/atlas/_templates/{decision,question,experiment}.md`) — added title rules in YAML comments, and explicit "ONE SENTENCE, gets pulled into orient summary" guidance on `## Decision` / `## Hypothesis` / `## Why this matters` first sections.

**atlas-entity/SKILL.md** — new sections "Naming: title is the menu signal" (universal rules + type-specific table + the "read it cold" test) and "Section conventions: first section is one sentence, self-contained".

**atlas-log/SKILL.md** — new sections "Naming: slug is the menu signal" (with good/bad table) and "Section convention: first sentence of Context carries the work".

**atlas-orient/scripts/orient.py** — added `first_sentence()` (handles wrapped paragraphs, splits on sentence-ending punct, 220-char ellipsis cap as safety net), `entity_file()`, `headline_for_entity()`, `headline_for_journal()`. `render_entity_list` now appends `  → <first sentence>` under each bullet for D/Q/E; `render_journal` does the same for active entries. Recent closed (table format) left untouched.

**Mid-stream fix:** user caught me writing "Naming (D-012):" and inline "(D-012)" everywhere in the SKILL files. Reverted — skills are operational guidance for the agent doing the work *now*; the D record exists separately for future maintainers. Don't mix channels. Templates also cleaned of "(D-012)" comments.

**Dogfood pass:** orient output now shows headlines for all 12 active Ds. D-007 reads "Skills activate on events, not phases." — exactly the menu signal we want, would never have surfaced from title alone. My own Context paragraph here was originally one 600-char run-on; rewrote to a tight first sentence per the new convention (orient's 220-char ellipsis cap was a safety net catching my own violation).

## Close

**Outcome**: D-012 ("Progressive-disclosure data layer: title is the menu, body loads on demand") shipped with all three concrete derivatives — title/slug naming rules in atlas-entity and atlas-log, first-section-is-one-sentence convention in templates, and orient.py rendering headlines under each D/Q/E and active journal entry.

**Verification result**: orient.py now outputs `→ <first sentence>` lines for all 12 active Ds, 5 open Qs, and 1 active journal entry; entity validate.py clean (17 entities checked); grep confirms no inline `D-012` references in operational files (skills, templates); dogfooded by tightening this entry's own Context paragraph to a self-contained first sentence.

**Keepers (finalized)**:
- D-012 (decision record + rationale + alternatives)
- Naming + Section conventions sections in atlas-entity/SKILL.md
- Naming + Section convention sections in atlas-log/SKILL.md
- Title-rule YAML comments + one-sentence Decision/Hypothesis/Why-this-matters guidance in all three entity templates
- orient.py `first_sentence`, `headline_for_entity`, `headline_for_journal` helpers; entity bullets now carry a one-line headline

**Throwaways (deleted)**:
- An accidentally-opened `atlas-transparency-recalibrate-announces` journal entry (deleted earlier when the user flagged that same-session refinement of just-closed work shouldn't open a fresh entry)
- An initial D-012 file with a too-long title; recreated with the tighter title

**Spawned entities**:
- D-012 created during this work
- Two follow-up issues surfaced for the user's review (journal lifecycle ambiguity; agent proactivity on D creation) — not yet recorded as Q/D, awaiting decision on shape
