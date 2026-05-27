#!/usr/bin/env python3
"""Close an open question.

Usage:
    close_question.py Q-007 --by D-012
    close_question.py Q-007 --by 2026-05-27-bench-result.md
    close_question.py Q-007 --wontfix
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("qid")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--by", help="entity-id (e.g. D-012) or journal filename")
    g.add_argument("--wontfix", action="store_true")
    args = ap.parse_args()

    if not args.qid.startswith("Q-"):
        sys.exit("ERROR: id must start with Q-")

    path, meta, body = _lib.load_entity(args.qid)

    if args.wontfix:
        meta["status"] = "wontfix"
        meta["answered-by"] = None
    else:
        ref = args.by
        if ref.startswith("D-"):
            meta["status"] = "merged-into-D"
        else:
            meta["status"] = "answered"
        meta["answered-by"] = ref

    _lib.save_entity(path, meta, body)
    print(f"{args.qid}: status={meta['status']}, answered-by={meta['answered-by']}")


if __name__ == "__main__":
    main()
