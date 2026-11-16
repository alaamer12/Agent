# End-to-End Examples

## 1. Detect available keys

```bash
python scripts/detect_keys.py
```

Possible output:

```
xai: available
openai: missing
gemini: available
```

## 2. Generate a UI icon (auto-select)

```bash
python scripts/genimage.py \
  --prompt "Flat vector icon of a rocket launch for a deploy button, 512x512, transparent background, indigo accent" \
  --out ./assets/icons/deploy-rocket.png
```

The script picks the first available provider, writes the PNG, and prints:

```
provider: xai
model: grok-imagine-image-2.0
saved: ./assets/icons/deploy-rocket.png
```

## 3. Force a specific provider

```bash
python scripts/gen_openai.py \
  --prompt "Studio product photo of a ceramic coffee mug, soft side lighting, 1:1" \
  --out ./assets/product/mug.png \
  --model gpt-image-2.5-flare \
  --size 1024x1024 \
  --quality medium
```

## 4. Agent conversation pattern

User: "Add a hero image for the landing page."

Agent (first time):
> I can generate project asset images using available API keys (xAI / OpenAI / Gemini). May I proceed when images are needed?

User: "Yes."

Agent:
> Generating a 16:9 hero image of a modern dashboard on a laptop in natural light…
> (runs genimage.py)
> Saved to `assets/hero-dashboard.png` via xAI Grok Imagine. You can drop it into the landing page.

## 5. Fallback behavior

If the primary key is rate-limited the unified script automatically tries the next provider and reports which one succeeded.
