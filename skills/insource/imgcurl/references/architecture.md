# imgcurl Architecture

High-level design of `scripts/download_images.py`. Agents should understand these invariants before modifying behaviour.

## Pipeline Stages

1. **Navigate + route GraphQL**  
   Playwright Chromium loads the page. Any request matching `**/_/graphql` is intercepted and re-issued via `curl_cffi` (Chrome 120 JA3 impersonation) so Medium and similar WAFs succeed.

2. **Observe image responses**  
   A `page.on("response")` handler records every image-like URL together with the current scroll position (`firstSeenAtScrollPx`). Bodies are buffered asynchronously.

3. **Scroll loop**  
   - `px` mode: stop after N pixels.  
   - `to-end` mode: stop when scrollHeight stabilises for two consecutive steps.  
   - `text` mode: evaluate a normalised DOM text search after every step; stop when the match is inside the viewport.  
   Each step is logged with the number of new image requests observed.

4. **Between filtering**  
   After scrolling, resolve `--between` into a pixel range (numeric or via the same text-finder) and discard images whose first-seen scroll position lies outside it.

5. **Canonical grouping**  
   For every remaining URL, `parse_canonical_asset_info` extracts a stable identity:
   - Medium / Miro → `medium:1*…` (or `0*…`) and an original un-resized candidate URL.
   - WordPress-style `-300x200` suffixes → strip to the base filename.
   - Everything else → basename or MD5 fallback.

6. **Highest-resolution upgrade**  
   For each canonical group:
   - Prefer the original Medium/Miro URL if it returns 200.
   - Otherwise keep the variant with the largest pixel count (tie-break by byte size).

7. **Perceptual deduplication**  
   Sort remaining assets by resolution descending. Keep an asset only if its 64-bit dHash differs by > 2 bits **or** its aspect ratio differs by ≥ 0.05 from every already-accepted higher-resolution asset. This collapses the same photograph served from different CDNs or under different filenames.

8. **Size exclusion & write**  
   Apply `--exclude` rules (label or dimension operators). Write survivors to disk with magic-byte-corrected extensions. Record every decision in the report.

## Key Helpers

| Function | Responsibility |
|----------|----------------|
| `detect_image_ext` | Magic-byte detection (PNG/JPEG/GIF/WEBP/AVIF/SVG). |
| `normalize_text` / `TEXT_FINDER_JS` | Cross-quote, dash, and unicode-normalised text search used by both scroll-to-text and `--between`. |
| `parse_canonical_asset_info` | Medium + WordPress + generic identity extraction. |
| `get_image_info` | Width, height, and 64-bit difference hash (dHash). |
| `get_image_size_label` | Maps max-dimension to small/medium/large/larger. |
| `matches_exclude` | Evaluates the parsed `--exclude` rule list. |
| `hamming_distance` | Bit-count distance between two dHashes. |

## Report Contract

The JSON report is the single source of truth. Important top-level keys:

- `options` — exact flags used (including resolved `betweenBounds` and `excludeRules`).
- `scrollLog` — array of `{fromPx, toPx, newImagesThisStep}`.
- `feedDetection.looksLikeInfiniteFeed` + `reasoning` — heuristic based on whether the tail of the scroll still produced new images.
- `summary` — counts for every outcome bucket.
- `downloaded`, `deduplicated`, `excludedByCondition`, `excludedByBetween`, `authBlocked`, `failed`, `skippedSmall` — full detail lists.

Agents must surface the `summary` and the feed-detection reasoning after every run.

## Design Invariants

- Never download a lower-resolution variant when a higher one for the same canonical ID (or perceptually identical image) is available.
- Prefer the original Medium/Miro asset over any resized CDN URL.
- Text matching is tolerant of curly quotes, en-dashes, and replacement characters.
- The overall `--timeout` is a hard deadline checked at every major stage.
- Auth-blocked (401/403) responses are recorded but never written as files.
