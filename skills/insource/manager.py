#!/usr/bin/env python3
"""Unified skill and agent manager for the insource registry.

Commands
--------
    python manager.py skill <name> ...     link/copy skills (default command)
    python manager.py agent                deploy AGENTS.md to agent configs
    python manager.py lint                 validate SKILL.md descriptions and sync

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
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
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

__version__ = "2.0.0"

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
MANIFEST_NAME = "manager-copies.json"
LOCKFILE_NAME = "skills-lock.json"
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
COMMANDS = {"skill", "agent", "lint"}


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
# hard-copy manifest
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


def manifest_path(registry: Path) -> Path:
    return registry / MANIFEST_NAME


def load_manifest(registry: Path) -> dict[str, Any]:
    path = manifest_path(registry)
    if not path.exists():
        return {"version": 1, "copies": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "copies": {}}
    if not isinstance(data, dict):
        return {"version": 1, "copies": {}}
    data.setdefault("version", 1)
    copies = data.setdefault("copies", {})
    if not isinstance(copies, dict):
        data["copies"] = {}
    return data


def save_manifest(registry: Path, data: dict[str, Any]) -> None:
    path = manifest_path(registry)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


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
        for name, source in known.items():
            direct = root / name
            if is_link_like(direct):
                if not direct.exists():
                    add("link", name, direct, "broken-link", f"link target is gone (expected {source})")
                elif not same_path(direct, source):
                    add("link", name, direct, "wrong-target",
                        f"points at {os.path.realpath(direct)} instead of {source}")
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
    path = registry_root / LOCKFILE_NAME
    if not path.exists():
        return {"version": 1, "locked": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "locked": {}}
    if not isinstance(data, dict):
        return {"version": 1, "locked": {}}
    data.setdefault("version", 1)
    data.setdefault("locked", {})
    return data


def save_lockfile(registry_root: Path, data: dict[str, Any]) -> None:
    path = registry_root / LOCKFILE_NAME
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


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
                return "unchanged", f"-> {src}"
            if not dry_run:
                remove_entry(dest)
                make_link(src, dest)
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
        display_info(f"[lock] recorded {len(successful)} skill(s) into {LOCKFILE_NAME}")
    return 1 if failures else 0


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
        except Exception:
            data = None
        if isinstance(data, dict):
            return data, None
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
    for path in walk_skills(registry):
        add(path.name, path, "registry")
    for agent in DEFAULT_AGENTS:
        root = agent_skill_dir(agent)
        if root.is_dir():
            for path in walk_skills(root):
                add(path.name, path, f"agent:{agent}")
    for root in extra_roots:
        if root.is_dir():
            for path in walk_skills(root):
                add(path.name, path, f"into:{root}")
    return list(seen.values())


def cmd_lint(args: argparse.Namespace, registry: Path, jobs: int, issues: Sequence[SyncIssue]) -> int:
    limit = args.max_description
    if limit <= 0:
        raise ManagerError("--max-description must be a positive number")
    extra_roots = [resolve_into(value) for value in (args.into or [])]
    records = list(load_records(registry).values())
    skills = lint_skill_dirs(registry, extra_roots, records)
    if not skills:
        display_warn(f"no SKILL.md files found in {registry} or the configured skill folders")
        return 0

    frontmatters = map_concurrent(
        lambda item: read_frontmatter(item[1] / "SKILL.md"), skills, jobs
    )
    warnings: list[tuple[str, str, Path, int | None, str]] = []
    checked_rows: list[list[str]] = []
    total_checked = 0
    for (name, path, label), (data, error) in zip(skills, frontmatters):
        total_checked += 1
        if data is None:
            warnings.append((name, label, path, None, error or "missing frontmatter"))
            checked_rows.append([name, label, "missing", "missing", str(path)])
            continue
        description = data.get("description")
        if not isinstance(description, str) or not description.strip():
            warnings.append((name, label, path, None, "missing description"))
            checked_rows.append([name, label, "missing", "missing", str(path)])
            continue
        length = len(description)
        state = "over" if length > limit else "ok"
        checked_rows.append([name, label, str(length), state, str(path)])
        if length > limit:
            warnings.append((name, label, path, length, "over limit"))

    if warnings:
        rows = []
        for name, label, path, length, reason in warnings:
            if length is None:
                rows.append([name, label, "missing", str(limit), "-", reason])
            else:
                rows.append([name, label, str(length), str(limit), str(length - limit), reason])
        display_table(
            ["Skill", "Location", "Chars", "Limit", "Over by", "Issue"],
            rows,
            title=f"description warnings ({len(warnings)})",
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

    hard_copies = sum(1 for record in records if record.kind == "dir")
    display_kv(
        [
            ("Registry", str(registry)),
            ("Roots scanned", str(1 + len(extra_roots) + sum(
                1 for agent in DEFAULT_AGENTS if agent_skill_dir(agent).is_dir()
            ))),
            ("SKILL.md files checked", str(total_checked)),
            ("Hard copies tracked", str(hard_copies)),
            ("Description warnings", str(len(warnings))),
            ("Synchronization issues", str(len(issues))),
            ("Description limit", f"{limit} characters"),
        ],
        title="lint summary",
        always=True,
    )
    if not warnings and not issues:
        display_ok(
            f"all {total_checked} SKILL.md files are within {limit} characters and every copy is in sync"
        )

    return 1 if (args.strict and (warnings or issues)) else 0


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
        description="Link or hard-copy skills into agent folders, deploy AGENTS.md, and lint skills.",
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
        ),
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", metavar="{skill,agent,lint}")

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
    skill.add_argument("-l", "--lock", action="store_true", help="record installs in skills-lock.json")
    skill.add_argument("-R", "--refresh", action="store_true", help="repair existing and locked entries")
    skill.add_argument("-i", "--into", default=None, help="project folder to install into instead of agent folders")
    skill.add_argument("-c", "--hard-copy", action="store_true", help="copy instead of link and track sync")
    skill.add_argument("-B", "--no-backup", action="store_true", help="skip the backup before --refresh")
    skill.add_argument("-L", "--list", action="store_true", help="list registry skills and exit")

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
        help="validate descriptions and copy synchronization",
        description="Check every SKILL.md description against the limit and audit hard-copy sync.",
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
        help="exit 1 when there are description warnings or sync issues",
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

        if command == "skill":
            display_command_report(
                "skill",
                settings=skill_settings(args, registry),
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



