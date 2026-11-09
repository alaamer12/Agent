# Provider: OpenAI (`openai`)

Direct OpenAI image generation and editing API.

- **Base URL**: `https://api.openai.com/v1`
- **Auth**: `Authorization: Bearer $OPENAI_API_KEY`
- **Docs**: `https://platform.openai.com/docs/guides/image-generation`
- **Status**: Verified 2026-10-04.

## Image Generation & Editing
- **Endpoint**: `POST /images/generations` (generate), `POST /images/edits` (edit)
- **Mode**: Synchronous. GPT Image models return `b64_json` base64 strings.
- **Models**:
  - `gpt-image-2.5-flare` — Fast everyday generation (default).
  - `gpt-image-2.5-sunburst` — High precision, multi-reference editing.
- **Parameters**: `size` (`1024x1024`, `1536x1024`, `1024x1536`), `quality` (`low`, `medium`, `high`, `xhigh`), `n`.
- **Note on edits**: Edits use multipart form encoding with source image mask/reference.

## Video Status
- **Notice**: OpenAI Sora 2 models and the Videos API were shut down on **September 24, 2026**. OpenAI does not offer a public video generation API. Video requests route to KovAPI, xAI, or Google Gemini Omni.
