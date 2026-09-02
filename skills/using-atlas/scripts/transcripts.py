#!/usr/bin/env python3
"""Search this machine's agent transcripts for the current project.

The record store holds what was worth keeping. This reads the other half —
the raw conversation, which is complete, recent, and disposable — for the two
questions the store cannot answer: what was I doing on some past day, and did
I already try this.

**This machine only.** Transcripts live outside the repository and are pruned
after a few weeks, so two machines working on one project never share them.
That is not a gap to close: wanting a transcript to be durable or visible
elsewhere is the signal that it should have been a record.

**Coupled on purpose, and narrowly.** Reading a transcript means reading some
harness's private on-disk format, which will change. The coupling is confined
to the adapters below; each one knows where its harness keeps files, how it
maps a project path to them, and what its fields are called. Everything above
that line works in terms of Session and Message.

Which harness you are running under is never asked. "What did I do here last
Tuesday" does not depend on the answer, so every adapter that finds data for
this project is searched and each result says where it came from.

    transcripts.py list
    transcripts.py grep "register cliff"
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

MAX_OUTPUT_BYTES = 12000


class Session:
    __slots__ = ("harness", "id", "title", "start", "end", "count", "source")

    def __init__(self, harness, id, title, start, end, count, source):
        self.harness = harness
        self.id = id
        self.title = title
        self.start = start
        self.end = end
        self.count = count
        self.source = source

    @property
    def short(self):
        return self.id[:8]


class ClaudeCode:
    """Claude Code keeps one JSONL per session under a directory named after
    the project path with separators flattened to hyphens."""

    name = "claude-code"

    def __init__(self):
        # Both overrides are the harness's own: CLAUDE_CONFIG_DIR relocates
        # the config directory, and CLAUDE_CODE_PROJECT_DIR_NAME replaces the
        # flattened path, which the mangling below would otherwise get wrong.
        config = os.environ.get("CLAUDE_CONFIG_DIR") or (Path.home() / ".claude")
        self.root = Path(config) / "projects"
        self.dir_name = os.environ.get("CLAUDE_CODE_PROJECT_DIR_NAME")

    def available(self):
        return self.root.is_dir()

    def _dir_for(self, cwd):
        return self.root / (self.dir_name or re.sub(r"[/.]", "-", str(cwd)))

    @staticmethod
    def _text(record):
        """Prose only. Tool calls and their results are the bulk of a
        transcript's bytes and none of its meaning."""
        message = record.get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        if not isinstance(content, list):
            return ""
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")

    def _records(self, path):
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    def sessions_for(self, cwd):
        directory = self._dir_for(cwd)
        if not directory.is_dir():
            return []
        sessions = []
        for path in directory.glob("*.jsonl"):
            title, stamps, count = None, [], 0
            for record in self._records(path):
                if record.get("type") == "ai-title":
                    title = record.get("aiTitle") or title
                    continue
                # Count what grep would search, not what the file holds: a
                # record carrying only a tool result is most of the file and
                # none of the conversation.
                if not self._keep(record) or not self._text(record).strip():
                    continue
                count += 1
                if record.get("timestamp"):
                    stamps.append(record["timestamp"])
            if not count:
                continue
            sessions.append(Session(
                harness=self.name, id=path.stem, title=title,
                start=min(stamps) if stamps else "", end=max(stamps) if stamps else "",
                count=count, source=path,
            ))
        return sessions

    @staticmethod
    def _keep(record):
        if record.get("type") not in ("user", "assistant"):
            return False
        # isMeta marks injected context (hook output, reminders); isSidechain
        # marks subagent traffic. Neither is anything a person said or read.
        return not record.get("isMeta") and not record.get("isSidechain")

    def messages(self, session):
        for record in self._records(session.source):
            if not self._keep(record):
                continue
            text = self._text(record).strip()
            if text:
                yield (record.get("timestamp", ""),
                       (record.get("message") or {}).get("role") or record["type"],
                       text)


ADAPTERS = [ClaudeCode()]


def collect(cwd):
    sessions = []
    for adapter in ADAPTERS:
        if adapter.available():
            sessions.extend(adapter.sessions_for(cwd))
    return sorted(sessions, key=lambda s: s.end, reverse=True)


def adapter_for(session):
    return next(a for a in ADAPTERS if a.name == session.harness)


def short_time(stamp):
    try:
        return datetime.fromisoformat(stamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return stamp[:16]


def cmd_list(args):
    sessions = collect(Path.cwd())
    if not sessions:
        print(f"No transcripts on this machine for {Path.cwd()}.")
        return
    print(f"{len(sessions)} session(s) for {Path.cwd()}, newest first. "
          f"This machine only.\n")
    for s in sessions[:args.limit]:
        span = short_time(s.start)
        if s.end[:16] != s.start[:16]:
            tail = short_time(s.end)
            span += " → " + (tail[11:] if tail[:10] == span[:10] else tail)
        print(f"{s.short}  {span:<27} {s.count:>4} msg  {s.title or '(untitled)'}")
    if len(sessions) > args.limit:
        print(f"\n… {len(sessions) - args.limit} older, pass --limit to see them.")


def cmd_grep(args):
    try:
        pattern = re.compile(args.pattern, re.IGNORECASE)
    except re.error as exc:
        sys.exit(f"ERROR: bad pattern: {exc}")

    sessions = collect(Path.cwd())
    written, hits, truncated = 0, 0, False
    out = []
    for session in sessions:
        if args.session and not session.id.startswith(args.session):
            continue
        for stamp, role, text in adapter_for(session).messages(session):
            if args.since and stamp[:10] < args.since:
                continue
            lines = text.splitlines()
            for n, line in enumerate(lines):
                if not pattern.search(line):
                    continue
                hits += 1
                window = lines[max(0, n - args.context): n + args.context + 1]
                block = (f"── {session.harness} {session.short} "
                         f"{short_time(stamp)} {role}\n"
                         + "\n".join(f"   {ln}" for ln in window) + "\n")
                written += len(block.encode("utf-8"))
                if written > args.max_bytes:
                    truncated = True
                    break
                out.append(block)
            if truncated:
                break
        if truncated:
            break

    print("".join(out), end="")
    if not hits:
        print(f"No match for {args.pattern!r} in {len(sessions)} session(s) "
              f"on this machine.")
    elif truncated:
        print(f"… output capped at {args.max_bytes} bytes; narrow the pattern, "
              f"or pass --session to search one.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="sessions for this project, newest first")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(func=cmd_list)

    p_grep = sub.add_parser("grep", help="search prose across those sessions")
    p_grep.add_argument("pattern")
    p_grep.add_argument("--context", type=int, default=1, help="lines either side")
    p_grep.add_argument("--since", help="only messages on or after YYYY-MM-DD")
    p_grep.add_argument("--session", help="restrict to one session id prefix")
    p_grep.add_argument("--max-bytes", type=int, default=MAX_OUTPUT_BYTES)
    p_grep.set_defaults(func=cmd_grep)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
