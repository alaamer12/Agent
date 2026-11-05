# How versions work

The version-number policy: what the string means, when it moves, who moves it, where it is written, and what travels with it.

- **Pattern (shape, never a live value):** `<MAJOR>.<MINOR>.<PATCH>.dev<N>` - a SemVer-shaped base (spec: https://semver.org) plus a monotonic `.devN` build tag. What the current version IS comes from the declaration sites below, never from this file - a version number written here is stale the moment anyone bumps.
- **Bump rule (written, not probabilistic):** every change that requires a rebuild bumps `.devN` by one; the base MAJOR/MINOR/PATCH moves only on an explicit user request. Guessing the bump kind from a change's "feel" is forbidden.
- **Who bumps:** `.devN` - the agent, by the written rule (mechanical); base MAJOR/MINOR/PATCH - explicit user request only.
- **Build/sequence code:** `.devN` strictly increasing, never repeated or decremented (stores and package managers reject repeats).
- **Dual versioning - the scheme, explained operationally:** this project carries TWO version shapes for TWO audiences.
  - *Public base* `<MAJOR.MINOR.PATCH>` - what users, the stores, and the About screen see; it changes only per section 3's bump rule and reads as a release.
  - *Internal build tag* `<base>.devN` - what CI artifacts, file names, logs, and device telemetry carry; it identifies one rebuild for regression hunting (a field report names the exact `.devN`).
  The mapping: `canary` builds (§3.1) ship tagged with `.devN` everywhere; a `main` release cut (§3.2) ships the bare base and the `.devN` never appears on a user-facing surface. Both numbers live at the declaration sites; this section owns only the scheme.
- **Declaration sites:** the number has more than one writable home, so it is a sync block - the
  homes and anchors are tabled in **section 19**; this section owns only the rule that a bump moves
  every row in the same change. The About screen READS the runtime value - a version string
  hardcoded in UI is a section 14 violation.
- **Attachments:** defined per subsection below; a bump that does not move each attachment its kind
  requires is a half-done bump.
- **Procedure:** Read: `docs/versioning.md` - the file-by-file checklist (this section stays obligations
  + pointers).

### 18.1 Changelog

- Format: Keep a Changelog with the base version headings; reverse-chronological; types as the spec
  defines (added / changed / deprecated / removed / fixed / security).
- Which bumps get an entry: one entry per release cut (a base version moving to `main`); `.devN` bumps
  add no changelog line. File: `CHANGELOG.md`.
- Voice: user-facing effect, not commit replay; every entry under its version heading.

### 18.2 Release notes

- Audience: survey teams/users, not diffs; publish to the in-app release banner and the store listing.
- Template pointer `docs/templates/release-notes.md`: none created yet - pending, do not fabricate a
  format.

### 18.3 Public documentation

- Docs that state versions - installation page, offline-sync setup guide, compatibility table - are
  declaration sites too: update them in the same change as the bump. An unupdated doc is a stale
  declaration site (section 11).

### 18.4 Tags and artifacts

- VCS tag per release cut: `v<MAJOR.MINOR.PATCH>` on `main`; tagging is outward - ask first
  (section 12).
- Artifact naming embeds the build: the APK/MSIX carries `1.4.2.dev3` so a field device can report its
  exact build.
