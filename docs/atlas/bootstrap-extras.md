# Bootstrap Extras

Items surfaced during atlas-bootstrap that did **not** become D / Q / E entities.
Revisit periodically; promote anything still load-bearing via atlas-entity.

## D-NNN candidates not promoted

- **atlas-init is idempotent** — implementation choice, not architectural;
  documented in `docs/design.md` "Trade-offs and rejected alternatives". Promote
  to D-NNN only if the idempotency contract becomes a constraint on future skills.
- **Post-hoc atlas-log appends (no pre-hoc confirmation)** — UX decision; lives
  inside the `atlas-log` skill itself rather than the framework. Promote if
  multiple skills end up needing the same "post-hoc transparency" pattern.
- **No `type` field in journal frontmatter** — schema micro-decision; subordinate
  to D-005 (one file per work unit). Promote only if a schema migration revisits it.
- **No backfilling journal during bootstrap** — meta-rule that lives inside
  this skill's own contract (see `skills/atlas-bootstrap/SKILL.md`); promoting
  to D would be self-referential noise.

## Q-NNN candidates not promoted

- **`_index.md` git-tracking conflict risk** — documented in design.md with a
  known fallback (gitignore + always regenerate). Promote if friction shows.
- **`bootstrap-extras.md` consumption workflow** — meta-question about this
  very skill; low immediate stakes. Promote if extras accumulate without ever
  being reviewed.

## TODO markers

scan.py surfaced none.
