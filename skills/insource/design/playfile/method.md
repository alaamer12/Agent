# playfile — one screen per file, the URL is the state, the folder is the iteration

A playfile is a design-review artifact, not a product: a single `.html` file that opens by double-click,
looks like the screen, and carries its whole review value in itself and in the folder's `README.md`.
`/design prototype` is the same thinking grown into a system (dock, specs, story catalogs); **playfile is the wave
of files you review before any system is worth building**. The one discipline both keep: every meaningful
state is reachable by URL alone.

## The shape

```
design/                      <- the project's design directory (use what exists; else create ./design/)
  mvp/                       <- one folder per iteration wave
    README.md                <- the review dossier for this wave
    projects.html            <- one screen per file
    settings.html
    onboarding.html
  v2-notifications/
    README.md                <- states the provenance rule
    settings.html            <- copied here because v2 changes it
    projects.html            <- still just a link: ../mvp/projects.html lives; this folder has none
```

Screens link each other with plain `<a href>` — the product's navigation *is* the review path. Opening
`index` is never required; any file opens alone.

## The seven laws

1. **One file = one screen, self-contained.** Inline `<style>`/`<script>`; CDNs (Tailwind, fonts, icons) are
   fine — these files are throwaway by design. No build step, no server, no shared JS module.
2. **The URL is the state.** Every state a reviewer should see is forceable by query param and survives
   refresh and copy-paste; clicking a real control updates the URL so the state the reviewer landed on and
   the state they clicked into are the same code path. The full light contract:
   [`references/url-state.md`](references/url-state.md).
3. **Role-named tokens, state color is truth.** `--brand / --surface / --ink / --line` in one inline block;
   success/warning/danger keep the same hue across themes and brand variants — brand color is identity,
   state color is meaning.
4. **Every control is alive or honestly disabled.** In a review file a dead button teaches the reviewer a
   lie: link it, force its state by param, or draw it disabled — never leave it clickable and mute.
5. **Design data is illustrative and says so.** Plausible real-shaped content (the product's language and
   direction — Arabic RTL stays RTL), never lorem ipsum; the README banner records that numbers are design
   data. Sparse by default; `?filled=1` shows the crowded realistic case.
6. **The folder is the iteration; copies follow change.** A screen enters the new folder the first time this
   version changes it; until then the new README *links* to the shipped folder's file. When a linked screen
   gets edited, it is copied in and its links pulled back. Never two live copies of one decision.
7. **The README is the deliverable as much as the screens.** Status banner, Files table telling the reviewer
   what to try (`?param` per row), dated decisions (reversals kept and marked), open questions, the
   provenance rule, CDN note. Anatomy and filled example: [`references/review-readme.md`](references/review-readme.md).

## Where everything lives

| File | Purpose | Read when |
|---|---|---|
| [`references/url-state.md`](references/url-state.md) | The light URL-state contract: naming, defaults, `?theme`/`?filled`, the click-path rule | Before writing a screen's params |
| [`references/review-readme.md`](references/review-readme.md) | Dossier anatomy, the provenance rule, decision dating, reviewer-only params | Before writing or updating a folder README |
| [`assets/screen.html`](assets/screen.html) | Self-contained single-screen skeleton: token block, theme + state wiring, live links | Starting any screen |
| [`assets/folder-readme.md`](assets/folder-readme.md) | README dossier template | Starting a wave |

## Boundary with `/design prototype`

Use playfile while designs are *proposals under review*: files, no tooling, the README carries the story.
Move to `/design prototype` when the artifact needs to *behave like the app at scale*: deep per-component state
trees, story catalogs, a shared dock, component builders, many routes kept honestly in sync — the moment a
wave's README starts reading like a spec document and reviewers ask for links that compose, the files want
the system. A playfile wave that graduates is rebuilt, not patched; the README's decisions carry over and
get recorded there. The two skills never contradict: `/design prototype` owns the machinery, playfile owns its
absence.
