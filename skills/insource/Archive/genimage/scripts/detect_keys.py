#!/usr/bin/env python3
"""Detect which image-generation providers have usable API keys in the environment."""

from __future__ import annotations

import os
import sys


def has_key(*names: str) -> bool:
    return any(os.environ.get(n) for n in names)


def main() -> int:
    providers = [
        ("xai", has_key("XAI_API_KEY")),
        ("openai", has_key("OPENAI_API_KEY")),
        ("gemini", has_key("GEMINI_API_KEY", "GOOGLE_API_KEY")),
    ]
    for name, ok in providers:
        print(f"{name}: {'available' if ok else 'missing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
