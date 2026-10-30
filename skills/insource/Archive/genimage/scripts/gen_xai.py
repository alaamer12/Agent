#!/usr/bin/env python3
"""Generate an image with xAI Grok Imagine (OpenAI-compatible endpoint)."""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="xAI Grok Imagine image generation")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", required=True, help="Output file path (png/jpg)")
    parser.add_argument("--model", default="grok-imagine-image-2.0")
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--aspect-ratio", default=None)
    parser.add_argument("--resolution", default="1k", choices=["1k", "2k"])
    parser.add_argument("--quality", default=None, choices=["low", "medium", "auto"])
    parser.add_argument("--response-format", default="b64_json", choices=["b64_json", "url"])
    args = parser.parse_args()

    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("ERROR: XAI_API_KEY not set", file=sys.stderr)
        return 1

    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai package required (pip install openai)", file=sys.stderr)
        return 1

    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    kwargs = {
        "model": args.model,
        "prompt": args.prompt,
        "n": args.n,
        "response_format": args.response_format,
    }
    # xAI-specific optional params (passed through if the SDK allows extra)
    extra = {}
    if args.aspect_ratio:
        extra["aspect_ratio"] = args.aspect_ratio
    if args.resolution:
        extra["resolution"] = args.resolution
    if args.quality:
        extra["quality"] = args.quality

    try:
        resp = client.images.generate(**kwargs, **extra)
    except TypeError:
        # Older SDK may not accept extra kwargs; retry without them
        resp = client.images.generate(**kwargs)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    item = resp.data[0]
    if args.response_format == "b64_json" and getattr(item, "b64_json", None):
        data = base64.b64decode(item.b64_json)
        out.write_bytes(data)
    elif getattr(item, "url", None):
        import urllib.request
        with urllib.request.urlopen(item.url) as r:
            out.write_bytes(r.read())
    else:
        print("ERROR: no image data in response", file=sys.stderr)
        return 1

    print(f"provider: xai")
    print(f"model: {args.model}")
    print(f"saved: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
