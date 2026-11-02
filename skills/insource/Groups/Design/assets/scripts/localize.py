"""Download externally-hosted assets (icons, fonts, images, media) into the project.

Takes a manifest of URLs - one per line, `URL` or `URL relative/destination.ext` - and stores each
file locally, verifying the bytes match a known asset signature so an HTML error page is never
saved as a "font". Fonts, icon fonts and CDN-served images are the usual targets; the point is to
make the project stop depending on a third-party host at runtime.

Usage:
    python scripts/localize.py --manifest vendor-assets.txt --out assets/vendor
    python scripts/localize.py --url https://example.com/icons/logo.svg --out assets/icons/logo.svg

Manifest example (vendor-assets.txt):
    https://fonts.googleapis.com/css2?family=Inter   css/inter.css
    https://cdn.example.com/icons/arrow.svg          icons/arrow.svg
    https://cdn.example.com/logo.png

Licensing: downloading makes the file local; it does not make it yours. Keep the license text the
source provides, and check the asset's terms before redistributing it.

Requires: Python standard library only.
"""

import argparse
import os
import sys
import urllib.request

# Font CDNs negotiate format by User-Agent: a generic client is served TTF, a browser is served
# WOFF2 (roughly 8x smaller). A browser-like default keeps font localization from silently doubling
# the download size; override with --user-agent when a host expects something else.
DEFAULT_USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

SIGNATURES = [
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"RIFF", "webp/other-riff"),
    (b"wOFF", "woff"),
    (b"wOF2", "woff2"),
    (b"\x00\x01\x00\x00", "ttf"),
    (b"OTTO", "otf"),
    (b"%PDF", "pdf"),
    (b"\x1aE\xdf\xa3", "webm"),
    (b"\x00\x00\x00\x18ftyp", "mp4"),
]

TEXTUAL = ("svg", "css", "js", "json")


def sniff(path):
    with open(path, "rb") as handle:
        head = handle.read(512)
    for magic, kind in SIGNATURES:
        if head.startswith(magic):
            if kind == "webp/other-riff":
                return "webp" if head[8:12] == b"WEBP" else "riff"
            return kind
    stripped = head.lstrip()
    if stripped.startswith(b"<svg") or b"<svg" in stripped[:256]:
        return "svg"
    if stripped.startswith(b"<!DOCTYPE html") or stripped.startswith(b"<html"):
        return "html"
    return "unknown"


EXT_FOR_KIND = {
    "png": ".png", "jpg": ".jpg", "gif": ".gif", "webp": ".webp", "svg": ".svg",
    "woff": ".woff", "woff2": ".woff2", "ttf": ".ttf", "otf": ".otf",
    "pdf": ".pdf", "mp4": ".mp4", "webm": ".webm", "css": ".css", "html": ".html", "text": ".txt",
}


def finalize_extension(target, kind):
    """Give the saved file the extension its bytes actually are.

    URLs like picsum's /800/1400 or Unsplash's photo-<id> carry no extension; a file named
    'photo' with JPEG bytes is an asset nobody can find by name. Returns (path, note)."""
    expected = EXT_FOR_KIND.get(kind)
    if expected is None:
        return target, None
    root, extension = os.path.splitext(target)
    if not extension:
        corrected = root + expected
        os.replace(target, corrected)
        return corrected, "added %s" % expected
    if extension.lower() != expected:
        corrected = root + expected
        os.replace(target, corrected)
        return corrected, "extension corrected %s -> %s" % (extension, expected)
    return target, None


def destination_for(url, out_dir, explicit):
    if explicit:
        return explicit if os.path.isabs(explicit) else os.path.join(out_dir, explicit)
    name = url.split("?")[0].rstrip("/").split("/")[-1] or "download"
    return os.path.join(out_dir, name)


def download(url, target, user_agent):
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
        content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "wb") as handle:
        handle.write(data)
    return len(data), content_type


def sniff_with_type(path, content_type):
    kind = sniff(path)
    if kind in ("html", "unknown"):
        if "text/css" in content_type:
            return "css"
        if "image/svg+xml" in content_type:
            return "svg"
        if content_type.startswith("text/"):
            return "text"
    return kind


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default=None, help="file with 'URL [dest]' lines")
    parser.add_argument("--url", default=None, help="single URL to fetch")
    parser.add_argument("--out", required=True, help="output directory (or exact file with --url)")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT,
                        help="User-Agent for the requests (default: a browser UA, so font CDNs serve WOFF2)")
    args = parser.parse_args(argv)

    if not args.manifest and not args.url:
        parser.error("give --manifest or --url")

    jobs = []
    if args.url:
        jobs.append((args.url.strip(), None))
    if args.manifest:
        with open(args.manifest, encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                jobs.append((parts[0], parts[1] if len(parts) > 1 else None))

    failures = 0
    for url, explicit in jobs:
        target = destination_for(url, args.out, explicit)
        try:
            size, content_type = download(url, target, args.user_agent)
        except Exception as error:  # noqa: BLE001 - report, keep going
            print("FAIL %s -> %s" % (url, error))
            failures += 1
            continue
        kind = sniff_with_type(target, content_type)
        target, note = finalize_extension(target, kind)
        if kind in ("html", "unknown"):
            print("WARN %s saved as %s but looks like %s - check the URL" % (url, target, kind))
        suffix = " [%s]" % note if note else ""
        print("ok   %s -> %s (%s, %d bytes)%s" % (url, target, kind, size, suffix))

    print("done : %d fetched, %d failed" % (len(jobs) - failures, failures))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
