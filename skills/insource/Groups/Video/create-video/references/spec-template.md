# The Spec Artifact

Two files, both committed next to the composition, both written before any
timeline exists:

```
<project>/
├── video-spec.json    the machine contract — spec.py validates and derives from it
└── video-spec.md      the human contract — purpose, axes, scenes, decisions
```

`video-spec.json` is authoritative. `video-spec.md` explains the *why* that the
JSON cannot hold: what was rejected, what was inferred, what gave way when two
axes fought.

## Starting point

```bash
python3 scripts/spec.py --example > video-spec.json
```

Edit that. Do not hand-write the JSON from scratch — the example is the shape
`spec.py` expects.

## Field rules

| Field | Rule |
|---|---|
| `title` | working title; fine to be provisional |
| `purpose` | **one sentence**, and it must be testable: what the viewer knows, feels, or does after. "Looks cool" is not a purpose. |
| `audience` | who is watching, in their words, not a demographic |
| `aspect` | one of `16:9 9:16 1:1 4:5 4:3 3:2 16:10 21:9` — set by where it plays |
| `duration_seconds` | the target, and `structure` must sum to it within 5% |
| `fps` | `24 25 30 50 60 120 240`; 30 is the default, 24 for filmic, 60 for UI demos |
| `audio` | `none`, `music`, `voiceover`, `music+voiceover`, `music+sfx`, `voiceover+sfx`, `music+voiceover+sfx` |
| `language` | the on-screen text and caption language |
| `dimensions` | all six axes, every one pinned — see `dimensions.md` |
| `structure` | ordered scenes; each needs `role`, `intent`, `seconds`, `content` |
| `assets` | paths to logo, footage, fonts, music. Missing entries are the build's blockers. |
| `constraints` | brand colours, must-include, must-avoid, deadline |

### Scene fields

- `role` — one of the canonical roles (`hook`, `pain_point`, `product_intro`,
  `feature_showcase`, `benefit_highlight`, `social_proof`, `demo`, `cta`,
  `branding`, `segment`) or a listed alias. The role selects the blueprint menu.
- `intent` — what this beat must do **to the viewer**. Not a description of the
  shot; the shot is `content`. "Make the cost of the status quo visible" is an
  intent; "show a dashboard" is content.
- `seconds` — the window. `spec.py` divides it by the pacing band to get the
  scene's arrival count.
- `content` — what is actually on screen: the words, the UI, the figure. `[slot]`
  means it is still unwritten, and the build will stall on it.
- `motion` — optional, and the reason the render can be verified. See below.

## The motion promise

`motion` states, per scene, what a viewer should be able to see move:

```json
"motion": { "expect": "right", "what": "the panel slides in from the left edge" }
```

`expect` is one of `top`, `top-right`, `right`, `bottom-right`, `bottom`,
`bottom-left`, `left`, `top-left`, `in-place` — the direction the subject
**travels**, never where it comes from. A panel entering from the left edge
travels **right**. Getting this backwards is the single most common way a
"motion" note turns into an untestable sentence.

`in-place` covers a subject that stays put while changing: rotation about itself,
a word swap, a colour morph, a breathing idle.

Free-text `motion` earns a warning, not a check: without an `expect` there is
nothing to verify the render against.

Write a promise only where movement carries meaning. Most scenes do not need one.

## What `spec.py` gives back

```bash
python3 scripts/spec.py video-spec.json          # build sheet, exit 1 on errors
python3 scripts/spec.py video-spec.json --json   # same, machine-readable
```

It validates every enum, catches a structure that does not sum to the duration,
computes canvas and frame count, converts pacing into cuts and transition
milliseconds, counts arrivals per scene, flags a plan that will read as stalled
or as frantic, maps the camera and tone axes to specific
`hyperframes-animation` rules, suggests blueprints per role, and emits the
snapshot-plus-`motion.py` verification block for each promise.

**Errors block the build.** Warnings are judgment calls — read each one out and
say which way you resolved it, in the lock message.

## After the build

The spec is the acceptance criteria. When the render passes, append the outcome
to `video-spec.md`:

```markdown
## Verified
- check: clean (0 issues)
- arrivals: 13 measured against 14 implied
- scene 4 motion: expected right, measured right (conf 0.91)
- scene 5 motion: expected bottom, measured bottom-right (conf 0.62) — accepted,
  the button also drifts 40px right on entrance; matches the storyboard
```

A promise that fails is a bug in the composition or a promise that was wrong.
Decide which, fix it, and record the decision — never quietly re-label the spec
to match a render that missed it.
