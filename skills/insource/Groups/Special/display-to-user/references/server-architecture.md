# server.py reference

## What it is

A dependency-free Python stdlib HTTP server (`http.server`) that serves a
single-page viewer (`index.html`) showing a project's file tree, git status,
and file previews. No pip installs, no Node — works anywhere Python 3 is
available, since it's meant to run inside arbitrary project directories with
unknown toolchains.

## Files

- `server.py` — the backend. Serves `index.html` at `/`, and two JSON
  endpoints: `/api/tree` and `/api/file`.
- `index.html` — the frontend. Vanilla JS, no build step. The material-icon-theme
  icon manifest (~470KB) is embedded directly in a `<script>` tag as
  `window.MATERIAL_ICONS_MANIFEST` — this was a deliberate fix (see "Design
  decisions" below) so the deliverable is exactly 2 files with no folder
  structure to lose track of.

## CLI flags (server.py)

```
python3 server.py [--port PORT] [-p PORT] [--root ROOT] [-r ROOT]
```
- `--port` / `-p`: default `8420`
- `--root` / `-r`: default is the current working directory (`os.getcwd()`)
  at the time the script is launched — NOT the directory the script file
  lives in. This matters: `cd` into the target project first, or pass
  `--root` explicitly, before launching.

## API surface

### `GET /api/tree`
Returns:
```json
{
  "cwd": "/abs/path/to/project",
  "is_git": true,
  "branch": "main",
  "changed": ["path/to/file.js", "some-untracked-dir"],
  "tree": [ { "name": "...", "path": "...", "type": "file|dir", "changed": bool, "children": [...] } ]
}
```
- `changed` comes from `git status --porcelain`. Untracked directories are
  collapsed by git into a single `dirname/` entry — the server normalizes
  this and does prefix-matching so every file inside still gets marked
  `changed: true` in the tree (see `path_is_changed()` in server.py).
- Directories walk-ignore: `.git`, `node_modules`, `__pycache__`, `.venv`,
  `venv`, `dist`, `build`, `.next`, `.turbo`, `target`, `.cache`, plus any
  dotfile/dotdir except `.github`.

### `GET /api/file?path=<relative path>`
Returns file content as JSON for syntax highlighting / markdown preview.
- Rejects path traversal: any resolved path outside `ROOT` (via `..`,
  absolute paths, or symlinks) returns 403.
- 404 if not a file, 413 if over 2MB (`MAX_FILE_BYTES`), 415 if binary
  (can't be decoded as UTF-8 text).

### Everything else
Falls through to serving `index.html` — this is a deliberate SPA-style
catch-all, not a bug. A request to a stale/removed route (e.g. the old
`/vendor/material-icons.json` from before the manifest was embedded) will
return the HTML page with a 200, not a 404.

## Frontend behavior

- Icon resolution mirrors VS Code's real icon-theme matching precedence:
  exact `fileNames` match → longest-matching compound `fileExtensions`
  (e.g. `component.spec.ts` matches `test-ts` before falling back to
  `typescript`) → default `file` icon. See the `resolveFileIconName` /
  `resolveFolderIconName` functions.
- The "Only changed" toggle is pure client-side filtering (`filterVisible`)
  against the `changed` boolean already present on every tree node — no
  extra round-trip, and it's reflected in the URL as `?only-changed=true`
  via `history.replaceState`.
- Right-click on a `.md`/`.markdown`/`.html`/`.htm` file shows a context
  menu with "Preview" / "View source". Markdown renders through
  `markdown-it` (html: false) then `DOMPurify.sanitize`. HTML files render
  inside `<iframe sandbox="allow-same-origin">` — deliberately omitting
  `allow-scripts` so a previewed page cannot execute JavaScript against the
  viewer's origin.
- Syntax highlighting is `highlight.js` with auto language detection; a
  small `LANG_MAP` maps common extensions to highlight.js language classes
  as a hint, but highlight.js will still auto-detect if omitted.
  **CDN gotcha:** the plain `highlight.js` npm package does NOT ship a
  prebuilt browser bundle (no `highlight.min.js` anywhere in it — it's
  unbundled ES modules meant for a bundler). The correct CDN source is the
  separately-published `@highlightjs/cdn-assets` package, which mirrors the
  official `cdn-release` GitHub repo and does contain `highlight.min.js` and
  `styles/*.css` at its root. If you ever change the highlight.js version,
  verify the new version's `@highlightjs/cdn-assets` release actually
  contains those files before changing the URL — don't assume the plain
  `highlight.js` package path works just because other CDN-linked libraries
  (markdown-it, DOMPurify) happen to publish their browser bundle under
  `dist/` in their main package.
- Both `hljs.highlightElement()` call sites go through a `safeHighlight()`
  wrapper that no-ops (with a `console.warn`) if `hljs` is undefined or
  throws — a CDN script failing to load should degrade to unhighlighted
  text, not break the whole file viewer. The markdown-preview path is
  stricter: if `markdown-it` or `DOMPurify` failed to load, it refuses to
  render and falls back to showing raw source instead, because rendering
  markdown-it's output without DOMPurify would be an XSS risk — that one
  fails closed, not open.

## Design decisions worth knowing before modifying this

1. **No third-party Python packages.** The target machine's project
   directory could be any language/ecosystem — don't add a `pip install`
   step. If you need JSON, HTTP, subprocess, or path handling, it's in the
   stdlib.
2. **No build step for the frontend.** Plain HTML + vanilla JS + CDN
   `<script src>` tags (highlight.js, markdown-it, DOMPurify). A Vue SFC or
   React build was considered and rejected — it would require a compiler
   step, breaking the "just run python3 server.py" simplicity.
3. **Icon manifest is embedded, not fetched.** Originally served from a
   separate `vendor/material-icons.json` file over `/vendor/...`. This
   broke in practice: users downloading 3 separate files (rather than a
   zip) sometimes lost the `vendor/` subfolder, and the frontend's
   `fetch()` call had no `res.ok` check, so a 404 error body got silently
   parsed as if it were the real manifest, crashing on
   `MANIFEST.fileNames[...]` being undefined. Embedding the manifest
   directly in `index.html` eliminates the whole failure class. If you
   ever need to update the manifest (e.g. bump the material-icon-theme
   version), regenerate it with a script like:
   ```python
   import json, re
   manifest = json.load(open("material-icons.json"))  # from the npm package
   html = open("index.html").read()
   idx = html.index("<script>")
   injected = "<script>\nwindow.MATERIAL_ICONS_MANIFEST = " + json.dumps(manifest) + ";\n"
   html = html[:idx] + injected + html[idx+len("<script>"):]
   open("index.html", "w").write(html)
   ```
   (This assumes the first bare `<script>` tag — not a `<script src=...>`
   tag — is the one holding the app's own JS, which it is in the current
   file.)
4. **All fetches now check `res.ok` before parsing.** This was the actual
   root cause of the manifest bug above — apply the same discipline to any
   new endpoint you add: never assume a 200.
