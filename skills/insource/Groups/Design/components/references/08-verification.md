# Verification

A gallery is a claim about pixels, so it is verified by looking. Everything scripted narrows the search; none
of it substitutes for the render.

## 1. Static checks

```bash
node scripts/stories_check.mjs validate  js/stories.registry.js
node scripts/stories_check.mjs coverage  js/stories.registry.js --impl js/components
node scripts/stories_check.mjs urls      js/stories.registry.js --base http://localhost:<port> --out cards.txt
node scripts/stories_check.mjs --selftest          # 14 checks; proves the tool itself still works
```

`--impl` takes a directory of per-component renderers (shared mode) or a single `.js` bundle (cloned mode — the
tool says so, because cloned renderers drift). Exit codes: `0` clean, `1` findings, `2` usage/import error.

What they cannot tell you: whether a card looks right, whether a state is real, whether the disabled text is
legible in dark mode. That is what step 3 is for.

## 2. Server and routing

```bash
# start the project's dev command (per package.json / lockfile), then:
for u in / /index.pages.html /index.stories.html "/index.stories.html?show-only=disabled" \
         "/index.stories.html?id=toggle&show-only=invalid&theme=dark&dir=ltr" "/stories"; do
  printf "%s -> %s\n" "$u" "$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:<port>$u")"
done
```

Every entry answers directly, with a query string, and after refresh. The rename from `index.html` to
`index.pages.html` must leave no dead bookmark: the old gallery URL still resolves.

## 3. The force-every-card sweep

Read `cards.txt` and render each URL. Screenshot or browser — the criterion is **seen**.

Per card, ask four questions:

1. Is this visibly different from its neighbours? (Two identical cards = one fake state.)
2. Does it behave like the real thing? (Disabled control actually unfocusable; error message in the slot the
   product uses.)
3. Is it legible here? (Dark theme, compact density, RTL — the three places contrast and overflow hide.)
4. Could this be a screenshot from the app? (If the chrome is lying about the component, the card is.)

Automate the capture if the project has a browser tool; do not automate the judgement.

## 4. Hostile input

The gallery must degrade honestly, never crash and never fabricate:

```text
?show-only=nonexistent        → empty state naming the bad value; NOT the full gallery
?id=unknown-component         → empty state
?theme=sepia                  → default theme, page renders
?q=<90 characters>            → filtered or empty, layout intact
?show-only=disabled&show-only=invalid   → one wins predictably, no double-render crash
props.value = "<script>"      → rendered as text
missing props for a state     → the card says so; no blank box
a renderer that throws        → error card for that one state; the rest of the page renders
```

Also confirm the interaction rules: typing does not create 40 history entries; back/forward restores the exact
view; clearing search leaves the theme and direction alone; focus stays in the search box while typing.

## 5. Boundaries

- `index.stories.html` is thin: metadata, links, `data-page`, one script.
- `stories.css` contains no component styling; component CSS contains no gallery chrome.
- One state helper: `grep -rn "URLSearchParams" js/` should hit the helper only.
- No rule in `_app.css` that exists only for the gallery.
- No duplicated renderer where the shared one was chosen; no silent clone where the user chose shared.

## 6. The delivery report

```text
COMPONENTS  16 registered · 16 rendering · 0 error cards · 0 missing renderers
CARDS       61 states · 10 via:props (visually confirmed distinct)
MODE        shared renderers (js/components/) — user's choice, recorded
FACETS      dir(rtl default) · theme(light/dark/system) · density(comfortable/compact)
CHECKS      validate 0 · coverage 0 (2 notes) · routes 200 · 61/61 cards rendered
GAPS        file-picker has no permission-denied card: trigger exists in the upload flow, not implemented
DRIFT       3 components cloned from pages (numeric-field, slider, cookie-editor) — list with source lines
URLS        cards.txt (61) · shortcuts: ?show-only=disabled · ?show-only=invalid,error · ?dir=ltr
NEXT        index.html now routes to Pages | Stories; old gallery URL preserved
```

`GAPS` and `DRIFT` are the two lines that make the report credible. A report without them claims completeness
that no first pass has.
