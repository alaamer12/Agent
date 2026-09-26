---
name: create-video
argument-hint: <what the video is for, where it plays, how long>
description: Turn a vague video request into locked, numeric direction, then lay out, verify and deliver a professional video project. Loads after the hyperframes entry point has routed the job and written BRIEF.md, and never competes with it or the hyperframes domain skills. Converts the brief into six independent axes — genre, pacing, visual, camera, editing, tone — plus aspect, duration, audio and scenes, each resolving to numbers: cuts per minute, seconds per arrival, transition milliseconds, easing. scripts/spec.py validates the spec and derives a build sheet with a per-scene arrival budget; scripts/scaffold.py writes the project structure and passes hyperframes lint; scripts/qa.py gates the render on measurable thresholds — dead air, all-clips-at-t=0, dwell, loudness, true peak, safe-zone ink — and motion promises are measured on rendered frames. Use for launch, demo, explainer, ad, promo, reel, short or hero video when direction must be pinned, a project structured, or quality proven.
---

# Create Video

## Overview

The gap between "make me a video about our app" and a good video is not rendering
skill — it is that nobody pinned what the video is, and nothing structural
stopped a scene from freezing. This skill closes both gaps: it converts a brief
into numbers, and it lays the project out so the numbers are enforced by the files.

**Position in the ecosystem.** `/hyperframes` is the mandatory entry point. It owns
project state, the intent interview, `BRIEF.md`, and workflow routing. Do not run a
competing interview over a brief that already exists. This skill is the
**direction and structure layer** that runs after the job is routed, and it hands
every craft question to the skill that owns it:

| Question | Owner |
|---|---|
| Which workflow is this? What does the brief say? | `/hyperframes` |
| Composition contract — `data-*`, tracks, sub-comps, determinism | `/hyperframes-core` |
| Motion rules, scene blueprints, transitions, runtime adapters | `/hyperframes-animation` |
| Named keyframes, camera moves, FLIP, masks, SVG | `/hyperframes-keyframes` |
| Palette, typography, `frame.md`, narration, beat planning | `/hyperframes-creative` |
| Sourcing or generating images, icons, logos, audio, LUTs | `/media-use` |
| Mixing, ducking, gain automation, effect chains | `/hyperframes-audio` |
| Registry blocks — before hand-building any named look | `/hyperframes-registry` |
| Timeline layout, track kinds, safe zones in Studio | `/hyperframes-studio` |
| init / lint / check / snapshot / preview / render / publish | `/hyperframes-cli` |
| **Six-axis lock, build sheet, project scaffold, acceptance tests** | **this skill** |

```
BRIEF.md → lock six axes → video-spec.json → spec.py build sheet
        → scaffold.py → lint → fill the arrival slots (animation/creative)
        → check → qa.py quality gate → measure motion promises → render → deliver
```

### Conflict protocol

When this skill and a HyperFrames skill could both answer, the HyperFrames skill
answers. Four rules make that mechanical rather than a judgement call per turn:

1. **`/hyperframes` is the entry point and owns routing, the intent interview,
   `BRIEF.md`, the review loop, and the production loop.** This skill never runs a
   competing interview, never re-asks what `BRIEF.md` records, and never claims a
   route. It reads the route and continues from it.
2. **No craft is restated here.** Motion, design, audio, media, layout and CLI
   knowledge live in the owners above. If this skill needs one of those, it loads
   the owner. A paragraph here that duplicates an owner is a defect.
3. **Its own claims are the ones nobody made:** the six-axis numeric lock, the
   arrival budget, the scaffolded project shape, the measurable quality bar, the
   delivery matrix, and framework choice.
4. **On a direct contradiction, HyperFrames wins and this skill says so** — and
   reports the conflict, because two skills asserting the same ground is a bug to
   fix in one of them, not a coin flip at runtime.

## 0. Choose the framework

`/hyperframes` defaults to HyperFrames unless the user names another framework or
asks only to record a browser session. Keep that default; it is the right answer
for most of what this skill is asked to build. Flag the three cases where the
default costs them something, and hand the decision back:

| The job | A better fit | Why |
|---|---|---|
| Frames come from a live database or per-user data at render scale | Remotion / a code-driven pipeline | parametric rendering is its normal case |
| Concatenating, trimming, or re-muxing existing footage only | `ffmpeg` directly | no composition layer is needed |
| The deliverable must be a live, interactive page | WAAPI / CSS in the app itself | a render is the wrong medium |

Everything else — motion graphics, product and UI stories, typographic beats,
data-viz, composites over footage, decks, captioned clips — stays in HyperFrames
and continues at step 1. State the choice and the reason; never silently switch
frameworks mid-project.

## 1. Lock the six axes

Read `references/dimensions.md`. Six independent dials, each answering a different
question, and one word never settles two of them — *cinematic* is a visual style
and says nothing about pace.

```
Genre · Pacing · Visual style · Camera style · Editing style · Tone
```

Pacing is the axis with the arithmetic downstream: it fixes cuts per minute, the
seconds per arrival, and the transition band, and `spec.py` turns those into a
per-scene arrival count. Tone lands on the easing family. Camera decides whether a
camera rule is needed at all — `static` is a legitimate, cheap answer.

**A scene is not a shot.** A 9-second scene at moderate pacing is roughly three
arrivals inside one story beat, not one block held for nine seconds.

Ask only what the brief left open, in at most two batches of four
(`AskUserQuestion` caps at four questions, 2–4 options each), and put the number
in every option: `Fast — 24–45 cuts/min, shots 1.3–2.5s`. Never ask in bare
adjectives; route the user's adjectives through the word→axis table first. See
`references/interview.md`.

**Purpose, aspect, duration, and audio are never silently inferred.** If the user
declines to decide, decide from the genre defaults and say out loud what you chose.

## 2. Write the spec, get the build sheet

```bash
python3 scripts/spec.py --example > <project>/video-spec.json   # edit that
python3 scripts/spec.py <project>/video-spec.json
```

`spec.py` validates every enum and derives: canvas and frame count, cuts/min and
transition ms, **arrivals per scene**, whether the plan will read as stalled or as
frantic, which `hyperframes-animation` rules the camera and tone axes imply,
blueprint suggestions per role, and the verification block for each motion promise.

- **Errors block the build.** A structure that does not sum to the duration is a
  real contradiction, not a rounding matter.
- **Warnings are judgment calls.** Read each one out and say which way you resolved
  it. Never swallow one.
- Re-run after every correction — the numbers move with the axes.

A scene's `motion` promise states the direction the subject **travels**, never
where it comes from: a panel entering from the left edge travels **right**. That
convention is what makes the render testable. See `references/spec-template.md`.

## 3. Scaffold the project

```bash
npx hyperframes init <project>          # owns hyperframes.json, meta.json, package.json
python3 scripts/scaffold.py <project>/video-spec.json --project <project>
npx hyperframes lint .                  # 0 errors before authoring anything
```

`scaffold.py` writes the structure in `references/project-layout.md`: a root of
timed hosts only, one sub-composition per scene **pre-cut into its arrival slots**
(each a timed `.clip` with a labelled `fromTo` on the inner span, staggered across
the window, on the tone's easing), a single caption track, a decoration layer,
`assets/`, `frame.md`, and a `.gitignore` for generated output. Each scene file
opens with its intent, content, beat count, blueprint, and motion promise, so the
direction survives context compaction.

It refuses to run without `hyperframes.json` and never overwrites `index.html`
without `--force`.

If music drives the cut, detect the grid now — pacing against a beat grid, not a
guess: `npx hyperframes beats <project>`.

## 4. Fill the scenes

For each scene file, in order:

1. Read the design spec (`frame.md`) first and quote its tokens verbatim —
   `/hyperframes-creative` owns that contract, and its `house-style.md` plus
   `video-composition.md` are the two files it says to read before writing HTML.
2. Pick the shape from the build sheet: a blueprint for a multi-phase scene, or
   2–4 atomic rules. Load `/hyperframes-animation`; read the entry you chose.
   Before hand-building a named look (film grain, glitch, shimmer sweep, CRT),
   search `/hyperframes-registry` for the primitive.
3. **Fill every arrival slot the scaffold made.** The beat count is a floor, not a
   suggestion — a scene that leaves its slots empty is the failure this skill
   exists to prevent.
4. Re-lint per scene. `npx hyperframes check . --json` after each one beats
   discovering five problems at the end.

## 5. Verify against the spec

The spec is the acceptance criteria, not a mood board.

```bash
npx hyperframes check . --json --at-transitions     # lint, runtime, layout, motion, contrast
npx hyperframes snapshot . --at <times> --no-end -o snapshots/scene-NN
python3 scripts/motion.py snapshots/scene-NN/frame-00-at-<a>.png snapshots/scene-NN/frame-01-at-<b>.png
```

`spec.py` prints the exact times, this skill's own absolute `motion.py` path, and
each scene's promised direction — `scripts/motion.py` belongs to this skill, so
nothing here depends on any other skill being installed. A promise measured as
something else, or as `cannot-determine`, is a bug: fix the tween, never re-label
the promise. If motion cannot be measured for some reason, read the two snapshots
yourself and say you eyeballed it rather than implying it was measured.

Then `npx hyperframes preview .` and watch it at real speed — timing that reads
correctly in a still is often wrong in motion. Confirm the Studio row count too:
one decoration host, one row per scene, one caption row, audio rows. A wall of
unlabelled rows means scene markup leaked into the root.

## 6. Quality gate

`check` proves the composition is valid. The quality bar proves it is good enough
to ship — thresholds with numbers, in `references/quality-bar.md`.

```bash
python3 scripts/qa.py <project> --spec <project>/video-spec.json --video renders/master.mp4
```

`qa.py` reads the timeline out of the composition files and the pixels out of the
render: dead air between scenes, overlaps, whether the first scene opens at t=0,
whether every clip lands at t=0 (the strongest AI tell), arrival dwell, the
arrival budget against the spec, rendered duration / canvas / fps / audio presence,
integrated loudness and true peak, and safe-zone compliance measured as ink in the
outer 5% of the frame. It exits non-zero on a failure.

Then read the contact sheet against the tells list: one easing family everywhere,
everything centred, web-scale type, a transition on every cut, no rest before a
cut, a first frame that is a still. Fix what measures; judge what doesn't.

A warning is a decision — fix it or name it in the handoff. An unmentioned
warning is a defect shipped on purpose.

## 7. Deliver

```bash
npx hyperframes render . -o renders/master.mp4 -f <fps> -q delivery
```

One master, N derivatives, each from the composition rather than from a
transcode. Read `references/delivery.md` for the matrix, and remember a vertical
cut is a re-author, not a resize: safe zones tighten, two-column layouts die, and
the hook moves forward. Feed placements start muted, so the story must survive
silence.

Report axes, runtime, canvas, the `qa.py` result, arrivals measured against
arrivals implied, each motion promise's verdict, and anything that gave way.
Append that record to `video-spec.md`.

## Do not

- Run a second intent interview on top of an existing `BRIEF.md`, or claim a route.
- Restate the owning skills' motion, design, audio, media, or layout knowledge here.
- Build from an adjective. Unpinned means pin it or declare you inferred it.
- Let a scene ship with empty arrival slots.
- Trust `check` output while lint still errors — an error switches off the layout
  and contrast audits, and `0 samples` then reads as clean when nothing ran.
- Quietly re-label a motion promise to match a render that missed it.
- Hand off with an unresolved `qa.py` warning that you never named.
- Switch frameworks mid-project without saying why.

## Resources

- `references/dimensions.md` — the six axes and what each forces, word→axis
  routing, genre defaults, axis conflicts, aspect/platform coupling.
- `references/interview.md` — derive-then-ask, the four never-inferred slots,
  batching under the four-question cap, writing options as numbers, the lock.
- `references/spec-template.md` — `video-spec.json` field rules, the motion
  promise convention, what `spec.py` returns, the post-build verification record.
- `references/project-layout.md` — the tree, the four structural laws, host and
  transport-template contract, naming, what the scaffold pre-cuts and why.
- `references/quality-bar.md` — numeric acceptance thresholds for cut, read time,
  frame, and sound, plus the ten AI tells and how each is caught.
- `references/delivery.md` — master-and-derivatives matrix, the muted-first rule,
  loudness targets, captions, naming, and the pre-handoff pass.
- `scripts/spec.py` — validator + derivation engine (`--example`, `--json`); exit 1 on errors.
- `scripts/scaffold.py` — writes and pre-cuts the project from the spec (`--dry-run`, `--force`).
- `scripts/qa.py` — the measurable quality gate over timeline, render, and pixels.
- `scripts/motion.py` — this skill's own frame-to-frame direction measurement, so
  verification never depends on another skill being installed.
