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
import subprocess
import sys
from collections import Counter
from pathlib import Path

# _lib and links belong to the record layer. Importing the siblings beats a
# third copy of the same loader: the two existing copies already carry a
# "mirror any change in the other" comment, which is a standing invitation to
# forget. The relative path holds in the repo and under ~/.claude/skills alike.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "atlas-entity" / "scripts"))
import _lib  # noqa: E402
import links  # noqa: E402

REMINDER = (
    "<system-reminder>This project uses atlas. Invoke the `using-atlas` skill "
    "before responding, so the rules for writing records are in context when "
    "you need them. The state below is already loaded — do not re-read it."
    "</system-reminder>"
)

# Above this, the last commit is a bulk change rather than a work unit.
MAX_WIP = 10

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


def touched_records(records):
    """Records the working tree has changed, plus those in the last commit.

    This is what replaced the journal's list of entries in flight, and it is
    derived rather than declared: an uncommitted record is by definition a
    draft, which is by definition the work in hand. A date window cannot say
    that — it reports whatever happened to be written recently, and goes
    empty the moment work pauses.
    """
    def paths(*args):
        try:
            proc = subprocess.run(args, capture_output=True, text=True, timeout=5)
        except (OSError, subprocess.SubprocessError):
            return []
        if proc.returncode != 0:
            return []
        return proc.stdout.splitlines()

    names = set()
    # `-uall` because the default collapses a wholly untracked directory into
    # one entry, which is exactly the shape of a store on its first day.
    for line in paths("git", "status", "--porcelain", "-uall", "--", str(_lib.RECORDS)):
        names.add(line[3:].strip().split(" -> ")[-1])
    names.update(paths("git", "log", "-1", "--name-only", "--pretty=format:",
                       "--", str(_lib.RECORDS)))

    stems = {Path(n).stem for n in names if n.endswith(".md")}
    return sorted((r for r in records.values() if r.stem in stems), key=lambda r: r.id)


def render_records(out, records, state):
    memory = sorted((r for r in records.values() if r.type == "memory"),
                    key=lambda r: r.id)
    out.append(f"## Constraints in force ({len(memory)})")
    # The whole always-loaded budget: one line each, body on demand.
    out += [f"- {r.id:03d} {r.title}" for r in memory] or ["*(none recorded)*"]
    out.append("")

    open_qs = sorted((r for r in records.values()
                      if r.type == "question" and r.id not in state),
                     key=lambda r: r.id)
    out.append(f"## Open questions ({len(open_qs)})")
    out += [f"- {r.id:03d} {r.title}" for r in open_qs] or ["*(none)*"]
    out.append("")

    touched = touched_records(records)
    if touched:
        out.append(f"## Work in progress ({len(touched)})")
        if len(touched) > MAX_WIP:
            # A commit touching this many records is a migration or a bulk
            # rewrite, not a work unit — listing it is noise, not continuity.
            out.append(f"*The last commit touched {len(touched)} records in bulk; "
                       f"see `git show --stat`.*")
        else:
            out.append("*Uncommitted records, and what the last commit touched.*")
            for r in touched:
                standing = state.get(r.id)
                mark = f", {standing[0]}" if standing else ""
                out.append(f"- {r.id:03d} {r.title} — {r.type}{mark}")
        out.append("")

    counts = Counter(r.type or "untyped" for r in records.values())
    breakdown = ", ".join(f"{n} {t}{'s' if n != 1 else ''}"
                          for t, n in sorted(counts.items(), key=lambda kv: -kv[1]))
    total = f"{len(records)} record" + ("s" if len(records) != 1 else "")
    out.append(f"*{total} — {breakdown}. Decisions and experiments are "
               f"an archive consulted on demand, not listed here: Read "
               f"`{_lib.RECORDS}/_index.md` for the full menu, or open one directly at "
               f"`{_lib.RECORDS}/NNN-*.md` when a title above is the one you need.*")


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
    print("\n".join(out))


if __name__ == "__main__":
    main()
