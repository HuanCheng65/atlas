---
date: 2026-06-12
slug: fix-script-and-skill-doc-bugs-from-design-review
project: Atlas
tags: [scripts, skills, journal, review-followup]
status: closed
opened: 2026-06-12 15:46
closed: 2026-06-12 15:51
verification-result: passed
related: []
---

# Fix script and skill doc bugs from design review

## Context

A design review of the atlas framework this session surfaced six bug-class findings: grill-me's fallback path still instructs hand-writing journal frontmatter/timestamps (contradicting the script-owned-timestamps rule), close.py silently clobbers and truncates instead of refusing when a Close section exists, find_entry's glob suffix-matches wrong entries, atlas-entity's SKILL.md references skills that no longer exist (atlas-session-start/end), docs/atlas/README.md claims new.py auto-reindexes when it doesn't, and the two _lib.py copies have diverged (entity side lacks the timestamp-resolver fix, flow-style lists, and atomic writes). Also minor: new.py slugify truncates at 60 chars mid-word while the documented rule is ~70. This entry covers fixing all of these; design-level findings from the same review are deferred to a follow-up discussion.

## Work log

### 2026-06-12 15:51
Fixed all six review findings plus two extras found during verification:

1. **grill-me fallback** (`skills/grill-me/SKILL.md`): fallback entry creation now routes through `open.py` (heredoc Context, script-owned frontmatter/timestamps); removed the hand-written frontmatter template and the now-redundant manual reindex instruction.
2. **close.py clobber** (`skills/atlas-log/scripts/close.py`): now refuses with a loud error when a `## Close` section already exists, matching its docstring — previously it silently replaced the section and truncated everything after it.
3. **find_entry suffix match** (`skills/atlas-log/scripts/_lib.py`): slug lookup now requires exact `YYYY-MM-DD-<slug>.md`; bare-slug suffix collisions (e.g. `cleanup` matching `...-python3-cleanup.md`) can no longer write to the wrong file.
4. **Stale skill names** (`skills/atlas-entity/SKILL.md`): Out-of-scope section now points to `atlas-log` / `atlas-orient` instead of the nonexistent `atlas-session-end` / `atlas-session-start`.
5. **new.py auto-reindex** (`skills/atlas-entity/scripts/new.py`): now calls `reindex.build_index_for(type)` after creating an entity, making the README's "auto-run inside new.py" claim true.
6. **_lib divergence** (`skills/atlas-entity/scripts/_lib.py`): ported journal-side YAML behavior (timestamp resolver dropped on loader+dumper, flow-style lists, width cap, atomic writes); both _lib docstrings now carry an explicit keep-mirrored instruction.

Extras: slugify cap aligned to the documented ~70 chars with word-boundary cut + stderr note (was silent 60-char mid-word cut); distributed `templates/_templates/` synced with the project-local templates that had gained the title-rules comments (atlas-init would have shipped stale templates).

Verification: sandbox project under /tmp exercised suffix-mismatch refusal, exact-slug append, pre-existing-Close refusal, normal close, double-close refusal, new.py auto-reindex + truncation note, supersede round-trip (flow lists, plain dates, null preserved). Real repo: validate.py OK (21 entities), reindex idempotent. Sandbox removed.

Noticed but not actioned: journal `project:` frontmatter is inconsistent across entries (Atlas/atlas/Kairos); grill-me still tells the agent to Edit `tags`/`related` frontmatter on existing entries while atlas-log forbids frontmatter edits — both deferred to the design discussion.

## Close

**Outcome**: All six bug-class findings from the design review fixed, plus two same-class extras (slugify truncation, distributed-template drift) found during verification.

**Verification result**: Sandbox project exercised every changed code path (wrong-slug refusal, exact append, Close-section refusal, double-close refusal, auto-reindex, truncation note, supersede YAML round-trip); real repo validate.py OK (21 entities) and reindex idempotent. No formal Plan section existed (entry opened ad-hoc); close criterion was implementation done + validators pass.

**Keepers (finalized)**:
- None — verification was a throwaway sandbox by design.

**Throwaways (deleted)**:
- /tmp/atlas-fix-test sandbox project (removed).

**Spawned entities**:
- None yet; the review's design-level findings (D-list scaling, orient parsing derived views, hook-vs-skill contradiction, grill-me description/body mismatch, verification-result signal, prose-based enforcement, index nondeterminism) move to a follow-up discussion and will spawn D/Q there as they settle.
