"""Tests for the post-write store guard.

The guard exists for the writes no script owns: a record edited in place, a
typed edge appended to a published one. What it must get right is reporting a
broken store once rather than on every command that follows, and staying out
of the way otherwise.
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
GUARD = REPO / "hooks" / "store_guard.py"
NEW = REPO / "skills" / "atlas-entity" / "scripts" / "new.py"


def guard(cwd):
    return subprocess.run([sys.executable, str(GUARD)],
                          cwd=cwd, capture_output=True, text=True)


def make(project, rtype, title, body, new_tags="fixture"):
    proc = subprocess.run(
        [sys.executable, str(NEW), "--type", rtype, "--title", title,
         "--new-tag", new_tags],
        cwd=project, input=body, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return Path(proc.stdout.strip().splitlines()[-1])


@pytest.fixture
def project(tmp_path):
    (tmp_path / "docs" / "atlas" / "records").mkdir(parents=True)
    (tmp_path / "docs" / "atlas" / "VERSION").write_text("2\n", encoding="utf-8")
    return tmp_path


def test_a_directory_without_a_store_is_untouched(tmp_path):
    proc = guard(tmp_path)
    assert proc.returncode == 0
    assert proc.stdout == "" and proc.stderr == ""


def test_a_healthy_store_passes_and_gets_its_index_rebuilt(project):
    make(project, "decision", "A settled choice", "body\n")
    index = project / "docs" / "atlas" / "records" / "_index.md"
    index.unlink()

    assert guard(project).returncode == 0
    assert "A settled choice" in index.read_text(encoding="utf-8")


def test_a_link_that_resolves_to_nothing_is_reported(project):
    # The failure the guard exists for: this supersede never takes effect,
    # and without the check nothing says so until someone runs validate.
    make(project, "decision", "The new way",
         "It replaces the old one: (supersedes:: [[001-no-such-record]]).\n")

    proc = guard(project)
    assert proc.returncode == 2
    assert "001-no-such-record" in proc.stderr
    assert "never takes effect" in proc.stderr


def test_a_hand_edit_of_a_written_record_is_caught(project):
    # No script owns this write, which is the whole reason the check is a hook.
    path = project / make(project, "memory", "Registers stay under 128", "body\n")
    path.write_text(path.read_text(encoding="utf-8")
                    + "\nSee [[009-never-written]].\n", encoding="utf-8")

    assert guard(project).returncode == 2


def test_one_broken_state_is_reported_once(project):
    make(project, "decision", "The new way",
         "Replaces it: (supersedes:: [[001-no-such-record]]).\n")

    assert guard(project).returncode == 2
    # Unchanged store, so the next command says nothing rather than repeating
    # the complaint through every step of the fix.
    second = guard(project)
    assert second.returncode == 0
    assert second.stderr == ""


def test_a_further_change_is_checked_again(project):
    path = project / make(project, "decision", "The new way",
                          "Replaces it: (supersedes:: [[001-no-such-record]]).\n")
    assert guard(project).returncode == 2
    assert guard(project).returncode == 0

    path.write_text(path.read_text(encoding="utf-8").replace(
        "[[001-no-such-record]]", "[[002-still-missing]]"), encoding="utf-8")
    assert guard(project).returncode == 2


def test_rebuilding_the_index_does_not_count_as_a_change(project):
    make(project, "decision", "A settled choice", "body\n")
    assert guard(project).returncode == 0
    # The index was just rewritten; that must not read as the store moving,
    # or the guard would validate on every call forever.
    assert guard(project).returncode == 0
