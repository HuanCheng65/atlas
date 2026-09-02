# Agent Rules

## Project context

See PROJECT.md for background and long-term goals.

<!-- atlas-init: BEGIN (managed block; delete entire block + re-run atlas-init to refresh) -->
## Project memory

The project's memory lives at `docs/atlas/`. The SessionStart hook loads its current state into your context; **invoke the `atlas:using-atlas` skill** before responding, for the rules on writing to it. Make that call your first action and make it silently — no preamble, no "I'll start by…", no acknowledgement, and no summary of what was loaded. Answer the user's message as though you had simply always known the rest, and refer to this material as the project's memory rather than by the name of the tooling.

Atlas data changes ride the work unit's own commits — never commit `docs/atlas/` updates standalone unless the atlas content is itself the work; commit messages describe the content, not the framework.

See `docs/atlas/README.md` for the data model.
<!-- atlas-init: END -->

## Coding conventions

(your conventions here)
