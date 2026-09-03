---
id: 43
title: Every check names the source of its verdict
date: 2026-09-03
type: decision
tags: [verification, workflow]
---

# Every check names the source of its verdict

A test written after the code, from the code, asserts what the code does rather
than what was required. It passes on the first run and never fails again. The
existing rule asked a plan to declare a verification approach without setting
any bar on it, which admits exactly this
([[006-verification-keepers-throwaways-instead-of-enforced-tdd]]), and the
Keeper/Throwaway split it introduced was a judgment with no criterion and no
default.

## Decision

Each check in a work unit's Spec names where its verdict comes from: a
reference implementation, a property or invariant, data whose answers are known
independently, a failure that actually happened, or values the user specified.
If the source is the code under test, that must be said — it is a
characterization test, correct when the subject is code being refactored and
the point is to detect change, misleading when read as a correctness check.
A check with no source named is decoration.

A Keeper fossilizes a specific failure that happened or an invariant stated
somewhere. Everything else is a Throwaway by default.

This (supersedes:: [[006-verification-keepers-throwaways-instead-of-enforced-tdd]]),
whose choice not to enforce TDD stands: verification form still varies by task,
and tests, a reference comparison, an eval set, a manual checklist and a
measured threshold all qualify.

## Rationale

Writing the test first is one way to keep the verdict's source independent of
the implementation, and prescribing it as the only way is what made strict TDD
a poor fit for research code. Naming the source is the property TDD was being
used to buy, stated directly, so it can be satisfied by any of the forms.

Giving Keeper a criterion rather than a judgment removes a decision that has to
be made per task and therefore gets skipped. "Which failure does this check
correspond to" has an answer or it does not.

## Consequences

- `grill-me` asks for the source alongside each check, and the earlier
  allowance that Keeper and Throwaway lists "may shift during work" is replaced
  by a default of Throwaway.
- The bar is stated in `using-atlas` as well, because checks get written during
  ordinary work without `grill-me` being invoked at all.
