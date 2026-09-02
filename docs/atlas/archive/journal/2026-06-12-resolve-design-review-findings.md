---
date: 2026-06-12
slug: resolve-design-review-findings
project: Atlas
tags: [design, decisions, project-md, review-followup]
status: closed
opened: 2026-06-12 16:03
closed: 2026-06-12 16:18
verification-result: passed
related: []
---

# Resolve design review findings

## Context

Walk through the design-level findings from this session's framework review (the bug-class findings were fixed and closed separately) and settle a direction for each: D-list scaling / decision positioning, orient parsing derived views, index nondeterminism, hook-vs-skill session semantics, grill-me description/body mismatch, verification-result signal, and prose-vs-mechanical enforcement. (retroactive — from earlier in this conversation) The first topic, decision positioning, was discussed over several exchanges: the user challenged the ADR borrowing ("decisions or principles?"), which reframed the scaling problem as a usage-model mismatch — ADR's record format was borrowed together with a load-everything-at-session-start consumption pattern ADR never had. Direction settled: decisions stay an ADR-style event log; standing rules promote into a curated constitution section of PROJECT.md.

## Work log

### 2026-06-12 16:04
Decision-positioning question settled and recorded as D-017 (constitution/archive split): D records stay an ADR-style event log; standing rules promote as one-liners with D-pointers into a curated PROJECT.md constitution section; orient inlines the constitution and shrinks the D menu to recent/unreviewed; compact gains the promote-or-archive review duty; validate gains a pointer check. Working promotion test: "does violating it produce visible resistance?" — embodied decisions stay archival, behavioral constraints promote. Implementation deferred until the orient-related findings (direct frontmatter scan, deterministic index) settle so the orient rework lands once.

### 2026-06-12 16:07
Orient/index direction settled and recorded as D-018: orient (and any agent-facing read) scans entity/journal frontmatter directly; _index.md files demoted to deterministic human-only browse views (run-date-dependent sections like the journal's 14-day window move into orient's render-time logic; full by-status/by-tag/by-month listings stay). Index stays git-tracked; gitignore+regenerate remains the fallback. Implementation will land together with D-017's orient menu changes so orient is rebuilt once.

### 2026-06-12 16:10
Activation-unit semantics settled and recorded as D-019: the counting unit for session-start setup is the context window, not the session. Context rebuilt (startup/clear/compact) → hook demands fresh using-atlas; intact window → re-invocation stays forbidden; resume → hook asks only for an atlas-orient refresh (instructions still in context, project state possibly moved). Fix lands as hook matcher differentiation + using-atlas wording change ("once per session" → "once per context window").

### 2026-06-12 16:14
grill-me description/body mismatch fixed (no new D — this applies the existing triggers-live-in-persistent-surfaces principle): the absolute "Do NOT skip even if the request seems clear" in the description is replaced with "seeming clarity is not a skip reason; underspecified edges are" plus the four skip conditions lifted up from the body (trivial task / complete written plan handed over / explicit skip request / onboarding via atlas-bootstrap). Body's "When NOT to use" section unchanged; the two layers now agree. One wording tweak vs the reviewed draft: dropped an inline "when:" colon so the YAML frontmatter stays a plain scalar — verified the frontmatter still parses.

### 2026-06-12 16:17
Final two items settled. D-020 recorded (mechanical affordances over prose constraints): when an agent rule can be enforced by a script default/refusal, hook, or validator, build the mechanism; prose is reserved for judgment calls. First applications attached to the record: open.py derives the project name from PROJECT.md's H1 (--project becomes override), and atlas-log's frontmatter ban narrows to script-owned fields (opened/closed/status/verification-result/work-log timestamp headers) with tags/related explicitly editable — dissolving the grill-me collision. Q-006 opened for the verification-result signal question (all 13 closes are 'passed'); to be answered by observation during the dogfood week. All seven design-level findings from the review now have a settled direction: D-017 (decision positioning), D-018 (orient/index), D-019 (activation unit), grill-me description fix (trigger-surface mismatch), Q-006 (verification signal), D-020 (enforcement principle).

## Close

**Outcome**: All seven design-level findings from the framework review have a settled direction, each either recorded as an entity or fixed directly.

**Verification result**: No formal Plan section (entry opened ad-hoc for a discussion phase); close criterion was every finding addressed with user sign-off per item. validate.py OK (26 entities); grill-me frontmatter parse-checked after the description rewrite.

**Keepers (finalized)**:
- D-017, D-018, D-019, D-020, Q-006 — the decision/question records themselves.
- grill-me description rewrite (skip conditions lifted into the persistent trigger surface).

**Throwaways (deleted)**:
- None.

**Spawned entities**:
- D-017 (decisions stay ADR events; standing rules promote into PROJECT.md constitution)
- D-018 (orient scans frontmatter; _index.md demoted to deterministic human-only view)
- D-019 (using-atlas re-injects per context window; resume only re-orients)
- D-020 (mechanical affordances over prose constraints; first applications: open.py project auto-derive, narrowed frontmatter ban)
- Q-006 (does verification-result carry signal — observe during dogfood week)

Implementation of D-017/D-018/D-019/D-020 is deliberately deferred to a follow-up work unit (orient/index/hook/PROJECT.md rework plus the two D-020 applications), to be planned via grill-me.
