# Provider: Google Gemini (`gemini`)

Google Gemini API for multimodal image generation and Gemini Omni video synthesis.

- **Base URL**: `https://generativelanguage.googleapis.com`
- **Auth**: `x-goog-api-key: $GEMINI_API_KEY` or `$GOOGLE_API_KEY`
- **Docs**: `https://ai.google.dev/gemini-api/docs/omni`
- **Status**: Verified 2026-11-09.

## Image Generation (Nano Banana)
- **Endpoint**: `POST /v1beta/models/{model}:generateContent`
- **Mode**: Synchronous. Generates inline base64 image parts in `candidates[0].content.parts`.
- **Models**: `gemini-3.1-flash-image`, `gemini-3.1-flash-lite-image`, `gemini-3-pro-image`.

## Video Generation (Gemini Omni Flash)
- **Endpoint**: `POST /v1beta/interactions` (Interactions API)
- **Mode**: Synchronous. The video is returned directly as inline base64 encoded MP4 in `steps[].content` with `"type": "video"`.
- **Models**:
  - `gemini-omni-1.2-flash` (recommended default)
  - `gemini-omni-1.1-flash` (auto-routes to 1.2 effective Dec 3, 2026)
- **Parameters**:
  - `duration`: `3s` to `15s` in `response_format.duration` (default `10s`).
  - `aspect_ratio`: `"16:9"` (default) or `"9:16"`.
  - `resolution`: `360p`, `720p` (default), `1080p`, `4k`.
  - `input`: Text prompt, plus up to 6 reference images for subject/character consistency or first/last frame interpolation.
- **Durability**: Because the video bytes are returned inline in the response, there is no URL expiration. The engine writes bytes directly to `.mp4`.
