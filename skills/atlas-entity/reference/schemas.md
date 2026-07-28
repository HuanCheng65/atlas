# Atlas Entity Schemas

All three entity types share a base frontmatter, with type-specific extensions. Every field listed below must be present in the frontmatter (with empty list/null/empty dict as default value when no content yet). `validate.py` enforces this.

## Base fields (all types)

| Field | Type | Notes |
|---|---|---|
| id | string | Format `<TYPE>-NNN`, 3-digit zero-padded |
| title | string | Human-readable |
| date | YYYY-MM-DD | Creation date |
| status | string | See lifecycle.md; valid values differ per type |
| tags | list[string] | Free-form, can be `[]` |
| related | list[string] | Cross-type refs, e.g. `[D-003, Q-012]` |
| source-journal | string or null | Journal filename that spawned this, or null |

## Decision (D-NNN) specific

| Field | Type | Notes |
|---|---|---|
| supersedes | list[string] | D-ids this supersedes |
| superseded-by | list[string] | D-ids that supersede this |
| affects | list[string] | Paths or modules, e.g. `[src/kernel/sla_*]` |
| triage | string | `pending \| promoted \| archival` — review state. `pending` shows in orient's menu; `promoted` requires a `(D-NNN)` pointer line in PROJECT.md (validate enforces the pair both ways); `archival` is a reviewed event record |

Status: `planned | active | superseded | rejected`

## Experiment (E-NNN) specific

| Field | Type | Notes |
|---|---|---|
| hypothesis | string or null | One-sentence claim |
| config | object | Key params only, short scalar values |
| result | object | Key numbers only. `{}` until completed |
| artifacts | list[string] | Paths to traces, plots, logs |
| conclusion | string or null | One- or two-sentence verdict |

Status: `planned | running | completed | abandoned`

The four content fields (`hypothesis`, `config`, `result`, `conclusion`) are
machine summaries for scanning without loading bodies — validate rejects any
string value in them over 300 chars. The body sections (Hypothesis / Setup /
Result / Conclusion) own the full prose; a body that says "见 frontmatter" /
"see frontmatter" instead of its content is a validate error.

## Question (Q-NNN) specific

| Field | Type | Notes |
|---|---|---|
| severity | string | `low \| medium \| high` |
| answered-by | string or null | D-id, E-id, or journal filename |

Status: `open | answered | wontfix | merged-into-D`

## File naming

`<TYPE>-NNN-<slug>.md`. Slug is lowercase alphanumeric with hyphens, capped at ~70 chars (`new.py` truncates at a word boundary and warns).

Example: `D-012-use-cuda-graphs-for-dispatch.md`

## Cross-references

Any entity may reference any other via:
- `related: [D-003, E-007, Q-012]` — semantic relation, no specific meaning
- Decision-specific: `supersedes`, `superseded-by`
- Question-specific: `answered-by`

`validate.py` checks all references resolve and bidirectional pairs (supersedes ↔ superseded-by) are consistent.
