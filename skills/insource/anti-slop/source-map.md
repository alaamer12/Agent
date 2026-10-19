# Impeccable Slop catalog source map

Snapshot reviewed on 2026-10-06 from <https://impeccable.style/slop/>. The rendered page reports 67 catalog patterns, split into 61 source/browser detector rules and 6 design-review patterns. The local `antipatterns.json` and `registry.rs` each contain 60 records; the live page has one additional detector (`images-move-on-hover`) and six additional design-review entries.

The official page is preserved as rendered DOM/text at `assets/source/slop.html` and `assets/source/slop.txt`, with 23 sequential viewport captures under `assets/screenshots/slop/impeccable.style_slop/`. Catalog details and modality labels below follow that captured page. `Local ID` preserves an existing stable ID; `—` means the item is new relative to both supplied 60-entry sources and needs a new registry ID.

## Catalog entries

| # | Stable ID | Catalog name | Section | Modality | Local ID |
|---:|---|---|---|---|---|
| 1 | `design-system-font` | Font outside DESIGN.md | Your design system | Source | `design-system-font` |
| 2 | `design-system-color` | Color outside DESIGN.md | Your design system | Source | `design-system-color` |
| 3 | `design-system-radius` | Radius outside DESIGN.md | Your design system | Source | `design-system-radius` |
| 4 | `design-system-font-size` | Font size outside DESIGN.md | Your design system | Source | `design-system-font-size` |
| 5 | `codex-grid-background` | Decorative grid-line background | Visual Details | Source | `codex-grid-background` |
| 6 | `border-accent-on-rounded` | Border accent on rounded element | Visual Details | Source | `border-accent-on-rounded` |
| 7 | `glassmorphism-everywhere` | Glassmorphism everywhere | Visual Details | Design review | — |
| 8 | `side-tab` | Side-tab accent border | Visual Details | Source | `side-tab` |
| 9 | `gpt-thin-border-wide-shadow` | Hairline border with wide shadow | Visual Details | Source | `gpt-thin-border-wide-shadow` |
| 10 | `repeating-stripes-gradient` | Repeating-gradient stripes | Visual Details | Source | `repeating-stripes-gradient` |
| 11 | `extreme-border-radius-on-cards` | Extreme border-radius on cards | Visual Details | Design review | — |
| 12 | `rough-svg-illustrations` | Rough SVG illustrations | Visual Details | Design review | — |
| 13 | `kicker-above-heading` | Label above a heading | Typography | Source | `kicker-above-heading` |
| 14 | `undersized-ui-text` | Tiny interface text | Typography | Source | `undersized-ui-text` |
| 15 | `flat-type-hierarchy` | Flat type hierarchy | Typography | Source | `flat-type-hierarchy` |
| 16 | `icon-tile-stack` | Icon tile stacked above heading | Typography | Source | `icon-tile-stack` |
| 17 | `italic-serif-display` | Italic serif display headline | Typography | Source | `italic-serif-display` |
| 18 | `hero-eyebrow-chip` | Badge above the main headline | Typography | Source | `hero-eyebrow-chip` |
| 19 | `oversized-h1` | Oversized hero headline | Typography | Source | `oversized-h1` |
| 20 | `extreme-negative-tracking` | Crushed letter spacing | Typography | Source | `extreme-negative-tracking` |
| 21 | `overused-font` | Overused font | Typography | Source | `overused-font` |
| 22 | `single-font-for-everything` | Single font for everything | Typography | Design review | — |
| 23 | `all-caps-body` | All-caps body text | Typography | Source | `all-caps-body` |
| 24 | `radial-halo` | Radial-gradient background halo | Color & Contrast | Source | `radial-halo` |
| 25 | `radial-spotlight-glow` | Soft spotlight behind content | Color & Contrast | Source | `radial-spotlight-glow` |
| 26 | `ai-color-palette` | AI color palette | Color & Contrast | Source | `ai-color-palette` |
| 27 | `dark-glow` | Dark mode with glowing accents | Color & Contrast | Source | `dark-glow` |
| 28 | `gradient-text` | Gradient text | Color & Contrast | Source | `gradient-text` |
| 29 | `gray-on-color` | Gray text on colored background | Color & Contrast | Source | `gray-on-color` |
| 30 | `cream-palette` | Cream / beige palette | Color & Contrast | Source | `cream-palette` |
| 31 | `numbered-section-labels` | Tiny numbered section labels | Layout & Space | Source | `numbered-section-labels` |
| 32 | `edge-flush-cards` | Cards flush against the scroller edge | Layout & Space | Browser | `edge-flush-cards` |
| 33 | `text-occlusion` | Text covered by another element | Layout & Space | Browser | `text-occlusion` |
| 34 | `first-viewport-column-overflow` | Unbalanced opening columns | Layout & Space | Browser | `first-viewport-column-overflow` |
| 35 | `heading-rhythm` | Heading closer to the previous section | Layout & Space | Browser | `heading-rhythm` |
| 36 | `hero-metric-layout` | Hero metric layout | Layout & Space | Design review | — |
| 37 | `identical-card-grids` | Identical card grids | Layout & Space | Design review | — |
| 38 | `monotonous-spacing` | Monotonous spacing | Layout & Space | Source | `monotonous-spacing` |
| 39 | `nested-cards` | Nested cards | Layout & Space | Source | `nested-cards` |
| 40 | `line-length` | Line length too long | Layout & Space | Browser | `line-length` |
| 41 | `text-overflow` | Content overflowing its container | Layout & Space | Browser | `text-overflow` |
| 42 | `clipped-overflow-container` | Clipped menus and popovers | Layout & Space | Browser | `clipped-overflow-container` |
| 43 | `pulsing-dot` | Pulsing status dot | Motion | Source | `pulsing-dot` |
| 44 | `blinking-cursor` | Decorative blinking cursor | Motion | Browser | `blinking-cursor` |
| 45 | `marquee` | Auto-scrolling marquee | Motion | Source | `marquee` |
| 46 | `bounce-easing` | Bounce or elastic easing | Motion | Source | `bounce-easing` |
| 47 | `layout-transition` | Animation that changes layout | Motion | Source | `layout-transition` |
| 48 | `images-move-on-hover` | Images that move on hover | Motion | Source | — |
| 49 | `repeated-container-text` | Same text repeated inside one container | Copy | Source | `repeated-container-text` |
| 50 | `em-dash-overuse` | Em-dash overuse | Copy | Source | `em-dash-overuse` |
| 51 | `marketing-buzzword` | Generic marketing claims | Copy | Source | `marketing-buzzword` |
| 52 | `aphoristic-cadence` | Forced contrast | Copy | Source | `aphoristic-cadence` |
| 53 | `theater-slop-phrase` | Calling things “theater” | Copy | Source | `theater-slop-phrase` |
| 54 | `shape-assembled-illustration` | Placeholder-style illustrations | Imagery | Source | `shape-assembled-illustration` |
| 55 | `organic-clip-path` | Jagged image masks | Imagery | Source | `organic-clip-path` |
| 56 | `buried-raster` | Images hidden under overlays | Imagery | Source | `buried-raster` |
| 57 | `broken-image` | Broken or placeholder image | Imagery | Source | `broken-image` |
| 58 | `script-error` | JavaScript errors on load | General quality | Browser | `script-error` |
| 59 | `content-hidden-at-rest` | Content stuck waiting to appear | General quality | Browser | `content-hidden-at-rest` |
| 60 | `cramped-padding` | Cramped padding | General quality | Browser | `cramped-padding` |
| 61 | `body-text-viewport-edge` | Body text touching the page edge | General quality | Browser | `body-text-viewport-edge` |
| 62 | `justified-text` | Justified text | General quality | Source | `justified-text` |
| 63 | `low-contrast` | Low-contrast text | General quality | Source | `low-contrast` |
| 64 | `skipped-heading` | Skipped heading level | General quality | Source | `skipped-heading` |
| 65 | `tight-leading` | Tight line height | General quality | Source | `tight-leading` |
| 66 | `tiny-text` | Tiny body text | General quality | Source | `tiny-text` |
| 67 | `wide-tracking` | Wide letter spacing on body text | General quality | Source | `wide-tracking` |

## Example pages

The page presents 11 interactive demo cards. Each destination was opened, captured as rendered DOM and visible text, and captured visually; several pages require two sequential viewport captures. Modal Abuse also contains settings content that scrolls inside a dialog, with two additional internal-scroll captures.

| Example | Official URL | Related catalog IDs (visible demo findings) | Text / DOM | Screenshot captures |
|---|---|---|---|---|
| Purple Gradients Everywhere | <https://impeccable.style/antipattern-examples/purple-gradients> | `clipped-overflow-container`, `ai-color-palette`, `gradient-text`, `low-contrast`, `dark-glow` | `assets/source/examples/impeccable.style_antipattern-examples_purple-gradients.txt` | `assets/screenshots/examples/impeccable.style_antipattern-examples_purple-gradients/1.png`; `assets/screenshots/examples/impeccable.style_antipattern-examples_purple-gradients/2.png` |
| Lazy “Cool” | <https://impeccable.style/antipattern-examples/lazy-cool> | `glassmorphism-everywhere`, `dark-glow`, `hero-eyebrow-chip`, `text-occlusion`, `skipped-heading` | `assets/source/examples/impeccable.style_antipattern-examples_lazy-cool.txt` | `assets/screenshots/examples/impeccable.style_antipattern-examples_lazy-cool/1.png`; `assets/screenshots/examples/impeccable.style_antipattern-examples_lazy-cool/2.png` |
| Lazy “Impact” | <https://impeccable.style/antipattern-examples/lazy-impact> | `radial-spotlight-glow`, `gradient-text`, `low-contrast`, `bounce-easing`, `skipped-heading`, `ai-color-palette`, `marquee`, `dark-glow` | `assets/source/examples/impeccable.style_antipattern-examples_lazy-impact.txt` | `assets/screenshots/examples/impeccable.style_antipattern-examples_lazy-impact/1.png`; `assets/screenshots/examples/impeccable.style_antipattern-examples_lazy-impact/2.png` |
| Side-Tab Cards | <https://impeccable.style/antipattern-examples/thick-border-cards> | `side-tab`, `nested-cards`, `skipped-heading` | `assets/source/examples/impeccable.style_antipattern-examples_thick-border-cards.txt` | `assets/screenshots/examples/impeccable.style_antipattern-examples_thick-border-cards/1.png`; `assets/screenshots/examples/impeccable.style_antipattern-examples_thick-border-cards/2.png` |
| Cardocalypse | <https://impeccable.style/antipattern-examples/cardocalypse> | `nested-cards`, `text-occlusion`, `low-contrast` | `assets/source/examples/impeccable.style_antipattern-examples_cardocalypse.txt` | `assets/screenshots/examples/impeccable.style_antipattern-examples_cardocalypse/1.png`; `assets/screenshots/examples/impeccable.style_antipattern-examples_cardocalypse/2.png` |
| Copy-Paste Layouts | <https://impeccable.style/antipattern-examples/layout-templates> | `identical-card-grids`, `hero-metric-layout`, `ai-color-palette`, `low-contrast` | `assets/source/examples/impeccable.style_antipattern-examples_layout-templates.txt` | `assets/screenshots/examples/impeccable.style_antipattern-examples_layout-templates/1.png`; `assets/screenshots/examples/impeccable.style_antipattern-examples_layout-templates/2.png` |
| Inter Everywhere | <https://impeccable.style/antipattern-examples/inter-everywhere> | `overused-font`, `undersized-ui-text`, `low-contrast`, `icon-tile-stack`, `text-occlusion`, `skipped-heading` | `assets/source/examples/impeccable.style_antipattern-examples_inter-everywhere.txt` | `assets/screenshots/examples/impeccable.style_antipattern-examples_inter-everywhere/1.png`; `assets/screenshots/examples/impeccable.style_antipattern-examples_inter-everywhere/2.png` |
| Massive Icons | <https://impeccable.style/antipattern-examples/massive-icons> | `icon-tile-stack`, `skipped-heading` | `assets/source/examples/impeccable.style_antipattern-examples_massive-icons.txt` | `assets/screenshots/examples/impeccable.style_antipattern-examples_massive-icons/1.png` |
| Bad Contrast Choices | <https://impeccable.style/antipattern-examples/bad-contrast> | `low-contrast`, `gray-on-color`, `skipped-heading`, `ai-color-palette` | `assets/source/examples/impeccable.style_antipattern-examples_bad-contrast.txt` | `assets/screenshots/examples/impeccable.style_antipattern-examples_bad-contrast/1.png` |
| Redundant UX Writing | <https://impeccable.style/antipattern-examples/redundant-ux-writing> | `repeated-container-text`, `tiny-text` | `assets/source/examples/impeccable.style_antipattern-examples_redundant-ux-writing.txt` | `assets/screenshots/examples/impeccable.style_antipattern-examples_redundant-ux-writing/1.png`; `assets/screenshots/examples/impeccable.style_antipattern-examples_redundant-ux-writing/2.png` |
| Modal Abuse | <https://impeccable.style/antipattern-examples/modal-abuse> | `clipped-overflow-container`, `low-contrast`, `text-occlusion`, `flat-type-hierarchy` | `assets/source/examples/impeccable.style_antipattern-examples_modal-abuse.txt` | `assets/screenshots/examples/impeccable.style_antipattern-examples_modal-abuse/1.png`; `assets/screenshots/examples/modal-abuse-inner-full/01-001.png`; `assets/screenshots/examples/modal-abuse-inner-full/01-002.png` |

## Capture notes

- The Slop page was forced to render and expand before saving; the text export contains all section labels, all 67 names/descriptions, detection modalities, and the 11 example cards.
- Sequential page screenshots are numbered `1.png`–`23.png` under `assets/screenshots/slop/impeccable.style_slop/`.
- The example demos include the site’s detector overlays, which show the findings associated with each deliberately exaggerated design. Each screenshot path above includes all sequential scroll captures for that example; text exports preserve page copy and overlay labels.
- The Modal Abuse dialog is internally scrollable and clipped in the regular viewport. `scripts/capture_inner_scroll.py` captured two overlapping internal scroll states at `assets/screenshots/examples/modal-abuse-inner-full/`; the DOM/text capture also includes all settings through API Settings. The page's fixed preview clips the larger dialog even at a taller viewport, so these are the full available visual states rather than an uncropped export.
- The initial 60-source comparison preserves existing IDs and spelling. The seven net additions are six design-review entries plus `images-move-on-hover`; the six review-only entries must remain distinct from static detector rules.