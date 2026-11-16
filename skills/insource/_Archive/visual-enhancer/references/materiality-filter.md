# Materiality Filter — Reject vs Include

This is the single most important gate in the skill. A report full of cosmetic nitpicks is
noise; a report of substantive findings is useful. Apply this before writing any finding down.

## The core test

> Does the fix change **what element exists**, **how it's structured**, or **what pattern is
> applied** — or does it just nudge a value within the same category?

- Nudge a value → **reject**
- Change what exists / how it's organized / what pattern governs it → **include**

## Reject list (do not report these)

- Shade/hue tweaks within the same color family (`dark-green` → `light-green`,
  `#4F46E5` → `#4338CA`)
- Single-digit pixel spacing/margin/padding adjustments
- Font-weight or font-size micro-adjustments that don't change hierarchy (`600` → `700`)
- Border-radius tweaks (`4px` → `6px`) with no functional reasoning
- Swapping one icon for a very similar icon in the same style/library
- Any change you'd describe as "slightly" or "a bit more/less" of something already present

If you catch yourself writing "slightly," "a touch," or "just a bit" in a finding's problem
statement, that's a signal to discard it.

## Include list (worked examples)

**Color-as-system, not color-as-decoration**
- Reject: "Change the button from blue-600 to blue-700."
- Include: "All 8 nav icons share one flat gray with no color-coding, so users can't visually
  group or scan categories — introduce a per-category accent color system."

**Density / structure**
- Reject: "Reduce paragraph line-height from 1.6 to 1.5."
- Include: "This settings screen has 12 text-only rows with no icons, illustration, or visual
  break — the eye has nothing to anchor on across a full scroll. Needs a supporting visual
  element or the content split across views."

**Hierarchy**
- Reject: "Make the CTA font 2px bigger."
- Include: "The primary CTA and three secondary text links share identical visual weight, so
  there's no clear next action — the CTA needs to visually dominate (color, size, or isolation)."

**Motion/feedback**
- Reject: "Add a 100ms ease to the existing hover transition."
- Include: "The submit button gives zero visual feedback on click before the network response
  returns — no loading/pressed state exists at all in code, and one should be added."
  *(Note: only include this if a state genuinely exists elsewhere in the app to hook into, or
  if it's a real code gap being fixed, not just "missing" per the out-of-scope rule — see
  SKILL.md Step 1 scope note. If truly nothing exists to react to, this belongs to the future
  "missing states" skill instead.)*

**Structural decomposition (including CLI/TUI)**
- Reject: "Make the terminal table's column separators bold."
- Include: "This CLI prints a 40+ row flat table in one dump with no grouping — decompose into
  tabs/pages by category, using the project's existing `ink`/`yoga-layout` dependency (or,
  absent that, chunked/paginated output)."

**Visual noise / overstimulation**
- Reject: "Reduce the button's box-shadow blur radius from 8px to 6px."
- Include: "Every card on this dashboard uses full-saturation background color plus a drop
  shadow plus a gradient border — nothing reads as more important than anything else because
  everything is maximally styled. Needs a neutral base with color reserved for 1-2 accent
  elements."

**Content robustness / overflow**
- Reject: "Increase the max-width of the username field by 10px."
- Include: "The user-name badge has a fixed 120px width with no `text-overflow: ellipsis` or
  wrap handling — any name longer than ~14 characters will visibly overflow its container and
  collide with neighboring elements."
- Include: "This layout is fixed at 1024px with no media queries — on a 375px mobile viewport
  the sidebar and content overlap instead of stacking."

**Typography hierarchy**
- Reject: "Bump this heading from 20px to 22px."
- Include: "Headings, body, and captions across this page all render at 15-16px with the same
  weight — there's no typographic hierarchy at all, so the reader can't tell what's a heading
  versus a label without relying on position alone."

## Priority — how to assign it

Ground Priority in what breaks or degrades, not in personal taste:

- **High** — the issue actively breaks the visual experience for realistic content/usage
  (content robustness overflow, a screen so dense or noisy it's hard to use), or is a
  consistency break that makes the product feel unfinished across multiple screens.
- **Medium** — a real, material issue (per the filter above) that doesn't break usability but
  clearly falls short of the rest of the product's visual quality — e.g. one screen lacking the
  color-coding pattern every other screen has.
- **Low** — a genuine, material enhancement opportunity that's more "nice to have" than
  expected — e.g. an already-functional screen that could gain a supporting illustration.

Never assign High to something that's actually cosmetic — if you're tempted to mark a shade or
spacing tweak as High priority, that's a sign it shouldn't have passed the materiality filter
in the first place.

## Edge cases

- **Accessibility-adjacent findings** (contrast ratio too low to read, icon-only buttons with
  no label) are in scope *only* when framed as a visual/UX enhancement, not as an a11y audit —
  this skill isn't a compliance tool.
- **Consistency findings** across multiple files (e.g. "screen 2 and 4 use icon color-coding,
  screen 1 and 3 don't") are always material — inconsistency itself is a real, includable issue.
- When genuinely unsure whether something clears the bar, err toward excluding it. A shorter,
  higher-signal report is more useful than a long one that trains the user to skim past findings.
