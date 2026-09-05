"""Tests for the design document — one per grill round, written once.

The shape this replaced demanded Intent, Spec and Plan from every interview,
so a round that settled a design and reached no implementation had to invent
the level it never got to. What matters now is that the script writes only the
two sections a round always has, that the continuation line is never left to
memory, and that the date comes from the clock rather than from the caller.
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
START = REPO / "skills" / "grill-me" / "scripts" / "start.py"

PROJECT_MD = "# Project: Fixture\n\n## Background\n\nFixture project.\n"


def start(project, *args):
    return subprocess.run([sys.executable, str(START), *args],
                          cwd=project, capture_output=True, text=True)


@pytest.fixture
def project(tmp_path):
    (tmp_path / "docs" / "atlas" / "records").mkdir(parents=True)
    (tmp_path / "docs" / "atlas" / "VERSION").write_text("3\n", encoding="utf-8")
    (tmp_path / "PROJECT.md").write_text(PROJECT_MD, encoding="utf-8")
    return tmp_path


def test_the_script_owns_the_date(project):
    proc = start(project, "--slug", "rewrite-the-loader", "--new")
    assert proc.returncode == 0, proc.stderr
    path = Path(proc.stdout.strip())
    # There is no --date flag: a caller-supplied date is a fabricated one.
    assert path.name == f"{datetime.now():%Y-%m-%d}-rewrite-the-loader.md"
    assert path.parent == Path("docs/atlas/design")
    assert (project / path).exists()


def test_a_new_line_is_written_whole(project):
    path = project / start(project, "--slug", "a-round", "--new").stdout.strip()
    assert path.read_text(encoding="utf-8") == (
        "# A round\n\nStarts a new line.\n\n## Decided\n\n## Still open\n")


def test_a_continued_round_names_the_document_it_continues(project):
    first = project / start(project, "--slug", "the-first", "--new").stdout.strip()
    path = project / start(project, "--slug", "the-second",
                           "--from", first.name).stdout.strip()
    assert path.read_text(encoding="utf-8") == (
        "# The second\n\n"
        "Continues `docs/atlas/design/" + first.name + "`.\n\n"
        "## Decided\n\n## Still open\n")


def test_the_lineage_cannot_be_left_unstated(project):
    # The continuation link is the only structure holding the documents
    # together, so neither omitting it nor claiming both is allowed.
    assert start(project, "--slug", "a-round").returncode != 0
    both = start(project, "--slug", "a-round", "--new", "--from", "x.md")
    assert both.returncode != 0


def test_continuing_a_document_that_is_not_there_is_refused(project):
    proc = start(project, "--slug", "a-round", "--from", "2020-01-01-absent.md")
    assert proc.returncode != 0
    assert "no such design document" in proc.stderr


def test_the_skeleton_carries_no_status_and_no_work_log(project):
    path = project / start(project, "--slug", "a-round", "--new").stdout.strip()
    text = path.read_text(encoding="utf-8")
    # The two fields the journal died of, and the three sections this replaced.
    assert "status" not in text and "Work log" not in text
    assert "## Intent" not in text and "## Spec" not in text and "## Plan" not in text


def test_a_second_run_refuses_rather_than_overwriting(project):
    assert start(project, "--slug", "a-round", "--new").returncode == 0
    second = start(project, "--slug", "a-round", "--new")
    assert second.returncode != 0
    assert "exists" in second.stderr


def test_a_slug_that_is_not_kebab_case_is_refused(project):
    assert start(project, "--slug", "Rewrite The Loader", "--new").returncode != 0
    assert start(project, "--slug", "rewrite_the_loader", "--new").returncode != 0


def test_a_store_in_an_older_format_is_refused(project):
    (project / "docs" / "atlas" / "VERSION").write_text("2\n", encoding="utf-8")
    proc = start(project, "--slug", "a-round", "--new")
    assert proc.returncode != 0
