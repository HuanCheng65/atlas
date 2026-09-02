#!/usr/bin/env python3
"""Create a record under docs/atlas/records/.

One call writes the whole record: identity, tags, and the body on stdin. The
cost of writing a finding down has to stay at one command, because whenever
filing was more expensive than not filing, the findings went wherever filing
was free and stayed there.

    new.py --type memory --title "The register cliff is at 128" \\
           --tags h20,occupancy <<'EOF'
    Body prose, with [[021-overlap-loses|links]] where the reasoning is.
    EOF

Experiments carry five one-line machine summaries as flags:

    new.py --type experiment --title "..." --tags h20 \\
           --hypothesis "..." --config "..." --result "..." \\
           --conclusion "..." --artifacts "..." < body.md

A tag that is not already in use must be introduced with --new-tag. Reusing
the existing vocabulary is what keeps tags worth grouping by; without the
check the store drifts into a long tail of words used exactly once.
"""
import argparse
import datetime
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402

MAX_SLUG_LEN = 70

EXPERIMENT_FIELDS = ["hypothesis", "config", "result", "conclusion", "artifacts"]


def slugify(title):
    """ASCII slug from a title, or '' when the title leaves nothing usable.

    A CJK title survives ASCII folding only as whatever digits it contained,
    so "寄存器悬崖在 128" would otherwise become `001-128.md`. Requiring a
    letter turns that into a request for an explicit --slug.
    """
    ascii_form = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", ascii_form.lower()).strip("-")
    if not re.search(r"[a-z]", s):
        return ""
    if len(s) > MAX_SLUG_LEN:
        s = s[:MAX_SLUG_LEN].rsplit("-", 1)[0]
        print(
            f"NOTE: slug truncated to {s!r} — the title exceeds the ~{MAX_SLUG_LEN}-char "
            "slug rule, consider tightening it",
            file=sys.stderr,
        )
    return s


def tag_vocabulary(records):
    counts = Counter()
    for rec in records.values():
        for tag in rec.meta.get("tags") or []:
            counts[tag] += 1
    return counts


def format_vocabulary(counts):
    if not counts:
        return "  (the store has no tags yet — every tag is new)"
    return "\n".join(
        f"  {tag} ({n})" for tag, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", required=True, choices=list(_lib.TYPES))
    ap.add_argument("--title", required=True)
    ap.add_argument("--slug", help="override the slug derived from the title")
    ap.add_argument("--tags", default="", help="comma-separated, from the existing vocabulary")
    ap.add_argument("--new-tag", default="",
                    help="comma-separated tags being introduced deliberately")
    ap.add_argument("--date", help="override today's date (YYYY-MM-DD)")
    for field in EXPERIMENT_FIELDS:
        ap.add_argument(f"--{field}", help=f"experiment {field} — one line")
    args = ap.parse_args()

    _lib.require_version()

    body = sys.stdin.read().strip()
    if not body:
        sys.exit("ERROR: the body is the record; pass it on stdin")

    records = _lib.load_all()

    slug = args.slug or slugify(args.title)
    if not slug:
        sys.exit(f"ERROR: {args.title!r} yields an empty slug — pass --slug explicitly")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        sys.exit(f"ERROR: slug {slug!r} must be lowercase words joined by hyphens")

    known = tag_vocabulary(records)
    declared_new = [t.strip() for t in args.new_tag.split(",") if t.strip()]
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] + declared_new
    unknown = [t for t in tags if t not in known and t not in declared_new]
    if unknown:
        sys.exit(
            f"ERROR: {', '.join(unknown)} — not in the store's vocabulary. Reuse one of "
            f"these, or pass --new-tag to introduce it deliberately:\n"
            + format_vocabulary(known)
        )

    if args.type == "experiment":
        missing = [f for f in EXPERIMENT_FIELDS if not getattr(args, f)]
        if missing:
            sys.exit(f"ERROR: an experiment needs {', '.join('--' + m for m in missing)}")

    rid = _lib.next_id(records)
    meta = {
        "id": rid,
        "title": args.title,
        "date": args.date or datetime.date.today().isoformat(),
        "type": args.type,
        "tags": tags,
    }
    if args.type == "experiment":
        for field in EXPERIMENT_FIELDS:
            meta[field] = getattr(args, field)

    path = _lib.RECORDS / f"{_lib.format_stem(rid, slug)}.md"
    if path.exists():
        sys.exit(f"ERROR: file already exists: {path}")
    _lib.RECORDS.mkdir(parents=True, exist_ok=True)
    _lib.atomic_write(path, _lib.dump_md(meta, f"\n# {args.title}\n\n{body}\n"))

    import reindex  # noqa: E402  (same dir, path set above)
    reindex.build()

    print(path)


if __name__ == "__main__":
    main()
