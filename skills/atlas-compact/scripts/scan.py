#!/usr/bin/env python3
"""Compute the candidate list for a compact run.

Compact is two jobs. Consolidating the memory records, which are loaded into
every session and therefore have a budget; and reviewing the store for records
that have quietly stopped being true. Neither job should read the whole store —
the shortlist is computed here so the agent only opens what the signals point
at.

Every signal below is mechanical. Whether a candidate is really stale is the
one part that needs judgment, and it stays with the agent.

Usage:
    scan.py
"""
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "atlas-entity" / "scripts"))
import _lib  # noqa: E402
import links  # noqa: E402

# Memory titles are loaded into every session. The number is a budget, not a
# limit on what may be known — a record dropped from memory still exists in the
# store, it just stops being preloaded.
MEMORY_BUDGET = 40

QUIET_DAYS = 120
OVERLAP_THRESHOLD = 0.5

# The scope of a change is the readable form of "does a requirement map to a
# bounded edit". Nobody feels the interest on this the way a developer feels a
# slow build, so it is measured rather than noticed.
CHANGE_WINDOW = 30
WIDE_CHANGE = 8
COUPLING_MIN = 5
COUPLING_RATIO = 0.6
COUPLING_SHORTLIST = 8

# A backticked path with a directory separator and an extension: specific
# enough that a false positive is rare and a real dead reference is caught.
PATH_RE = re.compile(r"`([\w./-]+/[\w.-]+\.\w{1,6})`")


def parse_day(value):
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def leaked_links():
    """Record links written into documents the store does not own.

    A number means nothing to a reader who is not holding the store, and it
    stops meaning anything at all once the store is renumbered. Markdown only:
    a wikilink is a markdown construct, and an identifier appearing in code or
    in a filename is a name rather than a reference.
    """
    listed = subprocess.run(["git", "ls-files", "-z", "*.md"],
                            capture_output=True, text=True)
    if listed.returncode != 0:
        return {}

    found = defaultdict(set)
    for name in listed.stdout.split("\0"):
        path = Path(name) if name else None
        if path is None or path == Path("PROJECT.md") or _lib.ATLAS in path.parents:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for stem in links.WIKILINK_RE.findall(links.strip_code(text)):
            if _lib.STEM_RE.match(stem.strip()):
                found[str(path)].add(stem.strip())
    return found


def recent_changes(window=CHANGE_WINDOW):
    """Files touched per commit, over the last `window` commits.

    The store's own files are excluded. Records changing alongside the code
    they describe is the design working, not coupling.
    """
    listed = subprocess.run(
        ["git", "log", f"-n{window}", "--no-merges", "--name-only",
         "--format=\x01%h %s"],
        capture_output=True, text=True)
    if listed.returncode != 0:
        return []

    commits = []
    for line in listed.stdout.splitlines():
        if line.startswith("\x01"):
            commits.append((line[1:], set()))
        elif line.strip() and commits:
            path = Path(line.strip())
            if _lib.ATLAS not in path.parents and path != Path("PROJECT.md"):
                commits[-1][1].add(line.strip())
    return [(subject, files) for subject, files in commits if files]


def coupled_files(commits):
    """Pairs that nearly always change together.

    A pair like this is one decision spread across two places: the fact they
    share is stated twice, so every change to it has to be made twice.
    """
    appearances = defaultdict(int)
    together = defaultdict(int)
    for _, files in commits:
        listing = sorted(files)
        for name in listing:
            appearances[name] += 1
        for i, a in enumerate(listing):
            for b in listing[i + 1:]:
                together[(a, b)] += 1

    found = []
    for (a, b), n in together.items():
        if n < COUPLING_MIN:
            continue
        # Over the union, not over the smaller of the two: dividing by the
        # smaller count scores every rare file that happened to ride along with
        # a file which changes constantly, which is most of them.
        ratio = n / (appearances[a] + appearances[b] - n)
        if ratio >= COUPLING_RATIO:
            found.append((ratio, n, a, b))
    return sorted(found, reverse=True)[:COUPLING_SHORTLIST]


def neighbourhood(rid, mentions, incoming):
    return set(mentions.get(rid, [])) | set(incoming.get(rid, []))


def main():
    _lib.require_version()
    records = _lib.load_all()
    if not records:
        print("no records")
        return
    mentions, edges, _ = links.graph(records)
    state = links.derive_state(records, edges)
    incoming = links.backlinks(mentions)
    today = date.today()

    print(f"# Compact scan — {len(records)} records\n")

    memory = [r for r in records.values() if r.type == "memory"]
    print(f"## Memory budget: {len(memory)} / {MEMORY_BUDGET}")
    if len(memory) > MEMORY_BUDGET:
        print(f"over budget by {len(memory) - MEMORY_BUDGET} — merge overlapping "
              f"constraints and drop the ones no longer in force")
    quiet_memory = [r for r in memory
                    if (parse_day(r.meta.get("date")) or today) < today.replace(
                        year=today.year - 1)]
    for r in sorted(quiet_memory, key=lambda r: r.id):
        print(f"- untouched for over a year: [[{r.stem}]] {r.title}")
    print()

    print("## Questions with no answering record")
    open_qs = [r for r in records.values()
               if r.type == "question" and r.id not in state]
    aged = sorted(
        ((r, (today - d).days) for r in open_qs
         if (d := parse_day(r.meta.get("date")))),
        key=lambda kv: -kv[1],
    )
    for r, age in aged:
        cited = len(incoming.get(r.id, []))
        mark = " — quiet" if age > QUIET_DAYS and cited == 0 else ""
        print(f"- {age:>4}d, cited by {cited}: [[{r.stem}]] {r.title}{mark}")
    if not aged:
        print("*(none)*")
    print()

    print("## Records sharing most of their neighbourhood")
    pairs = []
    ids = sorted(records)
    for i, a in enumerate(ids):
        na = neighbourhood(a, mentions, incoming)
        if len(na) < 2:
            continue
        for b in ids[i + 1:]:
            nb = neighbourhood(b, mentions, incoming)
            if len(nb) < 2:
                continue
            union = (na | nb) - {a, b}
            if not union:
                continue
            overlap = len((na & nb) - {a, b}) / len(union)
            if overlap >= OVERLAP_THRESHOLD and records[a].type == records[b].type:
                pairs.append((overlap, a, b))
    for overlap, a, b in sorted(pairs, reverse=True):
        print(f"- {overlap:.0%}: [[{records[a].stem}]] / [[{records[b].stem}]]")
    if not pairs:
        print("*(none)*")
    print()

    print("## Records citing paths that no longer exist")
    dead = defaultdict(list)
    for rid, rec in sorted(records.items()):
        for candidate in set(PATH_RE.findall(rec.body)):
            if not Path(candidate).exists():
                dead[rid].append(candidate)
    for rid, paths in dead.items():
        print(f"- [[{records[rid].stem}]] — {', '.join(sorted(paths))}")
    if not dead:
        print("*(none)*")
    print()

    print("## Record links written outside the store")
    escaped = leaked_links()
    for path, stems in sorted(escaped.items()):
        print(f"- `{path}` — {', '.join(sorted(stems))}")
    if not escaped:
        print("*(none)*")
    print()

    print("## Tags used once")
    counts = defaultdict(int)
    for rec in records.values():
        for tag in rec.meta.get("tags") or []:
            counts[tag] += 1
    singletons = sorted(t for t, n in counts.items() if n == 1)
    print(", ".join(singletons) if singletons else "*(none)*")
    print()

    commits = recent_changes()
    print(f"## The scope of the last {len(commits)} changes")
    if commits:
        sizes = sorted(len(files) for _, files in commits)
        print(f"median {sizes[len(sizes) // 2]} files per commit, "
              f"widest {sizes[-1]}")
        wide = [(len(files), subject) for subject, files in commits
                if len(files) > WIDE_CHANGE]
        for count, subject in sorted(wide, reverse=True):
            print(f"- {count} files: {subject}")
    else:
        print("*(no history)*")
    print()

    print("## Files that change together")
    coupled = coupled_files(commits)
    for ratio, n, a, b in coupled:
        print(f"- {ratio:.0%} of the time ({n}×): `{a}` + `{b}`")
    if not coupled:
        print("*(none)*")


if __name__ == "__main__":
    main()
