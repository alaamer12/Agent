# <Usage> Artwork — <project name>

<!-- Copy to <usage>.md (e.g. on-boarding.md) in the project. Fill every <placeholder>; delete
     this comment. Style DNA, Character canon and Hard rules are copied VERBATIM into each
     prompt. Leave shipped artwork alone — prompts exist only for slots that need (re)generation. -->

- **Status:** <style-confirmed / nothing-pending / N frames pending>
- **Style anchor:** <path of first approved image, or "none yet">

## Placement & integration

- **Folder:** `<Resources/Images/Onboarding/>` — <how the build consumes it, e.g. "the csproj
  glob picks PNGs up automatically; no project-file edit needed">
- **Filenames are the contract:** the code looks up <where: enum/map/resource names>. New artwork
  for an existing slot = a same-named file dropped in; renaming or adding a slot is the only
  change that touches code.
- **Regeneration recipe:** produce at <dimensions/format from Soft rules>, save under the slot's
  name, done.

## Mapping (slot -> file -> subject -> status)

| Slot / screen | File | Subject | Status |
|---|---|---|---|
| <step 1 — "monitor projects as they publish"> | <step1.png> | <satellite dish> | <shipped> |
| <step 2 — "instant alerts"> | <step2.png> | <bell> | <shipped> |
| <step 5 — platform picker> | — | <the picker UI is the illustration> | <no-image> |
| <step 6 — "ready?"> | <step5.png> | <reused final scene> | <reused> |

<Close with the honest total: "All N steps covered by M shipped files; nothing pending." /
"Pending: <slots>." Statuses: shipped / replaced / reused / no-image / pending.>

## Shared Style (Style DNA — verbatim in every prompt)

> <Medium + mood + shape language, e.g. "Flat vector illustration, warm cream background
> (#FDF6EC). Accent palette: <brand blue> (#2386C8) and <brand orange> (#FFA200), teal detail
> (#1B7A5A). Soft elliptical dark ground shadow. Small geometric confetti — dots, plus signs,
> short squiggles. Generous negative space, thick clean shapes, minimal shading. Strictly 2D —
> no 3D rendering, no realistic materials, no skin textures.">

## Character canon (verbatim; omit if the set has no recurring subject)

> <"Same character throughout: young man, orange hair, dark-green t-shirt (#1B5E47), navy
> trousers (#1E2A4A), white sneakers." — or the subject-canon sentence for mascot/knight sets.>

## Hard rules (NO image may contain these — embedded in every prompt)

- <No text, no letters, no numbers.>
- <No real brand logos or site marks.>
- <...project-specific: no faces of real people, no religious symbols, ...>

A violation here is a defect: regenerate the image, embedded rule stays.

## Soft rules (recommended — aim, don't force)

- <Dimension/format: 1024x1024 PNG, square 1:1.>
- <Composition: generous negative space, calm palette, one focal object.>
- <Consistency: same ground-shadow device in every frame.>

A violation here is a judgment call, not a defect.

## Frames needing prompts (regenerate-only-if-needed)

<!-- One block per slot with Status pending/replaced/pending-optional. Shipped slots get NO
     prompt block. Reference: the anchor path once it exists. -->

### <step4.png> — <search/filter scene>

**Use it in:** <Onboarding step 4 — "search smartly">
**Save as:** `<Resources/Images/Onboarding/step4.png>` (slot name from the mapping)
**Reference:** <anchor path / none — this frame defines the style>

**Prompt:**

- **Style:** [Style DNA text] [Hard rules text]
- **Character:** [Character canon text] / "**The exact same** character from the reference image"
  when chaining.
- **Action:** <this frame's pose + subject interaction, one clear idea>
- **Color Palette & Background:** <shared palette + frame-specific composition notes>
