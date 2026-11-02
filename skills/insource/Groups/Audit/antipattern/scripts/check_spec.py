#!/usr/bin/env python3
"""Validate an anti-pattern specification (ANTIPATTERN.md format from this skill).

Usage: python check_spec.py <file> [--json]

A rule is a heading like `### AP-001: Name` followed by bold-labelled fields:
Avoid, Instead, Applies when, Why it matters, Exceptions, Compliance check
(Level is optional: Required or Recommended; Example is an optional before/after pair.)

Exit code 0 when valid, 1 when errors were found, 2 on usage or read errors.
Documents that follow another project format are outside this checker's scope.
"""
import argparse
import json
import re
import sys

REQUIRED_FIELDS = ["Avoid", "Instead", "Applies when", "Why it matters", "Exceptions", "Compliance check"]
OPTIONAL_FIELDS = ["Level", "Example"]
VALID_LEVELS = {"required", "recommended"}
RULE_RE = re.compile(r"^#{2,4}\s+(AP-\d+)\s*[:\-\u2014]\s*(.+?)\s*$")
HEADING_RE = re.compile(r"^#{1,6}\s")
ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS
FIELD_RE = re.compile(
    r"^\s*(?:[-*]\s*)?\*\*(" + "|".join(re.escape(f) for f in ALL_FIELDS) + r"):\*\*\s*(.*)$"
)
# Text that signals an unfinished template.
PLACEHOLDER_RE = re.compile(r"(<[^>\n]+>|\bTODO\b|\bTBD\b|\bFIXME\b)")


def parse(text):
    rules, current, field = [], None, None
    for number, line in enumerate(text.splitlines(), start=1):
        match = RULE_RE.match(line)
        if match:
            current = {"id": match.group(1), "name": match.group(2), "line": number, "fields": {}}
            rules.append(current)
            field = None
            continue
        if HEADING_RE.match(line):
            current, field = None, None  # a non-rule heading ends the rule
            continue
        if current is None:
            continue
        field_match = FIELD_RE.match(line)
        if field_match:
            field = field_match.group(1)
            current["fields"][field] = field_match.group(2).strip()
        elif field and line.strip():
            current["fields"][field] += " " + line.strip()
    return rules


def validate(rules):
    errors, warnings, seen = [], [], {}
    if not rules:
        errors.append("no rules found (expected headings like '### AP-001: Name')")
    for rule in rules:
        where = f"{rule['id']} (line {rule['line']})"
        if rule["id"] in seen:
            errors.append(f"{where}: duplicate id, first used at line {seen[rule['id']]}")
        seen[rule["id"]] = rule["line"]
        for name in REQUIRED_FIELDS:
            value = rule["fields"].get(name)
            if value is None:
                errors.append(f"{where}: missing field '{name}'")
            elif not value:
                errors.append(f"{where}: field '{name}' is empty")
        for name, value in rule["fields"].items():
            if PLACEHOLDER_RE.search(value):
                errors.append(f"{where}: field '{name}' contains placeholder text")
        level = rule["fields"].get("Level")
        if level is not None and level.strip().lower() not in VALID_LEVELS:
            errors.append(f"{where}: Level must be Required or Recommended, got '{level}'")
        avoid = rule["fields"].get("Avoid", "")
        if avoid and len(avoid.split()) < 4:
            warnings.append(f"{where}: 'Avoid' is very short; make the rule specific")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("file")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()
    try:
        with open(args.file, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as error:
        print(f"error: cannot read {args.file}: {error}", file=sys.stderr)
        return 2

    rules = parse(text)
    errors, warnings = validate(rules)
    if args.json:
        print(json.dumps({"rules": len(rules), "errors": errors, "warnings": warnings}, indent=2))
    else:
        print(f"{len(rules)} rule(s) checked in {args.file}")
        for message in errors:
            print(f"ERROR   {message}")
        for message in warnings:
            print(f"WARNING {message}")
        print("OK" if not errors else f"FAILED with {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
