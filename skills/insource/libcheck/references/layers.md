# Layer driving guide

Everything the cascade needs that is not mechanical enough for the script:
how to drive each layer, what was live-tested, and worked answers.

## Layer 1 — package managers

The value of this layer is that it resolves **through the project's own
config**: `npm config get registry`, `.npmrc` mirrors/private scopes, pip's
index-url, Go's `GOPROXY`, NuGet sources. "The registry" and "what this
project resolves" are different questions; layer 1 answers the second.

Detection is a probe, not an assumption:

```bash
command -v npm bun pip cargo go dotnet gem composer    # which exist
npm view sass version                                   # then ask
```

Live-tested on the workshop machine (2026-11-16), against the same packages
layer 3 resolved — agreement was exact (`sass 1.108.2`, `@ionic/core 9.0.11`,
`weasyprint 70.0`, Newtonsoft versions list contains 13.0.4):

| Tool | Test | Result |
|---|---|---|
| npm | `npm view sass version`, `dist-tags`, `time` | works; dist-tags showed `sass` ships `rc`/`test` tags — the trap made visible |
| bun | `bun pm view sass version` | works; same numbers |
| pip | `pip index versions weasyprint` | works; prints `weasyprint (70.0)` with available versions in parens, prereleases hidden unless `--pre`; command is flagged experimental — shape can change |
| dotnet | `dotnet package search Newtonsoft.Json --exact-match --format json` | works; returns **every** version as separate entries — sort and filter stable client-side; no dates in this output |
| cargo | `cargo info grass` | binary present but the machine's rustup has no default toolchain → errored honestly. On a configured install it shows the latest version line |
| go | `go list -m github.com/gorilla/mux@latest` | binary absent here. Semantics per Go docs: `@latest` is the highest **release** tag; prereleases and pseudo-versions are not "latest" |
| gem | `gem list -r rails --remote` | binary absent here; prints all remote versions including `.rc1`/`.beta` — filter before claiming stable |
| composer | `composer show <pkg>` | absent; composer resolves per-project, so remote-wide questions belong to layer 3 for PHP |

Rules when using layer 1:
- A headline number from a PM is a **dist-tag, not a proven stable** — for a
  stable claim get the version list (`npm view <p> versions --json`,
  `dotnet package search ... --format json`) and filter with
  `references/dialects.md`'s grammar, or cross-confirm with layer 3.
- Never install, update, or authenticate from this layer. Read-only queries.
- If the project pins a private mirror, layer 1's answer is the truth *for
  that project* while layer 3 is the truth *for the world* — report both when
  they differ; that difference is usually the finding the user wanted.

## Layer 2 — Context7 or equivalent MCP

Detection is mechanical: list the session's MCP tools and look for a
library-docs server (Context7 exposes `resolve-library-id` +
`get-library-docs`; equivalents: `mcp-server-fetch` for docs pages, vendor
MCPs). If none exists, **skip the layer silently** and say so in the verdict's
provenance (`layer 2: no docs MCP connected`) — absence is normal, this layer
is convenience, not foundation.

When present: resolve the library id first, ask for current docs/version,
then **confirm anything load-bearing against layer 3** — an MCP's index can
lag the registry by days; the registry cannot lag itself.

## Layer 3 — the script

Mechanical; see `dialects.md` for endpoints and `SKILL.md` for commands.
Treat an ERROR row as a real finding (network, name, ecosystem), never as
license to fall back to memory.

## Layer 4 — GitHub

With `gh` authenticated:
`gh api repos/<slug>/releases/latest -q '.tag_name + " " + .published_at'`,
tags via `gh api repos/<slug>/tags --jq '.[0].name'`, liveness via
`.pushed_at`, death via `.archived`. Unauthenticated: the script's `github:`
route (60 req/h budget — batch deliberately). GitHub answers "is the project
alive" even when it ships no releases (docs-only repos, monorepos where the
npm package is the release surface).

## Layer 5 — docs, changelogs, blogs

Fetch in this order until the question is answered: repo
`CHANGELOG.md`/`releases` (raw.githubusercontent.com works without API
limits), the homepage link from layer 3/4 metadata, vendor blog/announcements.
This layer owns what no registry carries: EOL dates ("v8 supported until
2027-06"), LTS windows, migration banners, "the Dart Sass rewrite is the
canonical implementation now" style statements. Quote, don't paraphrase, when
a deprecation sentence decides something.

## Layer 6 — web search

Discovery queries that set up the mechanical layers:
`"<lib>" official repository`, `"<lib>" npm package name`, `"<lib> <N> release
announced"`. Snippets are leads; any number found here becomes a verdict only
after layers 1–4 repeat it. Search-first is the failure mode this whole skill
exists to kill.

## Worked run: "is Ionic still v8?" (end-to-end evidence)

1. Layer 1 (npm, no ionic project here so public registry): `npm view
   @ionic/core version` → `9.0.11`; `dist-tags` shows `next: 8.0.0-rc.2` —
   stale tag, ignored after filtering.
2. Layer 3 `resolve npm:@ionic/core`: latest STABLE `9.0.11` (2026-11-11);
   newest `9.0.12-nightly.20261116` flagged PRERELEASE-NEWEST.
3. Layer 4 `github:ionic-team/ionic-framework`: release `v9.0.11` same day,
   pushed 2026-11-14, MIT.
4. Verdict: `@ionic/core v9.0.11 stable (2026-11-11), layers 1+3+4 agree;
   v9 is the current major — Ionic 8 knowledge is outdated.`
   No docs or search needed; memory was wrong and the cascade proved it.
