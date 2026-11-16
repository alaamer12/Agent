---
name: libcheck
version: 1.1.0
author: Amr
specialized: none
description: "Resolve what a library actually ships TODAY - latest stable, release date, prerelease-ahead?, deprecated? - through a six-layer evidence cascade: the project's own package manager (npm/bun/pip/dotnet/cargo/go, honoring the registry it resolves against), Context7 or equivalent MCP when connected, official registries (npm, PyPI, crates.io, Go, NuGet, RubyGems, Packagist) via scripts/probe_registries.py, GitHub releases and tags, vendor docs and changelogs, then web search for discovery only. Reads full version lists and filters prereleases per ecosystem dialect, so a dist-tag 'latest' beta is never mistaken for stable. Never answers from training memory. Use before pinning a dependency, or as the version-evidence step inside techstack, thebest, pick, packages. Triggers: latest version, version check, still maintained, is X deprecated, what does npm say about X. Not for choosing the stack itself (techstack) or authoring code."
when_to_use: Any question whose honest answer changes with time - what version is current, whether a prerelease is newest-but-unstable, whether a package is deprecated - before writing version pins, stack advisories, or dependency recommendations.
argument-hint: "[ecosystem:name (npm:sass, github:ionic-team/ionic-framework, ...) or a library question]"
---

# libcheck — current library truth, from bytes not memory

## The rule

A training-memory version is a defect waiting to surface. **Every version claim
carries a layer and a date**: `@ionic/core 9.0.11 (2026-11-11, registry)` — a
number without provenance is not an answer. When asked "what version is X", the
first move is a live probe, never recall. Recall is allowed only to *seed
candidates* (which repo, which package name) that a layer then proves.

## The six layers

Run them in order; descend when the layer above cannot answer, is absent, or
disagrees. Layers 1–3 are cheap and mechanical; 4–6 cost context and settle
only what the registries cannot say.

**1. Package manager — the canonical voice.** The toolchain the project already
has answers "what version can *this* project resolve, right now", through its
own configured registry, mirror, and auth. Probe what exists first; a missing
binary is a skip, not an error:

| Tool | Query | What it answers |
|---|---|---|
| `npm` | `npm view <pkg> version` / `versions --json` / `dist-tags` / `time` | dist-tag latest, full list, publish dates |
| `bun` | `bun pm view <pkg> version` | same registry, project config |
| `pip` | `pip index versions <pkg>` | latest stable (prereleases excluded) |
| `dotnet` | `dotnet package search <pkg> --exact-match --format json` | every NuGet version — filter stable yourself |
| `cargo` | `cargo info <crate>` | latest — needs a working rustup default |
| `go` | `go list -m github.com/owner/mod@latest` | highest release tag (skips prereleases/pseudo) |
| `gem` | `gem list -r <name> --remote` | all remote versions, prereleases included — filter |

Two permanent caveats: a PM's headline number is a **dist-tag, not a proven
stable** — when the claim matters, get the version *list* and filter, or
confirm against layer 3; and `pip index` is experimental, its output shape can
change. Per-tool dialects and which were live-tested: `references/layers.md`.

**2. Context7 / equivalent MCP** — if a library-docs MCP is in the session's
tool list, ask it; it is the fastest structured source when up, and the first
thing that dies, so absence is expected — skip silently. How to detect, query,
and which alternatives exist: `references/layers.md`.

**3. Official registries over HTTP — the deterministic workhorse:**

```bash
python scripts/probe_registries.py resolve npm:@ionic/core
python scripts/probe_registries.py npm:sass pypi:libsass crates:grass \
    go:github.com/gorilla/mux nuget:Newtonsoft.Json rubygems:sass packagist:scssphp/scssphp
```

`resolve` prints the full verdict for one package; the compact table batches.
Ecosystems: `npm pypi crates go nuget rubygems packagist` (prefix `github:`
routes to layer 4). It reads **full version lists**, filters prereleases in
each ecosystem's dialect, and separates *latest stable* from *newest
release*. Endpoints, rate limits, dialects: `references/dialects.md`.

**4. GitHub** — `python scripts/probe_registries.py github:owner/repo` reads
releases (skipping drafts/prereleases), falls back to tags, and always reports
`pushed_at` + archived. With `gh` authenticated prefer it (5,000 req/h vs 60):
`gh api repos/<slug>/releases/latest -q .tag_name,.published_at`.

**5. Vendor docs / changelogs / blogs** — WebFetch the homepage, `CHANGELOG.md`
or release notes the registry metadata points at. Use when the ecosystem has
no registry here, or for what registries cannot say: EOL statements, LTS
windows, "v9 is the last release supporting X".

**6. Web search** — discovery only: finding the canonical repo/package name or
an announcement the registries don't carry. A search snippet is never the sole
source for a version number; confirm it against layers 1–4.

## Reading the output

| Field | Meaning |
|---|---|
| `latest STABLE` | highest version with **no** prerelease marker in the ecosystem's dialect |
| `newest release` | highest by semver rank regardless of stability — with its date |
| `PRERELEASE-NEWEST` | newest published is a beta/rc/nightly; the stable line lags (vue, rxjs, Newtonsoft are live examples) |
| `dist tags` | registry pointer truth: npm `latest` vs `next`/`rc`/`beta` |
| `DEPRECATED` | the registry itself says stop using this (RubyGems `sass`, npm `node-sass`) |
| `ERROR ...` | the layer refused to answer — the reason is printed, never a guess |

The two classic traps this exists to catch: **`latest` tag ≠ stable** (rxjs:
`next=9.0.0-beta.1` while stable is `7.8.2`; sass ships `rc`/`test` tags), and
**repo ≠ release** (`sass/sass` is active on GitHub yet its release line died
at 3.4.21/2016 — the living line is `sass/dart-sass`).

## Verdict format

One line per package, provenance mandatory:

```
@ionic/core — v9.0.11 stable (2026-11-11) [layers 1+3 npm agree; GitHub confirms v9.0.11] — 9.0.12-nightly ahead, not stable
```

When layers disagree: report **both** values with their layer and date, name
the likelier reading (a configured PM sees what the project sees; registries
outpace docs prose; dist-tags outpace blog posts), and say what would settle
it. Never average, never silently pick.

## Boundaries

- Read-only: queries tools and fetches registries/GitHub; never installs,
  authenticates, writes lockfiles, or changes pins in a project. Recommends;
  the caller edits.
- Not a chooser: `techstack`/`thebest`/`pick` own the "which library" decision —
  libcheck is what they cite for "which version, still alive".
- Whole-project sweeps: run layer 1/3 once per dependency (batch table mode
  takes many specs); hand the audit shape to `packages`.
- Dates are as-of-fetch. A verdict older than the library's release cadence is
  stale by definition — re-probe rather than quote the previous answer.

## References

- `references/layers.md` — package-manager dialects and live-test matrix,
  driving layer 2 when an MCP exists, layer 5/6 recipes, worked Ionic run.
- `references/dialects.md` — registry endpoints, prerelease grammars,
  yanked/incompatible/pseudo-version rules, date sources, rate limits.
