#!/usr/bin/env python3
"""Generate an image with Google Gemini Nano Banana (native image models)."""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Gemini Nano Banana image generation")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", required=True, help="Output file path (png)")
    parser.add_argument("--model", default="gemini-3.1-flash-image")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY or GOOGLE_API_KEY not set", file=sys.stderr)
        return 1

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("ERROR: google-genai package required (pip install google-genai)", file=sys.stderr)
        return 1

    client = genai.Client(api_key=api_key)

    # Prefer generate_content with IMAGE modality (widely available)
    try:
        response = client.models.generate_content(
            model=args.model,
            contents=args.prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
    except Exception as e:
        print(f"ERROR: generate_content failed: {e}", file=sys.stderr)
        return 1

    img_bytes = None
    # Walk candidates / parts looking for inline image data
    for cand in getattr(response, "candidates", []) or []:
        content = getattr(cand, "content", None)
        if not content:
            continue
        for part in getattr(content, "parts", []) or []:
            inline = getattr(part, "inline_data", None)
            if inline is not None:
                data = getattr(inline, "data", None)
                if data is None:
                    continue
                if isinstance(data, (bytes, bytearray)):
                    img_bytes = bytes(data)
                else:
                    img_bytes = base64.b64decode(data)
                break
        if img_bytes:
            break

    if img_bytes is None:
        # Fallback: try interactions API shape if present
        try:
            interaction = client.interactions.create(
                model=args.model,
                input=args.prompt,
            )
            out_img = getattr(interaction, "output_image", None)
            if out_img and getattr(out_img, "data", None):
                img_bytes = base64.b64decode(out_img.data)
        except Exception:
            pass

    if img_bytes is None:
        print("ERROR: no image data found in Gemini response", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img_bytes)

    print(f"provider: gemini")
    print(f"model: {args.model}")
    print(f"saved: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
