---
date: 2026-05-28
slug: orient-coverage-and-project-authoring
project: Atlas
tags: [skills, orient, project-md, progressive-disclosure, authoring]
status: closed
opened: 2026-05-28 16:00
closed: 2026-05-28 16:06
verification-result: passed
related: [D-012, D-010]
---

# Orient coverage and project authoring

## Context

orient.py's PROJECT.md rendering misses load-bearing sections entirely: Non-goals and Hard constraints are never surfaced, so the agent doesn't know they exist and never reads them on demand — violating the progressive-disclosure principle that the menu must at least name what's important. Background/Stage/Roadmap-milestone also truncate mid-sentence because they use line-count slicing (first_lines) instead of the sentence-aware first_sentence used for entities. Plan: (A) rework orient's Project section to list all section headings as a menu plus inline the short high-value lists (Background failure modes, Non-goals, Hard constraints), and make truncation sentence-aware; (B) adjust PROJECT.md authoring so each section is either an inlineable short list or leads with a self-contained summary sentence, and remove the stale, scope-overlapping "Current stage" field (status lives in ROADMAP's Current milestone). Two candidate decisions surfaced: orient must include hard-constraints/non-goals in the menu, and mutable status must not live in the keep-stable PROJECT.md.

## Work log

### 2026-05-28 16:04
Reworked orient.py Project rendering: replaced line-count truncation (first_lines) with sentence-aware extraction, inlined the two guardrail sections (Non-goals, Hard constraints) in full, added a "More in PROJECT.md" menu line so unrendered sections stay discoverable, and removed the now-dead first_lines helper. Fixed roadmap milestone rendering to a bold-header + first-sentence hybrid (no more mid-word truncation). Edited PROJECT.md: Background now leads with a self-contained summary sentence; collapsed the stale multi-phase "Current stage" narrative to a one-line lifecycle marker pointing at ROADMAP. Encoded the authoring convention in templates/PROJECT.md (lead with extractable first sentence; keep guardrails as short bullet lists; keep Current stage to one word). Verified by running orient.py — guardrails now visible, no dangling fragments, stage no longer contradicts ROADMAP. Note: diverged from the earlier "delete Current stage" proposal — collapsed it instead, since the template intends it as a one-word lifecycle marker orthogonal to ROADMAP's milestone.

### 2026-05-28 16:06
Recorded the authoring convention as D-016 (active): PROJECT.md authored for orient extraction — self-contained first sentence per prose section, guardrails as short bullet lists orient inlines, Current stage as one lifecycle word; mutable/forward status lives only in ROADMAP. Related to the CLAUDE/PROJECT split, roadmap-single-section, and progressive-disclosure decisions. reindex + validate pass (21 entities).

## Close

orient.py truncation fixed and guardrail sections (Non-goals, Hard constraints) now surfaced; PROJECT.md Background leads with an extractable sentence and Current stage collapsed to a one-line marker; authoring convention encoded in the template and recorded as D-016. Verified by running orient.py: clean headlines, guardrails visible, stage no longer contradicts ROADMAP.
