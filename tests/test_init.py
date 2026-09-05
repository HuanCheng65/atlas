"""Tests for `bin/atlas-init`, which creates a store in a new project.

Both properties here were regressions, not hypotheticals. Bumping the store
format to v3 left atlas-init stamping a literal 2, so every store it created
was immediately refused as out of date by the scripts that had just created
it; and the store README it copies is a duplicate of this repository's own,
which drifted when only one of the two was edited.
"""
import filecmp
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
INIT = REPO / "bin" / "atlas-init"

sys.path.insert(0, str(REPO / "skills" / "atlas-entity" / "scripts"))
import _lib  # noqa: E402


@pytest.fixture
def project(tmp_path):
    subprocess.run([str(INIT)], cwd=tmp_path, check=True,
                   capture_output=True, env={**os.environ})
    return tmp_path


def test_a_new_store_is_stamped_with_the_version_the_scripts_read(project):
    stamped = (project / "docs" / "atlas" / "VERSION").read_text().strip()
    assert stamped == str(_lib.STORE_VERSION)


def test_a_new_store_is_readable_by_the_scripts_that_made_it(project):
    proc = subprocess.run(
        [sys.executable, str(REPO / "skills" / "atlas-entity" / "scripts" / "validate.py")],
        cwd=project, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def test_the_shipped_store_readme_matches_this_project_s_own(project):
    # The template is copied verbatim into every new store, so an edit to one
    # and not the other ships a description of a layout that no longer exists.
    assert filecmp.cmp(REPO / "templates" / "README.md",
                       REPO / "docs" / "atlas" / "README.md", shallow=False)
