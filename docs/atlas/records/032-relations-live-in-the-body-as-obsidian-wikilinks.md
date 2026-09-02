---
id: 32
title: Relations live in the body as Obsidian wikilinks
date: 2026-09-02
type: decision
tags: [data-model, schema, links, obsidian]
---

# Relations live in the body as Obsidian wikilinks

## Context

The dogfood store held 1268 references between records. 1163 of them were in
prose, where nothing could read them; 105 were in frontmatter `related` fields,
where they were read but carried no meaning beyond "these are connected". One
record had a tag literally named after another record's id, because the agent
wanted to express a link and tags were the only structured field available.

So the link graph already existed. It just had no parser, and the structured
half was in the wrong place: a relation declared in frontmatter is separated
from the sentence that justifies it, which is how the one hand-written
refutation pointer came to exist on the wrong record with no reverse link.

## Decision

Every relation lives in the body, written into the sentence that carries the
reasoning, in Obsidian's own syntax:

    [[047-slug]]                 a reference; produces a backlink
    (refutes:: [[021-slug]])     a typed edge

Frontmatter link fields are deleted. Verbs are `supersedes`, `refutes` and
`answers`; validate rejects any other rather than treating it as prose.

Writing the sentence and declaring the edge is one act, which is why it cannot
drift the way a frontmatter field does.

## Consequences

The vault opens in Obsidian with a working graph view and backlink pane and no
plugins, because the wikilink inside a typed edge is an ordinary wikilink. The
`verb::` wrapper is inert to core Obsidian and queryable if Dataview is
installed. The syntax is also one the model has seen a great deal of, which
costs less to write correctly than an invented one.

Obsidian resolves wikilinks by filename and does not consult frontmatter
aliases, so the link text must equal the filename. Renaming is therefore a
whole-store rewrite and belongs in a script, not in an agent's judgment.

Bodies that quote the syntax are not relations: code fences and inline code are
stripped before parsing, which this record depends on.
