#!/usr/bin/env python3
"""Emit the atlas state a session starts with.

Run by the SessionStart hook, whose output lands in the model's context
directly. The hook used to print a paragraph asking the agent to invoke a
skill, which invoked a second skill, which ran a script — three of the four
steps only relayed a request, and every one of them could be skipped.

Prints the guardrails and current state; the operating rules for atlas itself
live in the using-atlas skill body, which ships and versions with atlas rather
than in the user's CLAUDE.md.

Must be run from the project root; prints nothing if there is no store.
"""
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# _lib and links belong to the record layer. Importing the siblings beats a
# third copy of the same loader: the two existing copies already carry a
# "mirror any change in the other" comment, which is a standing invitation to
# forget. The relative path holds in the repo and under ~/.claude/skills alike.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "atlas-entity" / "scripts"))
import _lib  # noqa: E402
import links  # noqa: E402

RECENT_DAYS = 14

REMINDER = (
    "<system-reminder>This project uses atlas. Invoke the `using-atlas` skill "
    "before responding, so the rules for writing records are in context when "
    "you need them. The state below is already loaded — do not re-read it."
    "</system-reminder>"
)

# Violating these is costly, so they are inlined rather than named. Everything
# else in PROJECT.md is listed as a menu the agent opens on demand.
INLINE_SECTIONS = ["Non-goals", "Hard constraints", "Working rules"]
RENDERED = {"Current stage", "Background", "Glossary", *INLINE_SECTIONS}


def read(path):
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else None


def section(text, heading):
    pat = re.compile(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s+|\Z)",
                     re.MULTILINE | re.DOTALL | re.IGNORECASE)
    m = pat.search(text)
    return m.group(1).strip() if m else ""


def bullets(text):
    return [ln.lstrip("-* ").strip() for ln in text.split("\n")
            if ln.lstrip().startswith(("-", "*"))]


def first_sentence(text, cap=220):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    para = []
    for raw in text.split("\n"):
        ln = raw.strip()
        if not para:
            if not ln or ln.startswith(">"):
                continue
            para.append(ln)
        elif ln:
            para.append(ln)
        else:
            break
    if not para:
        return ""
    joined = " ".join(para)
    m = re.match(r"^(.+?[.!?。！？])(\s|$)", joined)
    sent = m.group(1).strip() if m else joined
    return sent if len(sent) <= cap else sent[:cap - 1].rstrip() + "…"


def parse_day(value):
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def render_project(out):
    project_md = read("PROJECT.md")
    if project_md is None:
        out += ["## Project", "⚠️  PROJECT.md not found at project root.", ""]
        return
    out.append("## Project (PROJECT.md)")
    for label, heading in (("Stage", "Current stage"), ("Background", "Background")):
        sec = section(project_md, heading)
        if sec:
            out.append(f"- **{label}**: {first_sentence(sec)}")
    for name in INLINE_SECTIONS:
        items = bullets(section(project_md, name))
        if items:
            out.append(f"- **{name}**:")
            out += [f"    - {item}" for item in items]
    glossary = section(project_md, "Glossary")
    if glossary:
        out.append(f"- **Glossary**: {len(bullets(glossary))} terms (see PROJECT.md)")
    rest = [h for h in re.findall(r"^##\s+(.+?)\s*$", project_md, re.MULTILINE)
            if h not in RENDERED]
    if rest:
        out.append(f"- **More in PROJECT.md**: {', '.join(rest)}")
    out.append("")


def render_roadmap(out):
    roadmap = read(_lib.ATLAS / "ROADMAP.md")
    if not roadmap:
        return
    milestone = section(roadmap, "Current milestone")
    if not milestone:
        return
    lines = [ln for ln in milestone.split("\n") if ln.strip()]
    out.append("## Roadmap (docs/atlas/ROADMAP.md)")
    out.append(f"- **Current milestone**: {lines[0].strip()}")
    body = first_sentence("\n".join(lines[1:]))
    if body:
        out.append(f"  → {body}")
    out.append("")


def render_records(out, records, state):
    memory = sorted((r for r in records.values() if r.type == "memory"),
                    key=lambda r: r.id)
    out.append(f"## Constraints in force ({len(memory)})")
    if memory:
        # The whole always-loaded budget: one line each, body on demand.
        out += [f"- [[{r.stem}]] {r.title}" for r in memory]
    else:
        out.append("*(none recorded)*")
    out.append("")

    open_qs = sorted((r for r in records.values()
                      if r.type == "question" and r.id not in state),
                     key=lambda r: r.id)
    out.append(f"## Open questions ({len(open_qs)})")
    out += [f"- [[{r.stem}]] {r.title} — {r.meta.get('date', '?')}" for r in open_qs] \
        or ["*(none)*"]
    out.append("")

    cutoff = date.today() - timedelta(days=RECENT_DAYS)
    recent = sorted((r for r in records.values()
                     if r.type != "memory" and (parse_day(r.meta.get("date")) or date.min) >= cutoff),
                    key=lambda r: (r.meta.get("date", ""), r.id), reverse=True)
    out.append(f"## Recent records, last {RECENT_DAYS} days ({len(recent)})")
    if recent:
        for r in recent:
            standing = state.get(r.id)
            mark = f" — {standing[0]}" if standing else ""
            out.append(f"- **{r.id:03d}** [[{r.stem}]] {r.title} — {r.meta.get('date', '?')}"
                       f" — {r.type}{mark}")
    else:
        out.append("*(none — nothing landed recently)*")
    out.append("")


def main():
    # On resume the conversation context survives, so the skill body is
    # already loaded and asking for it again would only cost a round trip;
    # what may have moved meanwhile is the store, so the state still ships.
    resume = "--resume" in sys.argv[1:]
    if not _lib.ATLAS.exists():
        return
    records = _lib.load_all()
    _, edges, _ = links.graph(records)
    state = links.derive_state(records, edges)

    out = ([] if resume else [REMINDER, ""]) + ["# Atlas state", ""]
    render_project(out)
    render_roadmap(out)
    render_records(out, records, state)
    out.append(f"*{len(records)} records in docs/atlas/records/. "
               f"Titles are the menu; open a record for its body.*")
    print("\n".join(out))


if __name__ == "__main__":
    main()
