---
name: genimage
description: Multi-provider image generation for project assets using available API keys for xAI Grok Imagine, OpenAI GPT Image, and Google Gemini Nano Banana. Use when the agent needs to create, generate, or produce images, icons, illustrations, mockups, placeholders, or visual assets for a project. Always ask the user for permission before the first generation in a session. Triggers include genimage, generate image, create asset image, project image, AI image asset, multi-API image.
metadata:
  version: "1.0"
  valid-as-of: "2026-10-04"
  providers: xai,openai,gemini
---

# GenImage — Multi-Provider Project Asset Image Generation

Generate high-quality images for project assets by routing to the first available provider among xAI Grok Imagine, OpenAI GPT Image, and Google Gemini Nano Banana. Prefer the cheapest/fastest available key; fall back in order of availability.

**API validity date: 2026-10-04.** All model IDs, endpoints, and parameters below were verified against official docs on this date. Re-check docs.x.ai, platform.openai.com, and ai.google.dev before production use if more than 30 days have passed.

## Permission gate (mandatory)

Before any image generation in a conversation or project session:

1. Ask the user once, clearly: "I can generate project asset images using available API keys (xAI / OpenAI / Gemini). May I proceed when images are needed?"
2. Wait for explicit affirmative consent.
3. Cache the permission for the rest of the session / project; do not re-ask unless the user revokes it.
4. Never generate without this consent. If the user declines, fall back to describing the needed asset or using existing placeholders.

## When to use

- Creating icons, illustrations, mockups, product shots, UI assets, hero images, placeholders, or any visual deliverable that belongs to the project.
- The agent decides an image would improve the output and a suitable key is present.
- User explicitly requests an image asset.

Do **not** use for:
- Real-person likenesses without reference images and explicit user confirmation (follow image-gen-edit rules if available).
- Content that violates any provider's usage policy.
- Pure chat replies that do not need a file asset.

## Provider selection (deterministic)

Check environment variables (or a `.env` / secrets file the user has configured) in this priority order:

1. `XAI_API_KEY` → use **xAI Grok Imagine**
2. `OPENAI_API_KEY` → use **OpenAI GPT Image**
3. `GEMINI_API_KEY` or `GOOGLE_API_KEY` → use **Google Gemini Nano Banana**

If none are set, inform the user and stop. Never invent keys or call public free endpoints that require authentication.

Prefer the first available provider. Optionally let the user override with an explicit preference ("use Gemini", "prefer OpenAI").

## Core workflow

1. **Permission** — already obtained (see gate above).
2. **Detect keys** — run the detection helper or inspect env.
3. **Craft prompt** — concise, positive, project-specific. Front-load the subject. Include style, lighting, composition, aspect ratio needs. Avoid negative prompts.
4. **Call the selected provider** via the corresponding script in `scripts/`.
5. **Save** the resulting image under the project's assets directory (default `./assets/` or a path the user specifies). Use a descriptive kebab-case filename.
6. **Report** the local path and which provider was used. Do not expose raw API keys or full base64 in the reply.

## Prompt guidelines for project assets

- Be specific about purpose: "flat vector icon for a settings button, 512×512, transparent background, soft indigo gradient"
- Match the project's visual language (colors, style, mood) if known.
- For UI assets prefer clean, simple, high-contrast designs.
- For marketing / hero images allow richer cinematic language.
- Always request the aspect ratio or size the project needs.

## Output handling

- Scripts write PNG (or JPEG when the provider returns it) to the path you supply.
- After generation, confirm the file exists and is non-empty.
- Prefer storing under a project-relative path so the asset can be committed or referenced later.
- Never upload generated images to third-party hosts unless the user explicitly asks.

## Error handling

- Rate-limit / quota → try the next available provider.
- Invalid key → report which key failed and continue to the next.
- Content policy refusal → rewrite the prompt more conservatively and retry once; if still blocked, inform the user.
- Network / timeout → retry once with exponential back-off, then fall back.

## References

- Provider details, model IDs, parameters, and example payloads → `references/providers.md`
- Prompt patterns for common asset types → `references/prompt-patterns.md`
- Quick examples of end-to-end usage → `references/examples.md`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/detect_keys.py` | Print which providers have usable keys |
| `scripts/gen_xai.py` | Generate via xAI Grok Imagine |
| `scripts/gen_openai.py` | Generate via OpenAI GPT Image |
| `scripts/gen_gemini.py` | Generate via Google Gemini Nano Banana |
| `scripts/genimage.py` | Unified entry point — auto-selects provider |

All scripts accept `--prompt`, `--out`, and provider-specific flags. Run with `--help` for details.

## Safety & cost notes

- Each generation incurs real cost on the chosen provider. Prefer the cheapest available key for bulk assets.
- Never log or echo API keys.
- Respect each provider's content policies and rate limits.
- Generated images are project assets owned by the user; do not claim copyright for the model.
