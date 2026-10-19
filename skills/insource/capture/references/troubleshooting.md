# Troubleshooting

Run `python scripts/check_env.py` first; it prints the exact fix for missing pieces.

| Symptom | Cause / fix |
|---|---|
| `ModuleNotFoundError: playwright` | `pip install playwright` |
| `Executable doesn't exist ... chromium` | `playwright install chromium` |
| Browser launch fails in a container | Add system deps: `playwright install --with-deps chromium` |
| `No designs folder found` | Pass `--dir <folder>`; check you're at the project root |
| `Unknown page(s)` | Run `designs --list` and use names exactly as printed |
| Dark capture looks light | Page uses localStorage or custom toggle: `theming.md` |
| Fonts/images missing | Assets are outside the served folder, or CDN blocked offline. Serve a parent folder with `--dir`, or use `--base-url` |
| Timeout on `networkidle` | Page keeps a connection open: add `--wait-until load` |
| Images missing in a full-page capture | Lazy-loaded content: add `--lazy` (and maybe `--wait-ms 800`) |
| `--output is for one target...` | Several targets, `--scroll` or `--slices`: use `--output-dir` |
| `No such file: x.html` | Path typo; `.html` targets are never treated as domains |
| Images differ in height between runs | `--full-page` on pages with dynamic content; pin `--width/--height` and drop `--full-page` |
| `page`: "needs Windows" / "Missing dependency" | Windows only; `pip install pywin32 psutil pillow` |
| `page`: `No matching window found` | Read the printed diagnosis; `page --list` (add `--include-hidden`) to see what exists; try `--title` |
| App capture is mirrored | `--flip-horizontal` (or `--no-flip-fix` if it is wrongly flipped) |
| Title bar not fully cropped | `--crop-top <px>` |
| `page`: title bar missing but you want it | `--include-frame` (window must be uncovered) |
| `page`: wrong window picked (helper/other) | `page --list`, then `--pid` or a more specific `--title` |
| `website`: "Nothing was downloaded" | Wrong URL, blocked/headless detection, or slow site: check the URL, raise `--timeout`, try `--wait-ms 5000` |
| `website`: VERIFY lists `404 ...` | Asset loads only later/on interaction or has a query string: raise `--wait-ms`/`--scroll-steps`, add `--depth` |
| `website`: VERIFY lists external hosts | Re-run with `--external [hosts]` |
| `website`: copy shows a blank page via `file://` | Serve it: `capture.py website --serve-only <dir>` |
| `website`: client-side routes 404 when served | Add `--spa` |
| `dom`: items missing from the saved HTML | Page didn't finish loading: raise `--max-rounds`, `--scroll-pause-ms`, add `--wait-for <selector>` or a site-specific `--click <button selector>` |
| `dom`: "reached --max-rounds" | More content exists: raise `--max-rounds` |
| `dom`: a button was clicked that shouldn't be | Use `--no-expand`, or narrow `--more-pattern` |
| `dom`: content still in JSON, not markup | Add `--api` and read `<name>.responses.json` |
| `dom`: file looks unstyled when opened | Expected (no assets saved): use `website` for a viewable copy, or `--base-tag` for a quick look |
| `dom`: navigation notice / timeout | Page never goes idle: `--wait-until load` and a larger `--wait-ms` |
| `design`: "MODE REQUIRED" (exit 2) | Ask the user: tokens, patterns, or both; then rerun with the mode |
| `design`: `curl not found` | Install curl (Windows 10+ includes `curl.exe`; check PATH) |
| `design`: "No CSS found" / tiny css.dump | CSS injected by JS or page is a shell: run `dom`, then `design ... --html-file`; or check `sources.json` for failed fetches |
| `design`: stylesheet skipped `HTTP 403/404` | Hotlink/auth protection or bad path: inspect `sources.json`; `--header` only if you're permitted |
| `design`: self-signed HTTPS fails | `--insecure` |
| `design`: want to re-analyse without refetching | `--reuse` (optionally `--out <folder>`) |
| `design patterns`: no repeated components | Small/unique page, or markup built by JS: use `--html-file` from `dom`, lower expectations |
| `screenshots`: `--selector ... matched no element` | Wrong selector, or the element renders later: check the selector, raise `--wait-ms` |
| `design`: text looks garbled | Check `encoding=` on the first line of `html.dump`; the page declared a different charset than its real one. Dumps are always UTF-8 |
| `design`: two runs for different pages overwrote each other | They no longer do (folder = host + path); pass `--out` to choose a folder yourself |
| `page`: "The window is minimized" | Restore the window, then capture again |
| `page`: `--target-size must look like 1280x800` / `--pad-color must be` | Fix the value; both are checked before capturing |
| `design patterns`: "No signature matched" but the site clearly uses something | Expected for unlisted or server-side tech: read **Raw evidence** (generator, headers, packages, attribute prefixes), then add a signature with `--signatures FILE` (`references/data-files.md`) |
| `design`: technology evidence has no header lines | Headers need a live fetch; `--html-file` and local files have none |
| `dom`: a "show more" button in another language isn't clicked | `--more-phrase "<its text>"` (and consider adding the language to `scripts/data/more_phrases.json`) |
| `dom`: a lazy image still has no `src` | The attribute name or value didn't look like a source: `--lazy-attr <name>` |
| `website`: an unwanted third-party host was saved with `--external` | `--block HOST` (repeatable) |
| `screenshots`: `--overlap ... must be smaller than the viewport height` | Use a smaller `--overlap` (default 100) or a taller viewport |
| `screenshots`: `would produce N screenshots` / `exceeds the cap` / `thinner than` | The mode would write too many or too thin images: use fewer slices, a smaller overlap, or raise `--max-shots` deliberately |
| `screenshots`: `Unknown device` | `--list-devices` (suggestions are printed for near-miss names) |
| `design`: `is not an HTML page` / `does not look like HTML` | Wrong URL (JSON, PDF, image) or a file without markup; if you have the rendered page saved, pass it with `--html-file` |
| `design`: a large stylesheet is missing | It exceeded `--max-bytes`; raise it |
| `website`: a real page was skipped as a "non-page link" | Its server reported a non-HTML `Content-Type`; check it, or use `--no-head-check` |
| `dom`: `warning: the response is ... not HTML` | The URL points at a file (PDF/JSON/image), not a page |

