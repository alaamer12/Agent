#!/usr/bin/env python3
"""Fetch one or more public GitHub raw files completely.

Usage:
  python fetch_skill.py URL
  python fetch_skill.py URL --output collected.txt

This helper intentionally uses only Python's standard library plus requests.
"""

import argparse
from pathlib import Path
import requests


def fetch(url: str) -> str:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--output", "-o")
    args = parser.parse_args()

    content = fetch(args.url)

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)


if __name__ == "__main__":
    main()
