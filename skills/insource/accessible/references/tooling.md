# Tooling

Three groups of scripts, three different questions. Every one is dependency-free Node ≥ 22
(global `WebSocket`) and finds a headless Chrome on its own via `$CHROME_PATH`, Playwright's
cache, then system paths — override with `--chrome`.

| question | group |
|---|---|
| is this screen calm and legible? | `../scripts/accessible-audit.mjs` and friends |
| did the redesign break the running app? | `../scripts/verify/` |
| how do 70 pages get converted consistently, and how do I know? | `../scripts/rollout/` |

Stack-specific patterns (colour utilities, token syntax, route declarations, file extensions)
are **not** hardcoded — they come from a stack profile. See `stack-profiles.md`; without one,
a measure that cannot match anything reports NOT MEASURED rather than a misleading 0.

---

## Measuring one rendered screen

Four groups, four different questions.

`mode-audit.mjs` — grades **which mode was actually delivered**, from a diff against the
original. Run it before delivery, not after being told. See `mode-audit.md`.

`accessible-audit.mjs`, `accessible-contrast.mjs`, `accessible-score.mjs` — judge **one rendered
screen**: is it calm, legible, within the comfort ceilings, comparable to a reference.

`verify/` proves a redesign broke **nothing in the running app** — real login, real data, both
builds walked and diffed. Read `verify/README.md` when the input is an application.

`rollout/` gets a pass through **dozens of pages** without the files drifting apart or the
delegated reviews becoming fiction — behaviour snapshot, generated page map, per-batch review
ledger with an audit pass. Read `rollout/README.md` when the input is a codebase.

`accessible-audit.mjs` — renders a UI in headless Chrome and measures what this skill's
moves are supposed to have achieved, so "it looks calmer" is a number you can compare
against a reference instead of a claim you have to trust.

No npm dependencies. Needs Node ≥ 22 (uses the built-in global `WebSocket` to talk
Chrome DevTools Protocol) and any headless Chrome/Chromium binary.

#$0Usage

```
node scripts/accessible-audit.mjs <file-or-url> [options]

  --out <path>        write the full JSON report (default: OS temp dir)
  --shot <path>       write a PNG of the rendered viewport
  --chrome <path>     Chrome binary, if auto-discovery fails
  --width / --height  viewport, default 1440x1000
  --exclude "<sel>"   comma-separated selectors to treat as low-dwell chrome
  --baseline <json>   print a per-metric delta against a saved report
  --json              dump raw JSON instead of the scorecard
```

Exit code `0` = clean, `1` = findings above threshold, `2` = usage/runtime error.

#$0Chrome auto-discovery

Looks for `$CHROME_PATH`, then Playwright's cache (`~/.cache/ms-playwright/chromium*/…`),
then common system paths. Override with `--chrome`:

```
--chrome "$HOME/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"
```

#$0Typical flow

```bash
# 1. measure the thing you just built
node scripts/accessible-audit.mjs build/redesign.html --out after.json --shot after.png

# 2. look at after.png. The numbers cannot see clipped text, wrapped filter rows,
#    a sticky bar covering content, or a heading that reads as decoration.

# 3. if the person already approved an output as the target, diff against it
node scripts/accessible-audit.mjs build/next-page.html --baseline after.json
```

#$0accessible-contrast.mjs — measured, not declared, contrast

```
node scripts/accessible-contrast.mjs <file.html|url> [--width 1440] [--height 1000]
                                      [--fails-only] [--json] [--csv out.csv] [--chrome path]
```

Screenshots the page, decodes the PNG in pure Node, and for every text run samples the
**surface pixels around it** rather than trusting CSS. Reports two numbers per run:

| | means | catches |
|---|---|---|
| `inner` | contrast against the dominant measured backdrop | wrong/incomplete DOM background resolution |
| `worst` | contrast against the nearest-luminance surface pixel in that region | **gradient ends, images, overlays** — a run can pass `inner` and fail `worst` |

`gradientRisk` = `inner − worst`. On a flat surface it is ~0; a large value means the text
sits on something that changes underneath it.

Three traps this script walked into and fixed, worth knowing if you extend it:
- **Anti-aliased glyph edges are not backdrop.** Sampling inside the text box makes every
  run report `worst ≈ 1.2` against its own halo. Sample a ring *around* the run.
- **That ring catches neighbouring text.** Comparing a label against the next label's
  glyphs also reports ~1.00. Restrict the worst-case scan to pixels near the dominant
  backdrop colour.
- **`oklch` and friends are not normalised anywhere readable** — resolve colour by
  rasterizing, in the page, before handing it to Node. A node-side parser silently drops
  every run on a modern palette and reports a clean page.

Exit code is the number of failing runs.

#$0Scoring and ranking

```
node scripts/accessible-score.mjs page1.html page2.html ... [--exclude ".rail,.chrome"] [--json]
```

Consumes the same audit and prints five weighted dimensions, a 0–100 composite and a letter
grade, ranked. Use it to compare directions against each other, or a redesign against its
own input.

| dimension | weight | driven by |
|---|---|---|
| Legibility | 22% | AA floor, median contrast band, smallest/median font size |
| Comfort | 24% | ceiling violations, halation, ink ratio, block rhythm, accent load |
| Hierarchy | 20% | signposts per screen, focus spread (low-confidence, capped), type steps |
| Length | 24% | effective screens (table-driven height discounted), longest unbroken run, sticky nav, distance to last control |
| Palette | 13% | competing saturated hue families, hue entropy, ramp temperature spread — **shades are rewarded, dispersion is not penalised** |
| Robustness | 10% | clipping, horizontal overflow, target sizes |

**Gates beat points.** AA floor breaches, halation on the reading surface and clipping cap
the grade outright; comfort-ceiling and *systemic* target failures cap less. Two 15px
checkboxes is a defect, not a gate — the target rule needs both a count floor and a share,
or a 13-control page trips on a denominator of thirteen.

**`--exclude` is ceiling-only.** Chrome may be loud; chrome's text must still be readable.

#$0What each metric is for

| Metric | Catches | Why this skill cares |
|---|---|---|
| `contrast.floor` | text below WCAG AA | the classic legibility check |
| `contrast.ceiling` | sustained text **above** ~14:1 on dark / ~19:1 on light | AA is a *minimum*; a palette can pass AA everywhere and still be painful. This is the check that was missing. |
| `contrast.halation` | high-chroma colour sitting on a near-black ground | the second eye-strain mechanism after raw contrast; blue/cyan/violet glow hardest |
| `whitespace.inkRatio` | share of the viewport covered by actual content | "open up spacing" as a number; climbing ink with flat gaps = density got worse, not better |
| `whitespace.medianGapPx` | breathing room between sibling blocks | distinguishes real spacing from a bigger font in the same box |
| `whitespace.densestRegions` | which container is the jammed one | a calm header can hide a 59%-ink table |
| `focus.ranked`, `hierarchySpread` | what visually dominates; top-vs-5th score ratio | flat information hierarchy = nothing wins the eye; spread under ~2x is the flag |
| `accents.coveragePct` | how much saturated colour is on screen | brand hue should be *concentrated* in chrome, not spread across every tile |
| `type.min/median/max` | the actual scale in effect | tells comfortable / large / enormous apart numerically instead of by feel |
| `hitTargets.aaViolations` | **controls** under 24×24 | WCAG 2.5.8 AA breach — counts against exit code |
| `hitTargets.belowComfort` | controls 24–44px | below 2.5.5 AAA; advisory, does not fail the run |
| `hitTargets.linkAdvisory` | text links under 24px | exempt by criteria (links in a sentence, or equivalent control elsewhere) — reported, never failed |
| `length.screens` | total height in viewport heights | soft signal only — see below |
| `length.longestWallScreens` | longest run with **no** heading/section break | **the real long-page failure**, not raw height |
| `length.lengthIsData` | is the height mostly inside `<table>` elements | long-because-data is legitimate; long-because-stacked is not |
| `length.stickyNav` | persistent orientation while scrolling | a long page with a sticky rail reads differently to one without |
| `length.tallest`, `length.repeats` | where height comes from; biggest run of near-identical sibling blocks | makes the finding actionable |
| `clipping` | overflowing text, boxes, page-level horizontal scroll | only ever visible once rendered |

#$0Why colours are resolved by rasterizing

Browsers hand back `oklch()`, `oklab()`, `lab()`, `lch()`, `color-mix()` and `color()`
**exactly as authored** — in computed styles, *and* in canvas `fillStyle`, which echoes
the string straight back. So neither string-parsing nor reading `fillStyle` normalises
them. A naive checker returns `null` for every colour, finds no violations, and reports a
clean pass on a page that is not clean — worse than no checker, because it looks like
evidence.

The only reliable resolution is to paint and read back the pixel:

```js
cx.globalCompositeOperation = 'copy';
cx.fillStyle = 'rgba(0, 0, 0, 0)';      // sentinel: setter rejects invalid colours
cx.fillStyle = str;
if (cx.fillStyle === 'rgba(0, 0, 0, 0)') return null;   // unparseable
cx.clearRect(0, 0, 1, 1);
cx.fillRect(0, 0, 1, 1);
const d = cx.getImageData(0, 0, 1, 1).data;             // true sRGB
```

If you adapt or rewrite any colour-measuring code for this skill, keep this.

#$0Reading the report honestly

- **Hard failures and advisories are separated deliberately.** The exit code counts only: contrast floor, contrast ceiling, halation, sub-24px *controls*, clipping, and length flags. Sub-44px controls, small text links, hierarchy spread, accent coverage and ink ratio are advisory — they inform a human judgement, they don't turn the run red. A page whose only findings are advisories exits 0.
- **Zero AA violations is not a pass.** Read `ceiling` and `halation` too.
- **Ceiling hits inside chrome are expected.** A saturated brand-hue rail is glanced at,
  not read, so it may carry contrast the working surface cannot. Scope it out with
  `--exclude ".rail"` rather than softening it — the fix for a harsh screen is almost
  never "quiet the bold region," it's "quiet the region people read."
- **Soft signals need a human.** Hierarchy spread, accent coverage and ink ratio are
  evidence, not verdicts. A screenshot you looked at outranks all three.

---

## Proving the running app still works

Proves a redesign didn't break anything, against the **running app** — not the markup.

`../scripts/accessible-audit.mjs` measures whether a rendered screen is calm and legible. These answer
a different question: whether the app still *works* the way it did before you restyled it.
Both are needed on a whole-project pass; neither substitutes for the other.

No npm dependencies. Node ≥ 22 (global `WebSocket`). Any headless Chrome — auto-discovered
from `$CHROME_PATH`, Playwright's cache, then system paths.

**Read `verification.md` before using these.** The scripts are simple; the
judgment about what a green result is allowed to mean is the whole point, and every trap in
that file came from a run that looked fine.

---

#$0The flow

```bash
# 0. you need the app running, and a way in. If you don't have credentials, ASK — then:
node auth.mjs --discover --root .          # where might they be? values stay redacted

# 1. get a session, and prove you have one
A11Y_EMAIL=… A11Y_PASSWORD=… \
  node auth.mjs --login http://localhost:5173/login --state session.json
node auth.mjs --probe http://localhost:5173 --state session.json   # exit 0 = logged in

# 2. sweep the redesigned build
node sweep.mjs --base http://localhost:5173 --state session.json \
  --side after --out sweep-after.json --shots shots-after \
  --values "Total Funds,Total Users,Active Funds"

# 3. sweep the ORIGINAL build the same way — same route list, same window, same account
#    (run the two builds one at a time if the API only allows one origin)
node sweep.mjs --base http://localhost:5173 --state session.json \
  --side before --routes sweep-after.json …   # reuse the list so both sides cover the same pages

# 4. diff
node parity.mjs --before sweep-before.json --after sweep-after.json --out parity.md
```

`parity.md` is the artifact to keep and to commit. It separates **regressions** (yours),
**pre-existing** (found, not caused), and the human checklist to hand over at the end.

---

#$0Scripts

#$0`browser.mjs` — shared session, no library
Not run directly. Opens Chrome with `--remote-debugging-port=0` and reads the real port back
from the profile, so a leftover instance can never be mistaken for yours; bounds every
evaluation with a timeout and a fallback, so one unanswerable page is a recorded failure
rather than a stalled run; captures `Runtime.exceptionThrown`, error/warning
`consoleAPICalled`, and `Log.entryAdded` (`source === 'javascript'` — filtering on `'js'`
silently drops all of it); and exposes `settle()` + `verdict()`, the render guard that stops
"no console errors" from meaning "the server was down".

#$0`auth.mjs` — get in, and prove it
```
node auth.mjs --discover [--root .]                       # candidate locations, redacted
node auth.mjs --login <url> [--email-env V --password-env V] [--state session.json]
node auth.mjs --probe <url> [--state session.json]
```
Fills the first two inputs using the native value setter plus an `input` event, because a
model-bound form ignores a plain assignment and submits blank. Exits non-zero and prints the
credential-acquisition order if the login doesn't take — and lists the four things to check
before concluding the app is broken.

It will not create a test user for you. That writes to someone's database; ask first
(`references/verification.md`, "Getting in").

#$0`sweep.mjs` — walk the app
```
node sweep.mjs --base <url> [--state session.json] [--side name] [--out sweep.json]
               [--crawl | --routes routes.json] [--values "Label,Label"] [--shots dir]
               [--settle 15000] [--max 120] [--ignore <regex>]
```
Either `--crawl` (collects same-origin links from the rendered navigation — the surface a
person can actually reach) or `--routes` (a JSON array of paths, so both sides cover the
identical list; parameterised paths are skipped, since `:id` is not a URL).

Per route: navigate, poll until the text stops changing, record URL/heading/node count, any
label→figure pairs you asked for, and console errors since that navigation. Three things it
will not let you pretend: a route that bounced to the login is an `AUTH` failure, not a pass;
an all-zero `--values` capture is flagged as a loading skeleton rather than trusted; and a
page only counts as rendered if the navigation succeeded **and** something that looks like
the application mounted (`--root-selector`, default `main,#app,#root,#__next,[data-v-app],#nuxt`).

That last one is load-bearing and was earned the hard way: a browser's own
connection-refused page has a heading, real paragraphs and dozens of nodes, so it clears any
text-or-count threshold. Point the sweep at a dead port and every route must come back
`NOT RENDERED` — run that check once per environment before trusting a clean sweep.

#$0`parity.mjs` — the diff and the report
```
node parity.mjs --before sweep-before.json --after sweep-after.json [--out parity.md]
```
Normalises away what varies between runs — origins, cache-busting hashes, chunk names, line
numbers — so a shared error compares as shared. Reports the four claims separately (render,
runtime, value, plus what's missing from either side), splits one-sided errors from
both-sided ones, and ends with the human checklist. Exit code is the number of items needing
a look.

---

#$0What these cannot do

- They cannot tell you the redesign is *correct* — only that it isn't obviously broken on
  first load. Mutations, permissions on non-admin roles, and long sessions are out of reach
  and stay out of the verified column.
- They cannot substitute for a real original. Sweeping the redesigned app twice and calling
  one copy "before" is not a control.
- They cannot see layout quality. That is `../scripts/accessible-audit.mjs`, and you still have to
  look at the screenshot.

---

## Rolling a pass across many pages

Getting a design pass through a whole application — dozens of pages — without the files drifting
apart, without the delegation becoming a fiction, and without losing the ability to say at the
end what was actually verified.

`../scripts/accessible-audit.mjs` measures one rendered screen. `../scripts/verify/` proves the running app
still works. These answer the middle question: *how do 71 pages get converted consistently, and
how do I know?*

No npm dependencies. Node ≥ 22. Framework-tolerant, with Vue and React recognised out of the
box for `identity.mjs`.

**Read `rollout.md` first.** The tools are simple; the order they run in and
the way their output is read is the whole method, and every default here exists because some-
thing in it went wrong during a real pass.

---

#$0The sequence

```bash
# 1. BEFORE touching anything — the only time this can be taken
node identity.mjs snapshot src/pages --out identity.json --allow-imports

# 2. the work queue, regenerated whenever you like
node map.mjs --src src/pages --snapshot ../app-origin/src/pages \
     --moves moves.json --ledger design/verification --out map.md

# 3. waves: workers convert, reviewers review, each writing its own shard
node ledger.mjs record --batch B1 --reviewer agent-A --file src/pages/x.vue \
     --status pass --note "8 columns, date filter, both row actions present"

# 4. close — is the ledger evidence, and did any logic move?
node ledger.mjs audit
node ledger.mjs summary
node identity.mjs diff src/pages --baseline identity.json
node map.mjs ... --out map.md          # regenerate, now with verdicts filled in
```

---

#$0identity.mjs — the mechanical half of "no logic changed"

```
node identity.mjs snapshot <dir> --out baseline.json [--allow-imports]
node identity.mjs diff     <dir> --baseline baseline.json
```

Hashes the logic block and collects bindings, declared emits and API call sites per file. The
diff is a **review queue, not a verdict**: renaming a route legitimately changes a string inside
a script, and a pass that reports zero changes after 70 files is more suspicious than one that
reports fifty. Classify each failure and put the classification in the ledger.

`--allow-imports` excludes import lines from the hash, because adding an import for a shared
component is normal in a redesign. The choice is recorded in the baseline and the diff **refuses
to run under a different one** — hashing one side with imports and the other without disagrees
on every converted file and reads as catastrophic breakage of pages that are fine.

Take the baseline from the original state. It cannot be reconstructed later, and a baseline
generated after the pass reports zero failures while comparing nothing.

#$0map.mjs — origin, state and review in one generated table

```
node map.mjs --src src/pages --snapshot ../app-origin/src/pages \
     [--moves moves.json] [--ledger <dir>] [--out map.md] [--ext .vue,.jsx,.tsx]
```

Four columns, each defending against a specific way a rollout lies:

| column | catches |
|---|---|
| ancestor | where a file came from, marked `_(moved)_`. Without a move table every renamed file reads "new, no ancestor" — indistinguishable from unverified work. |
| state | raw colour and palette utilities left in **markup only**. Counting class strings inside script blocks makes the gate unsatisfiable, because those are frozen data for a design pass; the number gets ignored within a day. |
| wiring | a component used in markup and never imported — renders as nothing, errors nowhere, invisible to a compile check. |
| review | the latest ledger verdict per file, with the reviewer's name. |

#$0ledger.mjs — who checked what, and whether they looked

```
node ledger.mjs record --batch B1 --reviewer name --file <path> [--file ...] \
     --status pass|fail|blocked --note "what you actually saw"
node ledger.mjs audit | summary | failures
```

One JSONL shard per batch, never one shared file: parallel appends lose lines.

`record` refuses a `pass` with a note under six words. `audit` reports reused sentences, thin
passes, files whose latest verdict is not a pass, and batch ids shared by several reviewers.
It exists because a real rollout produced 81 review records of which **36 shared a sentence with
a record about a different file** — one reviewer wrote the same paragraph for eight unrelated
pages, all `pass`, and the ledger read as "73 files reviewed and clean".

Run the audit before quoting any number from the map's review column.

---

#$0What these cannot do

- `identity.mjs` cannot tell an intended change from a mistake. It lists; you classify.
- `map.mjs` cannot see a page that is technically converted and still wrong. The review column
  is only as good as the ledger, and the audit is only as good as the reviewers.
- Nothing here verifies behaviour at runtime. That is `../scripts/verify/`, against a real control build.
- None of it survives a shared mutable design system. If the token layer changes mid-rollout,
  everything before the change is suspect and the map will not tell you so.
