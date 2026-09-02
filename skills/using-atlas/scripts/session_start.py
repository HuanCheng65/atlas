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
# forget. The relative path is safe because the skills ship as one plugin: a
# sibling is always present, in the repo and in an install alike.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "atlas-entity" / "scripts"))
import _lib  # noqa: E402
import links  # noqa: E402

REMINDER = (
    "<system-reminder>The project's memory is loaded below and is already in "
    "context — do not re-read or re-derive it. Invoke the `atlas:using-atlas` "
    "skill "
    "now, before replying, for the rules on writing to it. Do both silently: "
    "no preamble, no acknowledgement, and do not summarise this state back to "
    "the user. Answer their message as though you had simply always known what "
    "is written here, and when you must refer to this material, call it the "
    "project's memory or notes rather than naming the tooling."
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


def constitution_links():
    """Record numbers PROJECT.md already quotes, in any section.

    A rule inlined above and its decision listed below would be the same
    claim twice, in a payload where every line is paid for every session.
    """
    project_md = read("PROJECT.md") or ""
    return {int(n) for n in re.findall(r"\[\[(\d{3,})-", project_md)}


def _git(*args):
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return []
    return proc.stdout.splitlines() if proc.returncode == 0 else []


def _resolve(records, names):
    stems = {Path(n).stem for n in names if n.endswith(".md")}
    return sorted((r for r in records.values() if r.stem in stems), key=lambda r: r.id)


def uncommitted_records(records):
    """Records the working tree has changed — the work actually in hand.

    This is what replaced the journal's list of entries in flight, and it is
    derived rather than declared: an uncommitted record is by definition a
    draft, and a draft is by definition unfinished work.
    """
    # `-uall` because the default collapses a wholly untracked directory into
    # one entry, which is exactly the shape of a store on its first day.
    names = {line[3:].strip().split(" -> ")[-1] for line in
             _git("git", "status", "--porcelain", "-uall", "--", str(_lib.RECORDS))}
    return _resolve(records, names)


def head_records(records):
    """Records the last commit changed — context, not work in hand.

    `git log -1 -- <path>` would answer a different question, "the last commit
    that touched this path", and so keeps reporting a migration from weeks ago
    after any commit elsewhere. `--root` so a repository's first commit is not
    silently empty.
    """
    return _resolve(records, _git("git", "diff-tree", "--no-commit-id",
                                  "--name-only", "-r", "--root", "HEAD",
                                  "--", str(_lib.RECORDS)))


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

    # Titles are the menu, so the menu ships rather than being fetched: an
    # agent that would have to read the index anyway lands the same bytes in
    # context, one tool call later. Decisions stay few by construction — a
    # decision is architecturally significant or it is not a decision — while
    # experiments grow without bound, so only decisions are named.
    quoted = set(constitution_links())
    live = sorted((r for r in records.values()
                   if r.type == "decision" and r.id not in state
                   and r.id not in quoted),
                  key=lambda r: r.id)
    out.append(f"## Decisions in force ({len(live)})")
    if quoted:
        out.append(f"*{len(quoted)} more are quoted above as Working rules.*")
    out += [f"- {r.id:03d} {r.title}" for r in live] or ["*(none)*"]
    out.append("")

    drafts = uncommitted_records(records)
    if drafts:
        out.append(f"## Uncommitted, still drafts ({len(drafts)})")
        if len(drafts) > MAX_WIP:
            # This many at once is a migration or a bulk rewrite, not a work
            # unit — listing them is noise rather than continuity.
            out.append("*A bulk change is in the working tree; see `git status`.*")
        else:
            for r in drafts:
                standing = state.get(r.id)
                mark = f", {standing[0]}" if standing else ""
                out.append(f"- {r.id:03d} {r.title} — {r.type}{mark}")
        out.append("")

    landed = head_records(records)
    if landed:
        # Context, not work in hand: named in one line so a session the day
        # after a commit knows what landed without mistaking it for a task.
        titles = "; ".join(f"{r.id:03d} {r.title}" for r in landed[:MAX_WIP])
        more = f" and {len(landed) - MAX_WIP} more" if len(landed) > MAX_WIP else ""
        out.append(f"*Last commit touched {len(landed)} record(s): {titles}{more}.*")
        out.append("")

    counts = Counter(r.type or "untyped" for r in records.values())
    breakdown = ", ".join(f"{n} {t}{'s' if n != 1 else ''}"
                          for t, n in sorted(counts.items(), key=lambda kv: -kv[1]))
    total = f"{len(records)} record" + ("s" if len(records) != 1 else "")
    retired = len(state)
    out.append(f"*{total} — {breakdown}"
               + (f"; {retired} superseded or answered, not listed" if retired else "")
               + f". Experiments and retired records are an archive consulted on "
               f"demand: Read `{_lib.RECORDS}/_index.md` for the full menu, or open "
               f"one directly at `{_lib.RECORDS}/NNN-*.md` when a title above is the "
               f"one you need.*")

    if _lib.ID_MAP_FILE.exists():
        # Only this project's own older documents carry these, so the line
        # costs nothing anywhere the store was never renumbered.
        out.append("")
        out.append(f"*Older documents here cite records as `D-007` / `E-021`, from "
                   f"before the store was renumbered. `grep '^E-021' "
                   f"{_lib.ID_MAP_FILE}` resolves one. They are prose, not links — "
                   f"read through them, do not rewrite them.*")


def main():
    # On resume the conversation context survives, so the skill body is
    # already loaded and asking for it again would only cost a round trip;
    # what may have moved meanwhile is the store, so the state still ships.
    resume = "--resume" in sys.argv[1:]
    if not _lib.ATLAS.exists():
        return
    complaint = _lib.version_complaint()
    if complaint:
        # Exiting would leave the session with no explanation at all. The
        # payload is what the agent reads, so put the problem in the payload.
        print(f"<system-reminder>The project's memory could not be loaded: "
              f"{complaint} Tell the user before doing anything that assumes "
              f"the project has no history.</system-reminder>")
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
