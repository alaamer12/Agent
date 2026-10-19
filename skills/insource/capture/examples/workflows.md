# Example workflows

## 1. Capture every design, both themes
User: `/capture designs both themes`
```
python scripts/capture.py designs --themes light dark --theme-key app-theme
```
Report the page count and the output folder; view one dark image to confirm the theme applied.

## 2. Just one screen
User: "screenshot projects.html"
```
python scripts/capture.py screenshots --url design/projects.html --output .capture/projects/design_light.png
```

## 3. Design vs running app (parity loop)
Same viewport on both sides so images align 1:1.
```
python scripts/capture.py designs --pages projects --width 1280 --height 800
python scripts/capture.py page --list                    # find the window/PID first (Windows)
python scripts/capture.py page --name MyApp.exe --target-size 1280x800 \
    --output .capture/projects/app_v{n}.png
```
Compare `design_light.png` against the newest `app_vN.png`; after each fix, re-run only the `page` line.

## 4. Check what would be captured
```
python scripts/capture.py designs --list
```

## 5. Component only
```
python scripts/capture.py screenshots --url mockups/dashboard.html --selector ".sidebar" --output .capture/sidebar.png
```

## 6. Using a dev server
```
python scripts/capture.py designs --dir design --base-url http://localhost:5173 --pages home settings
```

## 7. Responsive check of live sites
User: "screenshot example.com and example.org on mobile and tablet"
```
python scripts/capture.py screenshots example.com example.org --view mobile --full-page --output-dir .capture/mobile
python scripts/capture.py screenshots example.com example.org --view tablet --full-page --output-dir .capture/tablet
```

## 8. Long page in reviewable chunks
```
python scripts/capture.py screenshots https://example.com/docs --slices 5 --lazy
python scripts/capture.py screenshots https://example.com/docs --scroll --overlap 150   # real-size steps
```

## 9. Fit more page into one image
```
python scripts/capture.py screenshots design/home.html --zoom 50% --full-page --output .capture/home_overview.png
```

## 10. Mirror a site for offline use
User: "download example.com so I can browse it offline"
```
python scripts/capture.py website https://example.com --depth 1 --external fonts.googleapis.com fonts.gstatic.com
python scripts/capture.py website --serve-only .capture/website/example.com --open
```
Read the VERIFY lines; if any `404` or external host remains, adjust and re-run (see `references/website.md`).

## 11. Quick single-page mirror (own site)
```
python scripts/capture.py website http://localhost:3000 --output-dir snapshot --no-verify
```

## 12. Scrape-ready HTML of a JS-heavy listing
User: "get all the products from shop.com/list, it loads more as you scroll"
```
python scripts/capture.py dom https://shop.com/list --text --api
python scripts/capture.py dom https://shop.com/list --click ".pager .load-next" --wait-for ".product-card" --max-rounds 40
```
Then parse `.capture/dom/shop.com_list.html` with BeautifulSoup; prefer `.responses.json` if it contains the product fields. Check the count against the page's own total.

## 13. Offline copy AND complete content
```
python scripts/capture.py website https://example.com --depth 1 --external
python scripts/capture.py dom https://example.com/catalog --api --text
```
`website` keeps it viewable offline; `dom` guarantees the expanded content is in markup (see `references/choosing.md`).

## 14. Several pages at once
```
python scripts/capture.py dom https://a.com/x https://b.com/y --output-dir .capture/dom
```

## 15. Extract a site's design system
User: "get the colors and typography of example.com"
```
python scripts/capture.py design tokens https://example.com
```
Read `.capture/design/example.com/design-system.md`; quote palette, body/code fonts, type scale, spacing grid, breakpoints. Raw CSS: `css.dump`.

## 16. HTML patterns for a clone (mode unclear? ask first)
User: "capture this site's design so I can recreate it" -> ask: tokens, patterns, or both?
```
python scripts/capture.py design both https://example.com
```
Then build from `design-system.md` (tokens) and `design-patterns.md` (skeleton, components + CSS, checklist).

## 17. JS-rendered site
```
python scripts/capture.py dom https://spa.example.com -o .capture/dom/spa.html
python scripts/capture.py design patterns https://spa.example.com --html-file .capture/dom/spa.html
```

## 18. Re-analyse without the network
```
python scripts/capture.py design tokens --reuse --out .capture/design/example.com
```

## 19. Verify the install
```
python scripts/check_env.py --smoke
```
