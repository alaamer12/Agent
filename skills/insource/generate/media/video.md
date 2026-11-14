# Video Generation Guide

Read this file when generating or editing video clips. For still image generation, read `media/image.md`.

## Key Parameters for Video

| Parameter | Flags | Details |
|---|---|---|
| Media flag | `--media video` or `--video` | Directs the engine to video provider rows and video endpoints. |
| Prompt | `--prompt "..."` | Text description of the scene, camera movement, lighting, action beats, and audio. |
| Output | `--out <file/dir>` | Output path. Default extension is `.mp4`. Atomic download prevents partial saves. |
| Duration | `--duration <seconds>` | Integer seconds (e.g. `--duration 5`). Mapped per vendor (`5s` for Gemini Omni, integer for xAI/Wan). |
| Size / Aspect | `--size 16:9 / 9:16 / 1:1` | Aspect ratio for landscape, portrait/vertical, or square video. |
| Resolution | `--resolution 720P / 1080P` | Video resolution (e.g. `480P`, `720P`, `1080P`). Normalized across vendors. |
| Input Image(s) | `--image <file/url>` | Starting frame (first frame) or reference still. Auto-encoded to base64/URL object. |
| Image Role | `--image-role first_frame / reference` | Guidance for models supporting multi-image references (e.g. KovAPI Wan 3.0). |

## Provider Selection for Video

| Provider | Priority | Auth Env | Models | Pricing / Unit | Retention / Quirks |
|---|---|---|---|---|---|
| `kovapi` | 10 | `KOVAPI_API_KEY`, `NEZHA_API_KEY` | `seedance-2.0`, `wan3.0-video`, `minimax-h3`, `veo-3.1`, `grok-imagine-video-1.5` | ~$0.04 - $0.30 / sec (or per clip) | Async job: submit -> poll (`/v1/videos/jobs/{id}`) -> download MP4. 7-day retention. Formerly NezhaGate. |
| `xai` | 20 | `XAI_API_KEY` | `grok-imagine-video-1.5`, `grok-imagine-video-1.5-lite` | $0.02 - $0.08 / sec | Async job: `POST /v1/videos/generations` -> poll `/v1/videos/{id}` -> `video.url`. 1-day retention. |
| `gemini` | 40 | `GEMINI_API_KEY`, `GOOGLE_API_KEY` | `gemini-omni-1.2-flash`, `gemini-omni-1.1-flash` | Per second / token | Synchronous Interactions API (`POST /v1beta/interactions`), returns inline base64 MP4. Native audio & multimodality. |

*(Note: OpenAI Sora 2 and Videos API were shut down on 2026-09-24 and are not available in the registry).*

## Common Video Prompt Patterns

### Text-to-Video: Cinematic Scene
```bash
python scripts/generate.py --video \
  --prompt "Cinematic continuous drone shot sweeping over misty pine-covered mountains at sunrise, golden light breaking through fog, 4k photorealistic, ambient wind sound" \
  --duration 5 \
  --size 16:9 \
  --resolution 1080P \
  --out assets/mountains.mp4
```

### Image-to-Video: Animate a Product or Drawing
```bash
python scripts/generate.py --video \
  --image assets/product-still.png \
  --prompt "Slow 360-degree orbit around the product on a reflective dark studio turntable, studio lighting, smooth continuous motion" \
  --duration 8 \
  --resolution 720P \
  --out assets/product-turn.mp4
```

### Seeded Video Context (Multi-shot Continuity)
Seed a context with an anchor scene and reference images before generating iterations:
```bash
python scripts/generate.py --context-seed intro-sequence \
  --media video \
  --system "Cinematic cyberpunk aesthetic, rainy neon-lit streets, slow push-in camera motion." \
  --prompt "Establish visual mood, color grade, and lighting continuity." \
  --image scene-still-1.png \
  --image scene-still-2.png \
  --image character-sheet.png

python scripts/generate.py --context intro-sequence \
  --media video \
  --prompt "A lone courier in a trench coat walks down a damp alleyway, reflections on puddles" \
  --duration 5 \
  --out assets/shot1.mp4
```
Multiple `--image` flags are encoded and saved in the context turn, providing character and aesthetic consistency across all subsequent shots.
