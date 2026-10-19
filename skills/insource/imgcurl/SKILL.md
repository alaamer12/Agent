---
name: imgcurl
description: Download page images at highest resolution with scroll, text-range filtering, size exclusion, and perceptual deduplication via Playwright + curl_cffi. Use when the user asks to download images from a URL, scrape page images, capture Medium or lazy-loaded images, or extract unique high-res assets while skipping thumbnails.
---

# Imgcurl

Download images from any webpage while preserving the original highest-resolution version. Handles lazy loading, infinite feeds, WAF-protected endpoints (Medium GraphQL), text-range filtering, size-based exclusion, and perceptual deduplication.

## When to Use

- User wants images from a specific page or article (especially Medium, blogs, portfolios).
- Need to scroll to trigger lazy-loaded images or stop at a text marker.
- Filter images by vertical range (`--between`) or exclude thumbnails/avatars.
- Deduplicate resized variants and keep only the largest unique assets.

## Core Workflow

1. **Prepare output directory** — create a clean folder for downloads and the report.
2. **Choose scroll strategy** — none / pixel count / `to-end` / text-to-scroll-to.
3. **Optionally set bounds** — `--between min,max` (px or text anchors) to limit which images are kept.
4. **Optionally exclude sizes** — `--exclude small|medium|large|larger` or dimension rules.
5. **Run the script** — see `scripts/download_images.py`.
6. **Inspect report.json** — summary of downloaded, deduplicated, excluded, failed, and feed-detection reasoning.

## Quick Start

```bash
python scripts/download_images.py \
  --url "https://example.com/article" \
  --out ./downloads \
  --scroll to-end \
  --exclude "small|medium"
```

Common variants:

```bash
# Scroll a fixed distance
--scroll 5000

# Scroll until a text snippet is visible
--scroll "Right now, the only thing I feel certain"

# Keep only images first-seen between two text anchors
--between "Introduction,Conclusion"

# Exclude anything ≤ 400×400 or labeled small/medium
--exclude "<=400x400,small,medium"
```

Full CLI reference and flag semantics → `references/cli-reference.md`  
Architecture, dedup logic, Medium handling → `references/architecture.md`  
Concrete usage patterns → `examples/usage-patterns.md`

## Dependencies

- Python 3.10+
- `playwright` (+ Chromium browser)
- `curl_cffi` (TLS/JA3 impersonation for WAF)
- `Pillow`

```bash
pip install playwright curl_cffi pillow
python -m playwright install chromium
```

## Output

- Images written to `--out` with sane filenames derived from the original URL (extension corrected from magic bytes).
- `report.json` (or custom `--report`) containing:
  - options used, scroll log, text-match result
  - feedDetection (looksLikeInfiniteFeed + reasoning)
  - summary counts + full lists of downloaded / deduplicated / excluded / failed

## Agent Guidance

- Prefer the script over hand-rolled Playwright or requests code — it already solves canonical ID extraction, original-resolution upgrade, dHash dedup, and auth-blocked handling.
- After a run, always surface the `summary` section of the report and the feed-detection reasoning to the user.
- If the page is behind a strong WAF or requires login, the script may still capture publicly reachable image URLs; document any auth-blocked entries.
- Never invent new CLI flags; extend the existing script or open a follow-up task.

## Anti-patterns

- Do not re-implement image downloading with plain `requests` or Playwright `page.screenshot` when this skill is available.
- Do not download every variant of the same Medium/Miro asset — the canonical + dHash pipeline already keeps the largest unique one.
- Do not ignore the report; it is the source of truth for what was kept and why.
