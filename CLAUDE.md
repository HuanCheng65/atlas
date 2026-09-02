# Agent Rules

## Project context

See PROJECT.md for background and long-term goals.

<!-- atlas-init: BEGIN (managed block; delete entire block + re-run atlas-init to refresh) -->
## Operational memory (atlas)

This project uses atlas at `docs/atlas/`. The SessionStart hook loads the current state into your context; **invoke the `using-atlas` skill** before responding, for the rules on what earns a record and when to write one. Make the `Skill(using-atlas)` call your first action: no preamble, no "I'll start by…", no acknowledgment text before it.

Atlas data changes ride the work unit's own commits — never commit `docs/atlas/` updates standalone unless the atlas content is itself the work; commit messages describe the content, not the framework.

See `docs/atlas/README.md` for the data model.
<!-- atlas-init: END -->

## Coding conventions

(your conventions here)
