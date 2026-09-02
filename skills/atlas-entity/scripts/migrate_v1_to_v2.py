#!/usr/bin/env python3
"""One-time conversion from the D/E/Q store to the unified record store.

Renumbers every entity onto one counter, moves the files flat into
`docs/atlas/records/`, rewrites prose `D-007` references as wikilinks, turns
the frontmatter relation fields into typed edges on the record that declares
them, drops the fields the link graph now derives, and moves the journal to
`docs/atlas/archive/journal/` untouched.

Numbering follows the reference graph, not the old ids: a record must be
numbered above everything it cites, or the direction rule fails on arrival.
Where the old store contains a genuine cycle — an older entity edited to
point at a newer one, which is the failure this redesign removes — the cycle
is broken by date and every resulting forward reference is reported for
manual resolution rather than silently rewritten.

    migrate.py --dry-run     # report only, touch nothing
    migrate.py
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402

OLD_DIRS = {"D": "decisions", "E": "experiments", "Q": "questions"}
OLD_ID_RE = re.compile(r"\b([DEQ]-\d{3})\b")

TYPE_NAME = {"D": "decision", "E": "experiment", "Q": "question"}

# `supersedes` already points the right way: it sits on the newer record and
# names the older one, which is the shape the new store wants.
EDGE_FIELDS = {"supersedes": "supersedes"}

# `answered-by` points the wrong way — it sits on the question and names the
# record that answered it. The edge belongs on the answering record, so it is
# converted in reverse and the answerer must outrank the question.
REVERSE_EDGE_FIELDS = {"answered-by": "answers"}

DROP_FIELDS = [
    "status", "related", "superseded-by", "refuted-by", "triage", "affects",
    "source-journal", "severity", "supersedes", "answered-by", "slug", "source",
]

# PROJECT.md's Working rules and Hard constraints end each line with a pointer
# back to the decision that justifies it. The pointers move to wikilinks so the
# constitution keeps working and Obsidian can follow it.
PROJECT_POINTER_RE = re.compile(r"\((D-\d{3})\)")

# Tab-separated so `grep '^E-047' <file>` answers the question outright; the
# title is carried so the answer does not require opening the record.
ID_MAP_HEADER = (
    "# Pre-v2 identifiers and the records they became. Kept permanently:\n"
    "# the migration renumbers, and references written before it survive in\n"
    "# the archived journal and in documents outside docs/atlas/, which are\n"
    "# prose and were deliberately not rewritten.\n"
    "# old\tnew\ttitle\n"
)


class Entity:
    def __init__(self, old_id, path, meta, body):
        self.old_id = old_id
        self.path = path
        self.meta = meta
        self.body = body
        # The old slugifier truncated at a fixed character count, which left
        # some slugs ending in a hyphen or a doubled one mid-word.
        self.slug = re.sub(r"-+", "-", path.stem.split("-", 2)[2]).strip("-")
        self.date = str(meta.get("date") or "")
        self.new_id = None


def load_old():
    entities = {}
    for letter, dirname in OLD_DIRS.items():
        d = _lib.ATLAS / dirname
        if not d.exists():
            continue
        for path in sorted(d.glob(f"{letter}-*.md")):
            meta, body = _lib.parse_md(path.read_text(encoding="utf-8"))
            old_id = meta.get("id") or path.stem.rsplit("-", 1)[0]
            entities[old_id] = Entity(old_id, path, meta, body)
    return entities


def outgoing_refs(entity, known):
    """The entities this one will still point at after conversion: prose
    mentions plus the two relation fields that become typed edges.

    `related` and the reverse halves of supersedes/refutes are excluded — they
    are dropped rather than converted, so constraining the numbering by them
    would invent cycles that the new store never has.
    """
    refs = set(OLD_ID_RE.findall(entity.body)) & set(known)
    for field in EDGE_FIELDS:
        value = entity.meta.get(field)
        if isinstance(value, str):
            value = [value]
        for r in value or []:
            if r in known:
                refs.add(r)
    refs.discard(entity.old_id)
    return refs


def reverse_refs(entities):
    """{answerer old id: {question old id}} from the questions' `answered-by`.

    The edge runs from the answerer to the question, so the answerer must be
    numbered above it — the same constraint every other reference imposes,
    just declared from the far end."""
    out = {}
    for oid, e in entities.items():
        for field in REVERSE_EDGE_FIELDS:
            value = e.meta.get(field)
            if isinstance(value, str):
                value = [value]
            for target in value or []:
                if target in entities:
                    out.setdefault(target, set()).add(oid)
    return out


def order(entities):
    """Number cited records first. Kahn's algorithm over the reference graph,
    with (date, old id) breaking ties so the result is stable and roughly
    chronological; on a cycle, fall back to date order for what remains."""
    known = set(entities)
    deps = {oid: outgoing_refs(e, known) for oid, e in entities.items()}
    for answerer, questions in reverse_refs(entities).items():
        deps[answerer] |= questions
    dependents = {oid: set() for oid in entities}
    for oid, targets in deps.items():
        for t in targets:
            dependents[t].add(oid)

    remaining = dict(deps)
    sort_key = lambda oid: (entities[oid].date, oid)  # noqa: E731
    ordered, cyclic = [], False
    while remaining:
        ready = sorted((oid for oid, d in remaining.items() if not d), key=sort_key)
        if not ready:
            cyclic = True
            ready = [min(remaining, key=sort_key)]
        for oid in ready:
            ordered.append(oid)
            remaining.pop(oid)
            for dep in dependents[oid]:
                remaining.get(dep, set()).discard(oid)
    return ordered, cyclic


def convert(entity, id_map, stem_map, answers):
    meta = dict(entity.meta)
    body = entity.body

    edges = []
    for field, verb in EDGE_FIELDS.items():
        value = meta.get(field)
        if isinstance(value, str):
            value = [value]
        for target in value or []:
            if target in stem_map:
                edges.append(f"({verb}:: [[{stem_map[target]}]])")
    for question in sorted(answers.get(entity.old_id, ())):
        edges.append(f"(answers:: [[{stem_map[question]}]])")

    for field in DROP_FIELDS:
        meta.pop(field, None)

    meta.pop("id", None)
    new_meta = {
        "id": entity.new_id,
        "title": meta.pop("title", entity.slug),
        "date": meta.pop("date", ""),
        "type": TYPE_NAME[entity.old_id.split("-")[0]],
        "tags": meta.pop("tags", None) or [],
    }
    # Experiment summaries and anything else the old record carried follow the
    # identity block in declaration order; validate decides whether they belong.
    new_meta.update(meta)

    body = OLD_ID_RE.sub(
        lambda m: f"[[{stem_map[m.group(1)]}]]" if m.group(1) in stem_map else m.group(1),
        body,
    )
    if edges:
        body = body.rstrip() + "\n\n" + " ".join(edges) + "\n"

    return new_meta, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # The one script that must not call require_version: it is what fixes the
    # mismatch. It asserts the opposite instead.
    found = _lib.store_version()
    if found != 1:
        sys.exit(f"ERROR: {_lib.ATLAS} is already v{found} — this migration is v1 to v2")

    entities = load_old()
    if not entities:
        sys.exit("ERROR: no D/E/Q entities found — nothing to migrate")

    ordered, cyclic = order(entities)
    for n, oid in enumerate(ordered, start=1):
        entities[oid].new_id = n

    id_map = {oid: e.new_id for oid, e in entities.items()}
    stem_map = {oid: _lib.format_stem(e.new_id, e.slug) for oid, e in entities.items()}

    answers = reverse_refs(entities)

    forward = []
    for oid, e in entities.items():
        targets = outgoing_refs(e, set(entities)) | answers.get(oid, set())
        for target in targets:
            if id_map[target] > e.new_id:
                forward.append((stem_map[oid], stem_map[target]))

    overlong = [(stem_map[oid], _lib.display_width(str(e.meta.get("title", ""))))
                for oid, e in entities.items()
                if _lib.display_width(str(e.meta.get("title", ""))) > 90]

    print(f"{len(entities)} entities -> records 001..{len(entities):03d}"
          + (" (reference cycle broken by date)" if cyclic else ""))
    if forward:
        print(f"\n{len(forward)} forward reference(s) need manual resolution — the older "
              f"record cites a newer one, which the new store does not allow:")
        for src, dst in sorted(forward):
            print(f"  {src} -> {dst}")
    if overlong:
        print(f"\n{len(overlong)} title(s) over the 90-column budget, to be split or tightened:")
        for stem, width in sorted(overlong, key=lambda kv: -kv[1]):
            print(f"  {width:>4}  {stem}")

    if args.dry_run:
        return

    _lib.RECORDS.mkdir(parents=True, exist_ok=True)
    for oid, e in entities.items():
        meta, body = convert(e, id_map, stem_map, answers)
        _lib.atomic_write(_lib.RECORDS / f"{stem_map[oid]}.md", _lib.dump_md(meta, body))

    project = Path("PROJECT.md")
    if project.exists():
        text = project.read_text(encoding="utf-8")
        rewritten, n = PROJECT_POINTER_RE.subn(
            lambda m: f"([[{stem_map[m.group(1)]}]])" if m.group(1) in stem_map else m.group(0),
            text,
        )
        if n:
            _lib.atomic_write(project, rewritten)
            print(f"rewrote {n} constitution pointer(s) in PROJECT.md")

    for dirname in OLD_DIRS.values():
        shutil.rmtree(_lib.ATLAS / dirname, ignore_errors=True)
    # `_templates` is gone because new.py writes the file itself, and `topics`
    # was a journal-distillation surface with nothing left to distil.
    for stale in ("_templates", "topics"):
        shutil.rmtree(_lib.ATLAS / stale, ignore_errors=True)

    _lib.ID_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    rows = "".join(
        f"{oid}\t{stem_map[oid]}\t{entities[oid].meta.get('title', '')}\n"
        for oid in sorted(entities, key=lambda o: id_map[o])
    )
    _lib.atomic_write(_lib.ID_MAP_FILE, ID_MAP_HEADER + rows)
    print(f"wrote {len(entities)} identifier mappings to {_lib.ID_MAP_FILE}")

    journal = _lib.ATLAS / "journal"
    if journal.exists():
        archive = _lib.ATLAS / "archive"
        archive.mkdir(parents=True, exist_ok=True)
        shutil.move(str(journal), str(archive / "journal"))
        print(f"\njournal archived to {archive / 'journal'} unchanged")

    # Stamped last: until it is written the store is still v1, so an
    # interrupted run leaves a store that says so rather than one that lies.
    _lib.atomic_write(_lib.VERSION_FILE, f"{_lib.STORE_VERSION}\n")

    import reindex  # noqa: E402  (same dir, path set above)
    reindex.build()


if __name__ == "__main__":
    main()
