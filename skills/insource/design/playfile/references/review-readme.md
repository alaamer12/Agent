# The review README — the folder's dossier

One `README.md` per wave folder is what turns a pile of HTML into a review: it tells the reviewer what to
open, tells the next iteration what was decided, and tells anyone later which decisions were *revised*.
Anatomy first, then the rules that make each section carry weight. Start from
[`../assets/folder-readme.md`](../assets/folder-readme.md).

## Anatomy, in order

| Section | Required | What it holds |
|---|---|---|
| Title | yes | `# V[n] — [theme of the wave]` — the folder's name spoken once |
| Requirements pointer | if they exist | A link block: "implementation requirements live in [path] — read before writing any code; they supersede improvisation." |
| Status banner | yes | "**Design proposal for review.** All numbers, titles and stats are illustrative design data." The honesty the screens themselves claim. |
| The idea | yes | 2-4 sentences: what this wave changes about the product's shape, in one paragraph a newcomer can read. |
| Provenance rule | yes | Which screens this wave touches, the copy-on-change rule, and where the shipped state lives ("screens enter `vN/` the first time vN changes them; until then they link to `../vN-1/`"). |
| Files table | yes | One row per `.html` in this folder: file → **what to try**, naming every force-param its row supports. The table *is* the state index — a param that renders but is not in the table is undocumented, a table row without a working param is a defect. |
| Mechanics | optional | How the wave's notable interactions actually work (view transitions, morph, reveal), at the depth a reviewer needs to trust them — not an implementation guide. |
| Identity system | optional | Token tables when this wave introduces them (brand palettes, light/dark values, the "state colors never change" rule). |
| Decisions | yes | Numbered, **dated**, one to three sentences each: what was ruled, and the reason. A reversed decision keeps its old entry marked `REVERSED [date] — see #N`; the trail is the value. |
| Open questions | yes | What the wave does not settle, phrased so an answer is a decision, not a discussion. Empty means the reviewer is being handed a claim of completeness. |
| CDN note | yes | The honest line: files load Tailwind/icons from CDNs without SRI; review artifacts only, the product renders from its own tokens. |

## The rules that give the dossier its force

- **Dates on decisions.** "Rail on the left" is an opinion; "rail on the left, REVERSED 2025-11-04 — owner
  ruled right edge, RTL reading-start" is history. Undated decisions get re-litigated every wave.
- **Reversals are entries, not edits.** Never delete a spent decision; mark it spent and point at the one
  that killed it. The list of what changed *and why it changed again* is what stops the third reinvention.
- **Params in the table, or they do not exist.** The Files table is the contract between the URL and the
  reviewer. Writing `?state=busy` in a screen and not in the table means nobody finds it; writing it in the
  table with no rendering behind it teaches distrust of every other row.
- **Requirements beat improvisation.** When a steering/spec document owns the behavior, the README links to
  it rather than restating it — one owner per fact — and the screens must match the doc, not the other way
  around. A mismatch discovered while building is a *decision entry* (change the doc) or a defect (change
  the screen), never a silent drift.
- **Provenance is stated, not assumed.** A new folder that copies everything rots in two waves: two live
  files, one decision, drift guaranteed. The rule ("link until changed; copy when editing; pull links
  back") is written in the README precisely so the *next* wave follows it without rediscovering it.

## Filled micro-example (illustrative)

```markdown
# V2 — Notifications wave

> → Implementation requirements: `.steering/v2/notify-requirements.md` — supersedes improvisation.

> **Status: design proposal for review.** All counts and texts are illustrative design data.

**Provenance.** `settings.html` enters v2 because v2 changes it; the feed still ships from
`../mvp/projects.html` and is linked, not copied.

## Files

| File | What to try |
|---|---|
| [`settings.html`](./settings.html) | Notification bands and the grouping threshold; `?state=empty` shows the first-run form; `?theme=dark` (reviewer-only — product ships light-only). |
| [`alerts.html`](./alerts.html) | The digest editor; `?filled=1` for 40-rule crowding; `?state=error` for the save-failure surface. |

## Decisions

1. **Digest is opt-out, not opt-in (2025-10-12).** Opt-in shipped at 4% uptake in the pilot; the band
   default changed.
2. **Per-channel quiet hours — REVERSED 2025-10-20, see #3.** …
3. **One quiet window shared by channels (2025-10-20).** Owner ruled: per-channel schedules read as noise
   at review; the pilot data never needed them.

## Open questions

1. Does the digest carry read-receipts? Answer decides whether `alerts.html` gains a `?receipts=on` state.

## CDN note

Tailwind/FontAwesome via CDN without SRI. Review artifacts only; the app renders these from DesignTokens.
```
