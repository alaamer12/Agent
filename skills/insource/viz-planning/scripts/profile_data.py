#!/usr/bin/env python3
"""
profile_data.py — structural profile of a JSON/JSONL/CSV dataset, built to
answer viz-planning's triage questions from evidence instead of guesswork.

Prints:
  - volume (record count)
  - schema (fields found, presence rate, types, empty/null rate, cardinality
    for candidate categorical fields, numeric range for candidate numeric fields)
  - exact-duplicate count
  - a monotonicity check across the WHOLE file (not just a sample) on
    numeric/orderable fields — the strongest evidence for "is this data
    inherently ordered/continuous"
  - a RANDOM sample (reveals distribution/diversity)
  - a SEQUENTIAL sample, first N in file order (reveals continuity/pattern)
  Comparing the random and sequential samples is the point: if they look
  similar, order probably doesn't carry meaning; if the sequential sample
  shows a clear trend the random one doesn't, the data likely has a
  meaningful inherent order (append order, time order, etc).

Usage:
    python3 profile_data.py <path> [--random N] [--sequential N]

Defaults: --random 8 --sequential 8
Supports: .json (array of objects, or an object with exactly one list-valued
          field), .jsonl / .ndjson, .csv
"""

import argparse
import csv
import json
import random
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

CAP = 5000  # cap collected values per field, to bound memory on huge files


def load_records(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            list_fields = [k for k, v in data.items() if isinstance(v, list)]
            if len(list_fields) == 1:
                print(f"(top-level JSON is an object; using its list field {list_fields[0]!r})")
                return data[list_fields[0]]
            if len(list_fields) > 1:
                largest = max(list_fields, key=lambda k: len(data[k]))
                print(f"(top-level JSON has multiple list fields {list_fields}; using largest, {largest!r})")
                return data[largest]
            return [data]  # a single record, not a collection
        raise ValueError("Unrecognized JSON top-level shape")
    if suffix in (".jsonl", ".ndjson"):
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
    if suffix == ".csv":
        with open(path, "r", encoding="utf-8", newline="") as f:
            return [coerce_row(row) for row in csv.DictReader(f)]
    raise ValueError(f"Unsupported file type: {suffix}. Supported: .json .jsonl .ndjson .csv")


def coerce_row(row: dict) -> dict:
    """CSV values arrive as strings; recover int/float/bool/null so stats work."""
    out = {}
    for k, v in row.items():
        out[k] = coerce_value(v)
    return out


def coerce_value(v):
    if v is None or v == "":
        return None
    if v in ("true", "True", "TRUE"):
        return True
    if v in ("false", "False", "FALSE"):
        return False
    try:
        iv = int(v)
        return iv
    except (ValueError, TypeError):
        pass
    try:
        return float(v)
    except (ValueError, TypeError):
        pass
    return v


def is_emptyish(value):
    return value is None or value == "" or value == {} or value == []


def empty_kind(value):
    """Distinguish null / "" / {} / [] rather than lumping them into one 'empty' bucket —
    references/01-data-foundations.md treats these as meaningfully different."""
    if value is None:
        return "null"
    if value == "":
        return "empty_string"
    if value == {}:
        return "empty_object"
    if value == []:
        return "empty_array"
    return None


def looks_like_timestamp(value):
    if not isinstance(value, str):
        return False
    if len(value) >= 8 and value[:4].isdigit() and "-" in value[:10]:
        return True
    if value.isdigit() and len(value) in (10, 13):  # unix seconds / millis
        return True
    return False


def field_type(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "timestamp?" if looks_like_timestamp(value) else "string"
    return type(value).__name__


def decimal_places(v):
    """How many decimal places a float was actually given at — informs a rounding/precision
    decision instead of guessing one (see references/02-semantics-and-intent.md)."""
    if isinstance(v, float):
        s = repr(v)
        if "e" in s or "E" in s:
            return None  # scientific notation — not a meaningful decimal-place count
        return len(s.split(".")[1]) if "." in s else 0
    return None


def try_parse_dt(value):
    """Best-effort parse of a timestamp-looking value into a datetime, to compute a span.
    Returns None rather than raising if it doesn't parse — this is a hint, not a validator."""
    if isinstance(value, str):
        s = value.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(s)
        except ValueError:
            return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            if value > 10**12:
                return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
            if value > 10**9:
                return datetime.fromtimestamp(value, tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            return None
    return None


def hashable(v):
    if isinstance(v, (dict, list)):
        return json.dumps(v, sort_keys=True, default=str)
    return v


def profile_scalars(records, n_random, n_seq):
    n = len(records)
    types = Counter(field_type(v) for v in records)
    distinct = len(set(hashable(v) for v in records))
    print(f"\n=== Volume ===\n{n} records (flat list of scalars, not objects)")
    print(f"\n=== Types / cardinality ===\ntypes: {dict(types)}  distinct values: {distinct}")
    print(f"\n=== Random sample ({min(n, n_random)}) ===")
    for v in random.sample(records, min(n, n_random)):
        print(repr(v))
    print(f"\n=== Sequential sample, first {min(n, n_seq)} ===")
    for v in records[: min(n, n_seq)]:
        print(repr(v))


def profile(records, n_random, n_seq):
    n = len(records)
    print(f"\n=== Volume ===\n{n} records")
    if n == 0:
        return
    if not isinstance(records[0], dict):
        profile_scalars(records, n_random, n_seq)
        return

    field_presence = Counter()
    field_types = defaultdict(Counter)
    field_empty_kinds = defaultdict(Counter)
    field_values = defaultdict(list)

    for r in records:
        if not isinstance(r, dict):
            continue
        for k, v in r.items():
            field_presence[k] += 1
            field_types[k][field_type(v)] += 1
            kind = empty_kind(v)
            if kind is not None:
                field_empty_kinds[k][kind] += 1
            elif len(field_values[k]) < CAP:
                field_values[k].append(v)

    all_fields = sorted(field_presence.keys())
    consistent = all(field_presence[f] == n for f in all_fields)
    print(f"\n=== Schema ({len(all_fields)} distinct fields) ===")
    print("Every record has every field: " + ("yes" if consistent else "no — schema varies across records"))

    for f in all_fields:
        present = field_presence[f]
        missing = n - present  # field absent from the record entirely — different from present-but-empty
        empty_breakdown = field_empty_kinds[f]
        empty_total = sum(empty_breakdown.values())
        empty_str = ", ".join(f"{k}:{c}" for k, c in empty_breakdown.most_common()) if empty_breakdown else "none"
        type_str = ", ".join(f"{t}x{c}" for t, c in field_types[f].most_common())
        vals = field_values[f]
        distinct = len(set(hashable(v) for v in vals)) if vals else 0

        extra = ""
        if vals and distinct <= 20 and all(field_type(v) in ("string", "int", "bool") for v in vals[:100]):
            top = Counter(hashable(v) for v in vals).most_common(8)
            extra = "  categorical candidate, top values: " + ", ".join(f"{v!r}x{c}" for v, c in top)
        elif vals and all(field_type(v) in ("int", "float") for v in vals):
            nums = [v for v in vals if isinstance(v, (int, float))]
            if nums:
                max_dp = max((decimal_places(v) or 0) for v in nums)
                extra = (f"  numeric range: {min(nums)}..{max(nums)}, mean {statistics.mean(nums):.2f}, "
                         f"up to {max_dp} decimal place(s) observed")
        elif vals and all(field_type(v) == "timestamp?" for v in vals):
            lo, hi = min(vals), max(vals)  # lexical min/max works for ISO 8601 and equal-length epoch strings/ints
            dt_lo, dt_hi = try_parse_dt(lo), try_parse_dt(hi)
            span_note = f", span ~{abs((dt_hi - dt_lo).days)} days" if dt_lo and dt_hi else ""
            extra = f"  time range: {lo} .. {hi}{span_note}"

        print(
            f"- {f}: present {present}/{n} ({present/n:.0%}), missing (field absent) {missing}, "
            f"empty (present but empty-ish) {empty_total} [{empty_str}], "
            f"types [{type_str}], distinct sampled {distinct}{extra}"
        )

    seen = Counter(json.dumps(r, sort_keys=True, default=str) for r in records if isinstance(r, dict))
    dupes = sum(c - 1 for c in seen.values() if c > 1)
    print(f"\n=== Duplicates ===\nExact-duplicate records: {dupes}")

    print("\n=== Continuity / ordering check (whole file, not a sample) ===")
    found = False
    for f in all_fields:
        raw = [r.get(f) for r in records if isinstance(r, dict) and f in r and not is_emptyish(r.get(f))]
        numeric_vals = [v for v in raw if isinstance(v, (int, float)) and not isinstance(v, bool)]
        ts_vals = [v for v in raw if isinstance(v, str) and looks_like_timestamp(v)]
        vals, kind = None, None
        if raw and len(numeric_vals) == len(raw):
            vals, kind = numeric_vals, "numeric"
        elif raw and len(ts_vals) == len(raw):
            vals, kind = ts_vals, "timestamp-like string (compared lexically — works for ISO 8601)"
        if vals and len(vals) >= max(5, int(n * 0.5)):
            increasing = all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))
            decreasing = all(vals[i] >= vals[i + 1] for i in range(len(vals) - 1))
            if increasing or decreasing:
                found = True
                print(f"- {f} ({kind}): monotonically {'increasing' if increasing else 'decreasing'} across "
                      f"the file — data appears ordered by this field")
    if not found:
        print("- no field is monotonic across the whole file — no obvious inherent ordering detected")

    k_rand = min(n, n_random)
    k_seq = min(n, n_seq)
    print(f"\n=== Random sample ({k_rand}) — check for distribution/diversity ===")
    for r in random.sample(records, k_rand):
        print(json.dumps(r, default=str, ensure_ascii=False)[:500])

    print(f"\n=== Sequential sample (first {k_seq}, file order) — check for continuity/pattern ===")
    for r in records[:k_seq]:
        print(json.dumps(r, default=str, ensure_ascii=False)[:500])

    print(
        "\n=== Compare the two samples above ===\n"
        "Similar-looking → order probably doesn't carry meaning (independent records).\n"
        "Sequential shows a trend the random one doesn't → the data likely has a\n"
        "meaningful inherent order (append order, time order, etc)."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path")
    parser.add_argument("--random", type=int, default=8)
    parser.add_argument("--sequential", type=int, default=8)
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    records = load_records(path)
    profile(records, args.random, args.sequential)


if __name__ == "__main__":
    main()
