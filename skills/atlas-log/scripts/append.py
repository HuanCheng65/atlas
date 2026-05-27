#!/usr/bin/env python3
"""Append a timestamped subsection to a journal entry's Work log.

Body comes from stdin. The script generates the `### YYYY-MM-DD HH:MM`
header from datetime.now (or --at) and appends to the existing
`## Work log` section.

Usage:
    echo "$body" | append.py --slug <slug> [--at "YYYY-MM-DD HH:MM"]

stdout: the timestamp written (e.g. "2026-05-28 01:12")
stderr + non-zero exit on any error

Refuses to append to a closed entry. Refuses if no `## Work log`
section exists (malformed entry).
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402

WORK_LOG_RE = re.compile(r"(?m)^## Work log\s*$")
NEXT_H2_RE = re.compile(r"(?m)^## ")


def main():
    ap = argparse.ArgumentParser(
        description="Append a Work log subsection. Body via stdin."
    )
    ap.add_argument("--slug", required=True, help="bare slug (no date prefix)")
    ap.add_argument("--at", default=None, help="backfill timestamp 'YYYY-MM-DD HH:MM' (default: now)")
    args = ap.parse_args()

    path, meta, body = _lib.load_entry(args.slug)

    if meta.get("status") != "active":
        _lib.die(
            f"entry {args.slug!r} has status={meta.get('status')!r}; cannot append to a non-active entry"
        )

    ts = _lib.parse_at(args.at) if args.at else _lib.now_str()
    subsection_body = _lib.read_stdin_body(required=True, label="Work log body")

    m = WORK_LOG_RE.search(body)
    if not m:
        _lib.die(
            f"entry {args.slug!r} has no `## Work log` section — malformed entry, refuse to write"
        )

    insert_at = _find_insertion_point(body, m.end())
    chunk = f"\n### {ts}\n{subsection_body}\n"
    new_body = body[:insert_at].rstrip() + "\n" + chunk + body[insert_at:].lstrip()
    if not new_body.endswith("\n"):
        new_body += "\n"

    _lib.save_entry(path, meta, new_body)
    _lib.run_reindex()
    print(ts)


def _find_insertion_point(body, work_log_header_end):
    """Find the byte index just before the next H2 (or EOF) after the Work log header."""
    next_h2 = NEXT_H2_RE.search(body, pos=work_log_header_end)
    if next_h2:
        return next_h2.start()
    return len(body)


if __name__ == "__main__":
    main()
