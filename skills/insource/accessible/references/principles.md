# Accessible: principles deep-dive

This expands the reasoning behind each move in `SKILL.md`. It stays deliberately free of any single worked example — see `examples/` for varied, short before/after snippets across different UI styles instead. Applying a principle from here should never mean reproducing the look of any one example; the point is the underlying reasoning, applied fresh to whatever input is in front of you.

## Why "add a dashboard" isn't the same as move 1

The easiest way to fake a restructure is to leave the original crowded view untouched and bolt a summary panel on top of it. This looks like progress (there's now a chart!) but doesn't reduce noise, because the detail view is still trying to answer every question at once. The tell that move 1 actually happened: after redistribution, the detail rows/cards are measurably *lighter* than before — not because information was deleted, but because it now has a better home. If your redesign's detail view still carries the same number of distinct facts per row as the original, move 1 didn't happen yet, no matter how nice the new summary section looks.

A useful discipline: write the question list out as literal sentences before writing any markup ("is everything healthy," "what's the trend," "which item is the outlier," "what's the composition," "what exactly needs fixing on this one item"). If you can't articulate the questions, you can't tell whether your projections actually answer them or are decorative in the same way a bad chart is decorative (see move 11).

## Why "one job per unit" needs an explicit audit, not just intuition

It's easy to *feel* like a redesign is decluttered because the colors are softer and the padding is bigger, while the actual informational density per row hasn't changed. The audit is mechanical: for each unit (row, card, list item) in your plan, write down the list of distinct things it tells the user. If that list is long, the unit hasn't actually been simplified — it's just been restyled. Headers are a common place this slips: a card header that carries a title, a subtitle, a filter control, and two buttons is doing four jobs, however clean its typography looks.

## The scanned-vs-confirmed distinction (move 3), generalized

This distinction generalizes past pills/tags specifically: the same test — "does the user compare this value *across* many items, or only *check* it within one item" — applies to any visual treatment decision. Values compared across items benefit from a consistent, distinct visual object (so the eye can jump from row to row and immediately spot the different one). Values only checked within one item don't need that distinctness; giving them the same visual weight as scanned values is itself a form of noise, because it makes everything look equally important to scan, when only some of it is.

## Sizing zones to content, not to a grid (move 4)

A common failure when applying "split into zones" mechanically is forcing every zone into a uniform grid (always 50/50, always 3 equal columns) regardless of what's inside. The right test is: does this region's content need more or less room to stay legible at the type scale you've chosen? A dense trend line squeezed into a narrow column becomes illegible before its container is even "small" in absolute terms; a single dominant number with a short legend looks lost in a wide container. Let the content drive the ratio.

## The dwell-time palette split (move 8), generalized past "dark vs light"

The instinct to apply is not literally "make backgrounds light" — a UI whose primary working surface genuinely benefits from a dark theme (a code editor, a media tool, a night-mode reading app) shouldn't be forced light just because "accessible" sounds like it means bright. The actual principle is: identify where sustained visual attention lives during a session, and put the calmer, lower-fatigue treatment there, regardless of which direction "calmer" points for that surface (softened light for something that was harshly dark, or a softened dark for something that was harshly bright and glary). Put the brand's boldest, most saturated, most identity-forward color choices in chrome that's glanced at rather than read continuously. The mechanism (a fixed, regionally-scoped color vs. one global theme token) is the transferable part; "light main content" is one instance of it, not the rule itself.

The same over-narrowing happens to "chrome" itself, and it's worth naming separately because it's easy to fix the first bias (dark vs. light) while leaving this second one untouched. "Chrome" means the low-dwell-time region, full stop — it doesn't mean "a dark sidebar with an accent color," which is one instance that shows up often in examples and therefore gets over-learned as the rule. Two axes are actually independent and both open:

- **Position** — a side rail, a top bar, a bottom bar, or a floating/collapsible panel are all valid instances of "glanced-at chrome," chosen from the product's actual navigation depth and screen proportions, not from which is most familiar.
- **Color** — chrome being "bold and identity-forward" doesn't mean it has to stay a neutral dark or light tone with the brand color used only as an accent. Painting chrome in the brand's full, saturated hue as its dominant surface color is equally valid, precisely because glanced-at regions don't accumulate the fatigue that sustained saturation would cause on a reading surface. Dark-neutral, light-neutral, and full-brand-hue are three genuinely different, defensible answers for chrome's color — none is the default, and none is determined by whichever direction the light/dark call landed on for the working surface.

## Chart-ink ratio (move 11) as a portable test

This move borrows the idea of a high "data-ink ratio" from data-visualization practice: every mark on a chart should be attributable to information, not decoration. A fast, portable test while building or reviewing any chart: point at each visible element and say out loud what specific number, comparison, or fact it lets someone read. If you get to an element you can't finish that sentence for, remove it. This test applies equally to a line chart, a bar chart, a gauge, a progress ring, or a custom SVG visualization — the mechanism (name what each mark earns its place by conveying) doesn't depend on chart type.

## Icon cost-to-visibility matching (move 12) as a spectrum, not a binary

Treat "which icons deserve full custom treatment" as a spectrum, not an all-or-nothing rule: at one end, primary navigation and brand-adjacent marks are seen by every user, every session, and set the tone for the whole interface — worth the investment of a proper icon system. At the other end, a rarely-glanced-at overflow-menu icon deep in a dense table is seen briefly, rarely focused on directly, and swapped out for a properly labeled, consistently sized minimal symbol without real cost to the experience. Most real interfaces have icons across this whole spectrum simultaneously; matching the investment to where an icon actually sits on it, rather than picking one policy for the entire UI, is the point.

## Why the mode boundaries fall where they do

The three modes aren't an arbitrary three-point scale — each boundary marks a real jump in what kind of change is being made, and in what it costs to reverse or to get wrong.

Lite changes only *how existing things render* — nothing moves, nothing new is created, no navigation changes. This means a Lite pass is essentially risk-free to apply and just as easy to undo; it's pure rendering polish. That's why Lite can (and should) push type/spacing/weight further than feels natural: there's no structural risk being taken, so there's no reason to hold back on the one dimension that mode is allowed to touch.

Medium starts *moving and restructuring* things — a stat that lived in a table cell might now live in a chart elsewhere, a page might gain a new companion screen. This is reversible in principle but requires real thought about where things go (the whole reasoning behind the redistribution move), and it can affect navigation and mental models the user already has for the product. It's a meaningfully bigger commitment than Lite, which is why it's a separate mode rather than "Lite, but more."

Ultra additionally *replaces the visual system itself* — color roles, elevation, the whole token layer. This is the hardest to partially undo (there's no small tweak that reverts a full re-theme) and the easiest to get wrong in a way that damages brand recognition, which is exactly why "same brand feeling" is called out as the one requirement that spans all three modes rather than being mode-specific: it's the actual guardrail on Ultra's much larger blast radius, not a nice-to-have.

## Why explicit mode confirmation matters here specifically

Most requests in this skill's domain benefit from picking a sensible default and proceeding. Mode selection is a deliberate exception: Lite and Ultra can produce results different enough from each other that guessing wrong wastes a genuinely large amount of work — an Ultra-scale re-theme when the person wanted a quick polish is not a minor miss, and neither is a timid font-only pass when the person wanted a full redesign. The cost of asking one short question up front is small; the cost of building the wrong scale of change is not.
