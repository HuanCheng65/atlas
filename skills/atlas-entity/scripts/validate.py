#!/usr/bin/env python3
"""Validate atlas entities: orphan refs, bidirectional consistency, frontmatter.

Usage:
    validate.py

Exits non-zero on any error.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402

ALL_TYPES = ["D", "E", "Q"]

VALID_STATUS = {
    "D": {"planned", "active", "superseded", "rejected"},
    "E": {"planned", "running", "completed", "abandoned"},
    "Q": {"open", "answered", "wontfix", "merged-into-D"},
}

REQUIRED_BASE = ["id", "title", "date", "status", "tags", "related", "source-journal"]
REQUIRED_BY_TYPE = {
    "D": ["supersedes", "superseded-by", "affects"],
    "E": ["hypothesis", "config", "result", "artifacts", "conclusion"],
    "Q": ["severity", "answered-by"],
}


def load_all():
    entities = {}
    for t in ALL_TYPES:
        d = _lib.ATLAS / _lib.TYPE_DIR[t]
        if not d.exists():
            continue
        for p in d.glob(f"{t}-*.md"):
            meta, _ = _lib.parse_md(p.read_text(encoding="utf-8"))
            eid = meta.get("id") or p.stem.rsplit("-", 1)[0]
            entities[eid] = (p, meta)
    return entities


def main():
    entities = load_all()
    errors = []

    def err(msg):
        errors.append(msg)

    # required fields + status legality
    for eid, (path, meta) in entities.items():
        t = eid.split("-")[0]
        for field in REQUIRED_BASE + REQUIRED_BY_TYPE.get(t, []):
            if field not in meta:
                err(f"{eid}: missing required field `{field}` ({path.name})")
        status = meta.get("status")
        if status is not None and status not in VALID_STATUS.get(t, set()):
            err(f"{eid}: illegal status `{status}` for type {t}")

    # reference checks
    def check_refs(eid, meta, key):
        refs = meta.get(key) or []
        if isinstance(refs, str):
            refs = [refs]
        for r in refs:
            if r is None:
                continue
            if r.endswith(".md") or "/" in r:
                jpath = _lib.ATLAS / "journal" / r if not r.startswith("journal/") else _lib.ATLAS / r
                if not jpath.exists():
                    err(f"{eid}.{key}: journal not found: {r}")
                continue
            if r not in entities:
                err(f"{eid}.{key}: references missing entity `{r}`")

    for eid, (_, meta) in entities.items():
        t = eid.split("-")[0]
        check_refs(eid, meta, "related")
        if meta.get("source-journal"):
            check_refs(eid, meta, "source-journal")
        if t == "D":
            check_refs(eid, meta, "supersedes")
            check_refs(eid, meta, "superseded-by")
        if t == "Q" and meta.get("answered-by"):
            check_refs(eid, meta, "answered-by")

    # bidirectional supersedes consistency
    for eid, (_, meta) in entities.items():
        if not eid.startswith("D-"):
            continue
        for target in meta.get("supersedes") or []:
            tgt = entities.get(target)
            if tgt and eid not in (tgt[1].get("superseded-by") or []):
                err(f"{eid} supersedes {target} but {target}.superseded-by omits {eid}")
        for target in meta.get("superseded-by") or []:
            tgt = entities.get(target)
            if tgt and eid not in (tgt[1].get("supersedes") or []):
                err(f"{eid} superseded-by {target} but {target}.supersedes omits {eid}")

    # status final-state invariants
    for eid, (_, meta) in entities.items():
        if meta.get("status") == "superseded" and not (meta.get("superseded-by") or []):
            err(f"{eid}: status=superseded but superseded-by is empty")
        if meta.get("status") == "merged-into-D":
            ab = meta.get("answered-by")
            if not (isinstance(ab, str) and ab.startswith("D-")):
                err(f"{eid}: status=merged-into-D but answered-by is not a D-id ({ab!r})")

    if errors:
        print(f"\n{len(errors)} error(s):\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"OK ({len(entities)} entities checked)")


if __name__ == "__main__":
    main()
