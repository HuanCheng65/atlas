"""Internal helpers shared across atlas record scripts.

A record is `docs/atlas/records/NNN-slug.md`. The filename is authoritative:
wikilinks resolve by filename, so `id` and `slug` in frontmatter must agree
with it. Frontmatter carries identity and machine summaries only — every
relation between records lives in the body as a wikilink.
"""
import os
import re
import tempfile
import unicodedata
from pathlib import Path

import yaml

ATLAS = Path("docs/atlas")
RECORDS = ATLAS / "records"

TYPES = ("decision", "experiment", "question", "memory")

# `NNN-slug`: at least three digits, zero-padded, then a lowercase slug.
STEM_RE = re.compile(r"^(\d{3,})-([a-z0-9]+(?:-[a-z0-9]+)*)$")

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


class _RecordLoader(yaml.SafeLoader):
    """SafeLoader that keeps `YYYY-MM-DD` as a string.

    Default SafeLoader resolves it to `date` via the implicit timestamp
    resolver, which makes round-trips unstable. Dropping the resolver on
    BOTH loader and dumper keeps the plain form stable.
    """


class _RecordDumper(yaml.SafeDumper):
    """SafeDumper matching record frontmatter:
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


_drop_timestamp_resolver(_RecordLoader)
_drop_timestamp_resolver(_RecordDumper)


def _flow_list_representer(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


_RecordDumper.add_representer(list, _flow_list_representer)


def parse_md(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta = yaml.load(m.group(1), Loader=_RecordLoader) or {}
    return meta, m.group(2)


def dump_md(meta, body):
    yaml_str = yaml.dump(
        meta,
        Dumper=_RecordDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=10**6,
    )
    return f"---\n{yaml_str}---\n{body}"


def display_width(text):
    """Rendered width, counting CJK and other wide characters as two columns.

    Titles are capped by width rather than character count: a 40-character
    Chinese title carries roughly as much as an 80-character English one and
    occupies the same room in an index line.
    """
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
               for ch in text)


def split_stem(stem):
    """`047-register-cliff` -> (47, 'register-cliff'). Raises on a bad stem."""
    m = STEM_RE.match(stem)
    if not m:
        raise ValueError(f"bad record filename stem: {stem!r} (want NNN-slug)")
    return int(m.group(1)), m.group(2)


def format_stem(rid, slug):
    return f"{rid:03d}-{slug}"


def record_paths():
    if not RECORDS.exists():
        return []
    return sorted(p for p in RECORDS.glob("*.md") if p.name != "_index.md")


def load_all():
    """Return {id: Record} for every record on disk, keyed by integer id.

    Reads bodies too — relations live there, so no caller can work without
    them and a body-less variant would only invite a second read.

    Files whose name does not parse are skipped rather than raising — every
    caller wants the store it can read, and validate reports the unreadable
    names separately so they are never lost.
    """
    records = {}
    for path in record_paths():
        try:
            rid, slug = split_stem(path.stem)
        except ValueError:
            continue
        meta, body = parse_md(path.read_text(encoding="utf-8"))
        records[rid] = Record(id=rid, slug=slug, path=path, meta=meta, body=body)
    return records


class Record:
    __slots__ = ("id", "slug", "path", "meta", "body")

    def __init__(self, id, slug, path, meta, body):
        self.id = id
        self.slug = slug
        self.path = path
        self.meta = meta
        self.body = body

    @property
    def stem(self):
        return format_stem(self.id, self.slug)

    @property
    def type(self):
        return self.meta.get("type")

    @property
    def title(self):
        return self.meta.get("title")

    def __repr__(self):
        return f"<Record {self.stem}>"


def next_id(records=None):
    """One monotonic counter across every type. Ids are never reused: a
    deleted record's number stays retired so old links keep their meaning."""
    if records is None:
        records = load_all()
    return (max(records) + 1) if records else 1


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


def save_record(record):
    atomic_write(record.path, dump_md(record.meta, record.body))
