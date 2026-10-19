#!/usr/bin/env python3
"""Unified multi-provider image generator. Tries providers in priority order."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

PROVIDERS = [
    ("xai", "XAI_API_KEY", "gen_xai.py"),
    ("openai", "OPENAI_API_KEY", "gen_openai.py"),
    ("gemini", ("GEMINI_API_KEY", "GOOGLE_API_KEY"), "gen_gemini.py"),
]


def key_available(spec) -> bool:
    if isinstance(spec, str):
        return bool(os.environ.get(spec))
    return any(os.environ.get(n) for n in spec)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a project asset image using the first available provider"
    )
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", required=True, help="Output image path")
    parser.add_argument(
        "--provider",
        choices=["xai", "openai", "gemini", "auto"],
        default="auto",
        help="Force a provider or let auto-select (default)",
    )
    # Pass-through optional flags that some providers understand
    parser.add_argument("--model", default=None)
    parser.add_argument("--size", default=None)
    parser.add_argument("--quality", default=None)
    parser.add_argument("--aspect-ratio", default=None)
    parser.add_argument("--resolution", default=None)
    args = parser.parse_args()

    order = PROVIDERS
    if args.provider != "auto":
        order = [p for p in PROVIDERS if p[0] == args.provider]
        if not order:
            print(f"ERROR: unknown provider {args.provider}", file=sys.stderr)
            return 1

    last_err = None
    for name, key_spec, script_name in order:
        if not key_available(key_spec):
            continue

        script = SCRIPT_DIR / script_name
        cmd = [sys.executable, str(script), "--prompt", args.prompt, "--out", args.out]
        if args.model:
            cmd += ["--model", args.model]
        if args.size and name == "openai":
            cmd += ["--size", args.size]
        if args.quality and name in ("openai", "xai"):
            cmd += ["--quality", args.quality]
        if args.aspect_ratio and name == "xai":
            cmd += ["--aspect-ratio", args.aspect_ratio]
        if args.resolution and name == "xai":
            cmd += ["--resolution", args.resolution]

        try:
            result = subprocess.run(cmd, check=False)
            if result.returncode == 0:
                return 0
            last_err = f"{name} exited {result.returncode}"
        except Exception as e:
            last_err = f"{name}: {e}"

    if last_err:
        print(f"ERROR: all providers failed. Last error: {last_err}", file=sys.stderr)
    else:
        print(
            "ERROR: no API keys found. Set XAI_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY / GOOGLE_API_KEY",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
