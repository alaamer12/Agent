#!/usr/bin/env python3
"""Discover existing anti-pattern documentation in a project (read-only).

Usage: python discover_scope.py <project-root> [--max-docs N]

Prints JSON with:
  spec_files          ANTIPATTERN(S).md files found
  doc_sections        headings in docs that look like anti-pattern sections
  agent_instruction_files  AGENTS.md, CLAUDE.md, and similar convention files
  mode_hint           "B" if anything relevant was found, otherwise "C or A (depends on the request)"

The script never modifies files. The mode hint is only a hint: a user-specified
scope (Mode A) always takes precedence over what this script finds.
"""
import argparse
import json
import os
import re
import sys

# Directories that never contain project documentation worth reading.
EXCLUDED_DIRS = {
    ".git", "node_modules", "venv", ".venv", "dist", "build", "target", "vendor",
    "__pycache__", ".next", ".tox", ".mypy_cache", ".pytest_cache", ".gradle", ".idea",
}
SPEC_NAMES = {"antipattern.md", "antipatterns.md", "anti-pattern.md", "anti-patterns.md"}
DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".txt"}
AGENT_FILES = {
    "agents.md", "claude.md", "contributing.md", ".cursorrules",
    "copilot-instructions.md", "gemini.md",
}
# Headings that suggest an anti-pattern or "things to avoid" section.
HEADING_RE = re.compile(
    r"^\s{0,3}#{1,6}\s+.*\b(anti-?patterns?|code smells?|pitfalls?|things to avoid|"
    r"do not|don'?ts?|never do|avoid)\b",
    re.IGNORECASE,
)
MAX_DOC_BYTES = 1_000_000  # skip very large docs (changelogs, generated references)
DEFAULT_MAX_DOCS = 400     # cap on scanned docs so huge repos stay fast


def scan(root, max_docs):
    spec_files, sections, agent_files = [], [], []
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in filenames:
            lower = name.lower()
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            if lower in SPEC_NAMES:
                spec_files.append(rel)
            if lower in AGENT_FILES:
                agent_files.append(rel)
            ext = os.path.splitext(lower)[1]
            if ext not in DOC_EXTENSIONS or scanned >= max_docs:
                continue
            try:
                if os.path.getsize(path) > MAX_DOC_BYTES:
                    continue
                with open(path, encoding="utf-8", errors="replace") as handle:
                    scanned += 1
                    for number, line in enumerate(handle, start=1):
                        if HEADING_RE.match(line):
                            sections.append(
                                {"file": rel, "line": number, "heading": line.strip()}
                            )
            except OSError as error:
                print(f"warning: could not read {rel}: {error}", file=sys.stderr)
    return spec_files, sections, agent_files, scanned


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("root", help="project root directory")
    parser.add_argument("--max-docs", type=int, default=DEFAULT_MAX_DOCS)
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        print(f"error: not a directory: {args.root}", file=sys.stderr)
        return 2

    spec_files, sections, agent_files, scanned = scan(args.root, args.max_docs)
    # Headings inside a spec file are redundant with the file itself.
    sections = [s for s in sections if s["file"] not in spec_files]
    found = bool(spec_files or sections)
    result = {
        "root": os.path.abspath(args.root),
        "spec_files": sorted(spec_files),
        "doc_sections": sections,
        "agent_instruction_files": sorted(agent_files),
        "docs_scanned": scanned,
        "mode_hint": "B" if found else "C or A (depends on the request)",
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
