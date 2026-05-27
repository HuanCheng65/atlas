"""Wire bidirectional supersedes between two decisions.

Usage:
    supersede.py D-009 D-012
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    old_id, new_id = sys.argv[1], sys.argv[2]
    if not (old_id.startswith("D-") and new_id.startswith("D-")):
        sys.exit("ERROR: supersede only applies to decisions")

    old_path, old_meta, old_body = _lib.load_entity(old_id)
    new_path, new_meta, new_body = _lib.load_entity(new_id)

    _lib.ensure_list(old_meta, "superseded-by")
    _lib.ensure_list(new_meta, "supersedes")

    if new_id not in old_meta["superseded-by"]:
        old_meta["superseded-by"].append(new_id)
    if old_id not in new_meta["supersedes"]:
        new_meta["supersedes"].append(old_id)

    old_meta["status"] = "superseded"

    _lib.save_entity(old_path, old_meta, old_body)
    _lib.save_entity(new_path, new_meta, new_body)

    print(f"{old_id}: status=superseded, superseded-by += {new_id}")
    print(f"{new_id}: supersedes += {old_id}")


if __name__ == "__main__":
    main()
