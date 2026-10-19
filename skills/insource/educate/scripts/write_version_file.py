#!/usr/bin/env python3
"""
Write the .version file that registers a docs directory with the cache,
recording which version of the library the pruned docs + index correspond to.

USAGE
    python write_version_file.py <docs-dir> <version> --library NAME [--source URL]

See examples/version-file.example.json for the resulting format.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", help="Docs directory to register (created if missing).")
    parser.add_argument("version", help="Version these docs correspond to.")
    parser.add_argument("--library", required=True, help="Library/framework name.")
    parser.add_argument("--source", default=None, help="Optional: where Scrape retrieved this from (URL, path, etc.).")
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "library": args.library,
        "version": args.version,
        "cached_at": datetime.now().isoformat(),
    }
    if args.source:
        record["source"] = args.source

    version_path = docs_dir / ".version"
    with open(version_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    print(f"Wrote {version_path}")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
