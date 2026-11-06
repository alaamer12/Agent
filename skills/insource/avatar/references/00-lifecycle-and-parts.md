# The avatar lifecycle and the parts contract - approach-neutral

Everything here holds whichever row of `data.csv` the job picked. Approach cards own the specifics; this
file owns the shape every avatar build shares.

## What an avatar is

An avatar is **a stand-in for an entity (person, team, bot, brand) wherever that entity is physically
absent**. That one sentence generates the whole design space, because every design question is a question
about what the stand-in must do:

- **Be recognized** - by its owner ("that's me") or by others ("that's Amr"). Recognition strength runs from
  photo (highest) through hand-drawn likeness, to monogram, to identicon (lowest - recognized by *string*,
  not by face).
- **Be consistent** - one entity, one avatar, across every surface and size; a family of entities, one
  visual grammar.
- **Be composable** - sometimes the avatar is not one picture but a *system*: attributes that swap
  (hair, outfit, background) while identity persists. That is what a parts model buys, and it is what
  `modular-svg-rig` exists for.
- **Be produced** - from a reference image, from a name string, from a seed hash, from a brief, or from a
  photo. The *source of truth* is the first axis of approach choice, not the medium.

## The design space (why no approach is the default)

| Axis | Poles | Decides |
|---|---|---|
| Medium | vector ↔ raster ↔ live-typographic | scaling, editability, delivery formats |
| Source of truth | reference image ↔ name/seed ↔ brief ↔ photo | whether you match, derive, or invent |
| Determinism | fixed artifact ↔ procedural (same input → same avatar) | reproducibility, bulk generation |
| Parts-ness | single image ↔ swappable system | whether a parts model is needed at all |
| Effort ceiling | monogram (minutes) ↔ rigged character family (hours) | budget honesty |

A request for "an avatar" answers none of these; a request for "the same guy with 4 haircuts" answers all
of them. Read the request on these axes, then pick the row of `data.csv` - or discover a new approach and
record it. **The catalog is a starting point, not a whitelist**: an open world means the interesting way
often is not in the table yet.

## The lifecycle

1. **Brief** - who/what is represented; where the avatar will appear (sizes, frames, backgrounds); one
   avatar or a family; swappable attributes or fixed; source material available (image? name? nothing?).
   Ask only what materially changes the approach; state the rest as assumptions.
2. **Approach choice** - `catalog.py list`, match the brief against the axes above; read the chosen
   approach's card. No fitting row that is `verified`? Either take an `unverified` row *and prove it on a
   throwaway first*, or invent the approach - then in both cases `catalog.py add` records it. Choosing
   "no rig" is a legitimate choice (`single-flat-svg`); do not build a system nobody asked for.
3. **Build** - per the approach card. The universal rule: **produce a first complete artifact early**,
   however crude, and iterate on the artifact, not on the plan.
4. **Parts** (only if the brief says swappable) - see the contract below.
5. **Verify and debug** - the checks are the same questions regardless of medium: Does it render? Does it
   match its source of truth? Does swapping one attribute change only that attribute? Does it survive the
   edge inputs? (failure taxonomy below)
6. **Deliver** - the artifact set the brief needs (formats, sizes, fallbacks), a short report (what matched,
   what was approximated, known limits), and **the catalog write-back**: new approach → `add`; re-proven →
   `stamp`; built resources → the approach's own CSV. A run that leaves the catalog unchanged is a run the
   next agent will repeat from zero.

## The parts contract - any medium

"Parts" means: the avatar decomposes into units that swap independently. The words differ per approach
(SVG slots, layer stacks, URL params, sticker glyphs), the contract does not:

- **Boundary** - every unit declares the region it owns (an envelope, a z-range, a param subset). A unit
  that paints outside its boundary corrupts other units.
- **Anchor** - units agree on shared coordinates where they meet (chin line, eye line, baseline, grid cell).
  Anchors are defined once, at the system level, and every unit is authored against them - never against
  each other.
- **Independence** - swapping one unit must leave every other unit pixel-identical. If swapping hair moves
  the ears, the layering or the ownership is wrong, not the hair.
- **Style consistency** - all units share one grammar (stroke weight, palette variables, corner radii).
  A part in the wrong style is a seam even when the geometry is perfect.
- **Overlap, not abutment** - where units meet, they overlap generously; edge-to-edge joins leak hairline
  gaps at every zoom and rounding. (In param/URL approaches the analogue: never let two params own the same
  pixel region.)
- **Tested in combination, not in isolation** - each unit passes alone *and* sampled against its neighbours;
  full cross-products explode, so cover every touching pair at minimum (that is what greedy pairwise
  sampling in the rig approach does - the principle generalizes).

## Debugging - the universal failure taxonomy

| Symptom | Usual cause | Where it bites in each medium |
|---|---|---|
| Hairline gap / seam at a join | abutting boundaries, rounding | SVG edges; emoji baselines; param overlap zones |
| Swap changes unrelated parts | ownership/layering bug | z-order; wrong param scope; layer stack |
| Looks wrong at 24px | detail density above the size budget | every medium - test at the *smallest real* size |
| Different on another machine | platform-dependent rendering | emoji fonts, CSS defaults, font fallbacks for monograms |
| Same input, different output | hidden nondeterminism | random seeds, clock/locale, unordered color pickers |
| Non-latin names break it | grapheme rules assumed ASCII | monogram initials, identicon seeding |
| "It matched but the family doesn't" | style drift between artifacts | palette variables not shared; hand-drawn variants diverge |
| Leak after "revocation-style" cleanup | stale caches/embedded copies | old exports, EXIF thumbnails - verify the *shipped bytes* |

Debug discipline, same as any verification skill: reproduce on the artifact, change **one** unit at a time,
re-run the check that failed, and when a bug class is understood, make the verifier catch it (the rig
approach's `examples/broken-parts/` + selftest is the template: every known-bad shape becomes a fixture that
proves the guard works).
