#!/usr/bin/env python3
"""Change a record's slug and rewrite every link that names it.

Wikilinks resolve by filename — Obsidian does not consult frontmatter aliases
— so a slug is part of the store's link graph rather than a cosmetic label.
Renaming is therefore a whole-store edit, and a mechanical one, which is why
it belongs in a script rather than in an agent's judgment.

    rename.py 047 register-cliff-at-128
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id", type=int)
    ap.add_argument("slug")
    args = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
        sys.exit(f"ERROR: slug {args.slug!r} must be lowercase words joined by hyphens")

    records = _lib.load_all()
    target = records.get(args.id)
    if target is None:
        sys.exit(f"ERROR: no record {args.id:03d}")
    if target.slug == args.slug:
        sys.exit(f"ERROR: {target.stem} already has that slug")

    old_stem, new_stem = target.stem, _lib.format_stem(args.id, args.slug)
    new_path = _lib.RECORDS / f"{new_stem}.md"
    if new_path.exists():
        sys.exit(f"ERROR: file already exists: {new_path}")

    # `[[old-stem]]` and `[[old-stem|display text]]`, nothing else — a bare
    # substring replace would also hit prose that happens to quote the stem.
    link_re = re.compile(r"\[\[" + re.escape(old_stem) + r"(\|[^\[\]]*?)?\]\]")

    rewritten = []
    for rid, rec in sorted(records.items()):
        new_body, n = link_re.subn(lambda m: f"[[{new_stem}{m.group(1) or ''}]]", rec.body)
        if n:
            rec.body = new_body
            if rid != args.id:
                _lib.save_record(rec)
            rewritten.append((rec.path.name, n))

    target.meta["id"] = args.id
    target.path = new_path
    _lib.atomic_write(new_path, _lib.dump_md(target.meta, target.body))
    (_lib.RECORDS / f"{old_stem}.md").unlink()

    import reindex  # noqa: E402  (same dir, path set above)
    reindex.build()

    total = sum(n for _, n in rewritten)
    print(f"{old_stem} -> {new_stem}; rewrote {total} link(s) in {len(rewritten)} file(s)")


if __name__ == "__main__":
    main()
