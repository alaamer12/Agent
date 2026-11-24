#!/usr/bin/env python3
"""Unified skill and agent manager for the insource registry.

Commands
--------
    python manager.py skill <name> ...     link/copy skills (default command)
    python manager.py interactive          checklist TUI: pick which skills stay installed
    python manager.py agent                deploy _Resources/AGENTS.md to agent configs
    python manager.py lint                 validate SKILL.md descriptions and sync
    python manager.py viber                install every skill the Viber lifecycle uses
    python manager.py crossreference       discover directed mentions between skills

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
import posixpath
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

__version__ = "2.12.0"

# ---------------------------------------------------------------------------
# optional dependencies
# ---------------------------------------------------------------------------

try:  # rich gives colour, boxes and wrapping; everything works without it
    from rich import box as rich_box
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table

    RICH_AVAILABLE = True
except Exception:  # pragma: no cover - exercised only without rich
    Console = None  # type: ignore[assignment]
    Panel = None  # type: ignore[assignment]
    Table = None  # type: ignore[assignment]
    rich_box = None  # type: ignore[assignment]
    RICH_AVAILABLE = False
    Live = None  # type: ignore[assignment]

try:  # PyYAML parses every frontmatter shape correctly; fallback is minimal
    import yaml
except Exception:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------

DEFAULT_DESCRIPTION_LIMIT = 1024
SKILL_LENGTH_LIMIT = 200
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
SPECIALIZED_GENERAL = "none"
SPECIALIZED_RE = re.compile(r"[a-z0-9][a-z0-9.+#-]*")
SPECIALIZED_REJECTED = {"general", "generic", "any", "all"}
SPECIALIZED_ALIASES = {
    "tailwindcss": "tailwind", "tw": "tailwind",
    "react native": "react-native", "rn": "react-native",
    "nextjs": "next.js",
    "vuejs": "vue", "vue.js": "vue",
    "nodejs": "node.js", "node": "node.js",
    "ts": "typescript", "js": "javascript",
    "postgres": "postgresql",
    "mmd": "mermaid", "gh": "github",
    "windows": "win32", "winapi": "win32",
    ".net": "dotnet", "csharp": "c#",
}
LINT_RULE_IDS = {
    "mixed-composition", "frontmatter", "version", "specialized",
    "name", "name-mismatch", "duplicate-name",
    "description", "description-multiline", "description-length",
    "skill-length", "argument-hint",
}
INITIAL_VERSION = "1.0.0"
DB_APP_DIR = "insource-manager"
DB_FILE_NAME = "manager.db"
LEGACY_STORE_FILES = {"copies": "manager-copies.json", "lock": "skills-lock.json",
                      "versions": "manager-versions.json"}
SKIP_NAMES = {"Archive", "_Archive", "_Resources", "__pycache__", "node_modules", ".git", ".venv", "venv"}
AGENT_SOURCE = Path("_Resources") / "AGENTS.md"
REFERENCE_SUFFIXES = {".md", ".mdx", ".txt", ".rst"}
REFERENCE_TOKEN_RE = re.compile(r"[\w-]+")
SKILL_SUPPORT_DIRS = {"reference", "references", "examples", "assets", "scripts", "templates",
                      "research", "docs", "tests", "evals", "fixtures", "data", "resources", "legacy"}
SKILL_TYPES = {"skill": "Skill", "meta-skill": "Meta-Skill", "battery-skill": "Battery-Skill"}
MIGRATION_AGENTS = {"qoder", "gemini"}

AGENT_SKILL_SUBDIRS: dict[str, Path] = {
    "qoder": Path(".qoder") / "skills",
    "junie": Path(".junie") / "skills",
    "gemini": Path(".gemini") / "config" / "skills",
    "opencode": Path(".config") / "opencode" / "skills",
    "claude": Path(".claude") / "skills",
}

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
COMMANDS = {"skill", "agent", "agents", "claim", "remote", "interactive", "lint", "viber", "report", "find", "crossreference"}


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


_AGENTS_CACHE: dict[str, dict[str, Any]] | None = None


def _agent_path(raw: str) -> Path:
    """A stored path may be absolute (user-set) or relative to the home
    directory (seeded default)."""
    path = Path(raw).expanduser()
    return path if path.is_absolute() else home_dir() / path


def agents_all(*, include_removed: bool = False) -> dict[str, dict[str, Any]]:
    """The agents table as {name: {skill_dir, md_paths, origin}}; removal
    tombstones are hidden unless asked for."""
    global _AGENTS_CACHE
    if _AGENTS_CACHE is None:
        conn = db_connect()
        try:
            rows = conn.execute(
                "SELECT name, skill_dir, md_paths, origin FROM agents ORDER BY name"
            ).fetchall()
        finally:
            conn.close()
        parsed: dict[str, dict[str, Any]] = {}
        for name, skill_dir, md_raw, origin in rows:
            try:
                mds = json.loads(md_raw)
            except (json.JSONDecodeError, TypeError):
                mds = []
            parsed[name] = {"skill_dir": skill_dir,
                            "md_paths": [str(m) for m in mds if str(m)],
                            "origin": origin}
        _AGENTS_CACHE = parsed
    if include_removed:
        return dict(_AGENTS_CACHE)
    return {n: r for n, r in _AGENTS_CACHE.items() if r["origin"] != "removed"}


def _agents_cache_clear() -> None:
    global _AGENTS_CACHE
    _AGENTS_CACHE = None


def agent_names() -> list[str]:
    return list(agents_all())


def agent_skill_dir(agent: str) -> Path:
    row = agents_all().get(agent)
    if row is None or not row["skill_dir"]:
        raise ManagerError(
            f"agent '{agent}' is not registered in the agents table; add it with "
            f"`manager.py agents --set {agent} --skill-dir PATH`"
        )
    return _agent_path(row["skill_dir"])


def agent_md_targets(agent: str) -> list[Path]:
    row = agents_all().get(agent)
    if row is None:
        raise ManagerError(
            f"agent '{agent}' is not registered in the agents table; add it with "
            f"`manager.py agents --set {agent} --skill-dir PATH`"
        )
    return [_agent_path(rel) for rel in row["md_paths"]]


AGENT_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,31}$")


def _store_agent_path(raw: str) -> str:
    """Store a user-supplied path as an absolute posix string."""
    return Path(raw).expanduser().absolute().as_posix()


def agents_set(name: str, *, skill_dir: str | None = None,
               md_paths: Sequence[str] | None = None, override: bool = False) -> tuple[str, str]:
    """Register or update one agents row. Returns (status, detail).
    Conflicts - a differing existing row or another agent owning the same
    skill dir - raise ManagerError unless override is set."""
    name = name.strip().lower()
    if not AGENT_NAME_RE.match(name):
        raise ManagerError(
            f"invalid agent name '{name}': lowercase letters, digits, dot, dash, "
            f"underscore, starting alphanumeric, max 32 characters"
        )
    all_rows = agents_all(include_removed=True)
    visible = agents_all()
    existing = all_rows.get(name)
    tombstoned = existing is not None and existing["origin"] == "removed"
    new_skill = _store_agent_path(skill_dir) if skill_dir else None
    new_mds = [_store_agent_path(p) for p in md_paths] if md_paths else None
    if new_skill is None and new_mds is None:
        raise ManagerError("agents --set needs at least --skill-dir or --md-path")
    if tombstoned and new_skill is None:
        raise ManagerError(f"agent '{name}' was removed; re-registering needs --skill-dir")
    if new_skill:
        clash = next((n for n, r in visible.items() if n != name and r["skill_dir"] == new_skill), None)
        if clash and not override:
            raise ManagerError(
                f"conflict: the skill dir '{new_skill}' already belongs to agent '{clash}'. "
                f"Pass --override to let '{name}' share it."
            )
    final_skill = new_skill or (existing["skill_dir"] if existing else "")
    final_mds = new_mds if new_mds is not None else (existing["md_paths"] if existing else [])
    if existing is not None and not tombstoned:
        if existing["skill_dir"] == final_skill and existing["md_paths"] == final_mds:
            return "unchanged", f"skill: {final_skill}; md: {', '.join(final_mds) or 'none'}"
        if not override:
            raise ManagerError(
                f"conflict: agent '{name}' is already registered as skill '{existing['skill_dir']}'"
                f", md [{', '.join(existing['md_paths']) or 'none'}]; the given values differ. "
                f"Pass --override to replace them."
            )
    conn = db_connect()
    try:
        conn.execute(
            "INSERT INTO agents (name, skill_dir, md_paths, origin, updated_at) VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET skill_dir = excluded.skill_dir, "
            "md_paths = excluded.md_paths, origin = excluded.origin, updated_at = excluded.updated_at",
            (name, final_skill, json.dumps(final_mds), "user",
             datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
    finally:
        conn.close()
    _agents_cache_clear()
    status = "added" if existing is None else ("re-registered" if tombstoned else "updated")
    return status, f"skill: {final_skill}; md: {', '.join(final_mds) or 'none'}"


def agents_remove(name: str) -> str:
    """Remove an agent. Seeded defaults become tombstones so they never
    re-seed behind the user; user-registered rows are deleted outright."""
    name = name.strip().lower()
    if name not in agents_all():
        raise ManagerError(
            f"agent '{name}' is not in the agents table (known: "
            f"{', '.join(agent_names()) or 'none'})"
        )
    conn = db_connect()
    try:
        if name in AGENT_SKILL_SUBDIRS:
            conn.execute(
                "UPDATE agents SET origin = 'removed', skill_dir = '', md_paths = '[]', updated_at = ? "
                "WHERE name = ?",
                (datetime.now().isoformat(timespec="seconds"), name),
            )
        else:
            conn.execute("DELETE FROM agents WHERE name = ?", (name,))
        conn.commit()
    finally:
        conn.close()
    _agents_cache_clear()
    return "tombstoned" if name in AGENT_SKILL_SUBDIRS else "deleted"


def cmd_agents(args: argparse.Namespace) -> int:
    if getattr(args, "inventory", False):
        return cmd_agents_inventory(args)
    if args.set and args.remove:
        raise ManagerError("--set and --remove are exclusive")
    if args.remove:
        kind = agents_remove(args.remove)
        display_info(f"[agents] '{args.remove}' {kind} (deployments on disk were not touched)")
    if args.set:
        status, detail = agents_set(args.set, skill_dir=args.skill_dir,
                                    md_paths=args.md_path, override=args.override)
        display_info(f"[agents] {status} '{args.set}' - {detail}")
    if args.json:
        print(json.dumps(agents_all(), ensure_ascii=False, indent=2))
        return 0
    if not (args.set or args.remove or args.list):
        display_info("no action given; showing the table (see --help for --set/--remove)")
    rows = [[name, r["skill_dir"], " | ".join(r["md_paths"]) or "-", r["origin"]]
            for name, r in sorted(agents_all(include_removed=True).items())]
    display_table(["Agent", "Skill dir", "Instruction files", "Origin"], rows,
                  title=f"{len([r for r in rows if r[3] != 'removed'])} agents (agents table)",
                  always=True)
    return 0


def agent_skill_inventory(directory: Path, registry: Path) -> list[dict[str, Any]]:
    """Installed skills in one agent directory: name, kind, source.
    Links resolve; managed hard copies carry their record's origin."""
    out: list[dict[str, Any]] = []
    try:
        entries = sorted(directory.iterdir(), key=lambda p: p.name.lower())
    except OSError:
        return out
    for entry in entries:
        if entry.name.startswith("."):
            continue
        if is_link_like(entry):
            kind = "symlink" if entry.is_symlink() else "junction"
            if not has_skill(entry):
                kind = "broken-link"
            out.append({"name": entry.name, "kind": kind,
                        "source": os.path.realpath(entry)})
        elif entry.is_dir() and has_skill(entry):
            rec = get_record(registry, entry)
            out.append({"name": entry.name,
                        "kind": "managed-copy" if rec else "unmanaged-dir",
                        "source": rec.source if rec else str(entry)})
    return out


def cmd_agents_inventory(args: argparse.Namespace) -> int:
    registry = (args.registry or REGISTRY).expanduser().resolve()
    data = {}
    rows: list[list[str]] = []
    for name in agent_names():
        directory = agent_skill_dir(name)
        items = agent_skill_inventory(directory, registry)
        data[name] = {"dir": str(directory), "skills": items}
        if not directory.is_dir():
            rows.append([name, "-", "-", "dir absent"])
            continue
        if not items:
            rows.append([name, "-", "-", "no skills installed"])
        for item in items:
            rows.append([name, item["name"], item["kind"], item["source"]])
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    total = sum(len(v["skills"]) for v in data.values())
    display_table(["Agent", "Skill", "Kind", "Source"], rows,
                  title=f"agent inventory ({len(data)} agents, {total} installed skills)",
                  always=True)
    return 0


def resolve_agent_dir(raw: str) -> tuple[Path, str]:
    """An agents-table name, or a direct folder path."""
    name = raw.strip().lower()
    if name in agents_all():
        return agent_skill_dir(name), name
    path = Path(raw).expanduser().absolute()
    return path, f"path:{path.as_posix()}"


def cmd_claim(args: argparse.Namespace, registry: Path) -> int:
    """Claim X into Y: Y ends with X's skill set. Modes: override (default)
    replaces shared entries, adds missing, and removes Y's manager-owned
    extras (unmanaged folders protected unless --force); --append adds only
    what Y lacks, deduped by name, never touching existing entries."""
    src_dir, src_label = resolve_agent_dir(args.from_agent)
    dst_dir, dst_label = resolve_agent_dir(args.into_agent)
    if same_path(src_dir, dst_dir):
        raise ManagerError("claim source and destination are the same folder")
    if is_under(dst_dir, registry):
        raise ManagerError("refusing to claim INTO the registry itself")
    if args.append and args.force:
        raise ManagerError("--append never removes; --force is meaningless with it")
    if not src_dir.is_dir():
        raise ManagerError(f"source '{src_label}' has no skills folder at {src_dir}")
    src_items = agent_skill_inventory(src_dir, registry)
    if not src_items:
        raise ManagerError(
            f"source '{src_label}' has no installed skills - refusing to claim an empty "
            f"set into '{dst_label}' (name a populated source, or remove entries explicitly)")
    src_items = [i for i in src_items if i["kind"] != "broken-link"]

    rows: list[list[str]] = []
    counts: Counter[str] = Counter()
    failures = 0
    dst_dir.parent.mkdir(parents=True, exist_ok=True)
    src_names = {i["name"] for i in src_items}
    for item in src_items:
        dest = dst_dir / item["name"]
        existing = is_link_like(dest) or dest.is_dir()
        if args.append and existing:
            rows.append([item["name"], src_label, dst_label, "kept",
                         "already installed (append never touches existing)"])
            counts["kept"] += 1
            continue
        mode = "symlink" if item["kind"] in ("symlink", "junction") else "hard-copy"
        source = Path(item["source"])
        # override replaces a same-named UNMANAGED folder: back it up first
        note_extra = ""
        if (existing and not args.append and not args.dry_run
                and not is_link_like(dest) and dest.is_dir()
                and get_record(registry, dest) is None):
            if not args.no_backup:
                archive = backup_dirs([dest], "claim-replace-backup")
                if archive is not None:
                    note_extra = f"; replaced unmanaged folder backed up as {archive.name}"
        status, detail = deploy_skill(
            source, dest, mode=mode, force=not args.append, agent=dst_label,
            registry=registry, dry_run=args.dry_run)
        rows.append([item["name"], str(source), dst_label, status, detail + note_extra])
        counts[status] += 1
        if status == "failed":
            failures += 1

    removed = 0
    if not args.append:
        for extra in agent_skill_inventory(dst_dir, registry):
            if extra["name"] in src_names:
                continue
            entry = dst_dir / extra["name"]
            if extra["kind"] == "broken-link" or is_link_like(entry):
                if not args.dry_run:
                    remove_entry(entry)
                rows.append([extra["name"], dst_label, "-",
                             "would unlink" if args.dry_run else "unlinked", "extra entry removed"])
                removed += 1
            elif extra["kind"] == "managed-copy":
                archive = None
                if not args.dry_run:
                    if not args.no_backup:
                        archive = backup_dirs([entry], "claim-remove-backup")
                    remove_tree_local(entry)
                    drop_record(registry, entry)
                rows.append([extra["name"], dst_label, "-",
                             "would remove copy" if args.dry_run else "removed copy",
                             "managed extra" + (f"; backup {archive.name}" if archive else "")])
                removed += 1
            elif args.force:
                archive = None
                if not args.dry_run:
                    if not args.no_backup:
                        archive = backup_dirs([entry], "claim-remove-backup")
                    remove_tree_local(entry)
                rows.append([extra["name"], dst_label, "-",
                             ("would remove" if args.dry_run else "removed") + " unmanaged",
                             "forced" + (f"; backup {archive.name}" if archive else "")])
                removed += 1
            else:
                rows.append([extra["name"], dst_label, "-", "protected",
                             "unmanaged folder not in source (use --force)"])
                counts["protected"] += 1
    counts["removed"] = removed
    display_table(["Skill", "From", "To", "Action", "Detail"], rows,
                  title=f"claim {src_label} -> {dst_label} "
                        f"({'append' if args.append else 'override'})",
                  always=True)
    display_counts(counts)
    summary = (f"[claim] {dst_label} now has {len(src_names)} of {src_label}'s skill set; "
               f"{counts.get('kept', 0)} kept, {removed} extra(s) removed")
    if args.dry_run:
        summary += " (dry run - nothing changed)"
    display_info(summary)
    return 1 if failures else 0


# ---------------------------------------------------------------------------
# remote skills: git-backed sources outside the registry
# ---------------------------------------------------------------------------

def remote_cache_root() -> Path:
    return db_path().parent / "remotes"


def _clear_readonly(func, path, *args) -> None:
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        pass


def remove_checkout_tree(path: Path) -> None:
    """Delete a manager-owned checkout. Git keeps loose objects read-only,
    which silently defeats rmtree(ignore_errors=True) on Windows."""
    if not path.exists():
        return
    try:
        shutil.rmtree(path, onexc=_clear_readonly)
    except TypeError:  # Python without onexc
        shutil.rmtree(path, onerror=_clear_readonly)


def remotes_all() -> dict[str, dict[str, Any]]:
    conn = db_connect()
    try:
        rows = conn.execute(
            "SELECT name, url, subpath, ref, head, added_at, updated_at FROM remotes ORDER BY name"
        ).fetchall()
    finally:
        conn.close()
    return {r[0]: {"name": r[0], "url": r[1], "subpath": r[2], "ref": r[3],
                   "head": r[4], "added_at": r[5], "updated_at": r[6]} for r in rows}


def remote_get(name: str) -> dict[str, Any] | None:
    return remotes_all().get(name.strip().lower())


def remote_upsert(name: str, url: str, subpath: str, ref: str, force: bool) -> str:
    """Register (or re-register) a remote. Returns added/updated/unchanged."""
    if not REMOTE_URL_RE.match(url) and not (os.path.isabs(url) and os.path.exists(url)):
        raise ManagerError(
            f"unsupported remote url '{url}': need https://, ssh://, git@host:path or an "
            "existing absolute local repo path")
    if not REMOTE_NAME_RE.match(name):
        raise ManagerError(f"invalid remote name '{name}': lowercase letters, digits, dot, "
                           "dash, underscore, max 64")
    existing = remote_get(name)
    if existing and existing["url"] != url and not force:
        raise ManagerError(
            f"conflict: remote '{name}' already points at '{existing['url']}'; "
            f"pass --force to re-point it to '{url}'.")
    status = "added" if existing is None else (
        "unchanged" if (existing["url"], existing["subpath"], existing["ref"]) == (url, subpath, ref)
        else "updated")
    conn = db_connect()
    try:
        conn.execute(
            "INSERT INTO remotes (name, url, subpath, ref, added_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(name) DO UPDATE SET url = excluded.url, "
            "subpath = excluded.subpath, ref = excluded.ref, updated_at = excluded.updated_at",
            (name, url, subpath, ref, datetime.now().isoformat(timespec="seconds"),
             datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
    finally:
        conn.close()
    return status


def remote_delete(name: str) -> None:
    conn = db_connect()
    try:
        cur = conn.execute("DELETE FROM remotes WHERE name = ?", (name,))
        conn.commit()
    finally:
        conn.close()
    if cur.rowcount == 0:
        raise ManagerError(f"no such remote '{name}' (known: "
                           f"{', '.join(remotes_all()) or 'none'})")


def derive_remote_name(url: str, subpath: str) -> str:
    def tail_of(raw: str) -> str:
        return raw.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]
    tail = tail_of(subpath or url)
    if tail in ("", "."):
        tail = tail_of(url)
    slug = re.sub(r"\.git$", "", tail)
    slug = re.sub(r"[^a-z0-9._-]+", "-", slug.lower()).strip("-.")[:64].strip("-.")
    return slug or "remote"


REMOTE_URL_RE = re.compile(r"^(https://|ssh://|git@)")
REMOTE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def remote_checkout(info: dict[str, Any]) -> Path:
    return remote_cache_root() / info["name"]


def remote_root(info: dict[str, Any]) -> Path | None:
    """The skill-search root inside the checkout (subpath), if fetched."""
    dest = remote_checkout(info) / info["subpath"] if info["subpath"] else remote_checkout(info)
    return dest if dest.is_dir() else None


def remote_skill_dirs(info: dict[str, Any]) -> list[Path]:
    root = remote_root(info)
    if root is None:
        return []
    if has_skill(root):
        return [root]
    return walk_skills(root)


def remote_fetch(info: dict[str, Any]) -> tuple[str, str]:
    """Clone or refresh the checkout. Manager owns this directory entirely."""
    name, url, ref = info["name"], info["url"], info["ref"]
    dest = remote_checkout(info)
    if (dest / ".git").exists():
        origin = _git(dest, "config", "--get", "remote.origin.url")
        if origin != url:
            remove_checkout_tree(dest)  # cache is manager-owned; re-clone
        else:
            before = _git(dest, "rev-parse", "HEAD")
            if ref:
                fetch_specs = [ref]
                resolve = "FETCH_HEAD"
            else:
                fetch_specs = ["+refs/heads/*:refs/remotes/origin/*"]
                resolve = "origin/HEAD"
            run = ["git", "-C", str(dest), "fetch", "--quiet", "--depth", "1", "origin",
                   *fetch_specs]
            proc = subprocess.run(run, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=180)
            if proc.returncode != 0:
                return "failed", f"fetch: {proc.stderr.strip()[:200]}"
            if not ref:
                subprocess.run(["git", "-C", str(dest), "remote", "set-head", "origin", "--auto"],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=60)
            proc = subprocess.run(["git", "-C", str(dest), "reset", "--quiet", "--hard",
                                   resolve], capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=60)
            if proc.returncode != 0:
                return "failed", f"reset: {proc.stderr.strip()[:200]}"
            after = _git(dest, "rev-parse", "HEAD")
            conn = db_connect()
            try:
                conn.execute("UPDATE remotes SET head = ?, updated_at = ? WHERE name = ?",
                             (after, datetime.now().isoformat(timespec="seconds"), name))
                conn.commit()
            finally:
                conn.close()
            return ("updated" if after != before else "unchanged"), (after or "")[:9]
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "clone", "--quiet", "--depth", "1"]
    cmd += ["--branch", ref] if ref else []
    cmd += [url, str(dest)]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=300)
    if proc.returncode != 0:
        remove_checkout_tree(dest)
        return "failed", f"clone: {proc.stderr.strip()[:200]}"
    head = _git(dest, "rev-parse", "HEAD")
    conn = db_connect()
    try:
        conn.execute("UPDATE remotes SET head = ?, updated_at = ? WHERE name = ?",
                     (head, datetime.now().isoformat(timespec="seconds"), name))
        conn.commit()
    finally:
        conn.close()
    return "cloned", (head or "")[:9]


def remote_skill_index() -> dict[str, Path]:
    """name -> skill dir, across fetched remotes (audit support)."""
    out: dict[str, Path] = {}
    for info in remotes_all().values():
        for d in remote_skill_dirs(info):
            out.setdefault(d.name, d)
    return out


def cmd_remote(args: argparse.Namespace) -> int:
    if args.add and args.remove:
        raise ManagerError("--add and --remove are exclusive")
    if args.add:
        name = args.name or derive_remote_name(args.add, args.path or "")
        status = remote_upsert(name, args.add, args.path or "", args.ref or "", args.force)
        info = remote_get(name)
        fstatus, detail = remote_fetch(info)
        rows = [[name, args.add, args.path or "-", args.ref or "-", fstatus, detail]]
        display_table(["Remote", "URL", "Subpath", "Ref", "Fetch", "Head"], rows,
                      title=f"remote {status} '{name}'", always=True)
        return 0 if fstatus != "failed" else 1
    if args.remove:
        info = remote_get(args.remove)
        if info is None:
            raise ManagerError(f"no such remote '{args.remove}' (known: "
                               f"{', '.join(remotes_all()) or 'none'})")
        victims: list[str] = []
        for agent_dir in [agent_skill_dir(a) for a in agent_names()]:
            if not agent_dir.is_dir():
                continue
            for entry in agent_dir.iterdir():
                if is_link_like(entry):
                    try:
                        if os.path.commonpath([os.path.realpath(entry),
                                               str(remote_checkout(info))]) == str(remote_checkout(info)):
                            victims.append(f"{entry.parent.name}/{entry.name}")
                    except (ValueError, OSError):
                        pass
        remote_delete(args.remove)
        remove_checkout_tree(remote_checkout(info))
        display_info(f"[remote] '{args.remove}' unregistered and its manager-owned cache deleted")
        if victims:
            display_warn("agent links still point into the removed cache: "
                         + ", ".join(victims) + " - re-point with `skill --remote` or clean with `skill -U`")
        return 0
    if args.update:
        targets = args.names or sorted(remotes_all())
        if not targets:
            display_info("no remotes registered; nothing to update")
            return 0
        rows, failures = [], 0
        for name in targets:
            info = remote_get(name.lower())
            if info is None:
                display_error(f"no such remote '{name}'")
                failures += 1
                continue
            status, detail = remote_fetch(info)
            rows.append([name, info["url"], status, detail])
            if status == "failed":
                failures += 1
        display_table(["Remote", "URL", "Fetch", "Head"], rows, title="remote update", always=True)
        return 1 if failures else 0
    data = {}
    rows = []
    for info in remotes_all().values():
        dirs = remote_skill_dirs(info)
        data[info["name"]] = {**info, "cache": str(remote_checkout(info)),
                              "skills": [d.name for d in dirs]}
        rows.append([info["name"], info["url"], info["subpath"] or "-", info["ref"] or "-",
                     str(len(dirs)) if remote_root(info) else "not fetched",
                     info["updated_at"] or info["added_at"]])
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    display_table(["Remote", "URL", "Subpath", "Ref", "Skills", "Updated"], rows,
                  title=f"{len(rows)} remotes (remotes table)", always=True)
    if not rows:
        display_info("no remotes registered; add one with `manager.py remote --add URL` "
                     "or install directly: `manager.py skill --remote URL`")
    return 0


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


def remove_tree_local(path: Path) -> None:
    """Delete a real directory tree WITHOUT following links or junctions:
    nested reparse points are removed as entries, never descended."""
    for entry in os.scandir(path):
        child = Path(entry.path)
        if is_link_like(child):
            remove_entry(child)
        elif entry.is_dir(follow_symlinks=False):
            remove_tree_local(child)
        else:
            child.unlink()
    path.rmdir()


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
        _ensure_agents_table(conn)
        _ensure_remotes_table(conn)
    except sqlite3.Error:
        conn.close()
        raise
    return conn


def _ensure_agents_table(conn: sqlite3.Connection) -> None:
    """Create the agents table and seed the built-in defaults once per name.
    Rows (including removal tombstones) survive later calls, so a removed
    default is never resurrected behind the user's back."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS agents ("
        "name TEXT PRIMARY KEY, skill_dir TEXT NOT NULL, "
        "md_paths TEXT NOT NULL DEFAULT '[]', "
        "origin TEXT NOT NULL DEFAULT 'seed', updated_at TEXT NOT NULL)"
    )
    now = datetime.now().isoformat(timespec="seconds")
    for name, subdir in AGENT_SKILL_SUBDIRS.items():
        mds = json.dumps([p.as_posix() for p in AGENT_MD_SUBDIRS.get(name, [])])
        conn.execute(
            "INSERT OR IGNORE INTO agents (name, skill_dir, md_paths, origin, updated_at) "
            "VALUES (?, ?, ?, 'seed', ?)",
            (name, subdir.as_posix(), mds, now),
        )
    conn.commit()


def _ensure_remotes_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS remotes ("
        "name TEXT PRIMARY KEY, url TEXT NOT NULL, subpath TEXT NOT NULL DEFAULT '', "
        "ref TEXT NOT NULL DEFAULT '', head TEXT NOT NULL DEFAULT '', "
        "added_at TEXT NOT NULL, updated_at TEXT NOT NULL)"
    )
    conn.commit()


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


def drop_install(registry: Path, target: Path) -> bool:
    """Remove the --into install index row for a target, if present."""
    data = load_installs(registry)
    into = data.setdefault("into", {})
    if _key(target) in into:
        del into[_key(target)]
        kv_set(registry, "installs", data)
        return True
    return False


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
    kind: str  # "hard-copy", "link", "folder" or "agent-md"
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
    nested = nested_skill_index(registry)
    remote_index = remote_skill_index()
    locked = load_lockfile(registry).get("locked", {})
    record_keys = set(load_records(registry))
    expected_md = registry / AGENT_SOURCE
    for agent in agents:
        for md_target in agent_md_targets(agent):
            if is_link_like(md_target):
                if not md_target.exists():
                    add("agent-md", "AGENTS.md", md_target, "broken-link",
                        f"instruction link target is gone (expected {expected_md})")
                elif not same_path(md_target, expected_md):
                    add("agent-md", "AGENTS.md", md_target, "wrong-target",
                        f"points at {os.path.realpath(md_target)} instead of {expected_md}")
            elif md_target.is_file() and expected_md.is_file():
                if md_target.read_bytes() != expected_md.read_bytes():
                    add("agent-md", "AGENTS.md", md_target, "stale-copy",
                        f"content differs from {AGENT_SOURCE.as_posix()}; run `agent` to relink")
        root = agent_skill_dir(agent)
        if not root.is_dir():
            continue
        for direct in sorted(root.iterdir()):
            name = direct.name
            if not is_link_like(direct):
                if (direct.is_dir() and name not in SKIP_NAMES and not name.startswith(".")
                        and not has_skill(direct)):
                    nested_skills = sorted(p.relative_to(direct).as_posix() for p in walk_skills(direct))
                    detail = ("folder has no top-level SKILL.md"
                              + (f"; nested skill(s) below it: {', '.join(nested_skills)}" if nested_skills else ""))
                    add("folder", name, direct, "missing-skill", detail)
                continue
            source = known.get(name) or nested.get(name) or remote_index.get(name)
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
    owned: set[Path] = set()
    for dirpath, dirnames, _ in os.walk(root):
        current = Path(dirpath)
        if has_skill(current):
            owned.add(current)
            if current != root:
                found.append(current)
                if prune:
                    dirnames[:] = []
                    continue
        inside_skill = current in owned or current.parent in owned
        if inside_skill:
            owned.add(current)
        dirnames[:] = sorted(
            name for name in dirnames
            if name not in SKIP_NAMES and not name.startswith(".")
            and not is_link_like(current / name)
            and (not inside_skill or name.lower() not in SKILL_SUPPORT_DIRS
                 or has_skill(current / name))
        )
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


def nested_skill_index(root: Path) -> dict[str, Path]:
    """Uniquely-nested skills (meta-children): name -> path.

    registry_skills() lists only what an install can address by name; children
    installed as their own junction (scss under styling, ...) resolve here.
    Ambiguous names are left out so nothing is ever relinked to a guessed
    location. Used by the sync audit and `skill --refresh` to detect and repair
    links when a skill's tree moved inside the registry.
    """
    top = set(registry_skills(root))
    index: dict[str, list[Path]] = {}
    for path in walk_skills(root, prune=False):
        name = path.name
        if name in top:
            continue
        index.setdefault(name, []).append(path)
    return {name: paths[0] for name, paths in index.items() if len(paths) == 1}


@dataclass(frozen=True)
class SkillStructure:
    kind: str
    children: tuple[Path, ...] = ()
    modules: tuple[Path, ...] = ()
    issues: tuple[str, ...] = ()


def inspect_directory(path: Path) -> SkillStructure:
    if not path.is_dir():
        return SkillStructure("broken-link" if is_link_like(path) else "plain")
    children = tuple(walk_skills(path))
    if not has_skill(path):
        return SkillStructure("group" if children else "plain", children)

    modules: list[Path] = []

    def visit(parent: Path) -> None:
        for branch in sorted(parent.iterdir()):
            if (not branch.is_dir() or is_link_like(branch) or has_skill(branch)
                    or branch.name in SKIP_NAMES or branch.name.startswith(".")
                    or branch.name.lower() in SKILL_SUPPORT_DIRS):
                continue
            if any(is_under(child, branch) for child in children):
                visit(branch)
            elif any(file.suffix.lower() == ".md" for file in iter_files(branch)):
                modules.append(branch)

    visit(path)
    kind = "meta-skill" if children else "battery-skill" if modules else "skill"
    issues = ()
    if children and modules:
        names = ", ".join(p.relative_to(path).as_posix() for p in modules)
        issues = (f"mixed composition: independent sub-skills and internal modules ({names}); "
                  "choose meta children with SKILL.md or battery modules without it",)
    return SkillStructure(kind, children, tuple(modules), issues)


def classify_directory(path: Path) -> str:
    return inspect_directory(path).kind


def skill_parent(path: Path, skills: Iterable[Path]) -> Path | None:
    parents = [parent for parent in skills if parent != path and is_under(path, parent)]
    return max(parents, key=lambda parent: len(parent.parts)) if parents else None


def diagnose_missing_skill(name: str, cwd: Path, registry_root: Path) -> str:
    """Provide detailed, actionable diagnostic feedback when a requested skill cannot be resolved."""
    roots: list[Path] = []
    for root in (cwd, registry_root):
        if root and root.is_dir() and not any(same_path(root, r) for r in roots):
            roots.append(root)

    # 1. Check if the name points to an existing directory
    for root in roots:
        candidate = (root / name) if not Path(name).is_absolute() else Path(name)
        if candidate.is_dir():
            structure = inspect_directory(candidate)
            if structure.kind == "group":
                child_count = len(structure.children)
                return (
                    f"'{name}' is an organizational group folder holding {child_count} skill(s), "
                    f"not an independent skill.\n"
                    f"Deploy individual skills instead, or run 'manager.py find {name}' to inspect them."
                )

            parent = skill_parent(candidate, (p for p in candidate.parents if has_skill(p)))
            if parent and any(same_path(candidate, m) for m in inspect_directory(parent).modules):
                return (
                    f"'{name}' is an internal module of the '{parent.name}' battery-skill, "
                    f"not an independent skill.\n"
                    f"Deploy the parent skill instead: 'manager.py skill {parent.name}'"
                )

            if not has_skill(candidate):
                return (
                    f"directory '{name}' exists but has no SKILL.md entrypoint; "
                    f"it cannot be deployed as an independent skill."
                )

    # 2. Check if the requested name matches an internal module of any battery-skill
    search_roots: list[Path] = []
    for root in (cwd, registry_root):
        if root and root.is_dir() and not any(same_path(root, r) for r in search_roots):
            search_roots.append(root)

    for root in search_roots:
        for skill_path in walk_skills(root, prune=False):
            structure = inspect_directory(skill_path)
            for module in structure.modules:
                if module.name == name or module.name.lower() == name.lower():
                    return (
                        f"'{name}' is an internal module of the '{skill_path.name}' battery-skill, "
                        f"not an independent skill.\n"
                        f"Deploy the parent skill instead: 'manager.py skill {skill_path.name}'"
                    )

    # Default fallback
    return f"no skill named '{name}' found in {cwd} or the registry {registry_root}"


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

    raise ManagerError(diagnose_missing_skill(name, cwd, registry_root))


def parse_agents(raw: str) -> list[str]:
    available = agent_names()
    if not raw:
        return available
    requested = [part.strip().lower() for part in raw.replace(",", " ").split() if part.strip()]
    if not requested or "all" in requested:
        return available
    result: list[str] = []
    unknown: list[str] = []
    for item in requested:
        name = ALIASES.get(item, item)
        if name not in agents_all():
            unknown.append(item)
        elif name not in result:
            result.append(name)
    if unknown:
        raise ManagerError(
            f"unknown agent(s): {', '.join(unknown)}. Registered: {', '.join(available)} - "
            f"add one with `manager.py agents --set NAME --skill-dir PATH`"
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
    archive.parent.mkdir(parents=True, exist_ok=True)
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
    if args.remove and (args.refresh or args.list):
        raise ManagerError("--remove cannot combine with --refresh/--list")
    if args.remote and (args.remove or args.refresh or args.list):
        raise ManagerError("--remote cannot combine with --remove/--refresh/--list")
    if args.list:
        skills = registry_skills(registry)
        rows = [[name, str(path.relative_to(registry))] for name, path in sorted(skills.items())]
        display_table(["Skill", "Path"], rows, title=f"{len(skills)} registry skills", always=True)
        return 0

    into = resolve_into(args.into) if args.into else None
    if into is not None and ({"-A", "--agents"} & invoked):
        raise ManagerError("--into targets one folder; drop --agents")

    if args.remove:
        return cmd_skill_remove(args, registry, into)

    if args.refresh:
        if args.skills or args.all:
            raise ManagerError("--refresh cannot be combined with skill names or --all")
        return cmd_refresh(args, registry, jobs, into)

    hard = bool(args.hard_copy or args.mode == "copy")
    if args.hard_copy and args.mode == "symlink" and ({"-M", "--mode"} & invoked):
        raise ManagerError("--hard-copy and --mode symlink contradict each other")
    mode = "hard-copy" if hard else "symlink"

    if args.remote:
        if args.all:
            raise ManagerError("--remote takes its skill list from the checkout; drop --all")
        if args.lock:
            display_warn("--lock records registry skills only; remote installs are not locked")
        sources = remote_sources(args.remote, list(args.skills))
    else:
        if args.all:
            names = sorted(registry_skills(registry))
        else:
            names = list(args.skills)
        if not names:
            raise ManagerError("name at least one skill, or use --all / --refresh")

        sources = []
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

    if args.lock and successful and not args.dry_run and not args.remote:
        record_locks(registry, successful, parse_agents(args.agents))
        display_info(f"[lock] recorded {len(successful)} skill(s) into the manager database")
    return 1 if failures else 0


def remote_sources(url: str, names: list[str]) -> list[Path]:
    """Resolve skill source dirs inside a remote checkout, registering and
    fetching the remote as needed. The registration key is the URL-derived
    name so `skill --remote` and `remote --add` agree on one entry."""
    rname = derive_remote_name(url, "")
    info = remote_get(rname)
    if info is not None and info["url"] != url:
        raise ManagerError(
            f"a remote named '{rname}' already points at '{info['url']}'; register this URL "
            f"under another name first: `manager.py remote --add {url} --name NAME`")
    if info is None:
        remote_upsert(rname, url, "", "", force=False)
        info = remote_get(rname)
        display_info(f"[remote] registered '{rname}' -> {url}")
    status, detail = remote_fetch(info)
    if status == "failed":
        raise ManagerError(f"remote fetch failed for '{rname}': {detail}")
    display_info(f"[remote] '{rname}': {status} ({detail})")
    dirs = remote_skill_dirs(info)
    if not dirs:
        raise ManagerError(
            f"no skill found in remote '{rname}' (checkout: {remote_checkout(info)}); if the "
            "skills live in a subfolder, register it first: "
            f"`manager.py remote --add {url} --path SUBPATH`")
    by_name = {d.name: d for d in dirs}
    if names:
        sources = []
        for raw in names:
            key = Path(raw.rstrip("/\\")).name
            hit = by_name.get(key)
            if hit is None:
                display_error(f"'{key}' is not a skill in remote '{rname}' "
                              f"(available: {', '.join(sorted(by_name))})")
            else:
                sources.append(hit)
        return sources
    if len(dirs) > 1:
        rows = [[d.name, d.relative_to(remote_checkout(info)).as_posix()] for d in dirs]
        display_table(["Skill", "Path in checkout"], rows, title=f"remote '{rname}' skills")
        raise ManagerError(
            f"remote '{rname}' holds {len(dirs)} skills; name the ones to install")
    return dirs


def remove_lock_entry(registry: Path, name: str, agent: str | None) -> None:
    """Drop the --lock row for (skill, agent); prune the skill when empty."""
    if agent is None:
        return
    data = load_lockfile(registry)
    entry = data.get("locked", {}).get(name)
    if isinstance(entry, dict) and agent in entry:
        del entry[agent]
        if not entry:
            del data["locked"][name]
        save_lockfile(registry, data)


def cmd_skill_remove(args: argparse.Namespace, registry: Path, into: Path | None) -> int:
    """Uninstall deployed skills - links, junctions and tracked hard copies -
    from agent folders or --into. Registry sources are never touched."""
    if args.all:
        names = sorted(registry_skills(registry))
    else:
        names = []
        for raw in args.skills:
            name = Path(raw.rstrip("/\\")).name
            if not name:
                raise ManagerError(f"--remove: cannot derive a skill name from '{raw}'")
            if name not in names:
                names.append(name)
    if not names:
        raise ManagerError("--remove: name at least one skill, or use --all")

    if into is not None:
        roots: list[tuple[str, Path, str | None]] = [(f"into {into}", into, None)]
    else:
        roots = [(agent, agent_skill_dir(agent), agent) for agent in parse_agents(args.agents)]

    rows: list[list[str]] = []
    counts: Counter[str] = Counter()
    failures = 0
    for label, root, agent in roots:
        for name in names:
            target = root / name
            exists_or_link = False
            try:
                exists_or_link = target.exists() or is_link_like(target)
            except OSError:
                pass
            if not exists_or_link:
                rows.append([label, name, "-", "absent", str(target)])
                counts["absent"] += 1
                continue
            if is_under(target, registry) or same_path(target, registry):
                rows.append([label, name, "-", "protected", "registry source is never removed here"])
                counts["protected"] += 1
                continue
            if is_link_like(target):
                kind = "symlink" if target.is_symlink() else "junction"
                detail = f"-> {os.path.realpath(target)}"
                if not args.dry_run:
                    try:
                        remove_entry(target)
                    except OSError as exc:
                        rows.append([label, name, kind, "failed", str(exc)])
                        counts["failed"] += 1
                        failures += 1
                        continue
                    drop_install(registry, target)
                    remove_lock_entry(registry, name, agent)
                rows.append([label, name, kind, "would unlink" if args.dry_run else "unlinked", detail])
                counts["unlinked"] += 1
                continue
            if target.is_file():
                if not args.force:
                    rows.append([label, name, "file", "skipped", "stray file, unmanaged (use --force)"])
                    counts["skipped"] += 1
                    continue
                if not args.dry_run:
                    remove_entry(target)
                rows.append([label, name, "file", "removed file" if not args.dry_run else "would remove file",
                             "unmanaged"])
                counts["removed"] += 1
                continue
            # real directory: managed copy, or unmanaged tree
            record = get_record(registry, target)
            managed = record is not None
            if not managed and not args.force:
                rows.append([label, name, "directory", "skipped",
                             "unmanaged directory, not a tracked copy (use --force)"])
                counts["skipped"] += 1
                continue
            action = ("would remove copy" if args.dry_run else "removed copy") if managed \
                else ("would remove tree" if args.dry_run else "removed tree")
            detail = "tracked in manager database" if managed else "unmanaged (forced)"
            if not args.dry_run:
                if not args.no_backup:
                    archive = backup_dirs([target], "skill-remove-backup")
                    if archive is not None:
                        detail += f"; backup {archive.name}"
                try:
                    remove_tree_local(target)
                except OSError as exc:
                    rows.append([label, name, "directory", "failed", str(exc)])
                    counts["failed"] += 1
                    failures += 1
                    continue
                drop_record(registry, target)
                drop_install(registry, target)
                remove_lock_entry(registry, name, agent)
            rows.append([label, name, "directory", action, detail])
            counts["removed"] += 1

    display_table(["Target", "Skill", "Kind", "Action", "Detail"], rows, title="skill removal")
    display_counts(counts)
    if not args.dry_run and counts.get("removed", 0) + counts.get("unlinked", 0):
        removed_rows = prune_installs(registry)
        if removed_rows:
            display_info(f"[installs] pruned {len(removed_rows)} stale index row(s)")
    return 1 if failures else 0


# ---------------------------------------------------------------------------
# interactive checklist picker
# ---------------------------------------------------------------------------

def checklist_step(visible: Sequence[str], selected: set[str], cursor: int,
                   key: str) -> tuple[int, set[str], str]:
    """Pure checklist transitions, shared by the TUI, its tests and prompts.
    Returns (cursor, selected copy, action) with action in move/toggle/all/
    done/quit/none."""
    out = set(selected)
    if key == "up":
        return max(0, cursor - 1), out, "move"
    if key == "down":
        return min(max(0, len(visible) - 1), cursor + 1), out, "move"
    if key == "home":
        return 0, out, "move"
    if key == "end":
        return max(0, len(visible) - 1), out, "move"
    if key == "pgup":
        return max(0, cursor - 10), out, "move"
    if key == "pgdn":
        return min(max(0, len(visible) - 1), cursor + 10), out, "move"
    if key == "space" and visible:
        name = visible[min(cursor, len(visible) - 1)]
        if name in out:
            out.discard(name)
        else:
            out.add(name)
        return cursor, out, "toggle"
    if key == "a" and visible:
        if any(name not in out for name in visible):
            out.update(visible)
        else:
            out.difference_update(visible)
        return cursor, out, "all"
    if key == "enter":
        return cursor, out, "done"
    if key in ("q", "esc", "ctrl-c"):
        return cursor, out, "quit"
    return cursor, out, "none"


def _read_key() -> str:
    """One keypress as a logical name (up/down/space/enter/esc/...); single
    printable characters come back lowercased."""
    if os.name == "nt":
        import msvcrt

        ch = msvcrt.getwch()
        if ch == "\x03":
            return "ctrl-c"
        if ch in ("\x00", "\xe0"):
            extended = msvcrt.getwch()
            return {"H": "up", "P": "down", "K": "left", "M": "right",
                    "G": "home", "O": "end", "I": "pgup", "Q": "pgdn",
                    "S": "delete"}.get(extended, "")
        if ch == "\x1b":
            return "esc"
        if ch in ("\r", "\n"):
            return "enter"
        if ch == "\x08":
            return "backspace"
        if ch == " ":
            return "space"
        return ch.lower()
    import select
    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ch = sys.stdin.read(1)
        if ch == "\x03":
            return "ctrl-c"
        if ch == "\x1b":
            if not select.select([sys.stdin], [], [], 0)[0]:
                return "esc"
            seq = sys.stdin.read(1)
            if seq == "[":
                code = sys.stdin.read(1)
                return {"A": "up", "B": "down", "C": "right", "D": "left",
                        "H": "home", "F": "end", "5": "pgup", "6": "pgdn"}.get(code, "")
            return "esc"
        if ch in ("\r", "\n"):
            return "enter"
        if ch in ("\x7f", "\x08"):
            return "backspace"
        if ch == " ":
            return "space"
        return ch.lower()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _checklist_lines(visible: Sequence[str], selected: set[str], cursor: int,
                     installed: set[str], height: int) -> tuple[list[str], int]:
    """Plain-text checklist window; returns (lines, top index kept on screen)."""
    top = min(max(0, cursor), max(0, len(visible) - 1))
    if cursor >= top + height:
        top = cursor - height + 1
    elif cursor < top:
        top = cursor
    top = max(0, min(top, len(visible) - height))
    lines = []
    for index in range(top, min(top + height, len(visible))):
        name = visible[index]
        box = "x" if name in selected else " "
        mark = ">" if index == cursor else " "
        tag = "installed" if name in installed else "-"
        lines.append(f"{mark} [{box}] {name:<30} {tag}")
    if not lines:
        lines.append("  (no skills match the filter)")
    return lines, top


_QUESTIONARY: Any = None
_QUESTIONARY_TRIED = False


def _questionary() -> Any:
    """Return the questionary module, or None when it is not installed.

    Imported on demand: only the interactive picker needs it, and prompt_toolkit
    is heavy enough to be noticed by --help and --json runs."""
    global _QUESTIONARY, _QUESTIONARY_TRIED
    if not _QUESTIONARY_TRIED:
        _QUESTIONARY_TRIED = True
        try:
            import questionary as module
        except Exception:  # pragma: no cover - exercised only without questionary
            module = None
        _QUESTIONARY = module
    return _QUESTIONARY


def _questionary_style(q: Any) -> Any:
    """One palette shared by the picker and the apply confirmation."""
    return q.Style([
        ("qmark", "fg:ansicyan bold"),
        ("question", "bold"),
        ("pointer", "fg:ansicyan bold"),
        ("highlighted", "fg:ansicyan bold"),
        ("selected", "fg:ansigreen"),
        ("answer", "fg:ansigreen bold"),
        ("instruction", "fg:ansibrightblack"),
        ("text", ""),
    ])


def _pick_checkbox(q: Any, names: Sequence[str], selected: set[str],
                   installed: set[str]) -> set[str] | None:
    """Multi-select through questionary: coloured rows, a real cursor row and
    type-to-filter search. None means the user cancelled."""
    width = min(36, max([len(name) for name in names] + [12]))
    choices = [
        q.Choice(
            title=(f"{name}{' ' * max(2, width - len(name))}installed"
                   if name in installed else name),
            value=name,
            checked=name in selected,
        )
        for name in names
    ]
    try:
        answer = q.checkbox(
            f"skills: {len(set(names) & selected)} of {len(names)} installed"
            " - keep the ones you want",
            choices=choices,
            style=_questionary_style(q),
            use_search_filter=True,
            use_jk_keys=False,
        ).ask(kbi_msg="")
    except (KeyboardInterrupt, EOFError):
        return None
    return None if answer is None else set(answer)


def _pick_tui(names: Sequence[str], selected: set[str], installed: set[str]) -> set[str] | None:
    """Interactive multi-select: questionary when it is installed and colour is
    on, otherwise the built-in key loop. None means the user cancelled."""
    q = _questionary()
    if q is not None and _DISPLAY.color:
        return _pick_checkbox(q, names, selected, installed)
    return _pick_keys(names, selected, installed)


def _pick_keys(names: Sequence[str], selected: set[str], installed: set[str]) -> set[str] | None:
    """Arrow-key multi-select rendered with rich Live (or ANSI redraw). None
    means the user cancelled."""
    state_selected = set(selected)
    cursor = 0
    pending_filter = ""
    committed_filter = ""
    mode = "nav"
    height = max(5, shutil.get_terminal_size((100, 30)).lines - 8)
    sys.stdout.write("\x1b[?25l")

    def visible_now() -> list[str]:
        needle = committed_filter.lower()
        return [n for n in names if not needle or needle in n.lower()]

    def frame() -> str:
        visible = visible_now()
        lines, _top = _checklist_lines(visible, state_selected, cursor, installed, height)
        done = sum(1 for n in visible if n in state_selected)
        header = (f"skills: {len(state_selected & set(names))}/{len(names)} selected"
                  f" ({done}/{len(visible)} shown)"
                  + (f"   filter: {committed_filter}" if committed_filter else ""))
        hint = ("up/down move - space toggle - a all/none - / filter - enter plan - q quit"
                + ("   [typing filter: enter applies, esc cancels]" if mode == "filter" else ""))
        return "\n".join([header, *lines, hint])

    console = _console()
    use_live = console is not None and Live is not None
    if use_live:
        from rich.text import Text

    live: Any = None
    try:
        if use_live:
            live = Live(Text(frame()), console=console, transient=True,
                        refresh_per_second=12)
            live.__enter__()
        else:
            sys.stdout.write("\x1b[2J\x1b[H" + frame() + "\n")
            sys.stdout.flush()
        while True:
            key = _read_key()
            if key == "":
                continue
            redraw = True
            if mode == "filter":
                if key == "enter":
                    committed_filter = pending_filter
                    mode = "nav"
                elif key in ("esc", "ctrl-c"):
                    pending_filter = committed_filter
                    mode = "nav"
                elif key == "backspace":
                    pending_filter = pending_filter[:-1]
                elif len(key) == 1 and key.isprintable():
                    pending_filter += key
                else:
                    redraw = False
            elif key == "/":
                pending_filter = committed_filter
                mode = "filter"
            else:
                visible = visible_now()
                cursor, state_selected, action = checklist_step(visible, state_selected, cursor, key)
                cursor = min(cursor, max(0, len(visible) - 1))
                if action == "done":
                    return state_selected
                if action == "quit":
                    return None
                if action == "none":
                    redraw = False
            if not redraw:
                continue
            if live is not None:
                live.update(Text(frame()))
            else:
                sys.stdout.write("\x1b[2J\x1b[H" + frame() + "\n")
                sys.stdout.flush()
    finally:
        if live is not None:
            live.__exit__(None, None, None)
        sys.stdout.write("\x1b[0m\x1b[?25h")
        sys.stdout.flush()


def _pick_fallback(names: Sequence[str], selected: set[str], installed: set[str]) -> set[str] | None:
    """Numbered-prompt multi-select for pipes, dumb terminals and --no-tui."""
    shown = set(selected)
    display_info("[interactive] numbered picker (type skill numbers to toggle them)")
    for index, name in enumerate(names, start=1):
        box = "x" if name in shown else " "
        tag = " installed" if name in installed else ""
        print(f"  {index:>3}. [{box}] {name}{tag}")
    while True:
        try:
            raw = input("choose> ").strip().lower()
        except EOFError:
            return None
        if not raw:
            continue
        if raw in ("done", "d"):
            return shown
        if raw == "quit":
            return None
        if raw == "all":
            shown = set(names)
            continue
        if raw == "none":
            shown = set()
            continue
        for token in raw.replace(",", " ").split():
            if not token.isdigit():
                print(f"  ? '{token}' is not a number, 'all', 'none', 'done' or 'quit'")
                continue
            index = int(token)
            if not 1 <= index <= len(names):
                print(f"  ? no skill number {index} (1..{len(names)})")
                continue
            name = names[index - 1]
            if name in shown:
                shown.discard(name)
            else:
                shown.add(name)


def _confirm_apply(use_tui: bool) -> bool:
    """Ask before touching anything; a TUI answer gets a TUI question."""
    q = _questionary() if use_tui and _DISPLAY.color else None
    if q is not None:
        try:
            return bool(q.confirm("Apply changes?", default=False,
                                  style=_questionary_style(q)).ask(kbi_msg=""))
        except (KeyboardInterrupt, EOFError):
            return False
    try:
        answer = input("Apply changes? [y/N] ").strip().lower()
    except EOFError:
        answer = ""
    return answer in ("y", "yes")


def cmd_interactive(args: argparse.Namespace, registry: Path, jobs: int, invoked: set[str]) -> int:
    """Reconcile what stays installed: multi-select the skills to keep, then
    apply installs/uninstalls behind one [y/N] confirmation."""
    into = resolve_into(args.into) if args.into else None
    if into is not None and ({"-A", "--agents"} & invoked):
        raise ManagerError("--into targets one folder; drop --agents")
    skills = registry_skills(registry)
    if not skills:
        raise ManagerError("the registry holds no skills to pick from")
    if into is not None:
        roots: list[tuple[str, Path, str | None]] = [(f"into {into}", into, None)]
    else:
        roots = [(agent, agent_skill_dir(agent), agent) for agent in parse_agents(args.agents)]
    installed: set[str] = set()
    for _label, root, _agent in roots:
        installed.update(item["name"] for item in agent_skill_inventory(root, registry))

    names = sorted(skills, key=str.lower)
    selected = {name for name in names if name in installed}
    tui = not args.no_tui and sys.stdin.isatty() and sys.stdout.isatty()
    if tui:
        chosen = _pick_tui(names, selected, installed)
    else:
        chosen = _pick_fallback(names, selected, installed)
    if chosen is None:
        display_info("[interactive] cancelled; nothing changed")
        return 0

    to_install = sorted(chosen - installed, key=str.lower)
    to_remove = sorted(installed & (set(names) - chosen), key=str.lower)
    foreign = sorted(installed - set(names))
    rows = [[name, "install"] for name in to_install] + [[name, "uninstall"] for name in to_remove]
    title = (f"interactive plan: {len(to_install)} install, {len(to_remove)} uninstall, "
              f"{len(chosen & installed)} keep, {len(names) - len(chosen) - len(to_remove)} absent")
    if rows:
        display_table(["Skill", "Action"], rows, title=title, always=True)
    else:
        display_info(f"{title}; nothing to change")
        return 0
    if foreign:
        display_info(f"left untouched (installed but not registry skills): {', '.join(foreign)}")
    if args.dry_run:
        display_info("[interactive] dry-run: plan shown, nothing applied")
        return 0
    if not _confirm_apply(tui):
        display_info("[interactive] declined; nothing changed")
        return 0

    rc = 0
    if to_install:
        deploy_args = argparse.Namespace(
            skills=to_install, all=False, agents=args.agents, lock=args.lock,
            refresh=False, remove=False, list=False, remote=None, into=args.into,
            hard_copy=args.hard_copy, mode=args.mode, force=args.force,
            dry_run=False)
        rc |= cmd_skill(deploy_args, registry, jobs, set())
    if to_remove:
        remove_args = argparse.Namespace(
            skills=to_remove, all=False, agents=args.agents, dry_run=False,
            force=args.force, no_backup=args.no_backup)
        rc |= cmd_skill_remove(remove_args, registry, into)
    return rc


VIBER_MANIFEST = Path("../../projects/viber/viber.json")


def viber_plan(registry: Path) -> list[dict[str, Any]]:
    """Resolve the viber census into rows: phase, name, status, entry label, path (None = not in registry)."""
    manifest_file = registry / VIBER_MANIFEST
    if not manifest_file.is_file():
        raise ManagerError(f"viber manifest not found: {manifest_file}")
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManagerError(f"cannot read {manifest_file}: {exc}") from exc
    known = registry_skills(registry)
    manifest_dir = manifest_file.resolve().parent
    step_info: dict[str, dict[str, str]] = {}
    for step in manifest.get("lifecycle", []):
        for name in step.get("commands", []):
            step_info[name] = {"phase": step.get("step", "-"), "status": "command"}
    for name, entry in manifest.get("skills", {}).items():
        serves = entry.get("fit", {}).get("serves", [])
        if serves and name not in step_info:
            step_info[name] = {"phase": ", ".join(serves), "status": "mandatory"}
    rows: list[dict[str, Any]] = []
    for name, entry in manifest.get("skills", {}).items():
        info = step_info.get(name, {"phase": "-", "status": "-"})
        base = {"phase": info["phase"], "status": info["status"], "entry": name}
        path_str = entry.get("path")
        if path_str:
            base_dir = manifest_dir if entry.get("owned") else registry
            resolved = (base_dir / path_str).resolve()
            if has_skill(resolved):
                rows.append({**base, "name": name, "path": resolved})
            elif resolved.is_dir():
                for member in sorted(walk_skills(resolved), key=lambda p: p.name):
                    rows.append({**base, "name": member.name, "path": member})
            else:
                rows.append({**base, "name": name, "path": None})
        else:
            rows.append({**base, "name": name, "path": known.get(name)})
    return rows


def cmd_viber(args: argparse.Namespace, registry: Path, jobs: int, invoked: set[str]) -> int:
    rows = viber_plan(registry)
    if args.list:
        display_table(
            ["Phase", "Entry", "Skill", "Status", "Path"],
            [[row["phase"], row["entry"], row["name"], row["status"],
              str(row["path"].relative_to(registry)) if row["path"] and row["path"].is_relative_to(registry)
              else str(row["path"]) if row["path"] else "not in registry"] for row in rows],
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
    # Children installed as their own junction resolve through the nested
    # index, so a skill tree moved inside the registry is still repairable.
    repairable = {**nested_skill_index(registry), **known}

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
        if agent is not None:
            expected = registry / AGENT_SOURCE
            for md_target in agent_md_targets(agent):
                if not is_link_like(md_target):
                    continue
                if md_target.exists() and same_path(md_target, expected):
                    continue
                if not expected.is_file():
                    rows.append([label, "AGENTS.md", "failed", f"source missing: {expected}"])
                    counts["failed"] += 1
                    failures += 1
                    continue
                if not args.dry_run:
                    try:
                        remove_entry(md_target)
                        make_link(expected, md_target)
                    except OSError as exc:
                        rows.append([label, str(md_target), "failed", str(exc)])
                        counts["failed"] += 1
                        failures += 1
                        continue
                rows.append([label, "AGENTS.md", "would relink" if args.dry_run else "relinked",
                             f"{md_target} -> {expected}"])
                counts["would relink" if args.dry_run else "relinked"] += 1
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

        for name, places in scan_existing(root, set(repairable)).items():
            direct = root / name
            if _key(direct) in records:
                continue
            source = repairable[name]
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
    source = registry / AGENT_SOURCE
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
    remote_roots: Sequence[tuple[Path, str]] = (),
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
    roots = [(agent_skill_dir(agent), f"agent:{agent}") for agent in agent_names()]
    roots.extend((root, f"into:{root}") for root in extra_roots)
    roots.extend(remote_roots)
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
DOCS_NAME = "_Docs"
DOCS_CATALOG_FILES = ("quick-index.md", "skill-details.md", "archive.md")
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


def _resolve_readme_target(rel: str, base: str) -> str:
    """A cleaned (_readme_path'd) link target made registry-relative from a part's base dir."""
    return posixpath.normpath(posixpath.join(base, rel)) if base and rel else rel


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


def readme_parts(registry: Path) -> list[tuple[str, str]] | None:
    """(base_dir, text) parts the catalog is parsed from, in order, or None if README is missing.

    The legacy layout keeps every catalog section inside README.md; the split
    layout keeps only the slim entry point there and carries Quick Index,
    Skill Details and Archive as files under _Docs/ (links rebased ../).
    """
    readme = registry / README_NAME
    if not readme.is_file():
        return None
    text = readme.read_text(encoding="utf-8", errors="replace")
    if "## Quick Index" in text:
        return [("", text)]
    parts = [("", text)]
    for name in DOCS_CATALOG_FILES:
        part = registry / DOCS_NAME / name
        if part.is_file():
            parts.append((DOCS_NAME, part.read_text(encoding="utf-8", errors="replace")))
    return parts


def parse_readme(text: str, base: str = "") -> dict[str, Any]:
    header, _, rest = text.partition("## Quick Index")
    quick, _, rest = rest.partition("## Skill Details")
    details_text, _, archive_text = rest.partition("## Archive")
    parsed: dict[str, Any] = {"header": header, "quick": [], "details": [], "archive": []}

    category = None
    for line in quick.splitlines():
        if line.startswith("### "):
            category = line[4:].strip()
        elif match := _README_QI_RE.match(line):
            parsed["quick"].append({"name": match[1], "path": _resolve_readme_target(_readme_path(match[2]), base), "summary": match[3] or "", "category": category})

    category, block = None, None
    for line in details_text.splitlines():
        if line.startswith("#### "):
            block = {"name": line[5:].strip().strip("`"), "category": category, "fields": {}, "base": base}
            parsed["details"].append(block)
        elif line.startswith("### "):
            category, block = line[4:].strip(), None
        elif block is not None and (match := _README_FIELD_RE.match(line)):
            block["fields"][match[1].strip()] = match[2].strip()

    for line in archive_text.splitlines():
        if match := _README_QI_RE.match(line):
            parsed["archive"].append({"name": match[1], "path": _resolve_readme_target(_readme_path(match[2]), base)})
    return parsed


def check_readme(registry: Path) -> list[tuple[str, str, str]]:
    """Return (skill, section, issue) rows where README.md/_Docs disagree with the skills on disk."""
    parts = readme_parts(registry)
    if parts is None:
        return [("-", "readme", f"{README_NAME} not found in {registry}")]
    issues: list[tuple[str, str, str]] = []
    legacy = len(parts) == 1 and "## Quick Index" in parts[0][1]
    if not legacy:
        for name in DOCS_CATALOG_FILES:
            if not (registry / DOCS_NAME / name).is_file():
                issues.append(("-", "readme", f"catalog file missing: {DOCS_NAME}/{name}"))
    header = parts[0][1].partition("## Quick Index")[0]
    if legacy:
        sub = parse_readme(parts[0][1])
    else:
        # _Docs carries the three sections in order; parse them as one flow.
        sub = parse_readme("\n".join(part_text for _, part_text in parts[1:]), DOCS_NAME)
    parsed: dict[str, Any] = {"header": header, "quick": sub["quick"], "details": sub["details"], "archive": sub["archive"]}
    catalog = expected_catalog(registry)

    archive_root = next(
        (registry / name for name in ("_Archive", "Archive") if (registry / name).is_dir()),
        registry / "Archive",
    )
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
        block["path"] = _resolve_readme_target(_readme_path(match[1]), block.get("base", ""))
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
    scan = list(parts)
    docs_dir = registry / DOCS_NAME
    if docs_dir.is_dir():
        catalog_names = set(DOCS_CATALOG_FILES)
        for doc in sorted(docs_dir.glob("*.md")):
            if doc.name not in catalog_names:
                scan.append((DOCS_NAME, doc.read_text(encoding="utf-8", errors="replace")))
    for base, part_text in scan:
        for match in _README_LINK_RE.finditer(part_text):
            target = match[1].strip()
            if not target or target.startswith("#") or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            rel = _resolve_readme_target(_readme_path(target), base)
            if _path_key(rel) not in reported and not (registry / rel).exists():
                issues.append(("-", "links", f"broken link: {DOCS_NAME}/{target}" if base == DOCS_NAME else f"broken link: {target}"))
    return issues


_HINT_INTERFACE_RE = re.compile(r"\b(?:sub-?)?(?:commands?|modes?)\b", re.I)
_HINT_NOISE_RE = re.compile(r"\b(?:than|via|without|needs?|need|step|why|adding|every|each)\b", re.I)
_HINT_ENUM_RE = re.compile(
    r"\b(?:one|two|three|four|five|six|both|several)\s+(?:distinct\s+)?(?:sub-?)?(?:commands?|modes?)\b",
    re.I)
_HINT_MODE_LETTER_RE = re.compile(r"\b[Mm]odes?\s+[A-Z]\b")
_HINT_COLON_LABEL_RE = re.compile(r"^\s*[-*]?\s*\**\s*(?:sub-?)?(?:commands?|modes?)\s*:\**", re.M | re.I)


def command_surface_evidence(skill_md: Path, name: str) -> str:
    """Evidence that a skill presents user-facing commands or modes; '' when none.

    Strong (fires alone): an interface heading naming commands/modes, or use of the
    skill's own slash address with an argument (`/name <thing>`). Weak (two needed):
    enumeration of N commands/modes, Mode A/Mode B letters, bold Commands:/Modes: labels.
    Prose vocabulary ("dark mode", "shell commands", doc-outline headings) never counts:
    the signals are structural - headings, self-slash usage, explicit enumerations.
    """
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    body = text.split("---", 2)[2] if text.count("---") >= 2 else text
    strong: list[str] = []
    weak = 0
    for line in body.splitlines():
        title = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
        if title:
            words = re.findall(r"[\w'’.-]+", title.group(1))
            if (len(words) <= 7
                    and not (re.match(r"^\d+[.)]\s", title.group(1)) and len(words) >= 5)
                    and _HINT_INTERFACE_RE.search(title.group(1))
                    and not _HINT_NOISE_RE.search(title.group(1))):
                strong.append(f'heading "{title.group(1)}"')
    for pat, label, kind in (
        (re.compile(rf"(?:^|[\s|`(])/{''.join(re.escape(c) for c in name)}(?=\s+[^\s`])[^`\n]*`?"),
         "self-slash usage", "strong"),
        (_HINT_ENUM_RE, "command/mode enumeration", "weak"),
        (_HINT_MODE_LETTER_RE, None, "weak"),
        (_HINT_COLON_LABEL_RE, "commands/modes label", "weak"),
    ):
        hits = pat.findall(body)
        if not hits:
            continue
        if kind == "strong":
            strong.append(f"{label} x{len(hits)}")
        elif label is None:
            letters = {h.split()[-1].upper() for h in hits}
            if len(letters) >= 2:
                strong.append(f"mode letters {sorted(letters)}")
        else:
            weak += 1
    if strong:
        return "; ".join(strong[:3])
    return f"enumeration+label x{weak}" if weak >= 2 else ""


def specialized_problem(data: dict[str, Any]) -> str | None:
    if "specialized" not in data or data["specialized"] is None:
        return "missing specialized (one technology, or none)"
    value = data["specialized"]
    items = [item.strip() for item in value.split(",")] if isinstance(value, str) else []
    if (not items or any(not SPECIALIZED_RE.fullmatch(item) or item in SPECIALIZED_REJECTED
                         for item in items)
            or (len(items) > 1 and SPECIALIZED_GENERAL in items)):
        return (f"invalid specialized {value!r} (one lowercase technology such as "
                f"'scss' or 'react-native', or '{SPECIALIZED_GENERAL}')")
    if len(items) > 1:
        return f"specialized lists {len(items)} technologies; prefer one per skill"
    canonical = SPECIALIZED_ALIASES.get(items[0])
    if canonical:
        return f"specialized {items[0]!r} is an alias; use {canonical!r}"
    return None


def skill_size(path: Path) -> tuple[int, bool]:
    """SKILL.md line count and whether the skill is nothing but that file."""
    try:
        files = list(iter_files(path))
    except OSError:
        return 0, False
    solo = len(files) == 1 and files[0].name == "SKILL.md"
    try:
        text = (path / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0, solo
    return len(text.splitlines()), solo


def lint_acceptances(data: dict[str, Any] | None) -> tuple[dict[str, str], list[str]]:
    """Parse `lint-accept` (rule id -> reason). Returns (accepted, problems)."""
    raw = (data or {}).get("lint-accept")
    if raw is None:
        return {}, []
    if not isinstance(raw, dict):
        return {}, ["lint-accept must be a mapping of rule id to reason"]
    accepted: dict[str, str] = {}
    problems: list[str] = []
    for rule, reason in raw.items():
        if rule not in LINT_RULE_IDS:
            problems.append(f"lint-accept names unknown rule '{rule}'")
        elif not isinstance(reason, str) or not reason.strip():
            problems.append(f"lint-accept for '{rule}' needs a non-empty reason")
        else:
            accepted[rule] = reason.strip()
    return accepted, problems


def cmd_lint(args: argparse.Namespace, registry: Path, jobs: int, issues: Sequence[SyncIssue]) -> int:
    limit = args.max_description
    if limit <= 0:
        raise ManagerError("--max-description must be a positive number")
    extra_roots = [resolve_into(value) for value in (args.into or [])]
    remote_roots: list[tuple[Path, str]] = []
    if getattr(args, "remote", False):
        for info in remotes_all().values():
            root = remote_root(info)
            if root is not None:
                remote_roots.append((root, f"remote:{info['name']}"))
            else:
                display_warn(f"remote '{info['name']}' is not fetched yet; skipped "
                             "(run `manager.py remote --update`)")
    records = list(load_records(registry).values())
    skills = lint_skill_dirs(registry, extra_roots, records, remote_roots)
    if not skills:
        display_warn(f"no SKILL.md files found in {registry} or the configured skill folders")

    frontmatters = map_concurrent(
        lambda item: read_frontmatter(item[1] / "SKILL.md"), skills, jobs
    )
    sizes = map_concurrent(lambda item: skill_size(item[1]), skills, jobs)
    warnings: list[tuple[str, str, Path, int | None, str]] = []
    accepted: list[tuple[str, str, Path, str, str, str]] = []
    checked_rows: list[list[str]] = []
    registry_names: dict[str, Path] = {}
    type_counts: Counter[str] = Counter()
    tracked_paths = set(registry_skills(registry).values())
    total_checked = 0
    if yaml is None:
        warnings.append(("-", "environment", registry, None, "YAML validation unavailable; install PyYAML for full validation"))
    for (name, path, label), (data, error), (lines, solo) in zip(skills, frontmatters, sizes):
        total_checked += 1
        structure = inspect_directory(path)
        skill_type = SKILL_TYPES[structure.kind]
        type_counts[structure.kind] += 1
        accept, accept_problems = lint_acceptances(data)

        def emit(rule: str, reason: str, length: int | None = None) -> None:
            if rule in accept:
                accepted.append((name, label, path, reason, rule, accept[rule]))
            else:
                warnings.append((name, label, path, length, reason))

        for problem in accept_problems:
            warnings.append((name, label, path, None, problem))
        for issue in structure.issues:
            emit("mixed-composition", issue)
        if data is not None and not args.no_version and path not in tracked_paths:
            version = _norm_version(data.get("version"))
            if version is None or SEMVER_RE.fullmatch(version) is None:
                emit("version", "missing or invalid version (expected semver X.Y.Z)")
        if data is None:
            emit("frontmatter", error or "missing frontmatter")
            checked_rows.append([name, skill_type, label, "missing", "missing", str(path)])
            continue
        if label == "registry":
            problem = specialized_problem(data)
            if problem:
                emit("specialized", problem)
            if not solo and lines >= SKILL_LENGTH_LIMIT:
                emit("skill-length",
                     f"SKILL.md has {lines} lines (limit {SKILL_LENGTH_LIMIT}); "
                     "split depth into references/ or modules")
            if not str(data.get("argument-hint") or "").strip():
                evidence = command_surface_evidence(
                    path / "SKILL.md", str(data.get("name") or path.name))
                if evidence:
                    emit("argument-hint",
                         f"presents commands/modes ({evidence}); declare argument-hint")
        skill_name = data.get("name")
        if not isinstance(skill_name, str) or not re.fullmatch(r"[a-z0-9-]+", skill_name):
            emit("name", "missing or invalid name (use lowercase letters, digits and hyphens)")
        else:
            if skill_name != path.name:
                emit("name-mismatch", f"name '{skill_name}' does not match folder '{path.name}'")
            if label == "registry":
                previous = registry_names.setdefault(skill_name, path)
                if previous != path:
                    emit("duplicate-name", f"duplicate name '{skill_name}' also at {previous}")
        description = data.get("description")
        if not isinstance(description, str) or not description.strip():
            emit("description", "missing description")
            checked_rows.append([name, skill_type, label, "missing", "missing", str(path)])
            continue
        if "\n" in description.strip() or "\r" in description.strip():
            emit("description-multiline", "description must be a single-line string")
        length = len(description)
        state = "over" if length > limit else "ok"
        checked_rows.append([name, skill_type, label, str(length), state, str(path)])
        if length > limit:
            emit("description-length", "over limit", length)

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
    if _DISPLAY.verbose and accepted:
        display_table(
            ["Skill", "Location", "Rule", "Finding", "Accepted because"],
            [[n, lab, rule, reason, why] for n, lab, _p, reason, rule, why in accepted],
            title=f"accepted findings ({len(accepted)})",
            always=True,
        )
    if _DISPLAY.verbose and checked_rows:
        display_table(
            ["Skill", "Type", "Location", "Chars", "State", "Path"],
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
            1 for agent in agent_names() if agent_skill_dir(agent).is_dir()
        ))),
        ("SKILL.md files checked", str(total_checked)),
        *[(title, str(type_counts[kind])) for kind, title in SKILL_TYPES.items()],
        ("Hard copies tracked", str(hard_copies)),
        ("Skill warnings", str(len(warnings))),
        ("Accepted findings", str(len(accepted))),
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
    roots: list[tuple[str, Path]] = [("", registry)]
    if getattr(args, "remote", False):
        for info in remotes_all().values():
            root = remote_root(info)
            if root is None:
                display_warn(f"remote '{info['name']}' is not fetched yet; skipped "
                             "(run `manager.py remote --update`)")
                continue
            roots.append((f"remote:{info['name']}/", root))

    wanted = set(args.skills)
    missing = set(wanted)
    rows: list[dict[str, Any]] = []
    counted_files: set[Path] = set()
    heads: list[tuple[str, str | None]] = []
    for prefix, base in roots:
        inventory = walk_skills(base, prune=False)
        if prefix and has_skill(base):
            inventory.insert(0, base)
        paths = [p for p in inventory if p.name in wanted] if wanted else list(inventory)
        for path in paths:
            missing.discard(path.name)
        status_map = git_status_map(base)
        head = git_head(base)
        heads.append((prefix.rstrip("/") or "registry", head))
        frontmatters = map_concurrent(lambda path: read_frontmatter(path / "SKILL.md"), paths, jobs)
        snaps = map_concurrent(skill_snapshot, paths, jobs)
        for path, (data, _err), snap in zip(paths, frontmatters, snaps):
            ver, desc_len = "-", 0
            if isinstance(data, dict):
                v = data.get("version")
                ver = str(v) if v is not None else "-"
                d = data.get("description")
                desc_len = len(d) if isinstance(d, str) else 0
            structure = inspect_directory(path)
            parent = skill_parent(path, inventory)
            rel = path.relative_to(base).as_posix()
            counted_files.update(path / name for name in snap["files"])
            row = {
                "name": path.name, "type": structure.kind,
                "parent": parent.relative_to(base).as_posix() if parent else None,
                "children": [child.relative_to(path).as_posix() for child in structure.children],
                "modules": [module.relative_to(path).as_posix() for module in structure.modules],
                "issues": list(structure.issues),
                "version": ver, "files": snap["file_count"], "desc": desc_len,
                "solo": snap["file_count"] == 1 and "SKILL.md" in snap["files"],
                "git": skill_git_state(rel, status_map), "path": prefix + rel,
            }
            if _DISPLAY.verbose:
                row["last_commit"] = git_last_commit(base, rel) or "-"
            rows.append(row)
    if wanted:
        for name in sorted(missing):
            display_warn(f"no {'registry or remote ' if len(roots) > 1 else 'registry '}skill named '{name}'")
    head = heads[0][1] if heads else None
    sort_key = args.sort
    rows.sort(key=lambda r: r[sort_key] if sort_key != "name" else r["name"].lower(),
              reverse=args.reverse)
    type_counts = {kind: sum(row["type"] == kind for row in rows) for kind in SKILL_TYPES}
    if args.json:
        print(json.dumps({"registry": str(registry), "head": head, "skills": rows,
                          "types": type_counts, "total_files": len(counted_files),
                          "remote_heads": {label: h for label, h in heads[1:]}}, indent=2))
        return 0
    headers = ["Skill", "Type", "Parent", "Version", "Files", "SKILL.md only", "Desc chars", "Git", "Path"]
    table_rows = [[r["name"], SKILL_TYPES[r["type"]], r["parent"] or "-", r["version"],
                   str(r["files"]), "yes" if r["solo"] else "-", str(r["desc"]), r["git"], r["path"]]
                  for r in rows]
    if _DISPLAY.verbose:
        headers.append("Last commit")
        for r, tr in zip(rows, table_rows):
            tr.append(r.get("last_commit", "-"))
    display_table(headers, table_rows, title=f"skill report ({len(rows)})", always=True)
    display_table(["Skill", "Issue"], [[r["path"], issue] for r in rows for issue in r["issues"]],
                  title="composition warnings", always=True)
    avg_desc = round(sum(r["desc"] for r in rows) / len(rows)) if rows else 0
    summary = [
        ("Skills", str(len(rows))),
        *[(title, str(type_counts[kind])) for kind, title in SKILL_TYPES.items()],
        ("Total files (unique)", str(len(counted_files))),
        ("Solo SKILL.md skills", str(sum(1 for r in rows if r["solo"]))),
        ("Avg description chars", str(avg_desc)),
        ("Sorted by", f"{sort_key}{' (desc)' if args.reverse else ' (asc)'}"),
        ("Git HEAD", head or "-"),
        *[("Git HEAD " + label, h or "-") for label, h in heads[1:]],
    ]
    display_kv(summary, title="report summary", always=True)
    return 0


def cmd_find(args: argparse.Namespace, registry: Path, jobs: int) -> int:
    removed = prune_installs(registry)
    if removed:
        display_info(f"[installs] pruned {len(removed)} stale --into record(s)")
    locked = load_lockfile(registry).get("locked", {})
    locations: list[tuple[str, Path]] = []
    structures: dict[Path, SkillStructure] = {}

    def structure(path: Path) -> SkillStructure:
        if path not in structures:
            structures[path] = inspect_directory(path)
        return structures[path]

    def add_tree(label: str, root: Path, include_root: bool = True) -> None:
        paths = walk_skills(root, prune=False)
        if include_root:
            paths.insert(0, root)
        for path in paths:
            locations.append((label, path))
            for module in structure(path).modules:
                locations.append((label, module))
            for parent in path.parents:
                if parent == root or not is_under(parent, root):
                    break
                locations.append((label, parent))

    add_tree("registry", registry, include_root=False)
    for agent in agent_names():
        directory = agent_skill_dir(agent)
        if directory.is_dir():
            for entry in sorted(directory.iterdir()):
                if entry.is_dir() or is_link_like(entry):
                    add_tree(f"agent:{agent}", entry)
    for entry in load_installs(registry).get("into", {}).values():
        add_tree("into (recorded)", Path(entry["target"]))
    if getattr(args, "remote", False):
        for info in remotes_all().values():
            root = remote_root(info)
            if root is None:
                display_warn(f"remote '{info['name']}' is not fetched yet; skipped "
                             "(run `manager.py remote --update`)")
                continue
            add_tree(f"remote:{info['name']}", root)

    found_any = False
    for item in dict.fromkeys(args.skills):
        candidate = Path(os.path.abspath(Path(item).expanduser()))
        explicit = candidate.is_dir() or is_link_like(candidate)
        name = candidate.name if explicit else item
        matches = [(label, path) for label, path in locations if path.name == name]
        if explicit:
            matches.append(("path argument", candidate))
        rows: list[list[str]] = []
        seen: set[str] = set()
        for label, path in matches:
            key = _key(path)
            if key in seen:
                continue
            seen.add(key)
            info = structure(path)
            kind = SKILL_TYPES.get(info.kind, info.kind)
            notes: list[str] = []
            parent = skill_parent(path, (p for p in path.parents if has_skill(p)))
            if info.kind in SKILL_TYPES:
                if parent:
                    notes.append(f"sub-skill of {parent.name}")
                if info.children:
                    notes.append(f"{len(info.children)} independent sub-skill(s)")
                if info.modules:
                    notes.append(f"{len(info.modules)} internal module(s), not independent")
            elif info.kind == "group":
                notes.append(f"not a skill; holds {len(info.children)} skill(s)")
            elif info.kind == "plain":
                if parent and path in structure(parent).modules:
                    notes.append(f"internal module of {parent.name}; not an independent skill")
                else:
                    notes.append("no SKILL.md; not a skill")
            else:
                notes.append("BROKEN link; no live skill verified")
            if is_link_like(path):
                link_kind = "symlink" if path.is_symlink() else "junction"
                notes.append(f"{link_kind} -> {os.path.realpath(path)}")
            elif label.startswith("agent:") and info.kind in SKILL_TYPES:
                notes.append("hard copy")
            notes.extend(info.issues)
            shown = path.relative_to(registry).as_posix() if is_under(path, registry) else str(path)
            rows.append([label, kind, shown, "; ".join(notes)])
        if name in locked:
            rows.append(["database", "lock record", ", ".join(sorted(locked[name])),
                         "record only; not proof of a live skill"])
        if rows:
            found_any = True
            display_table(["Where", "Type", "Path", "Note"], rows,
                          title=f"find: {item} ({len(rows)} match(es))", always=True)
        else:
            display_warn(f"find: '{item}' not in the registry, agent folders, or recorded --into installs")
    return 0 if found_any else 1


def scan_crossreferences(registry: Path, skills: Sequence[Path]) -> dict[str, Any]:
    index: dict[str, list[Path]] = {}
    for skill in skills:
        index.setdefault(skill.name.casefold(), []).append(skill)
    skill_set = set(skills)
    owners: dict[Path, Path | None] = {}
    edges: dict[tuple[Path, Path], dict[str, Any]] = {}
    ambiguous: dict[tuple[Path, str], dict[str, Any]] = {}
    errors: list[dict[str, str]] = []
    files_scanned = characters_scanned = 0

    def walk_error(error: OSError) -> None:
        errors.append({"file": str(error.filename), "error": str(error)})

    for dirpath, dirnames, filenames in os.walk(registry, onerror=walk_error):
        directory = Path(dirpath)
        dirnames[:] = sorted(name for name in dirnames
                             if name not in SKIP_NAMES and not name.startswith(".")
                             and not is_link_like(directory / name))
        owner = directory if directory in skill_set else owners.get(directory.parent)
        owners[directory] = owner
        if owner is None:
            continue
        source = owner.relative_to(registry).as_posix()
        owner_name = owner.name.casefold()
        for filename in sorted(filenames):
            path = directory / filename
            if filename.startswith(".") or path.suffix.lower() not in REFERENCE_SUFFIXES or is_link_like(path):
                continue
            relative = path.relative_to(registry).as_posix()
            try:
                with path.open(encoding="utf-8-sig") as stream:
                    for line_number, line in enumerate(stream, 1):
                        characters_scanned += len(line)
                        seen: set[str] = set()
                        for match in REFERENCE_TOKEN_RE.finditer(line):
                            name = match.group().casefold()
                            if name in seen or name == owner_name:
                                continue
                            seen.add(name)
                            targets = index.get(name)
                            if not targets:
                                continue
                            start = max(0, match.start() - 80)
                            end = max(start + 240, match.end())
                            evidence = {"file": relative, "line": line_number,
                                        "text": line[start:end].strip()}
                            if len(targets) > 1:
                                key = (owner, name)
                                if key not in ambiguous:
                                    ambiguous[key] = {
                                        "source": source, "name": name,
                                        "candidates": [p.relative_to(registry).as_posix() for p in targets],
                                        "evidence": [],
                                    }
                                record = ambiguous[key]
                            else:
                                target = targets[0]
                                edge_key = (owner, target)
                                if edge_key not in edges:
                                    edges[edge_key] = {
                                        "from": owner.name, "to": target.name, "source": source,
                                        "target": target.relative_to(registry).as_posix(), "evidence": [],
                                    }
                                record = edges[edge_key]
                            record["evidence"].append(evidence)
                files_scanned += 1
            except (OSError, UnicodeError) as error:
                errors.append({"file": relative, "error": str(error)})

    for (source, target), edge in edges.items():
        edge["mutual"] = (target, source) in edges
        edge["count"] = len(edge["evidence"])
    return {
        "edges": sorted(edges.values(), key=lambda edge: (edge["source"], edge["target"])),
        "ambiguous": sorted(ambiguous.values(), key=lambda item: (item["source"], item["name"])),
        "errors": errors,
        "stats": {"skills": len(skills), "files_scanned": files_scanned,
                  "characters_scanned": characters_scanned, "edges": len(edges)},
    }


def cmd_crossreference(args: argparse.Namespace, registry: Path) -> int:
    result = scan_crossreferences(registry, walk_skills(registry, prune=False))
    result["registry"] = str(registry)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        rows = []
        for edge in result["edges"]:
            first = edge["evidence"][0]
            rows.append([edge["from"], edge["to"], str(edge["count"]),
                         "yes" if edge["mutual"] else "no", f"{first['file']}:{first['line']}"])
        display_table(["From", "To", "Mention lines", "Mutual", "First evidence"], rows,
                      title="skill crossreferences (textual mentions, not proven dependencies)", always=True)
        if _DISPLAY.verbose:
            display_table(["From", "To", "Evidence", "Text"],
                          [[edge["from"], edge["to"], f"{item['file']}:{item['line']}", item["text"]]
                           for edge in result["edges"] for item in edge["evidence"]],
                          title="reference evidence", always=True)
        display_table(["Source", "Ambiguous name", "Candidates"],
                      [[item["source"], item["name"], ", ".join(item["candidates"])]
                       for item in result["ambiguous"]], title="ambiguous references", always=True)
        display_table(["File", "Read error"],
                      [[item["file"], item["error"]] for item in result["errors"]],
                      title="incomplete scan", always=True)
        display_kv([(key.replace("_", " "), value) for key, value in result["stats"].items()],
                   title="crossreference summary", always=True)
    return 1 if result["errors"] or result["ambiguous"] else 0


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
        description="Deploy skills and agent instructions, lint and classify skills, locate installs, and discover crossreferences.",
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
            "  python manager.py crossreference\n"
            "  python manager.py crossreference --json\n"
            "  python manager.py remote --add https://github.com/acme/skills -p skills/\n"
            "  python manager.py skill --remote https://github.com/acme/skills foo bar\n"
            "  python manager.py remote --update\n"
            "  python manager.py lint --remote\n"
            "  python manager.py interactive\n"
            "  python manager.py interactive --into ./my-project --hard-copy\n"
            "  python manager.py viber --into ./my-project --hard-copy\n"
        ),
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", metavar="{skill,agent,agents,claim,remote,interactive,lint,viber,report,find,crossreference}")

    skill = subparsers.add_parser(
        "skill",
        help="link, copy, refresh, or remove skills (default command)",
        description="Link or copy named skills into global agent folders or a project folder; "
                    "--remove uninstalls them from wherever they are deployed "
                    "(symlinks, junctions, tracked hard copies).",
    )
    add_common(skill)
    add_deploy_flags(skill)
    add_mode_flag(skill)
    skill.add_argument("skills", nargs="*", help="skill name(s) or a path to a skill directory")
    skill.add_argument("-a", "--all", action="store_true", help="every skill in the registry")
    skill.add_argument("-A", "--agents", default="all", help="comma-separated agents or 'all'")
    skill.add_argument("-l", "--lock", action="store_true", help="record installs in the manager database")
    skill.add_argument("-R", "--refresh", action="store_true", help="repair existing and locked entries")
    skill.add_argument("-U", "--remove", action="store_true",
                       help="uninstall named skills from agent folders (or --into): links and "
                            "junctions are removed without touching sources, tracked hard copies "
                            "are removed (backed up first); unmanaged directories need --force; "
                            "registry sources are always protected")
    skill.add_argument("-i", "--into", default=None, help="project folder to install into instead of agent folders")
    skill.add_argument("-c", "--hard-copy", action="store_true", help="copy instead of link and track sync")
    skill.add_argument("-B", "--no-backup", action="store_true", help="skip the backup before --refresh or --remove of hard copies")
    skill.add_argument("-L", "--list", action="store_true", help="list registry skills and exit")
    skill.add_argument("-x", "--remote", metavar="URL", default=None,
                       help="take the named skills from a remote git repo instead of the "
                            "registry: registers the URL if new, fetches it, deploys from the "
                            "cache (links point into the cache; keep fresh with `remote --update`)")

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
    viber.set_defaults(skills=[], all=False, refresh=False, no_backup=False, remove=False, remote=None)

    agent = subparsers.add_parser(
        "agent",
        help="deploy AGENTS.md to agent configurations",
        description=f"Link or copy the registry's {AGENT_SOURCE.as_posix()} into each selected agent's global instruction file.",
    )
    add_common(agent)
    add_deploy_flags(agent)
    add_mode_flag(agent)
    agent.add_argument("-A", "--agents", default="all", help="comma-separated agents or 'all'")
    agent.add_argument("-c", "--hard-copy", action="store_true", help="copy instead of link and track sync")

    agents = subparsers.add_parser(
        "agents",
        help="manage the agents table: where each code agent lives",
        description="Code-agent locations are read from the agents table, seeded once from the "
                    "built-in defaults (qoder, junie, gemini, opencode, claude). --set registers or "
                    "updates a row; --remove unregisters without touching deployments on disk. "
                    "Every --agents use in skill/viber/agent reads this table.",
    )
    add_common(agents)
    agents.add_argument("-s", "--set", metavar="NAME", default=None,
                        help="register a new agent or update this one")
    agents.add_argument("-d", "--skill-dir", default=None, metavar="PATH",
                        help="skills folder for --set (relative paths resolve against the current folder)")
    agents.add_argument("-m", "--md-path", action="append", default=None, metavar="PATH",
                        help="instruction file for --set, repeatable; omit to keep existing ones on update")
    agents.add_argument("-x", "--remove", metavar="NAME", default=None,
                        help="unregister this agent; a seeded default stays removed (tombstone row)")
    agents.add_argument("-O", "--override", action="store_true",
                        help="replace differing existing values or share a skill dir despite the conflict")
    agents.add_argument("-L", "--list", action="store_true",
                        help="show the table explicitly (also the default with no action flag)")
    agents.add_argument("-I", "--inventory", action="store_true",
                        help="list the skills installed in each agent folder (name, kind, resolved source)")
    agents.add_argument("--json", action="store_true", help="print the table as JSON")

    claim = subparsers.add_parser(
        "claim",
        help="claim one agent's skill set into another: claim X into Y",
        description="Make Y end with X's skill set. Default mode is OVERRIDE: shared "
                    "names are replaced (unmanaged folders replaced are backed up first), "
                    "missing are added, and Y's extras are removed when manager-owned "
                    "(unmanaged extras are protected unless --force). --append adds only "
                    "what Y lacks, deduped by name, and never touches existing entries. "
                    "X and Y are agent names from the agents table or direct folder paths. "
                    "Deployment kind follows the source entry: links link, copies copy.",
    )
    add_common(claim)
    claim.add_argument("from_agent", metavar="FROM", help="source agent name or skills folder")
    claim.add_argument("into_agent", metavar="TO", help="destination agent name or skills folder")
    claim.add_argument("-a", "--append", action="store_true",
                       help="only add what the destination lacks; existing entries are kept untouched")
    claim.add_argument("-f", "--force", action="store_true",
                       help="override mode also removes UNMANAGED extra folders (backed up first)")
    claim.add_argument("-d", "--dry-run", action="store_true",
                       help="show what would happen, change nothing")
    claim.add_argument("-B", "--no-backup", action="store_true",
                       help="skip the automatic backup zips before replacing/removing real folders")

    remote = subparsers.add_parser(
        "remote",
        help="register and refresh git-backed remote skill sources",
        description="Remotes are git repositories outside this registry whose skills you can "
                    "install with `skill --remote URL`. Manager clones them shallow into its "
                    "cache (next to the database) and owns those copies entirely: a refresh "
                    "re-fetches and hard-resets; --remove deletes the cache with it. --add "
                    "registers + fetches once; --update refreshes one, several or all; with no "
                    "action flag this lists the remotes table and fetched skill counts.",
    )
    add_common(remote)
    remote.add_argument("-L", "--list", action="store_true",
                        help="show the remotes table explicitly (default with no action flag)")
    remote.add_argument("-a", "--add", metavar="URL", default=None,
                        help="register a remote git URL (https://, ssh://, git@host:path or a "
                             "local repo path for tests) and fetch it once")
    remote.add_argument("-n", "--name", default=None,
                        help="name for --add (default: derived from the URL/repo or --path slug)")
    remote.add_argument("-p", "--path", default="", metavar="SUBPATH",
                        help="path inside the repo holding the skill(s), e.g. skills/")
    remote.add_argument("--ref", default="",
                        help="branch or tag to track instead of the repo's default")
    remote.add_argument("-f", "--force", action="store_true",
                        help="--add: re-point an existing name at a different URL")
    remote.add_argument("-u", "--update", action="store_true",
                        help="re-fetch; named remotes follow, all remotes without")
    remote.add_argument("-x", "--remove", metavar="NAME", default=None,
                        help="unregister a remote and delete its manager-owned cache; agent "
                             "links left pointing into it are reported, not silently removed")
    remote.add_argument("names", nargs="*", help="remote name(s) for --update")
    remote.add_argument("--json", action="store_true", help="list mode: JSON instead of a table")

    interactive = subparsers.add_parser(
        "interactive",
        help="arrow-key checklist: pick which skills stay installed, confirm with [y/N]",
        description="Multi-select over every registry skill, pre-checked from what the target "
                    "folders currently hold. Space toggles, typing filters the list, ctrl-a "
                    "selects everything, ctrl-i inverts, enter plans: newly checked get "
                    "installed, unchecked-but-installed get uninstalled, everything else is "
                    "left alone. A plan table follows and NOTHING changes until you confirm "
                    "'Apply changes?'. --no-tui (or a piped terminal) falls back to a numbered "
                    "prompt. Uses questionary when it is installed for the coloured picker. "
                    "Skills installed that are not in the registry (hand-made, remote-only) "
                    "are never touched.",
    )
    add_common(interactive)
    add_deploy_flags(interactive)
    add_mode_flag(interactive)
    interactive.add_argument("-A", "--agents", default="all", help="comma-separated agents or 'all'")
    interactive.add_argument("-i", "--into", default=None,
                             help="project folder to reconcile instead of agent folders")
    interactive.add_argument("-c", "--hard-copy", action="store_true",
                             help="installs copy instead of linking")
    interactive.add_argument("-l", "--lock", action="store_true",
                             help="record installs in the manager database")
    interactive.add_argument("-B", "--no-backup", action="store_true",
                             help="skip the backup zips before uninstalling hard copies")
    interactive.add_argument("-T", "--no-tui", action="store_true",
                             help="numbered prompt instead of the arrow-key checklist")

    lint = subparsers.add_parser(
        "lint",
        help="validate skill metadata and installation synchronization",
        description="Check all independent SKILL.md metadata, classify Skill / Meta-Skill / "
                    "Battery-Skill, flag mixed independent/internal composition, and audit installs. "
                    "Support folders and internal modules are not independently linted skills.",
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
        help="exit 1 on metadata, composition, version, sync or README findings",
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
    lint.add_argument(
        "-x", "--remote", action="store_true",
        help="also lint the skills inside every fetched remote checkout",
    )

    report = subparsers.add_parser(
        "report",
        help="report skill types, parents, file counts, description lengths, versions and git state",
        description="Report every independent skill, including meta children. Meta-Skill has "
                    "nested SKILL.md entrypoints; Battery-Skill has Markdown-backed internal "
                    "module folders without their own SKILL.md; Skill has neither. Standard "
                    "support folders (references, assets, scripts, etc.) do not make a battery. "
                    "Mixed composition is flagged. Per-row file counts include descendants; "
                    "the summary counts unique files. Sortable; optional JSON output.",
    )
    add_common(report)
    report.add_argument("skills", nargs="*", help="optional skill names to filter the report")
    report.add_argument(
        "--sort", choices=["name", "type", "files", "desc", "version"], default="name",
        help="sort column (default: name)",
    )
    report.add_argument("--reverse", action="store_true", help="sort descending")
    report.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    report.add_argument("-x", "--remote", action="store_true",
                        help="also report skills from every fetched remote checkout "
                             "(paths prefixed remote:<name>/)")

    find = subparsers.add_parser(
        "find",
        help="locate a skill in the registry, agent folders, or recorded --into installs",
        description="Find skills, groups and internal modules in this registry, global agent "
                    "folders and recorded --into installs, with structural skill types. "
                    "Lock records are shown separately, not as live skills. Exit 0 when any "
                    "name or path resolves, 1 when none does. No skill files are changed; "
                    "stale --into records are pruned from the database.",
    )
    add_common(find)
    find.add_argument(
        "skills", nargs="+",
        help="skill/module/group name(s), or directory path(s) to classify",
    )
    find.add_argument("-x", "--remote", action="store_true",
                      help="also search fetched remote checkouts")

    crossreference = subparsers.add_parser(
        "crossreference",
        help="discover directed mentions among all registry skills with file/line evidence",
        description="Compare every active registry skill; takes no skill names. Scan "
                    ".md/.mdx/.txt/.rst documents once using a skill-name hash index. "
                    "Matches whole name tokens, case-insensitively, including slash commands "
                    "and Markdown links. Shows mentions, not proven dependencies. Meta "
                    "children own their files; battery modules belong to their parent. "
                    "Archives, resources outside skills, hidden files and links are skipped. "
                    "No database writes. Exit 1 on ambiguous targets or unreadable content; "
                    "otherwise 0, including an empty graph.",
    )
    add_common(crossreference)
    crossreference.add_argument("--json", action="store_true", help="emit all evidence and scan statistics as JSON")

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
    if args.remote:
        labels.append("-x/--remote")
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
    rows = [
        ("Registry", str(registry)),
        ("Destination", destination),
        ("Mode", mode),
        ("Skills", action),
    ]
    if getattr(args, "remote", None):
        rows.insert(1, ("Remote", args.remote))
    return rows


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
    if args.remote:
        labels.append("-x/--remote")
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
    if args.remote:
        labels.append("-x/--remote")
    if args.quiet:
        labels.append("-q/--quiet")
    if args.verbose:
        labels.append("-v/--verbose")
    if args.no_color:
        labels.append("-C/--no-color")
    return labels


def parse_cli_args(parser: argparse.ArgumentParser, argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments with helpful diagnostic hints for common shell mistakes."""
    try:
        return parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code != 0:
            try:
                parsed, unknown = parser.parse_known_args(argv)
                hints: list[str] = []
                # Check for unquoted paths with spaces (e.g. --into or -i)
                into_val = getattr(parsed, "into", None)
                if into_val and isinstance(into_val, str) and unknown:
                    candidate = into_val
                    for tok in unknown:
                        candidate += " " + tok
                        if Path(candidate).expanduser().exists():
                            hints.append(
                                f"path argument '{into_val}' contains unquoted spaces and was split by your shell.\n"
                                f"  Wrap the target path in quotes: --into \"{candidate}\""
                            )
                            break
                if any(tok == "manager.py" or tok.endswith("manager.py") for tok in unknown):
                    hints.append("manager.py appeared inside the arguments, likely due to a duplicate pasted command.")
                if hints:
                    sys.stderr.write("\n[hint] " + "\n[hint] ".join(hints) + "\n\n")
            except Exception:
                pass
        raise


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
        args = parse_cli_args(parser, [command] + rest)
    except SystemExit as exc:
        return int(exc.code or 0)

    configure_display(
        quiet=args.quiet or (command in {"report", "crossreference"} and args.json),
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
        if command == "agents":
            return cmd_agents(args)
        if command == "claim":
            return cmd_claim(args, registry)
        if command == "remote":
            return cmd_remote(args)
        if command == "interactive":
            return cmd_interactive(args, registry, jobs, invoked)
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
                    ("Source", str(registry / AGENT_SOURCE)),
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
                        ("-x/--remote", args.remote),
                        ("-q/--quiet", args.quiet),
                        ("-v/--verbose", args.verbose),
                        ("-C/--no-color", args.no_color),
                    ] if active
                ],
                implicit=implicit,
            )
            return cmd_find(args, registry, jobs)
        elif command == "crossreference":
            return cmd_crossreference(args, registry)
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

        issues = audit_all(registry, agent_names(), jobs)
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



