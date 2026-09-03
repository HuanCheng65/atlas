#!/usr/bin/env python3
"""Open the file for a work unit: one file, three sections, written once.

The file that used to hold this was `docs/atlas/plan.md`, a single path
overwritten by every work unit in turn. That is what made it rot: a committed
file whose content is only correct while one particular piece of work is in
flight, and which looks authoritative in git forever. One file per work unit
removes the defect without removing the plan — each file is a dated account of
what was undertaken that day, which stays true.

The date lives in the filename and nowhere else, and this script owns it. The
sections are written by the script rather than remembered, so the structure is
mechanical.

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

## Intent

## Spec

## Plan
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--slug", required=True,
                    help="lowercase kebab-case, names the work, not the task type")
    args = ap.parse_args()

    if not SLUG_RE.match(args.slug):
        sys.exit(f"slug must be lowercase kebab-case: {args.slug!r}")

    complaint = _lib.version_complaint()
    if complaint:
        sys.exit(complaint)

    _lib.WORK.mkdir(parents=True, exist_ok=True)
    path = _lib.WORK / f"{datetime.now():%Y-%m-%d}-{args.slug}.md"
    if path.exists():
        # Two work units on one day with one slug is more often a second run
        # against a file already being filled in than a genuine collision.
        sys.exit(f"{path} exists; re-run with a distinguishing slug")

    title = args.slug.replace("-", " ")
    path.write_text(SKELETON.format(title=title[:1].upper() + title[1:]),
                    encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
