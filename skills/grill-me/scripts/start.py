#!/usr/bin/env python3
"""Open the document for one round of grilling: what it decided, what it left.

A grill crosses one gap — from something vague to something more decided — and
the gaps do not come in a fixed set of three. Settling a product's form is
design at one depth; how each module is built is design one depth lower, and
neither is Intent, Spec or Plan. The skeleton this used to write demanded all
three from every interview, so a round that stopped at a design had to invent
the levels it never reached. The level is now a label in the title.

The continuation line is the only structure holding the documents together, and
a spine maintained by prose reminders is not maintained — so exactly one of
`--from` or `--new` is required, and `--from` refuses a target that is not
there.

The date lives in the filename and nowhere else, and this script owns it.

Must be run from the project root.
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "atlas-entity" / "scripts"))
import _lib  # noqa: E402

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

SKELETON = """\
# {title}

{lineage}

## Decided

## Still open
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--slug", required=True,
                    help="lowercase kebab-case, names what this round settled")
    lineage = ap.add_mutually_exclusive_group(required=True)
    lineage.add_argument("--from", dest="parent", metavar="FILENAME",
                         help="the design document this round continues")
    lineage.add_argument("--new", action="store_true",
                         help="this round starts a line of its own")
    args = ap.parse_args()

    if not SLUG_RE.match(args.slug):
        sys.exit(f"slug must be lowercase kebab-case: {args.slug!r}")

    complaint = _lib.version_complaint()
    if complaint:
        sys.exit(complaint)

    if args.parent:
        parent = _lib.DESIGN / Path(args.parent).name
        if not parent.is_file():
            sys.exit(f"no such design document: {parent}")
        lineage = f"Continues `{parent}`."
    else:
        lineage = "Starts a new line."

    _lib.DESIGN.mkdir(parents=True, exist_ok=True)
    path = _lib.DESIGN / f"{datetime.now():%Y-%m-%d}-{args.slug}.md"
    if path.exists():
        # Two rounds on one day with one slug is more often a second run
        # against a file already being filled in than a genuine collision.
        sys.exit(f"{path} exists; re-run with a distinguishing slug")

    title = args.slug.replace("-", " ")
    path.write_text(
        SKELETON.format(title=title[:1].upper() + title[1:], lineage=lineage),
        encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
