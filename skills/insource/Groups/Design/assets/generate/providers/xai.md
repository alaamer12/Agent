# Provider: xAI (`xai`)

Direct integration with xAI Grok Imagine API for high-speed image and video generation.

- **Base URL**: `https://api.x.ai/v1`
- **Auth**: `Authorization: Bearer $XAI_API_KEY`
- **Docs**: `https://docs.x.ai/docs/guides/video-generations`
- **Status**: Verified from official docs 2026-11-09.

## Image Generation
- **Endpoint**: `POST /images/generations`
- **Mode**: Synchronous. Returns base64 or URL directly.
- **Default model**: `grok-imagine-image-2.0`
- **Parameters**: `aspect_ratio`, `resolution` (`1k`, `2k`), `quality` (`low`, `medium`), `n`.
- **Pricing**: ~$0.04 (1k low) to $0.08 (2k medium) per image.

## Video Generation
- **Endpoint**: `POST /videos/generations`
- **Mode**: Async job. Returns `request_id`.
- **Poll**: `GET /videos/{id}`. Polling is free. Status: `done` when complete, `failed`/`expired` on error.
- **Result**: `video.url` (MP4 video download link).
- **Models**:
  - `grok-imagine-video-1.5` ($0.08/sec) — native 1080p, lip-synced audio, supports up to 14 reference images.
  - `grok-imagine-video-1.5-lite` ($0.02/sec) — economical choice, upscales 720p to 1080p.
  - `grok-imagine-video` ($0.05/sec) — legacy workhorse.
- **Parameters**:
  - `duration`: 1 to 15 seconds (default 8).
  - `aspect_ratio`: `16:9`, `9:16`, `1:1`.
  - `resolution`: `480p`, `720p`, `1080p`.
  - `image`: URL object `{"url": "..."}` or data URL for image-to-video / starting frame.
- **Durability**: Results are retained for 1 day; downloaded immediately by the engine.
