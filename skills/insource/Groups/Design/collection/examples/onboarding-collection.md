# Filled manifest excerpt — on-boarding.md

A real-shaped output of the skill. The mascot frames share one character; the knight example
shows the same file shape with a subject canon instead.

## on-boarding.md — mascot collection

- **Status:** style-confirmed — nothing pending
- **Style anchor:** `assets/illustrations/onboarding/01-inspect.png`
- **Aspect:** 1:1, PNG (soft rule below)

**Placement & integration:** ships to `assets/illustrations/onboarding/`; the carousel view
resolves images by slot name from an array, so `01-inspect.png`… are the filenames the code
looks for — replacing an image means dropping a same-named file, no code edit.

**Mapping:**

| Slot | File | Subject | Status |
|---|---|---|---|
| Slide 1 — "find what matters" | 01-inspect.png | character + magnifier over an icon | shipped |
| Slide 2 — "relax, it's free" | 02-welcome.png | lounging in orange armchair | shipped |
| Slide 3 — permissions | — | the permission sheet itself is the illustration | no-image |
| Completion — "you're in" | 03-success.png | mid-air leap, checkmark shield | shipped |

All four slides covered by three PNGs; nothing pending.

**Hard rules (embedded in every prompt):** no text, no letters, no numbers, no real brand logos
or app-store marks.
**Soft rules:** 1024x1024 PNG; generous negative space; the flat dark oval floor shadow appears
in every frame; confetti accents stay sparse.

**Style DNA (verbatim in every prompt):**
> Flat 2D vector brand illustration, modern tech art style, friendly corporate cartoon style,
> clean smooth geometric shapes, minimal shading, smooth solid colors. Strictly 2D vector
> graphic art — no 3D rendering, no realistic materials, no skin textures, no hyper-realism.
> Palette: solid bright green, vibrant blue, dark teal, orange highlights. Clean warm off-white
> canvas, flat dark shadow oval under the subject on the floor plane, subtle line-art geometric
> UI background elements.

**Character canon (verbatim):**
> Stylized 2D cartoon character with an exaggerated, simple silhouette. Bright orange hair,
> blocky facial features with a simple happy expression. Wears a solid vibrant green t-shirt and
> simple blue flat trousers.

| # | Frame | Use it in | Save as | Reference |
|---|---|---|---|---|
| 1 | 01-inspect | Onboarding slide 1 — "find what matters" | assets/illustrations/onboarding/01-inspect.png | — (anchor) |
| 2 | 02-welcome | Onboarding slide 2 — "relax, it's free" | assets/illustrations/onboarding/02-welcome.png | 01-inspect.png |
| 3 | 03-success | Completion screen — onboarding done | assets/illustrations/onboarding/03-success.png | 01-inspect.png |

The prompts below stay in the manifest for the regenerate-only-if-needed case — while a frame is
`shipped` nobody re-runs its prompt.

### Frame 1 — 01-inspect

**Prompt:**
- **Style:** [Style DNA text]
- **Character:** [Character canon text]
- **Action:** The character is crouched low on one knee in a playful, cartoonish posture, holding
  a large, simplified flat-vector magnifying glass to inspect a small icon on the floor.
- **Color Palette & Background:** Warm off-white canvas; solid bright green, vibrant blue, dark
  teal, orange highlights; flat dark shadow oval under the character; subtle line-art geometric
  UI background elements.

### Frame 2 — 02-welcome *(generated against 01-inspect.png)*

**Prompt:**
- **Style:** [Style DNA text] **Matches the exact visual style and 2D character design of the
  reference image.**
- **Character:** **The exact same** stylized 2D cartoon character with bright orange hair, green
  t-shirt and blue trousers from the reference image.
- **Action:** The character is lounging in a highly simplified, modern 2D orange armchair,
  leaning back happily with hands behind their head in a relaxed, friendly posture.
- **Color Palette & Background:** Warm off-white canvas; large clean 2D blue circle shape behind
  the chair; minimalist geometric laptop on a thin-line side table; flat dark shadow oval under
  the chair.

### Frame 3 — 03-success *(generated against 01-inspect.png)*

**Prompt:**
- **Style:** [Style DNA text] **Matches the exact visual style and 2D character design of the
  reference image.**
- **Character:** [Character canon text] — same person as the reference.
- **Action:** The character is depicted in a mid-air celebratory leap, holding up a sleek, 2D
  glossy green checkmark shield with both hands to celebrate onboarding completion.
- **Color Palette & Background:** Clean off-white background; flat dark oval floor shadow beneath;
  minimalist 2D geometric accents and small floating star particles framing the scene.

## A second collection, same file shape — protection.md (knight set)

No human mascot here — the **subject canon** is the knight itself, and it holds the verbatim slot:

> A stylized, friendly 2D cartoon knight; armor of clean simplified flat 2D vector shapes with
> soft inner grey and charcoal mesh gradients for a smooth, semi-curved look; cheerful minimal
> glowing visor.

Style DNA swaps family to premium 2D mesh gradient ("flat 2D vector art base — strictly no 3D
rendering…"), palette to dark forest green / deep navy / yellow accent stars, same grounding
oval shadow. Frames then vary only the Action line: "stands in a confident protective stance,
holding a stylized white envelope under one arm, a sleek silver-and-orange sword over the
shoulder" / "seals a glowing envelope…" etc. Two collections in one project never share a Style
DNA block — each file owns its own.
