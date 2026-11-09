# The transformation moves, in full

`SKILL.md` carries the one-line index and the mode gate; this carries the reasoning each move needs. Load the moves your mode includes and read them properly — the paragraphs explaining *why* a move under-delivers are the part that stops a confident, shallow pass.

## The transformation moves, by mode

Each move below is tagged with the lowest mode it belongs to; every mode includes all moves tagged at or below its own level.


### [Lite+] Open up typography and spacing
Increase base type size and line-height for anything read continuously, and give elements enough internal padding to breathe. Headings get real weight and, usually, slightly tightened letter-spacing. **In Lite, this is the primary move** — it should visibly transform the feel of the screen through type/spacing/weight alone, without touching layout, adding regions, or changing what's a pill vs. plain text. Push it further than feels natural for "just a font change": larger jumps in size and padding than a first instinct suggests are what make a Lite pass actually register as a real improvement rather than a barely-noticeable tweak.

**But "how much bigger" is a real judgment call, not a one-size answer — surface it rather than picking silently.** The right scale depends on the surface: a dense data-console table read for minutes at a stretch wants a smaller jump than a marketing page or a single-focus form. There's also a ceiling most people don't expect: past a certain point, "bigger" stops reading as "more comfortable" and starts costing scannability — a data-dense screen with everything blown up forces more scrolling and more eye travel per fact, which is its own kind of fatigue. So:

- If the person hasn't specified, state the scale you're defaulting to in one line before or alongside the pass (e.g. "opening up type/spacing by roughly 10–15% — say if you want it larger or to leave it closer to the original") rather than silently picking a number and moving on.
- If the person's own words carry an intensity signal ("comfortable," "a bit more breathing room" vs. "huge," "enormous," "can't strain to read it") or a scale reference (a specific point size, "like a book," "like a phone settings screen"), take that as the target and say so, rather than defaulting to a fixed percentage regardless of what they asked for.
- If they ask for something in comfortable/large/enormous terms without a number, treat it as a spectrum and pick a concrete point on it, named out loud: *comfortable* ≈ a restrained bump mainly to line-height/padding with type size barely moving; *large* ≈ a clearly noticeable size increase across the board, still dense-content-safe; *enormous* ≈ near accessibility/low-vision scale, where density itself may need to drop (fewer columns, more relocation) to keep the result scannable rather than just zoomed-in. Naming which of these (or where between them) you're building is more useful to them than a bare percentage.
- Rerunning this skill on a screen that already went through an accessible pass is a signal worth naming, not silently compounding: if the input already shows the hallmarks of a prior pass (a deliberate tonal ramp, generous padding, a redistributed dashboard), say so and ask whether this round should push the scale further, hold it steady and focus on other moves, or pull back — rather than treating it as a fresh crowded screen and stacking another full size increase on top.


### [Lite+] Replace concatenated-text stats with visual encoding
Any run-on stat string becomes a small proportional visual (segmented bar, ring, sparkline) plus a compact legend, in place, without moving where that stat lives on the screen. Keep the color-to-meaning mapping consistent across the whole UI.


### [Lite+] Promote inline warnings/errors to their own block
A warning crammed into a cell becomes a full-width callout: icon, bold headline claim, one plain-language sentence, a clear action. This can happen at Lite scoped to *within* the same row/unit (the warning gets its own full-width sub-block right where it was) — moving it to an entirely different section of the page, or a different page, is a Medium-level relocation (see move 1).


### [Lite+] Give actions fixed, predictable zones
Within each existing row/card/header, arrange its own actions into one consistent trailing cluster instead of scattering them — this is a local rearrangement inside a unit that already exists, not a relocation across units. Introducing a *new* shared zone that pulls actions together from multiple different rows or sections (e.g. a floating bulk-action bar that didn't exist before) is a Medium-level addition, since it changes the page's structure, not just one unit's internal order.


### [Lite+] Charts carry only what answers their question — no chart-junk
Cut any chart element that doesn't answer a specific reading — this applies even to charts that already exist in the input; a chart's own excess decoration can be trimmed without relocating the chart itself.


### [Lite+] Use a real icon system where it earns its cost
Convert identity-defining, always-visible chrome icons (nav, brand mark) to a proper icon system; be pragmatic about small repeated low-emphasis glyphs elsewhere — in place, without adding new icons or new navigation.


### [Lite+] Design the states, not only the populated view
A screen is not one view; it is populated, empty, loading, partial, zero-result, forbidden, failing, and mid-save. Find which of those the input currently renders — and which it renders as *the same thing*, usually the populated layout with nothing in it, which reads as a designed emptiness rather than a missing state. Give each one that can occur in this product its own rendering, in the place the state already appears: empty says what would be here and how to get some, loading says how long and what's happening, zero-result says which filters produced nothing and how to widen them, forbidden says who to ask, failure says what to retry and what is already saved.

This is Lite because it doesn't move anything — it replaces an absent or shared rendering with a specific one where it already lives. **The reason it is a move and not a polish item: for a new user, the empty state *is* the product**, and for a user with a typo in a filter, the zero-result state is the entire experience. A pass that redesigns only the fully-populated case has redesigned the least-visited state in the app and reported the rest as done. Note also that an error or loading state that appears *inside* a control someone is mid-using (a field's validation message, a save that failed) belongs adjacent to that control rather than in a page-level banner — see the writing-surface move, and don't fight the person's focus with a toast that covers the thing they were about to click.


### [Lite+] Keep the structure readable by more than one sense
Whatever the pass does to how a screen looks, it must not damage how a screen *is*: heading levels stay a real outline rather than a size ladder, every control keeps a name and a label that survives being read aloud, focus order follows the order the content is in, colour keeps being a reinforcement of a distinction rather than the only carrier of it, motion keeps respecting the reduced-motion preference, and anything that was reachable by keyboard is still reachable. A pass may also improve these — give an icon-only control its name, turn a clickable `div` into a button, replace a colour-only status with a shape or word — but the direction is one-way: **a defect here is not a style choice**, and it is the class of regression that photographs beautifully and is invisible in every screenshot, because the render you are looking at is one of the ways the screen can be used, not the only one.


### [Medium+] Redistribute the same data into multiple projections, not multiple copies
List every distinct question the crowded view is forced to answer at once (e.g. "is everything OK," "what's the trend," "how do items compare," "what's the composition," "which item needs action, and why"). Give each question its own purpose-built projection of the *same* data — a summary metric, a trend visualization, a comparison view, a composition view, a detail row — rather than repeating full detail everywhere. This is the move that most determines whether a redesign reduces noise or just restyles it.

**At Medium**, these projections usually live in new sections of the same page (in-page redistribution, per the mode definition above) — only extract a genuinely new page when this page's content has clearly outgrown one page's hierarchy, and treat that as the exception, not the default. **At Ultra**, default to actually extracting the aggregate-question projections (health, trend, comparison, composition) onto their own new page, distinct from the page that keeps the detail list/table — a single long page with nicely reorganized in-page sections is not, by itself, a complete Ultra outcome, even if the palette and layout within that one page changed completely. The test either mode should apply before finalizing: if this page currently tries to answer more than roughly 2 of the listed questions on its own, at Ultra that's a strong signal a second page is warranted, not just a second in-page section.


### [Medium+] Give every row/card exactly one job
Audit each repeating unit: how many distinct things is it telling the user at once? After redistribution, most units should carry 1–2 responsibilities, each in its own clear slot — this typically requires restructuring the unit's internal layout, which is why it's Medium rather than Lite.


### [Medium+] Fold non-scanned values into plain text; keep scanned values distinct
Ask, per value: scanned across many rows, or only confirmed within one? Scanned values stay distinct objects; confirmed values collapse into plain text. This changes what markup/components exist, not just their styling, so it's Medium.


### [Medium+] Split into zoom levels, sized to content
Lay out redistributed projections (move above) as distinct zones — glance → context → detail — sized to what each region's content actually needs, not forced into a uniform grid. A new shared action surface that spans multiple rows/units (a floating bulk-select bar, a consolidated toolbar pulling controls together from previously-scattered locations) belongs here too — it's a new structural region, not a within-unit rearrangement.


### [Medium+] Treat a writing surface as a surface
A form, a dialog, a wizard, an inline editor: this is where the user *does* something rather than
reads something, and it is the region every other move in this file is silent about. It is fair
game at Medium — it is rearrangement inside a surface that already exists, exactly like
restructuring a row.

- **Order fields by the decision, not by the record.** The sequence that produced the schema, the
  alphabetical order of a model, or "required first" are all orders that make someone hold the
  form's plan in their head while filling it. The right order is the one they were already thinking
  in, which is readable off the surface itself: what do they know before they can answer this field?
- **Group what belongs together, and name the groups.** Related fields in one cluster with a label
  that says the relation; paired values (two languages of one text, an amount and its currency, a
  date and its timezone) sit adjacent or side-by-side rather than interleaved down a single column —
  an interleaved pair forces the reader to remember one field while editing its twin, which is the
  exact memory-load failure the redistribution move avoids in tables.
- **One screen per decision.** If completing the surface requires deciding two unrelated things,
  that is two surfaces, sequenced — not one long scroll. Equally: a two-field job is not a wizard.
  Adding steps is a cost, and only pays for itself when it removes a wrong decision.
- **Make the expensive action structurally different from the routine one.** Destructive, irreversible
  or outward-facing actions should not be the same weight, in the same position, in the same cluster
  as Save. The fixed-zones move organises controls; this decides which ones get separated and why.
- **Anchor the action surface, and size the container to its content.** Buttons that sit after the
  last field disappear on a short viewport; a textarea sized by eye gets a scrollbar inside a modal
  that has no reason to scroll. Both of those are symptoms of treating the container as a layout
  rather than a surface with a job.
- **A dialog inherited from the old system is the same failure as an inherited taxonomy.** Every
  other container got reconsidered; this one was kept because "the modal already exists." If the pass
  changed nothing about how a thing is created, then how that thing is created was never diagnosed.

**Repainting is not redesigning.** If a surface's controls are the same ones, in the same order, with
the same grouping and only different classes, it was restyled. That is legitimate work at Lite and is
not, at any mode, the move described here.


### [Medium+] Protect the cost of the work
Every calming move raises what it costs to *use* the screen unless something bounds it. This is that
bound, and it is the missing half of the ceilings file: type, padding, contrast and page length all
have maxima because they can hurt the eye; nothing here has a maximum, because "too organised" is not
a harm — the limit is entirely relative to the job the surface does, which is why no instrument in
this skill catches it without being told to look.

Measure it from the structure, before and after: rows or records visible per screenful; clicks and
keystrokes from opening the screen to finishing the common task; whether the values someone compares
are ever on screen at the same time; how much must be remembered between one step and the next; how
far the focus indicator has to travel; what a mistake costs to undo.

**The rule: a pass may trade cost for comprehension only where comprehension is the job.** A screen
someone reads occasionally and must understand can afford a scroll. A screen someone uses four hours
a day cannot — opening up its spacing raises its height, which lowers rows per screenful, which adds
scrolling and eye travel, which is the same fatigue the move exists to remove, arrived at by a
different route. On those surfaces the calm treatment is applied to *encoding and hierarchy* (quieter
rules, real column emphasis, tabular figures, colour that carries information instead of decorating
it) and the density is defended.

Concrete ways a well-intentioned pass makes work worse, each of which has happened somewhere:
hiding a column someone reconciles against; moving a control hit 200 times a day further from the
row it acts on because it read as clutter; splitting a comparison across two pages; adding a
confirmation step to a routine bulk action while leaving the destructive single action one click;
putting the validation message somewhere other than the field being typed in; and re-sequencing a
form so the last field entered is now the one that determines whether the earlier ones are valid.

Name the trade in the report. "Rows per screenful 22 → 18, accepted because this table is read, not
keyed" is a complete justification. Silence about it is not.


### [Medium+] Design the range, not one width
Every pass in this skill has been derived from a screen observed at one width. Products are used
across a range, and the range is discoverable from the input: what the grid columns are, whether the
app's own styles contain breakpoint rules, whether the users are field or desk, what the product
does on a phone. Where the input supports narrow use, a Medium-level restructure must state how the
surface reflows, because the failure is silent and complete — every measurement is taken at desktop,
every ceiling passes, and the screen is unusable on the device most people are holding.

Reflow is not "stack the cards." The decisions that need to survive: does a table remain comparable
when its columns wrap or become stacked rows (usually no — which argues for fewer columns, a
detail drill-in, or horizontal scroll with a pinned key, rather than a card list that destroys the
comparison); does chrome that moves to a bottom bar keep its order and its discoverability; does a
drag target, a hover tooltip or a hover-revealed action still exist when the input is a thumb; do
touch targets and thumb reach match the frequency of the control. And the reverse direction is
allowed: a pass may legitimately narrow the supported range and say so — "this is a desk tool, the
phone view is the read-only one" is a design decision, but it has to be one, out loud.

**Decide a region's layout from the width the region actually gets, not from the viewport.** A
component that is 420px wide on a 1440px monitor and 420px on a tablet has the same layout problem
in both places, and a viewport media query will hand it two columns on the desktop and one on the
tablet — the opposite of what either user needs. Where a surface's own width is what determines
whether its contents fit side by side, size the breakpoint to that. The trap in doing it: a
threshold written as the *exact* computed width of the common case collapses that case, because
`max-width` is inclusive — measured once as "every medium dialog silently stopped pairing the two
language fields it exists to pair," and only visible in a render, never in the source.


### [Ultra only] Rebuild the palette as a tonal ramp, weighted by dwell time
Replace the existing color system (not just soften individual values) with a deliberate tonal ramp (2–4 steps, one consistent temperature/undertone) plus a status-color system (ink + soft-background pairs), assigned **per region by where the user's attention actually accumulates** — not by mechanically reusing the input's own current color scheme. This is Ultra-only because it's a genuine re-theme: every surface's color role gets reconsidered, not adjusted.

Judge the working surface's direction from what the product actually is, inferable from the source itself (a media/video tool, a creative/dark-context app, or anything whose own before-state signals darkness is core to its identity, not just an unexamined default → can legitimately stay dark, softened; a data-dense admin/ops console, a form-heavy business tool, anything meant for long analytical reading sessions → the strong default is to break away from all-dark and give the high-dwell-time working surface the light, low-fatigue treatment, even if the rest of the product's chrome stays a different, bolder treatment). Don't default to "keep it dark, just softer" as a safe middle ground without doing this judgment explicitly — that's the one outcome most likely to be a missed opportunity rather than a genuine call, because it changes the least and *looks* like a decision was made.

**Chrome — the low-dwell-time region carrying nav and brand — is its own set of independent judgment calls, not a fixed "dark sidebar" default.** Three separate questions, each genuinely open:
- **Where does it live?** A side rail is one instance, not the rule — a top bar, a bottom bar (mobile), a floating/collapsible panel, or chrome that changes position between breakpoints are equally valid depending on what the product's navigation depth and screen proportions actually call for. Don't reach for "sidebar" reflexively; ask where this specific product's nav actually belongs.
- **What color is it?** The brand's identity color doesn't have to be reduced to "a dark neutral with a colored accent" — chrome can legitimately be painted in the brand's actual hue as its dominant surface color (a full brand-green chrome, not dark-gray-with-a-green-highlight), precisely because it's glanced at rather than read continuously, so saturation there doesn't cost the fatigue it would on the working surface. Dark neutral, light neutral, and full-brand-hue are three genuinely different options — pick from evidence about what fits the brand, not by default to whichever is safest.
- **Does its color relate to the working surface's light/dark direction at all?** These are independent axes, not one decision — chrome can be a saturated brand color while the working surface is light, or dark-neutral while the working surface is light, or any other combination; the working-surface call above doesn't predetermine chrome's answer, and chrome's color doesn't predetermine the working surface's.

See `references/principles.md` for the full reasoning and `examples/dwell-time-palette.md` for the structural pattern, including how chrome position and chrome color get reasoned through as separate calls from the working-surface direction.


### [Ultra only] Add real depth
Give grouped surfaces a deliberate shadow and generous corner radius system, replacing flat 1px-border-only separation everywhere at once, reinforced by the new tonal ramp above. A Lite/Medium pass can nudge existing shadows/radii; Ultra is where a full elevation system gets designed from scratch.


### [Ultra only] Split into a real multi-page product, not a longer single page
Default to producing more than one output file/page (roughly the expected outcome ~85% of the time a data-dense screen goes through Ultra) — an "Overview"/dashboard page carrying the redistributed aggregate projections (health, trend, comparison, composition), separate and linked from a "detail" page carrying the actual list/table, mirroring how a real product would ship this rather than how a single file can be reorganized to feel like it. Before calling an Ultra pass complete, check: did the output stay a single file/page with only in-page sections, a new palette, and reorganized layout? If so, that is a Medium-grade result — the palette and layout moves happened, but the structural move that defines Ultra didn't. Go back and extract the aggregate page before delivering. The single-page exception is narrow: genuinely simple content (a short form, one focused tool, a screen with only 1–2 of the redistribution questions to answer at all) can legitimately stay single-page even at Ultra — state that reasoning explicitly when it applies, rather than defaulting to single-page silently.

**Naming the split page(s) creates the exact risk failure mode 10 describes — check the name actually earns its promise before shipping it.** Calling a new page "Overview" is only correct if what actually lands on it reads as quick, low-complexity, at-a-glance — genuine aggregate signals (health, composition, trend, "what needs attention") kept light: a handful of stat cards, a couple of charts, a short action list. If redistributing the original content still leaves that page carrying a dense table, many-column comparisons, or per-row granular detail, "Overview" is now mislabeling what's actually a second detail-grade page — the split happened, but the promise the name makes wasn't honored by what got put under it. This applies to every name introduced or kept through the pass, not just an "Overview" page: a "Summary" section that's longer and more granular than the content it summarizes, "Quick actions" hiding a dozen multi-step controls, a "Details" tab that's actually sparser than the "Overview" next to it — all the same failure, name promising one thing and content delivering another.


### [Ultra only] Re-derive the information architecture, not just each page's layout

Ultra is described as "re-structuring at every level", and the level that gets skipped is the one above the page: **which pages exist, how they group into navigation categories, what those categories are called, and what the routes are named.** A pass that rebuilds the palette, splits the aggregate onto its own page, and leaves the nav tree and every URL byte-identical to the input has done every Ultra move except the one that determines whether people can find things. Treat an unchanged taxonomy as a finding to justify, not a default.

How to do it, in order:

1. **Inventory the grouping, not the pages.** Every category and every item under it, in one view. You cannot see a bad taxonomy one category at a time — the whole point is what sits next to what.
2. **Ask what job each item belongs to.** For each leaf, name the task the person is doing when they need it — "I'm setting up a new fund", "I'm investigating why a price looks wrong", "I'm deciding what a customer can see". Items group because they answer the *same* job. Items that group because they are all "configuration", all "admin things", or all "small pages" are grouped by how the code was written, which is exactly the inheritance being questioned.
3. **Hunt the catch-all.** Any category named Settings / System / General / Misc / Other / Tools / More / Utilities is a hypothesis that nobody ever grouped these things — they accumulated. Empty it on paper, re-file every member by job, then see what genuinely has no job yet. Whatever survives is the real category, and it is usually much smaller than the original; if it is the same size, the re-file wasn't done, not that the bucket was correct.
4. **Check the shape as well as the contents.** Fifteen items under one parent is bad; thirteen parents of one or two items each is equally bad and just looks busier. Aim for a grouping a person can scan without expanding anything — usually a handful of top-level groups with a few children each. Siblings should be comparable in size; a category with 11 children next to one with 2 means the boundary between them is wrong.
5. **Reconcile the two taxonomies the app almost certainly has.** Nav grouping and permission/role grouping drift apart, and when they disagree — different names, different membership, an item grantable but not navigable — both are describing the same thing badly. Make them agree, and make the docs and the permissions dialog say the same words the nav does.
6. **Rename the routes to match.** A page that is reference data but lives at `/settings/markets` is mislabeled in the one place users, bookmarks, analytics and support links all copy from. Route names are user-facing copy; treat them with the same care as a heading.

**Blast radius is an input to the plan, not a reason to skip it.** Renaming a route or a permission id touches every place the old string appears — the router, the nav definition, the ability/permission constants, the role-grant UI, any deep link or redirect, and anything that hard-navigates by path. Enumerate those *before* renaming (grep the literal string across the app, not just the router file), decide whether old paths redirect or 404, and say which. "This would need the whole permission chain touched" is the reason a taxonomy like this survives — it is not a reason to leave it. If the app genuinely cannot be re-pathed safely, do the grouping and naming in the navigation, leave the URLs, and state that trade-off out loud rather than making it silently.

**Then delete the second copy of the route list.** Any page that hand-writes links to other pages — a hub, a sitemap, a 404's quick links, an empty state's suggestions — drifts into dead links the moment anything moves, and it drifts silently, because a link to a route that never existed renders fine until someone clicks it. One hub in this session pointed at two routes that had never been registered, and at five pages that had already moved. Generate those lists from the same definition the nav and the permission table read, so a route cannot be deleted without the link disappearing with it.

**This is a genuine consult.** A taxonomy is the one Ultra decision that outlives the rest of the pass and that the person will live with daily, and more than one grouping will pass steps 2–4. So: build the proposal, show the current grouping against the proposed one, name the items you moved and why, recommend one, and let them redirect before rewriting routes and permissions — not after.


### [Ultra only] Re-derive the interaction layer, not just the reading surfaces

Ultra is "re-structuring at every level," and after the level above the page, the level that gets
skipped is the one *inside* the surfaces where work happens. The palette moves, the tables
redistribute, the routes get re-derived — and the way a user creates a fund, exports a report or
fixes a validation error is byte-for-byte the input's, still wearing the old structure under the new
paint. `mode-audit.mjs` now counts this and reports it, because "71 pages converted, Ultra delivered"
and "0 of 77 dialogs designed" are both true statements about the same pass, and the second one is
the one the person notices on their first attempt to do their job.

Same method as the IA move, applied to tasks instead of navigation:

1. **Inventory the writing surfaces, not the pages.** Every form, dialog, drawer, inline editor and
   multi-step job, with what each one creates or changes. You cannot see a bad set of dialogs one
   dialog at a time — the whole point is that there are eleven of them and they are not the same
   eleven decisions.
2. **Ask what the user is deciding at each one, in what order.** The current sequence is almost
   always the order the data was modelled in, not the order the thought occurs in — the same
   "grouped by how the code was written" inheritance as a catch-all Settings category, one level
   down.
3. **Hunt the container mistake.** Is this job a modal at all? A modal is the inherited default, not
   a decision: a task with more than one screenful of content, anything done while comparing to what
   launched it, and anything you return to repeatedly are usually a page, a side panel, or an inline
   row. Conversely a confirm that interrupts a keyboard-first workflow for its third-act is usually
   not a modal either.
4. **Find the near-identical family.** Ten dialogs that differ only in which fields they show are one
   pattern that was copied ten times, and they will disagree about button order, width, label
   placement and validation timing in ways nobody chose. Unify into a pattern family with roles —
   the same move as collapsing an inherited taxonomy into a derived one, and the same argument for
   why the shared layer gets frozen before the wave goes out.
5. **Design each surface's states.** The create dialog that renders an empty list, saves silently
   into a failure, or shows a validation message three fields above the field in error is the
   states move applied to the writing surface, where it matters most because that is where the user
   is making mistakes rather than reading about someone else's.

**The blast radius is the same one that stopped the IA move, and it has a hard constraint here.**
Forms are wired to validation, submit handlers, dirty-state and permissions, and this skill changes
design, not behaviour. So: re-order, re-group, re-container, re-label positions, redesign the
feedback placement — and leave the submit semantics, the field set, the validation rules and what a
save does exactly as they were. State which parts of a flow you could not touch because they are
logic, and treat "touching it would mean changing behaviour" as a reason to report a limit, not a
reason to skip the diagnosis.

**The check before delivering:** pick three things a user can create or change in this product, and
say what is different about *how you do them* now. If the answer is the width, the border radius and
the button colour, the interaction layer did not go through the pass — and whatever the grade says,
that part of the outcome is Medium.

