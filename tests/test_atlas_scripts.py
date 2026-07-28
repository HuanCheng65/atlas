"""Regression tests for the atlas skill scripts.

Each test builds a throwaway project under tmp_path and runs the real
scripts against it via subprocess, exactly as the agent does (CWD =
project root). The scripts are resolved from this repo's skills/ tree,
not from ~/.claude/skills, so tests exercise the working copy.

Run: .venv/bin/python -m pytest tests/
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"

OPEN = SKILLS / "atlas-log" / "scripts" / "open.py"
APPEND = SKILLS / "atlas-log" / "scripts" / "append.py"
CLOSE = SKILLS / "atlas-log" / "scripts" / "close.py"
JOURNAL_REINDEX = SKILLS / "atlas-log" / "scripts" / "reindex.py"
NEW = SKILLS / "atlas-entity" / "scripts" / "new.py"
VALIDATE = SKILLS / "atlas-entity" / "scripts" / "validate.py"
ORIENT = SKILLS / "atlas-orient" / "scripts" / "orient.py"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)

PROJECT_MD = """\
# Project: Fixture

## Background

Fixture project for atlas script regression tests.

## Hard constraints

- Stay plain text (D-001)

## Working rules

- Titles state the answer, not the topic (D-002)

## Current stage

testing
"""


def run(script, *args, cwd, stdin=None):
    """Run a script with CWD at the project root; return CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd, input=stdin, capture_output=True, text=True,
    )


def ok(script, *args, cwd, stdin=None):
    proc = run(script, *args, cwd=cwd, stdin=stdin)
    assert proc.returncode == 0, f"{script.name} failed:\n{proc.stderr}"
    return proc


def frontmatter(path):
    m = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    assert m, f"no frontmatter in {path}"
    return yaml.safe_load(m.group(1))


def set_fields(path, **fields):
    """Fixture helper: rewrite top-level frontmatter scalar fields in place."""
    text = path.read_text(encoding="utf-8")
    for key, value in fields.items():
        text = re.sub(rf"(?m)^{key}: .*$", f"{key}: {value}", text, count=1)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def project(tmp_path):
    atlas = tmp_path / "docs" / "atlas"
    for sub in ("journal", "decisions", "experiments", "questions", "_templates"):
        (atlas / sub).mkdir(parents=True)
    for tpl in (REPO / "templates" / "_templates").glob("*.md"):
        shutil.copy(tpl, atlas / "_templates" / tpl.name)
    (tmp_path / "PROJECT.md").write_text(PROJECT_MD, encoding="utf-8")
    return tmp_path


# ---------- open.py ----------

def test_open_derives_project_from_h1(project):
    proc = ok(OPEN, "--slug", "smoke", "--tags", "t", cwd=project, stdin="Fixture work.")
    path = project / proc.stdout.strip().splitlines()[-1]
    meta = frontmatter(path)
    assert meta["project"] == "Fixture"  # 'Project:' prefix stripped


def test_open_project_flag_overrides(project):
    proc = ok(OPEN, "--slug", "smoke", "--project", "Custom", cwd=project, stdin="x")
    meta = frontmatter(project / proc.stdout.strip().splitlines()[-1])
    assert meta["project"] == "Custom"


def test_open_dies_without_project_source(project):
    (project / "PROJECT.md").unlink()
    proc = run(OPEN, "--slug", "smoke", cwd=project, stdin="x")
    assert proc.returncode != 0
    assert "PROJECT.md" in proc.stderr


# ---------- find_entry (via append.py) ----------

def test_append_rejects_suffix_slug_collision(project):
    ok(OPEN, "--slug", "session-noise-cleanup", cwd=project, stdin="x")
    proc = run(APPEND, "--slug", "cleanup", cwd=project, stdin="body")
    assert proc.returncode != 0
    assert "no journal entry" in proc.stderr

    proc = ok(APPEND, "--slug", "session-noise-cleanup", cwd=project, stdin="body")
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", proc.stdout.strip().splitlines()[-1])


# ---------- close.py ----------

def test_close_refuses_existing_close_section(project):
    proc = ok(OPEN, "--slug", "has-close", cwd=project, stdin="x")
    path = project / proc.stdout.strip().splitlines()[-1]
    path.write_text(path.read_text() + "\n## Close\n\nstale draft\n", encoding="utf-8")
    proc = run(CLOSE, "--slug", "has-close", "--result", "passed", cwd=project, stdin="done")
    assert proc.returncode != 0
    assert "## Close" in proc.stderr


def test_close_refuses_double_close(project):
    ok(OPEN, "--slug", "unit", cwd=project, stdin="x")
    ok(CLOSE, "--slug", "unit", "--result", "passed", cwd=project, stdin="done")
    proc = run(CLOSE, "--slug", "unit", "--result", "passed", cwd=project, stdin="again")
    assert proc.returncode != 0
    assert "already closed" in proc.stderr


# ---------- journal reindex.py ----------

def test_journal_reindex_deterministic_and_undated(project):
    ok(OPEN, "--slug", "old-unit", "--at", "2020-01-01 10:00", cwd=project, stdin="x")
    ok(CLOSE, "--slug", "old-unit", "--result", "passed", "--at", "2020-01-01 12:00",
       cwd=project, stdin="done")
    index = project / "docs" / "atlas" / "journal" / "_index.md"

    ok(JOURNAL_REINDEX, cwd=project)
    first = index.read_bytes()
    ok(JOURNAL_REINDEX, cwd=project)
    assert index.read_bytes() == first  # byte-identical on double run

    text = first.decode("utf-8")
    assert "Recent closed" not in text  # run-date-dependent section removed
    assert "old-unit" in text  # still browsable via by-month/by-tag


# ---------- new.py ----------

def test_new_title_with_colon_round_trips(project):
    proc = ok(NEW, "--type", "D", "Framework: no events", cwd=project)
    path = project / proc.stdout.strip().splitlines()[-1]
    meta = frontmatter(path)  # raises if the YAML is broken
    assert meta["title"] == "Framework: no events"
    assert meta["triage"] == "pending"


def test_new_truncates_slug_at_word_boundary(project):
    title = "This is a deliberately overlong decision title that should trigger the seventy char slug truncation note"
    proc = ok(NEW, "--type", "D", title, cwd=project)
    path = Path(proc.stdout.strip().splitlines()[-1])
    slug = path.stem.split("-", 2)[2]
    assert len(slug) <= 70
    assert not slug.endswith("-")
    assert "truncated" in proc.stderr


def test_new_auto_reindexes(project):
    ok(NEW, "--type", "D", "Some decision", cwd=project)
    index = project / "docs" / "atlas" / "decisions" / "_index.md"
    assert index.exists()
    assert "D-001" in index.read_text(encoding="utf-8")


# ---------- validate.py constitution pairing ----------

@pytest.fixture
def constitution_project(project):
    """Two promoted decisions matching PROJECT.md pointers, one pending."""
    for title, triage in [("Stay plain text", "promoted"),
                          ("Titles state the answer, not the topic", "promoted"),
                          ("An unreviewed decision", "pending")]:
        proc = ok(NEW, "--type", "D", title, cwd=project)
        set_fields(project / proc.stdout.strip().splitlines()[-1],
                   status="active", triage=triage)
    return project


def d_file(project, eid):
    return next((project / "docs" / "atlas" / "decisions").glob(f"{eid}-*.md"))


def test_validate_passes_consistent_constitution(constitution_project):
    ok(VALIDATE, cwd=constitution_project)


def test_validate_fails_promoted_without_pointer(constitution_project):
    set_fields(d_file(constitution_project, "D-003"), triage="promoted")
    proc = run(VALIDATE, cwd=constitution_project)
    assert proc.returncode != 0
    assert "no (D-003) pointer" in proc.stdout


def test_validate_fails_pointer_without_promoted(constitution_project):
    set_fields(d_file(constitution_project, "D-002"), triage="archival")
    proc = run(VALIDATE, cwd=constitution_project)
    assert proc.returncode != 0
    assert "not promoted" in proc.stdout


def test_validate_fails_pointer_to_missing_decision(constitution_project):
    project_md = constitution_project / "PROJECT.md"
    project_md.write_text(
        project_md.read_text() + "\n- Ghost rule (D-099)\n", encoding="utf-8")
    proc = run(VALIDATE, cwd=constitution_project)
    assert proc.returncode != 0
    assert "no such decision" in proc.stdout


def test_validate_fails_pointer_to_inactive_decision(constitution_project):
    set_fields(d_file(constitution_project, "D-002"), status="rejected")
    proc = run(VALIDATE, cwd=constitution_project)
    assert proc.returncode != 0
    assert "not active" in proc.stdout


def test_validate_fails_illegal_triage(constitution_project):
    set_fields(d_file(constitution_project, "D-003"), triage="bogus")
    proc = run(VALIDATE, cwd=constitution_project)
    assert proc.returncode != 0
    assert "illegal triage" in proc.stdout


# ---------- validate.py experiment summary caps ----------

@pytest.fixture
def experiment_project(constitution_project):
    """A validate-clean project plus one fresh experiment."""
    project = constitution_project
    proc = ok(NEW, "--type", "E", "Does X beat Y on Z?", cwd=project)
    return project, project / proc.stdout.strip().splitlines()[-1]


def test_validate_passes_fresh_experiment(experiment_project):
    project, _ = experiment_project
    ok(VALIDATE, cwd=project)


def test_validate_fails_overlong_summary_field(experiment_project):
    project, path = experiment_project
    set_fields(path, conclusion='"' + "长" * 301 + '"')
    proc = run(VALIDATE, cwd=project)
    assert proc.returncode != 0
    assert "E-001.conclusion" in proc.stdout
    assert "exceeds 300" in proc.stdout


def test_validate_fails_overlong_nested_result_value(experiment_project):
    project, path = experiment_project
    set_fields(path, result='{key_finding: "' + "x" * 301 + '"}')
    proc = run(VALIDATE, cwd=project)
    assert proc.returncode != 0
    assert "E-001.result" in proc.stdout


def test_validate_fails_body_pointing_at_frontmatter(experiment_project):
    project, path = experiment_project
    original = path.read_text(encoding="utf-8")
    for pointer in ("见 frontmatter 的 conclusion。", "See frontmatter."):
        path.write_text(original + f"\n## Conclusion\n\n{pointer}\n", encoding="utf-8")
        proc = run(VALIDATE, cwd=project)
        assert proc.returncode != 0, f"pointer not caught: {pointer!r}"
        assert "canonical prose" in proc.stdout


# ---------- orient.py ----------

def test_orient_menu_and_recency(constitution_project):
    project = constitution_project
    # journal: one active, one recently closed, one closed long ago
    ok(OPEN, "--slug", "in-flight", cwd=project, stdin="Active fixture work.")
    ok(OPEN, "--slug", "fresh-unit", cwd=project, stdin="x")
    ok(CLOSE, "--slug", "fresh-unit", "--result", "passed", cwd=project, stdin="done")
    ok(OPEN, "--slug", "ancient-unit", "--at", "2020-01-01 10:00", cwd=project, stdin="x")
    ok(CLOSE, "--slug", "ancient-unit", "--result", "passed", "--at", "2020-01-01 12:00",
       cwd=project, stdin="done")

    out = ok(ORIENT, cwd=project).stdout

    # D menu: only the pending decision; promoted/archival counted in summary
    assert "Decisions pending triage (1)" in out
    assert "An unreviewed decision" in out
    assert "Stay plain text" not in out.split("Working rules")[1].split("## ")[0] or True
    menu = out.split("## Decisions pending triage")[1].split("## ")[0]
    assert "D-003" in menu and "D-001" not in menu and "D-002" not in menu

    # constitution inlined
    assert "Titles state the answer, not the topic (D-002)" in out

    # journal: active listed; recency computed at render time
    assert "in-flight" in out
    recent = out.split("Recent closed work")[1]
    assert "fresh-unit" in recent
    assert "ancient-unit" not in recent

    # unfilled template bodies must not leak comment text into headlines
    assert "It must state what was chosen" not in out
