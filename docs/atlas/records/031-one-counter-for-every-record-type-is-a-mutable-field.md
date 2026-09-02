---
id: 31
title: One counter for every record; type is a mutable field
date: 2026-09-02
type: decision
tags: [data-model, entities, schema]
---

# One counter for every record; type is a mutable field

## Context

The store used three per-type counters and encoded the type in the identifier:
`D-007`, `E-021`, `Q-005`. The prefix is assigned when the record is created,
which is the moment of least information — in the dogfood store one decision
tagged `negative-result` reads as an experimental conclusion, and the coin flip
between the two was permanent because a thousand references depended on it.

This (supersedes:: [[004-three-entity-types-d-e-q-with-shared-base-frontmatter]]),
which established the three-type split and the shared base frontmatter.

## Decision

One monotonic counter across every type. A record is `NNN-slug.md` in a single
flat directory, and `type` is an ordinary frontmatter field that can be
corrected later without touching a single reference.

Four types: `memory`, `experiment`, `decision`, `question`. There is
deliberately no catch-all — a catch-all absorbs exactly the content that used
to accumulate in the journal's work log, renumbered.

Numbers are never reused. A retired number keeps old links meaningful.

## Consequences

Type becomes cheap to get wrong, which is the point: the agent no longer has to
classify correctly at creation time, and reclassification is a one-field edit.

A single counter also makes "links point backwards" expressible as an
assertion a script can check — `target < source` — which per-type counters
cannot express at all, since `D-004` and `E-042` have no order relation. The
principle in
[[030-a-record-s-truth-may-not-depend-on-a-future-edit]] would otherwise have
stayed prose.

The cost is that a reference no longer carries the type. In the old scheme
`related: [D-004, E-042]` told the agent what it was looking at without opening
anything. Under this scheme the sentence around the link supplies that context,
and generated views print the type. Migration had to rewrite every existing
reference, which was mechanical.
