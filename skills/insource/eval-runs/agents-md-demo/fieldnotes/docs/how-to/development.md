# How to develop in this project

- **Branching:** `main` (release) + `canary` (daily integration). Feature work lands on `canary`
  first; promotion to `main` is a release decision. What each name means operationally: the
  subsections below - a bare label would tell the agent nothing.
- **Versioning:** not this section's data - pattern, bump rule, sites, attachments live in section 17.
  Here a version only means: a `canary` build carries a `.devN` tag; a `main` cut is a release.

### 3.1 What "canary" is, mechanically

- Channel-selected at build time: `dotnet build -p:Channel=canary` (default in this repo's dev
  profiles); `Channel=main` produces the release artifact.
- Channel-only code lives in `Features/Canary/` and follows the `*.Canary.cs` naming; the csproj
  compiles that folder **only** when `Channel=canary` - a `main` build cannot contain it, and the
  UI layer must not reach into it directly (section 3's layer rule applies to it too).
- The app reports its channel at startup (About + log header): `canary` devices show the
  `.devN` build tag, `main` devices show the base version - field teams must be able to tell
  which build they hold without asking.

### 3.2 What "main" is, mechanically

- Release branch: protected, merge only via an approved promotion cut (section 14's ask tier for
  pushing to it); every `main` cut is tagged `v<base>` (section 17.4) and produces the signed
  store artifact - no `*.Canary.cs` code, no `.devN` suffix.
- **Promotion:** `canary` -> `main` on a human-approved release cut; "stable" = merged to `main` and
  tagged.
- **CI / release effects:** each `canary` build produces an Android APK + Windows MSIX for field
  testing; a `main` cut produces a signed release artifact.
- **Commits:** see the `commit` skill row (section 12) and [docs/commit-craft.md](docs/commit-craft.md)
  - do not restate the convention here.

### 3.1 What "canary" is, mechanically

- Channel-selected at build time: `dotnet build -p:Channel=canary` (default in this repo's dev
  profiles); `Channel=main` produces the release artifact.
- Channel-only code lives in `Features/Canary/` and follows the `*.Canary.cs` naming; the csproj
  compiles that folder **only** when `Channel=canary` - a `main` build cannot contain it, and the
  UI layer must not reach into it directly (section 3's layer rule applies to it too).
- The app reports its channel at startup (About + log header): `canary` devices show the
  `.devN` build tag, `main` devices show the base version - field teams must be able to tell
  which build they hold without asking.


### 3.2 What "main" is, mechanically

- Release branch: protected, merge only via an approved promotion cut (section 14's ask tier for
  pushing to it); every `main` cut is tagged `v<base>` (section 17.4) and produces the signed
  store artifact - no `*.Canary.cs` code, no `.devN` suffix.
