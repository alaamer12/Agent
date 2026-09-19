# Enhancement Categories

Use these as the lens for scanning each file. A finding's `Category` field in the report should
be one of these (or a close variant if genuinely needed).

## Color / Iconography
Icons or UI elements that share one flat color when distinct color-coding would aid scanning,
grouping, or recognition (settings lists, category tags, status indicators). Also: color used
inconsistently for the same semantic meaning across a flow (error is red on one screen, orange
on another).

*Good-pattern reference:* a settings list where each row's icon gets its own distinct accent
color (lock = blue, eye = teal, shield = orange, location = amber, ...) instead of one flat
gray for every icon. The color itself carries no extra meaning beyond helping the eye group and
scan rows faster — that's the bar a color/iconography fix should aim for.

*Contrast & accessibility as a visual-quality issue (not a compliance audit):* text or icons
that fail basic legibility against their background are a real visual defect, checkable and
material. Rough minimums worth flagging when clearly violated: body text ~4.5:1 contrast
against its background, large text/icons/controls ~3:1. Also flag when color is the *only*
differentiator for meaning — e.g. a chart or status list that relies on hue alone with no
shape/label/pattern backup, which breaks for colorblind users and is a real, includable finding
(not a nitpick), since it's about whether the information reads at all, not a shade preference.

## Typography hierarchy
Type that doesn't visually distinguish its own roles — headings, body, labels, and metadata all
rendering at similar weight/size with nothing to separate them at a glance — or an arbitrary,
inconsistent scale (sizes like 13px/15px/17px/19px scattered with no system) instead of a
deliberate few-step scale. Also: body text set at a line length (measure) so wide or narrow it's
uncomfortable to read — roughly 45–75 characters per line is the usual comfortable range for
paragraph text.

*What to look for:* a page where h1/h2/body/caption are all functionally the same size/weight
in the rendered output; font-size values that look picked ad hoc rather than pulled from a
scale; paragraph text stretching near-full-width on a wide viewport with no max-width/measure
constraint.

*Reject example:* "Bump this heading from 20px to 22px." (a value nudge within the same role)
*Include example:* "Headings, body, and captions across this page all render at 15-16px with
the same weight — there's no typographic hierarchy at all, so the reader can't tell what's a
heading versus a label without relying on position alone."

## Density
Screens/views that are heavy on text with no visual break — no icon, illustration, image, or
whitespace structuring to give the eye somewhere to land. Includes CLI output that dumps large
amounts of text/data with no visual grouping.

*Good-pattern reference:* an onboarding flow where each screen pairs a colorful hero
illustration in the upper section with a short plain-text block below, rather than a screen
that's all text top to bottom. The illustration doesn't need to explain everything — it just
needs to exist, so the screen doesn't read as a wall of text.

*Validation heuristic — the squint test:* mentally blur the rendered layout. Do the major
groups and the primary reading order still stand out as distinct clusters, or does everything
blend into one undifferentiated block? If related items aren't visually closer together than
unrelated ones, that's a real grouping/density problem — not just "add more whitespace
somewhere."

## Hierarchy
Multiple elements competing for attention with no clear primary action, or an important element
(CTA, key metric, alert) that doesn't visually stand out from secondary content.

*Validation heuristic — the skeleton test:* before including a hierarchy finding, mentally
strip the copy/text out of the section. Does the bare layout alone still communicate what's
important and why, through structure and visual weight rather than words? If it only works once
the actual text comes back, the "hierarchy problem" is really just font-size doing the work —
that's often a signal the finding is more cosmetic than structural. Use this to decide whether a
hierarchy finding clears the materiality bar or should be reworded/dropped.

## Visual noise / overstimulation
The opposite failure mode from Density — not too little visual interest, but too much
competing for attention at once: oversaturated colors used everywhere instead of as accents,
multiple elements all styled bold/large with no restraint, heavy decoration (shadows, gradients,
borders) stacked on top of itself, or excessive/gratuitous motion. The result is a screen that's
tiring to look at and where nothing actually stands out because everything is shouting.

*What to look for:* every button/card/element using full-saturation color instead of a few
accents against a neutral base; three or more heavy visual treatments stacked on the same
element (shadow + gradient + border + glow); animations that trigger on every interaction with
no clear purpose.

## Content robustness / overflow handling
Existing elements that visually break, clip, or misalign once real content (not the short
placeholder text used while building) is dropped in — long user names, long strings without
spaces, empty values, very short values, or right-to-left text. Also covers the same failure
mode across **viewport/device sizes**: layouts using fixed pixel widths with no reflow, elements
that overlap or get clipped at smaller viewports, or touch targets too small to tap reliably on
mobile (roughly 44×44px is the usual comfortable minimum). Both are the same underlying issue —
code that renders fine under one assumed condition (short text, or one screen size) but breaks
under a realistic range of actual conditions. This is about code that already exists and
already renders — it just hasn't been checked against real content or real device ranges.

*What to look for:* fixed-width containers with no truncation/ellipsis/wrap handling around
user-generated or dynamic text; layouts that assume a specific text length and would visibly
break with a longer or shorter real value; text/number formatting that ignores locale (raw
numbers with no separators, hardcoded date formats); no truncation strategy on long single-word
strings (URLs, emails, IDs) that would overflow their container; fixed-pixel layouts with no
media queries/container queries that would visibly break or clip at common breakpoints; tap
targets sized for a mouse cursor rather than a finger.

Note the distinction from the out-of-scope "missing states" rule: a container that exists and
renders, but breaks visually under long content or a smaller viewport, is an existing-code
defect — in scope. A state that has no code path at all (e.g. no error UI exists anywhere) is a
missing state — out of scope for this skill.

## Motion / Feedback
State changes (loading, success, error, selection, drag) that exist in the code's logic but
have no accompanying visual transition or feedback, making the interface feel static or
unresponsive. (Only in-scope when the state already exists in code — see SKILL.md's
out-of-scope note on entirely missing states.)

Motion is a first-class enhancement in its own right, not just an accessory to fix once
something else is addressed. A component can clear the materiality bar for Motion independently
of any other category — e.g. a text-heavy card can separately warrant a Density fix (add an
illustration) *and* a Motion fix (add a hover/reveal transition); one doesn't substitute for or
depend on the other. Don't hold back a real motion finding just because the same element already
has a finding in another category.

*Good-pattern reference:* a profile avatar with a small decorative ring/pulse or status
indicator anchored to it, rather than a bare static image with nothing to draw the eye or
signal state. A small anchored effect like this is often enough — it doesn't need to be a big
animation to qualify as a real motion/feedback enhancement.

*Timing guidance for Type A motion fixes* — pick duration by what the motion is communicating,
not by feel:

| Duration | Use |
|---|---|
| 100–150ms | Immediate feedback (button press, toggle) |
| 150–300ms | Routine state change (tab switch, expand/collapse) |
| 300–500ms | Layout, overlay, or view transition |

Exits should generally be faster than entrances. A proposed animation fix should also account
for `prefers-reduced-motion` — either note that the fix should be gated behind that media query,
or that existing motion in the codebase already handles it and the fix should follow the same
convention.

## Structural decomposition
A single view holding more visual/informational content than it can present clearly — long
tables, dense dashboards, multi-purpose screens — that would read better split across multiple
views, tabs, or pages. Applies equally to web and CLI/TUI surfaces.

## Visual-language consistency
One part of a flow/app uses a visual pattern (color-coding, iconography, spacing rhythm,
illustration style) that other equivalent parts don't, creating a jarring or unfinished feel
across otherwise-similar screens.

*Good-pattern reference:* a multi-screen onboarding carousel where every screen follows the
identical layout skeleton (gradient hero + illustration + heading + short body + CTA button) —
only the color and illustration subject change per screen. That repetition is what makes a
multi-screen flow feel like one designed product instead of stitched-together pages.

## Empty / edge-state polish
Where an empty, zero-result, or error state *already has code/markup for it* but is visually
thin (plain text only) compared to the rest of the app's visual language. (Do not flag
empty/error states that don't exist in code at all — that's out of scope; see SKILL.md.)

---

Every finding should map cleanly to one of these categories. If a finding doesn't fit any of
them, reconsider whether it's actually a visual/UX finding or something else (a11y-only,
functional bug, performance) that belongs to a different kind of review.
