#!/usr/bin/env python3
"""Load atlas state and print a navigator summary for session start.

Usage:
    orient.py

Reads:
  PROJECT.md (project root)
  docs/atlas/ROADMAP.md
  docs/atlas/decisions/_index.md
  docs/atlas/questions/_index.md
  docs/atlas/journal/_index.md

Prints a markdown summary to stdout. References source files instead of
duplicating content — the agent reads source for details when needed.

Must be run from project root.
"""
import re
import sys
from pathlib import Path

ATLAS = Path("docs/atlas")


def read(path):
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else None


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
    Heuristic: skip HTML comments / blockquotes, collect first paragraph (consecutive non-empty
    lines), then split on sentence-ending punctuation. If no sentence break, cap with ellipsis."""
    para_lines = []
    started = False
    for raw in text.split("\n"):
        ln = raw.strip()
        if not started:
            if not ln or ln.startswith("<!--") or ln.startswith(">"):
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


def entity_file(entity_id, subdir):
    """Find docs/atlas/<subdir>/<entity_id>-*.md. Returns Path or None."""
    matches = sorted((ATLAS / subdir).glob(f"{entity_id}-*.md"))
    return matches[0] if matches else None


def headline_for_entity(entity_id, subdir, section_pattern):
    """Pull the first sentence of the named section from an entity body.
    Returns '' if file or section missing — caller renders without sub-bullet."""
    f = entity_file(entity_id, subdir)
    if not f:
        return ""
    body = read(f)
    if not body:
        return ""
    sec = extract_section(body, section_pattern)
    return first_sentence(sec) if sec else ""


def headline_for_journal(filename):
    """Pull the first sentence of ## Context from a journal entry filename (e.g. '2026-05-28-foo.md')."""
    f = ATLAS / "journal" / filename
    body = read(f)
    if not body:
        return ""
    sec = extract_section(body, "Context")
    return first_sentence(sec) if sec else ""


# Guardrail sections inlined in full — violating them is costly, so the agent
# should see them without a second read. Other sections are named in the menu
# so the agent knows they exist and can open PROJECT.md on demand.
PROJECT_INLINE_SECTIONS = ["Non-goals", "Hard constraints"]
PROJECT_RENDERED = {"Current stage", "Background", "Glossary", *PROJECT_INLINE_SECTIONS}


def render_project(out, project_md):
    if project_md is None:
        out.append("## Project")
        out.append("⚠️  PROJECT.md not found at project root.")
        out.append("")
        return None

    title = "Unnamed Project"
    m = re.search(r"^#\s+(.+)$", project_md, re.MULTILINE)
    if m:
        title = m.group(1).strip()

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
    return title


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


ENTITY_HEADLINE_SECTION = {
    "decisions": "Decision",
    "questions": "Why this matters",
    "experiments": "Hypothesis",
}


def render_entity_list(out, label, idx_path, status_pattern, subdir=None):
    idx = read(idx_path)
    if idx is None:
        return
    section = extract_section(idx, status_pattern + r"\s*(?:\(\d+\))?")
    bullets = bullet_lines(section) if section else []
    out.append(f"## {label} ({len(bullets)})")
    if bullets:
        section_pat = ENTITY_HEADLINE_SECTION.get(subdir) if subdir else None
        for b in bullets:
            out.append(b)
            if section_pat:
                m = re.search(r"\*\*([DQE]-\d+)\*\*", b)
                if m:
                    headline = headline_for_entity(m.group(1), subdir, section_pat)
                    if headline:
                        out.append(f"  → {headline}")
    else:
        out.append("*(none)*")
    out.append("")


def render_journal(out):
    idx = read(ATLAS / "journal" / "_index.md")
    if idx is None:
        out.append("## Active journal entries")
        out.append("*(journal index not yet generated)*")
        out.append("")
        return

    active = extract_section(idx, r"Active\s*(?:\(\d+\))?")
    out.append("## Active journal entries")
    if active and "*No active entries.*" not in active:
        for ln in active.split("\n"):
            if not ln.strip():
                continue
            out.append(ln)
            # If this line is a top-level bullet with a markdown link to a journal file,
            # pull the first sentence of ## Context as a sub-bullet.
            m = re.match(r"^-\s+.*\[[^\]]+\]\(([^)]+\.md)\)", ln)
            if m:
                headline = headline_for_journal(m.group(1))
                if headline:
                    out.append(f"  → {headline}")
    else:
        out.append("*(none — no work in progress)*")
    out.append("")

    recent = extract_section(idx, r"Recent closed.*?")
    if recent and "*Nothing closed recently.*" not in recent:
        out.append("## Recent closed work (last 14 days)")
        for ln in recent.split("\n"):
            if ln.strip():
                out.append(ln)
        out.append("")


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
    render_entity_list(out, "Active decisions", ATLAS / "decisions" / "_index.md", "active", subdir="decisions")
    render_entity_list(out, "Open questions", ATLAS / "questions" / "_index.md", "open", subdir="questions")

    # Active experiments (only if experiments dir exists with index)
    if (ATLAS / "experiments" / "_index.md").exists():
        render_entity_list(out, "Running experiments", ATLAS / "experiments" / "_index.md", "running", subdir="experiments")

    render_journal(out)

    out.append("---")
    out.append("End of atlas context. Open source files for full content.")

    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
