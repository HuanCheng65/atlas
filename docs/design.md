# Atlas Design Notes

Standing design document. Records the current state of the design and the
rejected alternatives. For history of how we arrived here, see git log and
the archived journal.

## Problem statement

Long-running AI-assisted projects suffer from three failure modes:

1. **Context rot** — agent quality degrades as session length grows beyond
   ~50% of the context window
2. **Cross-session amnesia** — each new session has no knowledge of previous
   decisions, experiments, or open issues
3. **Decision drift** — without explicit decision tracking, past
   architectural choices get unintentionally reversed by later sessions

Existing solutions each address a subset:

- **Superpowers** enforces a heavyweight workflow on every task; great for
  discipline, bad for small tasks; doesn't address cross-session decision
  lifecycle
- **grill-me** elegantly solves task-start ambiguity via reverse
  interrogation; doesn't address persistence
- **GSD** targets context rot via fresh subagents and atomic commits;
  doesn't structure decision history
- **Workshop** captures decisions automatically; lacks lifecycle and
  supersedes semantics

Atlas composes the parts that work into a small, opinionated framework.

## Design principles

1. **Data and skills are separate.** Skills (capability) live at user-level
   (`~/.claude/skills/`); data (state) lives at project-level
   (`docs/atlas/`). One install, many projects.
2. **Plain text + git.** No SQLite, no vector DB. Markdown with YAML
   frontmatter is the only data format.
3. **Append-only events, maintained views.** Journal entries are mutable
   until committed and superseded rather than edited afterwards. Indexes
   and standing are derived views, recomputed on read.
4. **One domain, one skill.** Each cognitive domain gets one skill;
   deterministic operations live in scripts inside that skill.
5. **Scripts for the deterministic, prompts for the judgment.** Number
   assignment, frontmatter manipulation, link resolution, validation:
   scripts. Whether something is worth a record at all: agent reasoning.
6. **Schema enforced, not implied.** `validate.py` is the schema — there
   are no templates to drift out of sync with it.
7. **Verification declared, not TDD enforced.** Every task must declare
   how completion is checked, with kept vs discarded artifacts classified.
8. **Event-driven, not phase-driven.** There is no observable "session
   end", so nothing is scheduled for one. Records are written at events
   that actually occur: a measurement completes, a constraint is hit, a
   choice is settled, a commit is made. State loading is the one exception
   and it is a hook, not a judgment — the counting unit is the context
   window, so startup, clear and compact each reload.
9. **No coordination between sessions.** Parallel work across windows is
   normal and needs no shared state: records are append-mostly and
   independently numbered, so two sessions writing at once conflict only
   if they claim the same number, which git surfaces as a conflict.
10. **Mechanisms over prose.** When an agent behavioral rule can be
    enforced or made unnecessary by a mechanism — a script default, a
    script refusal, a hook, a validator — atlas builds the mechanism;
    prose instructions are reserved for judgment calls.
11. **The framework generates no events.** Operations run silently; chat
    mentions atlas only when user input is needed (entity confirmation,
    plan review, binding ambiguity, conflict alerts). Atlas data changes
    ride the work unit's own commits — atlas-only commits exist only when
    atlas content is itself the work.
12. **Archive vs constitution.** Decision records are an ADR-style log
    consulted on demand. PROJECT.md's Working rules are a separate,
    hand-authored artifact holding the rules in force that no mechanism
    enforces — a rule belongs there exactly when nothing stops the agent
    from violating it, and if a check can catch it, the check gets written
    instead. Nothing is promoted automatically; a rule is a rewrite of a
    decision for a different reader, not a status the decision earns.

13. **A record's truth may not depend on a future edit.** This is the
    principle the rest follows from. Stored status, reverse links and
    "close the entry when done" all encode a promise that somebody will
    come back, and in dogfooding nobody did: ten of eleven journal entries
    were never closed, and a refuted experiment kept asserting its result
    in every index for a month.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Session-start hook (settings.json)                      │
│  session_start.py — loads state straight into context    │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│  Skill layer (user-level: ~/.claude/skills/)             │
│  ──────────────────────────────────────────────────      │
│  using-atlas        grill-me                             │
│  atlas-entity       atlas-compact       atlas-bootstrap  │
└────────────────────────┬─────────────────────────────────┘
                         │ reads / writes
                         ▼
┌──────────────────────────────────────────────────────────┐
│  Data layer (per-project: <project>/docs/atlas/)         │
│  ──────────────────────────────────────────────────      │
│  ROADMAP.md                records/NNN-slug.md           │
│  plan.md                     └── _index.md               │
│  archive/                                                │
└──────────────────────────────────────────────────────────┘
                         ▲
                         │ created / maintained by
                         │
┌──────────────────────────────────────────────────────────┐
│  Bootstrap layer (repo: bin/, install.sh)                │
│  install.sh       — symlink skills into ~/.claude/       │
│  atlas-init       — create or extend docs/atlas/         │
└──────────────────────────────────────────────────────────┘
```

Project root files (`CLAUDE.md`, `PROJECT.md`) sit alongside the project's
own code. `CLAUDE.md` holds agent rules and a pointer to atlas; `PROJECT.md`
holds project constitution. `atlas-init` manages CLAUDE.md additively (via
a marker-delimited block) and creates PROJECT.md from template if missing.
`atlas-init` is idempotent — safe to re-run.

## Data model

### Records

One file per record: `docs/atlas/records/NNN-slug.md`, on a single monotonic
counter shared by every type. Numbers are never reused, so an old link keeps
its meaning.

Frontmatter carries identity only — `id`, `title`, `date`, `type`, `tags` —
plus, for experiments, five one-line machine summaries (`hypothesis`,
`config`, `result`, `conclusion`, `artifacts`) capped at 300 characters. The
body owns the prose.

Four types, with `type` an ordinary field rather than an ID prefix, because
the type is a judgment made at the moment of least information and has to
stay correctable without breaking every reference:

- **memory** — a constraint in force. Its title is loaded into every session,
  which makes the set a budget; it is rewritten in place, and git keeps the
  history.
- **experiment** — a measurement and what it showed.
- **decision** — a choice and the alternative it beat, in ADR form: context,
  decision, consequences.
- **question** — something unresolved.

### Relations and derived state

Every relation lives in the body, in Obsidian syntax, written into the
sentence that carries the reasoning:

```
[[047-slug]]                 a reference; produces a backlink
(refutes:: [[021-slug]])     a typed edge
```

Verbs are `supersedes`, `refutes`, `answers`, and nothing else. A typed edge
changes how the **target** renders, which is why it is declared on the newer
record: the older one is never touched.

Nothing stores standing. Superseded, refuted and answered are recomputed from
the incoming edges on every read. This is the point of the design — a record
that depends on a future edit to stay true will eventually be false, because
the edit is a thing somebody has to remember.

Two mechanical consequences, both enforced by `validate.py`:

- **Links point backwards** (`target < source`). A record may only cite what
  already existed. Memory records are exempt: they hold what is true now.
- **Titles are capped** at 90 columns, CJK counted double. A title that will
  not fit an index line is usually two records.

### The publication boundary

An uncommitted record is a draft and may be rewritten freely; a committed one
is superseded rather than edited. Adding a typed edge to a committed record is
the single permitted touch, since it changes nothing the record claims.

This is what replaced the journal's "close" ritual. There is no observable
moment when a session ends, so anything scheduled for one does not happen; a
commit, by contrast, is an event that already exists in the workflow.

### Format versions

`docs/atlas/VERSION` holds a number; its absence means v1, the pre-record
layout, since the file only came in with v2. Every entry point checks it and
refuses a store it does not match.

The check exists because the failure it prevents is silent. Read by v2 scripts,
a v1 store has no `records/` directory, so it loads as zero records: validate
reported OK on a store holding twenty-nine entities, and the session-start
payload told the agent the project had no memory at all. Both are plausible
states for a new project, which is what makes the wrong answer dangerous.

One migration script per version step, named for the step
(`migrate_v1_to_v2.py`), stamping the new version last so an interrupted run
leaves a store that still declares the old one. There is no migration runner
and no chain: one migration does not justify a framework, and the shape the
second one wants will be obvious when it exists.

### Archive

`docs/atlas/archive/` holds superseded layouts verbatim — currently the
pre-record journal. Frozen, still grep-able, never migrated. Bulk-converting
old material into the live store would only refill the inbox the redesign
emptied.

### Plans

`docs/atlas/plan.md` holds the plan for the work in hand, written by
`grill-me` and overwritten per work unit. It is deliberately not a record: a
plan describes intent, and the store holds what happened. Where intent, spec
and implementation should live relative to each other is an open question,
and this file is a placeholder, not an answer.

## Skill activation patterns

Skills are event-driven, not phase-driven. Each skill has its own triggers
described in its SKILL.md. The typical activation timeline for a task:

```
[new conversation on an atlas-enabled project]
       │
       ▼
   SessionStart hook         ← state is already in context; no skill involved
       │
       ▼
   using-atlas               ← the rules for writing records
       │
       ▼
   grill-me (non-trivial work)  → docs/atlas/plan.md
       │
       ▼
   work proceeds; records are written at the events that produce them:
       a measurement completes        → experiment record
       a constraint is hit            → memory record, or rewrite one
       a choice is settled            → decision record
       something unresolved surfaces  → question record
       │
       ▼
   commit — the drafts become published; the diff is the review point


[on demand:]
   atlas-entity     ← audit, rename, validate, migrate
   atlas-compact    ← memory over budget, or a staleness sweep; applies
                      without per-item confirmation, one revertable commit
```

For new projects: `atlas-init` (one-time) → normal workflow above.
For existing projects: `atlas-init` then `atlas-bootstrap` (one-time) →
normal workflow above.

## Verification: Keepers vs Throwaways

Every plan produced by `grill-me` must declare:

- **Verification** — how this task will be checked complete (unit test,
  reference comparison, eval set, manual checklist, ...)
- **Keepers (proposed)** — verification artifacts likely to become
  long-term regression assets
- **Throwaways (proposed)** — development-time scaffolds to delete after merge

Both lists are proposed at planning time and settled at the commit — what
seemed throwaway may turn out worth keeping, and vice versa.

This addresses the observed failure of AI-written tests (surface-level
scaffolds that pass once and clutter the repo forever) while preserving
discipline (no plan ships without a declared completion bar). The form
of verification varies by task: kernel work uses reference-impl comparison,
LLM apps use eval sets, business logic uses unit tests. Atlas does not
pick the form — the agent and user do, per task.

## Trade-offs and rejected alternatives

- **SQLite for entities** — rejected. Loses plain-text + git diff +
  tool-portability.
- **Vector DB for retrieval** — rejected. Maintenance overhead, opacity,
  and ripgrep over prose handles most queries at zero cost — especially now
  that every relation is written in the prose rather than in frontmatter.
- **Single CLAUDE.md as both agent rules and project background** —
  rejected. Different change frequencies, different audiences, different
  lengths. Split into CLAUDE.md (rules) + PROJECT.md (background).
- **Strict TDD enforcement (Superpowers style)** — rejected. Too rigid for
  research code and LLM apps. Replaced with Verification + Keepers /
  Throwaways.
- **Type as an ID prefix (`D-007`, `E-021`)** — rejected. The prefix is
  assigned at creation, the moment of least information, and freezes a
  judgment into an identifier that a thousand references depend on. Type is
  a field; one counter serves every type, which additionally makes "links
  point backwards" expressible as `target < source`.
- **One skill per action (new-decision, supersede, reindex, ...)** —
  rejected. Same cognitive domain belongs in one skill; deterministic
  operations belong in scripts.
- **Writing records at session end** — rejected, twice. A session has no
  observable end: the terminal closes, context compacts, work spans days.
  Anything scheduled for that moment does not happen. Records are written at
  events that do occur, and the commit is the boundary that publishes them.
- **The journal as an inbox with a promotion step** — rejected on dogfood
  evidence. Appending was free and filing a record cost a ceremony, so the
  valuable content went where filing was free and stayed: 317 appends
  against 49 promoted records, 49 of the appends empty, one entry at 155 KB
  still marked active a month after its last edit. The fix is pricing, not
  process — one command writes a record, so there is no backlog to drain.
- **Grepping the agent's own transcripts instead of keeping records** —
  rejected. Transcripts are per-machine, outside git, and pruned: the oldest
  surviving one covered three weeks against a store covering months. They
  remain the right fallback for "what did I actually do last Tuesday", and
  they are why session context is not stored — the window in which "what am
  I in the middle of" matters is the window transcripts cover.
- **A catch-all record type** — rejected. It would absorb exactly the
  content the inbox used to hold, renumbered.
- **Post-hoc one-line announces after atlas operations** — initially
  adopted as the transparency channel, later reversed on dogfood evidence:
  announce content decomposes into either duplicated work content (belongs
  unwrapped in the normal reply) or pure bookkeeping (belongs nowhere in
  chat). The work unit's commit now carries the record; operations are
  silent and the framework speaks only when it needs the user.
- **Inlining every active decision at session start** — replaced by the
  archive/constitution split (principle 12): the always-loaded surface is
  the curated Working rules section, not the unbounded decision log.
- **Bulk-extracting the archived journal into records** — rejected. The
  always-loaded budget admits a few dozen lines, so an expensive pass over
  hundreds of appends would yield candidates the eviction mechanism
  immediately discards. The archive stays grep-able; the user seeds the
  initial constraints from working knowledge.
- **`atlas-init` aborts when `docs/atlas/` exists** — rejected. Makes
  re-running unsafe and prevents partial recovery. Replaced with
  idempotent re-run: copy only missing files, skip existing ones, leave
  user edits intact.
- **`atlas-init --research / --dev` flags** — deferred. One template
  fits both for now; revisit when real friction shows up.
- **Plugin marketplace distribution** — deferred. Dotfiles + symlink is
  simpler for a personal tool.

## Open design questions

- **Where intent lives.** `plan.md` is a placeholder. Plans, specs and
  intent are a different problem from memory — the store holds what
  happened, and nothing here says how the thing you meant to build should be
  written down or kept in step with what got built.
- **Multi-machine sync.** Two machines writing records in parallel will
  claim the same number. Git surfaces that as a conflict rather than losing
  a record, but renumbering on merge is manual.
- **Memory eviction quality.** Compact rewrites the memory set and whatever
  is not carried forward stops being preloaded. The published work this
  borrows from trains the consolidator against task performance; there is no
  equivalent signal here, so the quality of each rewrite is unmeasured.
- **Research task verification.** How does `grill-me` handle research
  tasks where the hypothesis itself is being explored, so a Verification
  standard is genuinely hard to specify up-front?
- ~~**`bootstrap-extras.md` consumption.**~~ Resolved: it is a one-time
  onboarding leftover, not a recurring concern — the user processes or
  deletes it at leisure; compact does not scan it.
- **Cross-skill code sharing.** `using-atlas` and `atlas-compact` import
  the record layer from `atlas-entity` by relative path rather than carrying
  copies. This trades skill self-containment for a single loader; whether
  the coupling is acceptable at distribution time is untested.
