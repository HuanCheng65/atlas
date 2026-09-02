#!/usr/bin/env python3
"""Validate the atlas record store.

Checks identity (filename agrees with frontmatter, ids unique), schema
(required fields present, deleted fields absent, type legal, title within the
index-line budget), the frontmatter/body split for experiments, and the link
graph (every wikilink resolves, every typed edge uses a known verb and points
backwards).

The direction rule is the mechanical form of "a published record is never
edited": a record may only reference records that already existed when it was
written. Memory records are the stated exception — they hold the constraints
currently in force, are rewritten in place, and git keeps their history.

Usage:
    validate.py

Exits non-zero on any error.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402
import links  # noqa: E402

REQUIRED_BASE = ["id", "title", "date", "type", "tags"]
REQUIRED_BY_TYPE = {
    "experiment": ["hypothesis", "config", "result", "artifacts", "conclusion"],
}

# Fields the old schema stored and the link graph now derives. They are
# rejected by name so a half-finished migration fails loudly instead of
# leaving a field nothing reads.
DERIVED_FIELDS = [
    "status", "related", "supersedes", "superseded-by", "refuted-by",
    "answered-by", "triage", "affects", "source-journal", "severity",
]

# An index line has to stay scannable, and a title that will not fit is
# usually two findings joined by a semicolon.
MAX_TITLE_WIDTH = 90

# Experiment frontmatter fields are machine summaries scanned without loading
# the body; the body sections own the full prose.
E_SUMMARY_FIELDS = ["hypothesis", "config", "result", "conclusion"]
MAX_SUMMARY_LEN = 300

# A section that says "见 frontmatter" instead of its content is a hole.
FRONTMATTER_POINTER_RE = re.compile(r"见\s*frontmatter|see\s+frontmatter", re.IGNORECASE)

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def string_leaves(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from string_leaves(v)
    elif isinstance(value, list):
        for v in value:
            yield from string_leaves(v)


def collect_duplicate_ids():
    """load_all() keys by id, so a second file claiming a number would be
    silently dropped. Catch it from the filenames instead."""
    seen = {}
    for path in _lib.record_paths():
        try:
            rid, _ = _lib.split_stem(path.stem)
        except ValueError:
            continue
        seen.setdefault(rid, []).append(path.name)
    return {rid: names for rid, names in seen.items() if len(names) > 1}


def main():
    errors = []

    def err(msg):
        errors.append(msg)

    for path in _lib.record_paths():
        try:
            _lib.split_stem(path.stem)
        except ValueError as exc:
            err(str(exc))

    for rid, names in sorted(collect_duplicate_ids().items()):
        err(f"{rid:03d}: {len(names)} files claim this number: {', '.join(sorted(names))}")

    records = _lib.load_all()

    for rid, rec in sorted(records.items()):
        name = rec.path.name

        if rec.meta.get("id") != rid:
            err(f"{name}: frontmatter id is {rec.meta.get('id')!r}, filename says {rid}")
        if rec.meta.get("slug") not in (None, rec.slug):
            err(f"{name}: frontmatter slug is {rec.meta.get('slug')!r}, filename says {rec.slug!r}")

        for field in REQUIRED_BASE + REQUIRED_BY_TYPE.get(rec.type, []):
            if field not in rec.meta:
                err(f"{name}: missing required field `{field}`")

        for field in DERIVED_FIELDS:
            if field in rec.meta:
                err(f"{name}: field `{field}` is derived from the link graph — "
                    f"remove it from frontmatter")

        if rec.type not in _lib.TYPES:
            err(f"{name}: illegal type {rec.type!r} (one of {', '.join(_lib.TYPES)})")

        date = rec.meta.get("date")
        if date is not None and not (isinstance(date, str) and DATE_RE.match(date)):
            err(f"{name}: date must be YYYY-MM-DD, got {date!r}")

        tags = rec.meta.get("tags")
        if tags is not None and not isinstance(tags, list):
            err(f"{name}: tags must be a list, got {type(tags).__name__}")

        title = rec.title
        if isinstance(title, str):
            width = _lib.display_width(title)
            if width > MAX_TITLE_WIDTH:
                err(f"{name}: title is {width} columns wide, over the {MAX_TITLE_WIDTH} "
                    f"budget — a title that will not fit an index line is usually "
                    f"two records")
        elif title is not None:
            err(f"{name}: title must be a string, got {type(title).__name__}")

        if rec.type == "experiment":
            for field in E_SUMMARY_FIELDS:
                for s in string_leaves(rec.meta.get(field)):
                    if len(s) > MAX_SUMMARY_LEN:
                        err(f"{name}.{field}: {len(s)}-char value exceeds {MAX_SUMMARY_LEN} — "
                            f"frontmatter fields are one-line machine summaries; "
                            f"full prose belongs in the body")
                        break

        if FRONTMATTER_POINTER_RE.search(rec.body):
            err(f"{name}: body points at frontmatter instead of stating its content — "
                f"the body is the canonical prose; write it out")

    mentions, edges, dangling = links.graph(records)

    for source, stem, reason in dangling:
        err(f"{records[source].path.name}: link [[{stem}]] does not resolve — {reason}")

    for source, targets in mentions.items():
        if source in targets:
            err(f"{records[source].path.name}: links to itself")
        if records[source].type == "memory":
            continue
        for target in targets:
            if target > source:
                err(f"{records[source].path.name}: references {target:03d}, which did not "
                    f"exist when this record was written — links point backwards, and a "
                    f"published record is not edited to cite a later one")

    for source, edge_list in edges.items():
        for verb, target in edge_list:
            if verb not in links.VERBS:
                err(f"{records[source].path.name}: unknown edge `{verb}::` "
                    f"(one of {', '.join(links.VERBS)})")
            elif target > source:
                err(f"{records[source].path.name}: `{verb}::` points at {target:03d}, "
                    f"a later record — a typed edge is declared on the newer record")

    if errors:
        print(f"\n{len(errors)} error(s):\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"OK ({len(records)} records checked)")


if __name__ == "__main__":
    main()
