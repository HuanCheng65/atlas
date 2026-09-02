"""Tests for the session-start payload.

What ships at session start is a budget: everything printed is paid for in
every session on the project. These tests pin what earns a place — the
guardrails, the constraints in force, the open questions, and the work in
hand — and, just as much, what does not.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
START = REPO / "skills" / "using-atlas" / "scripts" / "session_start.py"
NEW = REPO / "skills" / "atlas-entity" / "scripts" / "new.py"

PROJECT_MD = """\
# Project: Fixture

## Current stage

prototype — see the roadmap.

## Background

A fixture project for session-start tests.

## Non-goals

- Team-scale collaboration

## Hard constraints

- Plain text and git only

## Working rules

- Titles state the claim

## Glossary

- **thing** — a thing

## Long-term goals

Someday.
"""


def run(*args, cwd, stdin=None):
    return subprocess.run([sys.executable, str(START), *args],
                          cwd=cwd, input=stdin, capture_output=True, text=True)


def make(project, rtype, title, body, tags=None, new_tags=None):
    args = ["--type", rtype, "--title", title]
    args += ["--tags", tags] if tags else ["--new-tag", new_tags or "fixture"]
    proc = subprocess.run([sys.executable, str(NEW), *args],
                          cwd=project, input=body, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip().splitlines()[-1]


@pytest.fixture
def project(tmp_path):
    (tmp_path / "docs" / "atlas" / "records").mkdir(parents=True)
    (tmp_path / "docs" / "atlas" / "VERSION").write_text("2\n", encoding="utf-8")
    (tmp_path / "PROJECT.md").write_text(PROJECT_MD, encoding="utf-8")
    return tmp_path


def test_guardrails_are_inlined_in_full(project):
    out = run(cwd=project).stdout
    assert "Team-scale collaboration" in out
    assert "Plain text and git only" in out
    assert "Titles state the claim" in out


def test_unrendered_project_sections_are_named_not_inlined(project):
    out = run(cwd=project).stdout
    assert "More in PROJECT.md**: Long-term goals" in out
    assert "Someday." not in out


def test_memory_titles_are_listed_in_full(project):
    make(project, "memory", "Keep registers under 128", "body\n", new_tags="h20")
    out = run(cwd=project).stdout
    assert "Constraints in force (1)" in out
    assert "001 Keep registers under 128" in out


def test_decisions_in_force_are_listed(project):
    make(project, "decision", "A choice that still binds", "body\n")
    out = run(cwd=project).stdout
    assert "Decisions in force (1)" in out
    assert "001 A choice that still binds" in out
    assert "_index.md" in out


def test_superseded_decisions_drop_off(project):
    make(project, "decision", "The old way", "body\n")
    make(project, "decision", "The new way",
         "Replaces it: (supersedes:: [[001-the-old-way]]).\n", tags="fixture")
    out = run(cwd=project).stdout
    assert "The old way" not in out
    assert "The new way" in out
    assert "1 superseded or answered, not listed" in out


def test_decisions_quoted_as_working_rules_are_not_repeated(project):
    make(project, "decision", "Titles state the claim", "body\n")
    project_md = project / "PROJECT.md"
    project_md.write_text(
        project_md.read_text(encoding="utf-8").replace(
            "- Titles state the claim",
            "- Titles state the claim ([[001-titles-state-the-claim]])"),
        encoding="utf-8")
    out = run(cwd=project).stdout
    assert "Decisions in force (0)" in out
    assert "1 more are quoted above as Working rules" in out


def test_experiments_are_counted_not_listed(project):
    proc = subprocess.run(
        [sys.executable, str(NEW), "--type", "experiment", "--title",
         "A run nobody needs at startup", "--new-tag", "bench",
         "--hypothesis", "h", "--config", "c", "--result", "r",
         "--conclusion", "cc", "--artifacts", "a"],
        cwd=project, input="body\n", capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    out = run(cwd=project).stdout
    assert "A run nobody needs at startup" not in out
    assert "1 experiment" in out


def test_answered_questions_drop_off(project):
    make(project, "question", "Still open", "body\n")
    make(project, "question", "Already settled", "body\n", tags="fixture")
    make(project, "decision", "The settlement",
         "Done: (answers:: [[002-already-settled]]).\n", tags="fixture")
    out = run(cwd=project).stdout
    assert "Still open" in out
    assert "Already settled" not in out
    assert "Open questions (1)" in out


def test_uncommitted_records_are_the_drafts(project):
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    make(project, "decision", "Something in hand", "body\n")
    out = run(cwd=project).stdout
    assert "Uncommitted, still drafts (1)" in out
    assert "001 Something in hand — decision" in out


def test_a_bulk_commit_is_summarised_not_listed(project):
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    for n in range(11):
        make(project, "decision", f"Bulk decision {n}", "body\n")
    out = run(cwd=project).stdout
    assert "A bulk change is in the working tree" in out
    wip = out.split("## Uncommitted, still drafts")[1].split("##")[0]
    assert "Bulk decision 3" not in wip


def test_a_commit_elsewhere_clears_the_landed_line(project):
    # `git log -1 -- <path>` answers "the last commit that touched this",
    # which after a commit elsewhere keeps reporting work that already landed.
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    def git(*args):
        subprocess.run(["git", *args], cwd=project, check=True,
                       capture_output=True, env={**os.environ, **env})
    git("init", "-q")
    make(project, "decision", "Landed already", "body\n")
    git("add", "-A")
    git("commit", "-qm", "records", "--no-verify")
    out = run(cwd=project).stdout
    assert "Uncommitted, still drafts" not in out
    assert "Last commit touched 1 record(s): 001 Landed already" in out

    (project / "unrelated.txt").write_text("x", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "something else", "--no-verify")
    assert "Last commit touched" not in run(cwd=project).stdout


def test_the_reminder_asks_for_silence(project):
    out = run(cwd=project).stdout
    assert "do not summarise this state back to the user" in out
    assert "silently" in out


def test_resume_omits_the_skill_reminder(project):
    assert "system-reminder" in run(cwd=project).stdout
    assert "system-reminder" not in run("--resume", cwd=project).stdout
    assert "# Atlas state" in run("--resume", cwd=project).stdout


def test_no_store_prints_nothing(tmp_path):
    assert run(cwd=tmp_path).stdout == ""
