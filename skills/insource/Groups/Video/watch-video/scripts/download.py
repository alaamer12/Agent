#!/usr/bin/env python3
"""Download a video via yt-dlp, or resolve a local file path.

Also fetches subtitles (manual first, then auto-generated) in VTT format so
transcribe.py can parse them without needing Whisper.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".mov", ".m4v", ".avi", ".flv", ".wmv"}


def is_url(source: str) -> bool:
    parsed = urlparse(source)
    return parsed.scheme in ("http", "https")


def resolve_local(path: str) -> dict:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise SystemExit(f"File not found: {p}")
    if p.suffix.lower() not in VIDEO_EXTS:
        print(
            f"[watch] warning: {p.suffix} is not a known video extension, proceeding anyway",
            file=sys.stderr,
        )
    return {
        "video_path": str(p),
        "subtitle_path": None,
        "info": {"title": p.name, "url": str(p)},
        "downloaded": False,
    }


def _pick_subtitle(out_dir: Path) -> Path | None:
    candidates = sorted(out_dir.glob("video*.vtt"))
    if not candidates:
        return None
    preferred = [c for c in candidates if ".en" in c.name]
    return preferred[0] if preferred else candidates[0]


def _pick_video(out_dir: Path) -> Path | None:
    for ext in (".mp4", ".mkv", ".webm", ".mov"):
        for candidate in out_dir.glob(f"video*{ext}"):
            return candidate
    for candidate in out_dir.glob("video.*"):
        if candidate.suffix.lower() in VIDEO_EXTS:
            return candidate
    return None


def _js_runtime_args() -> list[str]:
    """Pass a JS runtime to yt-dlp when it supports the flag and one is installed.

    YouTube deprecated extraction without a JS runtime, so without this every
    format may be missing.
    """
    try:
        help_text = subprocess.run(
            ["yt-dlp", "--help"], capture_output=True, text=True, timeout=20
        ).stdout
    except Exception:
        return []
    if "--js-runtimes" not in help_text:
        return []
    for runtime in ("deno", "node"):
        if shutil.which(runtime):
            return ["--js-runtimes", runtime]
    return []


def _read_info(out_dir: Path, url: str) -> dict:
    info_path = out_dir / "video.info.json"
    if not info_path.exists():
        return {"url": url}
    try:
        raw = json.loads(info_path.read_text())
    except Exception:
        return {"url": url}
    return {
        "title": raw.get("title"),
        "uploader": raw.get("uploader") or raw.get("channel"),
        "duration": raw.get("duration"),
        "url": raw.get("webpage_url") or url,
    }


def download_url(
    url: str,
    out_dir: Path,
    *,
    yt_extra: list[str] | None = None,
    skip_video: bool = False,
) -> dict:
    if shutil.which("yt-dlp") is None:
        raise SystemExit("yt-dlp is not installed. Install with: brew install yt-dlp")

    out_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(out_dir / "video.%(ext)s")

    cmd = [
        "yt-dlp",
        "-N", "8",
        "-f", "bv*[height<=720]+ba/b[height<=720]/bv+ba/b",
        "--merge-output-format", "mp4",
        "--write-info-json",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", "en,en-US,en-GB,en-orig",
        "--sub-format", "vtt",
        "--convert-subs", "vtt",
        "--no-playlist",
        "--ignore-errors",
    ]
    cmd += _js_runtime_args()
    cmd += list(yt_extra or [])
    if skip_video:
        cmd.append("--skip-download")
    cmd += ["-o", output_template, url]

    # yt-dlp may exit non-zero if a subtitle variant fails (e.g. 429) even when
    # the video itself downloaded fine. Treat "video file present" as success.
    result = subprocess.run(cmd, stdout=sys.stderr, stderr=sys.stderr)
    subtitle = _pick_subtitle(out_dir)

    if skip_video:
        return {
            "video_path": None,
            "subtitle_path": str(subtitle) if subtitle else None,
            "info": _read_info(out_dir, url),
            "downloaded": True,
        }

    video = _pick_video(out_dir)
    if video is None:
        message = f"yt-dlp did not produce a video file in {out_dir} (exit {result.returncode})"
        if subtitle:
            message += " — captions were fetched, so `--transcript-only` may still work"
        raise SystemExit(message)

    return {
        "video_path": str(video),
        "subtitle_path": str(subtitle) if subtitle else None,
        "info": _read_info(out_dir, url),
        "downloaded": True,
    }


def download(source: str, out_dir: Path, **kwargs) -> dict:
    if is_url(source):
        return download_url(source, out_dir, **kwargs)
    if kwargs.get("skip_video"):
        raise SystemExit("--transcript-only needs a URL with captions; a local file has none")
    return resolve_local(source)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: download.py <url-or-path> <out-dir>", file=sys.stderr)
        raise SystemExit(2)
    result = download(sys.argv[1], Path(sys.argv[2]))
    print(json.dumps(result, indent=2))
