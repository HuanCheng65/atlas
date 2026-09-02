---
id: 36
title: Compact rewrites the memory set; eviction is the default
date: 2026-09-02
type: decision
tags: [atlas-compact, agent-behavior]
---

# Compact rewrites the memory set; eviction is the default

## Context

Memory records hold the constraints in force and their titles are loaded into
every session, so the set has a budget. Any budgeted store needs eviction, and
eviction that requires a decision per item does not happen — which is the
failure this whole redesign exists to remove.

The published work on offline consolidation for language agents takes a
different shape: a working region is selected, treated as read-only evidence,
and replaced by a re-synthesised set. What is not carried into the rewrite does
not survive. Deduplication and abstraction become structural rather than
optional, and no decision to delete is ever required.

A community implementation of the same idea keeps the opposite default —
demoting low-scoring entries to an archive rather than dropping them — and
scores by recency and reference count, both of which are computable here.

This (answers:: [[015-topic-auto-promotion-heuristic-for-atlas-compact]]): the
heuristic that never worked is replaced by a rewrite, so nothing needs
promoting.

## Decision

Compact has two jobs. The first is a rewrite of the memory set within its
budget: the agent writes the constraints that should be in force now, and what
is not restated stops being preloaded. The second is a review of the store for
records that quietly stopped being true, working from a shortlist a script
computes — questions with no answering edge and no citations, same-type records
sharing most of their link neighbourhood, records citing paths absent from the
repo, tags used once.

Neither job asks for per-item confirmation. The run lands as one commit, which
is the review point.

## Consequences

Eviction is cheap because it loses nothing: the experiment or decision that
established a constraint stays in the store, and only the always-loaded line
goes away. That is what makes a default of dropping safe.

The quality of each rewrite is unmeasured. The published version trains its
consolidator against task performance and a counterfactual-ablation signal;
there is no equivalent here, so the selection is the agent's judgment with no
feedback loop. This is the weakest part of the design and worth revisiting if
the memory set visibly degrades.

Reading the whole store is avoided by construction — the agent opens only what
the shortlist names, so a compact run's context stays small as the store grows.
