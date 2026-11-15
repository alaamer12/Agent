---
name: design
version: 1.0.0
description: 'Design work, one skill, four modes: design-md (author the project''s canonical DESIGN.md: machine-readable tokens + human rationale, Google Labs design.md conventions - "/design DESIGN.md <file>"), playfile (throwaway design-review waves: self-contained linked HTML screens, URL-forced states, README dossiers - "/design a playfile"), prototype (interactive URL-driven prototype system: dev dock, component stories, per-component state trees, dedup guards - "/design prototype <screen>"), calibrate (extract the full design, visual and interaction DNA of a North-Star reference implementation and apply it to a project - "calibrate the /design of X to Y"). The router picks ONE mode and reads only its method.md. Triggers: DESIGN.md, design tokens, playfile, quick linked HTML mockups, prototype this, dev dock, stories gallery, calibrate design, match this app''s design to a reference. Not for UI redesign passes, page inventories or mockup-to-device parity - those stay separate skills (denoise, pages, parity).'
when_to_use: The user asks to author a DESIGN.md, run a wave of linked HTML review screens, build or extend an interactive URL-driven prototype, or calibrate a project's design to a reference implementation.
argument-hint: "[design-md|playfile|prototype|calibrate] <target>"
---

# design — one skill, four ways to operate

Name a mode and the target; with no mode named, the routing table below decides. Each mode is a
complete workflow in its own folder. The only rule that spans them: **load one `method.md`** —
never run two modes' machinery for a one-mode job.

## Modes

| Mode | The request sounds like | Method |
|---|---|---|
| `design-md` | "create a DESIGN.md for this project", "design tokens spec", "the app looks AI-generated — formalize its visual system" | [`design-md/method.md`](./design-md/method.md) |
| `playfile` | "quick linked HTML mockups of these screens", "review wave", "lighter prototype", "playfile this flow" | [`playfile/method.md`](./playfile/method.md) |
| `prototype` | "prototype this", "dev dock", "component stories", "make the mockups behave like the app" | [`prototype/method.md`](./prototype/method.md) |
| `calibrate` | "calibrate the design of X to Y", "make our app look like <reference>", "extract this reference's design DNA" | [`calibrate/method.md`](./calibrate/method.md) |

## Disambiguation — the pairs that get confused

- **playfile vs prototype.** A wave of proposals under review, one self-contained file per screen,
  no tooling: `playfile`. The artifact must behave like the app at scale — dock, story catalogs,
  deep state trees, shared modules: `prototype`. A playfile wave that graduates is rebuilt as a
  prototype, not patched.
- **design-md vs calibrate.** Inventing the project's own visual contract from its product feel:
  `design-md`. Copying an *existing reference's* design DNA (colors, type, spacing, interaction)
  into this project systematically: `calibrate`. A calibrated project still ends with its own
  DESIGN.md — calibrate feeds design-md, it does not replace it.
- **"calibrate the /design of X to Y" is calibrate mode**, never design-md: the word "design"
  there is the object of calibration, not a document request.

## Shared laws

- **The URL is the state.** In both `playfile` and `prototype`, every meaningful screen state is
  reachable by query param alone and survives refresh and copy-paste.
- **Nothing ships unrendered.** Any file that displays — screen, story, token sample — is opened
  in a browser and looked at before it is called done.
- **Design data says so.** Fake content in either prototype mode is plausible product content,
  labelled as design data; invented facts (legal numbers, reference-app claims) are never passed
  as real.

## Layout

```
design/
├── SKILL.md            # this router: mode table, disambiguation, shared laws
├── design-md/          # method.md + references/ + templates/ + examples/
├── playfile/           # method.md + references/ + assets/
├── prototype/          # method.md + references/ + assets/ + scripts/ + examples/
└── calibrate/          # method.md + references/ + examples/
```

The four modes were previously standalone skills (`/design-md`, `/playfile`, `/prototype`,
`/calibrate`); those entry points are gone — everything runs through `/design <mode>`.
