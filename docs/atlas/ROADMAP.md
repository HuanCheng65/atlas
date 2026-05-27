# Roadmap

> Short-term goals. For long-term goals see PROJECT.md.
>
> Scope is intentionally minimal — see D-010. Open questions live in
> Q-NNN; committed designs in D-NNN; finished work in closed journal
> entries + `git log`. This file holds only the current milestone.

## Current milestone

**Phase 2.5: ship atlas-compact + harden via sustained dogfood**

Phase 2's session-lifecycle work shipped under different names than
originally planned — `using-atlas` (session entry + intent watching),
`atlas-orient` (state load), `atlas-log` (journal lifecycle scripts) —
and `grill-me` shipped with the Verification / Keepers / Throwaways
convention as a hard output. Six skills now `ready` (see root README).
Remaining: `atlas-compact` and proving the design holds under sustained
real use.

Exit criteria:

- `atlas-compact` shipped with a first-pass topic-extraction heuristic
  (resolves Q-002).
- Echo uses atlas on the SLA project for one full week and reports
  design pressure points.
- Any drift, unclear conventions, or recurring agent failure modes
  surfaced during that week land as D-NNN or skill patches before the
  milestone closes.
