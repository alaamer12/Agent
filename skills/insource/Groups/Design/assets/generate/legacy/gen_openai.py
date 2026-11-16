#!/usr/bin/env python3
"""Generate an image with OpenAI GPT Image models."""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="OpenAI GPT Image generation")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", required=True, help="Output file path (png)")
    parser.add_argument("--model", default="gpt-image-2.5-flare")
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="medium")
    parser.add_argument("--n", type=int, default=1)
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        return 1

    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai package required (pip install openai)", file=sys.stderr)
        return 1

    client = OpenAI(api_key=api_key)

    result = client.images.generate(
        model=args.model,
        prompt=args.prompt,
        size=args.size,
        quality=args.quality,
        n=args.n,
    )

    item = result.data[0]
    b64 = getattr(item, "b64_json", None)
    if not b64:
        print("ERROR: no b64_json in response (GPT Image returns base64)", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(b64))

    print(f"provider: openai")
    print(f"model: {args.model}")
    print(f"saved: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
