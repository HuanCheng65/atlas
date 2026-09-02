---
id: 38
title: Record identifiers stay inside the store; leaked ones are resolved, not rewritten
date: 2026-09-03
type: decision
tags: [data-model, packaging]
---

# Record identifiers stay inside the store; leaked ones are resolved, not rewritten

## Context

Preparing the v1 migration for a project that had run on atlas for months, a
count of old-format identifiers outside `docs/atlas/` came back in the
hundreds: forty in the paper narrative, twenty in a design assessment,
seventeen in an experiment result file, thirteen in a shell script — one of
them baked into the script's own filename. A second copy of the whole store
sat in a git worktree the migration would never see.

The first instinct was a tool that finds these and converts them to
wikilinks. That instinct is wrong twice over. It would edit documents the
store does not own, and it treats the symptom: the identifiers should not
have been there. The store already forbids citing record numbers in
conversation and in distributed skill bodies
([[025-distributed-skill-bodies-cite-reasoning-inline-never-this-pr]]), for
the same reason in both places — the number means nothing to the reader. The
project's own prose was never covered, and that is where the largest leak
happened.

The leak also silently voided a guarantee. The store promises numbers are
never reused so an old link keeps its meaning, yet migration renumbers every
record ([[031-one-counter-for-every-record-type-is-a-mutable-field]]). That
is survivable only while references live inside the store, where the
migration rewrites them in the same pass.

## Decision

Identifiers are internal to the store. They may appear inside `docs/atlas/`
and in PROJECT.md, whose constitution links records by design; anywhere else
the project writes in content language.

References that already leaked stay exactly as they are. They are prose, not
links, and a document that read correctly when it was written keeps reading
correctly. The migration writes `docs/atlas/archive/v1-id-map.tsv` — old
identifier, new record stem, title — and keeps it permanently, so
`grep '^E-047'` answers what a stale reference meant without opening
anything. The session-start payload names the map only on stores that have
one.

## Consequences

- The migration's write scope is the store plus PROJECT.md, and stays there.
- The archived journal, which keeps its old identifiers verbatim, becomes
  readable rather than merely grep-able.
- A prohibition with no check will be violated, so the leak needs detecting
  where the store is already scanned rather than restating in prose.
- Every project migrated from v1 carries one more permanent file. It is a
  few kilobytes and it is inside the boundary.

## Alternatives considered

- Converting external references to wikilinks — rejected. Correct for a
  design document, wrong for an archived one, and actively destructive for a
  script whose filename carries the identifier as a name rather than a
  reference. No rule separates the three without reading each case, which
  makes it agent work on a few hundred sites for no gain.
- Preserving the old numbers through the migration so nothing needs
  resolving — rejected. It would keep the type prefix as identity, which is
  the thing the renumbering exists to remove.
