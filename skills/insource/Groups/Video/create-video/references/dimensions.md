# The Six Axes

Six independent dials. A video is one value from each, and **each axis answers a
different question** — never let one word settle two of them.

```
Video
├── Genre          what the video IS          → viewer's expectations, structure
├── Pacing         how fast it MOVES          → cuts/min, shot seconds, transition ms
├── Visual style   how it LOOKS               → palette, depth, grain, letterbox
├── Camera style   how the FRAME BEHAVES      → which camera rules the build needs
├── Editing style  how SHOTS JOIN             → cut character, transition family
└── Tone           how it FEELS               → easing family, hold length
```

The orthogonality law: *cinematic* is not a genre. An educational video, a
documentary, an advertisement and a vlog can all be cinematic. If the user says
"cinematic", that settles `visual_style` and tells you nothing about the other
five — ask or infer them separately.

## Genre — what kind of video is it?

`educational` `documentary` `tutorial` `vlog` `interview` `news` `commentary`
`review` `storytelling` `comedy` `drama` `action` `horror` `thriller` `romance`
`advertisement` `product_showcase` `cinematic` `music_video` `short_film`
`animation` `explainer` `motivational` `gaming` `reaction` `travel` `cooking`
`fitness` `podcast` `announcement`

Genre fixes **what the structure must contain** — a `tutorial` owes a
step-by-step body, an `advertisement` owes a hook and a CTA, a `documentary`
owes a thesis and evidence. It does not fix how fast it cuts or how it looks.

## Pacing — how fast does it move?

| Value | Cuts/min | Shot length | Transition | What the viewer feels |
|---|---|---|---|---|
| `very_slow` | 2–6 | 10–30 s | 900–1600 ms | meditative; each shot is sat in |
| `slow` | 6–12 | 5–10 s | 600–1000 ms | calm; gradual reveals, long holds |
| `moderate` | 12–24 | 2.5–5 s | 350–600 ms | conversational; one idea per shot |
| `fast` | 24–45 | 1.3–2.5 s | 150–350 ms | energetic; little is held, arrivals are sharp |
| `very_fast` | 45–90 | 0.5–1.3 s | 60–150 ms | relentless; density is the point |

Pacing is the axis with the most downstream arithmetic, so it is never left
implied. It sets how many arrivals a scene must contain: `spec.py` divides each
scene's window by the band's midpoint and reports the beat count per scene.

**A scene is not a shot.** A 9-second scene at `moderate` pacing is not one
static block for 9 seconds — it is ~2–3 arrivals inside one beat of the story.

## Visual style — how does it look?

`cinematic` `realistic` `minimal` `animated` `handheld` `stylized` `flat`
`editorial`

This is art direction: colour range, depth simulation, grain, letterboxing,
focus falloff. It is not motion — a `flat` design can cut at `very_fast`.

## Camera style — how does the frame behave?

`static` `handheld` `tracking` `drone` `closeup` `wide` `mixed`

This decides whether the build needs a virtual-camera rule at all:

| Value | Rules to read in hyperframes-animation |
|---|---|
| `static` | none — motion must come from inside the frame |
| `handheld` | `sine-wave-loop` (drift on the world wrapper) |
| `tracking` | `camera-cursor-tracking`, `nudge-curve` |
| `drone` | `3d-camera-flight`, `viewport-change` |
| `closeup` | `coordinate-target-zoom`, `depth-of-field-blur` |
| `wide` | `multi-phase-camera`, `viewport-change` |
| `mixed` | `multi-phase-camera`, `coordinate-target-zoom` |

`static` is a real answer and a cheap one; do not add camera motion to satisfy a
brief that never asked for it.

## Editing style — how do shots join?

`long_takes` `standard_cuts` `jump_cuts` `montage` `rapid_cuts` `mixed`

| Value | Cut character | Transition family |
|---|---|---|
| `long_takes` | few cuts, motion inside the frame carries it | dissolve or none |
| `standard_cuts` | clean cuts on idea boundaries | short dissolve or hard cut |
| `jump_cuts` | same framing, content jumps forward | hard cut |
| `montage` | compressed sequence of fragments | hard cut, occasional wipe |
| `rapid_cuts` | cuts on beats, sub-second shots | hard cut only — dissolves read as mush |

Editing style and pacing are separate: `montage` at `slow` pacing is a gentle
flow of long fragments; `rapid_cuts` at `very_fast` is a trailer.

## Tone — how does it feel?

`calm` `energetic` `serious` `funny` `emotional` `mysterious` `inspirational`

Tone lands on the **easing**, which is where "professional" is actually decided:

| Value | Easing behaviour |
|---|---|
| `calm` | `sine.inOut` / `power1` — slow in, slow out, long holds |
| `energetic` | `back.out` / `power4` — overshoot, snap, short holds |
| `serious` | `power2` — no overshoot, no bounce, deliberate |
| `funny` | `elastic.out` / `back.out` — overshoot and settle; timing is the joke |
| `emotional` | `sine.inOut` over long durations — slow reveals, soft landings |
| `mysterious` | `power1.in` — things arrive late; holds outlast comfort |
| `inspirational` | `power3.out` — fast start, long glide into the rest |

## Word → axis disambiguation

Users hand you adjectives. Route each one to exactly one axis; if it touches two,
split it and say so.

| They say | It settles | It does NOT settle |
|---|---|---|
| "cinematic" | visual_style | genre, pacing |
| "punchy" | pacing (fast) + editing (rapid/hard cuts) | tone |
| "energetic" | tone | pacing — check it separately |
| "calm" | tone + usually slow pacing | visual_style |
| "dynamic camera" | camera_style | genre |
| "modern / clean" | visual_style (minimal) | pacing |
| "fast-paced" | pacing | editing_style |
| "story-driven" | genre (storytelling) | tone |
| "like Apple" | visual_style + tone | genre, duration |
| "makes me want to buy it" | genre (advertisement) + purpose | everything else |

## Defaults by genre

Propose these; never silently apply them. Each one still needs confirming
against the user's stated purpose.

| Genre | Pacing | Visual | Camera | Editing | Tone |
|---|---|---|---|---|---|
| educational | moderate | minimal | static | standard_cuts | calm |
| explainer | moderate | flat | static | standard_cuts | calm |
| documentary | slow | realistic | handheld | long_takes | serious |
| tutorial | moderate | minimal | closeup | jump_cuts | calm |
| advertisement | fast | cinematic | mixed | rapid_cuts | energetic |
| product_showcase | moderate | minimal | tracking | standard_cuts | inspirational |
| vlog | moderate | realistic | handheld | jump_cuts | funny |
| motivational | slow | cinematic | wide | montage | inspirational |
| gaming | very_fast | stylized | mixed | rapid_cuts | energetic |
| travel | slow | cinematic | drone | montage | emotional |
| cooking | moderate | realistic | closeup | jump_cuts | calm |
| review | moderate | editorial | static | standard_cuts | serious |
| announcement | fast | minimal | tracking | standard_cuts | energetic |

## When axes fight

Contradictions are information — surface them rather than averaging them away.

| Combination | Read it as | Do |
|---|---|---|
| `documentary` + `very_fast` | a trailer, not a film | confirm which one they meant |
| `calm` tone + `rapid_cuts` | uneasy; hard cuts undercut calm | propose `standard_cuts`, keep the tone |
| `slow` pacing + 15 s duration | 3 shots maximum — very little story fits | raise duration or speed pacing |
| `static` camera + `drone`-shaped brief ("fly over the city") | they want motion, chose the wrong axis | move to `drone` or `wide` |
| `very_fast` + dissolves | dissolves smear a fast cut | force hard cuts |

The tie-breaker is always **purpose**: the thing the viewer must know, feel, or
do. When two axes cannot both hold, the one serving the purpose wins and the
other yields — and you say which gave way.

## Aspect and platform coupling

Aspect is not cosmetic; it changes what the structure can carry.

| Aspect | Where it plays | What it forces |
|---|---|---|
| `9:16` | Shorts, Reels, TikTok | hook inside 1.5 s, text in the upper two thirds, burned-in captions, no small detail |
| `1:1`, `4:5` | feed video | one subject centred; multi-column layouts stop working |
| `16:9` | YouTube, embeds, decks | the only ratio that comfortably carries side-by-side comparison |
| `21:9` | hero web embeds | letterboxed already — do not add bars |

Sound is a structure question, not a nice-to-have: on `9:16` most viewers start
muted, so a `voiceover`-dependent beat needs captions or on-screen text to survive
without audio.
