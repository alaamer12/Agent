#!/usr/bin/env python3
"""Link global AGENTS.md from insource registry into all agent configurations.

Usage:
    python agents_symlink.py
    python agents_symlink.py --mode copy
    python agents_symlink.py --agents qoder,gemini,claude
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
from pathlib import Path

HOME = Path.home()
REGISTRY = Path(__file__).resolve().parent
SOURCE_AGENTS_MD = REGISTRY / "AGENTS.md"

# Agent configurations and their global instruction file locations
AGENT_TARGETS: dict[str, list[Path]] = {
    "qoder": [HOME / ".qoder" / "agents.md"],
    "gemini": [
        HOME / ".gemini" / "AGENTS.md",
        HOME / ".gemini" / "antigravity" / "AGENTS.md",
        HOME / ".gemini" / "antigravity" / "global_rules.md",
    ],
    "claude": [
        HOME / ".claude" / "CLAUDE.md",
        HOME / ".claude" / "agents.md",
    ],
    "junie": [HOME / ".junie" / "agents.md"],
    "opencode": [HOME / ".config" / "opencode" / "AGENTS.md"],
}


def is_link_like(path: Path) -> bool:
    try:
        st = os.lstat(path)
    except OSError:
        return False
    attrs = getattr(st, "st_file_attributes", 0)
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)) or stat.S_ISLNK(st.st_mode)


def link_file(source: Path, target: Path, mode: str = "symlink") -> str:
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() or is_link_like(target):
        if is_link_like(target):
            target.unlink()
        else:
            # Backup non-link existing file once if it has content
            backup = target.with_suffix(".bak")
            if not backup.exists():
                shutil.copy2(target, backup)
            target.unlink()

    if mode == "symlink":
        try:
            target.symlink_to(source)
            return "symlinked"
        except OSError as e:
            # Fallback to copy if Windows symlink permissions fail
            shutil.copy2(source, target)
            return f"copied (symlink failed: {e})"
    elif mode == "copy":
        shutil.copy2(source, target)
        return "copied"
    else:
        raise ValueError(f"Unknown mode: {mode}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=["symlink", "copy"],
        default="symlink",
        help="Link mode (symlink default, or copy)",
    )
    parser.add_argument(
        "--agents",
        default="all",
        help="Comma-separated agent names or 'all'",
    )
    args = parser.parse_args()

    if not SOURCE_AGENTS_MD.exists():
        sys.exit(f"Error: Source AGENTS.md not found at {SOURCE_AGENTS_MD}")

    selected = (
        list(AGENT_TARGETS.keys())
        if args.agents == "all"
        else [a.strip() for a in args.agents.split(",") if a.strip()]
    )

    print(f"Source file: {SOURCE_AGENTS_MD}")
    print(f"Deploy mode: {args.mode}\n")

    for agent in selected:
        if agent not in AGENT_TARGETS:
            print(f"[{agent}] Unknown agent, skipping.")
            continue
        targets = AGENT_TARGETS[agent]
        for target in targets:
            status = link_file(SOURCE_AGENTS_MD, target, mode=args.mode)
            print(f"[{agent}] -> {target} ({status})")


if __name__ == "__main__":
    main()
