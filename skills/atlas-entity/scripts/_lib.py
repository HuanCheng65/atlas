"""Internal helpers shared across atlas-entity scripts.

YAML round-trip behavior mirrors atlas-log/scripts/_lib.py — kept as a
separate copy for skill self-containment, so when changing loader/dumper
behavior in either file, mirror it in the other.
"""
import os
import re
import tempfile
from pathlib import Path

import yaml

ATLAS = Path("docs/atlas")
TYPE_DIR = {"D": "decisions", "E": "experiments", "Q": "questions"}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


class _EntityLoader(yaml.SafeLoader):
    """SafeLoader that keeps `YYYY-MM-DD` as a string.

    Default SafeLoader resolves it to `date` via the implicit timestamp
    resolver, which makes round-trips unstable. Dropping the resolver on
    BOTH loader and dumper keeps the plain form stable.
    """


class _EntityDumper(yaml.SafeDumper):
    """SafeDumper matching existing entity frontmatter:
    - timestamp resolver removed (mirrors loader); plain-style stays plain
    - lists emitted in flow style (`[a, b]`) instead of block style
    """


def _drop_timestamp_resolver(cls):
    new = {}
    for ch, resolvers in cls.yaml_implicit_resolvers.items():
        kept = [(t, r) for (t, r) in resolvers if t != "tag:yaml.org,2002:timestamp"]
        if kept:
            new[ch] = kept
    cls.yaml_implicit_resolvers = new


_drop_timestamp_resolver(_EntityLoader)
_drop_timestamp_resolver(_EntityDumper)


def _flow_list_representer(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


_EntityDumper.add_representer(list, _flow_list_representer)


def parse_md(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta = yaml.load(m.group(1), Loader=_EntityLoader) or {}
    return meta, m.group(2)


def dump_md(meta, body):
    yaml_str = yaml.dump(
        meta,
        Dumper=_EntityDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=10**6,
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


def atomic_write(path, content):
    """Write content to path atomically (tmpfile in same dir + rename)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def save_entity(path, meta, body):
    atomic_write(path, dump_md(meta, body))


def ensure_list(meta, key):
    if meta.get(key) is None:
        meta[key] = []
    elif not isinstance(meta[key], list):
        raise ValueError(f"field `{key}` must be list, got {type(meta[key]).__name__}")
