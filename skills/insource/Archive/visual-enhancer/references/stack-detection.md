# Stack Detection — Match Fix Complexity to What's Actually There

Run this before analyzing individual files, once per scan (general or targeted).

## What to check

1. **Manifest/lockfile**: `package.json` (+ `package-lock.json`/`yarn.lock`/`pnpm-lock.yaml`),
   or the equivalent for the project's language (`requirements.txt`, `Cargo.toml`, `go.mod`,
   `pubspec.yaml`, etc.). Read the full dependency list, not just devDependencies.
2. **Existing imports in the visual-code files themselves** — a dependency can be installed but
   unused, or used only in one corner of the app; check actual `import`/`require` statements in
   the files you're scanning, not just the manifest.
3. **Styling approach**: look for Tailwind config, CSS-in-JS (`styled-components`, `emotion`),
   CSS modules, a design-token file (`theme.js`, `tokens.json`, `variables.css`), or plain CSS.
   Whatever's already there is what fixes should use — don't introduce a second styling paradigm.
4. **Existing asset conventions**: where do current icons/illustrations live
   (`src/assets/icons/`, `public/images/`, etc.)? What format (`.svg`, `.png`)? What naming
   pattern? New asset suggestions (Type B fixes) should follow the same convention.
5. **For CLI/TUI projects specifically**: is there a rendering/layout library already in use
   (`ink`, `blessed`, `yoga-layout`, `cli-table3`, `chalk`, `ora`) or is output done via raw
   `console.log`/`process.stdout.write`? This single check determines whether a decomposition
   fix (Type C) can propose real components or must stay at the pagination/chunking level.
6. **Framework version/conventions**: React class vs. hooks, Vue 2 vs. 3, etc. — match
   whatever the codebase already does so suggested diffs are drop-in compatible.

## How this changes fix output

| Situation | Fix should... |
|---|---|
| Project has design tokens/theme file | Reference existing token names, not raw hex values |
| Project has no design tokens | Fix may introduce token-like CSS variables, but note it as a small new pattern, not assume one exists |
| CLI has `ink` + a tab/layout library | Propose real component code using it |
| CLI is raw `console.log` only | Propose pagination/chunking/grouping, not a new rendering library |
| Existing icon set has a consistent color system already (just not applied to the flagged file) | Fix should extend that *existing* system, not invent a new one |
| No icon/asset convention exists at all | Fix may establish one, but flag it clearly as a new pattern being introduced |

## Never do this

Do not suggest adding a new dependency as the default fix. Only propose one when the finding
genuinely cannot be solved with what's already in the project, and even then, prefix the fix
with `**Requires new dependency:** <name>` so it's an explicit, visible decision for the user —
never a silent assumption baked into the diff.
