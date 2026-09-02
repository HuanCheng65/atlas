"""Tests for the one-time D/E/Q -> record migration.

The fixture is written as raw old-format files rather than produced by a
script, because the scripts that produced that format are gone — the fixture
is what the store actually looked like, including the trailing-hyphen slugs
the old slugifier left behind.
"""
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills" / "atlas-entity" / "scripts"
MIGRATE = SCRIPTS / "migrate.py"
VALIDATE = SCRIPTS / "validate.py"

PROJECT_MD = """\
# Project: Fixture

## Background

Fixture project.

## Working rules

- Stay plain text (D-001)
- Titles state the answer (D-002)
"""

OLD = {
    "decisions/D-001-plain-text-and-git.md": """\
---
id: D-001
title: Plain text and git
date: 2026-01-05
status: active
tags: [storage]
related: [D-002]
source-journal: null
supersedes: []
superseded-by: []
affects: []
triage: promoted
source: bootstrap
---

# Plain text and git

Databases rot.
""",
    "decisions/D-002-titles-state-the-answer-and-not-merely-the-topic-at-hand-so-.md": """\
---
id: D-002
title: Titles state the answer
date: 2026-02-11
status: active
tags: [index]
related: []
source-journal: null
supersedes: [D-003]
superseded-by: []
affects: []
triage: promoted
---

# Titles state the answer

Replaces the earlier convention in D-003.
""",
    "decisions/D-003-titles-name-the-topic.md": """\
---
id: D-003
title: Titles name the topic
date: 2026-01-20
status: superseded
tags: [index]
related: []
source-journal: null
supersedes: []
superseded-by: [D-002]
affects: []
triage: archival
---

# Titles name the topic

The first convention.
""",
    "questions/Q-001-how-large-may-a-store-grow.md": """\
---
id: Q-001
title: How large may a store grow
date: 2026-01-06
status: open
tags: [scale]
related: [D-001]
source-journal: null
severity: medium
answered-by: null
---

# How large may a store grow

Unbounded growth would eventually defeat D-001.
""",
}


@pytest.fixture
def old_store(tmp_path):
    (tmp_path / "PROJECT.md").write_text(PROJECT_MD, encoding="utf-8")
    for rel, text in OLD.items():
        path = tmp_path / "docs" / "atlas" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    journal = tmp_path / "docs" / "atlas" / "journal"
    journal.mkdir(parents=True)
    (journal / "2026-01-05-first.md").write_text("---\nslug: first\n---\n\nwork\n",
                                                 encoding="utf-8")
    return tmp_path


def run(script, *args, cwd):
    return subprocess.run([sys.executable, str(script), *args],
                          cwd=cwd, capture_output=True, text=True)


def records(project):
    return project / "docs" / "atlas" / "records"


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---")[1])


def body(path):
    return path.read_text(encoding="utf-8").split("---", 2)[2]


def test_migration_produces_a_valid_store(old_store):
    assert run(MIGRATE, cwd=old_store).returncode == 0
    proc = run(VALIDATE, cwd=old_store)
    assert proc.returncode == 0, proc.stdout
    assert "4 records" in proc.stdout


def test_numbering_puts_cited_records_first(old_store):
    run(MIGRATE, cwd=old_store)
    names = sorted(p.name for p in records(old_store).glob("*.md") if p.name != "_index.md")
    # D-003 is cited by D-002, so it must take a lower number despite its id.
    order = {n.split("-", 1)[1].rsplit(".", 1)[0]: int(n.split("-")[0]) for n in names}
    assert order["titles-name-the-topic"] < order["titles-state-the-answer-and-not-merely-the-topic-at-hand-so"]


def test_prose_references_become_wikilinks(old_store):
    run(MIGRATE, cwd=old_store)
    text = "".join(body(p) for p in records(old_store).glob("*how-large-may-a-store-grow.md"))
    assert "[[" in text and "D-001" not in text


def test_supersedes_becomes_a_typed_edge(old_store):
    run(MIGRATE, cwd=old_store)
    path = next(records(old_store).glob("*titles-state-the-answer-*.md"))
    assert "(supersedes:: [[" in body(path)


def test_derived_fields_are_dropped(old_store):
    run(MIGRATE, cwd=old_store)
    for path in records(old_store).glob("[0-9]*.md"):
        meta = frontmatter(path)
        assert set(meta) <= {"id", "title", "date", "type", "tags"}


def test_trailing_hyphen_slug_is_normalised(old_store):
    run(MIGRATE, cwd=old_store)
    assert not any(p.stem.endswith("-") for p in records(old_store).glob("*.md"))


def test_journal_is_archived_untouched(old_store):
    before = (old_store / "docs" / "atlas" / "journal" / "2026-01-05-first.md").read_text()
    run(MIGRATE, cwd=old_store)
    archived = old_store / "docs" / "atlas" / "archive" / "journal" / "2026-01-05-first.md"
    assert archived.read_text() == before
    assert not (old_store / "docs" / "atlas" / "journal").exists()


def test_constitution_pointers_are_rewritten(old_store):
    run(MIGRATE, cwd=old_store)
    text = (old_store / "PROJECT.md").read_text(encoding="utf-8")
    assert "(D-001)" not in text
    assert "([[" in text


def test_dry_run_touches_nothing(old_store):
    proc = run(MIGRATE, "--dry-run", cwd=old_store)
    assert proc.returncode == 0
    assert not records(old_store).exists()
    assert (old_store / "docs" / "atlas" / "decisions").exists()


def test_forward_reference_is_reported(old_store):
    # D-003 is older and cited by D-002; make it cite D-002 back, which is the
    # shape migration cannot resolve on its own.
    path = old_store / "docs" / "atlas" / "decisions" / "D-003-titles-name-the-topic.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nReplaced by D-002.\n",
                    encoding="utf-8")
    proc = run(MIGRATE, "--dry-run", cwd=old_store)
    assert "forward reference" in proc.stdout


def test_answered_by_moves_the_edge_onto_the_answerer(old_store):
    # `answered-by` sits on the question and names its answerer, which is the
    # wrong end: the edge belongs on the record that did the answering.
    path = old_store / "docs" / "atlas" / "questions" / "Q-001-how-large-may-a-store-grow.md"
    path.write_text(path.read_text(encoding="utf-8").replace(
        "answered-by: null", "answered-by: D-002"), encoding="utf-8")
    assert run(MIGRATE, cwd=old_store).returncode == 0

    question = next(records(old_store).glob("*how-large-may-a-store-grow.md"))
    answerer = next(records(old_store).glob("*titles-state-the-answer-*.md"))
    assert "answers::" not in body(question)
    assert "(answers:: [[" in body(answerer)
    assert int(answerer.stem.split("-")[0]) > int(question.stem.split("-")[0])
    assert run(VALIDATE, cwd=old_store).returncode == 0


def test_overlong_title_is_reported(old_store):
    path = old_store / "docs" / "atlas" / "decisions" / "D-001-plain-text-and-git.md"
    path.write_text(path.read_text(encoding="utf-8").replace(
        "title: Plain text and git", "title: " + "x" * 95), encoding="utf-8")
    proc = run(MIGRATE, "--dry-run", cwd=old_store)
    assert "over the 90-column budget" in proc.stdout
