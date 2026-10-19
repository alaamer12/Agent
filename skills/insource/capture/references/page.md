# `page` reference

Captures a running **Windows** desktop app window and crops the OS title bar so it lines up with chromeless HTML mockups. Uses the bundled `scripts/winshot.py` (Win32 `PrintWindow`), so the window can be covered or in the background.

## Contents
- Requirements
- Finding the window
- Capturing
- Cropping and canvas
- Numbered history
- Limits

## Requirements
Windows and `pip install pywin32 psutil pillow`. On other systems, or with a package missing, `page` exits with a one-line explanation (nothing else in the skill depends on these). `python scripts/check_env.py` reports what is installed.

## Finding the window
Give any of `--pid`, `--name` (process/exe name, case-insensitive, e.g. `notepad.exe`), `--title` (window-title substring); filters combine. `--wait N` waits N seconds first, useful right after launching an app.

- `--list` prints matching windows (PID, process, size, visible, title), largest first; with no filter it lists every visible titled window. Use it first when unsure.
- When several windows match, the largest is captured and the command says which one.
- **Helper processes:** Electron apps, browsers and IDEs run many processes under one executable name, and only one owns the main window. With `--name`, processes whose parent has the same name are treated as helpers and the root process's window is preferred. An explicit `--title` always wins over that preference.
- **Nothing found?** The command explains why (no such process / process exists but has no visible titled window / only hidden windows). `--include-hidden --list` shows hidden and untitled top-level windows (tray apps, cloaked windows).
- `--debug` logs every process/window considered and how it was filtered.

## Capturing
- Default: `PrintWindow` with full-content rendering, so GPU-rendered and modern apps capture correctly even when covered.
- `--include-frame`: grabs real screen pixels of the window's true outer bounds, **including the OS title bar and caption buttons** (PrintWindow cannot render those). The window is brought to the foreground and must not be covered by anything. Auto-cropping is off in this mode unless you pass `--crop-top`.
- **RTL windows** (Arabic/Hebrew layouts, `WS_EX_LAYOUTRTL`) come out horizontally mirrored from PrintWindow; this is detected and corrected automatically. `--flip-horizontal` forces a flip, `--no-flip-fix` disables the correction.
- The process is made DPI-aware, so sizes are true pixels, not scaled.

## Cropping and canvas
- Default: auto-detects a dark title band at the top by pixel colour and crops it (its parameters are named constants at the top of `page.py`). Light title bars are not auto-detected. Override with `--crop-top N` or disable with `--no-crop`.
- **`--crop-client`**: crops exactly to the client area from Win32 window geometry (title bar and borders removed, DPI-aware, no pixel heuristics). It cannot be combined with `--include-frame`, `--crop-top` or `--no-crop`. Its logic is covered by tests against a fake Win32 layer but it has not been exercised on a live window.
- `--target-size WxH` pads/crops to a fixed canvas after cropping (content centered horizontally, top-aligned). `--pad-color` fills the rest (default `#FFFFFF`; use the mockup's page background for cleaner diffs). Both options are validated before capturing, so a typo fails immediately.

## Numbered history
`--output .capture/home/app_v{n}.png` writes `app_v1.png`, then `app_v2.png`, ... so iterations are kept side by side.

## Limits
- Windows only; one window per run (no region/full-screen mode).
- A minimized window has nothing to render: it is marked `[minimized]` in `--list`, and capturing it stops with an error asking you to restore it.
- Protected/DRM content and some GPU surfaces can render black; try `--include-frame` (screen pixels) with the window uncovered.
- `winshot.py` is importable (`find_target_windows`, `capture_window`, ...) if a script needs the targeting logic directly; `scripts/test_winshot.py` tests it against a fake Win32 layer on any OS.
