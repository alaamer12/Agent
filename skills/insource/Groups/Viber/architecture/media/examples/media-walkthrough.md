# Worked walkthrough: one landing screen through imgery

A composite screen — hero photo, "Sign up with Google" button, a feature
explainer video embed, icon row in the nav, brand marketing face — taken
through the pillar. Identifiers are illustrative; numbers come from the
references' cited evidence.

## Phase 0 — recon (what the code answered before any question)

- Hero: one hand-placed `hero.jpg` 640 KB, no `srcset`, `loading="lazy"`
  present → **the LCP candidate is lazy-loaded** (raster-loading §4 violation,
  the verified 3.5 s vs 2.9 s p75 pattern).
- Google button: inline `<svg d="…">` with three paths, two fills, circle
  "close enough" → hand-drawn glyph (brand-marks §law violation: wrong mark +
  trademark exposure; also the `viewBox` was cropped tight — the ring's outer
  stroke clipped, the geometry-contract symptom).
- Video: raw `<iframe youtube.com/embed/…>` above mid-fold → ~540 KB player
  + 100 KB–2 MB JS on page load with most visitors never pressing play
  (time-based-media §1 cost model).
- Icons: mixed Heroicons stroke set + a Font Awesome filled import + two
  hand-written paths → three grammars disagreeing at 16 px (svg-engineering
  §2–3: stroke weight/gap/corner noise).
- Fonts: Inter 6 weights as separate WOFFs, `font-display` unset, no fallback
  metrics → FOUT shift on every headline (fonts-delivery §4–5).

## Phase 1 — the interview answered only what the code couldn't

- Primary content: hero photo and CTA *are* the page purpose; the video is
  explanation most visitors skip → facade required (three-condition test).
- Brand authority: no design contact → vendor official Google asset, pinned.
- Network: p75 mobile 4G → hero budget set at ≤200 KB to hold LCP ≤2.5 s.

## Phase 2 — decisions per lane

1. **Pipeline:** one transform step emits AVIF→WebP→JPEG at declared widths;
   hero ships `w`+`sizes="80vw"`, eager + `fetchpriority="high"`, width/height
   attributes present; below-fold feature shots get `loading="lazy"` +
   `decoding="async"`. Result measured: 640 KB → 88 KB AVIF at 1200 px.
2. **Brand mark:** official "Sign in with Google" button artwork (per the
   brand-guidelines vector package), colors/geometry untouched, file committed
   with revision pinned and byte-verified (multi-path check passed — the
   fahlwy grading test); the drawn SVG deleted, ledger row added with a
   rights note.
3. **Icons:** one stroke grammar (24 px grid, 2 px round-cap) as components;
   color via `currentColor` + `--icon-secondary` where a badge needs it;
   Font Awesome import dropped (attribution debt + grammar clash); FA-
   style glyphs only ever return via the ledger if officially sourced.
4. **Embed:** swapped to a maintained lite-YouTube facade (nocookie default,
   self-probed `hqdefault` poster fallback ladder, keyboard-operable button,
   click = consent, aspect-ratio box so swap causes zero shift). First-render
   third-party JS measured at 0 KB.
5. **Fonts:** marketing face kept (brand load-bearing): WOFF2, two subsets
   (Latin + the shipped RTL locale), `swap` for the display face, `optional`
   for nothing (body moves to `system-ui` — the audit found Inter body was
   the only weight carrying meaning *nowhere*), plus `size-adjust` fallback
   table computed once. CLS after swap measured 0.00.
6. **Delivery:** hashed URLs + `immutable` max-age on the CDN; sanitizer
   (DOMPurify `svg:true`, or `setHTMLUnsafe` with audited allow-config) wired
   for the one user-upload SVG path — with the `<use>`-strips-in-baseline
   caveat handled at the sprite shell.

## Phase 3 — document & verify

`media-architecture.md` written from the template: LCP declaration, pipeline,
ledger rows, icon grammar, facade table, font table, budgets, sync points
(transform config ↔ doc; token file ↔ §5). Negative test shipped: an uploaded
`<svg><script>` renders inert through `<img>`; reduced-motion freezes the one
Lottie loop to its snapshot; slow-profile load shows zero reflow after the
hero placeholder resolves.

The lesson in one line: every fix above was a *decision the defaults refused
to make* — recon surfaced the habits, the interview pinned the costs, the
references carried the numbers, and the document makes them binding for the
next contributor, human or model.
