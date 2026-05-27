#!/usr/bin/env python3
"""Create a new entity (D/E/Q) under docs/atlas/.

Usage:
    new.py --type D "title goes here"
    new.py --type E "Kuairand-1K B-adaptive run"
    new.py --type Q "does gamma generalize across batch sizes"
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

# allow direct invocation without PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))
import _lib  # noqa: E402

TYPE_TEMPLATE = {"D": "decision.md", "E": "experiment.md", "Q": "question.md"}


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60]


def next_id(type_letter):
    target_dir = _lib.ATLAS / _lib.TYPE_DIR[type_letter]
    target_dir.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(rf"^{type_letter}-(\d+)")
    existing = []
    for p in target_dir.glob(f"{type_letter}-*.md"):
        m = pattern.match(p.name)
        if m:
            existing.append(int(m.group(1)))
    n = max(existing, default=0) + 1
    return f"{type_letter}-{n:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", required=True, choices=["D", "E", "Q"])
    ap.add_argument("title")
    args = ap.parse_args()

    template_path = _lib.ATLAS / "_templates" / TYPE_TEMPLATE[args.type]
    if not template_path.exists():
        sys.exit(f"ERROR: template not found at {template_path}")

    entity_id = next_id(args.type)
    slug = slugify(args.title)
    today = datetime.date.today().isoformat()

    content = template_path.read_text(encoding="utf-8")
    content = (
        content.replace("{{ID}}", entity_id)
        .replace("{{TITLE}}", args.title)
        .replace("{{DATE}}", today)
        .replace("{{SLUG}}", slug)
    )

    out_path = _lib.ATLAS / _lib.TYPE_DIR[args.type] / f"{entity_id}-{slug}.md"
    if out_path.exists():
        sys.exit(f"ERROR: file already exists: {out_path}")
    out_path.write_text(content, encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
