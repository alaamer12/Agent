#!/usr/bin/env python3
"""Static compliance auditor for Blockiya Pattern (Base and Strict).

Usage:
    python scripts/audit_blockiya.py <file_or_directory> [--strict] [--core-name NAME]

The utilities package name is configurable: `blockiya-core` is the author's
recommended name, not a requirement — pass --core-name when the project uses
another name for its <<Utility>> package.

Exit codes:
    0 -> No errors found (warnings may still be printed)
    1 -> One or more Blockiya rule violations found
    2 -> Invalid path
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys


@dataclass
class Finding:
    file: Path
    line: int
    severity: str  # "ERROR" | "WARN"
    rule: str
    message: str


def strip_comments_preserving_lines(text: str) -> str:
    """Replace comments with spaces while keeping line numbers intact."""
    def _blank(match: re.Match[str]) -> str:
        return "".join("\n" if ch == "\n" else " " for ch in match.group(0))

    text = re.sub(r"/\*[\s\S]*?\*/", _blank, text)
    text = re.sub(r"//[^\n]*", _blank, text)
    return text


def audit_file(path: Path, strict: bool, core_name: str = "blockiya-core") -> list[Finding]:
    raw = path.read_text(encoding="utf-8")
    cleaned = strip_comments_preserving_lines(raw)
    lines = cleaned.splitlines()
    findings: list[Finding] = []

    is_adapter = "adapter" in path.name.lower() or "adapters" in [p.lower() for p in path.parts]
    is_core = core_name.lower() in [p.lower() for p in path.parts]
    if is_core:
        return findings

    for idx, line in enumerate(lines, start=1):
        # 1. Zero-styling rule (adapters may use ClassNames internally)
        if not is_adapter:
            if re.search(r"\bclassName\s*=", line):
                findings.append(Finding(
                    path, idx, "ERROR", "zero-styling",
                    "Avoid `className=` in Blockiyas/views; use <<Primitive>> token props."
                ))
            if re.search(r"\bstyle\s*=\s*\{\{", line):
                findings.append(Finding(
                    path, idx, "ERROR", "zero-styling",
                    "Avoid inline `style={{...}}` in Blockiyas/views; use <<Primitive>> token props."
                ))

        # 2. Direct API calls instead of queries/ hooks
        if re.search(r"\b(?:fetch|invoke)\s*\(", line):
            findings.append(Finding(
                path, idx, "ERROR", "queries-layer",
                "Direct `fetch()`/`invoke()` call detected; move data access into a `queries/` hook."
            ))

        # 3. Intent contract purity (no UX decisions like window.confirm / navigate inside Blockiya)
        if re.search(r"\bwindow\.confirm\s*\(", line):
            findings.append(Finding(
                path, idx, "ERROR", "intent-contract",
                "Confirmation dialog inside Blockiya violates 'fire intents and stop'; let the caller decide."
            ))

        # 4. Behavioral primitive state leakage
        if re.search(r"\b(?:isOpen|setIsOpen)\b", line):
            findings.append(Finding(
                path, idx, "WARN", "behavioral-encapsulation",
                "`isOpen` detected; behavioral primitives (Dropdown, Modal, Tooltip) must own open state internally via compound components."
            ))

        # 5. Barrel-only import rule for the utilities package (recommended name: blockiya-core)
        if re.search(rf"""from\s+['"][^'"]*{re.escape(core_name)}/(?:structural|intents|derivation|hooks)/""", line):
            findings.append(Finding(
                path, idx, "ERROR", "core-barrel-import",
                f"Import from `{core_name}` root index.ts only, never from internal subpaths."
            ))

        if strict:
            # 6. Strict: no manual useState for isLoading / error async lifecycle
            if re.search(r"\[\s*(?:isLoading|isSaving|error)\s*,\s*set(?:IsLoading|IsSaving|Error)\s*\]\s*=\s*useState", line):
                findings.append(Finding(
                    path, idx, "ERROR", "strict-use-intent",
                    "Strict Blockiya: replace manual `isLoading`/`isSaving`/`error` useState with `useIntent`."
                ))
            # 7. Strict: no manual useMemo for derivation
            if re.search(r"\buseMemo\s*\(", line):
                findings.append(Finding(
                    path, idx, "WARN", "strict-use-derive",
                    "Strict Blockiya: prefer `useDerive(source, moduleScopeDeriver)` over inline `useMemo`."
                ))
            # 8. Strict: raw .map() rendering in JSX
            if re.search(r"\{[^}]*\.map\s*\(", line):
                findings.append(Finding(
                    path, idx, "WARN", "strict-structural-for",
                    "Strict Blockiya: replace inline `.map()` JSX rendering with `<For each={} keyExtractor={}>`."
                ))
            # 9. Strict: raw && conditional JSX rendering
            if re.search(r"\{[^}]*&&\s*<[A-Za-z]", line):
                findings.append(Finding(
                    path, idx, "WARN", "strict-structural-if",
                    "Strict Blockiya: replace inline `{cond && <Component />}` with `<If>` or `<Maybe>`."
                ))

    # 10. Props ceiling (>7 props on *BlockProps or *Props)
    for match in re.finditer(r"(?:type|interface)\s+(\w*Block\w*Props)\s*(?:=\s*)?\{([\s\S]*?)\}", cleaned):
        prop_type_name = match.group(1)
        body = match.group(2)
        prop_lines = [
            ln.strip() for ln in body.splitlines()
            if ln.strip() and ":" in ln and not ln.strip().startswith(("{", "}"))
        ]
        if len(prop_lines) > 7:
            line_no = cleaned[: match.start()].count("\n") + 1
            findings.append(Finding(
                path, line_no, "WARN", "props-ceiling",
                f"`{prop_type_name}` declares {len(prop_lines)} props (ceiling is 3-7). Consider splitting into child Blockiyas or grouping by domain."
            ))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit React/TypeScript files against Blockiya Pattern rules."
    )
    parser.add_argument("target", type=Path, help="File or directory to audit")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforce Strict Blockiya rules (useIntent, useDerive, If/Maybe/For)",
    )
    parser.add_argument(
        "--core-name",
        default="blockiya-core",
        help="Name of the project's <<Utility>> package (author's recommended name: blockiya-core)",
    )
    args = parser.parse_args()

    if not args.target.exists():
        print(f"Error: path does not exist: {args.target}", file=sys.stderr)
        return 2

    files = (
        [args.target]
        if args.target.is_file()
        else sorted(p for p in args.target.rglob("*") if p.suffix in {".ts", ".tsx"})
    )

    all_findings: list[Finding] = []
    for f in files:
        all_findings.extend(audit_file(f, strict=args.strict, core_name=args.core_name))

    mode = "Strict Blockiya" if args.strict else "Base Blockiya"
    print(f"Audited {len(files)} file(s) in {mode} mode.")

    errors = [f for f in all_findings if f.severity == "ERROR"]
    warnings = [f for f in all_findings if f.severity == "WARN"]

    for f in all_findings:
        print(f"[{f.severity}] {f.file}:{f.line} ({f.rule}) {f.message}")

    print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
