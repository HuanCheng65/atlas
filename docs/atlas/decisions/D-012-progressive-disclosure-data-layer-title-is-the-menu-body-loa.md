---
id: D-012
title: "Progressive-disclosure data layer: title is the menu, body loads on demand"
date: 2026-05-28
status: active
tags: [data-model, skills, orient, design-principle]
related: [D-001, D-005, D-009]
source-journal: 2026-05-28-formalize-progressive-disclosure-conventions.md
supersedes: []
superseded-by: []
affects: [atlas-entity, atlas-log, atlas-orient, using-atlas, grill-me]
---

# Progressive-disclosure data layer: title is the menu, body loads on demand

## Context

Atlas's data layer (D / Q / E entities, journal entries, ROADMAP) has the same structural shape as Claude Code's skill system:

| Skill design | Atlas design |
|---|---|
| `description` field is short, scannable, drives dispatch | Entity / journal *title* drives orient decisions |
| `SKILL.md` body loaded only when skill is invoked | Entity / journal *body* read only when title signals relevance |
| One skill per cognitive domain (D-009) | One file per work unit (D-005) / one entity per decision |
| Skills cross-reference each other rather than inline | Entities `related: [...]`, journals `source-journal: ...` |
| `name` field is the slug; `description` is the menu copy | Filename slug is the identifier; title is the menu copy |

The user surfaced this parallel while asking whether decision titles and journal slugs needed naming principles. The answer is yes — and the reason traces to a deeper principle worth naming explicitly, because it'll guide every future addition (new entity type, new index layer, new skill, new template).

## Decision

Atlas is **progressive disclosure for project state**: the agent's working context should hold a small, scannable menu by default, and pull entity bodies on demand only when the menu signal warrants it.

Three concrete commitments:

1. **The title is the menu signal.** Anyone reading the orient summary should know from the title alone whether to fetch the body. If you need the body to know what was decided / what work happened, the title failed.
2. **Bodies follow section conventions designed for partial retrieval.** Each section should be independently readable. The first sentence-level section (Decision for D, Plan for journal, the question itself for Q) is short enough to ship in the orient summary, not just the title.
3. **Cross-references over inlining.** When two entities relate, link via `related` / `source-journal`; don't duplicate content into the dependent file's body.

## Rationale

**Why progressive disclosure at all:** the agent has a finite context window and pays a cost (latency + cache rot + attention dilution) for every token loaded. Loading 12 decision bodies at session start to "have full context" defeats the framework's purpose — it just relocates the rot from chat to data. Compact menu + on-demand fetch is the same pattern that makes skills scale; the same logic applies to project state.

**Why title-as-menu is the load-bearing rule:** orient's summary is what the agent reads first and often only. If titles are vague ("Logging strategy", "Naming things"), the agent must either fetch every body (defeating the point) or guess (sometimes wrong). Specific titles ("Plain text + git as the data layer", "Translate framework vocabulary in chat") let the agent decide which bodies to pull without guessing.

**Why this is its own D and not just a section in `atlas-entity/SKILL.md`:** the principle spans atlas-entity (D/Q/E titles), atlas-log (journal slugs/titles), atlas-orient (what goes in the summary), using-atlas (which skills route based on intent), and any future skill that touches the data layer. A single source of truth lets future additions inherit it; embedding it in one skill would create drift.

## Consequences

**Positive:**
- Future skills inherit the principle by default; new entity types (if any) get a clear naming bar.
- Orient summary becomes a richer menu without becoming heavy (title + one line per entity).
- Naming drift is now a fixable problem with a clear standard, not a matter of taste.

**Negative:**
- Adds discipline burden when writing titles: the easy "topic-label" title is now wrong; you must phrase the *answer*.
- Requires templates to enforce the "Decision = one sentence" / "Plan headline = one sentence" convention, otherwise orient can't reliably extract.
- Risk of premature optimization toward retrieval tooling (an `extract.py --section X` script). The decision explicitly defers that until the convention itself proves insufficient.

## Alternatives considered

- **No principle, let titles drift**: rejected — current state already has uneven titles (D-002 "Skills user-level, data project-level via symlink install" reads compressed; D-011 v1 leaned topic-ish). Without a written rule, drift continues and orient becomes less useful over time.
- **Encode the principle per-skill**: rejected — atlas-entity and atlas-log would re-derive the same rule independently, with slow drift between them. Single source of truth is cheaper to maintain (same argument that drove D-011's single-source approach).
- **Build a section-extract tool now** (`extract.py D-007 --section Rationale`): deferred. The capability is approximated by Read offsets + Grep + heading patterns; build the tool when convention proves insufficient, not before. Aligns with D-001's "plain text, don't over-engineer the data layer".
- **Move toward structured data (YAML body, JSON facets)**: rejected — directly contradicts D-001. Plain markdown stays the data layer; structure comes from section conventions, not new formats.
