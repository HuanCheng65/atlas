# Atlas

Operational memory for AI-assisted projects. A small, opinionated framework
of skills and data conventions that keep multi-session work coherent.

## What it provides

- A user-level **Claude Code skill** (`atlas-entity`) that maintains
  structured decisions, experiments, and open questions in `docs/atlas/`
- A per-project **data layout** under `docs/atlas/` with templates,
  validated frontmatter, and auto-generated indexes
- A small CLI (`atlas-init`) to bootstrap `docs/atlas/` in any project

See `docs/design.md` for the design notes.

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

## Update

```bash
cd ~/atlas
git pull
```

Symlinked skills update automatically — no reinstall needed.

## Requirements

- Python 3.8+ with `pyyaml` (for the scripts in `atlas-entity`)
- Claude Code (or any agent that reads `~/.claude/skills/`)
- Bash (for `install.sh` / `atlas-init`)

## Skills shipped

| Skill | Status |
|---|---|
| atlas-entity | ready — manages D/E/Q entities |
| atlas-session-start | TODO (phase 2) |
| atlas-session-end | TODO (phase 2) |
| atlas-compact | TODO (phase 2) |

## License

MIT