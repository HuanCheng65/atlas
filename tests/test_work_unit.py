"""Tests for the work unit file — one per unit of work, written once.

The file this replaced was a single path overwritten by every work unit in
turn, which is why it went stale: committed state whose truth held only while
one particular piece of work was in flight. So the properties that matter are
that a second work unit cannot land on the first one's path, that the date
comes from the clock rather than from the caller, and that session start can
name the current one without anything being stored to say which it is.
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
START = REPO / "skills" / "grill-me" / "scripts" / "start.py"
SESSION = REPO / "skills" / "using-atlas" / "scripts" / "session_start.py"

PROJECT_MD = "# Project: Fixture\n\n## Background\n\nFixture project.\n"


def start(project, *args):
    return subprocess.run([sys.executable, str(START), *args],
                          cwd=project, capture_output=True, text=True)


def session(project):
    return subprocess.run([sys.executable, str(SESSION)],
                          cwd=project, capture_output=True, text=True).stdout


@pytest.fixture
def project(tmp_path):
    (tmp_path / "docs" / "atlas" / "records").mkdir(parents=True)
    (tmp_path / "docs" / "atlas" / "VERSION").write_text("2\n", encoding="utf-8")
    (tmp_path / "PROJECT.md").write_text(PROJECT_MD, encoding="utf-8")
    return tmp_path


def git(project, *args):
    env = {**os.environ,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", *args], cwd=project, check=True,
                   capture_output=True, env=env)


def test_the_script_owns_the_date(project):
    proc = start(project, "--slug", "rewrite-the-loader")
    assert proc.returncode == 0, proc.stderr
    path = Path(proc.stdout.strip())
    # There is no --date flag: a caller-supplied date is a fabricated one.
    assert path.name == f"{datetime.now():%Y-%m-%d}-rewrite-the-loader.md"
    assert (project / path).exists()


def test_the_skeleton_is_written_not_remembered(project):
    path = project / start(project, "--slug", "a-unit").stdout.strip()
    text = path.read_text(encoding="utf-8")
    assert "## Intent" in text and "## Spec" in text and "## Plan" in text
    # No status and no work log: the two fields the journal died of.
    assert "status" not in text and "Work log" not in text


def test_a_second_run_refuses_rather_than_overwriting(project):
    assert start(project, "--slug", "a-unit").returncode == 0
    second = start(project, "--slug", "a-unit")
    assert second.returncode != 0
    assert "exists" in second.stderr


def test_a_slug_that_is_not_kebab_case_is_refused(project):
    assert start(project, "--slug", "Rewrite The Loader").returncode != 0
    assert start(project, "--slug", "rewrite_the_loader").returncode != 0


def test_a_store_in_an_older_format_is_refused(project):
    (project / "docs" / "atlas" / "VERSION").unlink()
    proc = start(project, "--slug", "a-unit")
    assert proc.returncode != 0


def test_session_start_names_the_latest_unit_and_its_intent(project):
    start(project, "--slug", "an-older-unit")
    path = project / start(project, "--slug", "the-newer-unit").stdout.strip()
    path.write_text(path.read_text(encoding="utf-8").replace(
        "## Intent\n", "## Intent\n\nReplace the loader. It is the last thing "
                       "reading the old format.\n"), encoding="utf-8")

    out = session(project)
    assert "the-newer-unit" in out
    assert "an-older-unit" not in out
    assert "Replace the loader." in out


def test_whether_it_is_committed_is_derived_not_stored(project):
    git(project, "init", "-q")
    start(project, "--slug", "a-unit")
    assert "Latest work unit (uncommitted)" in session(project)

    git(project, "add", "-A")
    git(project, "commit", "-qm", "work", "--no-verify")
    assert "Latest work unit (committed)" in session(project)


def test_outside_a_repository_neither_state_is_claimed(project):
    # `_git` returns nothing both when a file is unchanged and when git fails,
    # so without the repository check a project with no git at all would be
    # told its work unit is committed.
    start(project, "--slug", "a-unit")
    out = session(project)
    assert "Latest work unit\n" in out
    assert "committed" not in out


def test_no_work_directory_prints_no_section(project):
    assert "Latest work unit" not in session(project)
