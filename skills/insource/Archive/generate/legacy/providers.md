# Provider Reference — Valid as of 2026-10-04

**Note:** since v2.0 the machine-readable rows in `../data.csv` are the
source of truth for the engine (endpoints, param maps, features, pricing);
this file remains the human-readable deep detail. When they disagree, the
registry row wins — and the row's `status`/`valid_as_of` columns tell you
what was actually verified. For adding new vendors see
`provider-onboarding.md`.

All endpoints, model IDs, and parameters were verified against official documentation on **2026-10-04**. Re-validate before production use after 30 days.

## 1. xAI Grok Imagine

- **Base URL**: `https://api.x.ai/v1`
- **Endpoint**: `POST /images/generations`
- **Auth**: `Authorization: Bearer $XAI_API_KEY`
- **Recommended model**: `grok-imagine-image-2.0` (current generation; also accepts `grok-imagine-image` for older pricing tier)
- **SDK**: OpenAI-compatible (`base_url="https://api.x.ai/v1"`)

### Key parameters

| Parameter | Values | Notes |
|-----------|--------|-------|
| `model` | `grok-imagine-image-2.0` | Preferred |
| `prompt` | string | Required |
| `n` | 1–10 | Default 1 |
| `response_format` | `url` \| `b64_json` | Prefer `b64_json` for local save |
| `aspect_ratio` | `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`, `2:1`, `1:2`, `21:9`, `5:2`, `auto` | Default `auto` |
| `resolution` | `1k` \| `2k` | Default `1k` |
| `quality` | `low` \| `medium` \| `auto` | 2.0 model; auto maps generation→low, edit→medium |

### Example (Python, OpenAI SDK)

```python
from openai import OpenAI
import base64, os

client = OpenAI(api_key=os.environ["XAI_API_KEY"], base_url="https://api.x.ai/v1")
resp = client.images.generate(
    model="grok-imagine-image-2.0",
    prompt="...",
    n=1,
    response_format="b64_json",
    # aspect_ratio="1:1",  # optional
    # resolution="1k",
)
img_bytes = base64.b64decode(resp.data[0].b64_json)
```

### Pricing snapshot (2026-10-04)

- Grok Imagine Image 2.0: ~$0.04 (1k low) – $0.08 (2k medium) per image
- Older `grok-imagine-image`: ~$0.02 per image

Docs: https://docs.x.ai/docs/guides/image-generations

---

## 2. OpenAI GPT Image

- **Base URL**: `https://api.openai.com/v1`
- **Endpoint**: `POST /images/generations`
- **Auth**: `Authorization: Bearer $OPENAI_API_KEY`
- **Recommended models** (as of 2026-10-04):
  - `gpt-image-2.5-flare` — fast everyday generation (preferred default)
  - `gpt-image-2.5-sunburst` — higher-precision / editing fidelity
- **Deprecated / retired**: `dall-e-2`, `dall-e-3` (removed 2026-05-12); older `gpt-image-1*` series shutting down late 2026

### Key parameters

| Parameter | Values | Notes |
|-----------|--------|-------|
| `model` | `gpt-image-2.5-flare` / `gpt-image-2.5-sunburst` | Always set explicitly |
| `prompt` | string (up to ~32k chars) | Required |
| `n` | 1+ | Default 1 |
| `size` | `1024x1024`, `1536x1024`, `1024x1536`, `auto` | |
| `quality` | `low`, `medium`, `high`, `xhigh`, `max`, `auto` | |
| `response_format` | (returns `b64_json` by default for GPT Image) | |

GPT Image models return base64; there is no URL option for the current generation.

### Example (Python)

```python
from openai import OpenAI
import base64, os

client = OpenAI()  # reads OPENAI_API_KEY
result = client.images.generate(
    model="gpt-image-2.5-flare",
    prompt="...",
    size="1024x1024",
    quality="medium",
)
img_bytes = base64.b64decode(result.data[0].b64_json)
```

Docs: https://platform.openai.com/docs/guides/image-generation

---

## 3. Google Gemini Nano Banana (native image)

- **Base URL**: `https://generativelanguage.googleapis.com`
- **Preferred models** (2026-10-04):
  - `gemini-3.1-flash-image` — Nano Banana 2 (recommended workhorse)
  - `gemini-3.1-flash-lite-image` — cheapest / fastest
  - `gemini-3-pro-image` — Nano Banana Pro (highest quality)
- **Legacy**: `gemini-2.5-flash-image` retired / retiring; Imagen 4 shut down 2026-08-17
- **Auth**: `x-goog-api-key: $GEMINI_API_KEY` (or `GOOGLE_API_KEY`)

### Generation style

Use the Interactions / `generate_content` style (or the newer Interactions API). Images arrive as inline base64 parts.

### Example (Python, google-genai)

```python
from google import genai
from google.genai import types
import base64, os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"])

response = client.models.generate_content(
    model="gemini-3.1-flash-image",
    contents="Create a picture of ...",
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
        # image_config=types.ImageConfig(aspect_ratio="1:1")  # if supported
    ),
)

for part in response.candidates[0].content.parts:
    if part.inline_data is not None:
        img_bytes = part.inline_data.data  # already bytes in recent SDKs
        # or base64.b64decode(part.inline_data.data) depending on SDK version
```

Alternative (Interactions API, if available in the installed SDK):

```python
interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input="Create a picture of ...",
)
img_bytes = base64.b64decode(interaction.output_image.data)
```

Docs: https://ai.google.dev/gemini-api/docs/image-generation

---

## Fallback order used by genimage

1. xAI (`XAI_API_KEY`)
2. OpenAI (`OPENAI_API_KEY`)
3. Gemini (`GEMINI_API_KEY` or `GOOGLE_API_KEY`)

If a call fails with auth / quota / policy, the unified script tries the next provider automatically.
