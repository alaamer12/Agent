#!/usr/bin/env python3
"""fahlwy image-search helper using icrawler.

Discover candidate image URLs via Baidu / Bing / Google image search,
then hand them to verify_sources.py for real-byte validation.

Usage:
    python3 scripts/search_images.py "keyword" [--engine baidu|bing|google] [--max 30] [--out dir]

Requires: pip install icrawler

Engine ranking: Baidu is believed to have the highest precision. Bing and
Google frequently return raw trash, broken links, or non-direct assets.
Default to Baidu. Always run results through verify_sources.py — search
engines return page URLs or thumbnails that may not be direct asset links.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

try:
    from icrawler.builtin import BaiduImageCrawler, BingImageCrawler, GoogleImageCrawler
except ImportError:
    print("icrawler not installed. Run: pip install icrawler", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser(description="Search image engines for candidate asset URLs")
    p.add_argument("keyword", help="Search term, e.g. 'free stock photo landscape'")
    p.add_argument("--engine", choices=["baidu", "bing", "google", "all"], default="baidu")
    p.add_argument("--max", type=int, default=30, help="Max images to fetch per engine")
    p.add_argument("--out", default="scratch/search_images", help="Download root dir")
    p.add_argument("--offset", type=int, default=None,
                   help="Skip first N results (random 0-50 if omitted)")
    args = p.parse_args()

    offset = args.offset if args.offset is not None else random.randint(0, 50)
    root = Path(args.out)
    root.mkdir(parents=True, exist_ok=True)

    engines = {
        "baidu": BaiduImageCrawler,
        "bing": BingImageCrawler,
        "google": GoogleImageCrawler,
    }
    to_run = list(engines.keys()) if args.engine == "all" else [args.engine]

    for name in to_run:
        storage = {"root_dir": str(root / name)}
        crawler = engines[name](storage=storage)
        print(f"[{name}] keyword={args.keyword!r} max={args.max} offset={offset}")
        try:
            crawler.crawl(
                keyword=args.keyword,
                max_num=args.max,
                # offset is supported by some backends; harmless if ignored
                # offset=offset,
            )
        except Exception as e:
            print(f"[{name}] crawl failed: {e}", file=sys.stderr)

    # Print discovered files so the agent can feed them to the verifier
    found = list(root.rglob("*.jpg")) + list(root.rglob("*.jpeg")) + \
            list(root.rglob("*.png")) + list(root.rglob("*.webp")) + \
            list(root.rglob("*.gif"))
    print(f"\nDiscovered {len(found)} local files under {root}")
    for f in found[:20]:
        print(f"  {f}")
    if len(found) > 20:
        print(f"  ... and {len(found) - 20} more")


if __name__ == "__main__":
    main()
