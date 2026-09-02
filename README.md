# Atlas

Operational memory for AI-assisted projects. A small, opinionated framework
of skills and data conventions that keep multi-session work coherent.

## What it provides

A per-project **record store** under `docs/atlas/`, a session-start hook that
loads its current state directly into the agent's context, and a small set of
**Claude Code skills** for writing to it.

Every record is one numbered file. Frontmatter carries identity; the body
carries the prose and every relation, written as Obsidian wikilinks in the
sentences that explain them. Nothing stores state that a later record can
determine: superseded, refuted and answered are computed from the link graph,
so no record has to be revisited to stay true.

- **using-atlas** — always loaded; what earns a record, when to write one, and
  how relations are expressed
- **atlas-entity** — store operations: validate, reindex, create, rename, and
  the one-time migration from the old D/E/Q layout
- **grill-me** — interview-driven planning before non-trivial work; produces a
  plan with mandatory verification criteria
- **atlas-compact** — periodic maintenance in two jobs: rewriting the memory
  set within its budget, and reviewing script-computed staleness candidates
- **atlas-bootstrap** — one-time onboarding for an existing project (a
  deterministic scan plus a 4-round interview)

Plus a small CLI (`atlas-init`) to scaffold `docs/atlas/` in any project.

See `docs/design.md` for design notes and `docs/atlas/records/_index.md` for
the framework's own store.

## Install (one-time, per machine)

```bash
git clone https://github.com/HuanCheng65/atlas.git ~/atlas
cd ~/atlas
./scripts/install.sh
```

This symlinks every directory under `skills/` into `~/.claude/skills/`.
Claude Code will pick them up at the next session start.

To uninstall:

```bash
~/atlas/scripts/uninstall.sh
```

## Initialize in a project

```bash
cd ~/my-project
~/atlas/scripts/atlas-init.sh
```

Or after adding `~/atlas/bin` to your `$PATH`:

```bash
atlas-init
```

The init script scaffolds `docs/atlas/` and adds a short "this project uses
atlas" pointer to `CLAUDE.md`, which routes the agent through `using-atlas`
at session start.

## Update

```bash
cd ~/atlas
git pull
```

Symlinked skills update automatically — no reinstall needed.

## Requirements

- Python 3.8+ with `pyyaml` (for the scripts under `skills/*/scripts/`)
- Claude Code (or any agent that reads `~/.claude/skills/`)
- Bash (for `install.sh` / `atlas-init`)

## Skills shipped

| Skill | Status |
|---|---|
| using-atlas | ready — always loaded; record-writing rules and triggers |
| atlas-entity | ready — validate, reindex, create, rename, migrate |
| grill-me | ready — interview-driven planning with verification criteria |
| atlas-bootstrap | ready — one-time onboarding for existing projects |
| atlas-compact | ready — memory consolidation and store review, one revertable commit per run |

## License

MIT
