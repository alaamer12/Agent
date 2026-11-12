# Theming (light/dark)

## Fast path
1. Add `--theme dark` to any browser command (`designs` also accepts `--themes dark`, or several themes).
2. If the page reads `localStorage`, add `--theme-key <key>`.
3. View the first dark image before reporting; a "dark" run can still render light.
4. If a body class/custom toggle drives the theme, use a URL param instead (last section).

`--theme light|dark` on `designs`, `screenshots`, `website`, `dom` and `images` (plus `--themes` on `designs`) applies three signals so most mockups switch correctly:

1. Emulate `prefers-color-scheme` (covers `@media (prefers-color-scheme: dark)`).
2. Toggle the `dark` class on `<html>` (Tailwind `darkMode: 'class'`, many hand-written mockups).
3. Set `data-theme="light|dark"` on `<html>` (DaisyUI, Radix-style tokens).

Without `--theme`/`--themes dark`, the page is left exactly as authored.

## Pages that read the theme from localStorage
Many mockups run an inline `<head>` script that reads a key before first paint (see `examples/sample-designs/index.html`). Signals 1-3 are applied *after* load, so such a page can flash or ignore them. Seed the key instead:

```
--theme-key <key>
```
Find the key: open the page source and search `localStorage.getItem(` in the head. The key is seeded with `light` or `dark` before any page script runs.

## Pages with a different mechanism
If dark mode is toggled by a body class, a custom attribute, or a button, none of the above applies. Either add a URL param to the mockup (preferred) and put it in `--url`, or tell the user the page needs a hook; don't silently ship a "dark" capture that is actually light. Verify by viewing the first dark image.
