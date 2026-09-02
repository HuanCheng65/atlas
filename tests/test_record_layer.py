"""Regression tests for the atlas record layer.

Each test builds a throwaway store under tmp_path and runs the real scripts
against it via subprocess, exactly as the agent does (CWD = project root).
Scripts resolve from this repo's skills/ tree, not from ~/.claude/skills, so
the working copy is what gets exercised.

Run: .venv/bin/python -m pytest tests/
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills" / "atlas-entity" / "scripts"

NEW = SCRIPTS / "new.py"
VALIDATE = SCRIPTS / "validate.py"
REINDEX = SCRIPTS / "reindex.py"
RENAME = SCRIPTS / "rename.py"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)

PROJECT_MD = """\
# Project: Fixture

## Background

Fixture project for record-layer regression tests.
"""


def run(script, *args, cwd, stdin=None):
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd, input=stdin, capture_output=True, text=True,
    )


def ok(script, *args, cwd, stdin=None):
    proc = run(script, *args, cwd=cwd, stdin=stdin)
    assert proc.returncode == 0, f"{script.name} failed:\n{proc.stdout}\n{proc.stderr}"
    return proc


def fails(script, *args, cwd, stdin=None):
    proc = run(script, *args, cwd=cwd, stdin=stdin)
    assert proc.returncode != 0, f"{script.name} unexpectedly succeeded:\n{proc.stdout}"
    return proc


def frontmatter(path):
    m = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    assert m, f"no frontmatter in {path}"
    return yaml.safe_load(m.group(1))


def body_of(path):
    m = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    return m.group(2)


def created(proc, project):
    return project / proc.stdout.strip().splitlines()[-1]


def set_body(path, body):
    meta_text = FRONTMATTER_RE.match(path.read_text(encoding="utf-8")).group(1)
    path.write_text(f"---\n{meta_text}\n---\n{body}", encoding="utf-8")


def set_field(path, key, value):
    text = path.read_text(encoding="utf-8")
    assert re.search(rf"(?m)^{key}: ", text), f"{key} not in {path.name}"
    path.write_text(re.sub(rf"(?m)^{key}: .*$", f"{key}: {value}", text, count=1),
                    encoding="utf-8")


@pytest.fixture
def project(tmp_path):
    (tmp_path / "docs" / "atlas").mkdir(parents=True)
    (tmp_path / "docs" / "atlas" / "VERSION").write_text("2\n", encoding="utf-8")
    (tmp_path / "PROJECT.md").write_text(PROJECT_MD, encoding="utf-8")
    return tmp_path


@pytest.fixture
def two_records(project):
    """A question and the experiment that answers it — the smallest store
    that exercises a typed edge."""
    ok(NEW, "--type", "question", "--title", "Does the register budget bind",
       "--new-tag", "h20,occupancy", cwd=project, stdin="Nothing pins it yet.\n")
    ok(NEW, "--type", "experiment", "--title", "The register cliff is at 128",
       "--tags", "h20",
       "--hypothesis", "h", "--config", "c", "--result", "r",
       "--conclusion", "cc", "--artifacts", "a",
       cwd=project,
       stdin="Measured. (answers:: [[001-does-the-register-budget-bind]])\n")
    return project


def records(project):
    return project / "docs" / "atlas" / "records"


# ---------- new.py ----------

def test_new_writes_flat_numbered_record(project):
    proc = ok(NEW, "--type", "decision", "--title", "Plain text and git",
              "--new-tag", "storage", cwd=project, stdin="Because databases rot.\n")
    path = created(proc, project)
    assert path.name == "001-plain-text-and-git.md"
    assert path.parent == records(project)
    meta = frontmatter(path)
    assert meta == {"id": 1, "title": "Plain text and git",
                    "date": meta["date"], "type": "decision", "tags": ["storage"]}


def test_counter_is_shared_across_types(project):
    ok(NEW, "--type", "decision", "--title", "First", "--new-tag", "x",
       cwd=project, stdin="body\n")
    proc = ok(NEW, "--type", "question", "--title", "Second", "--tags", "x",
              cwd=project, stdin="body\n")
    assert created(proc, project).name.startswith("002-")


def test_unknown_tag_is_refused_with_the_vocabulary(two_records):
    proc = fails(NEW, "--type", "decision", "--title", "T", "--tags", "novel",
                 cwd=two_records, stdin="body\n")
    assert "novel" in proc.stderr
    assert "h20 (2)" in proc.stderr


def test_new_tag_flag_admits_a_tag(two_records):
    ok(NEW, "--type", "decision", "--title", "T", "--new-tag", "novel",
       cwd=two_records, stdin="body\n")


def test_cjk_title_without_slug_is_refused(project):
    proc = fails(NEW, "--type", "memory", "--title", "寄存器悬崖在 128",
                 "--new-tag", "h20", cwd=project, stdin="body\n")
    assert "--slug" in proc.stderr


def test_cjk_title_with_explicit_slug_is_accepted(project):
    proc = ok(NEW, "--type", "memory", "--title", "寄存器悬崖在 128",
              "--slug", "register-cliff-128", "--new-tag", "h20",
              cwd=project, stdin="改估计器前先看 REG。\n")
    assert created(proc, project).name == "001-register-cliff-128.md"


def test_body_is_required(project):
    proc = fails(NEW, "--type", "decision", "--title", "T", "--new-tag", "x",
                 cwd=project, stdin="   \n")
    assert "stdin" in proc.stderr


def test_experiment_requires_its_summary_fields(project):
    proc = fails(NEW, "--type", "experiment", "--title", "T", "--new-tag", "x",
                 "--hypothesis", "h", cwd=project, stdin="body\n")
    assert "--config" in proc.stderr


# ---------- validate.py ----------

def test_validate_passes_a_clean_store(two_records):
    proc = ok(VALIDATE, cwd=two_records)
    assert "2 records" in proc.stdout


def test_derived_field_in_frontmatter_is_refused(two_records):
    path = records(two_records) / "001-does-the-register-budget-bind.md"
    path.write_text(path.read_text(encoding="utf-8").replace(
        "type: question", "type: question\nstatus: open"), encoding="utf-8")
    proc = fails(VALIDATE, cwd=two_records)
    assert "`status` is derived" in proc.stdout


def test_forward_reference_is_refused(two_records):
    set_body(records(two_records) / "001-does-the-register-budget-bind.md",
             "See [[002-the-register-cliff-is-at-128]].\n")
    proc = fails(VALIDATE, cwd=two_records)
    assert "did not exist when this record was written" in proc.stdout


def test_memory_records_may_reference_later_records(two_records):
    ok(NEW, "--type", "memory", "--title", "Check REG before touching the estimator",
       "--tags", "h20", cwd=two_records, stdin="Evidence: [[002-the-register-cliff-is-at-128]].\n")
    ok(NEW, "--type", "decision", "--title", "Later", "--tags", "h20",
       cwd=two_records, stdin="body\n")
    set_body(records(two_records) / "003-check-reg-before-touching-the-estimator.md",
             "Superseded evidence: [[004-later]].\n")
    ok(VALIDATE, cwd=two_records)


def test_unknown_verb_is_refused(two_records):
    path = records(two_records) / "002-the-register-cliff-is-at-128.md"
    path.write_text(path.read_text(encoding="utf-8").replace("(answers::", "(invalidates::"),
                    encoding="utf-8")
    proc = fails(VALIDATE, cwd=two_records)
    assert "unknown edge `invalidates::`" in proc.stdout


def test_typed_edge_may_not_point_forward(two_records):
    set_body(records(two_records) / "001-does-the-register-budget-bind.md",
             "(refutes:: [[002-the-register-cliff-is-at-128]])\n")
    proc = fails(VALIDATE, cwd=two_records)
    assert "a typed edge is declared on the newer record" in proc.stdout


def test_overlong_title_is_refused(two_records):
    set_field(records(two_records) / "001-does-the-register-budget-bind.md",
              "title", "x" * 95)
    proc = fails(VALIDATE, cwd=two_records)
    assert "95 columns wide" in proc.stdout


def test_cjk_title_counts_two_columns(two_records):
    set_field(records(two_records) / "001-does-the-register-budget-bind.md",
              "title", "题" * 46)
    proc = fails(VALIDATE, cwd=two_records)
    assert "92 columns wide" in proc.stdout


def test_dangling_link_is_refused(two_records):
    set_body(records(two_records) / "002-the-register-cliff-is-at-128.md",
             "See [[999-does-not-exist]].\n")
    proc = fails(VALIDATE, cwd=two_records)
    assert "does not resolve" in proc.stdout


def test_link_inside_a_code_fence_is_not_a_relation(two_records):
    set_body(records(two_records) / "002-the-register-cliff-is-at-128.md",
             "Write it as:\n\n```\n[[999-does-not-exist]]\n```\n\nand `[[998-nor-this]]` inline.\n")
    ok(VALIDATE, cwd=two_records)


def test_duplicate_number_is_refused(two_records):
    src = records(two_records) / "002-the-register-cliff-is-at-128.md"
    (records(two_records) / "002-a-second-claimant.md").write_text(
        src.read_text(encoding="utf-8"), encoding="utf-8")
    proc = fails(VALIDATE, cwd=two_records)
    assert "2 files claim this number" in proc.stdout


def test_filename_and_frontmatter_id_must_agree(two_records):
    set_field(records(two_records) / "002-the-register-cliff-is-at-128.md", "id", "7")
    proc = fails(VALIDATE, cwd=two_records)
    assert "frontmatter id is 7" in proc.stdout


def test_illegal_type_is_refused(two_records):
    set_field(records(two_records) / "001-does-the-register-budget-bind.md",
              "type", "note")
    proc = fails(VALIDATE, cwd=two_records)
    assert "illegal type 'note'" in proc.stdout


# ---------- reindex.py ----------

def test_index_shows_derived_standing_and_citations(two_records):
    ok(REINDEX, cwd=two_records)
    index = (records(two_records) / "_index.md").read_text(encoding="utf-8")
    assert "answered by 002" in index
    assert "cited by 1" in index
    assert "## Questions (1)" in index
    assert "## Experiments (1)" in index


def test_index_is_deterministic(two_records):
    ok(REINDEX, cwd=two_records)
    first = (records(two_records) / "_index.md").read_text(encoding="utf-8")
    ok(REINDEX, cwd=two_records)
    assert (records(two_records) / "_index.md").read_text(encoding="utf-8") == first


# ---------- rename.py ----------

def test_rename_rewrites_links_and_moves_the_file(two_records):
    ok(RENAME, "001", "register-budget", cwd=two_records)
    assert (records(two_records) / "001-register-budget.md").exists()
    assert not (records(two_records) / "001-does-the-register-budget-bind.md").exists()
    assert "[[001-register-budget]]" in body_of(
        records(two_records) / "002-the-register-cliff-is-at-128.md")
    ok(VALIDATE, cwd=two_records)


def test_rename_preserves_display_text(two_records):
    set_body(records(two_records) / "002-the-register-cliff-is-at-128.md",
             "As shown in [[001-does-the-register-budget-bind|the open question]].\n")
    ok(RENAME, "001", "register-budget", cwd=two_records)
    assert "[[001-register-budget|the open question]]" in body_of(
        records(two_records) / "002-the-register-cliff-is-at-128.md")


def test_rename_refuses_an_unknown_record(two_records):
    proc = fails(RENAME, "042", "whatever", cwd=two_records)
    assert "no record 042" in proc.stderr
