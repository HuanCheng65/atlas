"""Internal helpers shared across atlas-entity scripts."""
import re
from pathlib import Path

import yaml

ATLAS = Path("docs/atlas")
TYPE_DIR = {"D": "decisions", "E": "experiments", "Q": "questions"}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


def parse_md(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, m.group(2)


def dump_md(meta, body):
    yaml_str = yaml.dump(
        meta, sort_keys=False, allow_unicode=True, default_flow_style=False
    )
    return f"---\n{yaml_str}---\n{body}"


def find_entity_file(entity_id):
    """Locate the file for an id like 'D-007'."""
    if "-" not in entity_id:
        raise ValueError(f"bad id: {entity_id}")
    type_letter = entity_id.split("-")[0]
    if type_letter not in TYPE_DIR:
        raise ValueError(f"unknown type in id: {entity_id}")
    target_dir = ATLAS / TYPE_DIR[type_letter]
    matches = list(target_dir.glob(f"{entity_id}-*.md"))
    if not matches:
        raise FileNotFoundError(f"no file for {entity_id} in {target_dir}")
    if len(matches) > 1:
        raise RuntimeError(f"multiple files for {entity_id}: {matches}")
    return matches[0]


def load_entity(entity_id):
    path = find_entity_file(entity_id)
    meta, body = parse_md(path.read_text(encoding="utf-8"))
    return path, meta, body


def save_entity(path, meta, body):
    path.write_text(dump_md(meta, body), encoding="utf-8")


def ensure_list(meta, key):
    if meta.get(key) is None:
        meta[key] = []
    elif not isinstance(meta[key], list):
        raise ValueError(f"field `{key}` must be list, got {type(meta[key]).__name__}")
