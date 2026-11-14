# <Page or set> — image BOM — <project name>

<!-- Copy to bom/<page>.md in the project (one file per page that needs images), or to
     <usage>.md when the whole product is a single set. Fill every <placeholder>; delete this
     comment. Style DNA, Character canon and Hard rules are copied VERBATIM into each prompt.
     Leave shipped artwork alone - prompts exist only for slots that need (re)generation. -->

- **Source:** `PAGES.md` §<page>
- **Status:** <style-confirmed / nothing-pending / N slots pending>
- **Style canon:** `bom/style.md` (or "this file, single-page project")
- **Style anchor:** <path of the first approved image, or "none yet">
- **Placement:** `<public/images/<page>/>` - <how the build consumes it, e.g. "the glob picks
  files up automatically; no project-file edit needed">
- **Filenames are the contract:** the code looks up <where: enum/map/slot names>. New artwork for
  an existing slot = a same-named file dropped in; renaming or adding a slot is the only change
  that touches code.
- **Sheet plan:** <e.g. one 1536x1024 5x2 render for the avatar set; fallback: two 2x2 sheets>
- **Regeneration recipe:** `resources conform` reads the table below - do not rename slots there
  without updating the code.

## Slots

| Slot | Role | Source | Master | Delivery | Status |
|---|---|---|---|---|---|
| `<hero-home>` | <hero illustration, right of headline> | generate single | `<1600x900 single>` | `<800x450 16:9 avif q60 @1x,2x>` | <pending> |
| `<avatar-01..10>` | <testimonial personas> | generate sheet 5x2 | `<1536x1024 sheet 5x2 gutter 0>` | `<128x128 1:1 webp q82 @1x,2x>` | <pending> |
| `<logo>` | <brand mark, header> | reuse `brand/logo.svg` | — | `<240x64 svg>` | <shipped> |
| `<step-3>` | <permissions step> | none - the sheet UI is the illustration | — | — | <no-image> |
| `<photo-teaser>` | <pricing card photo> | fahlwy | — | `<640x360 16:9 jpeg q80 @2x>` | <pending> |

<Only `generate` rows get a prompt block and a master spec. Everything else is listed so the next
agent does not invent artwork for it. Close with the honest total: "N slots, M files shipped,
nothing pending" / "Pending: <slots>". Statuses: pending / shipped / reused / no-image.>

## Shared Style (Style DNA - verbatim in every prompt)

> <Medium + mood + shape language, e.g. "Flat vector illustration, warm cream background
> (#FDF6EC). Accent palette: <brand blue> (#2386C8) and <brand orange> (#FFA200), teal detail
> (#1B7A5A). Soft elliptical dark ground shadow. Small geometric confetti - dots, plus signs,
> short squiggles. Generous negative space, thick clean shapes, minimal shading. Strictly 2D -
> no 3D rendering, no realistic materials, no skin textures.">

<If the project has more than one page with images, move this section (and the two below) into
`bom/style.md` once, and link it from every page BOM. One canon, many references.>

## Character canon (verbatim; omit if the set has no recurring subject)

> <"Same character throughout: young man, orange hair, dark-green t-shirt (#1B5E47), navy
> trousers (#1E2A4A), white sneakers." - or the subject-canon sentence for mascot/knight sets.>

## Hard rules (NO image may contain these - embedded in every prompt)

- <No text, no letters, no numbers.>
- <No real brand logos or site marks.>
- <...project-specific: no faces of real people, no religious symbols, ...>

A violation here is a defect: regenerate the image, the embedded rule stays.

## Soft rules (recommended - aim, don't force)

- <Dimension/format: 1024x1024 PNG, square 1:1.>
- <Composition: generous negative space, calm palette, one focal object.>
- <Consistency: same ground-shadow device in every frame.>

A violation here is a judgment call, not a defect.

## Economy check (generated sheet rows only)

| Slot | Delivery x max DPR | Required master | Sheet cell | Valid? | Fallback |
|---|---|---|---|---|---|
| `<avatar-01..10>` | `<128px x 2>` | `<256x256>` | `<283x328>` | <yes> | <2x2 sheets / singles> |

<required_master = ceil(delivery px x max DPR); cell = (sheet px - gutters) / cols. Measure an
existing render with `resources`' `sheet_probe.py` before trusting this table.>

## Prompts - generated slots only (regenerate-only-if-needed)

<!-- One block per slot whose Status is pending or replaced. Shipped slots get NO prompt block.
     Prompt sections are fixed and in this order: Style, Character, Action, Color & Background. -->

### `<hero-home>` - <hero illustration>

**Use it in:** <Home page, right of the headline>
**Slot / save as:** `<public/images/home/hero-home.avif>` (the slot id is the filename stem)
**Master:** `<1600x900 single>` -> **Delivery:** `<800x450 16:9 avif q60 @1x,2x>`
**Reference:** <anchor path / none - this frame defines the style>

**Prompt:**

- **Style:** [Style DNA text] [Hard rules text]
- **Character:** [Character canon text] / "**The exact same** character from the reference image"
  when chaining.
- **Action:** <this frame's pose + subject interaction, one clear idea>
- **Color Palette & Background:** <shared palette + frame-specific composition notes>

## After generation

```bash
# 1. generate the master (command derived from the Master column)
# 2. measure a sheet, then conform each master into slot files
python scripts/conform.py --bom bom/<page>.md --group <slot-prefix> \
    --in raw/<sheet>.png --out <delivery folder>
python scripts/conform.py --bom bom/<page>.md --slots <single-slot-id> \
    --in raw/<single>.png --out <delivery folder>
# 3. review the result: transparency is invisible against white
python scripts/contact_sheet.py <delivery folder> --out review/<page>.png --skip-density
```

Conform trims each sheet cell or uses a single master whole, fits the delivery aspect, writes the
DPR ladder and verifies every file. The review sheet proves the edges by eye; the conform report
proves the geometry. Prompts, generation and conform must all use the same slot ids.
