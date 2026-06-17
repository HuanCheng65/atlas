# Atlas Design Notes

Standing design document. Records the current state of the design and the
rejected alternatives. For history of how we arrived here, see git log and
the journal entries.

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
   while active and frozen when closed. Entities (D / E / Q) are mutable
   with explicit lifecycle. Indexes are derived views.
4. **One domain, one skill.** Each cognitive domain gets one skill;
   deterministic operations live in scripts inside that skill.
5. **Scripts for the deterministic, prompts for the judgment.** ID
   assignment, frontmatter manipulation, validation: scripts. Whether
   something deserves to be a D-NNN, or whether a journal append is
   warranted: agent reasoning.
6. **Schema enforced, not implied.** Templates define required fields.
   `validate.py` checks them.
7. **Verification declared, not TDD enforced.** Every task must declare
   how completion is checked, with kept vs discarded artifacts classified.
8. **Event-driven, not phase-driven.** No "session start" or "session
   end" moment. Skills activate on events: a task is described
   (grill-me), work progresses (atlas-log), context is needed
   (atlas-orient). The counting unit for setup re-injection is the
   context window, not the session: rebuilt context (startup / clear /
   compact) re-demands using-atlas; resume only refreshes state via
   atlas-orient.
9. **Multi-active by default.** Parallel work across windows / topics is
   normal. Each agent instance carries "which entry am I working on" in
   conversation memory; multiple active journal entries coexist without
   coordination.
10. **Mechanisms over prose.** When an agent behavioral rule can be
    enforced or made unnecessary by a mechanism — a script default, a
    script refusal, a hook, a validator — atlas builds the mechanism;
    prose instructions are reserved for judgment calls.
11. **The framework generates no events.** Operations run silently; chat
    mentions atlas only when user input is needed (entity confirmation,
    plan review, binding ambiguity, conflict alerts). Atlas data changes
    ride the work unit's own commits — atlas-only commits exist only when
    atlas content is itself the work.
12. **Archive vs constitution.** Decision records are an ADR-style event
    log consulted on demand; the standing rules they establish promote as
    one-liners (with `(D-NNN)` pointers) into PROJECT.md's Working rules,
    which orient inlines every session. Triage state (`pending |
    promoted | archival`) tracks the split; validate enforces the
    pointer pairing both ways.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Skill layer (user-level: ~/.claude/skills/)             │
│  ──────────────────────────────────────────────────      │
│  grill-me           atlas-orient                         │
│  atlas-bootstrap    atlas-log                            │
│  atlas-entity       atlas-compact                        │
└────────────────────────┬─────────────────────────────────┘
                         │ reads / writes
                         ▼
┌──────────────────────────────────────────────────────────┐
│  Data layer (per-project: <project>/docs/atlas/)         │
│  ──────────────────────────────────────────────────      │
│  roadmap.md                topics/*.md                   │
│  journal/*.md              decisions/D-NNN-*.md          │
│    └── _index.md           experiments/E-NNN-*.md        │
│  _templates/*.md           questions/Q-NNN-*.md          │
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

### Entities (D / E / Q)

Three structured entity types share a base frontmatter (`id`, `title`,
`date`, `status`, `tags`, `related`, `source-journal`) and per-type
extensions. Status state machines differ per type (see
`skills/atlas-entity/reference/lifecycle.md`).

- **D-NNN** — long-term decision; linked by `supersedes` / `superseded-by`;
  carries `triage: pending | promoted | archival` (see principle 12)
- **E-NNN** — experiment; `hypothesis` / `config` / `result` / `conclusion`
- **Q-NNN** — open question; closed via `answered-by` (D-id, E-id, or journal)

`_index.md` files are derived, human-only browse views, regenerated by
`reindex.py`; their content is deterministic (no run-date dependence —
recency windows are computed by orient at render time). Agent-facing
reads parse frontmatter directly.

### Journal

A journal entry represents **one work unit** end to end: planning,
execution, closure. File path: `docs/atlas/journal/YYYY-MM-DD-<slug>.md`.
Body structure:

```
## Context             ← from grill-me
## Decisions resolved
## Steps
## Verification
## Keepers (proposed)
## Throwaways (proposed)
## Work log            ← appended by atlas-log during work
## Close               ← filled by atlas-log at close, with user confirmation
```

Frontmatter includes `status: active | closed`, `opened`, `closed`,
`verification-result`. Active entries are mutable; closed entries are frozen.

Multiple active entries coexist (parallel work). Each agent instance carries
"which entry am I working on" in conversation memory. `journal/_index.md`
shows all actives.

### Topics

Free-form `topics/<name>.md`. Long-form notes that emerge from journal
patterns. Never bootstrapped — only created when several journal entries
warrant distillation. `atlas-compact` writes them during its runs; the
run's single commit is the review point.

## Skill activation patterns

Skills are event-driven, not phase-driven. Each skill has its own triggers
described in its SKILL.md. The typical activation timeline for a task:

```
[new conversation on an atlas-enabled project]
       │
       ▼
   atlas-orient              ← read state, identify active work
       │
       ▼
   ┌─────────────────┐
   │ New work?       │
   └─────────────────┘
       │
   yes │             no
       ▼             ▼
   grill-me     atlas-log (append to existing active entry)
       │             │
       │             ▼
       │     (work continues, atlas-log appends as events occur...)
       │             │
       ▼             ▼
   atlas-log (append, append, append...)
       │
       ▼
   atlas-log (close, with user confirmation)


[in parallel throughout:]
   atlas-entity     ← create D / Q / E whenever work warrants
   atlas-compact    ← on demand (orient hints at backlog): clear backlog,
                      consolidate records; applies without per-item
                      confirmation, lands as one revertable commit
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

Keepers and Throwaways are **proposed** in the Plan section, **finalized**
by `atlas-log` in the Close section. The lists may shift during work — what
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
- **Vector DB for journal retrieval** — rejected. Maintenance overhead,
  opacity, and ripgrep + frontmatter handles ~80% of queries at zero cost.
- **Single CLAUDE.md as both agent rules and project background** —
  rejected. Different change frequencies, different audiences, different
  lengths. Split into CLAUDE.md (rules) + PROJECT.md (background).
- **Strict TDD enforcement (Superpowers style)** — rejected. Too rigid for
  research code and LLM apps. Replaced with Verification + Keepers /
  Throwaways.
- **Experiments as journal sub-type (`type: experiment`)** — rejected.
  Separate `experiments/` directory gives better browse experience for
  paper writing.
- **One skill per action (new-decision, supersede, reindex, ...)** —
  rejected. Same cognitive domain belongs in one skill; deterministic
  operations belong in scripts.
- **Session-end as an explicit step** — rejected. Session is a soft
  concept; explicit boundaries get missed or fragmented. Replaced with
  event-driven `atlas-log`: append on substantial work events, close
  only with user confirmation.
- **Plan and journal as separate files** — rejected. They describe the
  same work unit. Plan + Work log + Close are sections within one journal
  entry that evolves over time.
- **One active journal entry per project at any time** — rejected.
  Parallel work across windows / topics is normal. Each agent instance
  tracks its own current entry; the index supports any number of actives.
- **Pre-hoc confirmation for every atlas-log append** — rejected. Friction
  kills the flow. Close-by-proposal still requires confirmation because it
  is sticky.
- **Post-hoc one-line announces after atlas operations** — initially
  adopted as the transparency channel, later reversed on dogfood evidence:
  announce content decomposes into either duplicated work content (belongs
  unwrapped in the normal reply) or pure bookkeeping (belongs nowhere in
  chat). The work unit's commit now carries the record; operations are
  silent and the framework speaks only when it needs the user.
- **Inlining every active decision at session start** — replaced by the
  archive/constitution split (principle 12): the always-loaded surface is
  the curated Working rules section, not the unbounded decision log.
- **`type` field in journal frontmatter** (e.g. `log` vs `plan`) —
  rejected. One file already represents the full lifecycle of a work
  unit; type would be redundant noise.
- **Backfilling journal during bootstrap** — rejected. Journal records
  events going forward. Past events live in git log; do not duplicate.
- **`atlas-init` aborts when `docs/atlas/` exists** — rejected. Makes
  re-running unsafe and prevents partial recovery. Replaced with
  idempotent re-run: copy only missing files, skip existing ones, leave
  user edits intact.
- **`atlas-init --research / --dev` flags** — deferred. One template
  fits both for now; revisit when real friction shows up.
- **Plugin marketplace distribution** — deferred. Dotfiles + symlink is
  simpler for a personal tool.

## Open design questions

- **Stale active entry threshold.** Currently using "3 days no update" as
  the hint for "this might be stale, propose closing." Not validated
  against real usage.
- **Multi-machine sync.** When two machines diverge on the same atlas
  (different journal entries on each), is there a smarter merge strategy
  than manual resolution?
- **Research task verification.** How does `grill-me` handle research
  tasks where the hypothesis itself is being explored, so a Verification
  standard is genuinely hard to specify up-front?
- ~~**`bootstrap-extras.md` consumption.**~~ Resolved: it is a one-time
  onboarding leftover, not a recurring concern — the user processes or
  deletes it at leisure; compact does not scan it.
- **Cross-skill code sharing.** Each skill currently has its own scripts,
  with some duplication (e.g. `parse_md` inline in multiple places).
  Trade-off chosen for skill self-containment over DRY. Revisit if
  duplication grows past a few small functions.
