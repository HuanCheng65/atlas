#!/usr/bin/env python3
"""Open a new journal entry under docs/atlas/journal/.

The Context paragraph(s) come from stdin. The script handles timestamp,
filename date prefix, frontmatter scaffolding, and reindex.

Usage:
    echo "$context_body" | open.py \\
        --slug enforce-orient-and-interview-skills \\
        --project atlas \\
        --tags skills,hooks,dogfood \\
        [--related slug-a,slug-b] \\
        [--title "Optional title (default: derived from slug)"] \\
        [--at "2026-05-28 00:50"]   # backfill only; default = now

stdout: path of created file
stderr + non-zero exit on any error

Refuses to overwrite an existing file.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402


def slug_to_title(slug):
    return slug.replace("-", " ").capitalize()


def derive_project():
    """Project name from PROJECT.md's H1 (strips a leading 'Project:' prefix).
    Returns None when PROJECT.md or its H1 is missing."""
    p = Path("PROJECT.md")
    if not p.exists():
        return None
    m = re.search(r"^#\s+(.+)$", p.read_text(encoding="utf-8"), re.MULTILINE)
    if not m:
        return None
    name = re.sub(r"^Project:\s*", "", m.group(1).strip()).strip()
    return name or None


def parse_csv(s):
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser(
        description="Open a new journal entry. Context body via stdin."
    )
    ap.add_argument("--slug", required=True, help="kebab-case slug (no date prefix)")
    ap.add_argument(
        "--project",
        default=None,
        help="project name (default: derived from PROJECT.md's H1)",
    )
    ap.add_argument("--tags", default="", help="comma-separated tags")
    ap.add_argument("--related", default="", help="comma-separated related slugs / entity ids")
    ap.add_argument("--title", default=None, help="entry title (default: derived from slug)")
    ap.add_argument("--at", default=None, help="backfill timestamp 'YYYY-MM-DD HH:MM' (default: now)")
    args = ap.parse_args()

    _lib.validate_slug(args.slug)

    project = args.project or derive_project()
    if not project:
        _lib.die("could not derive a project name from PROJECT.md's H1 — pass --project")

    ts = _lib.parse_at(args.at) if args.at else _lib.now_str()
    date_str = ts.split(" ")[0]

    out_path = _lib.JOURNAL / f"{date_str}-{args.slug}.md"
    if out_path.exists():
        _lib.die(f"file already exists: {out_path}")

    if not _lib.JOURNAL.exists():
        _lib.die(
            f"{_lib.JOURNAL} not found — run from project root of an atlas-enabled project"
        )

    context_body = _lib.read_stdin_body(required=True, label="Context body")
    title = args.title or slug_to_title(args.slug)

    meta = {
        "date": date_str,
        "slug": args.slug,
        "project": project,
        "tags": parse_csv(args.tags),
        "status": "active",
        "opened": ts,
        "closed": None,
        "verification-result": None,
        "related": parse_csv(args.related),
    }

    body = f"\n# {title}\n\n## Context\n\n{context_body}\n\n## Work log\n"
    _lib.save_entry(out_path, meta, body)
    _lib.run_reindex()
    print(out_path)


if __name__ == "__main__":
    main()
