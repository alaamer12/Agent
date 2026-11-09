# Image Generation & Editing Guide

Read this file when generating or editing still images. For video generation, read `media/video.md`.

## Key Parameters for Images

| Parameter | Flags | Details |
|---|---|---|
| Prompt | `--prompt "..."` | The text prompt describing the desired image. Keep descriptions clear and specific. |
| Output | `--out <file/dir>` | Output path. Default extension is `.png`. Atomic download prevents partial saves. |
| Aspect / Size | `--size 1:1` or `16:9`, `1024x1024` | Mapped per vendor (`aspect_ratio` for xAI, `size` for OpenAI/KovAPI). |
| Resolution | `--resolution 1K` or `2K`, `4K` | Provider-specific resolution tier (e.g. 1k vs 2k on xAI; 1K/2K/4K on KovAPI). |
| Quality | `--quality low / medium / high` | Supported on xAI 2.0 and OpenAI GPT Image. |
| Variations | `--variations N` | Generates N images for the prompt (vendor `n` if supported, else client fan-out). |
| Image inputs | `--image <file/url>` | Reference or input images (repeatable). Automatically converted to vendor format (data URL, b64, multipart). |
| Editing | `--edit` | Routes to the vendor's image edit endpoint (e.g. background removal, modifications). Requires `--image`. |
| Batching | `--batch N --concurrency C` | Parallel image generation requests with live progress bar and final summary table. |

## Provider Selection for Images

| Provider | Priority | Auth Env | Best Used For | Notes |
|---|---|---|---|---|
| `kovapi` | 10 | `KOVAPI_API_KEY`, `NEZHA_API_KEY` | High concurrency (up to 50), GPT Image flare/sunburst, nano-banana | Async job: submit -> poll -> download. 7-day retention. Formerly NezhaGate. |
| `xai` | 20 | `XAI_API_KEY` | Fast native generation, aspect ratio flexibility | `grok-imagine-image-2.0`, synchronous base64. |
| `openai` | 30 | `OPENAI_API_KEY` | High-fidelity editing and flare generation | `gpt-image-2.5-flare`, synchronous base64. |
| `gemini` | 40 | `GEMINI_API_KEY`, `GOOGLE_API_KEY` | Nano Banana native multimodality, reference images | `gemini-3.1-flash-image`, inline base64 parts. |

## Common Prompt Patterns for Assets

### UI / Icon
```text
Flat vector icon of a gear for a settings button, 512x512, transparent background,
soft indigo-to-violet gradient, clean geometric lines, centered, no text, no drop shadow
```

### Product / Hero
```text
Studio product photo of a matte-black wireless headphone resting on a soft blue fabric,
three-point soft lighting, shallow depth of field, 4:3, commercial advertising style
```

### Illustration / Feature Card
```text
Isometric 3D illustration of a small team collaborating around a floating kanban board,
pastel color palette, soft ambient occlusion, clean modern tech aesthetic
```

## Seeded Context Flow for Iterative Design
When iterating on style, seed a context first with initial directives and reference images:
```bash
python scripts/generate.py --context-seed brand-icons \
  --system "You are a brand asset designer. Produce minimal flat vector icons with primary indigo (#4F46E5) and slate accents." \
  --prompt "Base brand guidelines and style established." \
  --image logo-ref1.png \
  --image logo-ref2.png \
  --image https://example.com/palette.png

python scripts/generate.py --context brand-icons \
  --prompt "Icon of a shield with a checkmark for security status" \
  --out assets/shield.png
```
All multiple `--image` inputs are automatically loaded, encoded to Base64, and saved into the context turn. Subsequent generations in `--context brand-icons` replay previous generated icons and seeded references (up to `max_ref_images`).
