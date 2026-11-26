#!/usr/bin/env python3
"""Baseline environment audit (heuristic map of the problem, not the enforcement gate).

Usage:
  python audit_env.py <repo-root> [--domains a.com b.com] [--emails x@a.com] [--app-ids com.a.app]
                      [--ports 3000 4000 5173] [--out report.md] [--json]

Scans source files and reports, per category, file:line hits so you can see the shape of the
problem, pick surfaces to parallelize, and later compare against the real gate's baseline.
Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", ".nuxt", ".output", ".turbo",
    "coverage", ".venv", "venv", "__pycache__", "android", "ios", ".gradle", "Pods",
}
EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".json", ".toml", ".html",
        ".yml", ".yaml", ".py", ".md"}
SKIP_FILES = {"package-lock.json", "bun.lock", "bun.lockb", "yarn.lock", "pnpm-lock.yaml"}
MAX_BYTES = 1_000_000

SURFACE_HINTS = [
    ("nuxt.config", "nuxt app"),
    ("vite.config", "vite app"),
    ("capacitor.config", "capacitor/mobile"),
    ("wrangler.toml", "cloudflare worker/edge"),
    ("turbo.json", "turbo orchestrator"),
    ("nx.json", "nx orchestrator"),
    ("next.config", "next app"),
]

ENV_ACCESS = [
    ("process.env", re.compile(r"\bprocess\.env\b")),
    ("import.meta.env", re.compile(r"\bimport\.meta\.env\b")),
    ("dynamic import.meta access", re.compile(r"Reflect\.get\(\s*import\.meta|import\.meta\.env\s*\?*\.?\[")),
    ("useRuntimeConfig", re.compile(r"\buseRuntimeConfig\s*\(")),
    ("NODE_ENV", re.compile(r"\bNODE_ENV\b")),
    ("dotenv", re.compile(r"""from\s+["']dotenv|require\(\s*["']dotenv|Bun\.file\([^)]*\.env""")),
    ("defensive process check", re.compile(r"globalThis\.process|typeof\s+process\b")),
]
LOOPBACK = re.compile(r"127\.0\.0\.1|\blocalhost\b|\[::1\]|0\.0\.0\.0")
RISKY_HOOKS = re.compile(
    r"dev-login|devMode|test/outbox|__[A-Z_]*TEST[A-Z_]*__|test-google-id-token|"
    r"fixture|purge-cache|ab_bell|snduk-fixture", re.I)
ENV_FILE_RE = re.compile(r"^\.env(\..+)?$")


def iter_files(root: str):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            if fn in SKIP_FILES:
                continue
            p = os.path.join(dp, fn)
            if os.path.splitext(fn)[1] in EXTS or ENV_FILE_RE.match(fn) or fn.startswith(".env"):
                try:
                    if os.path.getsize(p) <= MAX_BYTES:
                        yield p
                except OSError:
                    pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--domains", nargs="*", default=[])
    ap.add_argument("--emails", nargs="*", default=[])
    ap.add_argument("--app-ids", nargs="*", default=[])
    ap.add_argument("--ports", nargs="*", default=["3000", "3001", "4000", "5173", "8000", "8080", "8090"])
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = os.path.abspath(a.root)
    literals = [re.escape(x) for x in (a.domains + a.emails + a.app_ids)]
    lit_re = re.compile("|".join(literals)) if literals else None
    port_re = re.compile(r"(?:localhost|127\.0\.0\.1|\]|\b)\s*:(" + "|".join(map(re.escape, a.ports)) + r")\b")

    hits = defaultdict(list)       # category -> [(rel, line, text)]
    surfaces = defaultdict(set)
    env_files, example_vars = [], defaultdict(set)

    for p in iter_files(root):
        rel = os.path.relpath(p, root).replace("\\", "/")
        base = os.path.basename(p)
        for needle, label in SURFACE_HINTS:
            if base.startswith(needle):
                surfaces[label].add(os.path.dirname(rel) or ".")
        if ENV_FILE_RE.match(base) or base.startswith(".env"):
            env_files.append(rel)
            try:
                for line in open(p, encoding="utf-8", errors="ignore"):
                    m = re.match(r"\s*#?\s*([A-Z][A-Z0-9_]+)\s*=", line)
                    if m:
                        example_vars[rel].add(m.group(1))
            except OSError:
                pass
            continue
        is_test = "/tests/" in f"/{rel}" or ".test." in rel or ".spec." in rel
        try:
            lines = open(p, encoding="utf-8", errors="ignore").read().splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            s = line.strip()
            for name, rx in ENV_ACCESS:
                if rx.search(line):
                    hits[f"env-access: {name}"].append((rel, i, s[:140], is_test))
            if LOOPBACK.search(line) or port_re.search(line):
                hits["loopback/port literal"].append((rel, i, s[:140], is_test))
            if lit_re and lit_re.search(line):
                hits["business literal (domain/email/app id)"].append((rel, i, s[:140], is_test))
            if RISKY_HOOKS.search(line):
                hits["non-prod hook/route (verify guarded)"].append((rel, i, s[:140], is_test))

    # drift: vars present in some env files but not others
    all_vars = set().union(*example_vars.values()) if example_vars else set()
    drift = {f: sorted(all_vars - v) for f, v in example_vars.items() if len(example_vars) > 1}

    result = {
        "root": root,
        "surfaces": {k: sorted(v) for k, v in surfaces.items()},
        "env_files": sorted(env_files),
        "counts": {k: len(v) for k, v in hits.items()},
        "files_per_category": {k: len({h[0] for h in v}) for k, v in hits.items()},
        "hits": {k: v for k, v in hits.items()},
        "vars_missing_per_env_file": drift,
    }

    if a.json:
        out = json.dumps(result, indent=2)
    else:
        L = ["# Environment baseline audit", f"Root: `{root}`", ""]
        L.append("## Surfaces detected")
        for k, v in sorted(result["surfaces"].items()):
            L.append(f"- **{k}**: {', '.join(v)}")
        env_lines = [f"- {f}" for f in result["env_files"]] or ["- none"]
        L += ["", "## Env files", *env_lines, ""]
        L.append("## Counts (non-test hits / total)")
        for k, v in sorted(hits.items()):
            nt = sum(1 for h in v if not h[3])
            L.append(f"- {k}: {nt} / {len(v)} in {result['files_per_category'][k]} files")
        for k, v in sorted(hits.items()):
            L += ["", f"## {k}"]
            by = defaultdict(list)
            for rel, i, t, is_test in v:
                by[rel].append((i, t, is_test))
            for rel in sorted(by):
                L.append(f"- `{rel}`" + (" (test)" if by[rel][0][2] else ""))
                for i, t, _ in by[rel][:6]:
                    L.append(f"    - L{i}: `{t}`")
                if len(by[rel]) > 6:
                    L.append(f"    - ... +{len(by[rel]) - 6} more")
        if drift:
            L += ["", "## Variables missing per env template (drift hint)"]
            for f, miss in drift.items():
                if miss:
                    L.append(f"- `{f}` lacks: {', '.join(miss)}")
        out = "\n".join(L)

    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"wrote {a.out}")
        print("\n".join(f"{k}: {v}" for k, v in sorted(result["counts"].items())))
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
