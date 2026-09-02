---
id: 2
title: Skills user-level, data project-level via symlink install
date: 2026-05-27
type: decision
tags: [packaging, infrastructure]
---

# Skills user-level, data project-level via symlink install

## Context

Skills (capability) and atlas data (state) have different scopes. Skills are
generic and should be reusable across projects; data is project-specific and
must live with the code it describes. We needed to decide where each lives and
how skills get installed.

## Decision

Skills install once at user level (`~/.claude/skills/`) via the repo's
`install.sh`, which symlinks every directory under `skills/` into the user's
Claude Code skill directory. Per-project atlas data lives under
`<project>/docs/atlas/`, created by `atlas-init`.

## Rationale

- One install, many projects — no per-repo skill copy to keep in sync.
- Symlinks update automatically on `git pull`; no reinstall step.
- Data stays in the project repo, so every git checkout carries its own state.
- A plugin marketplace is overkill for a personal tool; dotfiles + symlink is simpler.

## Consequences

- Updating atlas == pulling the atlas repo. Skills stay current everywhere automatically.
- Projects can be archived self-contained because their atlas state travels with them.
- Cross-project upgrades to skill behavior land everywhere at once; need to be backward-compatible with existing per-project data.

## Alternatives considered

- Plugin marketplace distribution — deferred; overkill for a personal tool.
- Copying skills into each project — rejected; sync drift across projects.

Evidence: `docs/design.md` Architecture diagram + "Plugin marketplace distribution" bullet; `README.md` Install section; `PROJECT.md` Hard constraints.
