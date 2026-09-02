# Scan Checklist

`scan.py` covers what's automatable. This checklist covers what you must read manually before starting the interview.

## What scan.py gives you

- Git remote and recent commit history (last 50, plus decision-signal commits)
- Language breakdown by extension
- Top-level directory tree
- Existing documentation files (by filename)
- Other framework signals (Superpowers, GSD, ADR, ...)
- Prior plans / specs from other frameworks
- TODO / FIXME / XXX markers (up to 20)

## What you MUST read manually

After running scan.py and ingesting the YAML report, read these:

1. **README.md** — and READMEs of any subdirectory mentioned in scan. This gives you the user's own description of the project. Often contains stated goals and constraints.

2. **CHANGELOG.md if present** — chronological narrative of major changes. Often surfaces past decisions.

3. **Top 30 lines of each main package's entry file** — module docstrings or top-comment blocks usually state architectural choices.

4. **Existing CLAUDE.md / AGENTS.md / GEMINI.md if present** — signals the user has previously written rules for AI agents. Read what they wrote, plan to merge or replace.

5. **`docs/adr/` directory entries if present** — these ARE decisions in ADR format and likely worth carrying over with minimal change.

6. **A handful of plan / spec files from prior frameworks** — *skim* not deep-read. They reveal what the user has been working on. Most will NOT become records (they're task-level), but a few may surface architectural choices worth recording.

## What NOT to read

- Full source file bodies (read tops only)
- Test suites (low signal for project background)
- Generated docs / API references
- Anything inside ignored dirs (scan.py already excludes these)

## Self-check before Phase 2

You are ready for the interview when you can articulate, without re-reading:

- The project in one sentence
- 3-5 main themes of recent work (from commits)
- 2-3 candidate decisions you suspect (with evidence from scan + reads)
- Any obvious open questions or stale TODOs worth surfacing

If any of these is fuzzy, read more before starting the interview. Wasted Phase 1 minutes are saved Phase 2 minutes ×3.
