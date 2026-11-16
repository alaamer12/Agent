---
name: visual-enhancer
description: Audits any code that produces a visual/rendered output — web components (HTML/React/Vue/Svelte/CSS), design mockups, Storybook stories, CLI/TUI output (ink, blessed, yoga-layout, raw console output), or native UI layout code — and reports concrete, substantive visual/UX enhancements. Use this skill whenever the user invokes "/visual-enhance", asks to "enhance the visual", "improve the UI/UX", "review the design", "make this look better", "check for visual issues", or points at a screen/page/component/mockup/CLI output and asks what could look better — even if they don't use the words "visual enhancer" explicitly. Triggers on both general requests ("/visual-enhance" or "check the whole project") and targeted requests naming a specific file, component, folder, or page. Do NOT use for functional bug fixes, accessibility-only audits, or requests to build a new UI from scratch — this skill is for enhancing what already visually exists in code.
---

# Visual Enhancer

Audits existing rendered/visual code and produces a written report of **substantive** visual/UX
enhancements — never a redesign, never a list of cosmetic nitpicks. Output only, no code is
modified by this skill; the user applies suggested fixes themselves.

## Scope of what counts as "visual code"

Not just web. Anything that produces a rendered/visual experience:
- Web: HTML, React/Vue/Svelte/Angular components, CSS/Tailwind
- Design artifacts: static HTML mockups, Storybook stories (`.stories.*`)
- CLI/TUI: terminal apps rendering tables/dashboards — `ink`, `blessed`, `yoga-layout`,
  `cli-table3`, raw `console.log`/ANSI formatting
- Native/other layout code where Claude can reason about the resulting visual output

Out of scope for this skill: pure logic/backend files with no visual output; flagging things
that are **entirely missing** (no empty state, no loading state at all) — that's a separate,
future skill. This skill only enhances what already exists.

## Step 1 — Determine scope

- **General** ("/visual-enhance" alone, "check the whole project/app for visual issues") →
  scan the whole project.
- **Targeted** (a file, component, folder, or page is named, e.g. "check the checkout page",
  "/visual-enhance src/components/Header.jsx") → scan only that target.

For a general scan, first build a file list of visual-code candidates (skip config, tests,
pure-logic files, node_modules, build output).

## Step 2 — Detect the stack before prescribing anything

**Mandatory, before analyzing individual files.** Read `package.json`/manifest, lockfiles, and
scan existing imports to learn what's actually available:

- Frontend framework(s) in use, CSS approach (Tailwind, CSS modules, styled-components, plain CSS)
- Existing design tokens / color variables / theme files
- For CLI projects: is `ink`, `blessed`, `yoga-layout`, or similar already a dependency? Or is
  it a bare script using `console.log`?
- Existing asset conventions (where icons/illustrations live, naming pattern, style)

**Why this matters:** the fix must match the project's real stack. If a CLI project already
uses `ink` + `yoga-layout`, a fix for a long unwieldy table can propose real `ink` tab
components. If it's a bare `console.log` script, propose pagination/chunking instead — never
silently introduce a new dependency as the fix. If a heavier dependency genuinely is the only
real solution, still propose it, but label it explicitly: `**Requires new dependency:** ink`
so the user can decide.

See `references/stack-detection.md` for the full checklist.

## Step 3 — Find candidate issues, then apply the materiality filter

Look for problems in these categories: color/iconography (including contrast/accessibility),
typography hierarchy, content density, visual hierarchy, visual noise/overstimulation, content
robustness/overflow (including viewport/responsive breakage), motion/feedback, structural
decomposition, visual-language consistency. Note that flat/plain screens (too little visual
interest) and noisy/overstyled screens (too much competing for attention) are both in scope —
don't assume the problem is always "needs more." Full criteria and before/after examples for
each category, including the skeleton test and squint test heuristics for validating hierarchy
and density findings, are in `references/categories.md` — read it before generating findings.

**Every candidate finding must clear this bar before being included in the report:**

> If the fix is "change value X to value Y within the same category" (a shade of the same
> color, a few pixels of padding, a font-weight step) — **reject it, too trivial.**
> If the fix is "add, restructure, or introduce a new visual element or pattern" that changes
> how a user reads, navigates, scans, or feels about the screen — **include it.**

Full reject/include checklist with worked examples: `references/materiality-filter.md`.
When in doubt, apply this test out loud before writing the finding down; don't include a
finding you can't clearly justify against the bar.

There is **no cap** on the number of findings in a report — include everything that clears the
bar, however many that is.

**A single component or file can legitimately generate multiple findings across different
categories.** Don't force one verdict per component. A text-heavy card, for example, might
independently clear the bar for both a Density finding (needs a supporting illustration) *and*
a Motion finding (a reveal/hover transition would help it feel considered) — these are
different problems with different fixes, and both belong in the report as separate entries if
each independently clears the materiality bar on its own terms. Don't merge unrelated findings
into one to keep the report shorter, and don't skip a real finding just because the same
lines already have another finding attached to them.

## Step 4 — Classify the fix type

Each finding gets a fix in one of three types (detailed templates in `references/fix-types.md`):

- **Type A — Code/style fix**: a real diff, ready to paste (color tokens, spacing, layout,
  CSS/JS-driven motion).
- **Type B — New asset needed**: reference how the asset should be wired into the code, PLUS a
  ready-to-use image-generation prompt built from the *project's actual* brand/colors/style
  (pull real hex values, existing asset style, naming conventions — never invent generic
  placeholder brand language).
- **Type C — Restructure/decompose**: too much visual information in one view (long tables,
  dense dashboards, cluttered CLI output). Fix respects the stack detected in Step 2 — real
  code using the project's existing libraries, or a lighter-weight fix if no such library exists.

## Step 5 — Write the report

Output to `VISUAL_ENHANCEMENTS.md` at the project root, unless the user requested a different
location. Findings are ordered by file path, then by line number (code order) — not grouped by
category. Use the exact template in `assets/report-template.md`.

Structure:
1. A summary table up top (ID, File, Lines, Category, Issue, Priority) for fast scanning.
2. One detailed section per finding: Problem → Before (ASCII) → After (ASCII) → Suggested fix
   (per the type A/B/C templates above).

Assign Priority using the triage rule in `references/materiality-filter.md` (grounded in what
actually breaks/degrades, not personal taste) — don't leave it as a gut-feel label.

## Step 6 — Wrap up

After writing the file, tell the user how many findings were reported, and briefly name the
one or two most impactful ones. Don't restate the whole report in the chat — the file is the
deliverable. Offer to open/apply fixes for specific findings if asked.
