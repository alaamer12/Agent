---
name: accessible
description: Transforms crowded, noisy, visually overwhelming UIs into calm, readable, professional interfaces at one of three intensities: lite (type/spacing in place), medium (redistributes and relocates content), ultra (full re-theme, re-structure, and re-derived information architecture). Use when someone shares an existing UI — HTML/CSS, React, Vue, a screenshot, a mockup, an admin panel, a dashboard — and asks to make it cleaner, more readable, less cluttered or noisy, more professional, easier on the eyes, or accessible; or names a lite/medium/ultra pass. Also handles whole-codebase work: /accessible taste and /accessible snippet, rolling a pass across many pages with a generated map and an audited review ledger, verifying nothing broke against a real pre-redesign build, and grading which mode was actually delivered so an Ultra request is never quietly answered with a re-skin. Refactor/redesign only, not from-scratch. Framework-agnostic.
---

# Accessible

Turn a crowded, noisy UI into one that is calm, scannable, and professional — without losing any of the information it carries.

## Read the right reference before you act

This file is the decision procedure. The reasoning that makes each step correct lives in `references/` and loads on demand — a full pass should pull three or four of them, not all nine.

| when | load |
|---|---|
| the person says `taste` or `snippet` | `references/commands.md` |
| before diagnosing anything | `references/prior-pass.md` — is this already a pass, possibly your own? |
| applying any move | `references/moves.md` — read the moves your mode includes, in full |
| at Ultra, before building | `references/ultra-judgment-calls.md` |
| judging whether it is actually calm | `references/comfort-ceilings.md` |
| verifying (every mode, mandatory) | `references/render-verify.md` |
| the input is a running app | `references/verification.md` + `references/stack-profiles.md` |
| the input is dozens of pages | `references/rollout.md` + `references/subagent-prompts.md` |
| before claiming a mode was delivered | `references/mode-audit.md` |
| any script's flags, traps, or what a metric means | `references/tooling.md` |

## The one rule about how everything here is written

**These principles are illustrative, not a fixed visual style or markup pattern.** No font, palette, framework, templating syntax, or component shape is mandated. Every concrete snippet in `examples/` and `references/` is marked as one instance among many — never copy a class name or component structure out of them into an unrelated project. Reason from the structural description and express it in whatever the input's own language and styling system already is. If you come away thinking "so I write a `<div class="yield__bar">`", that is the wrong takeaway; the right one is "so I replace a concatenated stat string with a proportional visual plus a compact legend, built however this codebase builds small visuals."

## Modes — always required, always explicit

Determine the mode before any work. If the person hasn't said, ask; don't guess or default silently. Give a one-line description of each, don't over-explain.

- **Lite** — typography, spacing, visual encoding and micro-polish, applied *in place*. Layout regions, page count and navigation stay exactly as they are. Small structural growth is fine where it replaces something already there without moving it (a run-on stat becoming bar+legend in the same cell). What is fixed is *where on the page* each piece lives. **Always one file/page.**
- **Medium** — Lite plus redistributing and relocating within the page: new visual forms for the same data, rows restructured internally, warnings pulled into their own zone. Same brand feeling and colour direction; internal layout is fair game. **Usually still one page** — splitting is a judgment call made only when the content has clearly outgrown one hierarchy.
- **Ultra** — Medium plus a full re-theme and re-structuring at every level, **including the level above the page**: new palette, new visual language, multi-page output, and a re-derived information architecture (nav grouping, category names, route paths). **Default to multiple pages/files**; staying single-page is the exception and must be justified in a sentence.

Once confirmed, don't re-ask or hedge mid-task. A named mode is sufficient authorization for everything it implies, including adding pages or restructuring navigation at Ultra.

Where "page" means whatever the actual output format's equivalent is — a second file, a route or screen in a component app, a tab or panel in a design tool, a terminal view — not literally a second `.html` file. `examples/mode-*-fullpass.md` show what a complete pass at each mode looks like assembled, and each names how that mode silently drifts wrong.

**Two discriminators, and they are the two most common ways this skill fails.** An Ultra result that stayed one file with a new palette and tidier sections is a Medium result mislabeled. And an Ultra pass over an app that leaves the navigation grouping and every route name byte-identical to the input has not done the structural move — however complete the palette, spacing and page-split work turned out to be. Catch both before delivering, not after being told.

## Diagnose first: what "crowded" actually means

Name which of these apply, and which the chosen mode will actually address. Lite legitimately leaves some unfixed — say so rather than quietly under-delivering or reaching past the mode.

1. **Flat information hierarchy** — everything at one visual weight, so reading is required where glancing should work.
2. **Text standing in for visual encoding** — proportions, statuses or trends as run-on strings instead of shapes.
3. **Inline overflow** — warnings and secondary metadata crammed in with the primary content.
4. **Undifferentiated repetition** — many same-weight small elements with no grouping or priority.
5. **Harsh, cramped typography and spacing** — and note this runs both ways: too little contrast is illegible, too much is fatiguing. A minimum-only check waves the second through.
6. **No fixed zones for action** — controls scattered rather than in predictable places.
7. **Flat depth** — every surface on one plane, thin borders the only separator.
8. **Chart-junk** — charts carrying decoration rather than legible signal.
9. **Placeholder-style icons** — ad-hoc glyphs or emoji where a real icon system belongs.
10. **Name/content mismatch** — a heading, label or page title that promises one kind of engagement and delivers another ("Overview" over a dense table, "Quick actions" with a dozen multi-step controls). Flawless layout still misleads.
11. **Inherited taxonomy** — the app's *grouping* was decided once and only appended to: a catch-all bucket ("Settings", "Misc", "Other") whose members share a technical fact rather than a job, wildly unequal sibling sizes, nav disagreeing with the permission taxonomy, and route paths carrying the same misnomer into every bookmark and analytics report. Invisible to a page-at-a-time pass.

## The moves, by lowest mode

Full reasoning for each in `references/moves.md` — read yours, don't work from this index.

**Lite** — open up typography and spacing (the primary move; push further than a first instinct suggests) · replace concatenated-text stats with visual encoding · promote inline warnings to their own block · give actions fixed, predictable zones · strip chart-junk · use a real icon system where it earns its cost.

**Medium** — redistribute the same data into multiple projections, not multiple copies (the move that decides whether you reduced noise or just restyled it) · one job per row/card · fold non-scanned values into plain text, keep scanned values distinct · split into zoom levels sized to content.

**Ultra** — rebuild the palette as a tonal ramp weighted by dwell time · add real depth (a designed elevation system, not nudged shadows) · split into a real multi-page product · **re-derive the information architecture**.

## Preservation — every mode, no exceptions

- **Every data point.** Reorganized or re-projected, never dropped.
- **All interactive affordances** and their underlying behaviour and semantics.
- **Content and copy**, except where the original text *was* the noise. Never reworded to change meaning.
- **Brand and visual identity — the "same website" feeling.** The one requirement that spans all three modes including Ultra: a returning user should recognise the product. Ultra may change every hex and page count and still satisfy this by keeping the name, wordmark, navigation vocabulary and the spirit of the identity colour intact somewhere prominent — concentrated, not smeared.

## Verify by rendering — mandatory, every mode

Reading the markup you wrote is not verification. **No pass is delivered until it has been rendered, measured, looked at, and re-checked** — and this applies to each `taste` direction individually, not just a single-file pass.

1. **Measure** — `node scripts/accessible-audit.mjs <file-or-url> --out report.json --shot render.png`. For measured rather than declared contrast, `scripts/accessible-contrast.mjs`. For one comparable number, `scripts/accessible-score.mjs`.
2. **Look at `render.png`.** Do not skip this and trust the numbers. The script cannot see a chip whose text spills into the name beside it, a wrapped filter row, a sticky bar over the last row, a heading reading as decoration. Name what's wrong in your own words.
3. **Answer the mode checklist item by item**, pass or fail — not a summary sentence claiming you checked. Checklists and the comfort-ceiling gates: `references/render-verify.md`.
4. **Fix, re-render, re-check.** After three loops without converging, stop and report which items remain unmet rather than quietly delivering.
5. **Grade the mode** — `node scripts/mode-audit.mjs --requested <mode> --profile <stack-profile> --before <original tree> --after <current tree>`. It measures which mode was actually delivered from the diff and exits non-zero if that is below what was asked. **Nobody should have to ask for Ultra twice.** Details and the profile requirement: `references/mode-audit.md`.

**If the input is a running application, a second loop is mandatory**: a real pre-redesign control build, a proven-authenticated session, a route walk diffed against the original, a source diff read for dropped behaviour, and a functional checklist handed to the person. `references/verification.md`. **If it is dozens of pages**, snapshot the behaviour surface before editing anything and run the rollout sequence: `references/rollout.md`.

## Workflow

1. **Determine the mode.** If unstated, ask.
2. **Look at the actual input** — read files fully or examine a screenshot closely for real sizes, spacing and colour relationships. Reuse and extend any existing token system, except at Ultra where the token layer is being rebuilt. As part of the same look, read every section/page name against what is under it (failure 10) and, for an app rather than a page, write out its navigation grouping as one list (failure 11) — an inherited taxonomy is not visible one page at a time.
3. **Check whether the input is already a prior pass** — this conversation's own earlier outputs first, then the input's shape (`references/prior-pass.md`). If it is, stop and report that with the specific evidence and offer a genuinely different direction derived from this input's constraints, rather than diagnosing it as freshly crowded — unless their request already specifies a new direction or wants more of the same.
4. **Diagnose** against the eleven failures; state which apply and which this mode will address.
5. **At Ultra**, name the highest-effect judgment calls before building — working-surface light/dark; chrome's position; chrome's colour; single- vs multi-page split; **the information architecture**; how far the type/spacing scale goes. Recommend each from what the input signals, state it, proceed while inviting a quick correction. The IA call is the one to pause on: it outlives every other decision and the person knows which jobs their users do.
6. **At Medium/Ultra**, list the questions the crowded view answers at once before writing markup. At Ultra this is where the page-split and IA calls get applied — not implicitly, by seeing what fits once built. Audit for one-job-per-unit across the planned rows and cards.
7. **Build the token layer first** (ramp at Ultra; type and spacing scale at every mode), then rebuild region by region. **For dozens of pages**, run the rollout sequence instead: snapshot before editing, generate the map, freeze the shared layer and pilot on two or three pages, then wave the rest out with explicit file ownership and per-batch ledger records — and audit the ledger before quoting any count from it (`references/rollout.md`).
8. **Check preservation** — every stat, link and control still present somewhere; brand still recognisable.
9. **Run the render-verify loop** (above) until clean, then **grade the delivered mode** before writing the report. If it comes back below what was asked, either do the missing move or deliver under the mode it reached and name the unmet criterion.
10. **At Ultra, before delivering** — confirm output is multiple pages or the exception is stated in one sentence; the light/dark call was applied and not quietly reverted; any new name ("Overview", "Summary") matches what landed under it. Every item confirmed against a rendered screenshot you actually looked at, with ceiling and halation counts at zero on the working surface (chrome scoped out with `--exclude`). If you cannot state what the render showed you, you have not verified it — say so rather than implying you did.

## Resources

`references/` — the reasoning, loaded per the table above. `scripts/` — measurement, verification, and rollout tooling (see `references/tooling.md`). `assets/` — `taste-picker-template.html`, regenerated per `taste` run, and `stack-profiles/*.json`, starting points to copy and fix; none of them is your stack.

`examples/` — each file isolates one move, described by **structure and reasoning** rather than a markup shape to copy: `stat-encoding.md` (text stats → visual encoding) · `inline-warning.md` (cell-crammed warning → full-width callout) · `pill-vs-text.md` (scanned-across vs confirmed-within values) · `dwell-time-palette.md` (regional colour weighted by attention, incl. chrome position/colour) · `chart-ink.md` (chart-junk removal) · `one-job-per-row.md` (a unit doing one job vs many) · `rerun-detection.md` (recognising input that is already a pass, incl. your own, and re-approaching rather than patching). The three `mode-*-fullpass.md` files assemble several moves at whole-pass granularity.
