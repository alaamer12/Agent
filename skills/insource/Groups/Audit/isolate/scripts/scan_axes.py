#!/usr/bin/env python3
"""Scan a project for signs of unisolated variation. Language-agnostic, heuristic, stdlib only.

Usage:
  scan_axes.py PATH [--product NAME] [--tokens axis=a,b,c ...] [--top N] [--json]

What it reports:
  1. Filename variants: files like Name.Android.ext or name_windows.go, grouped by base name.
     A name carrying two axes at once (Name.Canary.Android.ext) is a grid and is flagged.
  2. Conditional-logic hotspots: preprocessor blocks, build tags, platform/channel/region checks.
  3. Identity literals: with --product, string literals that contain the product name.
  4. Existing structure: directories that already look like layers or overlays.

The output is evidence for the axis inventory, not a verdict. Confirm every finding by reading code.
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

SKIP_DIRS = {".git", "node_modules", "bin", "obj", "build", "dist", "out", "target", ".venv", "venv",
             "__pycache__", ".gradle", ".idea", ".vs", "Pods", "DerivedData", ".next", ".cache"}
CODE_EXT = {".cs", ".kt", ".kts", ".java", ".swift", ".m", ".mm", ".c", ".cc", ".cpp", ".h", ".hpp",
            ".go", ".rs", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".py", ".rb", ".dart", ".php", ".scala",
            ".csproj", ".props", ".targets", ".gradle", ".toml", ".cmake", ".bzl", ".xaml"}

DEFAULT_TOKENS = {
    "platform": {"android", "ios", "windows", "macos", "linux", "web", "wasm", "mobile", "desktop",
                 "tvos", "watchos", "browser", "node", "win", "mac"},
    "channel": {"canary", "beta", "alpha", "stable", "dev", "nightly", "rc", "preview", "staging",
                "prod", "production", "internal"},
}

PATTERNS = {
    "conditional-compilation": re.compile(r"^\s*#\s*(if|ifdef|ifndef|elif)\b|^\s*//go:build|#\[cfg(_attr)?\(|\bcfg!\("),
    "platform-check": re.compile(
        r"\b(Platform\.OS|process\.platform|navigator\.(platform|userAgent)|OperatingSystem\.Is\w+|"
        r"RuntimeInformation\.IsOSPlatform|DeviceInfo\.Platform|UIDevice|sys\.platform|platform\.system\(|"
        r"runtime\.GOOS|consts::OS|Environment\.OSVersion|Build\.VERSION)"),
    "channel-check": re.compile(
        r"\b(is_?[Cc]anary|IsCanary|BuildConfig\.FLAVOR|isBeta|IsBeta|isNightly)\b|"
        r"\b[Cc]hannel\s*(===?|!==?)\s*[\"']"),
    "audience-check": re.compile(
        r"\b(locale|region|country|countryCode|tenant|tenantId|market)\s*(===?|!==?|\.equals\(|\.Equals\()|"
        r"\bswitch\s*\(\s*(region|country|tenant|market)\b", re.IGNORECASE),
}


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def classify_name(path, vocab):
    """Return (base, {axis: token}) for a filename, or None if no axis token found."""
    name = os.path.basename(path)
    stem, _, ext = name.rpartition(".")
    if not stem:
        return None
    parts = stem.split(".")
    base = parts[0].lstrip("_")
    hits = {}
    for seg in parts[1:]:
        for axis, tokens in vocab.items():
            if seg.lower() in tokens:
                hits[axis] = seg
    # Go/Rust style suffix: name_windows.go
    m = re.match(r"^(.*)_([A-Za-z0-9]+)$", parts[0])
    if m:
        for axis, tokens in vocab.items():
            if m.group(2).lower() in tokens:
                hits[axis] = m.group(2)
                base = m.group(1).lstrip("_")
    return (base, hits) if hits else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--product", help="product name; reports string literals that contain it")
    ap.add_argument("--tokens", action="append", default=[], metavar="AXIS=A,B,C",
                    help="extra filename tokens for an axis, e.g. audience=eg,us")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        sys.exit(f"not a directory: {root}")

    vocab = {k: set(v) for k, v in DEFAULT_TOKENS.items()}
    for spec in args.tokens:
        axis, _, vals = spec.partition("=")
        vocab.setdefault(axis, set()).update(v.strip().lower() for v in vals.split(",") if v.strip())

    families = defaultdict(list)       # (dir, base) -> [(path, hits)]
    cond = {k: defaultdict(int) for k in PATTERNS}
    literals = defaultdict(int)
    layer_dirs = []
    scanned = 0
    lit_re = re.compile(r"[\"'][^\"'\n]*" + re.escape(args.product) + r"[^\"'\n]*[\"']") if args.product else None

    for path in iter_files(root):
        rel = os.path.relpath(path, root)
        cn = classify_name(path, vocab)
        if cn:
            families[(os.path.dirname(rel), cn[0])].append((rel, cn[1]))
        if os.path.splitext(path)[1].lower() not in CODE_EXT:
            continue
        scanned += 1
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except OSError:
            continue
        for line in text.splitlines():
            for key, rx in PATTERNS.items():
                if rx.search(line):
                    cond[key][rel] += 1
        if lit_re:
            n = len(lit_re.findall(text))
            if n:
                literals[rel] = n

    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for d in dirnames:
            if d.lower() in {"layers", "overlays", "flavors", "variants", "platforms"}:
                layer_dirs.append(os.path.relpath(os.path.join(dirpath, d), root))

    grids = []
    wide = []
    for (d, base), items in sorted(families.items()):
        for rel, hits in items:
            if len(hits) >= 2:
                grids.append(rel)
        if len(items) >= 3:
            wide.append({"base": os.path.join(d, base), "variants": sorted(r for r, _ in items)})

    result = {
        "root": root,
        "files_scanned": scanned,
        "filename_variants": {
            "families": len(families),
            "grid_names_two_axes": grids,
            "families_with_3plus_variants": wide[: args.top],
        },
        "conditional_hotspots": {
            k: sorted(v.items(), key=lambda kv: -kv[1])[: args.top] for k, v in cond.items()
        },
        "identity_literals": sorted(literals.items(), key=lambda kv: -kv[1])[: args.top] if lit_re else None,
        "identity_literal_files": len(literals) if lit_re else None,
        "existing_layer_dirs": layer_dirs,
    }

    if args.json:
        json.dump(result, sys.stdout, indent=2)
        print()
        return

    out = [f"# Axis scan: {root}", f"Files scanned: {scanned}", ""]
    out.append("## Filename variants")
    out.append(f"- Families with axis tokens in the name: {len(families)}")
    if grids:
        out.append(f"- GRID names (two axes in one filename), isolation problem: {len(grids)}")
        out += [f"    - {g}" for g in grids[: args.top]]
    else:
        out.append("- No filename carries two axes.")
    for w in wide[: args.top]:
        out.append(f"- Family with {len(w['variants'])} variants (family-file candidate): {w['base']}")
    out.append("")
    out.append("## Conditional-logic hotspots (line hits per file)")
    for key, files in result["conditional_hotspots"].items():
        total = sum(cond[key].values())
        out.append(f"- {key}: {total} hits in {len(cond[key])} files")
        out += [f"    - {f}: {n}" for f, n in files[:5]]
    out.append("")
    if lit_re:
        out.append(f"## Identity literals for '{args.product}'")
        out.append(f"- Literals found in {len(literals)} files (more than one source of identity means collision risk)")
        out += [f"    - {f}: {n}" for f, n in result["identity_literals"][:5]]
        out.append("")
    out.append("## Existing layer-like directories")
    out += [f"- {d}" for d in layer_dirs] or ["- none"]
    out.append("")
    out.append("Heuristic output. Confirm each finding by reading the code before adding it to the axis inventory.")
    print("\n".join(out))


if __name__ == "__main__":
    main()
