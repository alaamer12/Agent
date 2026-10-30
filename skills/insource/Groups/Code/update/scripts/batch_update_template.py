#!/usr/bin/env python3
"""
Batch Update Script (template)

Performs the same mechanical edit across many files in a consistent, controlled
way, and lets a human review it before anything is written.

USAGE
    python batch_update.py                          # same as --dry-run (safe default)
    python batch_update.py --dry-run --sample 8     # preview + inspect 8 random changed lines
    python batch_update.py --dry-run --seed 42      # reproducible random sample
    python batch_update.py --apply                  # actually write the changes (the USER runs this)

HOW TO CUSTOMIZE THIS TEMPLATE
    1. Set TARGET_FILES to globs scoped to the files where the Detect step found
       real occurrences. Do not point it at the whole repo unless that is what you
       verified. Note: "**/*.yml" does not match dot-directories such as
       .github/ - list those explicitly (".github/**/*.yml").
    2. Fill PATTERNS with one (regex, replacement, description) tuple per distinct
       pattern. Keep patterns separate: the report says which pattern matched where.
    3. Run the dry run, read the whole report, inspect the sample, fix the script,
       repeat. Only then hand the --apply command to the user.

SAFETY PROPERTIES (keep these if you adapt the script)
    - Nothing is written unless --apply is passed.
    - The preview shows the exact final text of each changed line, computed by the
      same function that apply uses, so "what you saw" is "what gets written".
    - Patterns run in order on each line; lines touched by more than one pattern
      are flagged as overlaps so you can check the chaining is intended.
    - Apply re-reads each file and refuses to touch a line that changed since the
      scan (stale preview), instead of overwriting it.
    - Line endings (CRLF / LF) and encoding are preserved; unreadable files are
      reported and skipped, not fatal.

LIMITS
    Matching is line-by-line. Text wrapped across lines (hard-wrapped Markdown,
    JSX that breaks mid-sentence) will not match; handle those by hand or adapt
    the script to match on whole-file text.
"""

import argparse
import glob
import os
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIGURE THESE SECTIONS FOR THE ACTUAL PROJECT
# ---------------------------------------------------------------------------

# Glob(s) for files to scan, relative to where you run the script.
TARGET_FILES = [
    "**/*.py",
]

# One tuple per distinct pattern found during the Detect step:
# (regex, replacement, human-readable description)
#
# Example:
# PATTERNS = [
#     (r"\bfrom old_module\b", "from new_module", "python import statement"),
#     (r'"old_module\.py"', '"new_module.py"', "quoted filename in config strings"),
# ]
PATTERNS = [
    # (regex, replacement, description) -- fill these in.
]

# Directory names to always skip, regardless of TARGET_FILES globs.
EXCLUDED_DIR_NAMES = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv",
                      ".next", "coverage", "target"}

ENCODING = "utf-8"

# ---------------------------------------------------------------------------
# Scaffolding -- shouldn't usually need to change below this line
# ---------------------------------------------------------------------------


@dataclass
class Change:
    file_path: str
    line_number: int
    before_line: str            # line without its line ending
    after_line: str             # exact text that will be written (without line ending)
    fired: list = field(default_factory=list)   # [(description, occurrence_count)]


def resolve_target_files():
    patterns = TARGET_FILES if isinstance(TARGET_FILES, (list, tuple)) else [TARGET_FILES]
    seen, files = set(), []
    for pattern in patterns:
        for path in glob.glob(pattern, recursive=True):
            if path in seen or not os.path.isfile(path):
                continue
            if any(part in EXCLUDED_DIR_NAMES for part in Path(path).parts):
                continue
            seen.add(path)
            files.append(path)
    return sorted(files)


def transform_line(line):
    """Apply every pattern, in order, to one line (no line ending).
    Returns (new_line, fired) where fired = [(description, count), ...].
    This single function is used for both the preview and the apply step."""
    fired = []
    for regex, replacement, description in PATTERNS:
        line, n = re.subn(regex, replacement, line)
        if n:
            fired.append((description, n))
    return line, fired


def split_ending(raw):
    """Split a raw line into (text, ending) preserving CRLF / LF / none."""
    for ending in ("\r\n", "\n", "\r"):
        if raw.endswith(ending):
            return raw[: -len(ending)], ending
    return raw, ""


def read_lines(path):
    # newline="" disables newline translation, so CRLF files stay CRLF.
    with open(path, "r", encoding=ENCODING, newline="") as f:
        return f.readlines()


def find_changes(files):
    changes, unreadable = [], []
    for path in files:
        try:
            lines = read_lines(path)
        except (UnicodeDecodeError, OSError) as e:
            unreadable.append((path, str(e)))
            continue
        for i, raw in enumerate(lines, start=1):
            text, _ = split_ending(raw)
            new_text, fired = transform_line(text)
            if fired and new_text != text:
                changes.append(Change(path, i, text, new_text, fired))
    return changes, unreadable


def print_dry_run_report(changes, unreadable):
    if not changes:
        print("No matching occurrences found. Check TARGET_FILES and PATTERNS.")
    else:
        files_touched = {c.file_path for c in changes}
        total_occ = sum(n for c in changes for _, n in c.fired)
        print(f"Dry run: {total_occ} occurrence(s) on {len(changes)} line(s) "
              f"in {len(files_touched)} file(s).\n")
        by_pattern = {}
        for c in changes:
            for desc, n in c.fired:
                entry = by_pattern.setdefault(desc, {"occ": 0, "files": set()})
                entry["occ"] += n
                entry["files"].add(c.file_path)
        print("By pattern:")
        for desc, e in by_pattern.items():
            print(f"  - {desc}: {e['occ']} occurrence(s) in {len(e['files'])} file(s)")
        print()
        overlaps = [c for c in changes if len(c.fired) > 1]
        if overlaps:
            print(f"Overlap warning: {len(overlaps)} line(s) are changed by more than one pattern "
                  f"(applied in PATTERNS order). Check these are intended:")
            for c in overlaps[:10]:
                print(f"  - {c.file_path}:{c.line_number}  [{', '.join(d for d, _ in c.fired)}]")
            if len(overlaps) > 10:
                print(f"  ... +{len(overlaps) - 10} more")
            print()
    if unreadable:
        print(f"Skipped {len(unreadable)} unreadable file(s) (binary or encoding issue):")
        for path, err in unreadable:
            print(f"  - {path}: {err}")
        print()


def print_sample(changes, sample_size, seed):
    if not changes:
        return
    rng = random.Random(seed)
    n = min(sample_size, len(changes))
    sampled = rng.sample(changes, n)
    print(f"Random sample of {n} changed line(s) (seed {seed}; re-run with --seed {seed} to reproduce):\n")
    for c in sampled:
        print(f"[{c.file_path}:{c.line_number}] ({', '.join(d for d, _ in c.fired)})")
        print(f"  - before: {c.before_line.strip()}")
        print(f"  + after:  {c.after_line.strip()}")
        print()


def apply_changes(changes):
    """Write exactly the previewed text, verifying each line is unchanged since the scan."""
    by_file = {}
    for c in changes:
        by_file.setdefault(c.file_path, []).append(c)

    modified, skipped = 0, []
    for path, file_changes in by_file.items():
        lines = read_lines(path)
        wrote = False
        for c in file_changes:
            idx = c.line_number - 1
            if idx >= len(lines):
                skipped.append((path, c.line_number, "file is shorter than at scan time"))
                continue
            text, ending = split_ending(lines[idx])
            if text != c.before_line:
                skipped.append((path, c.line_number, "line changed since the scan"))
                continue
            lines[idx] = c.after_line + ending
            wrote = True
        if wrote:
            with open(path, "w", encoding=ENCODING, newline="") as f:
                f.writelines(lines)
            modified += 1

    print(f"Applied changes to {modified} file(s).")
    if skipped:
        print(f"Skipped {len(skipped)} line(s) that no longer matched the preview; re-run the dry run:")
        for path, ln, why in skipped:
            print(f"  - {path}:{ln}: {why}")


def main():
    parser = argparse.ArgumentParser(description="Batch update script (see file header for usage).")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true",
                      help="Preview changes without writing to disk (this is also the default).")
    mode.add_argument("--apply", action="store_true",
                      help="Write the changes to disk. Run only after reviewing the dry run.")
    parser.add_argument("--sample", type=int, default=5,
                        help="Number of randomly sampled changed lines to show (default: 5).")
    parser.add_argument("--seed", type=int, default=None,
                        help="Seed for the random sample (default: random; printed so you can reproduce it).")
    args = parser.parse_args()

    if not PATTERNS:
        print("PATTERNS is empty -- fill it in with the patterns found during the Detect step.")
        sys.exit(1)

    files = resolve_target_files()
    if not files:
        print("No files matched TARGET_FILES -- check the glob(s).")
        sys.exit(1)

    changes, unreadable = find_changes(files)

    if not args.apply:
        seed = args.seed if args.seed is not None else random.randrange(1_000_000)
        print_dry_run_report(changes, unreadable)
        print_sample(changes, args.sample, seed)
        print("Dry run complete. No files were modified. Pass --apply to write the changes.")
        return

    if not changes:
        print("No changes to apply.")
        return
    apply_changes(changes)


if __name__ == "__main__":
    main()
