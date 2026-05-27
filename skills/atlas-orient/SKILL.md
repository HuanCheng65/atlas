---
name: atlas-orient
description: Load the current atlas state into your context. Invoked by `using-atlas` at session start to load initial context. Also use WHEN the user says "what were we working on", "where did we leave off", "what's the state of X"; when context seems stale mid-session; or when switching to a different project (different cwd). Reads PROJECT.md, roadmap, active D / Q / E indexes, active and recent journal entries; produces a navigator summary. Lightweight and idempotent — safe to re-invoke any time.
---

# Atlas Orient

You load the current state of an atlas-enabled project into your conversation context. This is the **first** skill to use when starting a session on a project where atlas is installed.

## When to use

- Invoked by `using-atlas` at session start to load initial state (canonical path)
- User says: "what were we working on?", "where did we leave off?", "what's the state of X?", "remind me about Y"
- Switching to a different project mid-conversation (different cwd)
- After a long pause in conversation, before resuming substantive work
- Context seems stale or you (agent) feel lost about which active entry is in flight

Trigger frequency: typically once per session via using-atlas, plus on-demand re-loads when needed. Re-invoking is cheap.

## When NOT to use

- Project has no `docs/atlas/` directory — atlas not installed here, skip
- Within the same continuous work session, you already loaded context — don't re-orient every message
- User is asking a one-off question unrelated to the project's atlas state

## How to use

Run the orient script from project root:

```bash
python ~/.claude/skills/atlas-orient/scripts/orient.py
```

The output is a short markdown summary. **Read it completely**. It is intentionally compact — each section is either a few bullets or points you at a source file with full detail.

What the summary contains:

- Project name, stage, background headline, glossary size
- Current milestone (one paragraph) — roadmap intentionally holds only this section
- Active D-NNN list (titles only — usually < 20, can fit in full)
- Open Q-NNN list
- Active journal entries (work currently in flight; may be > 1 if parallel work)
- Recent closed journal entries (last 14 days, table)

## After orient: what to do

1. **Take stock silently.** Bind to current state internally.
2. **Check for conflicts.** If the user has stated a goal in this conversation, compare against active decisions (does the goal contradict one?), open questions (already raised?), active journal entries (continuation or new thread?). Surface any conflicts to the user **in plain project language** — describe the prior decision's *content*, not its `D-NNN` ID; refer to past work by *what was done*, not the journal filename. See `using-atlas`'s "Speak in plain project language" for the principle and examples.
3. **Do not re-quote the summary back.** Use it as your internal context.

Note: identifying which active journal entry to bind to for new work is `using-atlas`'s job at session start. If orient is invoked mid-session and you find yourself unsure which entry is in flight, ask the user (in plain terms — e.g. "are we continuing the X work, or starting something new?", not "which active journal entry should I bind to?").

## Anti-patterns

- **DO NOT** orient on every message. Once per session is enough.
- **DO NOT** read every source file referenced in the summary up-front. The summary is the navigator — go to detail only when needed.
- **DO NOT** ignore conflicts the orient surfaces. If the user's stated goal contradicts an active decision, raise it directly — but in plain language (describe the decision's content), not by naming the `D-NNN` ID. See `using-atlas`'s foundational rule.
- **DO NOT** orient on projects without `docs/atlas/`. There is nothing to load.
- **DO NOT** dump the entire summary back into chat. It's for *you*, not the user.

## Cross-references

- After orient, if user starts new substantial work → use `grill-me` (which creates the new active journal entry)
- After orient, if user continues in-flight work → use `atlas-log` to append to the active entry
- If orient surfaces a stale active entry (>3 days no update, work appears done), propose closing it via `atlas-log`
- If orient surfaces a conflict between user goal and active D-NNN, do not silently override; the user must decide whether to supersede via `atlas-entity`
