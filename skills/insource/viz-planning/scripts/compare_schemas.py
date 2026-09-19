#!/usr/bin/env python3
"""
compare_schemas.py — check whether multiple data files actually share a
compatible schema, for the "multiple inputs with the same structure"
scenario in references/01-data-foundations.md.

Don't assume same-extension files (data1.json, data2.json, data3.json)
are safe to concatenate just because they look alike — this checks it.

Reports, across all files given:
  - record count per file
  - fields common to ALL files vs. fields only in SOME (schema drift across files)
  - type mismatches on fields that ARE common to all files
  - a verdict: identical / same-fields-different-types / field-sets-differ

Usage:
    python3 compare_schemas.py file1.json file2.json file3.json
    python3 compare_schemas.py data/*.jsonl
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from profile_data import load_records, field_type  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    per_file = {}
    for p in args.paths:
        path = Path(p)
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)
        try:
            records = load_records(path)
        except Exception as e:
            print(f"Could not load {path}: {e}", file=sys.stderr)
            sys.exit(1)
        fields = {}
        for r in records:
            if not isinstance(r, dict):
                continue
            for k, v in r.items():
                fields.setdefault(k, Counter())[field_type(v)] += 1
        per_file[str(path)] = {"count": len(records), "fields": fields}

    print(f"=== Comparing {len(per_file)} files ===")
    for name, info in per_file.items():
        print(f"- {name}: {info['count']} records, {len(info['fields'])} fields")

    all_field_names = set()
    for info in per_file.values():
        all_field_names |= set(info["fields"].keys())

    common = []
    partial = []
    for f in sorted(all_field_names):
        present_in = [name for name, info in per_file.items() if f in info["fields"]]
        if len(present_in) == len(per_file):
            common.append(f)
        else:
            partial.append((f, present_in))

    print(f"\n=== Field presence across files ===")
    print(f"Common to all {len(per_file)} files ({len(common)}): {', '.join(common) if common else '(none)'}")
    if partial:
        print(f"\nOnly in SOME files ({len(partial)}) — this is schema drift ACROSS files, "
              f"not just within one. Decide an unknown-field policy (see references/01-data-foundations.md) "
              f"before treating these files as one dataset:")
        for f, present_in in partial:
            missing_from = [n for n in per_file if n not in present_in]
            print(f"  - {f}: present in {present_in}, MISSING from {missing_from}")

    print(f"\n=== Type consistency on fields common to all files ===")
    mismatches = []
    for f in common:
        type_sets = {name: set(info["fields"][f].keys()) for name, info in per_file.items()}
        all_types = set().union(*type_sets.values())
        if len(all_types) > 1:
            mismatches.append(f)
            print(f"  - {f}: type differs across files -> " + ", ".join(f"{n}: {sorted(t)}" for n, t in type_sets.items()))
    if not mismatches:
        print("  none — every field common to all files has a consistent type")

    print(f"\n=== Verdict ===")
    if not partial and not mismatches:
        print("Schemas are IDENTICAL across all files — safe to concatenate directly.")
    elif not partial and mismatches:
        print(f"Same field set, but {len(mismatches)} field(s) have inconsistent types across files — "
              f"normalize types before concatenating, don't assume they'll coerce cleanly.")
    else:
        print(f"Field sets DIFFER across files ({len(partial)} field(s) not universal) — decide whether to "
              f"concatenate with an unknown-field policy, keep files as separate comparable datasets, or "
              f"treat this as a genuine schema-evolution case (see references/01-data-foundations.md).")


if __name__ == "__main__":
    main()
