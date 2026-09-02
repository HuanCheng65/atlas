# Record Schema

One file per record: `docs/atlas/records/NNN-slug.md`. `validate.py` is the
authority; this page is what it checks and why, plus the body shapes it cannot
check.

## Frontmatter

Every record:

| field | | |
|---|---|---|
| `id` | int | matches the filename; never reused after a record is deleted |
| `title` | string | the claim, not the topic; at most 90 columns, CJK counted double |
| `date` | `YYYY-MM-DD` | when it was written, not when it is true from |
| `type` | `memory` \| `experiment` \| `decision` \| `question` | correctable later; it is a judgment, not identity |
| `tags` | list | from the store's existing vocabulary unless introduced with `--new-tag` |

Experiments carry five more, each a **one-line machine summary** capped at 300
characters. They exist to be read without loading the body; the body owns the
prose, and a body that points back at frontmatter is an error.

| `hypothesis` | one falsifiable sentence |
| `config` | the parameters that would change the result |
| `result` | the key numbers |
| `conclusion` | the verdict in a sentence or two |
| `artifacts` | where the raw output lives |

Nothing else. In particular there is no `status`, and no field naming another
record: standing and relations are both derived from the link graph.

## Body

Free prose under an `# Title` heading, with the relations written into the
sentences that carry the reasoning. Suggested shapes — none enforced:

- **memory** — the constraint, then what to do about it. Cite the record that
  established it. Keep it short: memory titles are loaded into every session,
  and the file is rewritten in place when understanding changes.
- **experiment** — Hypothesis, Setup, Result, Conclusion. Setup carries enough
  to re-run it; Result carries the numbers; Conclusion says what it settles and
  what it does not.
- **decision** — Context (what forced the choice), Decision, Consequences
  (what it commits the project to, including what it gives up). Consequences is
  the section that gets skipped and the one a future reader needs.
- **question** — why it matters, what is known, what would answer it.

## Links

```
[[047-slug]]                    a reference; produces a backlink
[[047-slug|display text]]       the same, with alternate text
(refutes:: [[021-slug]])        a typed edge
```

Verbs: `supersedes`, `refutes`, `answers`. Nothing else; validate rejects an
unknown one rather than treating it as prose. A typed edge changes how the
**target** renders, which is why it is declared on the newer record — the older
one is never edited.

Links point at lower numbers. Memory records are exempt, because they are
rewritten in place rather than superseded.

Code fences and inline code are stripped before parsing, so documentation may
quote the syntax freely.
