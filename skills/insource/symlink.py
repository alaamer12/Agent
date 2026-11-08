#!/usr/bin/env python3
"""Link skills from this registry into per-agent global skill directories.

Default mode links the skills you name into every supported agent:

    python symlink.py avatar
    python symlink.py avatar mine
    python symlink.py avatar --agents opencode,gemini
    python symlink.py avatar --agents all --force

Refresh mode rewrites only the entries that already exist in an agent
directory and whose names exist in this registry. Anything the registry does
not know about is left untouched, and no new skills are added:

    python symlink.py --refresh --agents qoder,gemini

Supported agents and their global skill directories (Windows home):
    qoder     ~/.qoder/skills
    junie     ~/.junie/skills
    gemini    ~/.gemini/config/skills
    opencode  ~/.config/opencode/skills
    claude    ~/.claude/skills
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
import zipfile
from datetime import datetime
from pathlib import Path

HOME = Path.home()

AGENTS: dict[str, Path] = {
    "qoder": HOME / ".qoder" / "skills",
    "junie": HOME / ".junie" / "skills",
    "gemini": HOME / ".gemini" / "config" / "skills",
    "opencode": HOME / ".config" / "opencode" / "skills",
    "claude": HOME / ".claude" / "skills",
}

DEFAULT_AGENTS = list(AGENTS)

# Historical copy-based agents. Their real directories are old references and
# may be replaced without --force. All other agents keep real directories
# unless --force is passed.
MIGRATION_AGENTS = {"qoder", "gemini"}

ALIASES = {
    "claude-code": "claude",
    "claudecode": "claude",
    "gemini-cli": "gemini",
    "geminicli": "gemini",
    "open-code": "opencode",
}

SKIP_NAMES = {"Archive", "__pycache__", "node_modules", ".git", ".venv", "venv"}

REGISTRY = Path(__file__).resolve().parent


# --------------------------------------------------------------------------
# filesystem helpers
# --------------------------------------------------------------------------

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


def remove_entry(path: Path) -> str:
    """Remove a link, junction or real directory. Returns the kind removed."""
    if path.is_symlink():
        path.unlink()
        return "symlink"
    if is_reparse(path):
        # A junction/directory reparse point: os.rmdir removes the link only.
        os.rmdir(path)
        return "junction"
    if path.is_dir():
        shutil.rmtree(path)
        return "directory"
    path.unlink()
    return "file"


def make_link(source: Path, dest: Path) -> str:
    """Create a directory symlink, falling back to a junction if needed."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(source, dest, target_is_directory=True)
        return "symlink"
    except OSError as exc:
        fallback = _make_junction(source, dest)
        if fallback:
            return "junction"
        raise exc


def _make_junction(source: Path, dest: Path) -> bool:
    if os.name != "nt":
        return False
    import subprocess

    try:
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dest), str(source)],
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    return result.returncode == 0 and dest.exists()


def has_skill(path: Path) -> bool:
    try:
        return (path / "SKILL.md").is_file()
    except OSError:
        return False


# --------------------------------------------------------------------------
# registry discovery
# --------------------------------------------------------------------------

def walk_skills(root: Path, prune: bool = True) -> list[Path]:
    """Return directories containing SKILL.md.

    When prune is true, a skill directory is not searched further, matching the
    agent convention that one SKILL.md directory is one skill.
    """
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        rel_parts = current.relative_to(root).parts
        if any(part in SKIP_NAMES or part.startswith(".") for part in rel_parts):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_NAMES and not d.startswith(".")]
        # Never follow links while walking the registry.
        dirnames[:] = [d for d in dirnames if not is_link_like(current / d)]
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

    matches = [p for p in walk_skills(cwd, prune=False) if p.name == name]
    if len(matches) == 1:
        return matches[0].resolve()
    if len(matches) > 1:
        listing = "\n  ".join(str(p) for p in matches)
        raise SystemExit(f"error: '{name}' is ambiguous under {cwd}:\n  {listing}")

    fallback = registry_skills(registry_root).get(name)
    if fallback is not None:
        return fallback.resolve()

    raise SystemExit(
        f"error: no skill named '{name}' found in {cwd} or the registry {registry_root}"
    )


# --------------------------------------------------------------------------
# agent selection
# --------------------------------------------------------------------------

def parse_agents(raw: str) -> list[str]:
    if not raw:
        return DEFAULT_AGENTS
    requested = [part.strip().lower() for part in raw.replace(",", " ").split() if part.strip()]
    if not requested or "all" in requested:
        return DEFAULT_AGENTS
    result: list[str] = []
    unknown: list[str] = []
    for item in requested:
        name = ALIASES.get(item, item)
        if name not in AGENTS:
            unknown.append(item)
        elif name not in result:
            result.append(name)
    if unknown:
        raise SystemExit(
            f"error: unknown agent(s): {', '.join(unknown)}. "
            f"Available: {', '.join(DEFAULT_AGENTS)}"
        )
    return result


# --------------------------------------------------------------------------
# backup
# --------------------------------------------------------------------------

def backup_dirs(dirs: list[Path], label: str = "skill-sync-backup") -> Path | None:
    dirs = [d for d in dirs if d.exists()]
    if not dirs:
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive = HOME / f"{label}-{stamp}.zip"
    seen: set[str] = set()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for base in dirs:
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
                        zf.write(source, arcname=str(arcname))
                    except (OSError, ValueError):
                        continue
    return archive


# --------------------------------------------------------------------------
# operations
# --------------------------------------------------------------------------

def link_one(source: Path, dest: Path, *, force: bool, agent: str, dry_run: bool) -> tuple[str, str]:
    """Link source at dest. Returns (status, detail)."""
    src = source.resolve()
    name = dest.name

    if same_path(dest, src) and is_link_like(dest):
        return "unchanged", f"already -> {src}"

    if dest.exists() or is_link_like(dest):
        if dest.is_symlink() or is_reparse(dest):
            old = os.path.realpath(dest)
            if not dry_run:
                remove_entry(dest)
            status = "relinked"
            detail = f"{old} -> {src}"
        elif dest.is_dir():
            if agent not in MIGRATION_AGENTS and not force:
                return "skipped", "real directory (use --force to replace)"
            if not dry_run:
                remove_entry(dest)
            status = "replaced"
            detail = f"real directory -> {src}"
        else:
            if not force:
                return "skipped", "real file (use --force to replace)"
            if not dry_run:
                remove_entry(dest)
            status = "replaced"
            detail = f"real file -> {src}"
    else:
        status = "linked"
        detail = f"-> {src}"

    if not dry_run:
        try:
            make_link(src, dest)
        except OSError as exc:
            return "failed", str(exc)
    return status, detail


def run_link(
    names: list[str],
    agents: list[str],
    *,
    cwd: Path,
    registry_root: Path,
    force: bool,
    dry_run: bool,
) -> int:
    sources = [resolve_skill(name, cwd, registry_root) for name in names]
    failures = 0
    for agent in agents:
        target = AGENTS[agent]
        print(f"\n[{agent}] {target}")
        if not dry_run:
            target.mkdir(parents=True, exist_ok=True)
        for source in sources:
            status, detail = link_one(
                source,
                target / source.name,
                force=force,
                agent=agent,
                dry_run=dry_run,
            )
            if status == "failed":
                failures += 1
            print(f"  {status:<10} {source.name:<24} {detail}")
    return 1 if failures else 0


def scan_existing(base: Path, known: set[str]) -> dict[str, list[Path]]:
    """Find existing skill entries under base whose names are in known.

    Links/junctions are recorded as entries but never traversed, so a link to a
    skill elsewhere cannot pull its contents into this agent.
    """
    matches: dict[str, list[Path]] = {}

    def visit(directory: Path) -> None:
        try:
            entries = sorted(directory.iterdir(), key=lambda p: p.name.lower())
        except OSError:
            return
        for entry in entries:
            try:
                if is_reparse(entry):
                    # A link named after a registry skill is an old reference
                    # even when its target has already disappeared.
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


def run_refresh(
    agents: list[str],
    *,
    registry_root: Path,
    force: bool,
    dry_run: bool,
    do_backup: bool,
) -> int:
    known = registry_skills(registry_root)
    if not known:
        print(f"error: no skills found in registry {registry_root}", file=sys.stderr)
        return 1

    selected_dirs = [AGENTS[a] for a in agents if AGENTS[a].exists()]
    if do_backup and selected_dirs and not dry_run:
        archive = backup_dirs(selected_dirs)
        if archive:
            print(f"backup: {archive}")

    failures = 0
    for agent in agents:
        target = AGENTS[agent]
        print(f"\n[{agent}] {target}")
        if not target.exists():
            print("  skipped    (agent skill directory does not exist)")
            continue

        matches = scan_existing(target, set(known))
        if not matches:
            print("  no registry-owned entries found")
            continue

        for name in sorted(matches):
            source = known[name]
            places = matches[name]
            direct = target / name
            was = ", ".join(str(p.relative_to(target)) for p in places)
            already = (
                len(places) == 1
                and places[0] == direct
                and is_link_like(direct)
                and same_path(direct, source)
            )
            if already:
                print(f"  {'unchanged':<10} {name:<24} {was} -> {source}")
                continue

            if not dry_run:
                if direct not in places and direct.exists() and not is_link_like(direct):
                    print(f"  skipped    {name:<24} real directory not recognized as a skill")
                    continue
                try:
                    for place in places:
                        if place.exists() or is_link_like(place):
                            remove_entry(place)
                    if direct.exists() or is_link_like(direct):
                        remove_entry(direct)
                    make_link(source, direct)
                except OSError as exc:
                    print(f"  failed     {name:<24} {exc}")
                    failures += 1
                    continue

            state = "would relink" if dry_run else "relinked"
            print(f"  {state:<10} {name:<24} {was} -> {source}")
    return 1 if failures else 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="symlink.py",
        description="Link skills from this registry into global agent skill directories.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python symlink.py avatar\n"
            "  python symlink.py avatar --agents opencode,gemini\n"
            "  python symlink.py avatar mine --agents all --force\n"
            "  python symlink.py --refresh --agents qoder,gemini\n"
            "  python symlink.py --all --agents opencode\n"
        ),
    )
    parser.add_argument("skills", nargs="*", help="skill name(s) or a path to a skill directory")
    parser.add_argument(
        "--agents",
        default="all",
        help=f"comma-separated agents or 'all' (default: all). Choices: {', '.join(DEFAULT_AGENTS)}",
    )
    parser.add_argument("--refresh", action="store_true", help="relink only entries that already exist and are in the registry")
    parser.add_argument("--all", action="store_true", help="link every skill in the registry")
    parser.add_argument("--force", action="store_true", help="replace real directories/files at any agent")
    parser.add_argument("--dry-run", action="store_true", help="show what would happen without changing anything")
    parser.add_argument("--no-backup", action="store_true", help="skip the backup before --refresh")
    parser.add_argument("--registry", type=Path, default=REGISTRY, help="registry root (default: directory containing this script)")
    parser.add_argument("--list", action="store_true", help="list registry skills and exit")
    args = parser.parse_args(argv)

    registry_root = args.registry.resolve()
    if not registry_root.is_dir():
        print(f"error: registry not found: {registry_root}", file=sys.stderr)
        return 1

    if args.list:
        skills = registry_skills(registry_root)
        for name in sorted(skills):
            print(f"{name:<28} {skills[name].relative_to(registry_root)}")
        print(f"\n{len(skills)} skills")
        return 0

    agents = parse_agents(args.agents)

    if args.refresh:
        if args.skills or args.all:
            parser.error("--refresh cannot be combined with skill names or --all")
        return run_refresh(
            agents,
            registry_root=registry_root,
            force=args.force,
            dry_run=args.dry_run,
            do_backup=not args.no_backup,
        )

    if args.all:
        if args.skills:
            parser.error("--all cannot be combined with skill names")
        names = sorted(registry_skills(registry_root))
    else:
        names = args.skills

    if not names:
        parser.error("name at least one skill, or use --all / --refresh")

    return run_link(
        names,
        agents,
        cwd=Path.cwd(),
        registry_root=registry_root,
        force=args.force,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
