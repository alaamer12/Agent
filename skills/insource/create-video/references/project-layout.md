# Project Layout

The structure `scripts/scaffold.py` writes, and why each piece sits where it
does. Every rule here comes from the framework's own conventions — `hyperframes.json`
declares the paths, `/hyperframes-studio` owns the timeline shape,
`/hyperframes-core` owns the file contract, `/hyperframes-creative` owns `frame.md`.

## The tree

```
<project>/
├── index.html                        root composition — timed hosts and nothing else
├── hyperframes.json  meta.json  package.json      init owns these; never hand-write
├── video-spec.json  video-spec.md   create-video's locked direction
├── frame.md                         design tokens (frontmatter is normative)
├── compositions/
│   ├── scenes/01-hook.html          one sub-composition per scene, numbered in order
│   ├── decorations/ambient.html     grain, vignette, glow, tint, hairlines
│   ├── captions.html                THE one caption track
│   └── components/                  registry-installed parts (`hyperframes add` writes here)
├── assets/
│   ├── media/  icons/  logos/  fonts/  audio/
├── snapshots/  renders/  beats/  .hyperframes/     generated; gitignored
```

`compositions/`, `compositions/components/` and `assets/` are not a taste call —
they are the `paths` block that `hyperframes init` writes into `hyperframes.json`,
so the registry's `add` and `catalog` commands land there. Everything else is
directory discipline on top of that.

## The four structural laws

1. **Every scene is its own sub-composition.** The root holds only timed hosts.
   Nested markup left in the root does not become its own Studio row — it hides
   inside one opaque block that cannot be trimmed or moved part by part.
2. **One caption track.** All caption groups live in `compositions/captions.html`,
   in order, under a single host marked `data-track-kind="captions"`. Never one
   row per caption group, never captions sharing a track with graphics.
3. **One element kind per track.** `data-track-kind` is `graphics` for scenes and
   decorations, `captions` for the caption host; `video` and `audio` come from the
   tag itself. The `data-track-index` number is a display lane only — it never
   changes what renders on top. Layering is CSS's job.
4. **Safe zones.** Action-safe is 90% of the frame (5% inset): everything visible
   stays inside it. Title-safe is 80% (10% inset): captions and key content stay
   inside it. Guides live in the Studio preview overlay — never as elements in the
   composition HTML.

## Host and file contract

A host carries the timing and the geometry, and nothing else:

```html
<div id="scene-01" data-composition-id="scene-01"
     data-composition-src="compositions/scenes/01-hook.html"
     data-start="0" data-duration="4" data-track-index="1" data-track-kind="graphics"
     data-width="1920" data-height="1080"></div>
```

The scene file is a **transport template**: the runtime clones only what is
inside `<template>`, so its `<style>` and `<script>` must be in there — a `<head>`
style is silently dropped.

```html
<body>
  <template>
    <style>#root { position: absolute; inset: 0; }</style>
    <div id="root" data-composition-id="scene-01" data-width="1920" data-height="1080">…</div>
    <script>
      const tl = gsap.timeline({ paused: true });
      window.__timelines["scene-01"] = tl;
    </script>
  </template>
</body>
```

- Host slot id, inner `data-composition-id`, and the `window.__timelines["…"]`
  key are **the same string**. A mismatch is accepted silently and breaks at render.
- Style the sub-composition root as `#root`, never by class
  (`subcomposition_root_styled_by_class`), and size it with `inset: 0` — pixel
  dimensions belong on `data-width`/`data-height`.
- Keep ids unique across the assembled page by prefixing them with the
  composition id (`#scene-01-beat-2`).
- A standalone `index.html` root sits directly in `<body>` with **no** `<template>`
  wrapper — wrapping it is an error, not a style choice.

## What the scaffold pre-cuts, and why

Each generated scene file already contains the **arrival slots its pacing
implies** — `beats = scene_seconds ÷ pacing midpoint` — as separate timed `.clip`
blocks with a `fromTo` entrance on the inner `<span>`, staggered across the
window, using the tone's easing and the pacing's transition length.

That is the whole anti-frozen-frame mechanism, made structural: the file cannot
be filled in as one static block, because the block slots are already there and
each one is labelled with its beat number and the intent it serves. The header
comment carries the scene's intent, content, blueprint suggestion, and motion
promise, so the direction survives context compaction.

The tweens animate the `<span>` inside each `.clip`, never the clip itself —
the framework owns clip visibility and lint rejects a visibility tween on a clip.

## Naming

- Scenes: `NN-<role>.html`, zero-padded, ordered — the filename is the timeline
  position, so a reorder is a rename and shows up in `git diff`.
- Compositions inside: `scene-NN`; decoration hosts `decorations-<treatment>`;
  caption groups stay inside `captions.html`.
- Assets: `assets/<kind>/<name>.<ext>`, named for what they are, not for which
  scene first used them — shared assets are shared.

## Generated output stays out of the repo

`snapshots/`, `renders/`, `beats/`, `.hyperframes/`, `node_modules/` are build
artifacts. The scaffold writes the `.gitignore` for them. Re-rendering must never
produce a diff.

## Three things to know about the scaffold

- **GSAP loads from the framework's pinned CDN URL**, exactly as `hyperframes init`
  scaffolds it. That is the contract the renderer expects, so the scaffold keeps
  it; it is also an unsigned third-party script. For an offline or air-gapped CI
  render, vendor the file into `assets/fonts`-adjacent storage and rewrite the tag —
  and say so in the run summary, because it changes the render input.
- **Two `fromTo` calls on one target need `immediateRender: false` on the later
  one.** GSAP applies a `fromTo` from-state at authoring time, so the last-written
  from-state silently becomes the element's resting state for any seek before the
  first tween runs. `lint` flags this as `gsap_repeated_fromto_without_baseline`.
  A directional arrival is exactly two `fromTo` calls on one span — opacity, then
  travel — so the travel tween always carries the flag.
- **`scaffold.py` refuses to overwrite `index.html` without `--force`**, and
  refuses to run at all unless `hyperframes.json` exists. `init` owns the project
  identity files; this script owns the composition shape.

## Verifying the layout

```bash
npx hyperframes lint .        # static contract; 0 errors AND 0 warnings before authoring
npx hyperframes check . --json --at-transitions   # runtime, layout, motion, contrast
npx hyperframes timeline --json                   # what is actually on the timeline
```

`lint` catches per-file violations; it **cannot** prove the cross-file mount
contract, so `check` is not optional once scenes exist. And a lint *error*
switches off the layout and contrast audits — `check` then reports `0 samples`
and looks clean while nothing ran. Clear lint first, always.

`check --json` prints `[INFO]` lines before the payload, so parse from the first
`{`, not from line 1.

Snapshots land as `snapshots/frame-NN-at-<time>s.png`, where **NN counts across
the whole run**, so a six-time call produces `frame-00` … `frame-05`, not three
`frame-00/01` pairs. Snapshot each measured pair into its own `-o` directory and
the indices stay `00` and `01` — which is what `spec.py` emits.

Then open Studio and count the rows: one decoration host, one row per scene, one
caption row, the audio rows. A wall of unlabeled rows means scene markup leaked
into the root.

## What this layout was verified against

Scaffolding the example spec and running the loop produced: `lint` 0 errors 0
warnings across 8 files, `check` ok with runtime 0, layout 0 and contrast 5/5, and
three measured motion promises returning `in-place` (0.99), `right` (0.82) and
`top` (0.84) exactly as specified. That run is the reference for what "clean"
looks like — not a claim that any future scaffold is exempt from checking.

