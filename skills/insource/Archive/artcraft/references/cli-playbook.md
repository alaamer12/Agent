# ArtCraft App CLI Playbook

General patterns for any ArtCraft app's `<app>-cli`. The live source of truth is always
`<app>-cli commands --json` (every command with its param doc) and the fetched
`docs/cli.md` + `docs/mcp.md` — read those first; this playbook is the distilled field manual.

## Locating the CLI (cross-platform)

- Windows: `C:\Program Files\<App>\<app>-cli.exe` and `<app>.exe` (the GUI).
- Linux: `which <app>-cli` — installs may also live in `/snap/bin` (snap) or `~/.local/bin`.
- macOS: `/Applications/<App>.app/Contents/MacOS/`.
- If not found, ask the user where the app is installed; never guess-drive the GUI binary.

## Subcommands (same shape across ArtCraft apps)

- `info <file> [--json]` — structure, node counts, missing-font notes; ALWAYS check those notes.
- `export <file> -o <out> [--format ...] [--scale N] [--page NAME] [--node ID|NAME]`
  — a directory `<out>` writes one file per top-level frame (named after the frame).
- `render <file> -o out.png [--page NAME] [--scale N]` — whole-page composite.
- `convert <in> <out>` — format conversion by extension.
- `run <script.json> [--in f] [--out f]` — headless command script (the workhorse).
- `commands [--json] [--filter TEXT]` — the full command catalog with param docs.
- `mcp [--attach PORT] [--automation-read-root DIR] [--automation-write-root DIR]` — stdio MCP
  server, headless or attached to a running GUI (`<app>.exe --control PORT`).
- Global `--no-system-fonts` for machine-independent renders.

## `run` script rules

- JSON array of `{"command": id, "params": {...}}` (or `{"commands":[...]}`, or JSONL).
- **All-or-nothing**: one failing step rolls back everything and writes nothing; result lines
  print only after the whole script passes. Fix and rerun.
- `{"$step": n}` anywhere in params = the `id` returned by step n (zero-based).
  **Raw integers are literal node ids, never references** — steps targeting layers created by
  earlier steps MUST use `$step`.
- `--out` omitted = changes discarded (handy for `inspect.code`/query probes).
- Ids are sequential: a new document's first page is 1, first layer is 2.
- For anything beyond a handful of steps, generate the JSON with a Python script in
  `throwaway/` and track step indices programmatically — manual numbering causes off-by-one bugs.

## Engine conventions

- Coordinates: 1 unit = 1px at 100%, x right, **y down**; x/y on create commands are relative
  to the parent frame.
- Colors: `"#RRGGBB"` or `"#RRGGBBAA"` anywhere (fills, strokes, effects).
- Gradients inline: `{"type":"linearGradient","stops":["#A0A0FF","#60D0D4"]}` (also radial/angular/diamond).
- Effects: `{"type":"dropShadow","color":"#00000026","offset":[0,4],"radius":16}`; also
  innerShadow, layerBlur, backgroundBlur, noise, texture, glass. Note: effect OBJECTS use
  `offset:[x,y]`; only style-property paths (`effects/<i>/offsetX`) use scalar offsetX/offsetY.
- Text: `fontFamily`, `fontStyle` ("Regular","Medium","Semi Bold","Bold"), `fontSize`,
  `lineHeight` (`"150%"`|auto|px), `letterSpacing`, `textAlign`; a top-level `width` wraps.
- `padding` order is **[top,right,bottom,left]**; `cornerRadius` scalar or [tl,tr,br,bl].
- Auto layout: children are positioned by `layout/gap/padding/mainAlign/crossAlign/sizingH/sizingV`
  — never x/y on flow children. `mainAlign` also takes `spaceBetween|spaceAround|spaceEvenly`.
- Query live data instead of assuming: frame presets command (device sizes), fonts command
  (installed families).

## Gotchas that WILL bite you (verified the hard way)

1. **New frames default to 100px wide** unless `sizingH`/`width` is set — auto-layout children
   meant to hug need explicit `sizingH:"hug"` or their content is clipped at 100px.
2. **Frames clip children by default.** Shadows and overhangs get cut (`clip:false` on the
   parent). A hug-sized auto-layout row cuts a button's drop shadow into a hard gray band.
3. **`fill` and `fills` collide** — if both are present `fills` wins. When setting `fill:"#X"`,
   remove the default `fills`. Symptom: "transparent" cards over gradients.
4. **Unknown param keys fail the whole run** with a long "known:" list — that list IS the spec
   for the command; read it instead of guessing.
5. Singular-vs-plural id params differ per command (`inspect.properties` takes `id`,
   `inspect.assets` takes `ids`). The error text is precise — read it.
6. Documents start named "Untitled" — rename explicitly; `info` confirms it. `info` lists only
   top-level nodes — verify inner layers by exporting a PNG and looking at it, not by info.
7. Missing fonts render in a fallback silently — check `info` output after every build.
8. **Only frames (and components) take auto layout** — a rectangle rejects `layout/crossAlign/
   padding`. A "card with centered content" is a frame with fills, not a rectangle.

## Prototype / animation recipes

- Triggers: `onClick|onHover|onPress|onDrag|mouseEnter|mouseLeave|mouseDown|mouseUp|afterDelay{ms}|keyPress{key}`.
- Actions: `navigate|back|scrollTo|openOverlay|swapOverlay|closeOverlay|changeTo|openUrl|setVariable|setVariableMode|conditional`.
- Transitions: `instant|dissolve|smartAnimate|moveIn|moveOut|push|slideIn|slideOut` + direction,
  `durationMs`, easing (`easeOutBack`, spring names like `gentle|bouncy`, bezier).
- **Staged entrance**: build N state frames whose layers share identical names; a hidden group =
  `opacity:0` + `y:+32`; chain with `afterDelay` → `navigate` + `smartAnimate`.
- Overlays: `openOverlay {dest, position:"manual", offset:[x,y], close_on_outside:true, background:"#0B102099"}`.
- Theme switch without variables: two full frames + `navigate` + `dissolve` each way.
- Flows: `proto.flow.add {start:<frameId>, name}`. Playing needs the GUI or an attached MCP
  session — headless `run` can create interactions but not play them.
- Live-verify: start the GUI with `--control <port>`, drive with `scripts/mcp_drive.py`
  (open file, start preview, timed `screenshot {window:true}` catches frames mid-animation).

## Design → code (Dev Mode)

- `inspect.code {id, language: css|html|react|leptos|swiftui|compose, unit: px|rem, rootFontSize}`
  — write results to `exports/code-export/` FILES; users want files, not console dumps.
- `codeConnect.set {id, language, importPath, name}` — afterwards `inspect.code` returns the
  project's real import + snippet instead of generated markup.
- `inspect.properties {id, colorFormat: hex|rgb|css|hsl|hsb}`; `inspect.assets {ids}` +
  `file.exportLayers {assets:true}` (needs export settings on layers to be non-empty).

## Video/GIF (no native export — use ffmpeg)

1. Re-render the prototype's timeline as frames: one top-level frame per step in ONE document,
   named `f_%03d`, parameterizing opacity/y with the same easings/durations as the interactions
   (e.g. cubic ease-out `1-(1-p)^3`, back ease `1+c3*(p-1)^3+c1*(p-1)^2`, c1=1.70158).
2. `export doc --out throwaway/frames/ --format png` → `f_000.png …`
3. MP4 with dissolves between segments:
   ```
   ffmpeg -framerate 30 -i frames/f_%03d.png -framerate 30 -loop 1 -t 2 -i still_b.png ^
     -filter_complex "[0:v]fps=30,format=yuv420p[a];[1:v]fps=30,format=yuv420p[b];[a][b]xfade=transition=fade:duration=0.5:offset=<durA-0.5>[o]" ^
     -map "[o]" -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4
   ```
4. GIF (two-pass palette in one filter):
   ```
   ffmpeg -i out.mp4 -vf "fps=15,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" out.gif
   ```
5. Report honestly: this replays the prototype's motion, it is not a capture of the player.
