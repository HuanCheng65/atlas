---
id: 12
title: Entity frontmatter holds machine summaries; the body owns the prose
date: 2026-07-28
type: decision
tags: [entities, schema, validate, experiments]
---

# Entity frontmatter holds machine summaries; the body owns the prose

## Context

A dogfood example from another project showed the experiment entity's failure mode. The template gave the same content two homes — frontmatter fields (`hypothesis` / `config` / `result` / `conclusion`) and same-named body sections — and validate only presence-checked the frontmatter keys, so the agent filled frontmatter with multi-paragraph prose (80% of the file), duplicated part of it in the body, and punted the body Conclusion with a one-line pointer back at the frontmatter field. Meanwhile the machine path never read those fields: orient extracts its headline from the body's Hypothesis section. schemas.md had said "One-sentence claim / One-sentence verdict" all along — a prose rule nobody enforced.

## Decision

Every entity content field in frontmatter is a one-line machine summary — for experiments, string values in `hypothesis` / `config` / `result` / `conclusion` are capped at 300 characters by validate — while the body sections own the canonical full prose, and a body that points the reader back at frontmatter instead of stating its content is a validate error.

## Rationale

- Each piece of content needs exactly one owner; a dual-slot schema forces the agent to choose between duplication (which drifts) and pointers (which hollow out the body).
- Frontmatter is the scan surface — read in bulk without loading bodies — so it must stay short; kilobytes of hand-written YAML holding markdown prose is both a scan tax and an escaping hazard.
- Per the existing enforcement principle, the one-sentence rule already existed as prose and decayed; a length cap in validate makes the correct shape the only shape that passes.

## Consequences

- Existing over-stuffed experiment records (e.g. the one that surfaced this) fail validate until their prose moves into the body and frontmatter shrinks to summaries.
- "Scan all conclusions without loading bodies" stays cheap and honest: the frontmatter summary is guaranteed short, and the body is guaranteed complete.
- Template comments now state the constraint per field; the pointer ban applies to all entity types, not just experiments.

## Alternatives considered

- **Drop the four content fields from frontmatter entirely** (orient already extracts body first-sentences) — rejected: loses the ability to grep/scan structured conclusions and key numbers across experiments without opening bodies.
- **Let frontmatter hold the full prose and treat the body as optional rendering** — rejected: prose in hand-written YAML is fragile, the scan surface bloats, and the on-demand-readable document becomes the incomplete copy.
