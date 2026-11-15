---
name: design
version: 1.0.0
description: 'One skill, 15 product design modes: assets (image pipeline: BOM, masters, conform), bleed (layout registers - full-bleed vs framed cards), collection (image BOM, style canon, prompts), denoise (calm a crowded UI: lite/medium/ultra), design-md (canonical DESIGN.md: tokens + rationale), diverge (n genuinely different directions before committing), pages (page universe into PAGES.md: inventory, legal docs, conditional screens), parity (mockup-to-device gap closed autonomously), playfile (linked HTML review screens, URL-forced states), prototype (URL-driven prototype systems: dock, stories, guards), resources (favicons, icons, splash, OG, optimize, localize, conform), stateful (derive, gate and implement every screen state), scss (SCSS best practices), styling (new styling: tokens, layer chain, naming), styleup (retrofit styling into enforced tokens). Triggers: prototype, mockup, legal pages, error pages, denoise UI, pixel parity, image plan, favicon, splash, design tokens, state coverage, CSS architecture.'
when_to_use: Any design-family task - prototypes and review files, page inventory and trust documents, UI cleanup or direction previews, layout framing, state completeness, mockup parity, image planning and resource files, design-system docs, styling systems. Also /design <mode>.
argument-hint: "<mode> [command] [target]"
---

# design — one entry point, fifteen modes

Each mode is a complete, self-contained method living in its folder; this file is the map and
nothing more. Name the mode and the task (`/design denoise ultra on this admin panel`,
`/create a /design prototype of the funds screen`); with no mode named, route below.

## Modes

| Mode | Do it for | Also |
|---|---|---|
| `assets` | the imagery pipeline end to end: plan the BOM, generate masters, conform sheets into delivery files | routes to `collection` + `resources`; owns order and handoffs |
| `bleed` | "it looks like a page inside a page", take the full width, remove/contain the outer card | registers: page · framed · hybrid |
| `collection` | what images a page needs, the style canon, the prompts, sheet economy math | writes `bom/BOM.md`, `bom/<page>.md`, `bom/style.md` |
| `denoise` | a crowded, noisy UI must become calm and usable | modes lite/medium/ultra; verify-by-render mandatory |
| `design-md` | the project's binding `DESIGN.md`: machine-readable tokens + human rationale | bootstrapping or auditing a visual system |
| `diverge` | see n genuinely different directions before committing the project to one | `taste [n]` / `snippet` |
| `pages` | which pages a product has, needs, or must not have — core inventory, trust documents, conditional screens | three own modes: `main` · `secondary` · `complementary`; artifact `PAGES.md` |
| `parity` | the real device render must match the mockup, and the loop closes itself to threshold | capture→score→diagnose→fix, unattended |
| `playfile` | a wave of reviewable design proposals as linked HTML files, no tooling | URL is the state; README dossier per wave |
| `prototype` | an interactive prototype system that behaves like the app at scale | dev dock, stories, guards; multi-app suites |
| `resources` | the resource files themselves: create, convert, recolor, optimize, localize, inventory, conform | fourteen scripts; naming and format rules |
| `stateful` | every condition a screen can be found in must have an honest rendering | derive → gates → matrix consult → implement → verify |
| `scss` | SCSS projects: architecture pattern, maps, mixins, nesting, BEM, module system | reference guide, not a workflow |
| `styling` | writing NEW styling on any stack so a design system can exist | tokens, downward-only layer chain, naming |
| `styleup` | retrofitting an existing project's hardcoded styling into an enforced token system | inventory → migrate → guard → parity evidence |

## Routing a vague request

- "Make me a mockup" → a throwaway review wave: `playfile`. Something that must behave like the
  app (shared chrome, stories, deep state trees): `prototype`.
- "Clean this up" → one decided pass: `denoise` (ask the mode). Several directions first:
  `diverge`. The complaint is about the outer frame, not the content: `bleed`.
- "Which pages/screens does this product need?" or any legal/trust document → `pages`.
  Conditional screens that only appear on a trigger (payment result, 404, session gate) →
  `pages complementary`. Full state derivation of one existing screen → `stateful`.
- "Does the build match the design?" → `parity`.
- Images: deciding which are needed and their prompts → `collection`; the whole pipeline →
  `assets`; the files on disk (favicon, icons, splash, OG, conversion, sheet splitting) →
  `resources`; real photographs from free sources → `fahlwy` (external).
- Styling: new code and structure → `styling`; the project already exists and is hardcoded →
  `styleup`; SCSS-specific mechanics → `scss`; formalizing the visual contract → `design-md`.

## Shared laws (modes inherit; mode methods do not repeat them)

- **Load one mode.** Read the chosen `mode/method.md`, then only the references it tells you
  to load. Modes never quote each other; cross-mode pointers name the mode (`/design <mode>`).
- **Rendered work is verified by rendering.** Writing markup is not proof: render, look at the
  screenshot, name what is wrong, fix, re-render. Required in `denoise`, `diverge`,
  `prototype`, `playfile`, `parity`, `stateful`.
- **Never invent what evidence owns** — a legal fact (`pages secondary`), sheet geometry
  (`resources`), a trigger with no real event (`pages complementary`), data the product does
  not have (`prototype` labels fakes as faked). Ask instead.
- **One owner per fact.** Each mode folder owns its territory; nothing here restates a rule
  from another mode or from an external skill (`generate`, `fahlwy`, `components`,
  `impeccable`, `planner`, `techstack`).

## Layout

```
design/
├── SKILL.md        # this map: modes, routing, shared laws
├── assets/         method.md                       (router into collection/generate/resources)
├── bleed/          method.md + references/ + examples/
├── collection/     method.md + references/ + assets/ + examples/
├── denoise/        method.md + references/ + assets/ + examples/ + scripts/
├── design-md/      method.md + references/ + templates/ + examples/
├── diverge/        method.md + references/ + assets/ + examples/
├── pages/          method.md + references/ + main/ + secondary/ + complementary/
├── parity/         method.md + references/ + scripts/
├── playfile/       method.md + references/ + assets/
├── prototype/      method.md + references/ + assets/ + examples/ + scripts/
├── resources/      method.md + references/ + scripts/
├── stateful/       method.md + references/ + assets/ + examples/
├── scss/           method.md                       (the full guide; sections per topic)
├── styleup/        method.md + references/ + examples/ + scripts/
└── styling/        method.md + references/ + examples/
```
