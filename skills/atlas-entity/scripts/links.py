"""Parse the relations that live in record bodies.

Two forms, both Obsidian-native so the vault's graph and backlink panes work
with no plugin:

    [[047-register-cliff]]                  a plain reference
    [[047-register-cliff|the register cliff]]   the same, with display text
    (refutes:: [[021-overlap-loses]])       a typed edge

A plain reference means "this record is relevant here" and produces a
backlink. A typed edge additionally changes how the *target* renders: a
refuted experiment, a superseded decision, an answered question. Typed edges
are declared on the newer record and point backwards, which is what lets the
older record stay untouched after it has been committed.

Code spans and fenced blocks are stripped before parsing, so documentation
that quotes the syntax does not register as a relation.
"""
import re

# Only these three verbs change how a target renders. Anything else is a
# typo or an invented relation; validate rejects it rather than silently
# treating it as prose.
VERBS = ("supersedes", "refutes", "answers")

FENCE_RE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
# An indented code block: four spaces at the start of a line. Markdown's other
# way of writing a code sample, and records that document the link syntax use it.
INDENTED_CODE_RE = re.compile(r"^(?: {4}|\t).*$", re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

WIKILINK_RE = re.compile(r"\[\[([^\[\]|]+?)(?:\|[^\[\]]*?)?\]\]")
TYPED_EDGE_RE = re.compile(r"\(\s*([A-Za-z][A-Za-z-]*)\s*::\s*\[\[([^\[\]|]+?)(?:\|[^\[\]]*?)?\]\]\s*\)")


def strip_code(text):
    text = FENCE_RE.sub("", text)
    text = INDENTED_CODE_RE.sub("", text)
    return INLINE_CODE_RE.sub(" ", text)


def parse(body):
    """Return (mentions, edges) for one body.

    `mentions` is every wikilink target stem in document order, including the
    ones wrapped in a typed edge — a typed edge is also a reference.
    `edges` is a list of (verb, target stem) in document order; the verb is
    kept verbatim so validate can report an unknown one by name.
    """
    text = strip_code(body)
    mentions = [m.group(1).strip() for m in WIKILINK_RE.finditer(text)]
    edges = [(m.group(1), m.group(2).strip()) for m in TYPED_EDGE_RE.finditer(text)]
    return mentions, edges


def graph(records):
    """Resolve every body's links against the record set.

    Returns (mentions, edges, dangling):
      mentions  {source id: [target id, ...]}   deduplicated, ascending
      edges     {source id: [(verb, target id), ...]}
      dangling  [(source id, target stem, reason)]

    A target is resolved by filename stem, exactly as Obsidian resolves it —
    a link whose stem does not name a file on disk is dangling, and so is one
    whose stem names a different slug for the same number.
    """
    by_stem = {r.stem: r.id for r in records.values()}
    mentions, edges, dangling = {}, {}, []

    for rid, rec in records.items():
        raw_mentions, raw_edges = parse(rec.body)
        seen = []
        for stem in raw_mentions:
            target = by_stem.get(stem)
            if target is None:
                dangling.append((rid, stem, "no record with that filename"))
                continue
            if target not in seen:
                seen.append(target)
        mentions[rid] = sorted(seen)

        resolved = []
        for verb, stem in raw_edges:
            target = by_stem.get(stem)
            if target is None:
                continue  # already reported as a dangling mention
            resolved.append((verb, target))
        edges[rid] = resolved

    return mentions, edges, dangling


def backlinks(mentions):
    """Invert the mention map: {target id: [source id, ...]} ascending."""
    inverted = {}
    for source, targets in mentions.items():
        for target in targets:
            inverted.setdefault(target, []).append(source)
    return {t: sorted(s) for t, s in inverted.items()}


def derive_state(records, edges):
    """Compute each record's current standing from the edges pointing at it.

    Nothing here is stored in frontmatter. A record asserts what was true when
    it was written; whether that assertion still stands is a property of the
    records written since, so it is recomputed on every read.

    Returns {id: (state, [source id, ...])} for every record that something
    later has acted on. Records absent from the result are simply current.
    """
    incoming = {}
    for source, edge_list in edges.items():
        for verb, target in edge_list:
            incoming.setdefault(target, {}).setdefault(verb, []).append(source)

    state = {}
    for target, by_verb in incoming.items():
        if target not in records:
            continue
        # A record can be acted on more than once; report the strongest claim,
        # and supersession outranks the rest because it retires the record.
        for verb, label in (("supersedes", "superseded"),
                            ("refutes", "refuted"),
                            ("answers", "answered")):
            if by_verb.get(verb):
                state[target] = (label, sorted(set(by_verb[verb])))
                break
    return state
