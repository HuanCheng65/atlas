---
name: using-atlas
description: Auto-loaded at the start of every conversation on an atlas-enabled project (CLAUDE.md mentions docs/atlas/). Invoke this skill IMMEDIATELY at session start, BEFORE responding to the user's first message. Sets up atlas framework context, runs atlas-orient to load project state, and primes you to bootstrap a journal entry when work intent becomes clear. This is the SINGLE entry point to atlas — do not skip it, do not duplicate it. If skipped, all downstream atlas operations lose their starting context.
---

# Using Atlas

You are working on a project that uses atlas (operational memory framework at `docs/atlas/`). This skill is the framing layer: it sets up framework awareness, triggers state loading, and decides when to open a journal entry for the work this conversation is about to do.

## Speak in plain project language (foundational rule)

Atlas is operational memory **for you, the agent**. The user wants the *effect* — continuity, conflict-detection, decision recall — without being asked to context-switch into "the framework". Surfacing framework artifacts in conversation makes them feel like they're managing two things instead of one.

Two layers of communication exist; keep them distinct.

### Layer 1: Substantive conversation (the meat of the discussion)

When discussing the actual work, **translate framework vocabulary into plain project language**. The user is thinking about the work, not the data layer — don't make them context-switch.

- **Conflicts**: describe the *content* of the prior decision, not its ID.
  - Bad: "this conflicts with D-007."
  - Good: "this conflicts with what we settled earlier — skill activation is event-driven, not session-phase-driven."
- **Past work**: refer to *what was done*, not the journal file as a reference.
  - Bad: "as we worked out in `journal/2026-05-27-cuda-graphs.md`"
  - Good: "from the CUDA graphs work last week"
- **Open questions / experiments**: same — describe the question / experiment, don't say "Q-003" or "E-005".

### Layer 2: Operational announces (one-line, parenthetical, post-hoc)

When you open a journal, append a log, write a Plan, or close work, a brief one-line announce is appropriate. **File paths are fine and useful here** — the journal is plain text + git (D-001), so the file *is* the durable record the user can later open, `git log`, or edit. The path is a pointer, not framework noise.

What to drop is the **modifier verbiage** that describes the framework rather than the data:

- Good: `(opened docs/atlas/journal/2026-05-27-cuda-graphs.md)`
- Good: `(logged: P99 30.9 → 27.4ms, target hit)` — content-only also fine
- Good: `(closed — verification passed)`
- Bad: `(opened journal/2026-...md to track this work — this is a new active journal entry)` — extra framework descriptor verbiage
- Bad: `(appended to the active journal entry: …)` — "active journal entry" is framework abstraction

A rough rule: file paths and short content descriptions are fine; phrases like "active entry", "this journal entry", "to track this work", "I'll keep a log" that *describe the framework operation* in English are what to strip.

### Exceptions — name framework artifacts directly when:

- The user explicitly asks to see / list / audit / edit decisions / questions / journal items — name them; that's what they asked for.
- The user is working *on* atlas itself (editing skill files, entity templates, journal scripts in this repo) — atlas is the subject matter.
- During `atlas-bootstrap` — that's when the user is being introduced to the framework.

Internal instructions in this and other atlas skills continue to use precise framework vocabulary — that's for *you*, not for repetition back to the user.

## At session start (REQUIRED)

These three steps happen **before** you respond to the user's first message.

1. **Run atlas-orient.** Invoke the `atlas-orient` skill once, silently. It returns a markdown summary of current project state — read it fully, bind to it internally. Do NOT quote it back to the user.

2. **Enter watching mode.** Hold an internal "intent buffer" while reading the user's first substantive message. Do not yet bootstrap any journal entry; do not yet invoke other atlas skills. Just watch.

3. **Decide what to do** as soon as intent is clear (often on first message; occasionally requires 2-3 exchanges). See "Watching for work intent" below.

If `docs/atlas/` does not exist, atlas is not actually installed here — abort this skill and proceed normally without atlas. You may suggest the user run `atlas-init` if they appear to want atlas.

## Watching for work intent

Once you have enough signal from the user's opening messages, choose ONE of three:

### A. Bind to an existing active entry

**When:**
- User explicitly references an existing journal entry (slug, file path, `@journal/...`, or topic name)
- User's message clearly continues the work of exactly one existing active entry

**Action:** hold that slug in conversation memory. Subsequent `atlas-log` calls append to it. Do NOT create a new entry.

If multiple active entries plausibly match, ask the user once which one this conversation relates to, then bind.

### B. Bootstrap a new active entry

**When ALL three hold:**
- Message implies work that will produce concrete artifacts (code edits, decisions, document changes, experiment runs)
- You can extract a kebab-case slug candidate from the message's topic
- No existing active entry is a plausible continuation

**Action:** call `atlas-log`'s `open.py` script, piping the Context paragraph(s) via stdin:

```bash
python3 ~/.claude/skills/atlas-log/scripts/open.py \
    --slug <kebab-case-slug> \
    --project <project name from PROJECT.md> \
    --tags <comma,separated,tags> <<'EOF'
<one paragraph: what this work is about, based on opening messages>
EOF
```

Optional flags: `--related slug1,D-007` to link to existing entries / entities, `--title "Override default title"` if the slug-derived title is awkward.

The script generates the date prefix, `opened` timestamp, and full frontmatter scaffolding. **Never write timestamps by hand.** If you find yourself wanting to use Write to create the entry directly, stop — use `open.py`. The scripts exist because hand-written timestamps caused real bugs.

**If you deferred for several exchanges before bootstrapping**, the Context paragraph piped to stdin should include a sentence labeled `(retroactive — from earlier in this conversation)` capturing the signals you observed while watching. Do not lose that context — failing to backfill means the journal entry pretends the conversation started fresh, which is false.

Skip the full Plan sections (Decisions resolved / Steps / Verification / Keepers / Throwaways). Those come from `grill-me` if the user wants formal planning, OR emerge later if work turns substantial.

`open.py` prints the path of the created file on stdout. Hold the slug in conversation memory. **Announce briefly** — the path is fine; drop framework-descriptor verbiage:

> (opened docs/atlas/journal/2026-05-27-<slug>.md)

If the user is mid-flow on substantive work, the announce can be skipped entirely. See "Speak in plain project language" above for the principle.

User may immediately override ("call it Y" / "I'm not doing that") — delete the file via `rm` (no scripted "rename" yet; safe to just delete and re-run `open.py` if needed).

### C. Defer

**When:**
- Message is a pure query about project state ("what were we working on?")
- Message is read-only ("show me X" / "explain Y")
- Message is too vague to extract slug ("let's do something today")
- Message is greeting or off-topic ("hi" / "你在吗")

**Action:** don't bootstrap. Respond normally. Keep watching subsequent messages. Bootstrap when criteria for (B) are met.

If you've deferred for 3+ substantive exchanges and intent is still unclear, ask the user once what they're trying to do today, then decide.

## Routing to other skills

After intent is determined, subsequent agent actions route to the right skill:

| User signal | Skill to invoke |
|---|---|
| Wants planning on a non-trivial new task | `grill-me` — writes Plan into the active entry that using-atlas already opened |
| Asks "what were we working on" or context seems stale mid-session | `atlas-orient` — re-load state |
| Completes a unit of work, makes edits, runs experiments | `atlas-log` — appends as events happen |
| Decides something architectural | `atlas-entity` creates D-NNN; `atlas-log` appends a journal note |
| Surfaces a question or runs an experiment | `atlas-entity` creates Q-NNN / E-NNN |
| Onboarding existing project to atlas | `atlas-bootstrap` — rare, once per project |
| Periodic / milestone review | `atlas-compact` — planned |

## Anti-patterns

- **DO NOT** skip session-start setup. Always run atlas-orient first.
- **DO NOT** ask "should I open a journal entry?" before bootstrapping. Bootstrap silently when criteria met, announce after (in plain language — see top of this skill).
- **DO NOT** bootstrap an entry for queries, read-only requests, or greetings.
- **DO NOT** re-invoke using-atlas mid-session. Once per session. If context drifts, re-invoke `atlas-orient` to refresh state.
- **DO NOT** quote orient's output back to the user. Use it as your internal context.
- **DO NOT** create journal entries from a conversation that's just discussion / exploration. Wait for concrete work intent.
- **DO NOT** drag framework artifacts into *substantive* discussion — no `D-NNN`, `Q-NNN`, `E-NNN`, or journal filenames as references. Translate to content-level language. Operational one-line announces with file paths are a separate layer and *are* allowed. See "Speak in plain project language" above.

## Cross-references

- `atlas-orient` — load project state (on demand)
- `grill-me` — turn task description into a Plan, written into the active entry
- `atlas-log` — append to / close active journal entries
- `atlas-entity` — create D / E / Q
- `atlas-bootstrap` — onboard existing project (once per project)
- `atlas-compact` — periodic derivation (planned)