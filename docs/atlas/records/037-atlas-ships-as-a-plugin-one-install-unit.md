---
id: 37
title: Atlas ships as a Claude Code plugin; skills, hook and CLI install as one unit
date: 2026-09-02
type: decision
tags: [packaging, infrastructure, hooks]
---

# Atlas ships as a Claude Code plugin; skills, hook and CLI install as one unit

## Context

Installing atlas took three steps and only one of them was scripted.
`install.sh` symlinked the five skill directories into `~/.claude/skills/`;
`atlas-init` scaffolded `docs/atlas/` inside a project; and the SessionStart
hook that loads the store into context had to be written into
`~/.claude/settings.json` by hand. Nothing installed the hook and nothing
said it was missing, so on this machine it existed only because it was typed
in during a working session. It surfaced weeks later, by accident, when
someone read `atlas-init` expecting to find it there.

The hook was never `atlas-init`'s job. Init creates project-level data; the
hook is a machine-level registration; the two have different lifetimes and
re-running init in a second project would rewrite a global setting. The gap
was structural — no artifact owned machine-level setup as a whole.

## Decision

The repository is a Claude Code plugin: `.claude-plugin/plugin.json` at the
root, `hooks/hooks.json` carrying the SessionStart registration, with
`skills/` and `bin/` already in the positions the format expects. It installs
with one symlink, because any directory under `~/.claude/skills/` holding a
plugin manifest loads as `<name>@skills-dir` at personal scope — no
marketplace, no install step, no trust gate.

The scope split stands unchanged: skills are user-level and shared across
projects, data lives under `<project>/docs/atlas/` and travels with the repo.
Only the delivery mechanism is replaced (supersedes::
[[002-skills-user-level-data-project-level-via-symlink-install]]).

A marketplace is deliberately not part of this. Packaging and distribution
are separable and only packaging was needed.

## Rationale

- One artifact now owns everything machine-level. A component that no
  installer creates cannot be silently absent, which is the failure this
  fixes.
- `${CLAUDE_PLUGIN_ROOT}` is substituted inside SKILL.md bodies, so the
  `~/.claude/skills/...` paths hard-coded in every skill are gone. Each was a
  bet that the reader had installed atlas exactly where the author did.
- The symlink is kept rather than a copied install, because atlas is
  developed by being used. Skill bodies take effect immediately; only
  `hooks/` needs `/reload-plugins`.
- Skills are no longer separately installable, which is precisely what made
  sharing code between them a risk. The unit of distribution is the plugin,
  so a skill importing a sibling's library is structural rather than a bet on
  install layout (answers::
  [[017-cross-skill-code-duplication-threshold-and-consolidation-str]]).

## Consequences

- Skills are namespaced `atlas:<name>`. The CLAUDE.md pointer and the
  session-start reminder name `atlas:using-atlas` exactly.
- `bin/` joins the Bash tool's PATH while the plugin is enabled, so
  `atlas-init` runs unqualified and the PATH export is no longer needed.
- `install.sh` and `uninstall.sh` are deleted; one `ln -s` replaces both.
- An existing install must drop the five old skill symlinks and the
  hand-written SessionStart entries, or state loads twice per session.
- Skills-directory plugin loading is a recent Claude Code feature, so atlas
  now has a floor on the harness version.

## Alternatives considered

- Marketplace distribution — still out of scope. It adds a cached copy and an
  update step, which breaks the live-edit loop, and it answers a question
  about audience that nobody is asking.
- Teaching `atlas-init` to write the hook — rejected. A project-level command
  editing machine-level configuration inverts the ownership, and every later
  project would rewrite it.
