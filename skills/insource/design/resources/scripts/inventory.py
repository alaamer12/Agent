"""Audit a project's asset files: duplicates, unreferenced assets, and external asset URLs.

Reports:
  duplicates    identical files by content hash (the same image saved under two names)
  unreferenced  asset files whose filename never appears in any scanned text file
  external      http(s) URLs ending in an asset extension found in source files - candidates for
                `localize.py` (icons/fonts/media still served from a third party)

Reference detection is textual (filename appears in a scanned file), which is what a broken rename
leaves behind; it is a signal, not proof - dynamic references (names built at runtime) are listed
under "unreferenced" even when the app uses them. Say so when reporting.

Usage:
    python scripts/inventory.py --root . --assets assets public/icons
    python scripts/inventory.py --root . --json > inventory.json

Requires: Python standard library only.
"""

import argparse
import hashlib
import json
import os
import re
import sys

ASSET_EXTENSIONS = {
    # images
    ".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".bmp", ".ico", ".svg", ".tif", ".tiff",
    # fonts
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    # audio
    ".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".opus",
    # video
    ".mp4", ".webm", ".mov", ".mkv", ".avi", ".m4v",
    # documents shipped as assets
    ".pdf", ".epub", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".odt", ".ods", ".odp",
}

CATEGORY_OF = {
    **{ext: "images" for ext in (".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".bmp", ".ico", ".svg", ".tif", ".tiff")},
    **{ext: "fonts" for ext in (".woff", ".woff2", ".ttf", ".otf", ".eot")},
    **{ext: "audio" for ext in (".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".opus")},
    **{ext: "video" for ext in (".mp4", ".webm", ".mov", ".mkv", ".avi", ".m4v")},
    **{ext: "documents" for ext in (".pdf", ".epub", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".odt", ".ods", ".odp")},
}
TEXT_EXTENSIONS = {
    ".html", ".htm", ".css", ".scss", ".sass", ".less", ".js", ".jsx", ".ts", ".tsx", ".vue",
    ".svelte", ".astro", ".md", ".mdx", ".json", ".yaml", ".yml", ".xml", ".cshtml", ".razor",
    ".dart", ".kt", ".java", ".swift", ".xaml", ".resx", ".py", ".go", ".rs", ".rb", ".php",
}
EXTERNAL_ASSET = re.compile(
    r"https?://[^\s\"'()<>]+\.(?:png|jpe?g|webp|gif|svg|ico|woff2?|ttf|otf|mp4|webm|mp3)(?:\?[^\s\"'()<>]*)?",
    re.I)
# Font CDNs serve a stylesheet that itself references the font files; the stylesheet is an asset
# dependency even though its URL ends in neither a font nor an image extension.
FONT_CSS = re.compile(r"https?://fonts\.(?:googleapis\.com|bunny\.net)/[^\s\"'()<>]*", re.I)
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__", ".next", "target"}


def walk(root, skip):
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and d not in skip]
        for name in files:
            yield os.path.join(current, name)


def digest(path):
    hasher = hashlib.sha1()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="project root to scan (default: .)")
    parser.add_argument("--assets", nargs="*", default=None,
                        help="asset roots to inventory (default: all scanned directories)")
    parser.add_argument("--skip", nargs="*", default=[], help="directory names to skip")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    roots = [os.path.abspath(root) for root in (args.assets or [args.root])]
    asset_files, text_files = [], []
    for root in roots:
        for path in walk(root, set(args.skip)):
            extension = os.path.splitext(path)[1].lower()
            if extension in ASSET_EXTENSIONS:
                asset_files.append(path)
            elif extension in TEXT_EXTENSIONS:
                text_files.append(path)

    text_blob = {}
    for path in text_files:
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                text_blob[path] = handle.read()
        except OSError:
            continue

    hashes = {}
    for path in asset_files:
        hashes.setdefault(digest(path), []).append(path)
    duplicates = {h: names for h, names in hashes.items() if len(names) > 1}

    unreferenced = []
    for path in asset_files:
        name = os.path.basename(path)
        if not any(name in text for text in text_blob.values()):
            unreferenced.append(path)

    external = set()
    for path, text in text_blob.items():
        for match in EXTERNAL_ASSET.finditer(text):
            external.add(match.group(0))
        for match in FONT_CSS.finditer(text):
            external.add(match.group(0))

    sizes = {}
    for path in asset_files:
        category = CATEGORY_OF.get(os.path.splitext(path)[1].lower(), "other")
        sizes.setdefault(category, {"files": 0, "bytes": 0})
        sizes[category]["files"] += 1
        sizes[category]["bytes"] += os.path.getsize(path)

    result = {
        "assets": len(asset_files),
        "scanned_text_files": len(text_files),
        "sizes": sizes,
        "duplicates": [{"hash": h[:12], "files": names} for h, names in duplicates.items()],
        "unreferenced": sorted(unreferenced),
        "external_urls": sorted(external),
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print("assets    : %d file(s)" % len(asset_files))
    print("text files: %d scanned" % len(text_files))
    total_bytes = sum(v["bytes"] for v in sizes.values())
    for category in sorted(sizes):
        data = sizes[category]
        print("  %-10s %4d file(s) %10.1f KB" % (category, data["files"], data["bytes"] / 1024.0))
    print("  %-10s %4d file(s) %10.1f KB" % ("total", len(asset_files), total_bytes / 1024.0))
    print("")
    print("duplicates: %d group(s)" % len(duplicates))
    for h, names in duplicates.items():
        print("  [%s]" % h[:12])
        for name in names:
            print("    %s" % name)
    print("")
    print("unreferenced by filename: %d (dynamic references may be false positives)" % len(unreferenced))
    for name in sorted(unreferenced):
        print("  %s" % name)
    print("")
    print("external asset URLs: %d (candidates for localize.py)" % len(external))
    for url in sorted(external):
        print("  %s" % url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
