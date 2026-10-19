#!/usr/bin/env python3
"""
Compare a project's current dependency version against the version recorded
in a cached docs directory's .version file, and report a verdict.

USAGE
    python cache_version_check.py <docs-dir> <current-version>

Prints a JSON verdict to stdout:
{
  "verdict": "MAJOR",
  "cached_version": "4.0.0",
  "current_version": "4.1.0",
  "reason": "major version differs (4 vs 4)"
}

Verdicts:
  NO_CACHE  -- no .version file found. Run the full workflow from Prune onward.
  MATCH     -- versions are identical.
  PATCH     -- same major.minor, patch differs. Safe to reuse without asking.
  MINOR     -- same major, minor differs. Safe to reuse without asking.
  MAJOR     -- major version differs. STOP and ask the user whether to keep
              the existing docs or rebuild -- do not decide this silently.
  UNKNOWN   -- one or both versions couldn't be parsed into major.minor.patch.
              Treated the same as MAJOR (ask the user) since guessing wrong
              here is exactly the failure mode this script exists to avoid.

This script only detects and reports; it never asks the user itself and
never decides to rebuild or reuse on its own for a MAJOR/UNKNOWN verdict --
that decision is the agent's, in conversation with the user, every time.

Exit codes: 0 = safe to auto-reuse (MATCH/PATCH/MINOR), 2 = NO_CACHE,
3 = needs a user decision (MAJOR/UNKNOWN).
"""

import argparse
import json
import re
import sys
from pathlib import Path

VERSION_RE = re.compile(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?")


def parse_version(v: str):
    if v is None:
        return None
    m = VERSION_RE.search(v)
    if not m:
        return None
    major, minor, patch = m.groups()
    return (
        int(major),
        int(minor) if minor is not None else 0,
        int(patch) if patch is not None else 0,
    )


def compare(cached_version: str, current_version: str):
    if cached_version == current_version:
        return "MATCH", f"identical version strings ('{cached_version}')"

    cached = parse_version(cached_version)
    current = parse_version(current_version)

    if cached is None or current is None:
        return "UNKNOWN", "could not parse one or both versions into major.minor.patch"

    if cached[0] != current[0]:
        return "MAJOR", f"major version differs ({cached[0]} vs {current[0]})"
    if cached[1] != current[1]:
        return "MINOR", f"minor version differs ({cached[1]} vs {current[1]}, same major {cached[0]})"
    if cached[2] != current[2]:
        return "PATCH", f"patch version differs ({cached[2]} vs {current[2]}, same major.minor {cached[0]}.{cached[1]})"
    return "MATCH", "versions are equivalent"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("docs_dir", help="Docs directory that should contain a .version file.")
    parser.add_argument("current_version", help="The project's current dependency version, freshly detected.")
    args = parser.parse_args()

    version_path = Path(args.docs_dir) / ".version"
    if not version_path.exists():
        print(json.dumps({
            "verdict": "NO_CACHE",
            "cached_version": None,
            "current_version": args.current_version,
            "reason": f"no .version file at {version_path}",
        }, indent=2))
        sys.exit(2)

    with open(version_path, "r", encoding="utf-8") as f:
        cached = json.load(f)

    cached_version = cached.get("version")
    verdict, reason = compare(cached_version, args.current_version)

    print(json.dumps({
        "verdict": verdict,
        "cached_version": cached_version,
        "current_version": args.current_version,
        "reason": reason,
    }, indent=2))

    sys.exit(0 if verdict in ("MATCH", "PATCH", "MINOR") else 3)


if __name__ == "__main__":
    main()
