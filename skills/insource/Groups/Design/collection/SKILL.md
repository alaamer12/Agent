---
name: collection
description: >-
  Method for producing a coherent brand-illustration image collection for a project. Fixed
  steps: determine the style once (shared Style DNA - medium, brand palette hexes, guard lines
  like 'strictly 2D vector, no 3D rendering'); determine where the set lives and how code
  consumes it (folder plus slot filenames as the contract - drop a correctly named image in, no
  code change); determine how each frame behaves. The usage names the manifest file (e.g.
  on-boarding.md): slot-to-file-to-status mapping, hard rules (never in any image: no text, no
  brand logos) and soft rules (dimensions, aspect, density), and per-frame prompts in fixed
  sections with save names and reference-chaining from a style anchor; regenerate-only-if-needed
  - shipped artwork is left alone. Use when asked for an image collection, illustrations for app
  screens, a consistent set of generated art, or 'make images for onboarding'. Not for one
  single image prompt (imagegen), real photo/file sourcing (fahlwy), or asset management
  (assets).
---

# Collection

One style, one character, many frames — delivered as a manifest the project keeps and the image
generator follows. The whole skill is three decisions in fixed order, then a file.

## The fixed way

1. **Determine the style.** Write the Style DNA block ONCE: medium (flat 2D vector / premium 2D
   mesh gradient / [other]), mood ("friendly corporate cartoon"), shape language ("clean smooth
   geometric shapes, minimal shading"), palette, canvas ("warm off-white"), and the guard lines
   that stop drift ("strictly 2D — no 3D render engine style, no realistic materials, no skin
   textures"). If the project already has an illustration style, extract these sentences from it
   instead of inventing new ones.
2. **Determine where the set will be used — and where it lives.** The usage names the output
   file: `on-boarding.md`, `empty-states.md`, `landing-heroes.md`. Record the **placement
   contract**: the folder the artwork ships to, how the code consumes it, and the filenames the
   code already looks for. Filenames are a contract, not decoration — when a slot's name is
   `step1.png`, new artwork for that slot is just a same-named file dropped into the folder; no
   code edit. Renaming or adding a slot is the only thing that touches code. List the frames the
   usage actually needs — one per screen/slot, no decorative extras — and note honestly when a
   slot needs **no image** (the UI itself is the illustration).
3. **Determine how each frame behaves.** Per frame: pose, action, subject, emotion — matched to
   what that screen says. Searching/inspecting → crouched with a flat magnifier. Relaxing/welcome
   → lounging in an armchair. Protecting/privacy → knight with envelope. Success/celebration →
   mid-air leap with a checkmark shield. The behavior is the only part allowed to differ between
   frames.
4. **Write the manifest** from `assets/templates/collection-template.md` into the project:
   placement contract, slot → file → subject → **status** mapping (`shipped / replaced / reused /
   no-image / pending` — the section closes with whether anything is pending), shared Style DNA
   with the brand hexes, **Hard rules** (what no image may ever contain) and **Soft rules**
   (what is recommended: dimensions, aspect, density), then one prompt block per frame.
5. **Generate (only when the user asks for images now):** frame 1 (or a dedicated style anchor)
   first; every later frame is generated **image-to-image referencing the anchor**, and its prompt
   restates "Matches the exact visual style and character design of the reference image." Save
   each output under the manifest's filename.

## Regenerate-only-if-needed

Shipped artwork that looks right is **done** — the manifest does not re-prompt it and generation
does not touch it. Prompts are written only for slots that are missing, explicitly replaced, or
whose spec changed. Before generating a new image, check whether an existing one can be **reused**
under the mapping (a regenerated final-step scene reusing the old fifth file is cheaper and more
consistent than a new render). The manifest's status column is what makes "nothing pending" a
provable statement instead of a vibe.

## Consistency rules — the part that breaks collections

- **Character Definition is canon.** The character sentence ("bright orange hair, vibrant green
  t-shirt, blue flat trousers, blocky happy features") is copied **verbatim** into every prompt.
  Paraphrasing is drift: "orange-haired guy in a green tee" next month produces a different
  person.
- **Guard lines ride in every prompt**, not once in the header — image generators drift toward
  3D/realism per call, and the negative sentence is the only leash.
- **Hard rules are embedded, soft rules are recommended.** Hard rules are what NO image in the
  set may ever contain — "no text, no letters, no numbers, no real brand logos or site marks" —
  appended to every prompt, because generators love inventing wordmarks. Soft rules are what an
  image SHOULD be: dimensions (1024×1024 PNG), aspect, negative space, palette density — stated
  once in the manifest, honored in the generation size and in prompts where they fit. A violated
  hard rule means regenerate; a violated soft rule is a judgment call.
- **Fixed section anatomy** for every entry: `Style` → `Character` → `Action`/`Pose` → `Color
  Palette & Background`/`Composition`. Same order, same names — frames become diffable.
- **Reference-chaining beats description** once a first good image exists: describe the style in
  the anchor, then point at it ("the exact same stylized 2D cartoon character from the reference
  image") for the rest. `references/01-prompt-anatomy.md`.

## Output file — what every entry must carry

| Field | Content |
|---|---|
| Frame slug | `01-inspect`, `02-welcome` — ordered, filesystem-safe |
| Use it in | the exact screen/slot ("Onboarding slide 2, right illustration") |
| Prompt | full 4-section prompt, Style DNA + canon character embedded |
| Save as | final asset path + filename — when the code declares the slot name (`step1.png`), that IS the filename; otherwise the manifest names it (`assets/illustrations/onboarding/02-welcome.png`) |
| Reference | which image this frame is generated against (`01-inspect.png` or anchor path) |

The manifest is the deliverable; images are the optional second act.

## Boundaries

| Situation | Skill |
|---|---|
| One single image / ImageGen prompt craft | `imagegen` |
| Real photos, avatars, fonts, proven free sources | `fahlwy` |
| Renaming/organizing/converting files after they exist | `assets` |
| UI states needing illustrations designed for them | `stateful` (the states) → this skill (their art) |

## Resources

- `assets/templates/collection-template.md` — copy this to `<usage>.md` in the project
- `references/01-prompt-anatomy.md` — section anatomy, style families, guard lines, reference-chaining
- `examples/onboarding-collection.md` — a filled manifest excerpt, four frames
