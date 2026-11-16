# Bills of materials: dissecting a page into images

A BOM is the plan for one page's imagery: what is on the page, which of it must be generated, how
large each master has to be, how the masters are produced, and what each delivery file must be.
It is written **before** prompts, because the plan decides the prompt's composition and size.

```
pages tree ──► dissect ──► BOM.md + bom/<page>.md ──► prompts ──► generate ──► resources conform
                            ▲
                       bom/style.md (one canon)
```

Never invent pages: the BOM consumes what `pages` produced. A page with no imagery is recorded as
`no-images`, not skipped - an empty row is evidence, an absent row is an oversight.

---

## 1. The five reads

### Read 1 - regions

Divide the page into the places imagery can live: hero, feature cards, empty states, list rows,
navigation, modals, onboarding slides, auth screens, 404. One region can hold several slots (an
avatar stack), and one slot can appear in several regions (a logo). List regions first so
duplicates are visible before you write rows.

### Read 2 - classify

Every visual gets exactly one kind, and the kind decides the producer:

| Kind | Producer | Prompt? |
|---|---|---|
| Illustration, character, hero art, background texture | `generate` (single or sheet) | yes |
| Avatar / persona set | `generate` sheet, then conform | yes, once per set |
| Photo | `fahlwy` | no |
| Icon, logo, wordmark | `resources` (icon set, SVG) or an existing brand file | no |
| Screenshot, UI mockup | capture / reuse | no |
| Decorative gradient, shape | CSS | no row at all |

Only generated rows get a master spec and a prompt. Everything else is still **listed** - the BOM
is the complete inventory, not a list of things to generate. That is what keeps a later agent from
generating an illustration for an icon slot.

### Read 3 - measure

For each slot, record two sizes:

- **Delivery** - what ships. CSS size × DPR ladder, format, quality. `128x128 1:1 webp q82
  @1x,2x,3x` means three files: 128, 256, 384.
- **Master** - what must exist before conform. `required_master = ceil(delivery_px × max_DPR)`.

An avatar shown at 40 CSS px on a 3x screen needs 120 CSS px, so a 128px delivery is right and a
**384px master** is mandatory. Writing `128x128 @3x` and generating a 1024px sheet with 200px cells
is a plan that cannot be executed - the numbers are the first thing to check.

Aspect is not decoration either: `1:1` avatars, `16:9` heroes, `3:2` cards. Conform pads to the
declared aspect and refuses to squash; a mismatched source becomes padding, not a stretched face.

### Read 4 - route

| Route | When |
|---|---|
| `generate sheet CxR` | repeated, same-sized, same-style subjects: avatars, badges, sticker sets, icon illustrations |
| `generate single` | unique composition, full-bleed art, anything with layout-specific negative space |
| `reuse <path>` | a shipped file already satisfies the slot |
| `fahlwy` | real photography, real people |
| `resources` | vector icons, logos, favicons, derived brand files |

Sheet candidates share: subject type, aspect, style, and a background that does not matter when
cut. A hero illustration with a bespoke composition is never a sheet cell.

### Read 5 - find economy

Only for generated rows. Compute, do not guess (see §2). The Master cell holds only the chosen
plan, because `conform` parses it: `1536x1024 sheet 5x2 gutter 0`. Record the fallback
(`2x2 sheets`) in the economy check's Fallback column.

---

## 2. The economy test

Sheets are cheaper only while the cells are big enough:

```
required_master = ceil(delivery_px × max_DPR)          # W and H separately
cell            = (sheet_px - (cols - 1) × gutter) / cols
sheet valid     = cell >= max(required_master_w, required_master_h)  AND  count <= cols × rows
requests        = ceil(N / (cols × rows))              # vs N singles
master_quality  = generation tier (resolution, model)  # not encode quality
delivery_quality= format + qN at each DPR step         # not master quality
```

Worked comparison, ten avatars:

| Delivery | Required master | One 1536×1024 5×2 sheet | Requests |
|---|---|---|---|
| `128px @1x,2x` | 256px | cells 283×328 - valid | 1 |
| `128px @1x,2x,3x` | 384px | cells 283px - **invalid** | 3 sheets of 2×2, or 10 singles |
| `64px @1x,2x,3x` | 192px | valid | 1 |

The same sheet is economical at 2x and wasteful at 3x. That is the whole point of the arithmetic.

### Two qualities, never one word

- **Master quality** - how good the render is: model tier, resolution, prompt. A 4K sheet of poor
  art is still poor.
- **Delivery quality** - how the shipped file is encoded: WebP/AVIF/JPEG at `qN`, per DPR step.

Economy lives in requests and master size; it must never be paid for with either quality. A BOM
that says "use 1K to save money" while the slots need 384px masters is not economical, it is broken.

### Correlated risk

A sheet is one request and one failure domain: one malformed cell can invalidate the render, while
individual generations vary in style and cost N requests. Record which way the plan leans and what
happens if the sheet fails. Costs are never estimated in the BOM - `generate` writes `usage.jsonl`;
quote that.

---

## 3. Measuring a sheet that already exists

Before trusting a BOM row, measure the render with `resources`' probe:

```bash
python scripts/sheet_probe.py raw/avatars.png --grid 5x2 --delivery "128x128 1:1 webp @1x,2x"
```

It reports content bounds, the layout row by row, gutter widths, per-cell subject sizes, empty
cells, the interior cut lines an even split would land on, and the delivery ceiling. If `ceiling`
is smaller than `required_master`, the plan fails **before** writing prompts - fix the delivery
spec or the sheet size then.

Worked example (a real 1536×1024 RGBA sheet, five columns, two rows):

```
content   [62, 167, 1475, 822]   margins left=62 top=167 right=61 bottom=202
columns   5 bands, gaps [15, 15, 15, 16]
rows      2 bands, gap [103]
layout    regular - 10 subject(s), rows 5,5
grid      5x2 cells about 283x328
subjects  min 269x275, max 271x277
ceiling   269px square master
master    1536x1024 sheet 5x2
```

Conclusion for the BOM: `128x128 @1x,2x` is valid (needs 256 ≤ 269); `@3x` is not. The uneven
margins mean the cut must follow the content box, which is what `conform` does by default.

### A sheet whose rows disagree

A real catalog page is often not a grid: four rows holding 8, 8, 8 and 10 subjects, with the last
row's subjects closer together. The probe reports it instead of inventing a grid:

```
layout    mixed - 34 subject(s), rows 8,8,8,10
subjects  min 128x169, max 189x182
master    1536x1024 sheet rows 8,8,8,10
clips     8 interior cut line(s) of an even split land on content
```

`sheet rows ...` is the plan; conform cuts each row down the middle of its own measured gutters.
An even `8x4` grid would slice ten subjects and produce 32 files for 34 slots. The full worked
BOM: `examples/badge-catalog-bom.md`.

### A sheet of unrelated subjects

Nothing requires a sheet to hold variations of one thing. Six onboarding frames, a set of store
categories and thirty-four badges are the same problem: N subjects on one image, N slot ids. Name
them what the app calls them and list them in sheet order:

| Slot | Role | Source | Master | Delivery | Status |
|---|---|---|---|---|---|
| `welcome, permissions, finish, offline, empty-state, error` | onboarding frames | generate sheet 3x2 | `1536x1024 sheet 3x2 gutter 0` | `192x192 1:1 webp q82 @1x,2x` | pending |

Conform cuts row-major: `welcome` is cell 1, `error` is cell 6, and selecting a subset keeps that
mapping (`--slots error` cuts cell 6, not cell 1). Numbered ids are a convenience, not a
requirement - the order in the Slot cell is the sheet order. What the pipeline cannot do is infer a
mapping nobody wrote: if that list order is wrong, the names land on the wrong cells, so order the
row the way the sheet reads.


---

## 4. Files

```
BOM.md                  index: page, image count, generated count, no-images pages
bom/style.md            Style DNA, character canon, hard rules, soft rules (single canon)
bom/<page>.md           the page's slot table + prompts for its generated slots
bom/shared.md           logo, icon set, textures and avatars used by more than one page
```

`bom/shared.md` exists so a logo used on twenty pages is specified once. Its rows use the same
table; the only difference is that its slots are referenced from several page BOMs.

### BOM.md

| Page | Images | Generated | File | Status |
|---|---|---|---|---|
| home | 14 | 3 | `bom/home.md` | planned |
| onboarding | 5 | 4 | `bom/onboarding.md` | in progress |
| settings | 0 | 0 | — | no-images |
| pricing | 6 | 0 | `bom/pricing.md` | reused |

### Page BOM header

Every `bom/<page>.md` starts with what a later agent needs before reading the table:

```markdown
# home - image BOM

- Source: `<docs>/pages/home.md`
- Style canon: `bom/style.md`
- Placement: `public/images/home/`, resolved by slot id in `Home.tsx`
- Regeneration: `resources conform` reads this table; do not rename slots without updating code
```

---

## 5. Slot table grammar

| Column | Grammar | Notes |
|---|---|---|
| Slot | any id (`hero-home`, `welcome`), a comma list, or a range (`avatar-01..10`) | range = shorthand for a numbered family; ids become filename stems; a sheet of unrelated ids is listed in sheet order |
| Role | free text | what the region needs it for |
| Source | `generate sheet 5x2` / `generate single` / `sheet <path>` / `reuse <path>` / `fahlwy` / `resources` | producer, not format |
| Master | `WxH single`, `WxH sheet CxR [gutter N]`, or `WxH sheet rows 8,8,8,10` | required for any row that is cut, `-` otherwise |
| Delivery | `WxH [aspect] [format] [qN] [@DPRs]` | exactly what `conform` implements |
| Status | `pending / shipped / reused / no-image` | closes the "is anything missing" question |

`sheet rows` is for a master whose rows hold different subject counts. `conform` cuts it on the
measured gutters, so it takes no `gutter` and no `CxR` - writing both is a spec error, not a hint.

Both spec grammars are executed by `resources conform`; it reads this table directly. Do not write
a private variant of them in a project - if the grammar is missing something, change it here.

**An existing sheet is a BOM row too.** When the user already owns the pixels (a catalog page, a
sprite sheet), the route is `sheet <path>` with the same Master and Delivery columns and no prompt:
`conform` cuts and fits it exactly like a render. That is how a reference image becomes project
assets without regenerating art that already exists.


---

## 6. Dissection checklist

Before leaving the plan:

- [ ] Every page in the `pages` tree appears in `BOM.md`, including `no-images` ones.
- [ ] Every generated slot has slot id, master, delivery, prompt, save path, reference.
- [ ] Every non-generated slot has a source route and **no** prompt.
- [ ] `required_master <= cell` for every sheet row (probe the sheet if it exists).
- [ ] Delivery aspects match the layout's boxes.
- [ ] Repeated same-sized subjects are on a sheet; unique compositions are singles.
- [ ] The fallback for each sheet is recorded.
- [ ] Shared assets are in `bom/shared.md`, not duplicated per page.
- [ ] Statuses are honest: `shipped` means the file exists and matches its spec.

## 7. Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Prompt asks for more detail than a cell can hold | master not planned | raise sheet size or make it a single |
| Same avatar appears twice with different faces | no shared style anchor / sheet reused across sets | one canon, one anchor, one sheet per set |
| Delivery files look soft | cell smaller than required master | raise master, lower DPR, or split sheets |
| The cut slices subjects / 32 files for 34 slots | the sheet's rows hold different counts, planned as `CxR` | probe it; plan `WxH sheet rows 8,8,8,10` instead |
| Icons appear as illustrations | classification skipped | route icons to `resources` |
| A page's images never shipped | page absent from `BOM.md` | list every page, mark `no-images` explicitly |
| Prompts and filenames disagree | slot id not used as the key | one id from BOM row to delivery file |
