# ASCII prototype

> **Connections** (paths are relative to `references/`)
> - Read when: phase 4: writing the prototype spec or building the options file.
> - Skip when: traditional style, or no options are being shown.
> - Read next: `prototype-html.md` (if any option is marked needs_html); `review-standards.md` (to review the spec before showing it).

The default way to present creative options. One HTML file with one section per option; each option shows its animation as a sequence of ASCII states over time, so the user can see how it progresses before anything is implemented.

## Contents
- What the user sees
- The spec file
- Drawing rules
- Frame cadence
- Transitions and pairs
- Synchronization lanes
- Worked frame example
- Running the scripts
- Manual fallback

## What the user sees

Each option section contains: name, concept, feel, technique tags, synchronization form, duration and easing, a lane strip when several elements are involved, and for each sequence a list of timestamped ASCII frames. A Play button steps through the frames at their real timing (with a speed control). Frames stay visible as static text, so the file works without scripts.

## The spec file

The prototype is generated from a JSON spec. Write the spec, validate it, then build.

```json
{
  "title": "Save button - micro animation options",
  "target": "SaveButton.tsx",
  "command": "micro",
  "tier": "rare",
  "options": [
    {
      "id": "A",
      "name": "Label rolls into a check",
      "concept": "The label slides up out of a clipped window while a check draws itself in.",
      "feel": "Precise and satisfying",
      "techniques": ["mask", "line drawing"],
      "sync": "domino",
      "interactive": false,
      "timing": { "duration_ms": 360, "easing": "cubic-bezier(0.22, 1, 0.36, 1)" },
      "properties": ["transform", "opacity", "stroke-dashoffset"],
      "reduced_motion": "Crossfade label to check, no movement.",
      "risk": "Needs a fixed button width to avoid layout shift.",
      "needs_html": false,
      "sequences": [
        { "label": "forward", "frames": [
          { "t": 0,   "art": "[  Save  ]", "note": "rest" },
          { "t": 120, "art": "[  ^^^^  ]", "note": "label exits upward" },
          { "t": 360, "art": "[   ok   ]", "note": "check drawn" }
        ] },
        { "label": "reverse", "frames": [
          { "t": 0,   "art": "[   ok   ]" },
          { "t": 160, "art": "[  Save  ]" }
        ] }
      ],
      "lanes": [
        { "element": "Label", "start": 0, "end": 160, "technique": "slide out" },
        { "element": "Check", "start": 120, "end": 360, "technique": "line drawing" }
      ]
    }
  ],
  "recommendation": { "option": "A", "reason": "Fits the rare tier and confirms in place." }
}
```

Field rules
- `command` is `micro`, `component` or `transition`. `tier` is `routine`, `rare` or `showcase`.
- `timing.duration_ms` must fit the tier cap (300, 600 or 1600) or carry a `duration_exception` string explaining why.
- `properties` lists what actually animates. Layout properties are errors unless `layout_exception` explains a deliberate container tween.
- `reduced_motion` is required for every option.
- Every option of a `transition` command needs a `forward` and a `reverse` sequence (labels may add detail, for example `forward: step 1 to 2`).
- `needs_html` with `html_reason` marks an option ASCII cannot convey. `demo_html` is added only when the user chooses a live prototype.
- `lanes` are optional; use them whenever more than one element animates.

## Drawing rules

- Use a fixed canvas for the whole option (same columns and rows in every frame). A frame that changes size looks like a layout change instead of an animation.
- Draw with monospace box characters (`┌ ─ ┐ │ └ ┘`) or plain ASCII (`+ - |`). Keep to one style per file.
- Show position by shifting the drawing inside the canvas. Show scale by changing the box size. Show opacity with fill density: `░` faint, `▒` half, `▓` strong, solid text for full, dotted borders for ghosted.
- Show blur with a trail or dotted edge (`·`), clipping with a cut edge, and rotation or 3D with a skewed outline and a short label.
- Label each frame with its time in milliseconds and, where useful, a short note on what is happening.
- Mark origin points and directions with arrows (`→ ↑ ↓ ←`) outside the artwork when direction is the point.
- Keep the artwork abstract. The goal is to communicate timing, order and movement, not to draw the final UI.

## Frame cadence

- Place frames at beats, not at even intervals: the start, the moment each element starts or finishes, the peak (an overshoot, a hold), and the end.
- Always include `t = 0` and the final resting state.
- Use roughly 4 to 9 frames per sequence. Fewer cannot show progression; more becomes noise.
- A spring with overshoot needs a frame at the peak and one after the settle.

## Transitions and pairs

Every transition option shows two sequences, forward and reverse, side by side in the page. The reverse is designed, not assumed: show its own timing and frames. For components show enter and exit; for micro animations show press and release or hover in and out when both matter.

## Synchronization lanes

When several elements animate, add `lanes`. The build renders a strip showing who starts and ends when:

```text
Label  ████████░░░░░░░░░░░░   0-160ms   slide out
Check  ░░░░██████████████░░   120-360ms line drawing
```

This is how domino order, instant sync and linked propagation become readable in ASCII. For linked relationships, add one lane per hop group (source, neighbors, distant) with their offsets.

## Worked frame example

```text
0ms          50ms              100ms
┌─────────┐        ┌─────────┐              ┌─────────┐
│ Button  │        │ Button  │              │ Button  │
└─────────┘        └─────────┘              └─────────┘
```

In a spec these are three frames of one sequence, each with its own `t` and `art`. Position inside the canvas carries the movement.

## Running the scripts

```bash
python scripts/validate_spec.py spec.json
python scripts/build_prototype.py spec.json --out .animate/prototypes/save-button-micro.html
```

Fix every validator error before building. The builder refuses an invalid spec. Report the output path to the user.

## Manual fallback

If scripts cannot run, write the same content directly as an HTML file with one section per option and timestamped ASCII frames in preformatted blocks, following the same rules.
