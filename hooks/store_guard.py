#!/usr/bin/env python3
"""Validate the record store after a tool call that changed it.

Derived state is only as good as the links it is derived from. A typed edge
whose target does not resolve is not an error anywhere — it is simply a link
that matches nothing, so the supersede it was meant to express silently does
not happen and the index keeps showing the old record as current. Nothing
about that is visible at the moment it is written.

The check cannot live in the script that creates records, because most writes
to the store are not that script: memory records are rewritten in place, typed
edges are appended to already-published records, and consolidation rewrites the
memory set wholesale. All of those are ordinary file edits.

So it runs after the fact, over the whole store, comparing a fingerprint
against the one session start recorded. Two things follow from that comparison
being the trigger. A tool call that changed nothing says nothing, and a problem
that predates the session is not reported here at all — this channel says "what
you just did broke something", and pinning a pre-existing state on an unrelated
command is a false accusation the reader has no way to check.
"""
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN / "skills" / "atlas-entity" / "scripts"))
import _lib  # noqa: E402

SCRIPTS = PLUGIN / "skills" / "atlas-entity" / "scripts"


def run(script):
    return subprocess.run([sys.executable, str(SCRIPTS / script)],
                          capture_output=True, text=True)


def main():
    if not _lib.RECORDS.is_dir():
        return 0

    # A store in an older format is a condition of the project, not of the
    # command that just ran. Session start reports it once, in words that fit;
    # repeating it here on every call would attribute it to whoever typed
    # something.
    if _lib.version_complaint():
        return 0

    cache = _lib.fingerprint_cache()
    current = _lib.fingerprint()
    if not cache.exists():
        # No baseline: session start did not run, or the temp file is gone.
        # Record where things stand rather than blaming this call for it.
        cache.write_text(current + "\n", encoding="utf-8")
        return 0
    if cache.read_text(encoding="utf-8").strip() == current:
        return 0

    checked = run("validate.py")
    if checked.returncode != 0:
        # Cached even on failure, so one broken state is reported once rather
        # than after every command until it is fixed.
        cache.write_text(current + "\n", encoding="utf-8")
        sys.stderr.write(checked.stdout + checked.stderr)
        sys.stderr.write(
            "\nThe record store does not validate. Links resolve by filename and "
            "derived state is computed from them, so a link that matches nothing "
            "is not an error later — it is a relation that never takes effect. "
            "Fix this before committing.\n")
        return 2

    run("reindex.py")
    cache.write_text(_lib.fingerprint() + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
