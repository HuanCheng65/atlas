---
name: using-atlas
description: Auto-loaded at the start of every conversation on an atlas-enabled project (CLAUDE.md mentions docs/atlas/). Invoke this skill IMMEDIATELY at session start, BEFORE responding to the user's first message. Sets up atlas framework context, runs atlas-orient to load project state, and primes you to bootstrap a journal entry when work intent becomes clear. This is the SINGLE entry point to atlas — do not skip it, do not duplicate it. If skipped, all downstream atlas operations lose their starting context.
---

# Using Atlas

You are working on a project that uses atlas (operational memory framework at `docs/atlas/`). This skill is the framing layer: it sets up framework awareness, triggers state loading, and decides when to open a journal entry for the work this conversation is about to do.

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

**Action:** create `docs/atlas/journal/YYYY-MM-DD-<slug>.md` with this skeleton:

```yaml
---
date: 2026-05-27
slug: <slug>
project: <inferred from PROJECT.md or cwd>
tags: []
status: active
opened: 2026-05-27 14:00
closed: null
verification-result: null
related: []
---
```

Body:

```markdown
# <Title from intent>

## Context
<one paragraph: what this work is about, based on opening messages>

## Work log
```

**If you deferred for several exchanges before bootstrapping**, also include in the Context section a paragraph labeled `(retroactive — from earlier in this conversation)` capturing the relevant signals you observed while watching. Do not lose that context — failing to backfill means the journal entry pretends the conversation started fresh, which is false.

Skip the full Plan sections (Decisions resolved / Steps / Verification / Keepers / Throwaways). Those come from `grill-me` if the user wants formal planning, OR emerge later if work turns substantial.

Announce in one line:

> (opened journal/2026-05-27-<slug>.md to track this work)

User may immediately override ("call it Y" / "I'm not doing that") — rename or delete the file. Zero friction by design.

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
- **DO NOT** ask "should I open a journal entry?" before bootstrapping. Bootstrap silently when criteria met, announce after.
- **DO NOT** bootstrap an entry for queries, read-only requests, or greetings.
- **DO NOT** re-invoke using-atlas mid-session. Once per session. If context drifts, re-invoke `atlas-orient` to refresh state.
- **DO NOT** quote orient's output back to the user. Use it as your internal context.
- **DO NOT** create journal entries from a conversation that's just discussion / exploration. Wait for concrete work intent.

## Cross-references

- `atlas-orient` — load project state (on demand)
- `grill-me` — turn task description into a Plan, written into the active entry
- `atlas-log` — append to / close active journal entries
- `atlas-entity` — create D / E / Q
- `atlas-bootstrap` — onboard existing project (once per project)
- `atlas-compact` — periodic derivation (planned)