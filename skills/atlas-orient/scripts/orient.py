#!/usr/bin/env python3
"""Load atlas state and print a navigator summary for session start.

Usage:
    orient.py

Reads:
  PROJECT.md (project root)
  docs/atlas/ROADMAP.md
  docs/atlas/{decisions,questions,experiments}/   — entity frontmatter + bodies
  docs/atlas/journal/                              — entry frontmatter + bodies

Reads entity and journal frontmatter directly, never `_index.md` — derived
views are for human browsing; the agent reads the facts they derive from.
Time-dependent filtering (the 14-day recency window) happens here at render
time, which keeps the committed indexes deterministic.

Prints a markdown summary to stdout. References source files instead of
duplicating content — the agent reads source for details when needed.

Must be run from project root.
"""
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml

ATLAS = Path("docs/atlas")

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
WORKLOG_TS_RE = re.compile(r"(?m)^### (\d{4}-\d{2}-\d{2}) \d{2}:\d{2}\s*$")
STALE_DAYS = 3


def parse_md(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}, text
    return meta, m.group(2)


def read(path):
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else None


def load_files(subdir, glob_pattern):
    """Yield (meta, body, path) for files under docs/atlas/<subdir>, skipping `_`-prefixed."""
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


def extract_section(body, heading_pattern):
    """Extract content between '## heading_pattern' (regex) and next '## ...' or EOF.
    Returns trimmed content or ''."""
    pat = re.compile(
        rf"^##\s+{heading_pattern}\s*$(.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    m = pat.search(body)
    return m.group(1).strip() if m else ""


def count_bullets(text):
    return sum(1 for ln in text.split("\n") if ln.lstrip().startswith(("-", "*")))


def bullet_lines(text):
    return [ln for ln in text.split("\n") if ln.lstrip().startswith(("-", "*"))]


def first_sentence(text, cap=220):
    """Return the first sentence of text, with wrapped lines joined.
    Heuristic: strip HTML comments (template placeholders), skip blockquotes, collect first
    paragraph (consecutive non-empty lines), then split on sentence-ending punctuation.
    If no sentence break, cap with ellipsis."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    para_lines = []
    started = False
    for raw in text.split("\n"):
        ln = raw.strip()
        if not started:
            if not ln or ln.startswith(">"):
                continue
            started = True
            para_lines.append(ln)
        else:
            if not ln:
                break
            para_lines.append(ln)
    if not para_lines:
        return ""
    para = " ".join(para_lines)
    m = re.match(r"^(.+?[.!?])(\s|$)", para)
    sent = m.group(1).strip() if m else para
    if len(sent) > cap:
        sent = sent[: cap - 1].rstrip() + "…"
    return sent


def parse_day(value):
    """Best-effort date from a frontmatter value ('YYYY-MM-DD', 'YYYY-MM-DD HH:MM',
    or a date object). Returns datetime.date or None."""
    s = str(value or "").strip()
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


# Guardrail sections inlined in full — violating them is costly, so the agent
# should see them without a second read. Working rules is the constitution:
# standing rules promoted from decisions, each line carrying its (D-NNN) pointer.
# Other sections are named in the menu so the agent can open PROJECT.md on demand.
PROJECT_INLINE_SECTIONS = ["Non-goals", "Hard constraints", "Working rules"]
PROJECT_RENDERED = {"Current stage", "Background", "Glossary", *PROJECT_INLINE_SECTIONS}


def render_project(out, project_md):
    if project_md is None:
        out.append("## Project")
        out.append("⚠️  PROJECT.md not found at project root.")
        out.append("")
        return

    out.append("## Project (PROJECT.md)")

    stage = extract_section(project_md, "Current stage")
    if stage:
        out.append(f"- **Stage**: {first_sentence(stage)}")

    bg = extract_section(project_md, "Background")
    if bg:
        out.append(f"- **Background**: {first_sentence(bg)}")

    for name in PROJECT_INLINE_SECTIONS:
        sec = extract_section(project_md, re.escape(name))
        bullets = bullet_lines(sec) if sec else []
        if bullets:
            out.append(f"- **{name}**:")
            for b in bullets:
                out.append(f"    - {b.lstrip('-* ').strip()}")

    glossary = extract_section(project_md, "Glossary")
    if glossary:
        n = count_bullets(glossary)
        out.append(f"- **Glossary**: {n} terms (see PROJECT.md)")

    # Menu of the sections not already rendered above, so nothing stays invisible.
    headings = re.findall(r"^##\s+(.+?)\s*$", project_md, re.MULTILINE)
    remaining = [h for h in headings if h not in PROJECT_RENDERED]
    if remaining:
        out.append(f"- **More in PROJECT.md**: {', '.join(remaining)}")

    out.append("")


def render_roadmap(out):
    roadmap = read(ATLAS / "ROADMAP.md")
    if not roadmap:
        out.append("## Roadmap")
        out.append("⚠️  docs/atlas/ROADMAP.md not found.")
        out.append("")
        return
    out.append("## Roadmap (docs/atlas/ROADMAP.md)")
    milestone = extract_section(roadmap, "Current milestone")
    if milestone:
        lines = [ln for ln in milestone.split("\n") if ln.strip()]
        header = lines[0].strip() if lines else ""
        out.append(f"- **Current milestone**: {header}")
        body = first_sentence("\n".join(lines[1:]))
        if body:
            out.append(f"  → {body}")
    out.append("")


def entity_line(out, meta, body, headline_section):
    tags = ", ".join(meta.get("tags") or [])
    line = f"- **{meta.get('id')}** {meta.get('title', '(no title)')} — {meta.get('date', '?')}"
    if tags:
        line += f" — tags: {tags}"
    out.append(line)
    sec = extract_section(body, headline_section)
    headline = first_sentence(sec) if sec else ""
    if headline:
        out.append(f"  → {headline}")


def render_decisions(out):
    entries = load_files("decisions", "D-*.md")
    live = [e for e in entries if e[0].get("status") in ("active", "planned")]
    pending = [e for e in live if e[0].get("triage", "pending") == "pending"]
    promoted = [e for e in live if e[0].get("triage") == "promoted"]
    archival = [e for e in live if e[0].get("triage") == "archival"]

    out.append(f"## Decisions pending triage ({len(pending)})")
    if pending:
        for meta, body, _ in pending:
            entity_line(out, meta, body, "Decision")
    else:
        out.append("*(none — all decisions triaged)*")
    out.append(
        f"\n*Promoted rules ({len(promoted)}) are inlined above as Working rules; "
        f"{len(archival)} archival decisions live in docs/atlas/decisions/.*"
    )
    out.append("")
    return len(pending)


def render_questions(out):
    entries = load_files("questions", "Q-*.md")
    open_qs = [e for e in entries if e[0].get("status") == "open"]
    out.append(f"## Open questions ({len(open_qs)})")
    if open_qs:
        for meta, body, _ in open_qs:
            entity_line(out, meta, body, "Why this matters")
    else:
        out.append("*(none)*")
    out.append("")


def render_experiments(out):
    if not (ATLAS / "experiments").exists():
        return
    entries = load_files("experiments", "E-*.md")
    running = [e for e in entries if e[0].get("status") == "running"]
    out.append(f"## Running experiments ({len(running)})")
    if running:
        for meta, body, _ in running:
            entity_line(out, meta, body, "Hypothesis")
    else:
        out.append("*(none)*")
    out.append("")


def stale_active_count(entries, today):
    """Active entries whose latest activity (work-log header, else opened) is old."""
    n = 0
    for meta, body, _ in entries:
        if meta.get("status") != "active":
            continue
        days = [d for d in (parse_day(ts) for ts in WORKLOG_TS_RE.findall(body)) if d]
        opened = parse_day(meta.get("opened") or meta.get("date"))
        if opened:
            days.append(opened)
        if days and (today - max(days)).days >= STALE_DAYS:
            n += 1
    return n


def render_journal(out, recent_days=14):
    entries = load_files("journal", "*.md")
    active = [e for e in entries if e[0].get("status") == "active"]
    active.sort(key=lambda e: str(e[0].get("opened", e[0].get("date", ""))), reverse=True)

    out.append("## Active journal entries")
    if active:
        for meta, body, p in active:
            tags = ", ".join(meta.get("tags") or []) or "(no tags)"
            out.append(f"- **{meta.get('date', '?')}** [{p.stem}]({p.name})")
            out.append(f"  - opened: {meta.get('opened', '?')}")
            out.append(f"  - tags: {tags}")
            sec = extract_section(body, "Context")
            headline = first_sentence(sec) if sec else ""
            if headline:
                out.append(f"  → {headline}")
    else:
        out.append("*(none — no work in progress)*")
    out.append("")

    today = datetime.now().date()
    cutoff = today - timedelta(days=recent_days)
    closed = [e for e in entries if e[0].get("status") == "closed"]
    recent = [
        e for e in closed
        if (d := parse_day(e[0].get("closed") or e[0].get("date"))) and d >= cutoff
    ]
    recent.sort(key=lambda e: str(e[0].get("closed", e[0].get("date", ""))), reverse=True)
    if recent:
        out.append(f"## Recent closed work (last {recent_days} days)")
        out.append("| Date | Entry | Tags | Result |")
        out.append("|------|-------|------|--------|")
        for meta, _, p in recent:
            tags = ", ".join(meta.get("tags") or [])
            result = meta.get("verification-result") or "?"
            out.append(f"| {meta.get('date', '?')} | [{p.stem}]({p.name}) | {tags} | {result} |")
        out.append("")

    return stale_active_count(entries, today)


def main():
    project_md = read("PROJECT.md")

    out = []
    title = "Atlas Context"
    if project_md:
        m = re.search(r"^#\s+(.+)$", project_md, re.MULTILINE)
        if m:
            title = f"Atlas Context: {m.group(1).strip()}"

    out.append(f"# {title}")
    out.append("")
    out.append("> Loaded by atlas-orient. Open referenced files for full detail.")
    out.append("")

    render_project(out, project_md)
    render_roadmap(out)
    pending = render_decisions(out)
    render_questions(out)
    render_experiments(out)
    stale = render_journal(out)

    if pending or stale:
        parts = []
        if stale:
            parts.append(f"{stale} active entr{'ies' if stale > 1 else 'y'} quiet for {STALE_DAYS}+ days")
        if pending:
            parts.append(f"{pending} decision{'s' if pending > 1 else ''} pending triage")
        out.append(f"> **Maintenance backlog**: {'; '.join(parts)} — consider an atlas-compact run.")
        out.append("")

    out.append("---")
    out.append("End of atlas context. Open source files for full content.")

    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
