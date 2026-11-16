---
name: create-video
version: 1.1.0
author: Amr
specialized: hyperframes
description: 'Turn a vague video request into locked, numeric direction, then lay out, verify and deliver a professional video project. Loads after the hyperframes entry point has routed the job and written BRIEF.md, and never competes with it or the hyperframes domain skills. Converts the brief into six independent axes — genre, pacing, visual, camera, editing, tone — plus aspect, duration, audio and scenes, each resolving to numbers: cuts per minute, seconds per arrival, transition milliseconds, easing. scripts/spec.py validates the spec and derives a build sheet with a per-scene arrival budget; scripts/scaffold.py writes the project structure and passes hyperframes lint; scripts/qa.py gates the render on measurable thresholds — dead air, all-clips-at-t=0, dwell, loudness, true peak, safe-zone ink — and motion promises are measured on rendered frames. Use for launch, demo, explainer, ad, promo, reel, short or hero video when direction must be pinned, a project structured, or quality proven.'
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
answers — the four rules that make that mechanical, including what this skill is
entitled to claim as its own: `references/conflict-protocol.md`.

## Preflight — HyperFrames must be installed (hard gate)

**Nothing in this skill runs before this check passes — not the axis lock, not
`spec.py`, not the scaffold.** Verify the HyperFrames skills are actually present.
If they are missing, stop with the exact install command and ask before installing
on the user's behalf; if the user declines, say this skill cannot responsibly run
and stop — no hand-rolled substitute pipeline. Procedure: `references/preflight.md`.

## 0. Choose the framework

`/hyperframes` defaults to HyperFrames unless the user names another framework or
asks only to record a browser session. Keep that default; it is the right answer
for most of what this skill is asked to build. The three jobs where the default
costs them something, and the better fit for each: `references/framework-choice.md`.
State the choice and the reason; never silently switch frameworks mid-project.

## 1. Lock the six axes

Read `references/dimensions.md`. Six independent dials, each answering a different
question, and one word never settles two of them — *cinematic* is a visual style
and says nothing about pace.

```
Genre · Pacing · Visual style · Camera style · Editing style · Tone
```

Pacing carries the arithmetic downstream, tone lands on the easing family, camera
decides whether a camera rule is needed at all, and a scene is not a shot — with
the word→axis table and genre defaults in `references/dimensions.md`.

Ask only what the brief left open, in at most two batches of four, numbers in
every option and never a bare adjective; purpose, aspect, duration and audio are
never silently inferred: `references/interview.md`.

## 2. Write the spec, get the build sheet

```bash
python3 scripts/spec.py --example > <project>/video-spec.json   # edit that
python3 scripts/spec.py <project>/video-spec.json
```

- **Errors block the build.** A structure that does not sum to the duration is a
  real contradiction, not a rounding matter.
- **Warnings are judgment calls.** Read each one out and say which way you resolved
  it. Never swallow one.
- Re-run after every correction — the numbers move with the axes.

Field rules, what `spec.py` returns, and the motion-promise convention that makes
the render testable: `references/spec-template.md`.

## 3. Scaffold the project

```bash
npx hyperframes init <project>          # owns hyperframes.json, meta.json, package.json
python3 scripts/scaffold.py <project>/video-spec.json --project <project>
npx hyperframes lint .                  # 0 errors before authoring anything
```

`scaffold.py` writes the structure in `references/project-layout.md`, pre-cut into
arrival slots; it refuses to run without `hyperframes.json` and never overwrites
`index.html` without `--force`.

If music drives the cut, detect the grid now — pacing against a beat grid, not a
guess: `npx hyperframes beats <project>`.

## 4. Fill the scenes

For each scene file, in order: design tokens first, the shape from the build sheet,
**every arrival slot filled**, re-lint per scene. The full order and what each step
loads from the owning HyperFrames skill: `references/authoring.md`.

## 5. Verify against the spec

The spec is the acceptance criteria, not a mood board. `spec.py` prints the exact
`check` / `snapshot` / `motion.py` commands — the times, this skill's own absolute
`motion.py` path, and each scene's promised direction. What a mismatched or
`cannot-determine` promise means, and the preview and Studio row checks, are in
`references/authoring.md`, which carries the command block verbatim.

## 6. Quality gate

`check` proves the composition is valid. The quality bar proves it is good enough
to ship — thresholds with numbers, in `references/quality-bar.md`.

```bash
python3 scripts/qa.py <project> --spec <project>/video-spec.json --video renders/master.mp4
```

What `qa.py` reads out of the timeline and the pixels, and the contact-sheet pass
against the tells list: `references/quality-bar.md`. A warning is a decision — fix
it or name it in the handoff. An unmentioned warning is a defect shipped on purpose.

## 7. Deliver

```bash
npx hyperframes render . -o renders/master.mp4 -f <fps> -q delivery
```

One master, N derivatives, each from the composition rather than from a transcode.
A vertical cut is a re-author, not a resize, and feed placements start muted. The
matrix, the handoff report and the record it appends: `references/delivery.md`.

## Do not

- Run any step of this pipeline before the Preflight gate confirms the
  HyperFrames skills are installed — and never substitute a hand-rolled
  pipeline when the user declines to install.
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

| Path | Load when / what it is |
|---|---|
| `references/conflict-protocol.md` | the four ownership rules; who wins a contradiction, and what this skill may claim |
| `references/preflight.md` | before any step: the install gate — check, stop with the exact fix, continue only when visible |
| `references/framework-choice.md` | the `/hyperframes` default, the three jobs it fits badly, and what to hand back |
| `references/dimensions.md` | the six axes and what each forces, word→axis routing, genre defaults, axis conflicts, aspect/platform coupling |
| `references/interview.md` | derive-then-ask, the four never-inferred slots, batching under the four-question cap, writing options as numbers, the lock |
| `references/spec-template.md` | `video-spec.json` field rules, the motion promise convention, what `spec.py` returns, the post-build verification record |
| `references/project-layout.md` | what the scaffold writes, the tree, the four structural laws, host and transport-template contract, naming, what the scaffold pre-cuts and why |
| `references/authoring.md` | the per-scene authoring order and the verification pass: snapshots, `motion.py` verdicts, preview, Studio rows |
| `references/quality-bar.md` | numeric acceptance thresholds for cut, read time, frame, and sound, what `qa.py` measures, plus the ten AI tells and how each is caught |
| `references/delivery.md` | master-and-derivatives matrix, the muted-first rule, loudness targets, captions, naming, and the pre-handoff pass |
| `scripts/spec.py` | validator + derivation engine (`--example`, `--json`); exit 1 on errors |
| `scripts/scaffold.py` | writes and pre-cuts the project from the spec (`--dry-run`, `--force`) |
| `scripts/qa.py` | the measurable quality gate over timeline, render, and pixels |
| `scripts/motion.py` | this skill's own frame-to-frame direction measurement, so verification never depends on another skill being installed |
