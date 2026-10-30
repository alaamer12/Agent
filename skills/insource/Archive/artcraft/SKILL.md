---
name: artcraft
description: General skill for working with ArtCraft's family of open-source, agent-drivable design apps (Rust alternatives to vendor-locked tools) on Windows and Linux. Use when asked to use an ArtCraft app, design UIs (login screens, landing pages, mobile/desktop frames) with these apps, discover and drive their CLI/MCP command surfaces, fetch their docs, build or play prototypes with animations, export designs to code (CSS/HTML/React/SwiftUI/Compose/Leptos), or turn rendered frames into MP4/GIF via ffmpeg.
---

# ArtCraft Toolkit

## Overview

ArtCraft (getartcraft.com) builds open-source, pure-Rust creative tools that replace vendor-locked
suites and are **agent-drivable by design**: every menu action is a command, exposed through a CLI
(`<app>-cli`), a JSON control channel, and an MCP server. All ArtCraft apps share the same CLI
shape, docs layout (`github.com/storytold/<app>` → `docs/cli.md`, `docs/mcp.md`) and command
engine — learn the surface fresh for each app, but expect the patterns in
`references/cli-playbook.md` to hold.

Locate the CLI first: Windows `C:\Program Files\<App>\<app>-cli.exe`; Linux `which <app>-cli`
(also check `/snap/bin`); if not found, ask the user.

## Directory hygiene (MANDATORY)

Every working area gets this split — never mix the two:

```
<project-root>/
├── throwaway/            # ALL temp/mid-flight: generator scripts, run-script JSON,
│   └── docs/<app>/       #   fetched docs, frame dumps, probes, logs
├── <name>.<app-native>   # project files ONLY: native documents
└── exports/              # deliverables ONLY: images, code-export/, video/, gif/
```

- Generator scripts (Python that emits `run` JSON) live in `throwaway/`, never in the project root.
- Rendered animation frames go to `throwaway/frames/`; only the encoded MP4/GIF is a deliverable.
- The project must be reproducible from throwaway scripts: keep generators idempotent.
- The project root must contain no mid-flight files when work is reported as done.

## Core workflow

1. **Learn the surface before doing.** Never guess parameters:
   - `<app>-cli --help`, then dump the catalog: `<app>-cli commands --json` →
     `throwaway/commands.json`. Its per-command param strings are the authoritative spec.
   - Fetch canonical docs: `python scripts/fetch_docs.py <app> throwaway/docs/<app>`
     (pure Python, works on Windows/Linux/macOS).
   - Query live data: presets/fonts commands — don't assume device sizes or installed fonts.
2. **Build with `run` scripts**: a JSON array of `{"command": id, "params": {...}}` executed
   headless — all-or-nothing, with `{"$step": n}` references to ids created earlier in the same
   script. Generate large scripts with a Python generator in `throwaway/` (manual step numbering
   causes off-by-one parent-reference bugs).
3. **Verify by rendering, always:**
   ```
   python scripts/run_script.py <cli> throwaway/build.json --out design.<ext>   # clean failure lines
   <cli> export design.<ext> -o throwaway/preview.png --node "Frame" --scale 2
   ```
   Then LOOK at the PNG and fix: transparent cards, 100px-clipped rows, cut shadows, overflowing
   text, missing fonts. Expect 2–3 render-fix iterations; that is normal.
4. **Prototypes/animations:** the engine has real prototype support (triggers, smartAnimate,
   overlays, theme switches) — recipes in `references/cli-playbook.md`. Verify live: start the GUI
   with `--control <port>`, then `python scripts/mcp_drive.py <cli> <port> throwaway/steps.json`
   (open file, start preview, timed window screenshots catch frames mid-animation).
5. **Design → code:** `inspect.code` (css/html/react/leptos/swiftui/compose, px|rem) — **write the
   results to files under `exports/code-export/`**, don't just print console output.
6. **Video/GIF:** no native export. Re-render the prototype's timeline as 30fps frames through the
   CLI, export the frame dir, assemble with ffmpeg (xfade dissolves; palette GIF). Exact commands
   in `references/cli-playbook.md`. State honestly that it replays the prototype's motion, it is
   not a player capture.

## Key facts (full details: read references/cli-playbook.md before building)

- `run` is **all-or-nothing**: one bad step rolls back everything; error text is precise — read it.
- Raw integers in params are literal node ids; use `{"$step": n}` for anything the script created.
- New frames default to **100px wide and clip children** — set `sizingH:"hug"` / `clip:false` where needed.
- `fill` and `fills` collide — when both are present `fills` wins (the transparent-card bug).
- Colors accept `#RRGGBB`/`#RRGGBBAA` inline anywhere; gradients inline; `padding` = [t,r,b,l]; y-down.
- Auto-layout children are positioned by `layout/gap/padding/mainAlign/crossAlign/sizingH|V`, not x/y.
- Smart-animate entrances = N state frames with identical layer names + `afterDelay`→`navigate`+`smartAnimate`.
- MCP: `<app>-cli mcp` is headless; `--attach <port>` drives the running GUI (`--control <port>`).
- Confine agent file access with `--automation-read-root/--automation-write-root`.

## Resources

- `scripts/fetch_docs.py` — download any ArtCraft app's docs from GitHub (pure Python, cross-platform).
- `scripts/run_script.py` — run a `run` script; prints only failures/writes, resolves frame ids (`--ids`).
- `scripts/mcp_drive.py` — JSON-steps driver for an attached MCP session (tools, waits, screenshots).
- `references/cli-playbook.md` — distilled field manual: subcommands, engine conventions, verified
  gotchas, prototype recipes, code-export options, ffmpeg commands.
