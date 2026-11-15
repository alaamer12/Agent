#!/usr/bin/env python3
"""Unified skill and agent manager for the insource registry.

Commands
--------
    python manager.py skill <name> ...     link/copy skills (default command)
    python manager.py agent                deploy AGENTS.md to agent configs
    python manager.py lint                 validate SKILL.md descriptions and sync
    python manager.py viber                install every skill the Viber lifecycle uses

The default command is ``skill``, so ``python manager.py avatar`` and
``python manager.py skill avatar`` are equivalent.

Skills link into each agent's global skill directory by default. ``--into``
redirects them into a local project instead. ``--hard-copy`` copies instead of
linking and records a source path plus fingerprints so every later run can
report whether the copy is still in sync.

Examples
--------
    python manager.py skill avatar
    python manager.py avatar mine --agents opencode,gemini
    python manager.py skill --all --lock
    python manager.py skill avatar --into ./my-project
    python manager.py skill avatar --into ./my-project --hard-copy
    python manager.py skill --refresh
    python manager.py agent --hard-copy --agents claude,opencode
    python manager.py lint --strict
    python manager.py viber --into ./my-project --hard-copy
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence
from urllib.parse import unquote

__version__ = "2.1.0"

# ---------------------------------------------------------------------------
# optional dependencies
# ---------------------------------------------------------------------------

try:  # rich gives colour, boxes and wrapping; everything works without it
    from rich import box as rich_box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    RICH_AVAILABLE = True
except Exception:  # pragma: no cover - exercised only without rich
    Console = None  # type: ignore[assignment]
    Panel = None  # type: ignore[assignment]
    Table = None  # type: ignore[assignment]
    rich_box = None  # type: ignore[assignment]
    RICH_AVAILABLE = False

try:  # PyYAML parses every frontmatter shape correctly; fallback is minimal
    import yaml
except Exception:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------

DEFAULT_DESCRIPTION_LIMIT = 1024
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
INITIAL_VERSION = "1.0.0"
DB_APP_DIR = "insource-manager"
DB_FILE_NAME = "manager.db"
LEGACY_STORE_FILES = {"copies": "manager-copies.json", "lock": "skills-lock.json",
                      "versions": "manager-versions.json"}
SKIP_NAMES = {"Archive", "__pycache__", "node_modules", ".git", ".venv", "venv"}
MIGRATION_AGENTS = {"qoder", "gemini"}

AGENT_SKILL_SUBDIRS: dict[str, Path] = {
    "qoder": Path(".qoder") / "skills",
    "junie": Path(".junie") / "skills",
    "gemini": Path(".gemini") / "config" / "skills",
    "opencode": Path(".config") / "opencode" / "skills",
    "claude": Path(".claude") / "skills",
}
DEFAULT_AGENTS = list(AGENT_SKILL_SUBDIRS)

AGENT_MD_SUBDIRS: dict[str, list[Path]] = {
    "qoder": [Path(".qoder") / "agents.md"],
    "gemini": [
        Path(".gemini") / "AGENTS.md",
        Path(".gemini") / "antigravity" / "AGENTS.md",
        Path(".gemini") / "antigravity" / "global_rules.md",
    ],
    "claude": [Path(".claude") / "CLAUDE.md", Path(".claude") / "agents.md"],
    "junie": [Path(".junie") / "agents.md"],
    "opencode": [Path(".config") / "opencode" / "AGENTS.md"],
}

ALIASES = {
    "claude-code": "claude",
    "claudecode": "claude",
    "gemini-cli": "gemini",
    "geminicli": "gemini",
    "open-code": "opencode",
}

REGISTRY = Path(__file__).resolve().parent
COMMANDS = {"skill", "agent", "lint", "viber", "report", "find"}


class ManagerError(Exception):
    """A user-facing error; main() prints it without a traceback."""


# ---------------------------------------------------------------------------
# display layer
# ---------------------------------------------------------------------------


@dataclass
class DisplayConfig:
    quiet: bool = False
    color: bool = True
    verbose: bool = False


_DISPLAY = DisplayConfig()
_CONSOLE: Any = None


def configure_display(*, quiet: bool, color: bool, verbose: bool) -> None:
    global _CONSOLE
    _DISPLAY.quiet = quiet
    _DISPLAY.color = color
    _DISPLAY.verbose = verbose
    _CONSOLE = None


def _rich_on() -> bool:
    return RICH_AVAILABLE and _DISPLAY.color


def _console(*, stderr: bool = False) -> Any:
    """Return a rich Console, or None when rich is unavailable/disabled."""
    global _CONSOLE
    if not _rich_on():
        return None
    if stderr:
        return Console(stderr=True, no_color=False, highlight=False)
    if _CONSOLE is None:
        _CONSOLE = Console(no_color=False, highlight=False)
    return _CONSOLE


def _cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("\r", " ").replace("\n", " ").strip()


def _ascii_table(headers: Sequence[Any], rows: Sequence[Sequence[Any]]) -> str:
    grid = [[_cell(c) for c in headers]] + [[_cell(c) for c in row] for row in rows]
    widths = [max(len(row[i]) for row in grid) for i in range(len(headers))]
    sep = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    def render(row: Sequence[str]) -> str:
        return "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) + " |"

    lines = [sep, render(grid[0]), sep]
    lines.extend(render(row) for row in grid[1:])
    lines.append(sep)
    return "\n".join(lines)


def display_table(
    headers: Sequence[Any],
    rows: Sequence[Sequence[Any]],
    *,
    title: str | None = None,
    always: bool = False,
) -> None:
    """Render a table with rich when available, otherwise with ASCII borders."""
    if _DISPLAY.quiet and not always:
        return
    if not rows:
        return
    headers = [_cell(h) for h in headers]
    if _rich_on():
        table = Table(
            title=title,
            box=rich_box.SIMPLE_HEAVY if rich_box else None,
            header_style="bold",
            title_justify="left",
        )
        for header in headers:
            table.add_column(header, overflow="fold")
        for row in rows:
            table.add_row(*[_cell(c) for c in row])
        _console().print(table)
        return
    if title:
        print(title)
    print(_ascii_table(headers, rows))


def display_banner(title: str, lines: Iterable[str], *, level: str = "warning") -> None:
    """Render an attention banner. Banners are never suppressed by --quiet."""
    body = "\n".join(str(line) for line in lines if str(line).strip())
    colors = {"warning": "yellow", "error": "red", "info": "cyan", "success": "green"}
    if _rich_on():
        _console().print(
            Panel(
                body,
                title=title,
                title_align="left",
                border_style=colors.get(level, "yellow"),
            )
        )
        return
    label = f"{title}"
    width = max([len(label), *(len(line) for line in body.splitlines())] + [0])
    bar = "+" + "-" * (width + 2) + "+"
    print(bar)
    print(f"| {label.ljust(width)} |")
    print(bar)
    for line in body.splitlines():
        print(f"| {line.ljust(width)} |")
    print(bar)


def display_kv(pairs: Sequence[tuple[str, Any]], *, title: str | None = None, always: bool = False) -> None:
    rows = [[key, value] for key, value in pairs]
    display_table(["Setting", "Value"], rows, title=title, always=always)


def display_command_report(
    command: str,
    *,
    settings: Sequence[tuple[str, Any]],
    flags: Sequence[str],
    implicit: bool = False,
) -> None:
    if _DISPLAY.quiet:
        return
    rows = [[key, value] for key, value in settings]
    rows.append(["Flags", ", ".join(flags) if flags else "none"])
    title = f"manager {command}" + (" (default command)" if implicit else "")
    display_table(["Setting", "Value"], rows, title=title)


def display_info(message: str) -> None:
    if not _DISPLAY.quiet:
        print(message)


def display_ok(message: str) -> None:
    if not _DISPLAY.quiet:
        print(f"[ok] {message}")


def display_warn(message: str) -> None:
    print(f"[warn] {message}", file=sys.stderr)


def display_error(message: str) -> None:
    print(f"[error] {message}", file=sys.stderr)


def display_counts(counts: Counter[str], *, title: str = "summary") -> None:
    if _DISPLAY.quiet or not counts:
        return
    order = ["linked", "relinked", "copied", "updated", "restored", "repaired",
             "unchanged", "skipped", "created",
             "would link", "would relink", "would copy", "would update",
             "would restore", "would repair", "would replace", "would create",
             "failed"]
    rows = [[name, str(counts[name])] for name in order if counts.get(name)]
    rows.extend([[name, str(count)] for name, count in sorted(counts.items()) if name not in order])
    display_table(["Result", "Count"], rows, title=title)


# ---------------------------------------------------------------------------
# paths and small filesystem helpers
# ---------------------------------------------------------------------------


def home_dir() -> Path:
    override = os.environ.get("MANAGER_HOME")
    return Path(override).expanduser() if override else Path.home()


def agent_skill_dir(agent: str) -> Path:
    return home_dir() / AGENT_SKILL_SUBDIRS[agent]


def agent_md_targets(agent: str) -> list[Path]:
    return [home_dir() / rel for rel in AGENT_MD_SUBDIRS[agent]]


def is_reparse(path: Path) -> bool:
    """True for symlinks and junctions on Windows (and symlinks elsewhere)."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    attrs = getattr(st, "st_file_attributes", 0)
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)) or stat.S_ISLNK(st.st_mode)


def is_link_like(path: Path) -> bool:
    return path.is_symlink() or is_reparse(path)


def same_path(a: Path, b: Path) -> bool:
    try:
        return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))
    except OSError:
        return False


def has_skill(path: Path) -> bool:
    try:
        return (path / "SKILL.md").is_file()
    except OSError:
        return False


def remove_entry(path: Path) -> str:
    """Remove a link, junction or real entry. Returns the kind removed."""
    if path.is_symlink():
        path.unlink()
        return "symlink"
    if is_reparse(path):
        os.rmdir(path)
        return "junction"
    if path.is_dir():
        shutil.rmtree(path)
        return "directory"
    path.unlink()
    return "file"


def clear_entries(entries: Iterable[Path]) -> None:
    for entry in entries:
        if entry.exists() or is_link_like(entry):
            remove_entry(entry)


def make_link(source: Path, dest: Path) -> str:
    """Create a directory symlink, falling back to a junction if needed."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(source, dest, target_is_directory=True)
        return "symlink"
    except OSError as exc:
        if _make_junction(source, dest):
            return "junction"
        raise exc


def _make_junction(source: Path, dest: Path) -> bool:
    if os.name != "nt":
        return False
    try:
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dest), str(source)],
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    return result.returncode == 0 and dest.exists()


# ---------------------------------------------------------------------------
# state database (single SQLite file in the OS platform data dir)
# ---------------------------------------------------------------------------


def platform_data_dir() -> Path:
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = str(Path.home() / "Library" / "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / DB_APP_DIR


def db_path() -> Path:
    override = os.environ.get("MANAGER_DB")
    if override:
        return Path(override).expanduser()
    return platform_data_dir() / DB_FILE_NAME


def db_connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS kv ("
            "registry TEXT NOT NULL, store TEXT NOT NULL, data TEXT NOT NULL, "
            "updated_at TEXT NOT NULL, PRIMARY KEY (registry, store))"
        )
    except sqlite3.Error:
        conn.close()
        raise
    return conn


def _registry_key(registry: Path) -> str:
    return os.path.normcase(os.path.abspath(str(registry)))


def kv_get(registry: Path, store: str) -> Any | None:
    """Read one store blob; a legacy JSON file is imported (and then removed)."""
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT data FROM kv WHERE registry = ? AND store = ?",
            (_registry_key(registry), store),
        ).fetchone()
        if row is not None:
            try:
                return json.loads(row[0])
            except json.JSONDecodeError:
                return None
    finally:
        conn.close()
    legacy = registry / LEGACY_STORE_FILES.get(store, "")
    if not LEGACY_STORE_FILES.get(store) or not legacy.is_file():
        return None
    try:
        data = json.loads(legacy.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if isinstance(data, dict):
        kv_set(registry, store, data)
        try:
            legacy.unlink()
        except OSError:
            pass
        return data
    return None


def kv_set(registry: Path, store: str, data: Any) -> None:
    conn = db_connect()
    try:
        conn.execute(
            "INSERT INTO kv (registry, store, data, updated_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(registry, store) DO UPDATE SET data = excluded.data, "
            "updated_at = excluded.updated_at",
            (_registry_key(registry), store, json.dumps(data, indent=2, sort_keys=True),
             datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# install index: where `--into` placed skills (links included, once lost)
# ---------------------------------------------------------------------------


def load_installs(registry: Path) -> dict[str, Any]:
    data = kv_get(registry, "installs")
    if not isinstance(data, dict):
        return {"version": 1, "into": {}}
    if not isinstance(data.get("into"), dict):
        data["into"] = {}
    return data


def record_install(registry: Path, target: Path, source: Path, mode: str, project: Path) -> None:
    data = load_installs(registry)
    data.setdefault("into", {})[_key(target)] = {
        "skill": target.name,
        "target": str(target),
        "source": str(source),
        "mode": mode,
        "project": str(project),
        "installed_at": datetime.now().isoformat(timespec="seconds"),
    }
    kv_set(registry, "installs", data)


def prune_installs(registry: Path) -> list[str]:
    """Drop index rows whose target path no longer exists. Returns removed keys."""
    data = load_installs(registry)
    into = data.setdefault("into", {})
    removed = [key for key, entry in into.items()
               if not Path(entry.get("target", "")).exists()
               and not is_link_like(Path(entry.get("target", "")))]
    for key in removed:
        del into[key]
    if removed:
        kv_set(registry, "installs", data)
    return removed


# ---------------------------------------------------------------------------
# hard-copy manifest (stored in the kv database)
# ---------------------------------------------------------------------------


@dataclass
class CopyRecord:
    skill: str
    source: str
    target: str
    kind: str  # "dir" or "file"
    fingerprint: str
    target_fingerprint: str
    files: int
    copied_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CopyRecord":
        return cls(
            skill=str(data.get("skill", "")),
            source=str(data.get("source", "")),
            target=str(data.get("target", "")),
            kind=str(data.get("kind", "dir")),
            fingerprint=str(data.get("fingerprint", "")),
            target_fingerprint=str(data.get("target_fingerprint", "")),
            files=int(data.get("files", 0) or 0),
            copied_at=str(data.get("copied_at", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill": self.skill,
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
            "fingerprint": self.fingerprint,
            "target_fingerprint": self.target_fingerprint,
            "files": self.files,
            "copied_at": self.copied_at,
        }


def _key(path: Path | str) -> str:
    return os.path.normcase(os.path.abspath(str(path)))


def load_manifest(registry: Path) -> dict[str, Any]:
    data = kv_get(registry, "copies")
    if not isinstance(data, dict):
        return {"version": 1, "copies": {}}
    data.setdefault("version", 1)
    copies = data.setdefault("copies", {})
    if not isinstance(copies, dict):
        data["copies"] = {}
    return data


def save_manifest(registry: Path, data: dict[str, Any]) -> None:
    kv_set(registry, "copies", data)


def load_records(registry: Path) -> dict[str, CopyRecord]:
    data = load_manifest(registry)
    records: dict[str, CopyRecord] = {}
    for key, value in data.get("copies", {}).items():
        if isinstance(value, dict):
            records[str(key)] = CopyRecord.from_dict(value)
    return records


def get_record(registry: Path, target: Path) -> CopyRecord | None:
    return load_records(registry).get(_key(target))


def record_copy(registry: Path, record: CopyRecord) -> None:
    data = load_manifest(registry)
    data.setdefault("copies", {})[_key(record.target)] = record.to_dict()
    save_manifest(registry, data)


def drop_record(registry: Path, target: Path) -> None:
    data = load_manifest(registry)
    copies = data.setdefault("copies", {})
    if _key(target) in copies:
        del copies[_key(target)]
        save_manifest(registry, data)


def is_under(child: Path, parent: Path) -> bool:
    try:
        child_s = os.path.normcase(os.path.abspath(child))
        parent_s = os.path.normcase(os.path.abspath(parent))
        return os.path.commonpath([child_s, parent_s]) == parent_s
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# fingerprints and concurrent reading
# ---------------------------------------------------------------------------


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            name
            for name in dirnames
            if name not in SKIP_NAMES
            and not name.startswith(".")
            and not is_link_like(Path(dirpath) / name)
        ]
        for filename in sorted(filenames):
            path = Path(dirpath) / filename
            if not is_link_like(path):
                yield path


def hash_file(path: Path) -> str | None:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return None
    return digest.hexdigest()


def fingerprint_path(path: Path) -> tuple[str, int] | None:
    """Hash a file or directory tree. Returns (fingerprint, file_count)."""
    if not path.exists():
        return None
    if path.is_file():
        digest = hash_file(path)
        return (digest, 1) if digest else None
    if not path.is_dir():
        return None
    entries: list[str] = []
    for file_path in iter_files(path):
        rel = file_path.relative_to(path).as_posix()
        digest = hash_file(file_path)
        entries.append(f"{rel}:{digest or 'unreadable'}")
    combined = hashlib.sha256("\n".join(sorted(entries)).encode("utf-8")).hexdigest()
    return combined, len(entries)


def map_concurrent(func: Callable[[Any], Any], items: Iterable[Any], jobs: int) -> list[Any]:
    values = list(items)
    if len(values) <= 1 or jobs <= 1:
        return [func(value) for value in values]
    with ThreadPoolExecutor(max_workers=min(jobs, len(values))) as pool:
        return list(pool.map(func, values))


# ---------------------------------------------------------------------------
# synchronization audit
# ---------------------------------------------------------------------------


@dataclass
class SyncIssue:
    kind: str  # "hard-copy" or "link"
    skill: str
    target: str
    state: str
    detail: str


def audit_all(registry: Path, agents: Sequence[str], jobs: int) -> list[SyncIssue]:
    """Check hard copies and links against their recorded/source state."""
    issues: list[SyncIssue] = []
    seen: set[tuple[str, str, str, str]] = set()

    def add(kind: str, skill: str, target: Path | str, state: str, detail: str) -> None:
        key = (kind, skill, str(target), state)
        if key in seen:
            return
        seen.add(key)
        issues.append(SyncIssue(kind, skill, str(target), state, detail))

    records = list(load_records(registry).values())
    paths = sorted({record.source for record in records} | {record.target for record in records})
    prints = dict(zip(paths, map_concurrent(lambda p: fingerprint_path(Path(p)), paths, jobs)))

    for record in records:
        source = Path(record.source)
        target = Path(record.target)
        if not source.exists():
            add("hard-copy", record.skill, target, "missing-source", "the recorded source no longer exists")
            continue
        if is_link_like(target):
            if target.exists():
                add("hard-copy", record.skill, target, "target-replaced",
                    f"a link now points at {os.path.realpath(target)}")
            else:
                add("hard-copy", record.skill, target, "missing-target", "the link at the copy location is broken")
            continue
        if not target.exists():
            add("hard-copy", record.skill, target, "missing-target", "the hard copy is missing")
            continue

        source_print = prints.get(record.source)
        target_print = prints.get(record.target)
        if source_print is None:
            add("hard-copy", record.skill, target, "source-unreadable", "cannot read the source to compare")
            continue
        if target_print is None:
            add("hard-copy", record.skill, target, "target-unreadable", "cannot read the copy to compare")
            continue

        source_changed = source_print[0] != record.fingerprint
        target_changed = target_print[0] != record.target_fingerprint
        if source_changed and target_changed:
            add("hard-copy", record.skill, target, "both-changed",
                "source and copy changed since the last copy; run `skill --refresh --force` after review")
        elif source_changed:
            add("hard-copy", record.skill, target, "source-changed",
                "source changed; run `skill --refresh` to re-copy")
        elif target_changed:
            add("hard-copy", record.skill, target, "target-modified",
                "copy was edited locally; `skill --refresh --force` overwrites it")

    known = registry_skills(registry)
    locked = load_lockfile(registry).get("locked", {})
    record_keys = set(load_records(registry))
    for agent in agents:
        root = agent_skill_dir(agent)
        if not root.is_dir():
            continue
        for direct in sorted(root.iterdir()):
            if not is_link_like(direct):
                continue
            name = direct.name
            source = known.get(name)
            if not direct.exists():
                detail = f"link target is gone (expected {source})" if source else "link target is gone; name is not in the registry"
                add("link", name, direct, "broken-link", detail)
            elif source is not None and not same_path(direct, source):
                add("link", name, direct, "wrong-target",
                    f"points at {os.path.realpath(direct)} instead of {source}")
            elif not has_skill(direct):
                add("link", name, direct, "missing-skill", "link target has no SKILL.md")
        for name, per_agent in locked.items():
            if agent not in per_agent or name not in known:
                continue
            direct = root / name
            if not direct.exists() and not is_link_like(direct) and _key(direct) not in record_keys:
                add("link", name, direct, "missing-locked",
                    f"locked skill is not present in {agent}'s skills folder")

    return issues


def display_sync_banner(issues: Sequence[SyncIssue]) -> None:
    if not issues:
        return
    counts = Counter(issue.state for issue in issues)
    summary = ", ".join(f"{count} {state}" for state, count in sorted(counts.items()))
    lines = [f"{len(issues)} entr{'y' if len(issues) == 1 else 'ies'} need attention: {summary}"]
    limit = len(issues) if _DISPLAY.verbose else 6
    for issue in issues[:limit]:
        lines.append(f"- {issue.skill} [{issue.state}] {issue.target}")
    if len(issues) > limit:
        lines.append(f"- ... and {len(issues) - limit} more; run `python manager.py lint` for the full report")
    display_banner("sync check", lines, level="warning")


# ---------------------------------------------------------------------------
# registry discovery and resolution
# ---------------------------------------------------------------------------


def walk_skills(root: Path, *, prune: bool = True) -> list[Path]:
    """Return directories containing SKILL.md without following links."""
    found: list[Path] = []
    for dirpath, dirnames, _ in os.walk(root):
        current = Path(dirpath)
        rel_parts = current.relative_to(root).parts
        if any(part in SKIP_NAMES or part.startswith(".") for part in rel_parts):
            dirnames[:] = []
            continue
        dirnames[:] = [
            name
            for name in dirnames
            if name not in SKIP_NAMES and not name.startswith(".") and not is_link_like(current / name)
        ]
        if current != root and has_skill(current):
            found.append(current)
            if prune:
                dirnames[:] = []
    return found


def registry_skills(root: Path) -> dict[str, Path]:
    """name -> path, shallowest wins (so top-level beats Groups copies)."""
    best: dict[str, Path] = {}
    for path in walk_skills(root):
        name = path.name
        previous = best.get(name)
        if previous is None or len(path.relative_to(root).parts) < len(previous.relative_to(root).parts):
            best[name] = path
    return best


def resolve_skill(name: str, cwd: Path, registry_root: Path) -> Path:
    candidate = Path(name).expanduser()
    if candidate.is_dir() and has_skill(candidate):
        return candidate.resolve()

    local = cwd / name
    if local.is_dir() and has_skill(local):
        return local.resolve()

    matches = [path for path in walk_skills(cwd, prune=False) if path.name == name]
    if len(matches) == 1:
        return matches[0].resolve()
    if len(matches) > 1:
        listing = "\n  ".join(str(path) for path in matches)
        raise ManagerError(f"'{name}' is ambiguous under {cwd}:\n  {listing}")

    fallback = registry_skills(registry_root).get(name)
    if fallback is not None:
        return fallback.resolve()

    raise ManagerError(f"no skill named '{name}' found in {cwd} or the registry {registry_root}")


def parse_agents(raw: str) -> list[str]:
    if not raw:
        return list(DEFAULT_AGENTS)
    requested = [part.strip().lower() for part in raw.replace(",", " ").split() if part.strip()]
    if not requested or "all" in requested:
        return list(DEFAULT_AGENTS)
    result: list[str] = []
    unknown: list[str] = []
    for item in requested:
        name = ALIASES.get(item, item)
        if name not in AGENT_SKILL_SUBDIRS:
            unknown.append(item)
        elif name not in result:
            result.append(name)
    if unknown:
        raise ManagerError(
            f"unknown agent(s): {', '.join(unknown)}. Available: {', '.join(DEFAULT_AGENTS)}"
        )
    return result


# ---------------------------------------------------------------------------
# lockfile (unchanged schema) and backups
# ---------------------------------------------------------------------------


def load_lockfile(registry_root: Path) -> dict[str, Any]:
    data = kv_get(registry_root, "lock")
    if not isinstance(data, dict):
        return {"version": 1, "locked": {}}
    data.setdefault("version", 1)
    data.setdefault("locked", {})
    return data


def save_lockfile(registry_root: Path, data: dict[str, Any]) -> None:
    kv_set(registry_root, "lock", data)


def record_locks(registry_root: Path, names: Iterable[str], agents: Iterable[str]) -> None:
    data = load_lockfile(registry_root)
    locked = data.setdefault("locked", {})
    now = datetime.now().isoformat(timespec="seconds")
    for name in names:
        entry = locked.setdefault(name, {})
        for agent in agents:
            entry[agent] = now
    save_lockfile(registry_root, data)


def backup_dirs(dirs: Sequence[Path], label: str = "skill-sync-backup") -> Path | None:
    existing = [directory for directory in dirs if directory.exists()]
    if not existing:
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive = home_dir() / f"{label}-{stamp}.zip"
    seen: set[str] = set()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for base in existing:
            for dirpath, dirnames, filenames in os.walk(base, followlinks=True):
                root = Path(dirpath)
                real = os.path.normcase(os.path.realpath(root))
                if real in seen:
                    dirnames[:] = []
                    continue
                seen.add(real)
                for filename in filenames:
                    source = root / filename
                    try:
                        arcname = base.name / source.relative_to(base)
                        bundle.write(source, arcname=str(arcname))
                    except (OSError, ValueError):
                        continue
    return archive


# ---------------------------------------------------------------------------
# deployment primitives
# ---------------------------------------------------------------------------


def install_copy(source: Path, target: Path) -> None:
    """Copy a file or tree into place through a staging path."""
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(target.name + f".tmp-{os.getpid()}")
    if staging.exists() or is_link_like(staging):
        remove_entry(staging)
    if source.is_dir():
        shutil.copytree(
            source,
            staging,
            ignore=shutil.ignore_patterns(*SKIP_NAMES),
            symlinks=False,
        )
    else:
        shutil.copy2(source, staging)
    if target.exists() or is_link_like(target):
        remove_entry(target)
    os.replace(staging, target)


def remember_copy(registry: Path, skill: str, source: Path, target: Path) -> bool:
    source_print = fingerprint_path(source)
    target_print = fingerprint_path(target)
    if source_print is None or target_print is None:
        return False
    record_copy(
        registry,
        CopyRecord(
            skill=skill,
            source=str(source.resolve()),
            target=str(target.resolve()),
            kind="dir" if target.is_dir() else "file",
            fingerprint=source_print[0],
            target_fingerprint=target_print[0],
            files=source_print[1],
            copied_at=datetime.now().isoformat(timespec="seconds"),
        ),
    )
    return True


def _would(status: str) -> str:
    mapping = {
        "linked": "would link",
        "relinked": "would relink",
        "copied": "would copy",
        "updated": "would update",
        "restored": "would restore",
        "repaired": "would repair",
        "replaced": "would replace",
        "created": "would create",
    }
    return mapping.get(status, f"would {status}")


def deploy_skill(
    source: Path,
    dest: Path,
    *,
    mode: str,
    force: bool,
    agent: str | None,
    registry: Path,
    dry_run: bool,
) -> tuple[str, str]:
    """Link or hard-copy one skill. Returns (status, detail)."""
    src = source.resolve()

    if mode == "symlink":
        if is_link_like(dest) and same_path(dest, src):
            if dest.exists():
                if agent is None and not dry_run:
                    record_install(registry, dest, src, mode, dest.parent)
                return "unchanged", f"-> {src}"
            if not dry_run:
                remove_entry(dest)
                make_link(src, dest)
                if agent is None:
                    record_install(registry, dest, src, mode, dest.parent)
            return "repaired", f"broken link -> {src}"

        if is_link_like(dest):
            old = os.path.realpath(dest)
            if not dry_run:
                remove_entry(dest)
            status, detail = "relinked", f"{old} -> {src}"
        elif dest.exists() and dest.is_dir():
            if agent not in MIGRATION_AGENTS and not force:
                return "skipped", "real directory (use --force to replace)"
            if not dry_run:
                remove_entry(dest)
            status, detail = "replaced", f"real directory -> {src}"
        elif dest.exists():
            if not force:
                return "skipped", "real file (use --force to replace)"
            if not dry_run:
                remove_entry(dest)
            status, detail = "replaced", f"real file -> {src}"
        else:
            status, detail = "linked", f"-> {src}"

        if dry_run:
            return _would(status), detail
        try:
            make_link(src, dest)
        except OSError as exc:
            return "failed", str(exc)
        drop_record(registry, dest)
        if agent is None:
            record_install(registry, dest, src, mode, dest.parent)
        return status, detail

    # hard copy
    record = get_record(registry, dest)
    if is_link_like(dest):
        if not dry_run:
            remove_entry(dest)
        status, detail = "replaced", "link -> hard copy"
    elif dest.exists():
        if record is None:
            if not force:
                return "skipped", "real path is not a managed copy (use --force)"
            if not dry_run:
                remove_entry(dest)
            status, detail = "replaced", "unmanaged path -> hard copy"
        else:
            source_print = fingerprint_path(src)
            target_print = fingerprint_path(dest)
            if source_print is None:
                return "failed", "source unreadable"
            if target_print is None:
                return "failed", "copy unreadable"
            source_changed = source_print[0] != record.fingerprint
            target_changed = target_print[0] != record.target_fingerprint
            if not source_changed and not target_changed:
                return "unchanged", f"-> {dest}"
            if target_changed and not force:
                return "skipped", "copy was modified (use --force to overwrite)"
            if not dry_run:
                remove_entry(dest)
            status = "updated" if source_changed else "repaired"
            detail = "source changed" if source_changed else "copy repaired"
    else:
        status, detail = "copied", f"-> {dest}"

    if dry_run:
        return _would(status), detail
    try:
        install_copy(src, dest)
    except OSError as exc:
        return "failed", str(exc)
    if not remember_copy(registry, dest.name, src, dest):
        return "failed", "copied but could not fingerprint the result"
    if agent is None:
        record_install(registry, dest, src, mode, dest.parent)
    return status, detail


def deploy_agent_file(
    source: Path,
    target: Path,
    *,
    hard: bool,
    force: bool,
    registry: Path,
    dry_run: bool,
) -> tuple[str, str]:
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)

    backup_note = ""
    if target.exists() or is_link_like(target):
        if is_link_like(target):
            if not dry_run:
                remove_entry(target)
            status, detail = "relinked", "replaced existing link"
        elif target.is_file():
            if not force:
                backup = target.with_suffix(".bak")
                if not backup.exists() and not dry_run:
                    shutil.copy2(target, backup)
                    backup_note = f"backup {backup}"
            if not dry_run:
                remove_entry(target)
            status, detail = "replaced", backup_note or "replaced existing file"
        else:
            return "failed", "path exists and is a directory"
    else:
        status, detail = ("copied" if hard else "linked"), f"-> {source}"

    if dry_run:
        return _would(status), detail
    try:
        if hard:
            install_copy(source, target)
        else:
            try:
                os.symlink(source, target)
            except OSError as exc:
                shutil.copy2(source, target)
                detail = f"copied (symlink failed: {exc})"
                hard = True
    except OSError as exc:
        return "failed", str(exc)

    if hard:
        if not remember_copy(registry, target.name, source, target):
            return "failed", "copied but could not fingerprint the result"
    else:
        drop_record(registry, target)
    return status, detail


# ---------------------------------------------------------------------------
# skill command
# ---------------------------------------------------------------------------


def resolve_into(raw: str) -> Path:
    path = Path(raw).expanduser()
    if path.exists() and not path.is_dir():
        raise ManagerError(f"--into path is not a directory: {path}")
    return path.resolve()


def scan_existing(base: Path, known: set[str]) -> dict[str, list[Path]]:
    """Find existing skill entries under base whose names are in known."""
    matches: dict[str, list[Path]] = {}

    def visit(directory: Path) -> None:
        try:
            entries = sorted(directory.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            return
        for entry in entries:
            try:
                if is_reparse(entry):
                    if entry.name in known:
                        matches.setdefault(entry.name, []).append(entry)
                    continue
                if not entry.is_dir():
                    continue
                if has_skill(entry):
                    if entry.name in known:
                        matches.setdefault(entry.name, []).append(entry)
                    continue
                visit(entry)
            except OSError:
                continue

    visit(base)
    return matches


def cmd_skill(args: argparse.Namespace, registry: Path, jobs: int, invoked: set[str]) -> int:
    if args.list:
        skills = registry_skills(registry)
        rows = [[name, str(path.relative_to(registry))] for name, path in sorted(skills.items())]
        display_table(["Skill", "Path"], rows, title=f"{len(skills)} registry skills", always=True)
        return 0

    into = resolve_into(args.into) if args.into else None
    if into is not None and ({"-A", "--agents"} & invoked):
        raise ManagerError("--into targets one folder; drop --agents")

    if args.refresh:
        if args.skills or args.all:
            raise ManagerError("--refresh cannot be combined with skill names or --all")
        return cmd_refresh(args, registry, jobs, into)

    if args.all:
        names = sorted(registry_skills(registry))
    else:
        names = list(args.skills)
    if not names:
        raise ManagerError("name at least one skill, or use --all / --refresh")

    hard = bool(args.hard_copy or args.mode == "copy")
    if args.hard_copy and args.mode == "symlink" and ({"-M", "--mode"} & invoked):
        raise ManagerError("--hard-copy and --mode symlink contradict each other")
    mode = "hard-copy" if hard else "symlink"

    sources: list[Path] = []
    for name in names:
        try:
            sources.append(resolve_skill(name, Path.cwd(), registry))
        except ManagerError as exc:
            display_error(str(exc))
    if not sources:
        return 1

    if into is not None:
        roots: list[tuple[str, Path, str | None]] = [(f"into {into}", into, None)]
        if args.lock:
            display_warn("--lock records agent installs only; ignored with --into")
    else:
        agents = parse_agents(args.agents)
        roots = [(agent, agent_skill_dir(agent), agent) for agent in agents]

    rows: list[list[str]] = []
    counts: Counter[str] = Counter()
    failures = 0
    successful: list[str] = []

    for label, root, agent in roots:
        existed = root.exists()
        if not existed:
            if not args.dry_run:
                try:
                    root.mkdir(parents=True, exist_ok=True)
                except OSError as exc:
                    display_error(f"cannot create {root}: {exc}")
                    failures += 1
                    continue
            rows.append([label, "-", mode, "would create" if args.dry_run else "created", str(root)])
        for source in sources:
            status, detail = deploy_skill(
                source,
                root / source.name,
                mode=mode,
                force=args.force,
                agent=agent,
                registry=registry,
                dry_run=args.dry_run,
            )
            rows.append([label, source.name, mode, status, detail])
            counts[status] += 1
            if status == "failed":
                failures += 1
            elif status != "skipped" and not args.dry_run and agent is not None:
                if source.name not in successful:
                    successful.append(source.name)

    display_table(["Target", "Skill", "Mode", "Status", "Detail"], rows, title="skill deployment")
    display_counts(counts)

    if args.lock and successful and not args.dry_run:
        record_locks(registry, successful, parse_agents(args.agents))
        display_info(f"[lock] recorded {len(successful)} skill(s) into the manager database")
    return 1 if failures else 0


VIBER_MANIFEST = Path("Groups") / "Viber" / "viber.json"


def viber_plan(registry: Path) -> list[dict[str, Any]]:
    """Resolve the viber manifest into rows: phase, name, status, entry label, path (None = not in registry)."""
    manifest_file = registry / VIBER_MANIFEST
    if not manifest_file.is_file():
        raise ManagerError(f"viber manifest not found: {manifest_file}")
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManagerError(f"cannot read {manifest_file}: {exc}") from exc
    known = registry_skills(registry)
    rows: list[dict[str, Any]] = []
    for phase in manifest.get("phases", []):
        for entry in phase.get("skills", []):
            label = entry.get("as") or entry["name"]
            base = {"phase": phase.get("phase", "-"), "status": entry.get("status", "-"), "entry": label}
            if "path" in entry:
                group = registry / entry["path"]
                members = sorted(walk_skills(group), key=lambda p: p.name) if group.is_dir() else []
                if not members:
                    rows.append({**base, "name": entry["name"], "path": None})
                for member in members:
                    rows.append({**base, "name": member.name, "path": member})
            else:
                rows.append({**base, "name": entry["name"], "path": known.get(entry["name"])})
    return rows


def cmd_viber(args: argparse.Namespace, registry: Path, jobs: int, invoked: set[str]) -> int:
    rows = viber_plan(registry)
    if args.list:
        display_table(
            ["Phase", "Entry", "Skill", "Status", "Path"],
            [[row["phase"], row["entry"], row["name"], row["status"],
              str(row["path"].relative_to(registry)) if row["path"] else "not in registry"] for row in rows],
            title=f"viber skills ({len({row['path'] for row in rows if row['path']})} installable)",
            always=True,
        )
        return 0
    missing = sorted({row["entry"] for row in rows if row["path"] is None})
    if missing:
        display_warn(f"viber names skills that are not in the registry yet, skipped: {', '.join(missing)}")
    sources: list[Path] = []
    for row in rows:
        if row["path"] is not None and row["path"] not in sources:
            sources.append(row["path"])
    if not sources:
        raise ManagerError("no viber skill resolves to the registry")
    args.skills = [str(path) for path in sources]
    return cmd_skill(args, registry, jobs, invoked)


def sync_copy(record: CopyRecord, registry: Path, *, force: bool, dry_run: bool) -> tuple[str, str]:
    source = Path(record.source)
    target = Path(record.target)
    if not source.exists():
        return "failed", "source no longer exists"
    source_print = fingerprint_path(source)
    if source_print is None:
        return "failed", "source unreadable"

    if is_link_like(target) or not target.exists():
        if not dry_run:
            if target.exists() or is_link_like(target):
                remove_entry(target)
            install_copy(source, target)
            remember_copy(registry, record.skill, source, target)
        return ("would restore" if dry_run else "restored"), f"-> {target}"

    target_print = fingerprint_path(target)
    if target_print is None:
        return "failed", "copy unreadable"
    source_changed = source_print[0] != record.fingerprint
    target_changed = target_print[0] != record.target_fingerprint
    if not source_changed and not target_changed:
        return "unchanged", "in sync"
    if target_changed and not force:
        return "skipped", "copy was modified (use --force to overwrite)"
    if dry_run:
        return "would update", "source changed"
    install_copy(source, target)
    remember_copy(registry, record.skill, source, target)
    return "updated", "source -> copy"


def cmd_refresh(args: argparse.Namespace, registry: Path, jobs: int, into: Path | None) -> int:
    known = registry_skills(registry)
    if not known:
        raise ManagerError(f"no skills found in registry {registry}")

    if into is not None:
        roots: list[tuple[str, Path, str | None]] = [(f"into {into}", into, None)]
    else:
        roots = [(agent, agent_skill_dir(agent), agent) for agent in parse_agents(args.agents)]

    if not args.no_backup and not args.dry_run:
        existing = [root for _, root, _ in roots if root.exists()]
        archive = backup_dirs(existing)
        if archive:
            display_info(f"backup: {archive}")

    records = load_records(registry)
    locked = load_lockfile(registry).get("locked", {})
    rows: list[list[str]] = []
    counts: Counter[str] = Counter()
    failures = 0

    for label, root, agent in roots:
        if not root.exists():
            rows.append([label, "-", "skipped", "skills folder is missing"])
            counts["skipped"] += 1
            continue

        for record in records.values():
            if record.kind == "dir" and is_under(Path(record.target), root):
                status, detail = sync_copy(
                    record, registry, force=args.force, dry_run=args.dry_run
                )
                rows.append([label, record.skill, status, detail])
                counts[status] += 1
                if status == "failed":
                    failures += 1

        if agent is not None:
            for name, per_agent in locked.items():
                if agent not in per_agent or name not in known:
                    continue
                direct = root / name
                if direct.exists() or is_link_like(direct) or _key(direct) in records:
                    continue
                if not args.dry_run:
                    try:
                        make_link(known[name], direct)
                    except OSError as exc:
                        rows.append([label, name, "failed", str(exc)])
                        counts["failed"] += 1
                        failures += 1
                        continue
                rows.append([label, name, "would restore" if args.dry_run else "restored",
                             f"locked -> {known[name]}"])
                counts["restored"] += 1

        for name, places in scan_existing(root, set(known)).items():
            direct = root / name
            if _key(direct) in records:
                continue
            source = known[name]
            if is_link_like(direct):
                if same_path(direct, source) and direct.exists():
                    rows.append([label, name, "unchanged", f"-> {source}"])
                    counts["unchanged"] += 1
                    continue
                if not args.dry_run:
                    clear_entries(places)
                    clear_entries([direct])
                    make_link(source, direct)
                rows.append([label, name, "would relink" if args.dry_run else "relinked", f"-> {source}"])
                counts["relinked"] += 1
                continue
            if direct.is_dir():
                if agent in MIGRATION_AGENTS or args.force:
                    if not args.dry_run:
                        clear_entries(places)
                        clear_entries([direct])
                        make_link(source, direct)
                    rows.append([label, name, "would replace" if args.dry_run else "replaced",
                                 f"real directory -> {source}"])
                    counts["replaced"] += 1
                else:
                    rows.append([label, name, "skipped", "real directory (use --force)"])
                    counts["skipped"] += 1
                continue
            if not args.dry_run:
                clear_entries(places)
                clear_entries([direct])
                make_link(source, direct)
            rows.append([label, name, "would relink" if args.dry_run else "relinked", f"-> {source}"])
            counts["relinked"] += 1

    display_table(["Target", "Skill", "Status", "Detail"], rows, title="refresh")
    display_counts(counts)
    return 1 if failures else 0


# ---------------------------------------------------------------------------
# agent command
# ---------------------------------------------------------------------------


def cmd_agent(args: argparse.Namespace, registry: Path) -> int:
    source = registry / "AGENTS.md"
    if not source.is_file():
        raise ManagerError(f"source AGENTS.md not found at {source}")

    hard = bool(args.hard_copy or args.mode == "copy")
    agents = parse_agents(args.agents)
    rows: list[list[str]] = []
    counts: Counter[str] = Counter()
    failures = 0

    for agent in agents:
        for target in agent_md_targets(agent):
            status, detail = deploy_agent_file(
                source,
                target,
                hard=hard,
                force=args.force,
                registry=registry,
                dry_run=args.dry_run,
            )
            rows.append([agent, str(target), status, detail])
            counts[status] += 1
            if status == "failed":
                failures += 1

    display_table(["Agent", "Target", "Status", "Detail"], rows, title="agent instructions")
    display_counts(counts)
    return 1 if failures else 0


# ---------------------------------------------------------------------------
# lint command
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^\ufeff?---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", re.S)


def parse_minimal_frontmatter(raw: str) -> dict[str, str]:
    """Tiny YAML subset fallback: scalar keys, quotes and block scalars."""
    data: dict[str, str] = {}
    lines = raw.splitlines()
    index = 0
    while index < len(lines):
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[index])
        if not match:
            index += 1
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in {"|", ">", "|-", ">-", "|+", ">+"}:
            block: list[str] = []
            index += 1
            while index < len(lines):
                line = lines[index]
                if line.strip() and not line.startswith((" ", "\t")):
                    break
                block.append(line.strip())
                index += 1
            joiner = " " if value.startswith(">") else "\n"
            data[key] = joiner.join(block).strip()
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            inner = value[1:-1]
            data[key] = inner.replace("''", "'") if value[0] == "'" else inner
        else:
            data[key] = value
        index += 1
    return data


def read_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return None, f"unreadable ({exc.__class__.__name__})"
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, "no frontmatter"
    raw = match.group(1)
    if yaml is not None:
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            mark = getattr(exc, "problem_mark", None)
            location = f" at line {mark.line + 2}" if mark is not None else ""
            return None, f"invalid YAML{location}"
        if isinstance(data, dict):
            return data, None
        return None, "frontmatter must be a mapping"
    parsed = parse_minimal_frontmatter(raw)
    return (parsed, None) if parsed else (None, "frontmatter is empty or unparsable")


def lint_skill_dirs(
    registry: Path,
    extra_roots: Sequence[Path],
    records: Iterable[CopyRecord],
) -> list[tuple[str, Path, str]]:
    seen: dict[str, tuple[str, Path, str]] = {}

    def add(name: str, path: Path, label: str) -> None:
        if not has_skill(path):
            return
        key = os.path.normcase(os.path.realpath(path))
        seen.setdefault(key, (name, path, label))

    for record in records:
        if record.kind == "dir":
            add(record.skill, Path(record.target), "hard-copy")
    for path in walk_skills(registry, prune=False):
        add(path.name, path, "registry")
    roots = [(agent_skill_dir(agent), f"agent:{agent}") for agent in DEFAULT_AGENTS]
    roots.extend((root, f"into:{root}") for root in extra_roots)
    for root, label in roots:
        if not root.is_dir():
            continue
        add(root.name, root, label)
        for path in walk_skills(root, prune=False):
            add(path.name, path, label)
        for path in sorted(root.iterdir()):
            if is_link_like(path) and has_skill(path):
                add(path.name, path, label)
                for nested in walk_skills(path, prune=False):
                    add(nested.name, nested, label)
    return list(seen.values())


README_NAME = "README.md"
STANDALONE_CATEGORY = "Standalone (repository root)"
_README_QI_RE = re.compile(r"^- \[([^\]]+)\]\(([^)]+)\)(?: — (.*))?$")
_README_FIELD_RE = re.compile(r"^- \*\*([^*]+):\*\* (.*)$")
_README_PATH_RE = re.compile(r"\]\(([^)]+)\)")
_README_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def _squash(value: Any) -> str:
    return " ".join(str(value).split()) if isinstance(value, str) else ""


def _readme_path(target: str) -> str:
    """A README link target as a registry-relative posix path: decoded, no './', no anchor or title."""
    target = target.strip()
    if ' "' in target:
        target = target.split(' "', 1)[0]
    path = unquote(target.split("#", 1)[0]).replace("\\", "/").strip()
    while path.startswith("./"):
        path = path[2:]
    return path.lstrip("/")


def _path_key(path: str) -> str:
    return _readme_path(path).casefold()


def expected_catalog(registry: Path) -> dict[str, dict[str, Any]]:
    """rel SKILL.md path -> what the README must say about that skill."""
    dirs = walk_skills(registry, prune=False)
    catalog: dict[str, dict[str, Any]] = {}
    for path in dirs:
        rel = path.relative_to(registry)
        data, _ = read_frontmatter(path / "SKILL.md")
        data = data or {}
        ancestors = [other for other in dirs if other != path and is_under(path, other)]
        parent = max(ancestors, key=lambda p: len(p.parts)) if ancestors else None
        catalog[(rel / "SKILL.md").as_posix()] = {
            "dir": path,
            "name": data.get("name") if isinstance(data.get("name"), str) else path.name,
            "description": _squash(data.get("description")),
            "use_case": _squash(data.get("when_to_use")),
            "hint": _squash(data.get("argument-hint")),
            "category": rel.parts[1] if rel.parts[0] == "Groups" and len(rel.parts) > 2 else STANDALONE_CATEGORY,
            "parent": parent,
        }
    by_dir = {info["dir"]: info for info in catalog.values()}
    for info in catalog.values():
        info["parent_name"] = by_dir[info["parent"]]["name"] if info["parent"] in by_dir else None
        info["children"] = sorted(
            other["name"] for other in catalog.values() if other["parent"] == info["dir"]
        )
    return catalog


def parse_readme(text: str) -> dict[str, Any]:
    header, _, rest = text.partition("## Quick Index")
    quick, _, rest = rest.partition("## Skill Details")
    details_text, _, archive_text = rest.partition("## Archive")
    parsed: dict[str, Any] = {"header": header, "quick": [], "details": [], "archive": []}

    category = None
    for line in quick.splitlines():
        if line.startswith("### "):
            category = line[4:].strip()
        elif match := _README_QI_RE.match(line):
            parsed["quick"].append({"name": match[1], "path": _readme_path(match[2]), "summary": match[3] or "", "category": category})

    category, block = None, None
    for line in details_text.splitlines():
        if line.startswith("#### "):
            block = {"name": line[5:].strip().strip("`"), "category": category, "fields": {}}
            parsed["details"].append(block)
        elif line.startswith("### "):
            category, block = line[4:].strip(), None
        elif block is not None and (match := _README_FIELD_RE.match(line)):
            block["fields"][match[1].strip()] = match[2].strip()

    for line in archive_text.splitlines():
        if match := _README_QI_RE.match(line):
            parsed["archive"].append({"name": match[1], "path": _readme_path(match[2])})
    return parsed


def check_readme(registry: Path) -> list[tuple[str, str, str]]:
    """Return (skill, section, issue) rows where README.md disagrees with the skills on disk."""
    readme = registry / README_NAME
    if not readme.is_file():
        return [("-", "readme", f"{README_NAME} not found in {registry}")]
    text = readme.read_text(encoding="utf-8", errors="replace")
    parsed = parse_readme(text)
    catalog = expected_catalog(registry)
    issues: list[tuple[str, str, str]] = []

    archive_root = registry / "Archive"
    archived = sorted(
        (path / "SKILL.md").relative_to(registry).as_posix()
        for path in walk_skills(archive_root, prune=False)
    ) if archive_root.is_dir() else []
    standalone = sum(1 for info in catalog.values() if info["category"] == STANDALONE_CATEGORY)
    groups = len({info["category"] for info in catalog.values()} - {STANDALONE_CATEGORY})
    claims = [
        (r"Total active skills: \*\*(\d+)\*\*", len(catalog), "active skills"),
        (r"(\d+) standalone", standalone, "standalone skills"),
        (r"(\d+) topic groups", groups, "topic groups"),
        (r"(\d+) archived", len(archived), "archived skills"),
    ]
    for pattern, actual, label in claims:
        match = re.search(pattern, parsed["header"])
        if match is None:
            issues.append(("-", "header", f"no count of {label} (on disk: {actual})"))
        elif int(match[1]) != actual:
            issues.append(("-", "header", f"claims {match[1]} {label}, on disk: {actual}"))

    quick_by_path: dict[str, dict[str, Any]] = {}
    for entry in parsed["quick"]:
        if _path_key(entry["path"]) in quick_by_path:
            issues.append((entry["name"], "quick-index", f"listed twice ({entry['path']})"))
        quick_by_path[_path_key(entry["path"])] = entry
    details_by_path: dict[str, dict[str, Any]] = {}
    for block in parsed["details"]:
        match = _README_PATH_RE.search(block["fields"].get("Path", ""))
        if match is None:
            issues.append((block["name"], "details", "detail block has no Path link"))
            continue
        block["path"] = _readme_path(match[1])
        if _path_key(block["path"]) in details_by_path:
            issues.append((block["name"], "details", f"listed twice ({block['path']})"))
        details_by_path[_path_key(block["path"])] = block

    def check_case(name: str, section: str, listed: str, actual: str) -> None:
        if listed != actual:
            issues.append((name, section, f"path case differs: README has {listed}, disk has {actual}"))

    for rel, info in sorted(catalog.items()):
        name = info["name"]
        entry = quick_by_path.get(_path_key(rel))
        if info["parent"] is None:
            if entry is None:
                issues.append((name, "quick-index", f"missing ({rel})"))
            else:
                check_case(name, "quick-index", entry["path"], rel)
                if entry["category"] != info["category"]:
                    issues.append((name, "quick-index", f"under '{entry['category']}', expected '{info['category']}'"))
                if entry["name"] != name:
                    issues.append((name, "quick-index", f"listed as '{entry['name']}'"))
                summary = _squash(entry["summary"]).rstrip("…").rstrip()
                if summary and not info["description"].startswith(summary):
                    issues.append((name, "quick-index", "summary does not match the current description"))
        elif entry is not None:
            issues.append((name, "quick-index", f"nested under '{info['parent_name']}'; only top-level skills belong here"))

        block = details_by_path.get(_path_key(rel))
        if block is None:
            issues.append((name, "details", f"missing ({rel})"))
            continue
        check_case(name, "details", block["path"], rel)
        fields = block["fields"]
        if block["name"] != name:
            issues.append((name, "details", f"headed '{block['name']}'"))
        if block["category"] != info["category"]:
            issues.append((name, "details", f"under '{block['category']}', expected '{info['category']}'"))
        if _squash(fields.get("Description")) != info["description"]:
            issues.append((name, "details", "description differs from SKILL.md"))
        if _squash(fields.get("Use-case")) != info["use_case"]:
            issues.append((name, "details", "use-case differs from when_to_use"))
        usage = _squash(fields.get("Usage")).strip("`")
        expected_usage = f"/{name} {info['hint']}" if info["hint"] else ""
        if usage != expected_usage:
            issues.append((name, "details", "usage differs from argument-hint"))
        if (fields.get("Parent") or "").strip("`") != (info["parent_name"] or ""):
            issues.append((name, "details", f"parent should be '{info['parent_name'] or 'none'}'"))
        listed_children = sorted(part.strip().strip("`") for part in fields.get("Sub-skills", "").split(",") if part.strip())
        if listed_children != info["children"]:
            issues.append((name, "details", f"sub-skills should be {', '.join(info['children']) or 'none'}"))

    active_keys = {_path_key(rel) for rel in catalog}
    for key, entry in quick_by_path.items():
        if key not in active_keys:
            issues.append((entry["name"], "quick-index", f"stale entry: no active skill at {entry['path']}"))
    for key, block in details_by_path.items():
        if key not in active_keys:
            issues.append((block["name"], "details", f"stale entry: no active skill at {block['path']}"))

    listed_archive = {_path_key(entry["path"]): entry for entry in parsed["archive"]}
    archived_keys = {_path_key(rel): rel for rel in archived}
    for key, rel in archived_keys.items():
        entry = listed_archive.get(key)
        if entry is None:
            issues.append((Path(rel).parent.name, "archive", f"missing ({rel})"))
        else:
            check_case(entry["name"], "archive", entry["path"], rel)
    for key, entry in listed_archive.items():
        if key not in archived_keys:
            issues.append((entry["name"], "archive", f"stale entry: no archived skill at {entry['path']}"))

    reported = set(quick_by_path) | set(details_by_path) | set(listed_archive)
    for match in _README_LINK_RE.finditer(text):
        target = match[1].strip()
        if not target or target.startswith("#") or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
            continue
        rel = _readme_path(target)
        if _path_key(rel) not in reported and not (registry / rel).exists():
            issues.append(("-", "links", f"broken link: {target}"))
    return issues


def cmd_lint(args: argparse.Namespace, registry: Path, jobs: int, issues: Sequence[SyncIssue]) -> int:
    limit = args.max_description
    if limit <= 0:
        raise ManagerError("--max-description must be a positive number")
    extra_roots = [resolve_into(value) for value in (args.into or [])]
    records = list(load_records(registry).values())
    skills = lint_skill_dirs(registry, extra_roots, records)
    if not skills:
        display_warn(f"no SKILL.md files found in {registry} or the configured skill folders")

    frontmatters = map_concurrent(
        lambda item: read_frontmatter(item[1] / "SKILL.md"), skills, jobs
    )
    warnings: list[tuple[str, str, Path, int | None, str]] = []
    checked_rows: list[list[str]] = []
    registry_names: dict[str, Path] = {}
    total_checked = 0
    if yaml is None:
        warnings.append(("-", "environment", registry, None, "YAML validation unavailable; install PyYAML for full validation"))
    for (name, path, label), (data, error) in zip(skills, frontmatters):
        total_checked += 1
        if data is None:
            warnings.append((name, label, path, None, error or "missing frontmatter"))
            checked_rows.append([name, label, "missing", "missing", str(path)])
            continue
        skill_name = data.get("name")
        if not isinstance(skill_name, str) or not re.fullmatch(r"[a-z0-9-]+", skill_name):
            warnings.append((name, label, path, None, "missing or invalid name (use lowercase letters, digits and hyphens)"))
        else:
            if skill_name != path.name:
                warnings.append((name, label, path, None, f"name '{skill_name}' does not match folder '{path.name}'"))
            if label == "registry":
                previous = registry_names.setdefault(skill_name, path)
                if previous != path:
                    warnings.append((name, label, path, None, f"duplicate name '{skill_name}' also at {previous}"))
        description = data.get("description")
        if not isinstance(description, str) or not description.strip():
            warnings.append((name, label, path, None, "missing description"))
            checked_rows.append([name, label, "missing", "missing", str(path)])
            continue
        if "\n" in description.strip() or "\r" in description.strip():
            warnings.append((name, label, path, None, "description must be a single-line string"))
        length = len(description)
        state = "over" if length > limit else "ok"
        checked_rows.append([name, label, str(length), state, str(path)])
        if length > limit:
            warnings.append((name, label, path, length, "over limit"))

    version_warnings: list[tuple[str, str, str, str, str]] = []
    version_stats: Counter = Counter()
    if not args.no_version:
        version_warnings, version_stats = check_versions(registry, jobs)

    if version_warnings:
        display_table(
            ["Skill", "Version", "Suggested bump", "Reason", "Path"],
            [[n, ver, sugg, reason, str(registry / rel / "SKILL.md")]
             for n, ver, sugg, reason, rel in version_warnings],
            title=f"version warnings ({len(version_warnings)})",
            always=True,
        )
    if _DISPLAY.verbose and version_stats:
        display_kv(
            [(k, str(v)) for k, v in sorted(version_stats.items())],
            title="version tracking", always=True,
        )

    if warnings:
        rows = []
        for name, label, path, length, reason in warnings:
            rows.append([name, label, str(length) if length is not None else "-", reason, str(path / "SKILL.md")])
        display_table(
            ["Skill", "Location", "Chars", "Issue", "Path"],
            rows,
            title=f"skill warnings ({len(warnings)})",
            always=True,
        )
    if _DISPLAY.verbose and checked_rows:
        display_table(
            ["Skill", "Location", "Chars", "State", "Path"],
            checked_rows,
            title="all checked skills",
            always=True,
        )
    if issues:
        display_table(
            ["Skill", "State", "Target", "Detail"],
            [[issue.skill, issue.state, issue.target, issue.detail] for issue in issues],
            title=f"synchronization issues ({len(issues)})",
            always=True,
        )
    readme_issues = check_readme(registry) if args.readme else []
    if readme_issues:
        display_table(
            ["Skill", "Section", "Issue"],
            [list(row) for row in readme_issues],
            title=f"README issues ({len(readme_issues)})",
            always=True,
        )

    hard_copies = sum(1 for record in records if record.kind == "dir")
    summary = [
        ("Registry", str(registry)),
        ("Roots scanned", str(1 + len(extra_roots) + sum(
            1 for agent in DEFAULT_AGENTS if agent_skill_dir(agent).is_dir()
        ))),
        ("SKILL.md files checked", str(total_checked)),
        ("Hard copies tracked", str(hard_copies)),
        ("Skill warnings", str(len(warnings))),
        ("Synchronization issues", str(len(issues))),
    ]
    if args.readme:
        summary.append(("README issues", str(len(readme_issues))))
    if not args.no_version:
        summary.append(("Version warnings", str(len(version_warnings))))
    summary.append(("Description limit", f"{limit} characters"))
    display_kv(summary, title="lint summary", always=True)
    if not warnings and not issues and not readme_issues and not version_warnings:
        tail = " and README.md matches the registry" if args.readme else ""
        display_ok(
            f"all {total_checked} SKILL.md files passed metadata checks and no synchronization issues were found{tail}"
        )

    return 1 if (args.strict and (warnings or issues or readme_issues or version_warnings)) else 0


# ---------------------------------------------------------------------------
# Skill versions: git-aware change tracking and bump suggestions
# ---------------------------------------------------------------------------


def load_versions(registry: Path) -> dict[str, Any]:
    data = kv_get(registry, "versions")
    if not isinstance(data, dict):
        return {"version": 1, "skills": {}}
    data.setdefault("version", 1)
    if not isinstance(data.get("skills"), dict):
        data["skills"] = {}
    return data


def save_versions(registry: Path, data: dict[str, Any]) -> None:
    kv_set(registry, "versions", data)


def _git(cwd: Path, *args: str, strip: bool = True) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() if strip else proc.stdout


def git_root(registry: Path) -> Path | None:
    out = _git(registry, "rev-parse", "--show-toplevel")
    return Path(out) if out else None


def git_head(registry: Path) -> str | None:
    return _git(registry, "rev-parse", "HEAD")


def git_status_map(registry: Path) -> dict[str, str]:
    """Working-tree changes keyed by path relative to the registry."""
    root = git_root(registry)
    if root is None:
        return {}
    out = _git(root, "status", "--porcelain", strip=False)
    if not out:
        return {}
    try:
        reg_rel = registry.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        reg_rel = "."
    prefix = "" if reg_rel == "." else reg_rel.rstrip("/") + "/"
    changes: dict[str, str] = {}
    for line in out.splitlines():
        if len(line) < 4:
            continue
        code, path = line[:2], line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        path = path.strip().strip('"')
        if prefix:
            if not path.startswith(prefix):
                continue
            path = path[len(prefix):]
        changes[path] = code
    return changes


def git_last_commit(registry: Path, rel: str) -> str | None:
    out = _git(registry, "log", "-1", "--format=%h %cs", "--", rel)
    return out or None


def skill_git_state(rel: str, status_map: dict[str, str]) -> str:
    if not status_map:
        return "clean"
    prefix = rel.rstrip("/") + "/"
    codes = [code for path, code in status_map.items() if path == rel or path.startswith(prefix)]
    if not codes:
        return "clean"
    if all(code == "??" for code in codes):
        return "untracked"
    if any(code == "??" for code in codes):
        return "mixed"
    return "modified"


def skill_snapshot(path: Path) -> dict[str, Any]:
    files: dict[str, str] = {}
    for file_path in iter_files(path):
        rel = file_path.relative_to(path).as_posix()
        files[rel] = hash_file(file_path) or "unreadable"
    combined = hashlib.sha256(
        "\n".join(f"{rel}:{files[rel]}" for rel in sorted(files)).encode("utf-8")
    ).hexdigest()
    return {"files": files, "fingerprint": combined, "file_count": len(files)}


def classify_change(old_files: dict[str, str], new_files: dict[str, str]) -> tuple[str | None, str]:
    """Suggest a semver bump from a per-file hash diff. Returns (suggestion, reason).

    Rules: edited/renamed files -> patch; new files -> minor; files both added and
    removed (a merge or rewrite) -> major. Renames are paired by identical hash so
    they read as patch, not as add+remove. This is a suggestion, never an auto-bump.
    """
    old_keys, new_keys = set(old_files), set(new_files)
    added = new_keys - old_keys
    deleted = old_keys - new_keys
    modified = {k for k in old_keys & new_keys if old_files[k] != new_files[k]}
    added_by_hash: dict[str, list[str]] = {}
    for k in added:
        added_by_hash.setdefault(new_files[k], []).append(k)
    renames: list[tuple[str, str]] = []
    remaining_deleted: set[str] = set()
    for k in deleted:
        bucket = added_by_hash.get(old_files[k])
        if bucket:
            renames.append((k, bucket.pop()))
        else:
            remaining_deleted.add(k)
    remaining_added = {k for bucket in added_by_hash.values() for k in bucket}
    if remaining_added and remaining_deleted:
        return "major", "files added and removed (possible merge or rewrite)"
    if remaining_added:
        return "minor", "new files added"
    if remaining_deleted:
        return "minor", "files removed"
    if renames and not modified:
        return "patch", "files renamed"
    if modified or renames:
        return "patch", "files edited"
    return None, "no change"


def _is_rename(old_files: dict[str, str], new_files: dict[str, str]) -> bool:
    """True when two snapshots are the same skill under a new name.

    A rename changes the ``name:`` field in SKILL.md, so the tree fingerprint is not
    identical. Treat it as a rename when the file set matches and every file except
    SKILL.md is byte-identical (SKILL.md may differ only by its name field).
    """
    if not old_files or set(old_files) != set(new_files):
        return False
    return all(old_files[k] == new_files[k] for k in old_files if k != "SKILL.md")


def _build_entry(name: str, rel: str, version: str | None, snap: dict[str, Any],
                 head: str | None, files: dict[str, str] | None = None,
                 fingerprint: str | None = None) -> dict[str, Any]:
    return {
        "version": version,
        "name": name,
        "path": rel,
        "commit": head,
        "fingerprint": fingerprint if fingerprint is not None else snap["fingerprint"],
        "file_count": snap["file_count"],
        "files": files if files is not None else snap["files"],
    }


def _norm_version(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def check_versions(registry: Path, jobs: int) -> tuple[list[tuple[str, str, str, str, str]], Counter]:
    """Track registry skill versions against a stored baseline.

    Warns when a skill changed (committed or working-tree) without a version bump,
    suggesting patch/minor/major from the change shape. A move (same name, new path,
    unchanged content) needs no bump; a rename suggests patch. New skills are recorded
    as a baseline. The state file is updated: bumps and moves rebaseline, unbumped
    changes keep the old baseline so the warning persists.
    """
    skills = registry_skills(registry)
    state = load_versions(registry)
    old_entries = state.get("skills", {})
    head = git_head(registry)
    names = sorted(skills)
    snaps = map_concurrent(lambda n: skill_snapshot(skills[n]), names, jobs)
    frontmatters = map_concurrent(lambda n: read_frontmatter(skills[n] / "SKILL.md"), names, jobs)
    current: dict[str, dict[str, Any]] = {}
    for n, snap, (data, _err) in zip(names, snaps, frontmatters):
        current[n] = {
            "rel": skills[n].relative_to(registry).as_posix(),
            "ver": _norm_version(data.get("version") if isinstance(data, dict) else None),
            "snap": snap,
        }
    by_fp: dict[str, str] = {}
    for n, e in old_entries.items():
        if e.get("fingerprint"):
            by_fp.setdefault(e["fingerprint"], n)
    cur_names = set(current)
    warnings: list[tuple[str, str, str, str, str]] = []
    stats: Counter = Counter()
    new_entries: dict[str, Any] = {}
    consumed: set[str] = set()

    for n in names:
        c = current[n]
        snap, rel, ver = c["snap"], c["rel"], c["ver"]
        valid = ver is not None and SEMVER_RE.match(ver) is not None
        if ver is None:
            warnings.append((n, "-", f"set {INITIAL_VERSION}", "missing version", rel))
            stats["missing_version"] += 1
        elif not valid:
            warnings.append((n, ver, "fix to X.Y.Z", "invalid version (expected semver X.Y.Z)", rel))
            stats["invalid_version"] += 1

        if n in old_entries:
            match, kind = n, "name"
        else:
            match, kind = None, "new"
            fp_name = by_fp.get(snap["fingerprint"])
            if fp_name and fp_name not in cur_names and fp_name not in consumed:
                match, kind = fp_name, "rename"
            else:
                for sn in sorted(old_entries):
                    if sn in cur_names or sn in consumed:
                        continue
                    if _is_rename(old_entries[sn].get("files", {}), snap["files"]):
                        match, kind = sn, "rename"
                        break

        if kind == "new":
            stats["new"] += 1
            new_entries[n] = _build_entry(n, rel, ver, snap, head)
            continue

        consumed.add(match)
        e = old_entries[match]
        old_ver = _norm_version(e.get("version"))
        old_files = e.get("files", {})
        old_fp = e.get("fingerprint")
        old_path = e.get("path")
        sugg, reason = classify_change(old_files, snap["files"])
        path_changed = old_path != rel
        bumped = valid and ver != old_ver

        if kind == "rename":
            if bumped:
                stats["bumped"] += 1
                sv, sf, sfp = ver, snap["files"], snap["fingerprint"]
            else:
                stats["unbumped"] += 1
                warnings.append((n, ver or "-", "patch", "skill renamed", rel))
                sv, sf, sfp = old_ver, old_files, old_fp
        elif sugg is None and path_changed:
            stats["moved"] += 1
            sv, sf, sfp = (ver if valid else old_ver), snap["files"], snap["fingerprint"]
        elif sugg is None:
            stats["unchanged"] += 1
            sv, sf, sfp = (ver if valid else old_ver), snap["files"], snap["fingerprint"]
        elif bumped:
            stats["bumped"] += 1
            sv, sf, sfp = ver, snap["files"], snap["fingerprint"]
        else:
            stats["unbumped"] += 1
            extra = f"; moved from {old_path}" if path_changed else ""
            warnings.append((n, ver or "-", sugg or "patch", reason + extra, rel))
            sv, sf, sfp = old_ver, old_files, old_fp
        new_entries[n] = _build_entry(n, rel, sv, snap, head, files=sf, fingerprint=sfp)

    for n in old_entries:
        if n not in consumed:
            stats["deleted"] += 1

    new_state = {"version": 1, "skills": new_entries}
    if new_state != state:
        save_versions(registry, new_state)
    return warnings, stats


def cmd_report(args: argparse.Namespace, registry: Path, jobs: int) -> int:
    skills = registry_skills(registry)
    names = sorted(skills)
    if args.skills:
        wanted = set(args.skills)
        names = [n for n in names if n in wanted]
        missing = wanted - set(names)
        for n in sorted(missing):
            display_warn(f"no registry skill named '{n}'")
    if not names:
        display_warn(f"no skills found in {registry}")
        return 0
    status_map = git_status_map(registry)
    head = git_head(registry)
    frontmatters = map_concurrent(lambda n: read_frontmatter(skills[n] / "SKILL.md"), names, jobs)
    snaps = map_concurrent(lambda n: skill_snapshot(skills[n]), names, jobs)
    rows: list[dict[str, Any]] = []
    for n, (data, _err), snap in zip(names, frontmatters, snaps):
        ver, desc_len = "-", 0
        if isinstance(data, dict):
            v = data.get("version")
            ver = str(v) if v is not None else "-"
            d = data.get("description")
            desc_len = len(d) if isinstance(d, str) else 0
        rel = skills[n].relative_to(registry).as_posix()
        row = {
            "name": n, "version": ver, "files": snap["file_count"],
            "desc": desc_len, "git": skill_git_state(rel, status_map), "path": rel,
        }
        if _DISPLAY.verbose:
            row["last_commit"] = git_last_commit(registry, rel) or "-"
        rows.append(row)
    sort_key = args.sort
    rows.sort(key=lambda r: r[sort_key] if sort_key != "name" else r["name"].lower(),
              reverse=args.reverse)
    if args.json:
        print(json.dumps({"registry": str(registry), "head": head, "skills": rows}, indent=2))
        return 0
    headers = ["Skill", "Version", "Files", "Desc chars", "Git", "Path"]
    table_rows = [[r["name"], r["version"], str(r["files"]), str(r["desc"]), r["git"], r["path"]] for r in rows]
    if _DISPLAY.verbose:
        headers.insert(5, "Last commit")
        for r, tr in zip(rows, table_rows):
            tr.insert(5, r.get("last_commit", "-"))
    display_table(headers, table_rows, title=f"skill report ({len(rows)})", always=True)
    total_files = sum(r["files"] for r in rows)
    avg_desc = round(sum(r["desc"] for r in rows) / len(rows)) if rows else 0
    summary = [
        ("Skills", str(len(rows))),
        ("Total files", str(total_files)),
        ("Avg description chars", str(avg_desc)),
        ("Sorted by", f"{sort_key}{' (desc)' if args.reverse else ' (asc)'}"),
        ("Git HEAD", head or "-"),
    ]
    display_kv(summary, title="report summary", always=True)
    return 0


def cmd_find(args: argparse.Namespace, registry: Path, jobs: int) -> int:
    """Locate a skill everywhere it could live: the registry inventory, the agent
    folders (live junctions and hard copies), the recorded --into installs, and the
    lockfile. Stale --into records are pruned on sight. Exit 0 when any name resolves."""
    names: list[str] = []
    for item in args.skills:
        candidate = Path(item).expanduser()
        if candidate.is_dir() and has_skill(candidate):
            names.append(candidate.name)
        else:
            names.append(item)
    registry_real = os.path.normcase(os.path.realpath(str(registry))) + os.sep
    installs = load_installs(registry)
    removed = prune_installs(registry)
    if removed:
        installs = load_installs(registry)
        display_info(f"[installs] pruned {len(removed)} stale --into record(s)")
    locked = load_lockfile(registry).get("locked", {})
    found_any = False
    for name in dict.fromkeys(names):
        rows: list[list[str]] = []
        for path in walk_skills(registry, prune=False):
            if path.name == name:
                rel = path.relative_to(registry).as_posix()
                depth = len(path.relative_to(registry).parts)
                rows.append(["registry", "sub-skill" if depth > 1 else "inventory",
                             rel, ""])
        for agent in DEFAULT_AGENTS:
            directory = agent_skill_dir(agent)
            if not directory.is_dir():
                continue
            dest = directory / name
            if is_link_like(dest):
                kind = "junction" if is_reparse(dest) else "symlink"
                try:
                    tgt = os.path.realpath(dest)
                except OSError:
                    tgt = "?"
                if not dest.exists():
                    note = "BROKEN link"
                elif os.path.normcase(os.path.realpath(tgt)).startswith(registry_real):
                    note = "live twin -> this registry"
                else:
                    note = "live, points elsewhere"
                rows.append([f"agent:{agent}", kind, tgt, note])
            elif dest.is_dir() and has_skill(dest):
                rows.append([f"agent:{agent}", "hard copy", str(dest), "real folder"])
        for entry in installs.get("into", {}).values():
            if entry.get("skill") != name:
                continue
            target = Path(entry.get("target", ""))
            alive = target.exists() or is_link_like(target)
            rows.append(["into (recorded)", entry.get("mode", "link"), str(target),
                         f"installed {entry.get('installed_at', '-')}" if alive
                         else "STALE on disk"])
        if name in locked:
            rows.append(["lockfile", "locked", ", ".join(sorted(locked[name])), ""])
        if rows:
            found_any = True
            display_table(
                ["Where", "Kind", "Path / target", "Note"],
                rows,
                title=f"find: {name} ({len(rows)} location(s))",
                always=True,
            )
        else:
            display_warn(
                f"find: '{name}' not in the registry, any agent folder, or any recorded "
                f"--into install; nothing else is known about it"
            )
    return 0 if found_any else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-r", "--registry", type=Path, default=None,
        help="registry root (default: the folder containing manager.py)",
    )
    parser.add_argument(
        "-j", "--jobs", type=int, default=None,
        help="concurrent reads for hashing and linting (default: CPU-based)",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress reports; warnings still print")
    parser.add_argument("-v", "--verbose", action="store_true", help="show extra detail in reports")
    parser.add_argument("-C", "--no-color", action="store_true", help="plain ASCII output, no rich rendering")


def add_deploy_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-f", "--force", action="store_true", help="replace real paths or modified copies")
    parser.add_argument("-d", "--dry-run", action="store_true", help="show what would happen, change nothing")


def add_mode_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-M", "--mode", choices=["symlink", "copy"], default="symlink",
        help="legacy alias: 'copy' is the same as --hard-copy (default: symlink)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manager.py",
        description="Link or hard-copy skills into agent folders, deploy AGENTS.md, lint skills, report skill stats, and find where a skill lives.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python manager.py skill avatar\n"
            "  python manager.py avatar mine --agents opencode,gemini\n"
            "  python manager.py skill --all --lock\n"
            "  python manager.py skill avatar --into ./my-project --hard-copy\n"
            "  python manager.py skill --refresh\n"
            "  python manager.py agent --agents claude,opencode\n"
            "  python manager.py lint --strict\n"
            "  python manager.py lint --readme\n"
            "  python manager.py report --sort files --reverse\n"
            "  python manager.py report techstack --json\n"
            "  python manager.py find techstack\n"
            "  python manager.py find pages revoke --quiet\n"
            "  python manager.py viber --into ./my-project --hard-copy\n"
        ),
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", metavar="{skill,agent,lint,viber,report,find}")

    skill = subparsers.add_parser(
        "skill",
        help="link or copy skills (default command)",
        description="Link or copy named skills into global agent folders or a project folder.",
    )
    add_common(skill)
    add_deploy_flags(skill)
    add_mode_flag(skill)
    skill.add_argument("skills", nargs="*", help="skill name(s) or a path to a skill directory")
    skill.add_argument("-a", "--all", action="store_true", help="every skill in the registry")
    skill.add_argument("-A", "--agents", default="all", help="comma-separated agents or 'all'")
    skill.add_argument("-l", "--lock", action="store_true", help="record installs in the manager database")
    skill.add_argument("-R", "--refresh", action="store_true", help="repair existing and locked entries")
    skill.add_argument("-i", "--into", default=None, help="project folder to install into instead of agent folders")
    skill.add_argument("-c", "--hard-copy", action="store_true", help="copy instead of link and track sync")
    skill.add_argument("-B", "--no-backup", action="store_true", help="skip the backup before --refresh")
    skill.add_argument("-L", "--list", action="store_true", help="list registry skills and exit")

    viber = subparsers.add_parser(
        "viber",
        help="install every skill the Viber lifecycle uses, in one shot",
        description=(
            "Link or copy the whole Viber skill set (listed in Groups/Viber/viber.json) into global "
            "agent folders or a project folder. Same flags and behaviour as `skill`; the skill list "
            "comes from the manifest instead of the command line."
        ),
    )
    add_common(viber)
    add_deploy_flags(viber)
    add_mode_flag(viber)
    viber.add_argument("-A", "--agents", default="all", help="comma-separated agents or 'all'")
    viber.add_argument("-l", "--lock", action="store_true", help="record installs in the manager database")
    viber.add_argument("-i", "--into", default=None, help="project folder to install into instead of agent folders")
    viber.add_argument("-c", "--hard-copy", action="store_true", help="copy instead of link and track sync")
    viber.add_argument("-L", "--list", action="store_true", help="list the viber skills and where they resolve, then exit")
    viber.set_defaults(skills=[], all=False, refresh=False, no_backup=False)

    agent = subparsers.add_parser(
        "agent",
        help="deploy AGENTS.md to agent configurations",
        description="Link or copy the registry's AGENTS.md into every agent's global instruction file.",
    )
    add_common(agent)
    add_deploy_flags(agent)
    add_mode_flag(agent)
    agent.add_argument("-A", "--agents", default="all", help="comma-separated agents or 'all'")
    agent.add_argument("-c", "--hard-copy", action="store_true", help="copy instead of link and track sync")

    lint = subparsers.add_parser(
        "lint",
        help="validate skill metadata and installation synchronization",
        description="Check all nested SKILL.md metadata and audit installed copies and links.",
    )
    add_common(lint)
    lint.add_argument(
        "-i", "--into", action="append", default=None, metavar="PATH",
        help="extra project folder to scan (repeatable)",
    )
    lint.add_argument(
        "-m", "--max-description", type=int, default=DEFAULT_DESCRIPTION_LIMIT,
        help=f"description character limit (default: {DEFAULT_DESCRIPTION_LIMIT})",
    )
    lint.add_argument(
        "-S", "--strict", action="store_true",
        help="exit 1 when there are description warnings, sync issues or README issues",
    )
    lint.add_argument(
        "--readme", action="store_true",
        help="also check README.md against the registry: counts, entries, categories, "
             "descriptions, usage, nesting, archive list and links",
    )
    lint.add_argument(
        "--no-version", action="store_true",
        help="skip skill version tracking (missing-version and unbumped-change warnings)",
    )

    report = subparsers.add_parser(
        "report",
        help="report per-skill file count, description length, version and git state",
        description="Summarize registry skills: file count, description length, version, "
                    "and git working-tree state. Sortable; optional JSON output.",
    )
    add_common(report)
    report.add_argument("skills", nargs="*", help="optional skill names to filter the report")
    report.add_argument(
        "--sort", choices=["name", "files", "desc", "version"], default="name",
        help="sort column (default: name)",
    )
    report.add_argument("--reverse", action="store_true", help="sort descending")
    report.add_argument("--json", action="store_true", help="emit JSON instead of a table")

    find = subparsers.add_parser(
        "find",
        help="locate a skill in the registry, agent folders, or recorded --into installs",
        description="Search every known place a skill can live: this registry, the global "
                    "agent folders (junctions and hard copies), installs recorded from "
                    "--into deploys, and the lockfile. Read-only; exit 0 when any name "
                    "resolves, 1 when nothing does. Stale --into records are pruned on sight.",
    )
    add_common(find)
    find.add_argument(
        "skills", nargs="+",
        help="skill name(s), or a path to a skill folder (its name is used)",
    )

    return parser


VALUE_FLAGS = {
    "-r", "--registry", "-j", "--jobs", "-A", "--agents",
    "-i", "--into", "-m", "--max-description",
}


def split_command(argv: Sequence[str]) -> tuple[str, list[str], bool]:
    """Return (command, remaining argv, implicit_default)."""
    index = 0
    while index < len(argv):
        token = argv[index]
        if token in COMMANDS:
            return token, list(argv[:index]) + list(argv[index + 1:]), False
        if token in VALUE_FLAGS:
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        break
    return "skill", list(argv), True


def invoked_flags(argv: Sequence[str]) -> set[str]:
    return {token.split("=", 1)[0] for token in argv if token.startswith("-")}


def skill_flag_labels(args: argparse.Namespace) -> list[str]:
    labels: list[str] = []
    if args.all:
        labels.append("-a/--all")
    if args.agents != "all":
        labels.append("-A/--agents")
    if args.lock:
        labels.append("-l/--lock")
    if args.refresh:
        labels.append("-R/--refresh")
    if args.into:
        labels.append("-i/--into")
    if args.hard_copy:
        labels.append("-c/--hard-copy")
    if args.mode != "symlink":
        labels.append("-M/--mode")
    if args.no_backup:
        labels.append("-B/--no-backup")
    if args.list:
        labels.append("-L/--list")
    if args.force:
        labels.append("-f/--force")
    if args.dry_run:
        labels.append("-d/--dry-run")
    if args.quiet:
        labels.append("-q/--quiet")
    if args.verbose:
        labels.append("-v/--verbose")
    if args.no_color:
        labels.append("-C/--no-color")
    return labels


def skill_settings(args: argparse.Namespace, registry: Path) -> list[tuple[str, str]]:
    if args.refresh:
        action = "refresh"
    elif args.list:
        action = "list"
    elif args.all:
        action = "all registry skills"
    else:
        action = ", ".join(args.skills) if args.skills else "none"
    destination = f"into {args.into}" if args.into else f"global agents ({args.agents})"
    mode = "hard-copy" if (args.hard_copy or args.mode == "copy") else "symlink"
    return [
        ("Registry", str(registry)),
        ("Destination", destination),
        ("Mode", mode),
        ("Skills", action),
    ]


def lint_flag_labels(args: argparse.Namespace) -> list[str]:
    labels: list[str] = []
    if args.into:
        labels.append("-i/--into")
    if args.max_description != DEFAULT_DESCRIPTION_LIMIT:
        labels.append("-m/--max-description")
    if args.strict:
        labels.append("-S/--strict")
    if args.readme:
        labels.append("--readme")
    if args.no_version:
        labels.append("--no-version")
    if args.quiet:
        labels.append("-q/--quiet")
    if args.verbose:
        labels.append("-v/--verbose")
    if args.no_color:
        labels.append("-C/--no-color")
    return labels


def report_flag_labels(args: argparse.Namespace) -> list[str]:
    labels: list[str] = []
    if args.skills:
        labels.append("skills filter")
    if args.sort != "name":
        labels.append("--sort")
    if args.reverse:
        labels.append("--reverse")
    if args.json:
        labels.append("--json")
    if args.quiet:
        labels.append("-q/--quiet")
    if args.verbose:
        labels.append("-v/--verbose")
    if args.no_color:
        labels.append("-C/--no-color")
    return labels


def main(argv: Sequence[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    raw = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    if not raw or raw[0] in {"-h", "--help"}:
        parser.print_help()
        return 0
    if raw[0] in {"-V", "--version"}:
        print(f"manager.py {__version__}")
        return 0

    command, rest, implicit = split_command(raw)
    try:
        args = parser.parse_args([command] + rest)
    except SystemExit as exc:
        return int(exc.code or 0)

    configure_display(
        quiet=args.quiet,
        color=not args.no_color and not os.environ.get("NO_COLOR"),
        verbose=args.verbose,
    )
    registry = (args.registry or REGISTRY).expanduser().resolve()
    jobs = args.jobs if args.jobs is not None else min(32, (os.cpu_count() or 4) * 4)

    try:
        if not registry.is_dir():
            raise ManagerError(f"registry not found: {registry}")
        if jobs < 1:
            raise ManagerError("--jobs must be 1 or greater")

        invoked = invoked_flags(rest)

        # --list is a fast registry read; do not run the sync audit first.
        if command == "skill" and args.list:
            return cmd_skill(args, registry, jobs, invoked)
        if command == "viber" and args.list:
            return cmd_viber(args, registry, jobs, invoked)

        if command in {"skill", "viber"}:
            settings = skill_settings(args, registry)
            if command == "viber":
                settings[-1] = ("Skills", f"viber set ({VIBER_MANIFEST.as_posix()})")
            display_command_report(
                command,
                settings=settings,
                flags=skill_flag_labels(args),
                implicit=implicit,
            )
        elif command == "agent":
            display_command_report(
                "agent",
                settings=[
                    ("Registry", str(registry)),
                    ("Agents", args.agents),
                    ("Mode", "hard-copy" if (args.hard_copy or args.mode == "copy") else "symlink"),
                ],
                flags=[
                    label for label, active in [
                        ("-A/--agents", args.agents != "all"),
                        ("-c/--hard-copy", args.hard_copy),
                        ("-M/--mode", args.mode != "symlink"),
                        ("-f/--force", args.force),
                        ("-d/--dry-run", args.dry_run),
                        ("-q/--quiet", args.quiet),
                        ("-v/--verbose", args.verbose),
                        ("-C/--no-color", args.no_color),
                    ] if active
                ],
                implicit=implicit,
            )
        elif command == "report":
            display_command_report(
                "report",
                settings=[
                    ("Registry", str(registry)),
                    ("Skills", ", ".join(args.skills) if args.skills else "all registry skills"),
                    ("Sort", f"{args.sort}{' (desc)' if args.reverse else ' (asc)'}"),
                ],
                flags=report_flag_labels(args),
                implicit=implicit,
            )
            return cmd_report(args, registry, jobs)
        elif command == "find":
            display_command_report(
                "find",
                settings=[
                    ("Registry", str(registry)),
                    ("Skills", ", ".join(args.skills)),
                ],
                flags=[
                    label for label, active in [
                        ("-q/--quiet", args.quiet),
                        ("-v/--verbose", args.verbose),
                        ("-C/--no-color", args.no_color),
                    ] if active
                ],
                implicit=implicit,
            )
            return cmd_find(args, registry, jobs)
        else:
            display_command_report(
                "lint",
                settings=[
                    ("Registry", str(registry)),
                    ("Extra roots", ", ".join(args.into) if args.into else "none"),
                    ("Description limit", f"{args.max_description} characters"),
                ],
                flags=lint_flag_labels(args),
                implicit=implicit,
            )

        issues = audit_all(registry, DEFAULT_AGENTS, jobs)
        display_sync_banner(issues)

        if command == "skill":
            return cmd_skill(args, registry, jobs, invoked)
        if command == "viber":
            return cmd_viber(args, registry, jobs, invoked)
        if command == "agent":
            return cmd_agent(args, registry)
        return cmd_lint(args, registry, jobs, issues)
    except ManagerError as exc:
        display_error(str(exc))
        return 1
    except KeyboardInterrupt:
        display_error("interrupted")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())



