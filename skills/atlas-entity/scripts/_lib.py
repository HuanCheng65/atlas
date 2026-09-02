"""Internal helpers shared across atlas record scripts.

A record is `docs/atlas/records/NNN-slug.md`. The filename is authoritative:
wikilinks resolve by filename, so `id` and `slug` in frontmatter must agree
with it. Frontmatter carries identity and machine summaries only — every
relation between records lives in the body as a wikilink.
"""
import hashlib
import os
import re
import tempfile
import unicodedata
from pathlib import Path

import yaml

ATLAS = Path("docs/atlas")
RECORDS = ATLAS / "records"
VERSION_FILE = ATLAS / "VERSION"

# Written once by the v1 migration and kept forever. The migration renumbers
# every record, and pre-v2 identifiers had escaped into documents the store
# does not own — project docs, result files, even a script's filename. Those
# are prose and stay as they are; this table is what keeps them resolvable.
ID_MAP_FILE = ATLAS / "archive" / "v1-id-map.tsv"

# Bumped by any change that makes a store unreadable to the previous scripts.
# Without this, new scripts read an old store as an empty one and report
# success — a 29-entity store validated OK and loaded as no memory at all.
STORE_VERSION = 2

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


def store_version():
    """The store's format version.

    The file only came in with v2, so its absence is v1 rather than a
    question — there is no version of atlas that wrote a store without it
    and meant something else.
    """
    if not VERSION_FILE.exists():
        return 1
    raw = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not raw.isdigit():
        raise ValueError(f"{VERSION_FILE} should hold a version number, got {raw!r}")
    return int(raw)


def version_complaint():
    """The reason these scripts must not read this store, or None if they may.

    Every entry point calls this. A format mismatch has to be loud: read as
    data, an unmigrated store looks exactly like an empty one, and an empty
    store is a perfectly plausible thing to have.
    """
    if not ATLAS.exists():
        return None
    found = store_version()
    if found == STORE_VERSION:
        return None
    if found > STORE_VERSION:
        return (f"{ATLAS} is v{found} and these scripts read v{STORE_VERSION} — "
                f"the store was written by a newer atlas. Update the skills.")
    if found == 1:
        return (f"{ATLAS} has no VERSION file, so it is a pre-record store (v1) and "
                f"these scripts read v{STORE_VERSION}. Run "
                f"atlas-entity/scripts/migrate_v1_to_v2.py --dry-run first; reading "
                f"it as-is would report an empty store. If the store is genuinely "
                f"empty, run atlas-init to stamp it instead.")
    return (f"{ATLAS} is v{found} and these scripts read v{STORE_VERSION}. "
            f"Run the migration for that step.")


def require_version():
    complaint = version_complaint()
    if complaint:
        raise SystemExit(f"ERROR: {complaint}")


def fingerprint():
    """Identity of the store's contents, cheap enough to compute per tool call.

    `_index.md` is excluded because it is derived: regenerating it must not
    look like a change to what it was derived from.
    """
    parts = []
    for path in sorted(RECORDS.glob("*.md")):
        if path.name == "_index.md":
            continue
        stat = path.stat()
        parts.append(f"{path.name}\t{stat.st_mtime_ns}\t{stat.st_size}")
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def fingerprint_cache():
    """Where the post-write guard keeps the last state it accepted.

    Keyed by project and held outside the repository. Session start seeds it
    so that a difference means this session changed something; losing the file
    costs one baseline, never a wrong answer.
    """
    key = hashlib.sha256(str(Path.cwd()).encode("utf-8")).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / f"atlas-store-guard-{key}"


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
