# imgcurl Usage Patterns

Concrete command lines and expected outcomes. Paths are relative to the skill root.

## 1. Full-page capture (most common)

```bash
python scripts/download_images.py \
  --url "https://medium.com/@author/some-article" \
  --out ./artifacts/medium-article \
  --scroll to-end \
  --exclude "small|medium"
```

- Scrolls until the page height stabilises.
- Drops avatars and card-scale images.
- Upgrades every Medium asset to the original Miro URL when reachable.
- Produces `artifacts/medium-article/report.json`.

## 2. Scroll to a specific paragraph

```bash
python scripts/download_images.py \
  --url "https://example.com/long-read" \
  --out ./artifacts/up-to-paragraph \
  --scroll "the only thing I feel certain about" \
  --exclude "<=200x200"
```

Stops as soon as the normalised text appears in the viewport. Useful for long articles where only the first half is wanted.

## 3. Between two text anchors

```bash
python scripts/download_images.py \
  --url "https://example.com/guide" \
  --out ./artifacts/section-images \
  --scroll to-end \
  --between "Installation,Troubleshooting"
```

Keeps only images whose first network request occurred while the viewport was between the two text markers.

## 4. Pixel-range only (no text)

```bash
python scripts/download_images.py \
  --url "https://example.com/gallery" \
  --out ./artifacts/top-3000 \
  --scroll 4000 \
  --between 0,3000 \
  --min-bytes 5000
```

Ignores anything first seen after 3000 px and anything under 5 KB.

## 5. Headed debug run

```bash
python scripts/download_images.py \
  --url "https://example.com" \
  --out ./artifacts/debug \
  --scroll 2000 \
  --headed \
  --timeout 60000
```

Opens a visible browser window; useful when diagnosing why images are not loading.

## 6. Minimal (no scroll, no filters)

```bash
python scripts/download_images.py \
  --url "https://example.com/static-page" \
  --out ./artifacts/static
```

Captures only images that fire during the initial `networkidle` wait.

## Interpreting the Report

After any run, open `report.json` and check:

```json
"summary": {
  "totalImagesDiscovered": 42,
  "downloaded": 11,
  "deduplicated": 18,
  "excludedByCondition": 7,
  "authBlocked": 2,
  "failed": 1
},
"feedDetection": {
  "looksLikeInfiniteFeed": false,
  "reasoning": "New image requests stopped appearing after scroll step 4 …"
}
```

Always relay the summary counts and the feed-detection reasoning to the user. If `looksLikeInfiniteFeed` is true, warn that more images would appear beyond the configured scroll limit.
