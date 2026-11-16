# Registry dialects — endpoints, grammars, traps

What `scripts/probe_registries.py` assumes about each ecosystem. Read this
before trusting, extending, or debugging the script; every "stable?" rule here
is exactly `_is_stable`'s contract.

## Endpoints (all public, read-only, no auth)

| Ecosystem | Version source | Dates from | Deprecation from | Rate limit |
|---|---|---|---|---|
| npm | `https://registry.npmjs.org/<pkg>` → `versions` keys + `dist-tags` | `time` map | `versions[latest].deprecated` string | generous |
| PyPI | `https://pypi.org/pypi/<pkg>/json` → `releases` | per-release file `upload_time` | `Private ::` classifier; yanked files skipped | ~30/min polite |
| crates.io | `https://crates.io/api/v1/crates/<name>` → `versions[].num` | `created_at` | yanked skipped; text scan of description | User-Agent required (403 without) |
| Go proxy | `https://proxy.golang.org/<module>/@v/list` | `@latest` gives the newest one's `Time` | none exists — date is the signal | generous |
| NuGet | `https://api.nuget.org/v3/registration5-gz-semver2/<id>/index.json` (gzip) | leaf `catalogEntry.published` | leaf `deprecation` / `listed: false` | generous |
| RubyGems | `https://rubygems.org/api/v1/versions/<gem>.json` (list) + `gems/<gem>.json` | `created_at` | info/name text contains "deprecat" | generous |
| Packagist | `https://repo.packagist.org/p2/<vendorpkg>.json` | entry `time` | `abandoned` field | generous |
| GitHub | `/repos/<slug>/releases` (drafts+prereleases excluded) → `/tags` fallback | `published_at`; else `pushed_at` liveness | `archived: true` | 60/h unauth; 5,000/h via `gh` |

## What counts as "not stable" — the dialects

`_is_stable` accepts only digits-and-dots after an optional `v`, minus these
ecosystem-shaped exceptions:

| Ecosystem | Prerelease spellings seen in the wild |
|---|---|
| npm / crates / NuGet | `1.2.0-rc.1`, `0.13.0-beta.4`, `9.0.0-alpha.7`, `2.0.0-preview.3`, `1.5.0-next.2`, `9.0.12-nightly.20261116`, `9.0.12-dev.11794527713.1ebd1ea1`, `1.26.0-test.3` |
| PyPI (PEP 440) | `2.0b5`, `1.0rc1`, `3.0a2`, `2.0.dev0`; **`.postN` is stable** (maintained exception in the script) |
| RubyGems | `3.0.0.rc1`, `2.0.0beta` — a letter segment means prerelease |
| Go | anything after `-` (`v1.2.3-rc1`), and pseudo-versions `v0.0.0-<utc>-<sha>` — never "latest stable" |
| Composer | tags like `v2.0.0-beta2`, `dev-main` |

Stable-but-flagged special cases (the script handles, future edits must keep):
- Go `+incompatible` (major ≥ 2 without `/vN` module path) — a real release
  but not module-aware; the date/rank logic strips the suffix before judging.
- NuGet four-segment versions (`13.0.1.0`) and lowercase/normalized forms.
- PyPI calendar-versioned projects (`weasyprint 70.0` — one number, still fine).

## Traps with live witnesses (2026-11-16 probes)

- **`sass/sass` repo ≠ Sass releases.** GitHub `releases/latest` = 3.4.21
  (2016, Ruby Sass); the repo is still active (issue/spec hosting) and has no
  GitHub Releases for Dart Sass. Correct sources: npm `sass` → 1.108.2,
  GitHub `sass/dart-sass` → 1.108.2. The script prints `-` when a repo has no
  usable release data; it never promotes a wrong number.
- **npm dist-tags lie about position, not existence**: `@ionic/core` keeps
  `next: 8.0.0-rc.2` *behind* `latest: 9.0.11` — an old rc tag from the 8→9
  transition. Tags are pointers to judge, never to trust blindly; the version
  list + filter is the ground.
- **npm `latest` can be a prerelease** (rare but real in fast-moving SDKs);
  that is exactly why "highest STABLE" is computed separately from any tag.
- **Go `@v/list` may be empty** for tagless repos (the script falls back to
  `@latest`, which then often returns a pseudo-version — flagged non-stable).
- **RubyGems deprecation is prose**: the `sass` gem says so in its
  description; no boolean field exists, hence the text scan.
- **pip index is experimental** and its output format can change; prefer
  layer 3's `/json` endpoint for stable claims.

## Extending the script

- New ecosystem = one fetcher returning the shared dict
  (`latest_stable`, `newest_any`, dates, `deprecated`, `dist_tags`, `repo`) +
  a `REGISTRY` entry + a row here. Reuse `registry_latest_stable`; never let
  a fetcher rank versions itself.
- Keep stdlib-only (no `packaging`, no `semver` libs): the workshop runs the
  deck on machines with no package guarantees. The local `_ver_key` covers
  observed dialects; exotic version schemes should be a failing test first.
- Dates must be ISO from the source. `None` stays `None` (displayed `-`);
  synthesizing a date from anything but bytes is forbidden.
- Errors surface as `ERROR <code> <reason>` rows: exit code 1 tells a caller
  some layer refused, and the reason (404 vs network vs unknown ecosystem) is
  the point of the row.
