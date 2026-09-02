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

# A backticked path with a directory separator and an extension: specific
# enough that a false positive is rare and a real dead reference is caught.
PATH_RE = re.compile(r"`([\w./-]+/[\w.-]+\.\w{1,6})`")


def parse_day(value):
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


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

    print("## Tags used once")
    counts = defaultdict(int)
    for rec in records.values():
        for tag in rec.meta.get("tags") or []:
            counts[tag] += 1
    singletons = sorted(t for t, n in counts.items() if n == 1)
    print(", ".join(singletons) if singletons else "*(none)*")


if __name__ == "__main__":
    main()
