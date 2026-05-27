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


def first_lines(text, n=2):
    lines = [ln for ln in text.split("\n") if ln.strip()]
    return "\n".join(lines[:n])


def count_bullets(text):
    return sum(1 for ln in text.split("\n") if ln.lstrip().startswith(("-", "*")))


def bullet_lines(text):
    return [ln for ln in text.split("\n") if ln.lstrip().startswith(("-", "*"))]


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
    bg = extract_section(project_md, "Background")
    glossary = extract_section(project_md, "Glossary")
    if stage:
        out.append(f"- **Stage**: {first_lines(stage, 1)}")
    if bg:
        out.append(f"- **Background**: {first_lines(bg, 2)}")
    if glossary:
        n = count_bullets(glossary)
        out.append(f"- **Glossary**: {n} terms (see PROJECT.md)")
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
        out.append(f"- **Current milestone**: {first_lines(milestone, 2)}")
    out.append("")


def render_entity_list(out, label, idx_path, status_pattern):
    idx = read(idx_path)
    if idx is None:
        return
    section = extract_section(idx, status_pattern + r"\s*(?:\(\d+\))?")
    bullets = bullet_lines(section) if section else []
    out.append(f"## {label} ({len(bullets)})")
    if bullets:
        out.extend(bullets)
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
            if ln.strip():
                out.append(ln)
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
    render_entity_list(out, "Active decisions", ATLAS / "decisions" / "_index.md", "active")
    render_entity_list(out, "Open questions", ATLAS / "questions" / "_index.md", "open")

    # Active experiments (only if experiments dir exists with index)
    if (ATLAS / "experiments" / "_index.md").exists():
        render_entity_list(out, "Running experiments", ATLAS / "experiments" / "_index.md", "running")

    render_journal(out)

    out.append("---")
    out.append("End of atlas context. Open source files for full content.")

    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
