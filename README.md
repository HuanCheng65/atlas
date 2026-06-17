# Atlas

Operational memory for AI-assisted projects. A small, opinionated framework
of skills and data conventions that keep multi-session work coherent.

## What it provides

A user-level set of **Claude Code skills** that route an agent through the
lifecycle of a project's operational memory, plus a per-project **data
layout** under `docs/atlas/` with templates, validated frontmatter, and
auto-generated indexes.

- **using-atlas** — session-start entry point; loads project state, watches
  for work intent, opens a journal entry when concrete work begins
- **atlas-orient** — loads current state (decisions, open questions,
  active and recent work) into the agent's context; produces a compact
  navigator summary
- **atlas-log** — maintains the journal under `docs/atlas/journal/` via
  open / append / close scripts (all timestamps from `datetime.now()`, never
  agent-fabricated)
- **atlas-entity** — manages structured decisions (D-NNN), experiments
  (E-NNN), and open questions (Q-NNN)
- **grill-me** — interview-driven planning before non-trivial work; produces
  a Plan with mandatory verification criteria
- **atlas-bootstrap** — one-time onboarding for an existing project
  (combines a deterministic scan with a 4-round interview)

Plus a small CLI (`atlas-init`) to scaffold `docs/atlas/` in any project.

See `docs/design.md` for design notes and `docs/atlas/decisions/_index.md`
for the framework's own decision log.

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
| using-atlas | ready — session entry point, watches for work intent, routes |
| atlas-orient | ready — loads project state into agent context |
| atlas-log | ready — journal lifecycle (open / append / close) |
| atlas-entity | ready — D / E / Q lifecycle, validation, reindex |
| grill-me | ready — interview-driven planning with verification criteria |
| atlas-bootstrap | ready — one-time onboarding for existing projects |
| atlas-compact | ready — periodic maintenance: clears backlog (stale entries, untriaged decisions, aging questions), consolidates records (merges, topic distillation), one revertable commit per run |

## License

MIT
