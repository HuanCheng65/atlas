"""Tests for atlas-compact's scan.py — the candidate-list generator.

The scan exists so a compact run reads a shortlist instead of the store, so
what matters is that each signal reports exactly the records it should and
stays quiet otherwise.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCAN = REPO / "skills" / "atlas-compact" / "scripts" / "scan.py"
NEW = REPO / "skills" / "atlas-entity" / "scripts" / "new.py"

PROJECT_MD = "# Project: Fixture\n\n## Background\n\nFixture project.\n"


def run(script, *args, cwd, stdin=None):
    return subprocess.run([sys.executable, str(script), *args],
                          cwd=cwd, input=stdin, capture_output=True, text=True)


def make(project, rtype, title, body, tags=None, new_tags=None, date=None):
    args = ["--type", rtype, "--title", title]
    if tags:
        args += ["--tags", tags]
    if new_tags:
        args += ["--new-tag", new_tags]
    if date:
        args += ["--date", date]
    if rtype == "experiment":
        for field in ("hypothesis", "config", "result", "conclusion", "artifacts"):
            args += [f"--{field}", "x"]
    proc = run(NEW, *args, cwd=project, stdin=body)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip().splitlines()[-1]


@pytest.fixture
def project(tmp_path):
    (tmp_path / "docs" / "atlas").mkdir(parents=True)
    (tmp_path / "docs" / "atlas" / "VERSION").write_text("2\n", encoding="utf-8")
    (tmp_path / "PROJECT.md").write_text(PROJECT_MD, encoding="utf-8")
    return tmp_path


def test_memory_budget_is_reported(project):
    make(project, "memory", "Keep registers under 128", "body\n", new_tags="h20")
    out = run(SCAN, cwd=project).stdout
    assert "Memory budget: 1 / 40" in out
    assert "over budget" not in out


def test_open_question_reports_age_and_citations(project):
    make(project, "question", "How large may a store grow", "body\n",
         new_tags="scale", date="2026-01-01")
    make(project, "decision", "Cap the store", "Bounded by [[001-how-large-may-a-store-grow]].\n",
         tags="scale")
    out = run(SCAN, cwd=project).stdout
    assert "cited by 1: [[001-how-large-may-a-store-grow]]" in out


def test_answered_question_drops_off_the_list(project):
    make(project, "question", "How large may a store grow", "body\n", new_tags="scale")
    make(project, "decision", "Cap the store",
         "Settled: (answers:: [[001-how-large-may-a-store-grow]]).\n", tags="scale")
    out = run(SCAN, cwd=project).stdout
    section = out.split("## Questions with no answering record")[1].split("##")[0]
    assert "*(none)*" in section


def test_records_sharing_a_neighbourhood_are_paired(project):
    for n in range(3):
        make(project, "experiment", f"Baseline {n}", "body\n", new_tags="bench")
    cites = " ".join(f"[[00{n}-baseline-{n - 1}]]" for n in (1, 2, 3))
    make(project, "decision", "First reading", f"From {cites}.\n", tags="bench")
    make(project, "decision", "Second reading", f"Also from {cites}.\n", tags="bench")
    out = run(SCAN, cwd=project).stdout
    assert "004-first-reading" in out and "005-second-reading" in out


def test_dead_paths_are_reported(project):
    make(project, "memory", "Estimator lives here",
         "The loop is in `src/gone/estimator.cuh`.\n", new_tags="cuda")
    out = run(SCAN, cwd=project).stdout
    assert "src/gone/estimator.cuh" in out


def test_live_paths_are_not_reported(project):
    (project / "src").mkdir()
    (project / "src" / "here.py").write_text("", encoding="utf-8")
    make(project, "memory", "Estimator lives here", "See `src/here.py`.\n",
         new_tags="cuda")
    out = run(SCAN, cwd=project).stdout
    section = out.split("## Records citing paths that no longer exist")[1].split("##")[0]
    assert "*(none)*" in section


def test_singleton_tags_are_listed(project):
    make(project, "decision", "One", "body\n", new_tags="shared,lonely")
    make(project, "decision", "Two", "body\n", tags="shared")
    out = run(SCAN, cwd=project).stdout
    section = out.split("## Tags used once")[1]
    assert "lonely" in section and "shared" not in section


def git_repo(project, **files):
    for name, text in files.items():
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for command in (["init", "-q"], ["add", "-A"]):
        subprocess.run(["git", *command], cwd=project, capture_output=True, check=True)


def test_record_links_escaping_the_store_are_reported(project):
    make(project, "decision", "A settled choice", "body\n", new_tags="scale")
    git_repo(project,
             **{"docs/paper-story.md": "As shown in [[001-a-settled-choice]].\n"})

    section = run(SCAN, cwd=project).stdout.split(
        "## Record links written outside the store")[1].split("##")[0]
    assert "docs/paper-story.md" in section
    assert "001-a-settled-choice" in section


def test_the_store_and_the_constitution_are_not_leaks(project):
    # PROJECT.md links records by design, and inside the store a link is the
    # point. Only documents the store does not own count.
    make(project, "decision", "A settled choice", "body\n", new_tags="scale")
    git_repo(project, **{
        "PROJECT.md": PROJECT_MD + "\n- A rule ([[001-a-settled-choice]])\n",
        "notes.md": "No identifiers here, just prose about the settled choice.\n",
    })

    section = run(SCAN, cwd=project).stdout.split(
        "## Record links written outside the store")[1].split("##")[0]
    assert "*(none)*" in section


def test_empty_store_says_so(project):
    assert "no records" in run(SCAN, cwd=project).stdout


# --- the scope of recent changes -------------------------------------------
#
# This reading is about the repository, not the store: a seam in the wrong
# place is paid for as a small change touching many files, and nobody notices
# that the way they notice a slow build. The fixtures below have a commit shape
# counted by hand, so the expected numbers do not come from the code under test.

def commit(project, subject, **files):
    env = {**os.environ,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for name, text in files.items():
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for command in (["add", "-A"], ["commit", "-qm", subject, "--no-verify"]):
        subprocess.run(["git", *command], cwd=project, capture_output=True,
                       check=True, env=env)


def scope_section(project, heading):
    return run(SCAN, cwd=project).stdout.split(heading)[1].split("##")[0]


@pytest.fixture
def repo(project):
    make(project, "decision", "A settled choice", "body\n", new_tags="scale")
    subprocess.run(["git", "init", "-q"], cwd=project, capture_output=True,
                   check=True)
    return project


def test_a_wide_commit_is_named_by_its_subject(repo):
    commit(repo, "narrow change", **{"a.py": "1\n"})
    commit(repo, "sprawling rewrite",
           **{f"mod{n}.py": "x\n" for n in range(9)})

    section = scope_section(repo, "## The scope of the last")
    assert "9 files: " in section
    assert "sprawling rewrite" in section
    assert "narrow change" not in section


def test_files_that_always_move_together_are_reported(repo):
    for n in range(5):
        commit(repo, f"paired {n}",
               **{"reader.py": f"{n}\n", "writer.py": f"{n}\n"})
    for n in range(5):
        commit(repo, f"lone {n}", **{"unrelated.py": f"{n}\n"})

    section = scope_section(repo, "## Files that change together")
    assert "`reader.py` + `writer.py`" in section
    assert "unrelated.py" not in section


def test_a_pair_below_the_threshold_stays_quiet(repo):
    # Two commits together is a coincidence, not a coupling.
    for n in range(2):
        commit(repo, f"paired {n}",
               **{"reader.py": f"{n}\n", "writer.py": f"{n}\n"})
    for n in range(4):
        commit(repo, f"reader only {n}", **{"reader.py": f"solo{n}\n"})

    assert "*(none)*" in scope_section(repo, "## Files that change together")


def test_the_store_does_not_count_as_coupling(repo):
    # Records changing alongside the code they describe is the design working.
    for n in range(5):
        commit(repo, f"work {n}", **{
            "reader.py": f"{n}\n",
            f"docs/atlas/records/{n + 900}-a-note.md":
                f"---\nid: {n + 900}\ntitle: A note\ndate: 2026-01-01\n"
                f"type: decision\ntags: [scale]\n---\n\nbody\n",
        })

    assert "*(none)*" in scope_section(repo, "## Files that change together")
