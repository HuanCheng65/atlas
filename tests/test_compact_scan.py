"""Tests for atlas-compact's scan.py — the maintenance agenda generator.

Builds a fixture store with known backlog and consolidation candidates,
then asserts each agenda section reports exactly them. `--today` pins the
clock so the agenda is deterministic.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"

SCAN = SKILLS / "atlas-compact" / "scripts" / "scan.py"
OPEN = SKILLS / "atlas-log" / "scripts" / "open.py"
APPEND = SKILLS / "atlas-log" / "scripts" / "append.py"
CLOSE = SKILLS / "atlas-log" / "scripts" / "close.py"
NEW = SKILLS / "atlas-entity" / "scripts" / "new.py"

TODAY = "2026-06-12"

PROJECT_MD = "# Project: Fixture\n\n## Background\n\nScan fixture.\n"


def run(script, *args, cwd, stdin=None):
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd, input=stdin, capture_output=True, text=True,
    )


def ok(script, *args, cwd, stdin=None):
    proc = run(script, *args, cwd=cwd, stdin=stdin)
    assert proc.returncode == 0, f"{script.name} failed:\n{proc.stderr}"
    return proc


def set_fields(path, **fields):
    text = path.read_text(encoding="utf-8")
    for key, value in fields.items():
        text = re.sub(rf"(?m)^{key}: .*$", f"{key}: {value}", text, count=1)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def store(tmp_path):
    """A store with one of everything the agenda should catch.

    - stale-work: active, last work-log entry 10 days before TODAY
    - fresh-work: active, work-log entry on TODAY
    - three closed entries tagged `perf` (cluster candidate), one of them
      also tagged `caching` and closed after Q-001 was raised
    - D-001/D-002 active, sharing tags [perf, caching] (overlap pair);
      D-001 pending, D-002 archival
    - Q-001 open, tagged [caching]
    """
    atlas = tmp_path / "docs" / "atlas"
    for sub in ("journal", "decisions", "experiments", "questions", "topics", "_templates"):
        (atlas / sub).mkdir(parents=True)
    for tpl in (REPO / "templates" / "_templates").glob("*.md"):
        shutil.copy(tpl, atlas / "_templates" / tpl.name)
    (tmp_path / "PROJECT.md").write_text(PROJECT_MD, encoding="utf-8")

    ok(OPEN, "--slug", "stale-work", "--at", "2026-05-30 10:00", cwd=tmp_path, stdin="x")
    ok(APPEND, "--slug", "stale-work", "--at", "2026-06-02 10:00", cwd=tmp_path, stdin="note")
    ok(OPEN, "--slug", "fresh-work", "--at", f"{TODAY} 09:00", cwd=tmp_path, stdin="x")
    ok(APPEND, "--slug", "fresh-work", "--at", f"{TODAY} 10:00", cwd=tmp_path, stdin="note")

    for i, (slug, tags, closed_at) in enumerate([
        ("perf-a", "perf", "2026-06-05 12:00"),
        ("perf-b", "perf", "2026-06-06 12:00"),
        ("perf-c", "perf,caching", "2026-06-07 12:00"),
    ]):
        ok(OPEN, "--slug", slug, "--tags", tags, "--at", "2026-06-04 10:00",
           cwd=tmp_path, stdin="x")
        ok(CLOSE, "--slug", slug, "--result", "passed", "--at", closed_at,
           cwd=tmp_path, stdin="done")

    for title, triage in [("First rule", "pending"), ("Second rule", "archival")]:
        proc = ok(NEW, "--type", "D", title, cwd=tmp_path)
        path = tmp_path / proc.stdout.strip().splitlines()[-1]
        set_fields(path, status="active", triage=triage,
                   tags="[perf, caching]", date="2026-06-01")

    proc = ok(NEW, "--type", "Q", "Is the cache layer settled?", cwd=tmp_path)
    set_fields(tmp_path / proc.stdout.strip().splitlines()[-1],
               tags="[caching]", date="2026-06-01")

    return tmp_path


def agenda(store, *extra):
    return ok(SCAN, "--today", TODAY, *extra, cwd=store).stdout


def section(text, heading):
    return text.split(f"## {heading}")[1].split("## ")[0]


def test_stale_actives(store):
    out = agenda(store)
    sec = section(out, "Stale active entries")
    assert "stale-work" in sec and "10 days" in sec
    assert "fresh-work" not in sec


def test_pending_triage(store):
    sec = section(agenda(store), "Decisions pending triage")
    assert "D-001" in sec and "First rule" in sec
    assert "D-002" not in sec


def test_open_questions_with_age(store):
    sec = section(agenda(store), "Open questions")
    assert "Q-001" in sec and "11 days old" in sec


def test_possibly_answered_hint(store):
    sec = section(agenda(store), "Possibly answered")
    assert "Q-001" in sec and "perf-c" in sec and "caching" in sec
    assert "perf-a" not in sec  # no tag overlap with the question


def test_decision_overlap_pair(store):
    sec = section(agenda(store), "Decision pairs sharing")
    assert "D-001 + D-002" in sec and "caching, perf" in sec


def test_tag_clusters_and_topics(store):
    sec = section(agenda(store), "Tag clusters")
    assert "**perf** (3)" in sec
    assert "**caching**" not in sec  # only 1 closed entry, below cluster-min
    assert "existing topics: (none)" in sec

    (store / "docs" / "atlas" / "topics" / "perf-lessons.md").write_text("# x\n")
    sec = section(agenda(store), "Tag clusters")
    assert "perf-lessons" in sec


def test_last_compact_run(store):
    assert "Last compact run: never" in agenda(store)
    ok(OPEN, "--slug", "compact-run", "--tags", "compact", "--at", "2026-06-08 10:00",
       cwd=store, stdin="x")
    ok(CLOSE, "--slug", "compact-run", "--result", "passed", "--at", "2026-06-08 11:00",
       cwd=store, stdin="done")
    assert "Last compact run: 2026-06-08" in agenda(store)


def test_agenda_deterministic(store):
    assert agenda(store) == agenda(store)


def test_stale_threshold_flag(store):
    sec = section(agenda(store, "--stale-days", "30"), "Stale active entries")
    assert "stale-work" not in sec
