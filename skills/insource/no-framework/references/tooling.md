# Tooling, Versions, TypeScript, and Limitations

## Verify versions and API compatibility before relying on this skill's code

Every version referenced in this skill's `examples/` and
`scripts/init-nof.sh` (VanJS, Navigo) is a snapshot, not a live source of
truth — library versions move forward, and this skill's own patterns can
lag behind a library's current API. Before scaffolding or writing code
against VanJS, Navigo, or anything else pulled in:

1. Search for the current latest stable version on npm (or the relevant
   registry) for each library being used.
2. If the current version is a major-version jump ahead of what this
   skill's examples reference, check that library's changelog/release
   notes for breaking API changes before assuming the patterns in
   `references/state_management.md`, `references/routing.md`, etc. still
   apply as written. A minor/patch bump is generally safe to assume
   compatible without a deep check; a major bump is not.
3. Use the version you actually found, not the one hardcoded in this
   skill, in the CDN URL or `package.json` entry you generate.

This is worth doing once per project/session, not on every single file —
check at the start, then build with confidence using what was found.

## Local dev server

NoF doesn't require a build step — a CDN import of VanJS/Navigo works
directly in a static HTML page. For local development:

- `live-server` — zero-config static server with auto-reload; simplest
  option for a no-build-step project. **Needs one flag to work with
  Navigo's default clean URLs**, see below — plain `live-server` with no
  flags will 404 the moment someone refreshes or directly opens a
  non-root route like `/products`.
- **Vite** — worth adding once the project wants TypeScript, bundling,
  or npm-installed (rather than CDN-imported) dependencies. Vite's dev
  server also handles SPA fallback routing (serving `index.html` for
  unknown paths) out of the box, which Navigo's clean-URL mode needs.
  `scripts/init-nof.sh --bundler vite` scaffolds this directly for a
  new project — see "Switching an existing CDN-based project to npm
  packages via Vite" below for what it generates.

Don't add Vite to a genuinely small project by default — it's an
addition to reach for when the project's needs justify it (TypeScript,
npm packages, bundling), not a default scaffold choice. Plain CDN
imports plus `live-server` is a complete, valid NoF setup on its own.

### `live-server` needs `--entry-file`, not `--spa`, for Navigo's clean URLs

This is an easy trap because the flag named `--spa` sounds like the
right one and isn't:

- `live-server --spa` rewrites requests like `/products` to
  `/#/products` — hash-based routing. That's the opposite of what
  `new Navigo('/')`'s default History API mode does (Navigo owns clean,
  hash-free URLs; see `references/routing.md`). Using `--spa` here
  actively fights Navigo rather than supporting it.
- `live-server --entry-file=index.html` is the actual fix: it serves
  `index.html` in place of any missing file, which is exactly the
  "unknown path → index.html" fallback History API routing needs. This
  is the flag `scripts/init-nof.sh`'s generated `README.md` uses.

Run it as `npx live-server . --entry-file=index.html` (or
`live-server --entry-file=index.html` if installed globally). Without
this flag, the app works fine when navigated to client-side (clicking
links, calling `navigateTo()`) but breaks on a hard refresh or a
directly-typed/bookmarked URL to anything other than `/` — a gap that's
easy to miss in dev because most testing happens via in-app navigation,
not direct loads.

### CDN imports need a full URL, not a bare specifier

`import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js"`
and `import Navigo from "https://cdn.jsdelivr.net/npm/navigo@8.11.1/+esm"`
both work directly in a browser with zero build step — that's what makes
the no-bundler setup possible at all. What does **not** work without a
bundler or import map is a bare specifier like `import Navigo from
'navigo'`: that syntax only resolves once something (Vite, or an
explicit `<script type="importmap">` in `index.html`) tells the browser
where `'navigo'` actually points. This isn't specific to Navigo — it's
true of any npm package. Every library import in the no-bundler NoF
setup should use the full CDN URL form; reserve the bare-specifier form
for projects that have actually added Vite.

### Switching an existing CDN-based project to npm packages via Vite

Once a project adds Vite, imports change from CDN URLs to bare
specifiers resolved from `node_modules`:

```jsx
// Before (no bundler, CDN):
import van from "https://cdn.jsdelivr.net/npm/vanjs-core@1.6.0/src/van.min.js";
import Navigo from "https://cdn.jsdelivr.net/npm/navigo@8.11.1/+esm";

// After (Vite, npm packages):
import van from "vanjs-core";
import Navigo from "navigo";
```

That also means adding a `package.json` (`npm install vanjs-core navigo
vite`) and letting `node_modules` hold the actual dependency code instead
of fetching it from a CDN on every page load.

**For a new project, `scripts/init-nof.sh --bundler vite` does this
scaffolding directly** — it generates every file with bare-specifier
imports from the start, plus `package.json`, `vite.config.js`, and a
`.gitignore` for `node_modules`/`dist`, so there's no by-hand swap to do
(`bash scripts/init-nof.sh <project-name> --bundler vite`, combinable
with `--demo`). Verify the pinned `vanjs-core`/`navigo`/`vite` versions
in the script are still current per step 0 before running it, the same
as the no-bundler path.

**For an existing CDN-based project** that wants to add Vite after the
fact, apply this same before/after swap by hand across `js/utils.js`,
`js/store.js`, `js/router.js`, and everything under `js/base/` and
`js/components/`, after running Vite's own project scaffolding (`npm
create vite@latest`) or hand-writing `package.json`/`vite.config.js` to
match what `--bundler vite` generates for a new project.

## CSS tooling: Less and Sass/SCSS are legitimate additions

Plain CSS is the NoF default, and it's genuinely sufficient for most
small-to-medium projects — especially with modern CSS custom properties
covering a lot of what used to require a preprocessor. But when a
project's stylesheet complexity actually grows past that (deep nesting
patterns, computed color values via functions, mixins reused across many
components), Less or Sass/SCSS are reasonable additions:

- Both compile down to plain CSS ahead of time or through a lightweight
  build step — neither requires a framework runtime in the browser, so
  neither breaks NoF's framework-free commitment.
- Sass has the larger ecosystem and is the more common default choice
  today if picking between the two without a specific reason to prefer
  Less.
- Add either the same way as Vite above: once the project's actual CSS
  complexity justifies it, not as a default scaffold choice for a small
  project where plain CSS handles things fine.

## Not every CSS-adjacent tool is vanilla-compatible

Being "about CSS" doesn't automatically make a tool framework-agnostic —
some CSS-in-JS systems are built specifically around a framework's
component model and require that framework's build tooling to function
at all. **StyleX is a notable example**: it's a build-time CSS-in-JS
system originally built for and tightly integrated with React component
patterns, requiring its own compiler step tied to that ecosystem — it is
not a drop-in "plain CSS with superpowers" tool the way Less/Sass are.

Before adding any CSS-in-JS or styling tool to a NoF project, verify it
actually runs standalone against plain DOM output (what VanJS produces)
rather than assuming it's vanilla-compatible just because "CSS" is in
the pitch. When in doubt, check the tool's own docs for whether it lists
framework-agnostic/vanilla usage as a supported mode, or whether every
example assumes a specific framework's build pipeline.

## HTMX and hypermedia-style libraries: vanilla-compatible, but a different architecture

HTMX (and similar hypermedia-oriented tools) genuinely passes the
vanilla-compatibility bar cleanly: it's a single dependency-free file, no
build step required, drop-in via a plain `<script>` tag — the same shape
as VanJS/Navigo in that respect. So the honest answer to "can I use
HTMX?" is yes, it's not disqualified by NoF's framework-free commitment
the way something like StyleX is.

But it's worth being explicit about what actually changes if it's used,
because it's a different *architecture*, not just an alternative router
or state library:

- **VanJS/Navigo is client-rendered**: state lives in the browser
  (`van.state()`), components are JS functions that build DOM, and
  routing swaps which client-side component is mounted. The server is
  typically a JSON API or a static file host.
- **HTMX is server-rendered, hypermedia-driven**: the server returns
  HTML fragments directly (not JSON), and HTMX's HTML attributes
  (`hx-get`, `hx-post`, `hx-target`, `hx-swap`) declare how those
  fragments get fetched and swapped into the page. There's no
  client-side component tree or client-side state store in the NoF
  sense — the source of truth for what to render lives on the server.

This means HTMX isn't really a drop-in replacement for Navigo (routing)
or a complement to VanJS state (`van.state()`/`van.derive()`) in the way
Less is a drop-in complement to plain CSS — it's a different way of
building the whole interactive layer, one that assumes a
backend capable of returning HTML fragments rather than JSON.

Practical guidance:

- If the person's backend is naturally suited to returning HTML
  fragments (a server-side templating stack — Flask/Django/Rails/
  Express with templates, etc.) and they want less client-side
  JavaScript in general, HTMX-only (no VanJS) is a legitimate,
  different-but-compatible-in-spirit architecture — genuinely simpler
  for that use case, and arguably even more aligned with "less code,
  full control" than adding a client-side reactive library at all. This
  is a real alternative to suggest when it fits better than default NoF,
  not just a variant of NoF.
- Mixing HTMX with VanJS in the same project is possible in principle
  (HTMX handling some server-fragment-swapping interactions, VanJS
  components handling purely client-side reactive UI elsewhere) but
  adds real complexity — two different mental models for "how does the
  DOM update" living side by side. Don't reach for this combination by
  default; only when a specific part of the app genuinely benefits from
  each model and the added complexity is worth it.
- Don't silently substitute HTMX for Navigo assuming it's "the same kind
  of thing but newer" — check with the person first if it's unclear
  whether they want the client-rendered NoF default or a
  server-rendered hypermedia approach, since the choice affects backend
  design, not just frontend file structure. This is exactly the kind of
  tooling fork worth surfacing with options rather than silently picking
  one (see the `questionnaire` skill if enabled).
- As with any library: check the current version and any relevant
  breaking changes before using it — htmx had a major version (4.0)
  release with some behavior changes (attribute inheritance defaults,
  event naming) alongside the still-current 2.x line, so verify which
  line is appropriate and current at the time of use rather than
  assuming.

## Any vanilla-compatible library, not just VanJS/Navigo

VanJS and Navigo are this skill's recommended default pairing, not a
hard requirement — NoF's actual commitment is to staying framework-free,
not to these two specific packages. A library is a reasonable fit for a
NoF project if it works as plain vanilla JavaScript: no required
framework runtime underneath it, usable via a plain `<script>`/import
without a framework-specific build pipeline. Verify this the same way as
the version-check discipline above — check the library's own docs for
whether it's advertised as framework-agnostic or vanilla-compatible
before assuming it fits, rather than assuming any small library
automatically qualifies.

## TypeScript integration (recommended once the project grows)

VanJS and Navigo both work fine with TypeScript. Type props explicitly
on components:

```tsx
interface Product {
  id: number;
  name: string;
  price: number;
}

const ProductCard = (product: Product, onAdd: (p: Product) => void) => {
  /* ... */
};
```

Add TypeScript when the project's component/prop surface has grown large
enough that catching prop-shape mistakes at compile time is worth the
added build step — not as a default for every NoF project from day one.

## Editor / DevTools

- VS Code + ESLint + Prettier is a reasonable default toolchain; nothing
  NoF-specific is required here.
- For actually diagnosing a bug, profiling reactivity, or reading stack
  traces through the minified CDN builds, see
  `references/debugging.md` — the one-line "check the Performance tab"
  version of this used to live here, but it wasn't specific enough to
  be useful on its own.

## Honest limitations

Be upfront about these rather than only presenting NoF's advantages —
they're real tradeoffs, not just caveats to bury:

- **Smaller ecosystem** than React/Vue/Angular — fewer pre-built
  component libraries, fewer Stack Overflow answers for edge cases.
- **Requires more discipline in larger teams** — there's no framework
  enforcing conventions (file structure, state patterns), so a team has
  to actually follow the conventions in this skill rather than have them
  enforced by tooling.
- **Less mature tooling** — no official devtools extension equivalent to
  React DevTools as of this writing; debugging relies more on browser
  DevTools directly.
- **Best suited to small-to-medium applications** — see the "when to
  use" section in SKILL.md for where this stops being the right choice.
