"""Internal helpers shared across atlas-log scripts.

All journal mutations go through these helpers so timestamps are
generated deterministically (datetime.now) and never fabricated by the
agent. YAML round-trip behavior mirrors atlas-entity/scripts/_lib.py —
kept as a separate copy for skill self-containment, so when changing
loader/dumper behavior in either file, mirror it in the other.
"""
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import yaml

ATLAS = Path("docs/atlas")
JOURNAL = ATLAS / "journal"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def die(msg, code=1):
    """Exit with an ERROR:-prefixed message on stderr."""
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


class _JournalLoader(yaml.SafeLoader):
    """SafeLoader that keeps `YYYY-MM-DD` / `YYYY-MM-DD HH:MM` as strings.

    Default SafeLoader resolves these to `date` / `datetime` via the
    implicit timestamp resolver. That forces the dumper to quote them
    on round-trip (since they'd otherwise re-resolve as timestamps).
    Dropping the timestamp resolver on BOTH ends keeps the form stable.
    """


class _JournalDumper(yaml.SafeDumper):
    """SafeDumper matching existing hand-written journal frontmatter:
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


_drop_timestamp_resolver(_JournalLoader)
_drop_timestamp_resolver(_JournalDumper)


def _flow_list_representer(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


_JournalDumper.add_representer(list, _flow_list_representer)


def parse_md(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta = yaml.load(m.group(1), Loader=_JournalLoader) or {}
    return meta, m.group(2)


def dump_md(meta, body):
    yaml_str = yaml.dump(
        meta,
        Dumper=_JournalDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=10**6,
    )
    return f"---\n{yaml_str}---\n{body}"


def now_str():
    """Current local time, 'YYYY-MM-DD HH:MM'. Single source of truth."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def parse_at(s):
    """Validate a user-supplied --at value; return canonical string."""
    try:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M")
    except ValueError:
        die(f"--at must be 'YYYY-MM-DD HH:MM', got {s!r}")
    return dt.strftime("%Y-%m-%d %H:%M")


def validate_slug(slug):
    if not slug:
        die("slug is empty")
    if not SLUG_RE.match(slug):
        die(f"slug must be kebab-case [a-z0-9-]+, got {slug!r}")
    if DATE_PREFIX_RE.match(slug):
        die(f"slug must not include a date prefix, got {slug!r}")
    if len(slug) > 80:
        die(f"slug too long ({len(slug)} > 80)")


def find_entry(slug):
    """Locate the journal file for a bare slug. Returns Path.

    Matches exactly `YYYY-MM-DD-<slug>.md` — a plain `*-{slug}.md` glob
    would also hit entries whose slug merely ends in `-{slug}` and could
    silently write to the wrong file.

    Exits with ERROR if zero or multiple matches.
    """
    validate_slug(slug)
    if not JOURNAL.exists():
        die(f"{JOURNAL} not found — run from project root of an atlas-enabled project")
    name_re = re.compile(rf"^\d{{4}}-\d{{2}}-\d{{2}}-{re.escape(slug)}\.md$")
    matches = sorted(p for p in JOURNAL.glob(f"*-{slug}.md") if name_re.match(p.name))
    if not matches:
        die(f"no journal entry with slug {slug!r}")
    if len(matches) > 1:
        names = ", ".join(p.name for p in matches)
        die(f"multiple entries match slug {slug!r}: {names}")
    return matches[0]


def load_entry(slug):
    path = find_entry(slug)
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


def save_entry(path, meta, body):
    atomic_write(path, dump_md(meta, body))


def read_stdin_body(required=True, label="body"):
    """Read markdown body from stdin. Strips trailing whitespace, keeps inner blank lines."""
    if sys.stdin.isatty():
        if required:
            die(f"{label} must be supplied via stdin (got an interactive tty)")
        return ""
    data = sys.stdin.read().rstrip()
    if required and not data.strip():
        die(f"{label} is empty (stdin had no content)")
    return data


def run_reindex():
    """Invoke reindex.py's main(). Imported lazily to avoid import cycles at module load."""
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    try:
        import reindex  # noqa: E402
        reindex.main()
    finally:
        if str(script_dir) in sys.path:
            sys.path.remove(str(script_dir))
