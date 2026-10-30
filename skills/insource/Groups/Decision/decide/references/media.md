# Media in the showcase

Images are one example. A showcase can use any medium: [images] [audio] [video] [PDFs and documents] [3D models] [fonts] [maps] [interactive demos] [data files] [any other medium a decision depends on]. The options here are illustrative. A hybrid or unlisted medium is always acceptable.

## Principles for every medium

1. **Source it.** Take media from official pages, documentation, press kits, or files the user uploaded. Never invent or guess a URL.
2. **Verify it before it goes on the page.** It exists, can be fetched, is the right kind of file (not an HTML error page), is not empty or corrupt, opens or plays, and has a sane size.
3. **Fail gracefully.** If an item fails to load, show a placeholder with its description and a link to the source. Never leave a broken control.
4. **Describe it.** Alt text for images, captions or a transcript for speech, a visible credit and source link for everything.
5. **Respect where the page runs.** Opened as a local file, remote URLs work. Some hosted viewers block remote and local-file media (check the environment's rules, since they change). Then embed small items as `data:` URIs (base64 adds about a third, and the page must stay within the host's size limit) and link out for large ones with a poster image or key frame. Tell the user which items were linked.
6. **Think about print.** Media cannot play on paper. In the PDF print a poster or key frame, the caption, the duration if any, and the visible URL.
7. **No surprises.** Controls visible, no autoplay with sound, `preload="metadata"`.
8. **Rights.** Prefer media the source allows to be shown, and credit it.

## Patterns by medium

| Medium | How to show it | Checker | In print |
|---|---|---|---|
| Image | `<figure><img alt loading="lazy">` with caption (see `page-structure.md`) | `check_images.py` | the image |
| Audio | `<audio controls preload="metadata" src>` with a label and duration | `check_media.py` | label, duration, URL |
| Video | `<video controls preload="metadata" poster>` plus `<track kind="captions">` when there is speech | `check_media.py` (poster with `check_images.py`) | poster, caption, URL |
| PDF or document | link card with a thumbnail; avoid iframes (often blocked) | `check_media.py` | title, page count if known, URL |
| 3D model | rendered stills or a short turntable video, plus a link to the model file | `check_media.py` for `.glb`/`.gltf` | stills |
| Font | specimen text rendered with `@font-face` from a `data:` URI | `check_media.py` | specimen |
| Anything else | link plus a preview image | write a checker (below) | preview image, URL |

Examples:

```html
<figure class="clip"><audio controls preload="metadata" src="URL-OR-DATA-URI"></audio>
  <figcaption>Microphone A, speech sample, 0:12. <a href="PAGE-URL" rel="noopener">Source</a></figcaption></figure>

<figure class="clip"><video controls preload="metadata" poster="POSTER-URI" src="URL-OR-DATA-URI">
  <track kind="captions" src="CAPTIONS-URI" srclang="en" label="English">
  <a href="URL">Open the video</a></video>
  <figcaption>Camera B, low-light test. <a href="PAGE-URL" rel="noopener">Source</a></figcaption></figure>
```

## Checkers that ship with this skill

- `scripts/check_images.py`: images.
- `scripts/check_media.py`: audio, video, PDF, `.glb`/`.gltf`, fonts. It checks the file signature against the extension, rejects HTML error pages and empty files, and uses `ffprobe` for audio and video duration when installed.

Both print `OK`, `WARN` or `PROBLEM` per reference, support `--hosted` and `--browser`, and exit 1 on any PROBLEM. Keep full URLs as plain string literals in the page's data so the scripts can find them.

## When no script exists for a medium

The agent may, and should, write one. Do not put an unchecked medium on the page.

1. Name the medium and how a broken file of that kind fails: an HTML error page saved with the right extension, a truncated download, the wrong codec, zero duration, a bad signature, the wrong sample rate or dimensions.
2. Write `scripts/check_<medium>.py` (next to the page if the skill folder is read-only). Start from `check_media.py`: keep `collect`, `check`, `verify` and the report format, and add the extensions, the file signature and any decoder or probe the medium needs.
3. Test it before trusting it. Run it on one known-good file and at least four bad ones: missing, corrupt or truncated, wrong type (for example HTML), and a blocked host. Confirm each is reported correctly.
4. Run it on the page and fix every PROBLEM.
5. Tell the user the script's name, what it verifies, and what it cannot verify (for example "plays in headless Chromium, not tested in Safari").

Contract for any checker:

- Usage `python check_<medium>.py page.html [--hosted] [--browser]`, with a docstring that states coverage and limits.
- Find references in attributes and in plain string literals, remove duplicates, report line numbers.
- One line per reference: `OK|WARN|PROBLEM line N: reference: detail`. PROBLEM means verified bad. WARN means it could not be confirmed (network blocked, optional tool missing). Never turn "could not check" into OK.
- A summary line, and exit code 1 on any PROBLEM.
- Standard library first. Detect optional tools (`ffprobe`, Pillow, ImageMagick, `exiftool`, a CLI for the medium) with `shutil.which` and say in the output when one is missing.
- `--hosted`: every reference must be embedded or linked out.
- `--browser`: a real load or playback test when a browser can do it.
- Network access only to fetch the referenced URLs, with a timeout and a size limit.
