#!/usr/bin/env python3
"""Detect languages and available analysis tools for a project (read-only).

Usage: python detect_tooling.py <project-root>

Prints JSON with detected languages (by file count), manifests, analyzers
already installed, and analyzers worth considering but missing. It never
installs anything. Prefer installed tools over writing custom analyzers.
"""
import argparse
import json
import os
import shutil
import sys

EXCLUDED_DIRS = {
    ".git", "node_modules", "venv", ".venv", "dist", "build", "target", "vendor",
    "__pycache__", ".next", ".tox", ".mypy_cache", ".pytest_cache", ".gradle", ".idea",
}
EXTENSION_LANGUAGE = {
    ".py": "python", ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript", ".go": "go", ".rs": "rust",
    ".java": "java", ".kt": "kotlin", ".cs": "csharp", ".rb": "ruby", ".php": "php",
}
MANIFESTS = {
    "package.json", "pyproject.toml", "requirements.txt", "setup.py", "go.mod",
    "Cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts", "Gemfile",
    "composer.json", "Dockerfile", "docker-compose.yml",
}
# Language -> analyzer executables worth looking for. Cross-language tools apply to all.
TOOLS = {
    "python": ["radon", "ruff", "mypy", "pyright", "vulture", "bandit", "import-linter", "pydeps"],
    "javascript": ["eslint", "madge", "depcruise", "knip"],
    "typescript": ["tsc", "eslint", "madge", "depcruise", "knip", "ts-prune"],
    "go": ["go", "gocyclo", "staticcheck", "golangci-lint", "gosec"],
    "rust": ["cargo", "cargo-udeps", "cargo-audit"],
    "java": ["pmd", "checkstyle", "spotbugs"],
    "kotlin": ["detekt"],
    "csharp": ["dotnet"],
    "ruby": ["rubocop", "flog", "reek", "brakeman"],
    "php": ["phpstan", "phpmd"],
}
CROSS_LANGUAGE = ["lizard", "jscpd", "cloc", "tokei", "semgrep", "ast-grep", "rg", "git"]
MAX_FILES = 200_000  # safety cap on the directory walk


def find_tool(name, root):
    """Return a path for an executable on PATH or in a local node_modules/.bin."""
    found = shutil.which(name)
    if found:
        return found
    local = os.path.join(root, "node_modules", ".bin", name)
    return local if os.path.exists(local) else None


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("root", help="project root directory")
    args = parser.parse_args()
    if not os.path.isdir(args.root):
        print(f"error: not a directory: {args.root}", file=sys.stderr)
        return 2

    counts, manifests, seen = {}, [], 0
    for dirpath, dirnames, filenames in os.walk(args.root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in filenames:
            seen += 1
            if seen > MAX_FILES:
                break
            if name in MANIFESTS or name.endswith(".csproj"):
                manifests.append(os.path.relpath(os.path.join(dirpath, name), args.root))
            language = EXTENSION_LANGUAGE.get(os.path.splitext(name)[1].lower())
            if language:
                counts[language] = counts.get(language, 0) + 1
        if seen > MAX_FILES:
            print("warning: file cap reached; counts are partial", file=sys.stderr)
            break

    languages = sorted(counts, key=counts.get, reverse=True)
    wanted = list(CROSS_LANGUAGE)
    for language in languages:
        wanted.extend(TOOLS.get(language, []))
    available, missing = {}, []
    for tool in dict.fromkeys(wanted):  # de-duplicate, keep order
        path = find_tool(tool, args.root)
        if path:
            available[tool] = path
        else:
            missing.append(tool)

    print(json.dumps({
        "root": os.path.abspath(args.root),
        "languages": {lang: counts[lang] for lang in languages},
        "manifests": sorted(manifests),
        "tools_available": available,
        "tools_missing": missing,
        "note": "Read-only detection. Install missing tools outside the repository, or skip them.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
