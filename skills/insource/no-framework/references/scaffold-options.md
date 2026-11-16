# Scaffold options — what each flag actually changes

`scripts/init-nof.sh <name> [--ui vanjs|preact|nanojsx] [--state native|nanostores] [--demo] [--bundler vite] [--styler tailwind|sass] [--css-tooling cli|vite-plugin]`

All flags combine freely. Every version the script writes into CDN URLs
or `package.json` is subject to workflow step 0: verify current versions
before treating a generated file as final.

## The clean scaffold vs `--demo`

The default scaffold is a genuinely minimal Hello World: one route, one
trivial page, a `base/Button.js` primitive, an empty `store.js` ready
for real state. Use this for an actual project — don't leave demo-only
content (a fake product cart) sitting in a real app's starting point.

`--demo` instead generates a fuller worked example: a cart store with an
action and a derived total, `base/Button.js` plus a `LoginButton`
business component built from it, `ProductCard` composition, two
routes — useful to see the patterns in action or as a learning
reference, not as the base for a real project. If it's unclear which
one fits what the person asked for, default to the clean scaffold —
"build me a NoF app for X" should get a clean starting point for X, not
unrelated demo content they'd have to delete first.

## `--bundler vite`

Switches the scaffold from the no-build-step CDN default to Vite + npm
packages: every generated file imports `vanjs-core` and `navigo` as
bare specifiers instead of CDN URLs (a bare `import Navigo from
'navigo'` doesn't work without a bundler — the CDN form is what makes
the no-build path possible), and the script generates `package.json`,
`vite.config.js`, and a `.gitignore`. Combine freely with `--demo`.

Use it when the person explicitly wants TypeScript, bundling, or
npm-managed dependencies from the start (see `tooling.md`'s "Local dev
server" section for when Vite is actually worth adding) — don't default
to it for a small project where the plain CDN setup is a complete,
valid answer on its own.

## `--ui vanjs|preact|nanojsx`

Picks the UI library — default `preact`. This changes:

- **component syntax** — JSX/`htm` for Preact and Nano JSX vs
  `van.tags()` for VanJS;
- **the local-state mechanism** — hooks vs `van.state()` vs class
  fields + `this.update()`;
- **what `js/store.js` uses** for shared state;
- **generated file extensions** — `.jsx` under `--bundler vite` for
  Preact/Nano JSX, `.js` otherwise;
- Preact and Nano JSX without a bundler get a generated `js/html.js`
  helper (one-time `htm.bind(h)`); VanJS needs none.

`ui_libraries.md` is the first file to check before writing any
component code for a non-default `--ui` — the full comparison, `htm`
vs JSX, `@preact/signals`, and Nano Stores equivalents of every
pattern.

## `--state native|nanostores`

Only applies to `--ui preact` (default `native`, meaning
`@preact/signals`). Pass `--state nanostores` to use Nano Stores
instead — when the store needs to be shared with a non-Preact part of
the same page. `--ui nanojsx` always uses Nano Stores for `js/store.js`
regardless of `--state` (Nano JSX has no reactive store of its own).
Passing `--state` with `--ui vanjs` or `--ui nanojsx` is a scaffolding
error explaining why, not a silently ignored flag.

## `--styler tailwind|sass` and `--css-tooling cli|vite-plugin`

Adds CSS tooling beyond the plain-CSS default. Neither Tailwind nor
Sass can be a CDN `<script>` tag the way VanJS/Navigo can — each
genuinely needs a compile step (see `tooling.md`'s Tailwind and Sass
sections for what that step looks like): Tailwind for utility-first
styling, Sass/Less for variables, nesting, or mixins beyond what plain
CSS custom properties comfortably handle. Both compile to plain CSS, so
they fit NoF's philosophy cleanly.

`--css-tooling cli|vite-plugin` picks between a standalone watcher
process and folding compilation into Vite; it defaults sensibly off
`--bundler` (`cli` without Vite, `vite-plugin` with it), so it rarely
needs to be passed explicitly.

**StyleX is not a supported `--styler` value** — it's tied to React's
component model, not vanilla-compatible. This is why `--styler` doesn't
offer it: it would generate a NoF project with a React-only compiler
and nothing to run it against. Before adding such a tool by hand,
verify it actually runs standalone against plain DOM/VanJS output
rather than assuming CSS-in-JS tooling is automatically
framework-agnostic just because it's "just CSS" on the surface.
Reach for any styling tool the same way as Vite: an addition once the
project's needs justify it, not a default for a small project where
plain CSS is enough.

## Any vanilla-JS-compatible library is fair game

NoF's principle is broader than the core two packages: any library that
works as plain vanilla JS — no required build step, no framework runtime
underneath it — can slot in alongside or instead of VanJS if the
project's needs call for it. A different small reactive library, a
vanilla date/animation/utility library, Nano Stores for cross-library
state — as long as it doesn't drag in React/Vue/Angular as a
dependency. Check compatibility and the current version the same way as
workflow step 0 before adding anything new.

Preact is the recommended default because it pairs a familiar JSX/hooks
surface and a large ecosystem with — via `@preact/signals` —
fine-grained updates close to VanJS's own; Navigo is small and
battle-tested regardless of what sits on top. VanJS and Nano JSX remain
full alternatives, not legacy options — `ui_libraries.md` covers when
each fits better.

## HTMX and hypermedia libraries

HTMX itself passes the vanilla-JS bar cleanly (single dependency-free
file, no build step) — but it's a **different architecture**, not an
alternative router: server-rendered, hypermedia-driven (the server
returns HTML fragments, HTML attributes declare the swapping), versus
NoF's client-rendered component-and-state model. It's a legitimate
alternative when the backend and the person's preferences fit it
better, not a drop-in swap for Navigo. `tooling.md` covers when to
suggest it instead of default NoF versus alongside it.
