# Prompt anatomy for collections

Generalized from working brand-illustration prompt sets. [Bracketed] items are examples; the
section shape and the drift rules are the skill.

## The four sections, always in this order

1. **Style / Core Style** — the Style DNA, identical text in every frame. Two proven families:
   - *Flat 2D vector:* "flat 2D vector brand illustration, modern tech art style, friendly
     corporate cartoon, clean smooth geometric shapes, minimal shading, smooth solid colors."
   - *Premium 2D mesh gradient:* "clean flat vector artwork enhanced with smooth, localized
     internal color gradients for a rounded, volumetric 2D look" — richer, still strictly 2D.
   Pick one family per collection; mixing families across a set reads as two brands.
2. **Character / Main Subject** — the canon sentence. Recurring mascot: full description,
   verbatim, every time. Non-character sets: the subject sentence plays the same role (the knight
   + envelope + sword is one canon block, reused exactly).
3. **Action / Pose & Action** — the only creative variable per frame: posture, what the subject
   holds/does, the emotion ("crouched low on one knee inspecting a small icon", "mid-air
   celebratory leap holding a checkmark shield", "lounging in a simplified orange armchair,
   hands behind head"). One to two sentences; one clear idea per frame.
4. **Color Palette & Background / Composition** — canvas, accent colors, and the grounding
   elements that make a set feel related: [flat dark oval floor shadow], [large clean circle
   shape behind subject], [thin-line side table], [floating star particles], [subtle line-art
   geometric UI elements]. Reuse the grounding device (shadow oval) across every frame.

## Guard lines — the anti-drift leash

Image generators drift toward 3D, realism, and texture call by call. Every prompt carries the
negatives, in the style section, every time:

```text
Strictly 2D vector graphic art — no 3D rendering, no realistic materials, no raytracing,
no skin textures, no hyper-realism.
```

This is one sentence of insurance for the whole collection; omitting it "because the style is
already described" is how frame 7 comes back plastic.

## Reference-chaining

Description aligns a set; a reference image *locks* it:

- Frame 1 (the **style anchor**) is generated from text only, then human-reviewed as the style
  law of the project.
- Every later frame is generated image-to-image against the anchor (generator's reference/
  edit input — [ImageGen `images` param], [any img2img reference slot]), and its prompt swaps
  description for pointer: **"Matches the exact visual style and 2D character design of the
  reference image"** + **"The exact same stylized 2D cartoon character … from the reference
  image."**
- The Style DNA and guard lines STILL stay in the prompt — reference + text beats either alone.
- If the anchor changes (style approved later), every chained frame is a regeneration candidate;
  that is why the manifest records each frame's reference.

## Verbatim rule

Canon text is copied, never re-typed. Two near-miss copies ("blue trousers" vs "simple blue
flat trousers") is the seed of drift; the manifest's Style DNA / Character canon blocks are the
single source, and frame prompts are assembled from them (paste, then write the Action line).

## Hard rules vs soft rules

Two lists, different force:

- **Hard rules — what no image may contain.** Typical: "no text, no letters, no numbers, no real
  brand logos or site marks" (generated wordmarks and fake UI copy are the classic failures;
  brand marks make artwork legally and visually someone else's). These are **embedded in every
  prompt** and violations mean regenerate — no exceptions, no "it's just one letter".
- **Soft rules — what an image should aim for.** Dimensions/format (1024×1024 PNG, square 1:1),
  negative space, palette calmness, recurring grounding devices. Stated once in the manifest,
  enforced through the generation call's size parameter and in prompts where they fit naturally.
  A soft-rule miss is a judgment call, not a defect — never spend a regeneration on it alone.

Writing them separately keeps the collection honest: the hard list protects the brand and the
law, the soft list protects the taste.

## The placement contract

The manifest's first job after style is declaring **where the set lives and how code eats it**:
the folder ([`Resources/Images/Onboarding/`], [assets/illustrations/...], a glob-picked
directory that needs no project-file edit), and the **slot filenames the code already looks for**.
When code resolves `step1.png..step5.png` by name, the filenames are load-bearing: new artwork
for an existing slot is a same-named file dropped in — zero code changes; renaming, or adding a
slot, is the only event that edits code. Two consequences:

- "Save as" is usually dictated, not designed; the manifest records the code's name.
- A slot may legitimately map to **no image** (the picker UI is the illustration) — record it as
  `no-image`, so "all slots covered" stays true and nobody generates a decorative duplicate.

## Brand hexes belong in the Style DNA

Unlike application styling (where `styling`/`styleup` demand token indirection), a generation
prompt IS the source — spelling colors as brand literals ("warm cream #FDF6EC, blue #2386C8,
orange #FFA200") is correct there, taken once from the project's palette and copied verbatim
everywhere. The single-source rule still applies: hexes are edited in the Style DNA block, never
re-typed per frame.

## Sizing and save names

- Decide aspect once per usage (onboarding slides usually share one ratio; hero art another) and
  put it in the manifest header so every generation call matches.
- Save names carry frame order and meaning, in the project's asset path convention:
  `assets/illustrations/onboarding/02-welcome.png` — never `image_17.png` [or generator-default
  names]; the manifest's "Save as" is law. After generating, normal asset rules apply —
  `assets` covers format/naming cleanup.
