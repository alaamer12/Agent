# Collection

One style, one character, many frames - delivered as a bill of materials the project keeps and the
image generator follows. **Plan first, then style, then prompts.** Writing a prompt before you know
whether the slot is generated, how large its master must be, or whether it shares a sheet with nine
siblings produces art the project cannot ship.

Two scopes, one pipeline:

| Scope | Question | Artifact |
|---|---|---|
| **Page** (BOM) | what images does this page need, and how is each produced? | `bom/<page>.md` |
| **Set** (style + prompts) | how do these frames look like one family? | `bom/style.md` + the page's prompt blocks |

The slot id is the key in the BOM row, the prompt block, the generated file and the delivered file.
Write both halves in one pass and nothing downstream has to reconcile them.

## The fixed way

0. **Dissect and plan (BOM).** Read the reference or the pages, list every visual, classify it,
   and decide how each one is produced. Write `BOM.md`, `bom/<page>.md` and `bom/style.md`. Nothing
   below starts before this, because the plan sets the master size and the prompt's composition.
1. **Determine the style.** Write the Style DNA block ONCE in `bom/style.md`: medium (flat 2D
   vector / premium 2D mesh gradient / [other]), mood ("friendly corporate cartoon"), shape
   language ("clean smooth geometric shapes, minimal shading"), palette, canvas ("warm off-white"),
   and the guard lines that stop drift ("strictly 2D - no 3D render engine style, no realistic
   materials, no skin textures"). If the project already has an illustration style, extract these
   sentences from it instead of inventing new ones.
2. **Determine placement.** The folder the artwork ships to, how the code consumes it, and the
   filenames the code already looks for. Filenames are a contract, not decoration - when a slot's
   name is `step1.png`, new artwork for that slot is a same-named file dropped into the folder; no
   code edit. Renaming or adding a slot is the only thing that touches code.
3. **Determine how each frame behaves.** Per frame: pose, action, subject, emotion - matched to
   what that screen says. Searching/inspecting → crouched with a flat magnifier. Relaxing/welcome
   → lounging in an armchair. Protecting/privacy → knight with envelope. Success/celebration →
   mid-air leap with a checkmark shield. Behavior is the only part allowed to differ between
   frames.
4. **Write the prompts**, one block per **generated** slot, from
   `assets/templates/collection-template.md`: fixed sections, Style DNA + character canon copied
   verbatim, hard rules appended, reference-chained from the style anchor.
5. **Plan the generation run**, then hand it over: the BOM row already states the master size, the
   sheet grid and the delivery spec, so the command to `generate` is derived, not re-invented.
   After generation, `resources` (conform: probe → split → fit → verify) turns the raw sheet into
   the slot files. Pages marked `no-images` skip both.

## Bills of materials

A BOM is **page-scoped** and **imagery-only**. It answers "what images this page ships and how each
one is made" - not fonts, video or documents, which keep their own flows.

**One file per page** that needs images. Pages that need none are not omitted: `BOM.md` lists them
as `no-images`, so "this page has no artwork" is a recorded decision instead of an oversight.

| File | Contents |
|---|---|
| `BOM.md` | index: every page in the `pages` tree (`<docs>/pages/`), image count, `no-images` marker, shared assets |
| `bom/<page>.md` | that page's slot table + prompts for its generated slots |
| `bom/style.md` | Style DNA, character canon, hard and soft rules - the single canon |

### The slot table

The schema lives here; `resources` reads it and changes nothing about it.

| Slot | Role | Source | Master | Delivery | Status |
|---|---|---|---|---|---|
| `avatar-01..10` | avatar set | generate sheet 5x2 | 1536x1024 sheet 5x2 gutter 0 | `128x128 1:1 webp q82 @1x,2x` | pending |
| `badge-01..34` | achievement badges | sheet `refs/badges.png` | 1536x1024 sheet rows 8,8,8,10 | `96x96 1:1 webp q82 @1x` | pending |
| `hero-home` | hero illustration | generate single | 1600x900 single | `800x450 16:9 avif q60 @1x,2x` | pending |
| `logo` | brand mark | reuse `brand/logo.svg` | — | `240x64 svg` | shipped |
| `photo-teaser` | stock photo | `fahlwy` | — | `640x360 16:9 jpeg q80 @2x` | pending |
| `icon-search` | icon | `resources` / icon set | — | `24x24 svg` | shipped |

- **Slot**: one id, a comma list, or a range for a numbered family (`avatar-01..10`). The id
  becomes the filename stem, and ids are arbitrary - `welcome`, `empty-state`, `hero-home`. For a
  sheet holding unrelated subjects, list them in the sheet's row-major order; that order is the cut
  order.
- **Source**: `generate` (single or sheet), `sheet <path>` (an existing sheet image to cut - a
  reference catalog the user owns), `reuse <path>`, `fahlwy`, `resources`. Only rows with a master
  get a spec and a prompt; only generated rows get a prompt.
- **Master**: `WxH single`, `WxH sheet CxR [gutter N]`, or `WxH sheet rows 8,8,8,10` when the rows
  hold different subject counts - the raw render the slot is cut from. It must hold
  `delivery px x max DPR` per axis; `resources` reads this cell, so notes never go in it. Do not
  guess it: `resources`' `sheet_probe.py` measures the image and prints the exact spec to paste.
- **Delivery**: `WxH [aspect] [format] [qN] [@1x,2x,3x]` - exactly what `resources` implements.
- **Status**: `pending / shipped / reused / no-image`.

### Dissecting a reference - five reads

1. **Regions.** Page or mockup → regions (hero, cards, empty state, nav, list rows).
2. **Classify.** Each visual is one of: illustration, avatar/persona, photo, icon, logo/wordmark,
   texture/background, screenshot, none-of-the-above. Classification decides the producer.
3. **Measure.** Box and aspect in the layout, then the real device pixels and DPR - that is the
   delivery spec. A 128 CSS px avatar at 3x needs a 384px master.
4. **Route.** Generated sheet / generated single / reuse existing / stock (`fahlwy`) / icon set
   (`resources`). Only the first two get prompts.
5. **Find economy.** Repeated, same-sized, same-style subjects are sheet candidates; unique
   full-bleed art is a single. Sheet rows do not have to share a column count - a catalog of
   badges is 8,8,8,10 - but each row is still one render plan. Record the arithmetic, not a feeling.

Detail, worked sheets and the full dissection checklist: `references/02-bom.md`.

## Economy - sheets are cheaper only when the math says so

```
required_master = ceil(delivery_px x max_DPR)       # per axis
cell            = (sheet_px - (cols-1) x gutter) / cols
sheet valid     = cell >= required_master           # and count fits CxR
requests        = ceil(N / cells_per_sheet)  vs  N
```

The avatar sheet above: 10 avatars at 128px `@1x,2x` need 256px masters; a 1536×1024 5×2 sheet
gives 283px cells → valid, 1 request instead of 10. Raise the delivery to `@3x` (384px masters)
and the same sheet **fails** - you need 3 sheets of 2×2 (12 cells), 10 singles, or a larger master.
Measure with `resources`' `sheet_probe.py` before committing the plan.

Economy is not cheapness. A sheet trades cost for **correlated risk**: one bad cell invalidates
the whole render, while individual generations drift in style. Record the fallback (`2x2 sheets`
or `singles`) in the economy check, outside the Master cell `resources` reads, so a failed sheet has
a plan, not a panic. Never estimate prices in
the BOM - the actual cost comes from `generate`'s `usage.jsonl`.

## Regenerate-only-if-needed

Shipped artwork that looks right is **done** - the BOM does not re-prompt it and generation does not
touch it. Prompts exist only for slots that are missing, explicitly replaced, or whose spec changed.
Before generating, check whether an existing file can be **reused** for the slot. The status column
is what makes "nothing pending" a provable statement instead of a vibe.

## Consistency rules - the part that breaks collections

- **Character Definition is canon.** The character sentence ("bright orange hair, vibrant green
  t-shirt, blue flat trousers, blocky happy features") is copied **verbatim** into every prompt.
  Paraphrasing is drift: "orange-haired guy in a green tee" next month produces a different person.
- **Guard lines ride in every prompt**, not once in the header - image generators drift toward
  3D/realism per call, and the negative sentence is the only leash.
- **Hard rules are embedded, soft rules are recommended.** Hard rules are what NO image in the set
  may ever contain - "no text, no letters, no numbers, no real brand logos or site marks" -
  appended to every prompt, because generators love inventing wordmarks. Soft rules are what an
  image SHOULD be: dimensions, aspect, negative space, palette density - stated once in
  `bom/style.md`, honored in the generation size and in prompts where they fit. A violated hard
  rule means regenerate; a violated soft rule is a judgment call.
- **Fixed section anatomy** for every prompt: `Style` → `Character` → `Action`/`Pose` → `Color
  Palette & Background`/`Composition`. Same order, same names - frames become diffable.
- **Reference-chaining beats description** once a first good image exists: describe the style in
  the anchor, then point at it ("the exact same stylized 2D cartoon character from the reference
  image") for the rest. `references/01-prompt-anatomy.md`.

## BOM.md index

```markdown
# Image BOM - <project>

Style canon: `bom/style.md`. Shared assets: `bom/shared.md`.
Every page in the `pages` tree is listed; `no-images` is a decision, not a gap.

| Page | Images | Generated | File | Status |
|---|---|---|---|---|
| home | 14 | 3 | `bom/home.md` | planned |
| onboarding | 5 | 4 | `bom/onboarding.md` | in progress |
| settings | 0 | 0 | — | no-images |
```

## Output file - what every generated slot must carry

| Field | Content |
|---|---|
| Slot id | `hero-home`, `avatar-01` - the key shared by BOM row, prompt, render, delivery file |
| Role / use | the exact screen and placement ("Onboarding slide 2, right illustration") |
| Master | size, single or sheet grid, gutter - what `generate` must produce |
| Delivery | size, aspect, format, quality, DPR ladder - what `resources` must write |
| Prompt | full 4-section prompt, Style DNA + canon character embedded, hard rules appended |
| Save as | final path + filename derived from the slot id (the code's slot name wins when it declares one) |
| Reference | which image this frame is generated against (anchor path) |

The BOM and manifest are the deliverable; images are the second act.

## Boundaries

| Situation | Go instead |
|---|---|
| Writing one image prompt, running generations, video | `generate` |
| Real photos, avatars from a library, proven free sources | `fahlwy` |
| Splitting a generated sheet, fitting delivery sizes, naming, verifying | `resources` (conform) |
| Renaming/organizing/converting files after they exist | `resources` |
| Deciding which pages a product has | `pages` - the BOM consumes the `pages` tree, never invents pages |
| UI states needing illustrations designed for them | `stateful` (the states) → `assets` (their art) |

## Resources

- `assets/templates/collection-template.md` - copy to `bom/<page>.md` (or `<usage>.md` for a
  single-set product); includes the BOM slot table
- `references/01-prompt-anatomy.md` - section anatomy, style families, guard lines, reference-chaining
- `references/02-bom.md` - dissection checklist, economy math, sheet planning, worked examples
- `examples/onboarding-collection.md` - a filled manifest excerpt, four frames
- `examples/avatar-sheet-bom.md` - a filled page BOM: one sheet, ten avatar slots, measured
- `examples/badge-catalog-bom.md` - a filled page BOM for an existing catalog sheet whose rows
  hold 8,8,8,10 subjects: the `sheet rows` route, cut without regenerating anything
