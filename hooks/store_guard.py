#!/usr/bin/env python3
"""Validate the record store after anything that could have written to it.

Derived state is only as good as the links it is derived from. A typed edge
whose target does not resolve is not an error anywhere — it is simply a link
that matches nothing, so the supersede it was meant to express silently does
not happen and the index keeps showing the old record as current. Nothing
about that is visible at the moment it is written.

The check cannot live in the script that creates records, because most writes
to the store are not that script: memory records are rewritten in place, typed
edges are appended to already-published records, and consolidation rewrites the
memory set wholesale. All of those are ordinary file edits.

So it runs after the fact, over the whole store, on every tool call that could
have touched it. A fingerprint of the record files short-circuits the common
case, and is updated even when validation fails, so one broken state is
reported once rather than on every subsequent command.
"""
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "atlas-entity" / "scripts"
RECORDS = Path("docs/atlas/records")


def fingerprint():
    """Identity of the store's contents, cheap enough to compute every call.

    `_index.md` is excluded because it is derived: regenerating it must not
    look like a change to the thing it was derived from.
    """
    parts = []
    for path in sorted(RECORDS.glob("*.md")):
        if path.name == "_index.md":
            continue
        stat = path.stat()
        parts.append(f"{path.name}\t{stat.st_mtime_ns}\t{stat.st_size}")
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def cache_file():
    # Keyed by project, outside the repository: losing it costs one extra
    # validation, so a wiped temp directory needs no handling of its own.
    key = hashlib.sha256(str(Path.cwd()).encode("utf-8")).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / f"atlas-store-guard-{key}"


def run(script):
    return subprocess.run([sys.executable, str(SCRIPTS / script)],
                          capture_output=True, text=True)


def main():
    if not RECORDS.is_dir():
        return 0

    cache = cache_file()
    current = fingerprint()
    if cache.exists() and cache.read_text(encoding="utf-8").strip() == current:
        return 0

    checked = run("validate.py")
    if checked.returncode != 0:
        cache.write_text(current + "\n", encoding="utf-8")
        sys.stderr.write(checked.stdout + checked.stderr)
        sys.stderr.write(
            "\nThe record store does not validate. Links resolve by filename and "
            "derived state is computed from them, so a link that matches nothing "
            "is not an error later — it is a relation that never takes effect. "
            "Fix this before committing.\n")
        return 2

    run("reindex.py")
    cache.write_text(fingerprint() + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
