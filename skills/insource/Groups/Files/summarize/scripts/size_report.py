#!/usr/bin/env python3
"""
size_report.py — report line/word/character counts for a source file and its
summary, plus the resulting compression ratio.

Usage:
    python3 size_report.py <input_path> <output_path>
    python3 size_report.py <input_path> --stdin-output   # read summary from stdin
    python3 size_report.py --text-input --stdin-output   # both via stdin (rare)

Design notes:
- Pure standard library (no dependencies) so it runs in any environment.
- Counts lines, words, and characters for both files and prints a compact
  before/after table plus a single-line reduction percentage, suitable for
  pasting directly under a delivered summary.
- If Python is unavailable, use the bash or PowerShell equivalents in
  references/06-output-and-reporting.md instead — same three metrics.
"""

import sys


def counts(text: str) -> dict:
    lines = text.splitlines()
    words = text.split()
    return {
        "lines": len(lines),
        "words": len(words),
        "chars": len(text),
    }


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def pct_reduction(before: int, after: int) -> str:
    if before == 0:
        return "n/a"
    return f"{(1 - after / before) * 100:.1f}%"


def print_report(before: dict, after: dict, input_label: str, output_label: str) -> None:
    rows = [
        ("Lines", before["lines"], after["lines"]),
        ("Words", before["words"], after["words"]),
        ("Characters", before["chars"], after["chars"]),
    ]
    label_w = max(len("Metric"), max(len(r[0]) for r in rows))
    in_w = max(len("Input"), max(len(str(r[1])) for r in rows))
    out_w = max(len("Summary"), max(len(str(r[2])) for r in rows))

    print(f"{'Metric':<{label_w}}  {'Input':>{in_w}}  {'Summary':>{out_w}}  Reduction")
    for name, b, a in rows:
        print(f"{name:<{label_w}}  {b:>{in_w}}  {a:>{out_w}}  {pct_reduction(b, a)}")
    print()
    print(f"Input:   {input_label}")
    print(f"Summary: {output_label}")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    if "--stdin-output" in args:
        args.remove("--stdin-output")
        output_text = sys.stdin.read()
        output_label = "(stdin)"
    else:
        if len(args) < 2:
            print("Error: need <input_path> <output_path>, or --stdin-output.")
            sys.exit(1)
        output_path = args[1]
        output_text = read_file(output_path)
        output_label = output_path

    input_path = args[0]
    input_text = read_file(input_path)

    before = counts(input_text)
    after = counts(output_text)
    print_report(before, after, input_path, output_label)


if __name__ == "__main__":
    main()
