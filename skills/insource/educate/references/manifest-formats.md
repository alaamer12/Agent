# Manifest formats reference

How `scripts/dependency_version_template.py` finds a dependency's version, and — the part that matters most — how to extend it to an ecosystem it doesn't already cover.

## This is a template, not a fixed tool

`ECOSYSTEM_DETECTORS` in the script is a plain Python list of dictionaries. The entries it ships with (Node, PHP, Python, Rust, Go, Ruby) are **illustrative starting examples**, included to show the pattern and cover the most common cases out of the box — they are not a claim that only these ecosystems exist or are supported. A project using `[Elixir's mix.exs]`, `[.NET's *.csproj]`, `[Swift's Package.swift]`, `[JVM's pom.xml or build.gradle]`, or any other manifest format should get a detector entry added for it, the same way the existing ones were written.

## The two generic engines

Almost every manifest format fits one of two shapes:

| Engine | Fits | How it works |
|---|---|---|
| `json_fields` | Any JSON manifest with dependency info under named object fields | `json.loads` the file, then check each listed field (e.g. `dependencies`) for the package name as a key. Exact — no regex heuristics. |
| `regex_manifest` | Anything text/TOML/line-based | Substitutes the (already-escaped) package name into a regex template via `{pkg}`, searches the whole file, and takes the first non-empty captured group as the raw version spec. |

**Adding support for a new ecosystem is almost always: pick whichever engine fits, write one dict entry, done.** No new Python function required. This was deliberately tested while building this skill — an Elixir `mix.exs` detector was added as a pure data entry with zero changes to the engine code, and it worked immediately.

### Example: adding a new `regex_manifest` entry

```python
{
    "name": "elixir/mix (mix.exs)",
    "type": "regex_manifest",
    "glob": "**/mix.exs",
    "pattern": r'\{{:{pkg},\s*"([^"]+)"',
},
```

### Gotcha: escaping literal braces in a `regex_manifest` pattern

The `pattern` string is run through `str.format(pkg=...)` to substitute the package name, which means **any literal `{` or `}` the target syntax itself uses must be doubled** (`{{` / `}}`) or `str.format` will raise `ValueError: unmatched '{' in format spec`. This bit the Elixir example above directly during testing — Elixir's tuple syntax `{:pkg, "1.0.0"}` needed `\{{:{pkg}` rather than `\{:{pkg}`. Languages whose dependency declarations use literal braces (Elixir, Scala sbt, JSON-like TOML tables) will hit this; languages that don't (Go, Ruby) won't.

### When neither generic engine fits

If a format needs real structural parsing — XML (`pom.xml`), YAML with non-trivial nesting, anything where a regex would be too fragile to trust — write a small dedicated function instead, following the same signature as the two generic engines:

```python
def run_my_new_engine(entry, package_name, project_root):
    """Return a list of (file_path, raw_spec) tuples."""
    ...

ENGINES["my_new_type"] = run_my_new_engine
```

Then reference `"type": "my_new_type"` in the `ECOSYSTEM_DETECTORS` entry. This is the escape hatch for the genuinely unusual case — most real-world additions won't need it.

## Monorepo and polyglot-repo handling

The script globs `**/<manifest>` from the project root for every detector, so it naturally finds every package's manifest in a monorepo — and every ecosystem's manifests in a polyglot repo (e.g. a Node frontend next to a Python backend) — without needing to parse workspace configuration (`workspaces` in package.json, `[workspace]` in Cargo.toml, `pnpm-workspace.yaml`, etc.). It just checks everywhere a matching manifest exists. This is deliberately simple: parsing every workspace-config format correctly is a bigger job than the version-conflict check needs, and globbing broadly errs on the side of finding *more* potential conflicts, not fewer.

The tradeoff: it will also pick up manifests that aren't actually part of the workspace (e.g. an unrelated example app vendored into a subfolder). If a reported "conflict" looks spurious, check whether the flagged manifest is actually part of the project before escalating it to the user.

## Version string normalization caveats

`normalize_version()` extracts the first thing that looks like `1.2.3` out of a raw spec (which might be `^1.2.3`, `>=1.2.3,<2.0.0`, `~1.2`, etc.). This is a heuristic:

- Range specs (`>=1.0,<2.0`) only report the *first* bound, not the actual resolved version — if you need the exact resolved version rather than the declared range, check the lockfile (`package-lock.json`, `Cargo.lock`, `poetry.lock`, `go.sum`, `Gemfile.lock`) instead of the manifest.
- Pre-release/build metadata suffixes (`1.2.3-beta.1`, `1.2.3+build5`) are captured as part of the version string, which is usually what you want for the cache version-check logic, but be aware it means `1.2.3` and `1.2.3-beta.1` are *not* treated as identical.
