#!/usr/bin/env python3
"""Print a maintenance agenda for an atlas-compact run.

Usage:
    scan.py [--stale-days 3] [--cluster-min 3] [--today YYYY-MM-DD]

Collects, mechanically, everything a compact run should look at:

  1. Stale active journal entries (no work-log activity past the threshold)
  2. Decisions pending triage
  3. Open questions, with ages
  4. Possibly-answered hints: open questions whose tags overlap journal
     entries closed after the question was raised
  5. Decision-overlap hints: active decision pairs sharing >= 2 tags
  6. Tag clusters over closed journal entries (topic candidates), with
     existing topics listed for comparison
  7. Last compact run (the latest closed journal entry tagged `compact`)

The agenda is data, not verdicts — what to do about each item is the
judgment half of compact, which the agent does. `--today` exists for
deterministic tests; default is the real date.

Must be run from project root. Read-only: writes nothing.
"""
import argparse
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import yaml

ATLAS = Path("docs/atlas")

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
WORKLOG_TS_RE = re.compile(r"(?m)^### (\d{4}-\d{2}-\d{2}) \d{2}:\d{2}\s*$")


def parse_md(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}, text
    return meta, m.group(2)


def load_files(subdir, glob_pattern):
    d = ATLAS / subdir
    if not d.exists():
        return []
    out = []
    for p in sorted(d.glob(glob_pattern)):
        if p.name.startswith("_"):
            continue
        meta, body = parse_md(p.read_text(encoding="utf-8"))
        if meta:
            out.append((meta, body, p))
    return out


def parse_day(value):
    s = str(value or "").strip()
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def last_activity(meta, body):
    """Most recent known activity date: latest work-log header, else opened/date."""
    days = [d for d in (parse_day(ts) for ts in WORKLOG_TS_RE.findall(body)) if d]
    opened = parse_day(meta.get("opened") or meta.get("date"))
    if opened:
        days.append(opened)
    return max(days) if days else None


def main():
    ap = argparse.ArgumentParser(description="Print a compact maintenance agenda.")
    ap.add_argument("--stale-days", type=int, default=3,
                    help="active entries without activity for this many days are stale")
    ap.add_argument("--cluster-min", type=int, default=3,
                    help="closed entries sharing a tag to flag it as a topic candidate")
    ap.add_argument("--today", default=None,
                    help="override today's date (YYYY-MM-DD) — for deterministic tests")
    args = ap.parse_args()

    if not ATLAS.exists():
        print("ERROR: docs/atlas/ not found — run from project root", file=sys.stderr)
        sys.exit(1)

    today = parse_day(args.today) if args.today else date.today()
    if args.today and today is None:
        print(f"ERROR: --today must be YYYY-MM-DD, got {args.today!r}", file=sys.stderr)
        sys.exit(1)

    journal = load_files("journal", "*.md")
    decisions = load_files("decisions", "D-*.md")
    questions = load_files("questions", "Q-*.md")
    actives = [(m, b, p) for m, b, p in journal if m.get("status") == "active"]
    closed = [(m, b, p) for m, b, p in journal if m.get("status") == "closed"]

    out = ["# Compact agenda", ""]

    # 1. stale actives
    stale = []
    for meta, body, p in actives:
        last = last_activity(meta, body)
        if last and (today - last).days >= args.stale_days:
            stale.append((meta, p, (today - last).days))
    out.append(f"## Stale active entries (>= {args.stale_days} days quiet): {len(stale)}")
    for meta, p, age in sorted(stale, key=lambda x: -x[2]):
        out.append(f"- [{p.stem}]({p.name}) — quiet for {age} days")
    out.append("")

    # 2. pending triage
    pending = [(m, p) for m, _, p in decisions
               if m.get("status") in ("active", "planned")
               and m.get("triage", "pending") == "pending"]
    out.append(f"## Decisions pending triage: {len(pending)}")
    for meta, p in pending:
        out.append(f"- **{meta.get('id')}** {meta.get('title')} — {meta.get('date')}")
    out.append("")

    # 3. open questions with ages
    open_qs = [(m, p) for m, _, p in questions if m.get("status") == "open"]
    out.append(f"## Open questions: {len(open_qs)}")
    for meta, p in open_qs:
        raised = parse_day(meta.get("date"))
        age = f"{(today - raised).days} days old" if raised else "age unknown"
        out.append(f"- **{meta.get('id')}** {meta.get('title')} — {age}")
    out.append("")

    # 4. possibly-answered hints
    hints = []
    for meta, _, p in questions:
        if meta.get("status") != "open":
            continue
        q_tags = set(meta.get("tags") or [])
        q_date = parse_day(meta.get("date"))
        if not q_tags or not q_date:
            continue
        for jmeta, _, jp in closed:
            j_closed = parse_day(jmeta.get("closed") or jmeta.get("date"))
            overlap = q_tags & set(jmeta.get("tags") or [])
            if j_closed and j_closed > q_date and overlap:
                hints.append((meta.get("id"), jp.stem, sorted(overlap)))
    out.append(f"## Possibly answered (open question vs later closed work): {len(hints)}")
    for qid, stem, overlap in hints:
        out.append(f"- {qid} ↔ {stem} — shared tags: {', '.join(overlap)}")
    out.append("")

    # 5. decision-overlap hints
    live = [(m, p) for m, _, p in decisions if m.get("status") == "active"]
    pairs = []
    for i in range(len(live)):
        for j in range(i + 1, len(live)):
            shared = set(live[i][0].get("tags") or []) & set(live[j][0].get("tags") or [])
            if len(shared) >= 2:
                pairs.append((live[i][0].get("id"), live[j][0].get("id"), sorted(shared)))
    out.append(f"## Decision pairs sharing >= 2 tags (merge candidates?): {len(pairs)}")
    for a, b, shared in pairs:
        out.append(f"- {a} + {b} — shared tags: {', '.join(shared)}")
    out.append("")

    # 6. tag clusters over closed journal entries
    by_tag = defaultdict(list)
    for meta, _, p in closed:
        for tag in meta.get("tags") or []:
            by_tag[tag].append(p.stem)
    topics = sorted(p.stem for p in (ATLAS / "topics").glob("*.md")) \
        if (ATLAS / "topics").exists() else []
    candidates = {t: v for t, v in by_tag.items() if len(v) >= args.cluster_min}
    out.append(f"## Tag clusters over closed entries (topic candidates at >= {args.cluster_min}): "
               f"{len(candidates)}")
    for tag in sorted(candidates, key=lambda t: -len(by_tag[t])):
        out.append(f"- **{tag}** ({len(by_tag[tag])}): {', '.join(by_tag[tag])}")
    if topics:
        out.append(f"- existing topics: {', '.join(topics)}")
    else:
        out.append("- existing topics: (none)")
    out.append("")

    # 7. last compact run
    compact_runs = [parse_day(m.get("closed") or m.get("date"))
                    for m, _, _ in closed if "compact" in (m.get("tags") or [])]
    compact_runs = [d for d in compact_runs if d]
    last_run = max(compact_runs).isoformat() if compact_runs else "never"
    out.append(f"## Last compact run: {last_run}")
    out.append("")

    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
