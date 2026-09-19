# Viewport Sizing & Frameless Layout

> **What this owns:** the target dimensions per viewport, the frameless rules and the native affordances that replace device decoration, and how file count relates to viewport count. The URL-state contract is a different concern — see [`query-param-states.md`](query-param-states.md).

## Viewport definitions

| Viewport | Meaning | Layout width target | Notes |
|---|---|---|---|
| `desktop` (default) | The default webview frame inside any browser | Fluid, design for ~1280–1440px, with a sensible max-content-width (`max-width: 1200–1280px; margin: auto;` is typical) | No simulated browser chrome — it's a normal page. Should still be reasonably responsive down to ~768px unless the user only cares about one fixed width. |
| `tablet` | iPad-class viewport | ~768–834px wide, treat as portrait unless specified | Sits between mobile and desktop patterns — often a 2-column version of the mobile layout, or a narrower version of desktop. |
| `mobile` | Phone-class viewport | ~390–430px wide (iPhone-class), full-bleed | Design the layout itself for a single-column phone screen — sticky header, sticky bottom nav/tab bar, thumb-reachable primary actions near the bottom. |

Set the meta viewport tag on every file:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
```

## Frameless rules (critical)

"Frameless" means: no depiction of the device the page runs on. This includes avoiding:
- Rounded-rectangle phone bezels, camera notches drawn as UI, home-indicator bars unless they're a genuinely functional safe-area spacer.
- Fake browser toolbars/tabs/URL bars for desktop mockups.
- Drop shadows or perspective transforms that make the whole `<body>` look like it's "sitting" inside a device photo.

What frameless does NOT mean: skip realistic native affordances. Mobile and tablet mockups should still include, when relevant to the screen:
- `env(safe-area-inset-top)` / `env(safe-area-inset-bottom)` padding on sticky headers/footers.
- A sticky bottom tab bar or nav for app-like mobile mockups, sized ~56–64px tall plus safe-area inset.
- Touch-sized tap targets (44px+ minimum height for buttons/rows).
- `overscroll-behavior-y: none` on `html`/`body` to prevent rubber-band scroll bleed feeling like a webpage instead of an app, if the mockup is meant to feel like a native app screen.

For desktop, "frameless" mostly just means: don't wrap the page in anything. Build the actual page content edge-to-edge as it would appear in a real browser tab.

## Single-file vs multi-file responsive

- Single file, one viewport (most common default): fixed target width via the `.app`/container max-width, no need for extensive media queries.
- Single responsive file covering multiple viewports (only when explicitly requested): use standard Tailwind responsive prefixes (`md:`, `lg:`) and design the mobile layout as the base, progressively enhancing upward — this is more code than separate files but is what "one responsive file" means.
- Multiple files, one per viewport (default when multiple viewports are wanted but not explicitly "one responsive file"): each file is independently laid out for its target width, sharing the same visual language (colors, type, components) but not sharing markup structure. This is almost always less total code and less risk of layout bugs than forcing one DOM to reflow across all three breakpoints, which is why it's the default multi-viewport approach for this skill.

## Embedding a screen at a smaller size

These dimensions describe the screen's *own* viewport, and they hold when a screen is embedded somewhere else — a gallery preview of a mobile file must still lay out at 412×850, never at the size of the box showing it. The scaling mechanics for that case belong to [`gallery-index.md`](gallery-index.md) §2.
