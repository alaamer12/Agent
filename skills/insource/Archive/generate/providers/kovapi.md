# Provider: KovAPI (`kovapi`)

KovAPI (formerly NezhaGate) is an OpenAI-compatible multi-model gateway providing both image and video generation under one API key.

- **Base URL**: `https://kovapi.com/v1`
- **Auth**: `Authorization: Bearer <key>` via `KOVAPI_API_KEY`, `NEZHA_API_KEY`, or `NEZHAGATE_API_KEY`
- **Docs**: `https://docs.kovapi.com/en/api`
- **Status**: Documented 2026-11-09; image flow user-verified on gateway.

## Image Generation
- **Endpoint**: `POST /images/generations` (or `POST /images/edits`)
- **Mode**: Async job. Returns HTTP 202 with job `id` (e.g. `img_...`).
- **Poll**: `GET /images/jobs/{id}`. Status: `queued` -> `processing` -> `succeeded` / `failed`.
- **Result**: `data[0].url` (or `data[0].image_url`).
- **Models**: `gpt-image-2.5-flare` (default), `gpt-image-2.5-sunburst`, `nano-banana-2`, `nano-banana-pro`.
- **Pricing**: Billed in credits ($1 = 200 credits; 1 credit = $0.005). ~$0.005 to $0.05 per image based on resolution. Failed jobs are refunded automatically.

## Video Generation
- **Endpoint**: `POST /videos/generations`
- **Mode**: Async job. Returns HTTP 202 with job `id`.
- **Poll**: `GET /videos/jobs/{id}`. Status: `queued` -> `processing` -> `succeeded` / `failed`.
- **Result**: `data[0].url` (MP4 video download link).
- **Models**: `seedance-2.0` (default), `seedance-2.5`, `wan3.0-video`, `wan3.0-video-prime`, `minimax-h3`, `veo-3.1`, `grok-imagine-video-1.5`.
- **Parameters**:
  - `duration`: 4 to 30 integer seconds (model dependent).
  - `resolution`: `480P`, `720P`, `1080P`.
  - `size`: `16:9`, `9:16`, `1:1`, `4:3`, `3:4`, `adaptive`.
  - `images`: Array of image URLs or data URLs.
  - `image_role`: `first_frame` (for 1 or 2 images) or `reference` (up to 10 images).
- **Pricing**: Most models billed per output second ($0.04/s to $0.38/s). Select models (`veo-3.1`, `seedance-2.0-clip`, `grok-imagine-video-1.5`) billed per clip.

## Result Durability
- Result URLs expire after **7 days** (some older endpoints may retain for 15 days).
- The engine automatically downloads results immediately to disk upon job completion.
