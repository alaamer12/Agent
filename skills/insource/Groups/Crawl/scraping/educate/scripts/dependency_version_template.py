#!/usr/bin/env python3
"""
Dependency Version Detection Script (template)

Detects which version(s) of a given package/library a project actually
depends on, by checking whatever dependency manifest(s) the project's
ecosystem actually uses -- including monorepos where different packages
might depend on conflicting versions.

USAGE
    python dependency_version_template.py <package-name> [--project-root PATH]

THIS SCRIPT IS A TEMPLATE, NOT A FIXED TOOL
    ECOSYSTEM_DETECTORS below ships with a handful of illustrative starting
    examples (Node, PHP, Python, Rust, Go, Ruby) covering common manifest
    shapes. That list is NOT exhaustive and is not a mandate to only support
    those ecosystems -- it exists to show the pattern. Before assuming a
    project isn't covered:

    1. Look at what manifest files actually exist in the project (a project
       may use several at once in a polyglot monorepo, or one not listed
       here at all -- .NET's *.csproj, Java/Kotlin's pom.xml or
       build.gradle[.kts], Swift's Package.swift, Elixir's mix.exs, and so
       on all exist and are just as valid).
    2. If an existing detector's `glob` already matches the manifest format
       in question, you likely don't need a new entry at all.
    3. If it's a new format but fits one of the two generic engines below
       (`json_fields` for JSON-shaped manifests, `regex_manifest` for
       anything else text/TOML/line-based), add a plain data entry -- no new
       parsing code required. That's the common case.
    4. Only write a brand new handler function if the format genuinely
       doesn't fit either generic shape (see "Extending" in
       references/manifest-formats.md).

    Adding support for an ecosystem should almost always be "add a
    dictionary to a list," not "write a new parser."
"""

import argparse
import glob
import json
import re
import sys
from pathlib import Path

EXCLUDED_DIR_NAMES = {
    "node_modules", ".git", "target", "venv", ".venv", "vendor",
    "dist", "build", "__pycache__", ".cache", ".batch_update_backups",
    "obj", "bin", "_build", "deps",
}

# ---------------------------------------------------------------------------
# ECOSYSTEM_DETECTORS -- illustrative starting examples, not an exhaustive or
# mandatory list. Each entry is plain data describing where to look and how
# to read it; add, remove, or edit entries freely for the project at hand.
#
# Two generic engine types cover almost everything:
#   "json_fields"     -- manifest is JSON; check named top-level object
#                         fields for a `package_name` key.
#                         [e.g. package.json, composer.json, or any other
#                         JSON manifest with a similar dependency-object shape]
#   "regex_manifest"  -- manifest is text/TOML/line-based; search the whole
#                         file with a regex, where "{pkg}" is substituted
#                         with the (already-escaped) package name.
#                         [e.g. Cargo.toml, pyproject.toml, go.mod, Gemfile,
#                         requirements.txt, or most other plain-text formats]
#
# If neither shape fits (e.g. XML like pom.xml, or something requiring real
# structural parsing), write a small dedicated function instead -- see
# references/manifest-formats.md for that extension path.
# ---------------------------------------------------------------------------

ECOSYSTEM_DETECTORS = [
    {
        "name": "node/npm/yarn/pnpm/bun (package.json)",
        "type": "json_fields",
        "glob": "**/package.json",
        "fields": ["dependencies", "devDependencies", "peerDependencies", "optionalDependencies"],
    },
    {
        "name": "php/composer (composer.json)",
        "type": "json_fields",
        "glob": "**/composer.json",
        "fields": ["require", "require-dev"],
    },
    {
        "name": "python/pyproject (PEP 621 / poetry / uv)",
        "type": "regex_manifest",
        "glob": "**/pyproject.toml",
        # Matches both `pkg = "1.2.3"` / `pkg = {{ version = "1.2.3" }}` (poetry-style
        # tables) and quoted list entries like "pkg>=1.2.3" (PEP 621 dependency lists).
        "pattern": r'["\']?{pkg}["\']?\s*=\s*(?:\{{[^}}]*version\s*=\s*)?["\']([^"\']+)["\']'
                   r'|["\']({pkg}\s*[=<>!~^][^"\']+)["\']',
    },
    {
        "name": "python/pip (requirements*.txt)",
        "type": "regex_manifest",
        "glob": "**/requirements*.txt",
        "pattern": r"^\s*{pkg}\s*([=<>!~^]{{1,2}}\s*[\w.\-]+)",
        "flags_multiline": True,
    },
    {
        "name": "rust/cargo (Cargo.toml)",
        "type": "regex_manifest",
        "glob": "**/Cargo.toml",
        "pattern": r'["\']?{pkg}["\']?\s*=\s*(?:\{{[^}}]*version\s*=\s*)?["\']([^"\']+)["\']',
    },
    {
        "name": "go/modules (go.mod)",
        "type": "regex_manifest",
        "glob": "**/go.mod",
        "pattern": r"{pkg}\s+(v[\w.\-+]+)",
    },
    {
        "name": "ruby/bundler (Gemfile)",
        "type": "regex_manifest",
        "glob": "**/Gemfile",
        "pattern": r'gem\s+["\']{pkg}["\']\s*,\s*["\']([^"\']+)["\']',
    },
    # Example Option: a project using a manifest shape not listed above --
    # say, Elixir's mix.exs or Swift's Package.swift -- would typically only
    # need one more entry here, of whichever generic type actually fits its
    # syntax, rather than a change anywhere else in this script.
]


def is_excluded(path: str) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in Path(path).parts)


def find_manifests(project_root: str, glob_pattern: str):
    pattern = str(Path(project_root) / glob_pattern)
    return sorted(p for p in glob.glob(pattern, recursive=True) if not is_excluded(p))


def normalize_version(raw_spec: str):
    """Best-effort extraction of a version core (e.g. '2.31.0') from a raw
    dependency spec that might include range operators, carets, 'v' prefixes,
    quotes, etc. Returns None if nothing version-like is found."""
    if raw_spec is None:
        return None
    match = re.search(r"(\d+(?:\.\d+){0,3}(?:[-.][0-9A-Za-z]+)*)", raw_spec)
    return match.group(1) if match else None


# ---------------------------------------------------------------------------
# Generic engines -- add new ECOSYSTEM_DETECTORS entries against these two
# rather than writing bespoke parsing code, whenever the manifest shape fits.
# ---------------------------------------------------------------------------


def run_json_fields(entry, package_name, project_root):
    """Engine for JSON manifests: look up package_name as a key inside any
    of the named top-level object fields (e.g. "dependencies")."""
    results = []
    for path in find_manifests(project_root, entry["glob"]):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        for field in entry["fields"]:
            deps = data.get(field)
            if isinstance(deps, dict) and package_name in deps:
                results.append((path, str(deps[package_name])))
                break
    return results


def run_regex_manifest(entry, package_name, project_root):
    """Engine for text/TOML/line-based manifests: substitute the escaped
    package name into the entry's pattern template and search the whole
    file. Returns the first non-empty captured group as the raw spec."""
    pattern = entry["pattern"].format(pkg=re.escape(package_name))
    flags = re.IGNORECASE | (re.MULTILINE if entry.get("flags_multiline") else 0)
    compiled = re.compile(pattern, flags)

    results = []
    for path in find_manifests(project_root, entry["glob"]):
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue
        m = compiled.search(text)
        if m:
            groups = [g for g in m.groups() if g]
            raw_spec = groups[0] if groups else m.group(0)
            results.append((path, raw_spec))
    return results


ENGINES = {
    "json_fields": run_json_fields,
    "regex_manifest": run_regex_manifest,
}


def detect(package_name, project_root):
    found = []
    for entry in ECOSYSTEM_DETECTORS:
        engine = ENGINES.get(entry["type"])
        if engine is None:
            continue  # unknown/custom type -- handle it with your own code path
        for path, raw_spec in engine(entry, package_name, project_root):
            found.append({
                "file": path,
                "ecosystem": entry["name"],
                "raw_spec": raw_spec,
                "normalized_version": normalize_version(raw_spec),
            })

    distinct_versions = sorted({
        f["normalized_version"] for f in found if f["normalized_version"]
    })

    return {
        "package": package_name,
        "project_root": project_root,
        "found": found,
        "distinct_versions": distinct_versions,
        "conflict": len(distinct_versions) > 1,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("package_name", help="Name of the package/library/module to look up.")
    parser.add_argument("--project-root", default=".", help="Root directory to search (default: current directory).")
    args = parser.parse_args()

    report = detect(args.package_name, args.project_root)
    print(json.dumps(report, indent=2))

    if not report["found"]:
        sys.exit(2)  # not found by any configured detector -- check whether
                      # the project's actual manifest format has an entry above
                      # before concluding the package isn't there at all
    if report["conflict"]:
        sys.exit(1)  # found, but with conflicting versions -- caller must ask the user
    sys.exit(0)


if __name__ == "__main__":
    main()
