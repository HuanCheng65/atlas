"""Tests for the v2 -> v3 migration: work units become design documents.

The only thing this migration is allowed to do is rename the directory. The
files it moves are dated accounts of what was undertaken, so reshaping them
into the new skeleton would fabricate a history that did not happen — which is
why the check is byte-identity rather than a structural assertion.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MIGRATE = REPO / "skills" / "atlas-entity" / "scripts" / "migrate_v2_to_v3.py"
TEMPLATE = REPO / "templates" / "README.md"
V2_README = REPO / "tests" / "fixtures" / "v2-store-readme.md"

OLD_UNIT = """\
# Land intent, spec and plan as work units

## Intent

Settle where a plan lives.

## Spec

One file per unit.

## Plan

1. Write the script.
"""


def migrate(project, *args):
    return subprocess.run([sys.executable, str(MIGRATE), *args],
                          cwd=project, capture_output=True, text=True)


@pytest.fixture
def project(tmp_path):
    atlas = tmp_path / "docs" / "atlas"
    (atlas / "records").mkdir(parents=True)
    (atlas / "VERSION").write_text("2\n", encoding="utf-8")
    (atlas / "work").mkdir()
    (atlas / "work" / "2026-09-03-a-unit.md").write_text(OLD_UNIT, encoding="utf-8")
    shutil.copyfile(V2_README, atlas / "README.md")
    return tmp_path


def test_the_files_survive_byte_for_byte(project):
    proc = migrate(project)
    assert proc.returncode == 0, proc.stderr
    atlas = project / "docs" / "atlas"
    assert not (atlas / "work").exists()
    moved = atlas / "design" / "2026-09-03-a-unit.md"
    assert moved.read_text(encoding="utf-8") == OLD_UNIT
    assert (atlas / "VERSION").read_text(encoding="utf-8") == "3\n"


def test_an_untouched_store_readme_is_refreshed(project):
    # Left alone it would go on describing work/ and the three sections, in
    # the file a reader opens to learn what the layout is.
    assert migrate(project).returncode == 0
    readme = project / "docs" / "atlas" / "README.md"
    assert readme.read_text(encoding="utf-8") == TEMPLATE.read_text(encoding="utf-8")


def test_an_edited_store_readme_is_reported_not_overwritten(project):
    readme = project / "docs" / "atlas" / "README.md"
    edited = readme.read_text(encoding="utf-8") + "\n## Local note\n"
    readme.write_text(edited, encoding="utf-8")

    proc = migrate(project)
    assert proc.returncode == 0
    assert readme.read_text(encoding="utf-8") == edited
    assert "has local edits" in proc.stdout


def test_a_dry_run_touches_nothing(project):
    proc = migrate(project, "--dry-run")
    assert proc.returncode == 0, proc.stderr
    atlas = project / "docs" / "atlas"
    assert (atlas / "work" / "2026-09-03-a-unit.md").exists()
    assert not (atlas / "design").exists()
    assert (atlas / "VERSION").read_text(encoding="utf-8") == "2\n"
    assert (atlas / "README.md").read_text(encoding="utf-8") == V2_README.read_text(
        encoding="utf-8")


def test_running_twice_refuses_rather_than_merging(project):
    assert migrate(project).returncode == 0
    second = migrate(project)
    assert second.returncode != 0
    assert "already v3" in second.stderr


def test_a_store_with_no_work_directory_is_still_stamped(project):
    (project / "docs" / "atlas" / "work" / "2026-09-03-a-unit.md").unlink()
    (project / "docs" / "atlas" / "work").rmdir()
    assert migrate(project).returncode == 0
    assert (project / "docs" / "atlas" / "VERSION").read_text(
        encoding="utf-8") == "3\n"


def test_a_store_that_is_not_v2_is_refused(project):
    (project / "docs" / "atlas" / "VERSION").unlink()
    proc = migrate(project)
    assert proc.returncode != 0
    assert "v1" in proc.stderr
