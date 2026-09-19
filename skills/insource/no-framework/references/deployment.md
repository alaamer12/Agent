# Building, Bundling, and Shipping

This covers taking a NoF app from local dev to a live URL. NoF's two
paths (no-bundler/CDN, or Vite) diverge here, and the no-bundler path
has a production-only gap that's easy to miss because it doesn't show
up locally if the local dev server happens to hide it. Read the "URL
fallback in production" section below even if everything works in local
testing — it's the one thing here that silently breaks for real users
if skipped, not just a nice-to-have.

## No-bundler path: there is no build step

If the project never added Vite, shipping is just uploading the project
folder to a static host as-is — the same CDN-imported files that run in
dev run in production unchanged. No `npm run build`, no `dist/` folder,
no minification step to remember.

**One real tradeoff worth knowing about, not necessarily fixing:**
pinning `vanjs-core@1.6.0` / `navigo@8.11.1` (or whatever versions were
verified per `references/tooling.md` step 0) to a CDN URL means
production now has a runtime dependency on that CDN (jsdelivr, unpkg,
esm.sh, whichever was used) staying available indefinitely at that
exact version — not just as a dev convenience, but every time a real
user's browser loads the app. jsdelivr's specific answer to this is
version fallback and a multi-provider setup, which makes it a
reasonable bet for a small-to-medium project, but it's still an external
dependency an entirely self-hosted app wouldn't have.

If that tradeoff isn't acceptable for a given project (compliance
requirement, offline/air-gapped deploy target, or just wanting zero
runtime third-party dependencies), the fix is to vendor the files
instead of fetching them from a bundler:

1. Download the exact pinned build once (`van.min.js` from the CDN URL
   already in use, the Navigo `+esm` output the same way).
2. Save them under a local path, e.g. `js/vendor/van.min.js`,
   `js/vendor/navigo.min.js`.
3. Change the imports from the CDN URL to the local path:
   `import van from "./vendor/van.min.js"`.

This is still a no-bundler setup — nothing about it requires Vite — it
just trades "always fetches the CDN's current copy of that version" for
"serves a copy checked into the project," which needs to be manually
re-vendored on a deliberate version bump rather than staying implicitly
current. Most NoF projects don't need this; default to the plain CDN
import and only vendor when a specific reason calls for it.

## URL fallback in production (same problem as local dev, different host)

`references/routing.md` covers why Navigo's default clean-URL History
API mode needs the server to serve `index.html` for unknown paths, and
`references/tooling.md` covers the local-dev-server fix
(`live-server --entry-file=index.html`). **That local fix does not carry
over to production** — each static host needs its own equivalent
config, and without it, a real user refreshing the page or opening a
bookmarked/shared link to anything other than `/` gets a 404 from the
host, not from the app. This is easy to miss because it never shows up
while testing via in-app navigation (clicking links, calling
`navigateTo()`) — it only shows up on a hard reload or a direct URL,
which is exactly the kind of testing step that's easy to skip.

Common hosts and their equivalent config:

- **Netlify** — add a `_redirects` file at the project root:
  ```
  /*  /index.html  200
  ```
- **Vercel** — add a `vercel.json` at the project root:
  ```json
  { "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }
  ```
- **GitHub Pages** — doesn't support server-side rewrites at all, so the
  common workaround is a custom `404.html` that redirects to
  `index.html` while preserving the intended path (search "spa-github-
  pages" for the standard trick, since it's a well-known third-party
  snippet rather than something to reproduce here). If avoiding that
  workaround matters more than clean URLs for a specific project, GitHub
  Pages is also one legitimate reason to instantiate Navigo in hash mode
  instead of History API mode — that trades clean URLs for a setup that
  needs no server-side fallback config at all, which is a reasonable
  call specifically for a host with no rewrite support.
- **S3 + CloudFront (or similar static bucket + CDN)** — configure the
  bucket's error document to `index.html`, and if using CloudFront,
  add a custom error response mapping 403/404 to `/index.html` with a
  200 status.

Whichever host is used, verify this by actually reloading the browser
on a non-root route after deploying — don't assume the config is
correct just because it's in place; a wrong path or a missed 200-status
override is a common way this config silently doesn't work.

## Vite path: the actual build step

Once a project has added Vite (see `references/tooling.md` for when
that's justified and what changes about the imports), shipping isn't
"upload the folder as-is" anymore — Vite needs an explicit build:

```bash
npm run build
```

This produces a `dist/` folder containing minified, bundled, hashed
(`app.a1b2c3.js`-style) output. A few things that change from the
no-bundler path:

- **Deploy `dist/`, not the source folder.** The source `index.html`
  references `js/router.js` directly; Vite's build generates its own
  `dist/index.html` with the correct hashed script tags already wired
  in — don't hand-edit script paths, Vite handles this as part of the
  build.
- **`vite preview`** serves the built `dist/` output locally so you can
  sanity-check the actual production build before deploying, as
  distinct from `vite dev`'s dev server. Worth doing at least once
  before shipping, since dev and prod builds aren't always identical
  (minification can occasionally surface a bug dev mode hides).
- **The URL-fallback requirement above still applies** to wherever
  `dist/` ends up hosted — Vite's own dev server handles this
  automatically during `vite dev`/`vite preview`, but the production
  host serving the built `dist/` folder needs the same host-specific
  config as the no-bundler path.
- Minification and bundling are handled by Vite automatically — there's
  no separate minification step to add on top of `npm run build`.

## Pre-ship checklist

- [ ] Verify current library versions were checked per
      `references/tooling.md` step 0, not left on whatever was pinned
      when the project started.
- [ ] Confirm URL fallback is configured for the actual host being
      deployed to, and verify it by reloading on a non-root route after
      deploying — not just trusting the config file is correct.
- [ ] (No-bundler only) Decide deliberately whether CDN-pinning's
      external-dependency tradeoff is acceptable for this project, or
      vendor the files if not.
- [ ] (Vite only) Run `vite preview` against the actual `dist/` build at
      least once before deploying, not just `vite dev`.
