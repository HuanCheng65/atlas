"""Tests for the session-start payload.

What ships at session start is a budget: everything printed is paid for in
every session on the project. These tests pin what earns a place — the
guardrails, the constraints in force, the open questions, and the work in
hand — and, just as much, what does not.
"""
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


def test_decisions_are_counted_not_listed(project):
    make(project, "decision", "A choice nobody needs at startup", "body\n")
    out = run(cwd=project).stdout
    assert "A choice nobody needs at startup" not in out
    assert "1 decision" in out
    assert "_index.md" in out


def test_answered_questions_drop_off(project):
    make(project, "question", "Still open", "body\n")
    make(project, "question", "Already settled", "body\n", tags="fixture")
    make(project, "decision", "The settlement",
         "Done: (answers:: [[002-already-settled]]).\n", tags="fixture")
    out = run(cwd=project).stdout
    assert "Still open" in out
    assert "Already settled" not in out
    assert "Open questions (1)" in out


def test_uncommitted_records_are_the_work_in_progress(project):
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    make(project, "decision", "Something in hand", "body\n")
    out = run(cwd=project).stdout
    assert "Work in progress (1)" in out
    assert "001 Something in hand — decision" in out


def test_a_bulk_commit_is_summarised_not_listed(project):
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    for n in range(11):
        make(project, "decision", f"Bulk decision {n}", "body\n")
    out = run(cwd=project).stdout
    assert "touched 11 records in bulk" in out
    assert "Bulk decision 3" not in out


def test_resume_omits_the_skill_reminder(project):
    assert "system-reminder" in run(cwd=project).stdout
    assert "system-reminder" not in run("--resume", cwd=project).stdout
    assert "# Atlas state" in run("--resume", cwd=project).stdout


def test_no_store_prints_nothing(tmp_path):
    assert run(cwd=tmp_path).stdout == ""
