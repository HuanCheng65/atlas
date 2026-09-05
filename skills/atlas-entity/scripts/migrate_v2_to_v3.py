#!/usr/bin/env python3
"""One-time conversion from work units to design documents.

`docs/atlas/work/` held one file per work unit, with Intent, Spec and Plan.
That fixed shape demanded three levels from every interview, including the
rounds that settled a design and reached no implementation. The directory is
renamed to `docs/atlas/design/`, where each file is one round of thinking.

Existing files are moved byte for byte. They are dated accounts of what was
undertaken, and rewriting them into the new shape would fabricate a history
that did not happen; the new skeleton applies to files written from here on.

The store's own README describes the layout being changed, so an untouched
copy of the v2 template is refreshed and an edited one is reported.

    migrate_v2_to_v3.py --dry-run     # report only, touch nothing
    migrate_v2_to_v3.py
"""
import argparse
import hashlib
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402

OLD = _lib.ATLAS / "work"

# The store's README is copied out of `templates/` when the store is created,
# and describes the layout this migration changes. Refreshing it is only safe
# where the project has not touched it, so the v2 template is identified by
# hash and anything else is reported for the user to reconcile.
TEMPLATE = Path(__file__).resolve().parents[3] / "templates" / "README.md"
V2_README_SHA = "6d93fab68ab6d2d0eab0c37ab73bcfea9a635f30dd42f9ec26076c13a48f00c4"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    found = _lib.store_version()
    if found == 3:
        sys.exit(f"{_lib.ATLAS} is already v3.")
    if found != 2:
        sys.exit(f"{_lib.ATLAS} is v{found}; this migration converts v2. "
                 f"Run the migration for that step first.")

    if _lib.DESIGN.exists():
        sys.exit(f"{_lib.DESIGN} already exists; resolve it by hand before "
                 f"running this migration.")

    files = sorted(OLD.glob("*.md")) if OLD.is_dir() else []
    for path in files:
        print(f"{path} -> {_lib.DESIGN / path.name}")
    if not OLD.exists():
        print(f"no {OLD} to move")

    readme = _lib.ATLAS / "README.md"
    stale_readme = readme.is_file() and hashlib.sha256(
        readme.read_bytes()).hexdigest() == V2_README_SHA
    if stale_readme:
        print(f"{readme} is the v2 template and will be refreshed")
    elif readme.is_file():
        print(f"{readme} has local edits and still describes work/ — "
              f"reconcile it against {TEMPLATE}")

    if args.dry_run:
        print("\ndry run: nothing written")
        return

    if OLD.exists():
        shutil.move(str(OLD), str(_lib.DESIGN))
        print(f"\nmoved {len(files)} file(s) to {_lib.DESIGN}")

    if stale_readme:
        shutil.copyfile(TEMPLATE, readme)
        print(f"refreshed {readme}")

    # Stamped last: until it is written the store is still v2, so an
    # interrupted run leaves a store that says so rather than one that lies.
    # The literal 3, not STORE_VERSION: this script converts one step, and the
    # store it leaves is a v3 store however far the scripts later move on.
    _lib.atomic_write(_lib.VERSION_FILE, "3\n")
    print(f"{_lib.VERSION_FILE} now reads 3")

    # This is the last step in the chain, so the index a mid-chain store could
    # not have is built here.
    import reindex  # noqa: E402  (same dir, path set above)
    reindex.build()


if __name__ == "__main__":
    main()
