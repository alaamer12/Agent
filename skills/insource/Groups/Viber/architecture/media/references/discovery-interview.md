# Media Architecture — discovery interview

Ask only what the codebase cannot answer (the parent's recon rules apply: the
repo's existing image/CDN usage, `<img>`/`<picture>` markup, `@font-face`
blocks, embed components, cache headers, and icon packages are read first).
Each question names the decision it seeds.

## A. What the media actually is

1. Which assets are the page's **primary content** — the thing the user came
   for? (This is the LCP candidate; it must never be lazy-loaded or facaded.
   Seeds §4 posture + §6 embed "primary?" column.)
2. Is any displayed "text" currently an image (banners, math, code
   screenshots)? Where locale or accessibility breaks because of it?
   (Seeds §2: CSS/SVG/web-fonts beat raster; text is never an image.)
3. Which looping GIFs / autoplay clips exist? (Seeds §2 GIF→video, §7 motion.)

## B. Icons and brand marks

4. Which **third-party brand marks** appear (sign-in buttons, payment,
   social)? Who is allowed to source them — is there a brand/press contact,
   or do we vendor official vectors pinned at a revision?
   (Seeds §3 ledger; this is the "Google button" question and it has a
   rights answer, not a taste answer.)
5. One icon grammar or several? Stroke weight, grid (16/20/24), caps/joins,
   corner radius — are they fixed tokens or per-pick from mixed libraries?
   (Seeds §5.)
6. Do consumers theme icon color per-part (hover, dark mode, `currentColor`)?
   Is a sprite `<use>` acceptable knowing its CSS inheritance limit, or must
   icons be components? (Seeds §5 delivery.)

## C. Performance posture

7. Who is the target user on which network — is a real p75 known (office
   fiber vs 3G mobile)? What byte budget does the hero image get there?
   (Seeds §9 numbers; blogs' examples are not evidence.)
8. Do the same icons/brand marks appear across many pages (cache/sprite win)
   or once per page (inline)? (Seeds §5 delivery + §8.)
9. Which third-party embeds exist, how far down the page, and does the user
   have to touch them to get value? (>100 KB JS + non-primary + interactive ⇒
   facade is required.) (Seeds §6.)
10. Is there an existing consent/CMP layer? Does "click the facade" double as
    consent, or is a gate needed? Does nocookie satisfy anyone in-org? (Seeds
    §6 consent column; remember nocookie ≠ consent.)

## D. Fonts and motion

11. Is the typeface load-bearing brand, or could `system-ui` carry body text?
    (Seeds §7; system-ui removes the download, the window, the shift, the
    pipeline, the audit.)
12. If a custom face: which locales/scripts ship (subsetting), what fallback
    do we metric-match, and does anyone accept a guaranteed-slow `block` vs a
    guaranteed-shift `swap` vs `optional` that may never paint? (Seeds §7.)
13. Which motion is essential vs decorative, and what is the static
    replacement per animated asset under `prefers-reduced-motion`? (Seeds §7;
    accessibility's user override outranks the default.)

## E. Delivery, caching, constraints

14. Do we control origin headers / a CDN / an on-the-fly optimizer, or are we
    on a fixed platform (which one)? Can we emit content-hashed immutable
    URLs? (Seeds §8; platform with no header control changes the answer from
    "set immutable" to "rely on hashed names + long max-age wherever you can".)
15. Are there data-saver / offline / embeddable constraints (mobile data,
    kiosk, content must work offline)? (Seeds §2 runtime, §8 SW.)
16. Which assets arrive from **users or third parties** (uploads, feed
    images)? Those SVGs/rasters need the sanitizer / image-mode path, not
    our optimization step. (Seeds §2 SVG security boundary.)
