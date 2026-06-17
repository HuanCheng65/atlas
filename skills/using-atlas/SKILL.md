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

### Layer 2: Framework operations — silent by default

Opening, appending, closing, reindexing: bookkeeping. **Do it silently — no "(opened …)", "(logged: …)", "(closed — passed)" lines.** The record reaches the user through the work unit's commit (see "Atlas changes ride work commits" below), a better audit channel than transient chat lines. If something just logged matters to the user right now — a result, a conclusion — say it in your normal reply *as work content*, unwrapped.

The framework speaks **only when it needs the user**:

- **Entity confirmation** — proposing a D / Q / E before creating it (batched at natural seams; see the trigger table)
- **Plan review** — a Plan is ready; the user must see where it lives and sign off
- **Binding ambiguity** — "are we continuing the X work, or starting something new?"
- **Conflict alert** — the user's stated goal contradicts a Working rule or active decision. This one is immediate, never batched: it is the framework's first-order reason to exist.

When the framework does speak, file paths are fine — the journal is plain text + git, so the path is a pointer the user can open. What stays banned is framework-descriptor verbiage ("active journal entry", "to track this work", "I'll keep a log") wrapped around it.

### Exceptions — name framework artifacts directly when:

- The user explicitly asks to see / list / audit / edit decisions / questions / journal items — name them; that's what they asked for.
- The user is working *on* atlas itself (editing skill files, entity templates, journal scripts in this repo) — atlas is the subject matter.
- During `atlas-bootstrap` — that's when the user is being introduced to the framework.

Internal instructions in this and other atlas skills continue to use precise framework vocabulary — that's for *you*, not for repetition back to the user.

## At session start (REQUIRED)

These three steps happen **before** you respond to the user's first message.

1. **Run atlas-orient.** Invoke the `atlas-orient` skill once. The `Skill(atlas-orient)` call must be your first action after using-atlas loads — no narration around it, no "I'll first orient…", no "let me load state". It returns a markdown summary of current project state — read it fully, bind to it internally. Do NOT quote it back to the user.

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
    --tags <comma,separated,tags> <<'EOF'
<one paragraph: what this work is about, based on opening messages>
EOF
```

The project name is derived from PROJECT.md's H1; pass `--project` only to override. Optional flags: `--related slug1,D-007` to link to existing entries / entities, `--title "Override default title"` if the slug-derived title is awkward.

The script generates the date prefix, `opened` timestamp, and full frontmatter scaffolding. **Never write timestamps by hand.** If you find yourself wanting to use Write to create the entry directly, stop — use `open.py`. The scripts exist because hand-written timestamps caused real bugs.

**If you deferred for several exchanges before bootstrapping**, the Context paragraph piped to stdin should include a sentence labeled `(retroactive — from earlier in this conversation)` capturing the signals you observed while watching. Do not lose that context — failing to backfill means the journal entry pretends the conversation started fresh, which is false.

Skip the full Plan sections (Decisions resolved / Steps / Verification / Keepers / Throwaways). Those come from `grill-me` if the user wants formal planning, OR emerge later if work turns substantial.

`open.py` prints the path of the created file on stdout. Hold the slug in conversation memory. **Do not announce** — the entry is bookkeeping and travels with the work's commits; the user encounters it at the next speak-moment (plan review) or in the commit diff. See "Speak in plain project language" above.

If the user later objects to the entry (wrong slug, wrong work), delete the file via `rm` and re-run `open.py` (no scripted "rename" yet).

### C. Defer

**When:**
- Message is a pure query about project state ("what were we working on?")
- Message is read-only ("show me X" / "explain Y")
- Message is too vague to extract slug ("let's do something today")
- Message is greeting or off-topic ("hi" / "你在吗")

**Action:** don't bootstrap. Respond normally. Keep watching subsequent messages. Bootstrap when criteria for (B) are met.

If you've deferred for 3+ substantive exchanges and intent is still unclear, ask the user once what they're trying to do today, then decide.

## Triggers the agent watches for (load-bearing)

This section exists because trigger conditions hidden inside other skills' bodies don't fire — the agent only loads those bodies *after* deciding to invoke them, so the trigger that should drive invocation is invisible at the moment that matters. The cross-skill triggers live **here**, in using-atlas, which is loaded at session start and stays in context the whole session.

**You are responsible for recognizing these moments as they happen.** Do not wait for the user to label them — they usually won't, because they're thinking about the work, not the framework. **Recognition is immediate; proposing is batched**: hold recognized D/Q/E candidates in a session buffer and propose them at the next natural seam — work wrap-up, before a close, a user pause — instead of interrupting mid-flow. The one exception is a conflict with a Working rule or active decision: surface that immediately.

| Agent-recognized moment | Action |
|---|---|
| A long-term architectural / framework / strategic choice gets settled in conversation — *even if no one called it a decision*, even if it emerged from back-and-forth refinement rather than an explicit "let's decide X" | Propose recording as D-NNN via `atlas-entity` (at the next seam). Default to proposing; only skip if you can articulate why it fails the D criteria (not long-term, no alternatives considered, won't be referenced) |
| An unresolved question surfaces that won't be answered in this session | Propose Q-NNN via `atlas-entity` (at the next seam) |
| A measurement / experiment produces a result that might be cited later | Propose E-NNN via `atlas-entity` (at the next seam) |
| You completed a substantive unit of work | Append via `atlas-log` — silently, no pre-confirmation, no announce |
| Work is wrapping up | The canonical seam: flush the candidate buffer — "did this work establish a long-term choice or surface an open question?" Propose D / Q before closing |

**Failure mode to prevent:** "the user didn't ask me to record this, so I'll skip it." If you catch yourself thinking that about something that meets the D/Q/E criteria above, the trigger fired — propose it (at the seam). Batching changes *when* you propose, never *whether*.

**Is it a D, or just a journal note?** The distinction people get wrong: a decision is a *constraint on future choices*, not *important work*. A big refactor is journal; the "from now on this layer uses pattern X" the refactor established is the decision. Quick test — *"Three months from now, building something related, will I need to dig up this rationale to know how to proceed?"* Yes → propose D. No → it stays in the journal. Two signals that push toward D: the choice is expensive to reverse, and it had real alternatives that were weighed and rejected (a single forced path is a method, not a decision). This heuristic lives here, in the persistently-loaded surface, on purpose — you make this call *before* invoking `atlas-entity`, and a skill's body only loads *after* you invoke it, so the criteria can't live there. atlas-entity's body holds the fuller checklist as a backstop.

The skill-specific *operational* details (which script to call, what frontmatter to fill, when to ask for confirmation on the action itself) live in each skill's body. Only the **recognition** lives here.

## Atlas changes ride work commits

Atlas data changes (journal entries, entities, indexes, PROJECT.md edits) are part of the work unit they describe. When committing, stage them **with the work's own commits** — never as standalone "update atlas docs" commits. An atlas-only commit is legitimate only when atlas content is itself the work (a design discussion whose product is decision records, a bootstrap, a compact run), and its message names the content ("settle decision positioning: ADR log + constitution split"), never the framework ("update atlas docs"). The commit doubles as the transparency channel: the user reviews the work diff and sees its record riding along — that is what replaced chat announces.

## Routing (reactive — when the user names the action)

When the user explicitly names what they want, route accordingly:

| User signal | Skill to invoke |
|---|---|
| Wants planning on a non-trivial new task | `grill-me` — writes Plan into the active entry that using-atlas already opened |
| Asks "what were we working on" or context seems stale mid-session | `atlas-orient` — re-load state |
| Asks to list / search / audit decisions, questions, journal entries | `atlas-entity` (entities) or direct file reads (journal) |
| Onboarding existing project to atlas | `atlas-bootstrap` — rare, once per project |
| Periodic maintenance ("clean up the store", accepting orient's backlog hint) | `atlas-compact` — runs unconfirmed, lands as one commit |

## Anti-patterns

- **DO NOT** skip session-start setup. Always run atlas-orient first.
- **DO NOT** narrate the setup sequence. The `Skill(using-atlas)` and `Skill(atlas-orient)` calls must be your first actions — no "I'll start by…", no "let me orient…", no acknowledgment text before them. Your first prose to the user comes *after* state is loaded.
- **DO NOT** ask "should I open a journal entry?" before bootstrapping. Bootstrap silently when criteria met — no announce either.
- **DO NOT** bootstrap an entry for queries, read-only requests, or greetings.
- **DO NOT** re-invoke using-atlas within an intact context window — once per context window. After a clear or compact the context is rebuilt and the session-start hook demands it again; that re-invocation is correct. On resume the conversation context survives: do not re-run using-atlas, refresh state with `atlas-orient` instead.
- **DO NOT** quote orient's output back to the user. Use it as your internal context.
- **DO NOT** create journal entries from a conversation that's just discussion / exploration. Wait for concrete work intent.
- **DO NOT** drag framework artifacts into *substantive* discussion — no `D-NNN`, `Q-NNN`, `E-NNN`, or journal filenames as references. Translate to content-level language. At legitimate speak-moments (plan review, entity proposals, conflicts), file paths and entity names are allowed; announce-style status lines are not. See "Speak in plain project language" above.

## Cross-references

- `atlas-orient` — load project state (on demand)
- `grill-me` — turn task description into a Plan, written into the active entry
- `atlas-log` — append to / close active journal entries
- `atlas-entity` — create D / E / Q
- `atlas-bootstrap` — onboard existing project (once per project)
- `atlas-compact` — periodic maintenance: backlog + consolidation