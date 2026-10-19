---
name: educate
description: Turns documentation retrieved by the Scrape skill into a pruned, project-relevant, indexed, version-aware knowledge base so the agent never has to re-read or re-search the full raw docs again. Use whenever the user asks to "learn"/"study" a library or framework's docs, wants deep or repeated work with a specific dependency's documentation, asks to build or refresh a local docs index/cache, or whenever you notice you're about to re-scrape or re-read the same third-party documentation you've already fetched. Requires the Scrape skill's output as input — if that documentation hasn't been retrieved yet, run or request Scrape first. Covers pruning raw docs, detecting the project's real dependency version from whatever manifest format its ecosystem actually uses (Node, Python, Rust, Go, Ruby, PHP, JVM, or others — a template, not a fixed list), monorepos with conflicting versions, building a searchable index, and version-aware cache reuse.
---

# Educate

## Dependency: this skill needs Scrape

Educate has nothing to work on without the **Scrape** skill. Scrape is responsible for retrieving raw documentation (crawling docs sites, reading a library's bundled docs, etc.) and handing Educate a directory of raw files. Educate's job starts *after* that — pruning, verifying, indexing, and caching what Scrape already retrieved.

Before doing anything else, confirm Scrape's output actually exists (a directory of raw scraped documentation for the library in question). If it doesn't:
- If Scrape is available as a skill/tool in this environment, run it first to retrieve the documentation, then proceed.
- If Scrape isn't available at all, stop and tell the user Educate can't run without documentation to work from — don't invent or hallucinate documentation content to index.

This skill assumes Scrape's output is a directory containing the library's raw documentation files (typically Markdown, sometimes HTML converted to Markdown), one directory per library/version. If your Scrape skill uses a different layout, adapt the paths below accordingly — the logic doesn't depend on the exact directory naming, just on having raw doc files to read.

## The workflow

```
Scrape → Prune → Verify Project Dependencies → Build Index → Register with Cache → Version Check
```

The last step, **Version Check**, is really the thing that happens on *every* invocation, including the very first one and every one after — see "Deciding whether to reuse the cache" below for why it's listed last but often needs to be checked first.

### 1. Prune the raw documentation

Immediately after Scrape hands off the raw docs, go through each file and cut it down to what's actually useful — this is judgment work you do directly, not something to hand off to a script, since "useful" depends on the project's actual setup.

The goal is to **maximize useful information density**, not to shrink files for its own sake:

- Cut boilerplate, repeated preambles, marketing copy, and verbose scene-setting that doesn't teach the agent anything it will use later.
- When documentation lists several alternatives (e.g. `npm install` / `yarn install` / `bun install`, or several supported ORMs, or multiple config formats), keep only the one that matches what step 2 below determines the project actually uses. Don't keep the others "just in case" — that's exactly the verbosity this step exists to remove.
- **Never remove a note, warning, or caveat that affects correctness** — breaking changes, required peer dependencies, platform-specific gotchas, security notes, deprecation notices. If you're unsure whether something is safe to cut, keep it; the cost of a slightly larger pruned file is much lower than the cost of silently dropping the one line that would have prevented a bug.
- Preserve code examples that are actually representative of real usage; cut redundant examples that just restate the same thing with trivial variations.

See `examples/pruning-before-after.md` for a worked example of what this looks like on a typical `Installation.md`.

Write the pruned output alongside (or in place of) the raw files — subsequent steps read from the pruned versions, not the raw ones.

### 2. Verify the project's actual dependency version

Before indexing, find out which version of the library the *project* actually depends on, so the index can be checked against the right documentation. **Don't assume the ecosystem — look at what manifest files the project actually has.** A project might be `[Node, via package.json]`, `[Python, via pyproject.toml or requirements.txt]`, `[Rust, via Cargo.toml]`, `[Go, via go.mod]`, `[Ruby, via Gemfile]`, `[PHP, via composer.json]`, `[JVM, via pom.xml or build.gradle]`, `[.NET, via *.csproj]`, `[Elixir, via mix.exs]`, `[Swift, via Package.swift]`, or something else entirely — these are illustrative examples of what exists, not an exhaustive list, and a polyglot monorepo may genuinely use several of them at once.

`scripts/dependency_version_template.py` is built around this: it's a template whose `ECOSYSTEM_DETECTORS` list ships with a handful of common ecosystems already filled in as working examples, not as the complete set of what it supports.

```bash
python scripts/dependency_version_template.py <package-name> --project-root <path>
```

If the project uses a manifest format not already in that list, **add a detector entry before concluding the package can't be found** — see `references/manifest-formats.md`. Adding one is almost always a data entry (a glob + either a set of JSON fields or a regex), not new parsing code, so this should rarely feel like real engineering work; treat "not found" as "check whether the detector list actually covers this project's ecosystem" before reporting the package as absent.

This searches **every** matching manifest under the project root (not just the first one it finds), which matters for monorepos: if `packages/a` depends on `library@4.0.0` and `packages/b` depends on `library@4.1.0`, both show up — and this holds across ecosystems too, e.g. a Node frontend and a Python backend in the same repo each get checked. **If it reports more than one distinct version, that's a real conflict — surface it to the user and ask them to unify the dependency versions rather than silently picking one to document against.** Don't just document whichever version you found first.

Once you have the project's actual version, compare it against whatever version the scraped documentation represents (Scrape should tell you this, or it's often stated in the docs themselves, e.g. a version selector or changelog reference). This comparison feeds directly into the version-check rules below.

### 3. Build the documentation index

Once the docs are pruned and the version is known, build a single index file that lets the agent jump straight to the right section instead of reading every file. `scripts/build_index.py` does this generically for Markdown docs:

```bash
python scripts/build_index.py <pruned-docs-dir> --library <name> --version <version> -o index.json
```

It walks the pruned files, extracts headings, and categorizes each section into one of: installation, configuration, api, features, usage, notes, other — see `references/index-schema.md` for the exact schema and how the categorization heuristic works. Skim the result afterward: heading-based categorization is a heuristic, not a guarantee, so re-file anything that landed in `other` but is clearly, say, a configuration section, and split anything that's miscategorized because a heading didn't use an obvious keyword.

From here on, when you need a specific piece of information about this library, read `index.json` first and jump straight to the referenced file/section — don't re-read the whole pruned doc set.

### 4. Register with the cache

Write a `.version` file into the docs directory recording which version this documentation and index correspond to:

```bash
python scripts/write_version_file.py <docs-dir> <version> --library <name>
```

See `examples/version-file.example.json` for the format. This is what lets a future invocation tell whether the cached index is still good without re-deriving anything.

## Deciding whether to reuse the cache

On any invocation where a cached index for this library might already exist, check the cache **before** doing anything else — there's no point re-scraping and re-pruning if the existing index is still valid for the version the project is using now.

```bash
python scripts/cache_version_check.py <docs-dir> <current-project-version>
```

This compares the project's current version (from step 2, re-run fresh each time — don't trust a stale reading) against the version recorded in `.version` and returns one of:

- **`NO_CACHE`** — no `.version` file found. Run the full workflow from Prune onward.
- **`MATCH`** or **`PATCH`** or **`MINOR`** — the difference, if any, is patch- or minor-level. **Reuse the existing index without asking** — don't bother the user over a version bump that's very unlikely to have changed the API surface documented.
- **`MAJOR`** — the project has moved to a new major version since the docs were cached. **Stop and ask the user** whether to keep using the existing (now possibly stale) documentation or rebuild it from Scrape onward. Don't decide this silently either way — a major version bump can mean the cached docs actively describe removed or changed behavior, so guessing wrong in either direction (needlessly rebuilding, or silently trusting stale docs) has a real cost.

The script only detects and reports the situation — it doesn't and can't ask the user itself. That decision belongs to you, in conversation, every time `MAJOR` comes back.

## Common pitfalls to check for

- **Pruning too aggressively**: if a "quick start" section is the only place a required environment variable or peer dependency is mentioned, cutting it because it "looked like boilerplate" creates a documentation gap that's worse than the verbosity it removed.
- **Trusting the first manifest found**: especially in monorepos, stopping at the first manifest file you see will miss real version conflicts between packages — or between ecosystems, in a polyglot repo. Always search the whole project root.
- **Assuming the ecosystem instead of checking**: `ECOSYSTEM_DETECTORS`' built-in entries are illustrative, not exhaustive — a project using an unlisted manifest format isn't "not applicable," it's a missing detector entry to add.
- **Treating heading-based categorization as final**: `build_index.py`'s topic classification is a starting point; skim the output, don't publish it blind.
- **Silently rebuilding or silently reusing on a major version change**: both are judgment calls that belong to the user, not a default the script or the agent should pick on its own.
- **Re-verifying the project version from a stale read**: dependencies change over the life of a project; re-run the version detection each time rather than relying on a version you determined in an earlier session.
