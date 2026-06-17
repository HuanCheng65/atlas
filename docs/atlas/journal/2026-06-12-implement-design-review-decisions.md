---
date: 2026-06-12
slug: implement-design-review-decisions
project: Atlas
tags: [skills, orient, project-md, hooks, scripts, tests, data-model]
status: closed
opened: 2026-06-12 16:25
closed: 2026-06-17 15:22
verification-result: partial
related: []
---

# Implement design review decisions

## Context

Implement the five decisions produced by this session's design review as one interlocking batch: the constitution/archive split for decisions (curated standing-rules section in PROJECT.md, shrunken orient D-menu), orient's rework to scan frontmatter directly with _index.md demoted to deterministic human-only views, context-window activation semantics for the session-start hook, the mechanical-affordance applications (open.py deriving the project name from PROJECT.md, narrowing atlas-log's frontmatter ban to script-owned fields), and the no-framework-events conventions (silent operations, speak only when user input is needed, atlas changes ride work commits). (retroactive — from earlier in this conversation) The last of these was settled in discussion immediately after the design-review journal entry closed: the user observed that atlas still surfaces explicitly in chat and as standalone atlas-doc commits in git history; unified diagnosis was that the framework generates events of its own on the user's two primary surfaces, and the direction settled was silence-by-default plus records riding the work unit's own commits.

## Decisions resolved

- **D-menu mechanism**: new `triage` frontmatter field on decisions — `pending` (template default) | `promoted` | `archival`. Orient's decision menu shows `pending` only. No time-based heuristics; compact will later propose triage flips.
- **Constitution form**: new `## Working rules` section in PROJECT.md — one bullet per rule, one sentence, trailing `(D-NNN)` pointer. Orient inlines it in full alongside Non-goals / Hard constraints.
- **No duplication for hard-constraint decisions**: validate's promoted⟺pointer check scans all of PROJECT.md, so the plain-text and skills/data-split decisions keep their existing Hard constraints bullets and just gain `(D-001)` / `(D-002)` pointers.
- **Bidirectional validation**: `triage: promoted` ⟺ a `(D-NNN)` pointer exists in PROJECT.md; every pointer must reference an existing, `status: active` decision. Superseding a promoted decision therefore fails validation until the constitution line is updated — the two-place maintenance is mechanically guarded.
- **Initial triage**: in-batch, as one batch-review table (agent drafts triage value + constitution-line draft per decision; user reviews once). Constitution line count is a watched budget; ~10 lines expected.
- **Glossary additions**: "Working rules" and "Triage".
- **Verification tooling**: pytest as a dev dependency — the runtime-deps hard constraint covers what adopting projects need, not this repo's dev tooling (user confirmed). Tests are Keepers.
- **Sequencing**: data layer & scripts → constitution + triage review → skill prose rewrites → hook split → tests + manual checklist.

## Steps

1. Add `triage: pending` to the decision template, both copies (`docs/atlas/_templates/decision.md`, `templates/_templates/decision.md`).
2. Backfill `triage: pending` into D-001..D-021 frontmatter so validate stays green before the review pass.
3. validate.py: require `triage` on D with legal values; promoted⟺PROJECT.md-pointer bidirectional check; every `(D-NNN)` pointer in PROJECT.md must resolve to an existing active D.
4. Draft the triage table (per D: proposed value + constitution-line draft or one-line archival reason) — user reviews, then apply: flip frontmatter values, write `## Working rules` + pointers into PROJECT.md, add the two glossary terms.
5. orient.py rework: scan entity/journal frontmatter directly (drop `_index.md` parsing); D menu = pending only, with a one-line summary of promoted/archival counts; inline Working rules; journal actives + closed-within-14-days computed at render time.
6. journal reindex.py: drop the run-date-dependent "Recent closed" section (keep Active / By tag / By month); confirm byte-determinism on double run.
7. open.py: `--project` becomes optional override; default derives from PROJECT.md's H1 (strip a leading "Project:" prefix); loud error when neither is available.
8. atlas-log SKILL.md: narrow the frontmatter-edit ban to script-owned fields (`opened`, `closed`, `status`, `verification-result`, Work log timestamp headers; `tags`/`related` explicitly editable); rewrite announce guidance to silence-by-default (speak only when user input is needed — close *proposals* remain such a moment).
9. using-atlas SKILL.md: rewrite Layer 2 (silence by default; D/Q/E proposals batch at natural seams; conflict alerts stay immediate); "once per session" → "once per context window"; add the commit convention (atlas changes ride work commits; atlas-only commits only when atlas content is the work; messages name the content).
10. grill-me SKILL.md + atlas-entity SKILL.md: align announce/proposal wording with the same conventions (plan review stays a speak-moment — the user must see the plan path).
11. bin/atlas-init: CLAUDE.md managed block gains the commit convention; refresh this repo's own CLAUDE.md block to match.
12. Hook split in `~/.claude/settings.json`: matcher `startup|clear|compact` → using-atlas demand (drop "resume" from the wording); matcher `resume` → atlas-orient refresh directive. Verify SessionStart matcher syntax against current Claude Code docs before editing.
13. tests/: pytest suite covering orient filtering + constitution inlining + render-time recency, validate bidirectional checks, reindex determinism, open.py project derivation, and regressions for today's script fixes (new.py title quoting, find_entry exact match, close.py double-refusal).
14. Run the 4-item manual hook checklist; sync docs (docs/atlas/README.md, templates/README.md, docs/design.md) with the new model.

## Verification

- `pytest tests/` green, asserting: orient menu lists exactly the `triage: pending` decisions of a fixture project; Working rules renders in full; closed-entry recency computed from frontmatter at render time; validate fails on (a) promoted-without-pointer, (b) pointer-to-missing-or-inactive-D, (c) illegal triage value, and passes on a consistent fixture; journal reindex run twice on the same fixture produces byte-identical output; open.py derives "Atlas" from `# Project: Atlas`; new.py round-trips a title containing ": "; find_entry rejects suffix collisions; close.py refuses both an existing Close section and a second close.
- Real repo: validate.py OK; orient output shows Working rules inlined and a D menu equal to the post-review pending set; `git diff` empty after a second reindex run.
- Manual hook checklist: /clear in an atlas project → using-atlas demanded; resume → orient refresh only; compact → using-atlas demanded; non-atlas project → hook silent.

## Keepers (proposed)

- `tests/` pytest suite (first regression assets of the repo) including its fixture builders.

## Throwaways (proposed)

- /tmp sandbox projects used during development; any scratch fixtures not promoted into `tests/`.

## Work log

### 2026-06-12 16:28
D-021 recorded (framework generates no events: silent ops, speak only when user input needed, atlas changes ride work commits; atlas-only commits legal only when atlas content is the work). While recording it, new.py crashed loudly on the title's ": " — the template substitution hand-rolled YAML by injecting the raw title into the frontmatter. Fixed: the title is now JSON-escaped before substitution (a JSON string is a valid YAML double-quoted scalar); body {{TITLE}} stays raw. Verified by re-creating D-021 with the colon title — frontmatter parses, validate.py OK.

### 2026-06-12 16:45
Steps 1-3 and 5-7 done (script/data layer, reordered slightly ahead of the triage review since they don't depend on its outcome): triage field added to both decision-template copies and backfilled as pending into D-001..D-021 via the entity _lib round-trip; validate.py now requires/checks triage values and enforces the constitution pairing bidirectionally (promoted⟺pointer, pointer⟺existing active D); orient.py rewritten to scan entity/journal frontmatter directly — D menu filters to triage:pending, Working rules joins the inlined guardrail sections, the 14-day recency window is computed at render time; journal reindex.py dropped the run-date-dependent Recent-closed section (double-run now byte-identical); open.py derives the project name from PROJECT.md's H1 with --project as override. Fixed in passing: first_sentence leaked the second line of multi-line HTML template comments into headlines — comments are now stripped wholesale before sentence extraction. Sandbox verified all validate failure modes fire loudly and pass on a consistent fixture; real repo validate OK (27 entities), orient output correct against current data.

### 2026-06-12 17:16
Steps 8-14 done. atlas-log: frontmatter ban narrowed to script-owned fields (opened/closed/status/verification-result/work-log headers; tags/related explicitly editable), all announce guidance replaced with silence-by-default, fallback open.py example updated for project auto-derivation. using-atlas: Layer 2 rewritten as "silent by default, speak only when the framework needs the user" (entity confirmation at seams / plan review / binding ambiguity / immediate conflict alerts), trigger table now batches D/Q/E proposals at natural seams while keeping recognition immediate, "once per session" became "once per context window" with resume→orient-only semantics, new "Atlas changes ride work commits" section. grill-me and atlas-entity aligned (plan review kept as a speak-moment; entity workflow gained triage and supersede-updates-constitution steps). atlas-init's managed CLAUDE.md block and this repo's CLAUDE.md gained the commit convention. Hook split into four matcher-differentiated SessionStart entries (startup/clear/compact → using-atlas demand reworded for context-window semantics; resume → atlas-orient refresh directive); JSON validated with jq, both commands pipe-tested including the non-atlas-dir silent case. pytest suite added at tests/test_atlas_scripts.py (17 tests: open.py derivation/override/failure, find_entry suffix rejection, close double-refusals, journal reindex determinism + no run-date section, new.py colon-title round-trip + 70-char word-boundary truncation + auto-reindex, validate constitution pairing in all five failure modes + consistent pass, orient menu filtering + constitution inlining + render-time recency + no comment leakage) — all green, runs via repo-local .venv (pytest+pyyaml; .gitignore'd). Docs synced: docs/atlas/README.md + templates/README.md (triage, human-only deterministic indexes, commit convention), templates/PROJECT.md (Working rules skeleton), atlas-orient SKILL.md (frontmatter-direct reads, new summary shape), design.md (principles 10-12, announce reversal recorded in trade-offs, resolved index-tracking question removed), bootstrap interview rounds (Round B triages each confirmed D and writes Working rules lines). Orient output on the real repo dropped from ~120 to 74 lines. Remaining: 4-item manual hook checklist (needs the user — /clear, resume, compact, non-atlas project).

## Close

**Outcome**: The five design-review decisions landed as one interlocking batch — triage field + constitution/archive split (Working rules in PROJECT.md), orient reworked to scan frontmatter directly with `_index.md` demoted to human-only views, context-window activation semantics for the session-start hook, mechanical-affordance applications (open.py derives the project name, atlas-log's frontmatter ban narrowed to script-owned fields), and silence-by-default / records-ride-work-commits conventions.

**Verification result**: partial. Automated coverage is green — pytest (26 tests) and validate.py both pass; the hook commands were pipe-tested at build time. The `clear → using-atlas demanded` leg of the manual hook checklist was observed working this session (this session began on a /clear and the hook fired). The remaining legs — resume → orient-only, compact → using-atlas, non-atlas project → silent — were not exercised end-to-end. Closed `partial` rather than `passed` to record that outstanding observation honestly (cf. the open question on whether verification-result carries signal).
