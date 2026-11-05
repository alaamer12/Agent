# How versions work

- **Scheme:** SemVer (spec: https://semver.org), shape `<MAJOR>.<MINOR>.<PATCH>` - this file never
  holds a live number; the current value lives at the declaration sites below and in git tags.
- **Written bump rule - the agent never guesses the kind:** MAJOR = billing-model breaking;
  MINOR = additive feature; PATCH = fix. A change not matching the table is asked, not felt.
- **Who bumps:** the external version bumps only on a release cut, by explicit user request; the
  internal build number bumps mechanically on every merge into `beta`.
- **Dual tracks, two meanings, independent:**
  - *External* (2.3-line per section 2.1 is context, not policy) - what stores, users, and the
    About page see; moves on release cuts only.
  - *Internal build number* - a strictly increasing integer in `services/api/build.py`, seen only
    in CI artifacts, logs, and telemetry; bumps on every beta merge. A beta merge is never a
    release; neither track waits for or resets the other.
- **Declaration sites:** the number has MORE THAN ONE writable home, so it is a sync block - the
  homes and their anchors are tabled in **section 19**; this section owns only the rule that an
  external bump moves every row in the same change. The About page READS the runtime value - a
  version string hardcoded in UI is a section 14 violation.
- **Attachments:** every bump kind moves its attachments; a half-done bump is a defect -
  subsections below.
- **Procedure:** file-by-file checklist: Read [docs/versioning.md](docs/versioning.md).

### 18.1 Changelog

`CHANGELOG.md` in Keep a Changelog format (spec: https://keepachangelog.com) - one entry per
release cut, user-facing voice, never a commit replay.

### 18.2 Release notes

Same event as the changelog entry, same voice, shaped for the announcement channel; no separate
template file yet - none recorded yet.

### 18.3 Public docs

Any page stating supported versions updates in the same change as the bump - an unupdated page is
a stale declaration site (section 11).

### 18.4 Tags

Release tag `v<version>` on `main`; tagging is outward - ask first (section 12).
