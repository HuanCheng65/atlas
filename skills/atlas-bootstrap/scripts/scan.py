#!/usr/bin/env python3
"""Scan project artifacts and produce a structured report for atlas-bootstrap.

Usage:
    scan.py [--output PATH]

Default output: /tmp/atlas-bootstrap-scan.yaml

Must be run from the project root.
"""
import argparse
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

DEFAULT_OUTPUT = "/tmp/atlas-bootstrap-scan.yaml"

DECISION_KEYWORDS = "decid|switch|migrat|adopt|refactor|rewrit|choose|chose|pick|select|drop|replace"
TODO_PATTERN = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b[:\s]")

IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__",
    "build", "dist", "target", ".next", ".cache", ".pytest_cache",
}

SOURCE_EXTENSIONS = {
    ".py", ".c", ".cpp", ".cc", ".h", ".hpp", ".cu", ".cuh",
    ".js", ".ts", ".jsx", ".tsx", ".rs", ".go", ".java", ".kt",
    ".swift", ".rb", ".scala", ".m", ".mm",
}


def run(cmd):
    """Run a shell command, return stdout. Empty string on error."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return ""
        return r.stdout
    except Exception:
        return ""


def get_git_remote():
    return run(["git", "config", "--get", "remote.origin.url"]).strip() or None


def get_recent_commits(n=50):
    out = run(["git", "log", "--oneline", "--no-merges", f"-{n}"])
    return [line.strip() for line in out.splitlines() if line.strip()]


def get_decision_commits():
    out = run([
        "git", "log",
        "--since=6.months.ago",
        "--pretty=format:%h|%ad|%s",
        "--date=short",
        f"--grep={DECISION_KEYWORDS}",
        "-i", "-E",
    ])
    commits = []
    for line in out.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            commits.append({
                "hash": parts[0],
                "date": parts[1],
                "subject": parts[2],
            })
    return commits


def find_doc_files():
    """Find common documentation files at project root and one level deep."""
    patterns = [
        r"^readme(\.md)?$",
        r"^changelog(\.md)?$",
        r"^contributing(\.md)?$",
        r"^architecture(\.md)?$",
        r"^claude\.md$",
        r"^agents\.md$",
        r"^gemini\.md$",
        r"^design\.md$",
        r"^project\.md$",
        r"^license(\.md)?$",
    ]
    found = []
    cwd = Path(".")
    for root, dirs, files in os.walk(cwd):
        depth = len(Path(root).relative_to(cwd).parts)
        if depth > 2:
            dirs.clear()
            continue
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            for pat in patterns:
                if re.match(pat, f, re.IGNORECASE):
                    found.append(str(Path(root) / f))
                    break
    return sorted(found)


def detect_frameworks():
    signals = {}
    if Path(".claude/superpowers").exists():
        signals["superpowers"] = "detected at .claude/superpowers/"
    if Path(".gsd").exists():
        signals["gsd"] = "detected at .gsd/"
    if Path("specs").is_dir() or Path("plans").is_dir():
        signals["spec_driven"] = "specs/ or plans/ directory at root"
    if Path("docs/adr").is_dir() or Path("adr").is_dir():
        signals["adr"] = "ADR directory found"
    if Path(".claude/skills").is_dir():
        skills = sorted(
            p.name for p in Path(".claude/skills").iterdir() if p.is_dir()
        )
        if skills:
            signals["claude_skills"] = skills
    return signals


def find_specs_and_plans():
    paths = []
    candidates = [
        ".claude/superpowers/plans", ".claude/superpowers/specs",
        "specs", "plans", "docs/specs", "docs/plans", "docs/adr",
    ]
    for d in candidates:
        p = Path(d)
        if p.is_dir():
            for f in p.rglob("*.md"):
                paths.append(str(f))
                if len(paths) >= 50:
                    return paths
    return paths


def language_breakdown():
    counter = Counter()
    cwd = Path(".")
    for root, dirs, files in os.walk(cwd):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in SOURCE_EXTENSIONS:
                counter[ext] += 1
    total = sum(counter.values())
    if total == 0:
        return {}
    return {
        ext: {"files": count, "pct": round(100 * count / total, 1)}
        for ext, count in counter.most_common(10)
    }


def find_todos(limit=20):
    cwd = Path(".")
    todos = []
    seen_files = 0
    for root, dirs, files in os.walk(cwd):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if Path(f).suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            path = Path(root) / f
            seen_files += 1
            if seen_files > 1000:
                return todos[:limit]
            try:
                with open(path, encoding="utf-8", errors="ignore") as fp:
                    for i, line in enumerate(fp, 1):
                        if TODO_PATTERN.search(line):
                            todos.append({
                                "file": str(path),
                                "line": i,
                                "text": line.strip()[:200],
                            })
                            if len(todos) >= limit * 3:
                                return todos[:limit]
            except Exception:
                continue
    return todos[:limit]


def top_level_structure():
    tree = []
    cwd = Path(".")
    for entry in sorted(cwd.iterdir()):
        if entry.name in IGNORE_DIRS or entry.name.startswith("."):
            continue
        if entry.is_dir():
            tree.append(entry.name + "/")
            try:
                for sub in sorted(entry.iterdir()):
                    if sub.name in IGNORE_DIRS or sub.name.startswith("."):
                        continue
                    suffix = "/" if sub.is_dir() else ""
                    tree.append(f"  {sub.name}{suffix}")
            except PermissionError:
                pass
        else:
            tree.append(entry.name)
    return tree


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    report = {
        "scanned_at": run(["date", "-Iseconds"]).strip() or "unknown",
        "project_dir": str(Path.cwd()),
        "git_remote": get_git_remote(),
        "languages": language_breakdown(),
        "top_level_structure": top_level_structure(),
        "existing_docs": find_doc_files(),
        "frameworks_detected": detect_frameworks(),
        "prior_specs_and_plans": find_specs_and_plans(),
        "recent_commits": get_recent_commits(50),
        "decision_signal_commits": get_decision_commits(),
        "todo_markers": find_todos(20),
    }

    output = yaml.dump(report, sort_keys=False, allow_unicode=True, default_flow_style=False)
    Path(args.output).write_text(output, encoding="utf-8")
    print(f"scan complete: {args.output}", file=sys.stderr)
    sys.stdout.write(output)


if __name__ == "__main__":
    main()
