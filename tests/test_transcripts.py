"""Tests for the transcript reader.

The store answers what was worth keeping; this answers what actually
happened. Both halves of that are load-bearing here: the prose has to come
through, and the ninety-odd percent that is tool traffic has to not.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TRANSCRIPTS = REPO / "skills" / "using-atlas" / "scripts" / "transcripts.py"


def record(**kwargs):
    return json.dumps(kwargs, ensure_ascii=False)


def text_message(role, text, stamp, **extra):
    return record(type=role, timestamp=stamp,
                  message={"role": role, "content": [{"type": "text", "text": text}]},
                  **extra)


def tool_message(stamp):
    """A user record carrying only a tool result — most of a real file."""
    return record(type="user", timestamp=stamp,
                  message={"role": "user", "content": [
                      {"type": "tool_result", "content": "40 lines of output"}]})


@pytest.fixture
def env(tmp_path):
    """A fake config directory holding one project's sessions."""
    project = tmp_path / "work"
    project.mkdir()
    config = tmp_path / "config"
    (config / "projects" / "fixture").mkdir(parents=True)
    return {
        "project": project,
        "sessions": config / "projects" / "fixture",
        "env": {**os.environ,
                "CLAUDE_CONFIG_DIR": str(config),
                "CLAUDE_CODE_PROJECT_DIR_NAME": "fixture"},
    }


def write_session(env, name, lines):
    (env["sessions"] / f"{name}.jsonl").write_text("\n".join(lines) + "\n",
                                                   encoding="utf-8")


def run(env, *args):
    return subprocess.run([sys.executable, str(TRANSCRIPTS), *args],
                          cwd=env["project"], env=env["env"],
                          capture_output=True, text=True)


def test_list_names_sessions_with_titles_and_counts(env):
    write_session(env, "aaaaaaaa1111", [
        record(type="ai-title", aiTitle="Kernel occupancy work"),
        text_message("user", "why is occupancy low", "2026-09-01T10:00:00Z"),
        text_message("assistant", "the register budget", "2026-09-01T10:05:00Z"),
    ])
    out = run(env, "list").stdout
    assert "aaaaaaaa" in out
    assert "Kernel occupancy work" in out
    assert "2 msg" in out
    assert "This machine only." in out


def test_tool_traffic_is_not_counted_as_conversation(env):
    write_session(env, "bbbbbbbb2222", [
        text_message("user", "hello", "2026-09-01T10:00:00Z"),
        *[tool_message("2026-09-01T10:01:00Z") for _ in range(20)],
    ])
    assert "1 msg" in run(env, "list").stdout


def test_injected_context_and_subagents_are_skipped(env):
    write_session(env, "cccccccc3333", [
        text_message("user", "a real question", "2026-09-01T10:00:00Z"),
        text_message("user", "hook output", "2026-09-01T10:00:01Z", isMeta=True),
        text_message("assistant", "subagent chatter", "2026-09-01T10:00:02Z",
                     isSidechain=True),
    ])
    assert "1 msg" in run(env, "list").stdout
    out = run(env, "grep", "output|chatter|question").stdout
    assert "a real question" in out
    assert "hook output" not in out
    assert "subagent chatter" not in out


def test_grep_labels_each_hit(env):
    write_session(env, "dddddddd4444", [
        record(type="ai-title", aiTitle="Titled"),
        text_message("assistant", "the register cliff is at 128",
                     "2026-09-01T11:30:00Z"),
    ])
    out = run(env, "grep", "register cliff").stdout
    assert "claude-code dddddddd" in out
    assert "2026-09-01 11:30" in out
    assert "assistant" in out
    assert "the register cliff is at 128" in out


def test_grep_shows_context_lines(env):
    write_session(env, "eeeeeeee5555", [
        text_message("assistant", "before\nMATCH HERE\nafter",
                     "2026-09-01T10:00:00Z"),
    ])
    out = run(env, "grep", "MATCH HERE", "--context", "1").stdout
    assert "before" in out and "after" in out
    assert "MATCH HERE" in out


def test_grep_caps_its_output(env):
    write_session(env, "ffffffff6666", [
        text_message("assistant", f"needle {n}", "2026-09-01T10:00:00Z")
        for n in range(500)
    ])
    out = run(env, "grep", "needle", "--max-bytes", "500").stdout
    assert len(out.encode("utf-8")) < 2000
    assert "capped at 500 bytes" in out


def test_since_filters_by_date(env):
    write_session(env, "aaaa11112222", [
        text_message("user", "old thing", "2026-08-01T10:00:00Z"),
        text_message("user", "new thing", "2026-09-01T10:00:00Z"),
    ])
    out = run(env, "grep", "thing", "--since", "2026-09-01").stdout
    assert "new thing" in out
    assert "old thing" not in out


def test_no_transcripts_says_so_rather_than_failing(env):
    proc = run(env, "list")
    assert proc.returncode == 0
    assert "No transcripts on this machine" in proc.stdout


def test_a_miss_reports_how_much_was_searched(env):
    write_session(env, "99999999aaaa", [
        text_message("user", "something", "2026-09-01T10:00:00Z"),
    ])
    out = run(env, "grep", "nothing like this").stdout
    assert "No match" in out
    assert "1 session(s)" in out
