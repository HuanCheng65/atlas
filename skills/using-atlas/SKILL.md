---
name: using-atlas
description: Auto-loaded at the start of every conversation on an atlas-enabled project (docs/atlas/ exists). Invoke IMMEDIATELY at session start, before responding to the user's first message. The session-start hook has already injected the project's state; this skill carries the rules for reading and writing the record store — what earns a record, when to write one, and how relations are expressed. This is the single entry point to atlas.
---

# Using Atlas

Atlas is operational memory for you, the agent. The project's state was already
injected into this context by the session-start hook — the guardrails from
PROJECT.md, the constraints currently in force, the open questions, and what
landed recently. **Do not re-read or re-run anything to load it.** This skill is
the other half: what to write, and when.

## Speak in plain project language

The user wants continuity and conflict-detection, not a second thing to manage.
When discussing the work, translate the data layer into plain language.

- **Conflicts**: describe what was decided and why, never the record number.
  Not "this conflicts with 013"; rather "this conflicts with what we settled —
  skills activate on events, not session phases."
- **Past work**: refer to what was done, not the file it lives in.
- **Constraints and questions**: describe them, don't cite them.

The same holds for what you write into the project's own files. A record link
belongs inside `docs/atlas/` and in PROJECT.md, whose constitution cites
records by design. Everywhere else — design notes, result files, READMEs,
commit messages — write what was decided. A number in those is unreadable
without the store, and stops meaning anything at all if the store is ever
renumbered.

Do not name the tooling either. The user does not need to know a framework is
involved; from their side this is simply that you remember the project. Say
"we settled this earlier" or "the notes say", never "atlas says" or "the
using-atlas skill". The first reply of a session is where this slips most:
open by answering what the user asked, not by reporting that state loaded.

Writing records is bookkeeping — do it silently. No "(recorded)" or "(logged)"
lines. The user encounters the record in the commit diff, which is a better
review surface than a chat line. If something you just wrote down matters to the
user right now, say it in your reply as work content, unwrapped.

Speak about the framework only when you need the user: proposing a record that
commits them to something, a plan review, or — immediately, never batched — a
conflict between what they just asked for and a constraint in force.

Name the mechanics directly when the user asks to see, list, audit or edit
records, or when the project being worked on is atlas itself.

## The store

Every record is `docs/atlas/records/NNN-slug.md` on one counter shared by all
types. Frontmatter carries identity only — `id`, `title`, `date`, `type`,
`tags`. There is no status field: whether a record still stands is computed from
the records written since.

Four types, and `type` is an ordinary field you can correct later:

| type | holds | test |
|---|---|---|
| `memory` | a constraint or prohibition in force | would someone not knowing this do the opposite? |
| `experiment` | a measurement and what it showed | is there a result somebody may cite? |
| `decision` | a choice and the alternative it beat | is the rationale needed to build on it? |
| `question` | something unresolved | will it outlive this session? |

The title is the menu. It has to identify the record on its own in an index; a
title that will not fit is usually two records. Nothing is a catch-all — a
record that states no claim is a diary entry, and diary entries belong in the
transcript, which is already complete and already grep-able.

## Relations live in the body

Write the link in the sentence that carries the reasoning, in Obsidian syntax:

    Confirmed on the clean tier, which (refutes:: [[021-overlap-loses-18pct]])
    — the earlier reading came from an occupancy tier with 16% variance.

A bare `[[NNN-slug]]` is a reference and produces a backlink. A typed edge —
`supersedes`, `refutes`, `answers`, and nothing else — additionally changes how
the **target** renders, so a superseded decision reads as superseded without
anyone going back to edit it.

**Links point backwards.** A record may only cite records that already existed
when it was written. Memory records are the exception: they hold what is
currently true, are rewritten in place, and git keeps their history.

Get the target's filename exactly right. Links resolve by filename and nothing
else, so a mistyped slug is not a broken link that surfaces later — it is a
relation that never happens, leaving the record it should have superseded
standing. A hook checks the store after every write and will tell you; treat
that as the error it is rather than as a lint.

## When to write

| moment | what to write |
|---|---|
| a measurement finishes and has a result | an `experiment` record, now — the numbers are in front of you and reconstructing them later is expensive |
| you hit a limit that will bite again — a cliff, a knob that does nothing, a path already measured and closed | a `memory` record, or rewrite the existing one |
| a choice gets settled that constrains future choices, even if nobody called it a decision | a `decision` record |
| a question surfaces that will not be answered this session | a `question` record |
| your understanding of a constraint changes | rewrite that memory record in place |

Do not wait for the end of the session — there is no observable moment where a
session ends, and anything that depends on one will not happen.

Do not ask permission first. An uncommitted record is a draft: rewrite it,
retype it, or delete it freely. **The commit is the publication boundary** — once
a record is committed it is superseded by a newer record, never edited. So the
review point is the diff, not an interruption mid-work.

The failure to guard against is "the user didn't ask me to record this." They
won't. Recognition is yours.

## Writing one

One command; the body is the record.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/atlas-entity/scripts/new.py" \
    --type memory --title "The register cliff is at 128" --tags h20 <<'EOF'
Any estimator change must be checked with `cuobjdump` first: crossing 128
registers drops residency a tier. Measured in [[019-register-ladder]].
EOF
```

Tags come from the store's existing vocabulary; the script prints it and
refuses an unknown tag unless you pass `--new-tag` deliberately. Reusing what is
there is what keeps tags worth grouping by.

## When the store does not have the answer

The store holds what was worth keeping. The raw conversation is the other
half — complete, recent, and disposable — and answers two things the store
cannot: what was being done on some past day, and whether something was
already tried.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/using-atlas/scripts/transcripts.py" list
python3 "${CLAUDE_PLUGIN_ROOT}/skills/using-atlas/scripts/transcripts.py" grep "register cliff"
```

`list` names the sessions for this project, newest first, with their message
counts; `grep` searches the prose across them and returns dated excerpts.
Both skip tool calls and their results, which are most of the bytes and none
of the meaning.

**This machine only, and only recently.** Transcripts sit outside the
repository and are pruned after a few weeks, so two machines working on one
project never share them. Take that as a signal rather than a limitation:
wanting something in a transcript to be durable, or visible from elsewhere,
means it should have been a record.

## Atlas changes ride the work's commits

Record changes are part of the work unit they describe. Stage them with the
work's own commit; the message names the content, never the framework. A
records-only commit is legitimate only when the records are themselves the work.

## Routing

| user signal | skill |
|---|---|
| non-trivial work about to start | `atlas:grill-me` |
| list / search / audit records, or a bulk record operation | `atlas:atlas-entity` |
| "clean up the store", memory over budget | `atlas:atlas-compact` |
| setting a project up on atlas — starting one, or onboarding one that exists | `atlas:atlas-bootstrap` |

## Anti-patterns

- **DO NOT** re-load state at session start; the hook already did it.
- **DO NOT** narrate the setup, and **DO NOT** summarise the loaded state back.
  Reciting the record counts, the milestone, or what the working tree contains
  is the same noise as announcing an operation. Invoke this skill and answer
  the user's actual message, as though you had always known the rest.
- **DO NOT** ask "should I record this?" before writing a draft record.
- **DO NOT** edit a committed record's claims — write a newer record with a
  typed edge pointing back at it.
- **DO NOT** cite record numbers in substantive conversation.
- **DO NOT** write `[[NNN-slug]]` into any file outside `docs/atlas/` and
  PROJECT.md.
