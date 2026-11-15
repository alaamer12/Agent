# Changelog / Release notes

The user-facing record of what changed. The version NUMBER policy belongs to the project's
rulebook (`agents-md` §20 and its attachment subsections own the format decision - `keepachangelog
-style`, headings, bump discipline); this reference owns the READ copy: what shipping users need
to see.

## Must include

1. **Dated entries, newest first** - the release date (the day it actually reached users - ASK,
   not the build timestamp), version label per the project's §20 shape.
2. **User-effect language** - "exports now include your attachments" not `feat(export): include
   attachments`; every entry answers what changed FOR THE READER; internal-only versions get a
   one-line "no user-facing changes" or skip the entry entirely.
3. **Kinds, consistently** - [Added / Changed / Fixed / Removed / Security] (or the project's
   chosen set, cited to its own convention, not reinvented here); breaking changes and behavior
   reversals get prominence, never buried mid-list.
4. **Migration/action flags** - when a change needs the user to DO something, the entry links the
   how (docs or support), because a changelog the reader must decode is an announcement.
5. **Removals with reasons** - deleting a feature gets the honest sentence; the "quietly vanished"
   pattern is what makes users stop reading changelogs.
6. **Subscribe** - [RSS/Atom]/email feed alongside the page (the same mail route rules as
   `unsubscribe.md` apply: feeds count as non-transactional mail if opted-in via email).

## Placement

A standalone route (`/changelog`) on the web canon; app surfaces link out (redirect rule - the
store cannot ship text edits, so the app never carries its own copy). Accordion per release is fine;
a single 3,000-line block is not - the archive pages by month/year past a real size.

## Writing professionally

- Cadence is the credibility: an update promised per release means the CHANGELOG.md attachment
  duty fires on the same commit as the version bump (one owner per fact again - the file the
  changelog renders FROM is the project's changelog, published here, not a second list hand-kept).
- Empty release months: honest one-liners ("maintenance and fixes only") or nothing - fabricated
  feature prose is the catalog's over-engineering example for this type.

## Ask the user - never invent

Label shape from §20; date semantics (rollout vs build); which channels auto-publish it; who edits
the entry voice; whether internal-only versions are hidden.
