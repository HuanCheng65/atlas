#!/usr/bin/env python3
"""Validate atlas entities: orphan refs, bidirectional consistency, frontmatter,
the PROJECT.md constitution pairing (triage: promoted ⟺ a `(D-NNN)` pointer
in PROJECT.md; every pointer resolves to an existing, active decision), and
the frontmatter/body split (E content fields are one-line machine summaries,
capped in length; bodies own the full prose and may not point at frontmatter).

Usage:
    validate.py

Exits non-zero on any error.
"""
import re
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

VALID_TRIAGE = {"pending", "promoted", "archival"}

# A constitution pointer is `(D-NNN)` in PROJECT.md (any section — Hard
# constraints lines carry pointers too, not just Working rules).
POINTER_RE = re.compile(r"\((D-\d{3})\)")

REQUIRED_BASE = ["id", "title", "date", "status", "tags", "related", "source-journal"]
REQUIRED_BY_TYPE = {
    "D": ["supersedes", "superseded-by", "affects", "triage"],
    "E": ["hypothesis", "config", "result", "artifacts", "conclusion"],
    "Q": ["severity", "answered-by"],
}

# E content fields are machine summaries scanned without loading the body;
# the body sections own the full prose. The cap keeps them one-liners.
E_SUMMARY_FIELDS = ["hypothesis", "config", "result", "conclusion"]
MAX_SUMMARY_LEN = 300

# Bodies are the canonical prose — a section that says "见 frontmatter" /
# "see frontmatter" instead of its content is a hole in the record.
FRONTMATTER_POINTER_RE = re.compile(r"见\s*frontmatter|see\s+frontmatter", re.IGNORECASE)


def string_leaves(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from string_leaves(v)
    elif isinstance(value, list):
        for v in value:
            yield from string_leaves(v)


def load_all():
    entities = {}
    bodies = {}
    for t in ALL_TYPES:
        d = _lib.ATLAS / _lib.TYPE_DIR[t]
        if not d.exists():
            continue
        for p in d.glob(f"{t}-*.md"):
            meta, body = _lib.parse_md(p.read_text(encoding="utf-8"))
            eid = meta.get("id") or p.stem.rsplit("-", 1)[0]
            entities[eid] = (p, meta)
            bodies[eid] = body
    return entities, bodies


def main():
    entities, bodies = load_all()
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
        if t == "D":
            triage = meta.get("triage")
            if triage is not None and triage not in VALID_TRIAGE:
                err(f"{eid}: illegal triage `{triage}` (must be one of {sorted(VALID_TRIAGE)})")
        if t == "E":
            for field in E_SUMMARY_FIELDS:
                for s in string_leaves(meta.get(field)):
                    if len(s) > MAX_SUMMARY_LEN:
                        err(f"{eid}.{field}: {len(s)}-char value exceeds {MAX_SUMMARY_LEN} — "
                            f"frontmatter fields are one-line machine summaries; "
                            f"full prose belongs in the body")
                        break

    # bodies own the prose — no "见 frontmatter" placeholders
    for eid, body in bodies.items():
        if FRONTMATTER_POINTER_RE.search(body):
            err(f"{eid}: body points at frontmatter instead of stating its content — "
                f"the body is the canonical prose; write it out")

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

    # constitution pairing: triage: promoted ⟺ (D-NNN) pointer in PROJECT.md
    project_path = Path("PROJECT.md")
    project_md = project_path.read_text(encoding="utf-8") if project_path.exists() else None
    pointers = set(POINTER_RE.findall(project_md)) if project_md else set()

    promoted = {
        eid for eid, (_, meta) in entities.items()
        if eid.startswith("D-") and meta.get("triage") == "promoted"
    }
    if promoted and project_md is None:
        err(f"decisions marked promoted ({', '.join(sorted(promoted))}) but PROJECT.md not found")
    for eid in sorted(promoted - pointers):
        err(f"{eid}: triage=promoted but PROJECT.md has no ({eid}) pointer")
    for eid in sorted(pointers - promoted):
        if eid not in entities:
            err(f"PROJECT.md points at ({eid}) but no such decision exists")
        else:
            err(f"PROJECT.md points at ({eid}) but its triage is "
                f"{entities[eid][1].get('triage')!r}, not promoted")
    for eid in sorted(pointers & promoted):
        if entities[eid][1].get("status") != "active":
            err(f"PROJECT.md points at ({eid}) but its status is "
                f"{entities[eid][1].get('status')!r}, not active — update the constitution line")

    if errors:
        print(f"\n{len(errors)} error(s):\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"OK ({len(entities)} entities checked)")


if __name__ == "__main__":
    main()
