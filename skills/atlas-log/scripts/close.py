#!/usr/bin/env python3
"""Close a journal entry: set frontmatter to closed and write Close section.

Close section body comes from stdin. Script sets `status: closed`,
`closed: <now>`, and `verification-result: <result>`.

Usage:
    echo "$close_body" | close.py \\
        --slug <slug> \\
        --result {passed|failed|partial} \\
        [--at "YYYY-MM-DD HH:MM"]

stdout: the close timestamp written
stderr + non-zero exit on any error

Refuses to close an already-closed entry. Refuses if Close section
already exists (would clobber).
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402

VALID_RESULTS = {"passed", "failed", "partial"}
CLOSE_HEADER_RE = re.compile(r"(?m)^## Close\s*$")


def main():
    ap = argparse.ArgumentParser(
        description="Close a journal entry. Close section body via stdin."
    )
    ap.add_argument("--slug", required=True, help="bare slug (no date prefix)")
    ap.add_argument("--result", required=True, choices=sorted(VALID_RESULTS))
    ap.add_argument("--at", default=None, help="backfill timestamp 'YYYY-MM-DD HH:MM' (default: now)")
    args = ap.parse_args()

    path, meta, body = _lib.load_entry(args.slug)

    if meta.get("status") == "closed":
        _lib.die(f"entry {args.slug!r} is already closed (closed={meta.get('closed')!r})")
    if meta.get("status") not in (None, "active"):
        _lib.die(
            f"entry {args.slug!r} has unexpected status={meta.get('status')!r}; refuse to close"
        )

    ts = _lib.parse_at(args.at) if args.at else _lib.now_str()
    close_body = _lib.read_stdin_body(required=True, label="Close section body")

    if CLOSE_HEADER_RE.search(body):
        _lib.die(
            f"entry {args.slug!r} already has a `## Close` section despite status="
            f"{meta.get('status')!r} — malformed entry, refuse to write"
        )
    new_body = body.rstrip() + f"\n\n## Close\n\n{close_body}\n"
    if not new_body.endswith("\n"):
        new_body += "\n"

    meta["status"] = "closed"
    meta["closed"] = ts
    meta["verification-result"] = args.result

    _lib.save_entry(path, meta, new_body)
    _lib.run_reindex()
    print(ts)


if __name__ == "__main__":
    main()
