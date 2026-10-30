#!/usr/bin/env python3
"""/watch entry point: download video, extract frames, parse transcript.

Prints a markdown report to stdout listing frame paths + transcript. Claude
then Reads each frame path to see the video.
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from download import download, is_url  # noqa: E402
from frames import MAX_FPS, auto_fps, auto_fps_focus, extract, format_time, get_metadata, parse_time  # noqa: E402
from transcribe import filter_range, format_transcript, parse_vtt  # noqa: E402
from whisper import load_api_key, transcribe_video  # noqa: E402


def report_transcript_only(
    args: argparse.Namespace,
    dl: dict,
    inbox: Path,
    outbox: Path,
    start_sec: float | None,
    end_sec: float | None,
) -> int:
    """Caption-only report: no frames, no video download, no Whisper."""
    info = dl.get("info") or {}
    focused = start_sec is not None or end_sec is not None

    print()
    print("# watch: transcript report")
    print()
    print(f"- **Source:** {args.source}")
    if info.get("title"):
        print(f"- **Title:** {info['title']}")
    if info.get("uploader"):
        print(f"- **Uploader:** {info['uploader']}")
    if info.get("duration"):
        print(f"- **Duration:** {format_time(info['duration'])} ({info['duration']:.1f}s)")
    print("- **Frames:** skipped (`--transcript-only`)")

    subtitle_path = dl.get("subtitle_path")
    if not subtitle_path:
        print("- **Transcript:** none available")
        print()
        print(
            "_No captions in `en,en-US,en-GB,en-orig` for this source. Whisper reads the audio "
            "track, which `--transcript-only` never downloads — re-run without the flag to "
            "transcribe it (needs a key in `~/.config/watch/.env`; see `setup.py`). "
            "If yt-dlp failed to reach the video at all, this run is blocked upstream — "
            "see the stderr above._"
        )
        print()
        print("---")
        print(f"_Input dir: `{inbox}` (captions only — the video was never downloaded)._")
        print(f"_Output dir: `{outbox}` — write the notes file here, then delete "
              f"`{inbox.parent}` when done._")
        return 0

    segments = parse_vtt(subtitle_path)
    if focused:
        segments = filter_range(segments, start_sec, end_sec)
    print(f"- **Transcript:** {len(segments)} segments (via captions)")

    print()
    print("## Transcript")
    print()
    text = format_transcript(segments)
    if text:
        if focused:
            print(f"_Source: captions. Filtered to {format_time(start_sec or 0)} → {format_time(end_sec or 0)}:_")
            print()
        print("```")
        print(text)
        print("```")
    else:
        print("_No transcript lines fell inside the requested range._")

    print()
    print("---")
    print(f"_Input dir: `{inbox}` (captions only — the video was never downloaded)._")
    print(f"_Output dir: `{outbox}` — write the notes file here, then delete "
          f"`{inbox.parent}` when done._")
    return 0


def slugify(source: str) -> str:
    """A filesystem-safe name for the work dir, derived from the source."""
    tail = re.split(r"[/?#]", source.strip())[-1] or "video"
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", tail).strip("-.")
    return cleaned[:48] or "video"


def work_root(args: argparse.Namespace) -> Path:
    """Where the run lives: the OS temp dir unless the user asked for a real path.

    Never the project directory by default — frames and a downloaded video are
    scratch, and scratch must not show up in `git status`.
    """
    if args.out_dir:
        return Path(args.out_dir).expanduser().resolve()
    named = Path(tempfile.gettempdir()) / "watch-video" / slugify(args.slug or args.source)
    if not named.exists():
        return named
    for n in range(2, 100):                      # never mix two runs in one directory
        candidate = named.parent / f"{named.name}-{n}"
        if not candidate.exists():
            return candidate
    return Path(tempfile.mkdtemp(prefix="watch-"))


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="watch",
        description="Download a video, extract auto-scaled frames, and surface the transcript.",
    )
    ap.add_argument("source", help="Video URL or local file path")
    ap.add_argument("--max-frames", type=int, default=80, help="Cap on frame count (default 80, hard max 100)")
    ap.add_argument("--resolution", type=int, default=512, help="Frame width in pixels (default 512)")
    ap.add_argument("--fps", type=float, default=None, help="Override auto-fps")
    ap.add_argument("--start", type=str, default=None, help="Range start (SS, MM:SS, or HH:MM:SS)")
    ap.add_argument("--end", type=str, default=None, help="Range end (SS, MM:SS, or HH:MM:SS)")
    ap.add_argument("--out-dir", type=str, default=None,
                    help="Work somewhere specific instead of the OS temp dir")
    ap.add_argument("--slug", type=str, default=None,
                    help="Name the temp work directory (defaults to a name derived from the source)")
    ap.add_argument(
        "--no-whisper",
        action="store_true",
        help="Disable Whisper fallback. Report frames-only if no captions available.",
    )
    ap.add_argument(
        "--whisper",
        choices=["groq", "openai"],
        default=None,
        help="Force a specific Whisper backend. Default: prefer Groq, fall back to OpenAI.",
    )
    ap.add_argument(
        "--transcript-only",
        action="store_true",
        help="Skip the video download and frame extraction; fetch captions only.",
    )
    ap.add_argument(
        "--cookies",
        type=str,
        default=None,
        help="Netscape cookies.txt for yt-dlp — the fix for 'Sign in to confirm you're not a bot'.",
    )
    ap.add_argument(
        "--cookies-from-browser",
        type=str,
        default=None,
        help="Browser to pull cookies from (e.g. chrome, firefox, chrome:Profile 1).",
    )
    args = ap.parse_args()

    yt_extra: list[str] = []
    if args.cookies:
        cookie_path = Path(args.cookies).expanduser()
        if not cookie_path.is_file():
            raise SystemExit(f"--cookies file not found: {cookie_path}")
        yt_extra += ["--cookies", str(cookie_path.resolve())]
    if args.cookies_from_browser:
        yt_extra += ["--cookies-from-browser", args.cookies_from_browser]

    max_frames = min(args.max_frames, 100)

    work = work_root(args)
    inbox, outbox = work / "input", work / "output"
    inbox.mkdir(parents=True, exist_ok=True)
    outbox.mkdir(parents=True, exist_ok=True)
    print(f"[watch] input dir:  {inbox}", file=sys.stderr)
    print(f"[watch] output dir: {outbox}", file=sys.stderr)

    print(
        "[watch] downloading via yt-dlp…" if is_url(args.source) else "[watch] using local file…",
        file=sys.stderr,
    )
    dl = download(
        args.source,
        inbox / "download",
        yt_extra=yt_extra,
        skip_video=args.transcript_only,
    )

    start_sec = parse_time(args.start)
    end_sec = parse_time(args.end)

    if args.transcript_only:
        return report_transcript_only(args, dl, inbox, outbox, start_sec, end_sec)

    video_path = dl["video_path"]

    meta = get_metadata(video_path)
    full_duration = meta["duration_seconds"]

    if start_sec is not None and start_sec < 0:
        raise SystemExit("--start must be non-negative")
    if end_sec is not None and start_sec is not None and end_sec <= start_sec:
        raise SystemExit("--end must be greater than --start")
    if full_duration > 0 and start_sec is not None and start_sec >= full_duration:
        raise SystemExit(f"--start {start_sec:.1f}s is past end of video ({full_duration:.1f}s)")

    effective_start = start_sec if start_sec is not None else 0.0
    effective_end = end_sec if end_sec is not None else full_duration
    effective_duration = max(0.0, effective_end - effective_start)
    focused = start_sec is not None or end_sec is not None

    if focused:
        fps, target = auto_fps_focus(effective_duration, max_frames=max_frames)
    else:
        fps, target = auto_fps(effective_duration, max_frames=max_frames)
    if args.fps is not None:
        fps = min(args.fps, MAX_FPS)
        target = max(1, int(round(fps * effective_duration)))

    scope = (
        f"{format_time(effective_start)}-{format_time(effective_end)} ({effective_duration:.1f}s)"
        if focused else f"full {effective_duration:.1f}s"
    )
    print(f"[watch] extracting ~{target} frames at {fps:.3f} fps over {scope}…", file=sys.stderr)

    frames = extract(
        video_path,
        inbox / "frames",
        fps=fps,
        resolution=args.resolution,
        max_frames=max_frames,
        start_seconds=start_sec,
        end_seconds=end_sec,
    )

    transcript_segments: list[dict] = []
    transcript_text: str | None = None
    transcript_source: str | None = None
    if dl.get("subtitle_path"):
        try:
            all_segments = parse_vtt(dl["subtitle_path"])
            transcript_segments = filter_range(all_segments, start_sec, end_sec) if focused else all_segments
            transcript_text = format_transcript(transcript_segments)
            transcript_source = "captions"
        except Exception as exc:
            print(f"[watch] subtitle parse failed: {exc}", file=sys.stderr)

    if not transcript_segments and not args.no_whisper:
        backend, api_key = load_api_key(args.whisper)
        if backend and api_key:
            try:
                all_segments, used_backend = transcribe_video(
                    video_path,
                    inbox / "audio.mp3",
                    backend=backend,
                    api_key=api_key,
                )
                transcript_segments = filter_range(all_segments, start_sec, end_sec) if focused else all_segments
                transcript_text = format_transcript(transcript_segments)
                transcript_source = f"whisper ({used_backend})"
            except SystemExit as exc:
                print(f"[watch] whisper fallback failed: {exc}", file=sys.stderr)
        else:
            hint = (
                f"--whisper {args.whisper} was set but the matching API key is missing"
                if args.whisper else
                "no subtitles and no Whisper API key found"
            )
            setup_py = SCRIPT_DIR / "setup.py"
            print(
                f"[watch] {hint} — run `python3 {setup_py}` to enable the Whisper fallback",
                file=sys.stderr,
            )

    info = dl.get("info") or {}

    print()
    print("# watch: video report")
    print()
    print(f"- **Source:** {args.source}")
    if info.get("title"):
        print(f"- **Title:** {info['title']}")
    if info.get("uploader"):
        print(f"- **Uploader:** {info['uploader']}")
    print(f"- **Duration:** {format_time(full_duration)} ({full_duration:.1f}s)")
    if focused:
        print(
            f"- **Focus range:** {format_time(effective_start)} → {format_time(effective_end)} "
            f"({effective_duration:.1f}s)"
        )
    if meta.get("width") and meta.get("height"):
        print(f"- **Resolution:** {meta['width']}x{meta['height']} ({meta.get('codec') or 'unknown codec'})")
    mode = "focused" if focused else "full"
    print(f"- **Frames:** {len(frames)} @ {fps:.3f} fps, {mode} mode (budget {target}, max {max_frames})")
    print(f"- **Frame size:** {args.resolution}px wide")
    if transcript_segments:
        in_range = " in range" if focused else ""
        print(
            f"- **Transcript:** {len(transcript_segments)} segments{in_range} "
            f"(via {transcript_source or 'captions'})"
        )
    else:
        print("- **Transcript:** none available")

    if not focused and full_duration > 600:
        mins = int(full_duration // 60)
        print()
        print(
            f"> **Warning:** This is a {mins}-minute video. Frame coverage is sparse at this length — "
            "accuracy degrades noticeably on anything over 10 minutes. For better results, "
            "re-run with `--start HH:MM:SS --end HH:MM:SS` to zoom into a specific section."
        )

    print()
    print("## Frames")
    print()
    print(f"Frames live at: `{inbox / 'frames'}`")
    print()
    print(
        "**Read each frame path below with the Read tool to view the image.** "
        "Frames are in chronological order; `t=MM:SS` is the absolute timestamp in the source video."
    )
    print()
    for frame in frames:
        print(f"- `{frame['path']}` (t={format_time(frame['timestamp_seconds'])})")

    print()
    print("## Transcript")
    print()
    if transcript_text:
        label = transcript_source or "captions"
        if focused:
            print(f"_Source: {label}. Filtered to {format_time(effective_start)} → {format_time(effective_end)}:_")
        else:
            print(f"_Source: {label}._")
        print()
        print("```")
        print(transcript_text)
        print("```")
    elif focused and dl.get("subtitle_path"):
        print(f"_No transcript lines fell inside {format_time(effective_start)} → {format_time(effective_end)}._")
    else:
        setup_py = SCRIPT_DIR / "setup.py"
        print(
            "_No transcript available — proceed with frames only. "
            "Captions were missing and the Whisper fallback was unavailable "
            "(no API key set, or `--no-whisper` was used). "
            f"Run `python3 {setup_py}` to enable Whisper, then re-run._"
        )

    print()
    print("---")
    print(f"_Input dir: `{inbox}` — the downloaded video plus `{inbox / 'frames'}`._")
    print(f"_Output dir: `{outbox}` — write the notes file and any `motion.py` reports here._")
    print(f"_Delete `{work}` when done, once the notes file is safely outside it._")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
