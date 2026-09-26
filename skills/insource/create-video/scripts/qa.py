#!/usr/bin/env python3
"""Measure a finished video against the quality bar.

HyperFrames' own verify proves the composition is valid. This proves it is good
enough to ship: it reads the timeline out of the composition files, the container
and loudness out of the render, and safe-zone compliance out of the pixels, then
reports pass / warn / fail with numbers.

  python3 scripts/qa.py <project-dir> [--video renders/x.mp4] [--spec video-spec.json]
  python3 scripts/qa.py <project-dir> --json

Exit 0 = no failures. Exit 1 = at least one failure. Thresholds and the reasoning
behind each live in references/quality-bar.md.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

MAX_GAP = 0.25          # dead air between scenes, seconds
MIN_DWELL = 0.15        # consecutive arrivals closer than this read as mush
ACTION_BAND_INK = 0.02  # ink allowed in the outer 5% (action-safe violation)
LOUD_TARGET = -14.0     # LUFS integrated, streaming default
LOUD_TOL = 1.0
TRUE_PEAK_MAX = -1.0    # dBTP
DURATION_TOL = 0.02     # against the declared spec duration

TAG = re.compile(r"<[a-zA-Z][^>]*>", re.S)
ATTRS = re.compile(r'([a-zA-Z][a-zA-Z-]*)="([^"]*)"')


def check(name, status, detail):
    return {"name": name, "status": status, "detail": detail}


def parse_hosts(index_html: Path) -> list[dict]:
    """Top-level timed hosts in the root composition, in document order."""
    text = index_html.read_text(errors="replace")
    hosts = []
    for tag in TAG.finditer(text):
        attrs = dict(ATTRS.findall(tag.group(0)))
        start, dur = attrs.get("data-start"), attrs.get("data-duration")
        src = attrs.get("data-composition-src")
        if start is not None and dur is not None and src:
            hosts.append({"src": src, "start": float(start), "duration": float(dur),
                          "kind": attrs.get("data-track-kind", "graphics")})
    return hosts


def parse_clips(scene_html: Path) -> list[dict]:
    """Every timed clip inside a scene file, with its own start and length."""
    text = scene_html.read_text(errors="replace")
    clips = []
    for tag in TAG.finditer(text):
        attrs = dict(ATTRS.findall(tag.group(0)))
        if "clip" not in attrs.get("class", "").split():
            continue
        start, dur = attrs.get("data-start"), attrs.get("data-duration")
        if start is not None and dur is not None:
            clips.append({"start": float(start), "duration": float(dur)})
    return clips


def timeline_checks(project: Path, spec: dict | None) -> tuple[list[dict], dict]:
    out: list[dict] = []
    index = project / "index.html"
    if not index.is_file():
        return [check("timeline", "fail", "no index.html at the project root")], {}

    graphics = [h for h in parse_hosts(index) if h["kind"] == "graphics"]
    if not graphics:
        return [check("timeline", "fail", "index.html declares no timed scene hosts")], {}

    span = max(h["start"] + h["duration"] for h in graphics)
    # A host covering essentially the whole film is a layer (ambient decoration),
    # not a beat in the sequence — it is meant to sit under everything.
    layers = [h for h in graphics if h["duration"] >= span * 0.9 and h["start"] <= 0.001]
    hosts = sorted([h for h in graphics if h not in layers], key=lambda h: h["start"])
    if layers:
        out.append(check("background layer", "pass",
                         f"{len(layers)} full-span layer(s) under {len(hosts)} scene(s)"))
    if not hosts:
        return out + [check("sequence", "warn", "only full-span layers — no scene sequence to read")], {}

    stats = {"scenes": len(hosts), "ends": max(h["start"] + h["duration"] for h in hosts),
             "arrivals": 0, "late_arrivals": 0}

    gaps = [(b["start"] - (a["start"] + a["duration"])) for a, b in zip(hosts, hosts[1:])]
    worst = max(gaps, default=0.0)
    overlaps = [g for g in gaps if g < -0.001]
    if gaps and worst > MAX_GAP:
        out.append(check("dead air", "fail", f"{worst:.2f}s gap between scenes; bar is {MAX_GAP}s"))
    else:
        out.append(check("dead air", "pass", f"largest gap {worst:.2f}s" if gaps else "single scene"))
    if overlaps:
        out.append(check("scene overlap", "fail",
                         f"{len(overlaps)} overlap(s), worst {min(overlaps):.2f}s"))
    else:
        out.append(check("scene overlap", "pass", "scenes run back to back"))

    if hosts[0]["start"] > 0.001:
        out.append(check("opening", "fail", f"first scene starts at {hosts[0]['start']:.2f}s, not 0"))
    else:
        out.append(check("opening", "pass", "starts at t=0"))

    per_scene = []
    for host in hosts:
        scene = project / host["src"]
        if not scene.is_file():
            out.append(check("scene files", "fail", f"{host['src']} is declared but missing"))
            continue
        clips = parse_clips(scene)
        per_scene.append((host, clips))
        stats["arrivals"] += len(clips)
        stats["late_arrivals"] += sum(1 for c in clips if c["start"] > 0.001)

    frozen = [f"{h['src']} ({len(c)} clips)" for h, c in per_scene if len(c) > 1
              and all(abs(x["start"]) < 0.001 for x in c)]
    if frozen:
        out.append(check("arrivals at t=0", "fail",
                         "everything lands at once — a slide, not a shot: " + "; ".join(frozen)))
    elif per_scene:
        out.append(check("arrivals at t=0", "pass",
                         f"{stats['late_arrivals']}/{stats['arrivals']} arrivals land after their "
                         f"scene opens"))

    tight = []
    for host, clips in per_scene:
        starts = sorted(c["start"] for c in clips)
        for a, b in zip(starts, starts[1:]):
            if 0 < b - a < MIN_DWELL:
                tight.append(f"{host['src']}: {b - a:.2f}s")
    if tight:
        out.append(check("arrival dwell", "warn",
                         f"{len(tight)} pair(s) closer than {MIN_DWELL}s — reads as mush: "
                         + "; ".join(tight[:3])))
    else:
        out.append(check("arrival dwell", "pass", f"no two arrivals within {MIN_DWELL}s"))

    if spec:
        want = spec.get("duration_seconds")
        if want and abs(stats["ends"] - want) / want > DURATION_TOL:
            out.append(check("declared duration", "fail",
                             f"timeline runs {stats['ends']:.1f}s, spec says {want:.1f}s"))
        elif want:
            out.append(check("declared duration", "pass", f"{stats['ends']:.1f}s matches spec"))

        implied = sum(max(1, scene.get("beats", 1)) for scene in
                      (spec.get("_plan") or [])) or None
        if implied:
            ratio = stats["arrivals"] / implied
            out.append(check("arrival budget",
                             "pass" if ratio >= 0.9 else "warn",
                             f"{stats['arrivals']} clips against {implied} arrivals the spec budgets "
                             f"({ratio:.0%})"))
    return out, stats


def probe(video: Path) -> dict:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", str(video)], capture_output=True, text=True)
    if res.returncode:
        raise SystemExit(f"ffprobe failed on {video}: {res.stderr.strip()[:200]}")
    return json.loads(res.stdout)


def loudness(video: Path) -> tuple[float | None, float | None]:
    res = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-af",
                          "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True)
    # ebur128 also logs a running I: for every analysed window, and it starts at
    # -70 while the gate is closed — only the Summary block is the real reading.
    _, _, summary = res.stderr.partition("Summary:")
    integrated = re.search(r"I:\s+(-?[\d.]+)\s+LUFS", summary)
    # this ffmpeg labels true peak dBFS, others dBTP — same measurement
    peak = re.search(r"Peak:\s+(-?[\d.]+)\s+dB(?:TP|FS)", summary)
    return (float(integrated.group(1)) if integrated else None,
            float(peak.group(1)) if peak else None)


def media_checks(video: Path, spec: dict | None) -> list[dict]:
    out: list[dict] = []
    info = probe(video)
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not v:
        return [check("container", "fail", "no video stream in the render")]

    duration = float(info.get("format", {}).get("duration") or v.get("duration") or 0)
    rate = v.get("r_frame_rate", "0/1")
    num, _, den = rate.partition("/")
    fps = (float(num) / float(den)) if den else 0.0
    size = f"{v.get('width')}x{v.get('height')}"
    bitrate = int(info.get("format", {}).get("bit_rate", 0)) / 1000

    out.append(check("container", "pass",
                     f"{size} @ {fps:.2f} fps, {duration:.2f}s, {bitrate:.0f} kb/s, "
                     f"{v.get('codec_name')}{'/yuv' + str(v.get('pix_fmt', ''))[3:] if v.get('pix_fmt') else ''}"))

    if spec:
        want = spec.get("duration_seconds")
        if want and abs(duration - want) / want > DURATION_TOL:
            out.append(check("rendered duration", "fail",
                             f"{duration:.2f}s vs {want:.2f}s declared (>2% off)"))
        elif want:
            out.append(check("rendered duration", "pass", f"{duration:.2f}s matches spec"))

        canvas = spec.get("_canvas")
        if canvas and size != f"{canvas[0]}x{canvas[1]}":
            out.append(check("canvas", "fail", f"rendered {size}, spec says {canvas[0]}x{canvas[1]}"))
        elif canvas:
            out.append(check("canvas", "pass", size))

        wants_audio = spec.get("audio", "none") != "none"
        if wants_audio and not a:
            out.append(check("audio", "fail", f"spec says audio={spec.get('audio')} but the render is silent"))
        elif not wants_audio and a:
            out.append(check("audio", "warn", "spec says audio=none but the render carries a track"))
        elif a:
            out.append(check("audio", "pass", f"{a.get('codec_name')} {a.get('sample_rate')} Hz"))

    if a:
        integrated, peak = loudness(video)
        if integrated is None:
            out.append(check("loudness", "warn", "ebur128 produced no reading"))
        else:
            status = "pass" if abs(integrated - LOUD_TARGET) <= LOUD_TOL else "warn"
            out.append(check("loudness", status,
                             f"{integrated:.1f} LUFS (target {LOUD_TARGET}±{LOUD_TOL})"))
        if peak is not None:
            out.append(check("true peak", "pass" if peak <= TRUE_PEAK_MAX else "fail",
                             f"{peak:.1f} dBTP (ceiling {TRUE_PEAK_MAX})"))
    return out


def gray(path: Path, width: int, height: int) -> list[int]:
    res = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf",
                          f"scale={width}:{height}:flags=area,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True)
    if res.returncode or len(res.stdout) < width * height:
        raise SystemExit(f"ffmpeg could not decode {path}")
    return list(res.stdout[: width * height])


def band_ink(pixels: list[int], w: int, h: int, inset: float) -> float:
    """Fraction of the outer ring (outside the inset box) that carries ink."""
    bg = Counter(v >> 4 for v in pixels).most_common(1)[0][0] << 4
    x0, x1 = int(w * inset), int(w * (1 - inset))
    y0, y1 = int(h * inset), int(h * (1 - inset))
    total = ink = 0
    for y in range(h):
        row = y * w
        for x in range(w):
            if x0 <= x < x1 and y0 <= y < y1:
                continue
            total += 1
            if abs(pixels[row + x] - bg) > 24:
                ink += 1
    return ink / max(1, total)


def frame_checks(project: Path) -> list[dict]:
    shots = sorted((project / "snapshots").glob("*.png")) if (project / "snapshots").is_dir() else []
    if not shots:
        return [check("safe zones", "warn",
                      "no snapshots/ to measure — run `npx hyperframes snapshot . --frames 9`")]
    worst = max(band_ink(gray(p, 160, 90), 160, 90, 0.05) for p in shots[:6])
    label = f"{worst:.1%} ink in the outer 5% across {min(len(shots), 6)} frame(s)"
    if worst > ACTION_BAND_INK:
        return [check("safe zones", "fail", f"content crosses action-safe: {label}")]
    return [check("safe zones", "pass", label)]


def main() -> int:
    ap = argparse.ArgumentParser(prog="qa", description=__doc__.splitlines()[0])
    ap.add_argument("project", type=Path)
    ap.add_argument("--video", type=Path, default=None, help="rendered file to measure")
    ap.add_argument("--spec", type=Path, default=None, help="video-spec.json to check against")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    for tool in ("ffprobe", "ffmpeg"):
        if shutil.which(tool) is None:
            raise SystemExit(f"{tool} is required — install ffmpeg")

    project = args.project.expanduser().resolve()
    if not project.is_dir():
        raise SystemExit(f"not a directory: {project}")

    spec = None
    spec_note = None
    if args.spec:
        spec_path = args.spec.expanduser().resolve()
        if not spec_path.is_file():
            raise SystemExit(f"spec not found: {spec_path}")
        spec = json.loads(spec_path.read_text())
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            from spec import ASPECTS, validate
            derived = validate(spec, [], [])
            spec["_canvas"] = ASPECTS.get(spec.get("aspect", ""))
            spec["_plan"] = derived["plan"]
        except Exception as exc:
            spec_note = f"spec could not be read as a create-video spec ({exc}); " \
                        f"canvas, duration and arrival-budget checks are skipped"
            spec = None

    results, _ = timeline_checks(project, spec)
    if spec_note:
        results.insert(0, check("spec", "warn", spec_note))
    elif spec and not spec.get("_canvas"):
        results.insert(0, check("spec", "warn",
                                f"aspect={spec.get('aspect')!r} is not a known canvas; the "
                                f"canvas check is skipped"))
    if args.video:
        video = args.video.expanduser().resolve()
        if not video.is_file():
            raise SystemExit(f"video not found: {video}")
        results += media_checks(video, spec)
    results += frame_checks(project)

    failures = [r for r in results if r["status"] == "fail"]
    warnings = [r for r in results if r["status"] == "warn"]

    if args.json:
        print(json.dumps({"ok": not failures, "failures": len(failures),
                          "warnings": len(warnings), "checks": results}, indent=2))
    else:
        print(f"# quality gate — {project.name}")
        print()
        mark = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}
        for r in results:
            print(f"  [{mark[r['status']]}] {r['name']:<20} {r['detail']}")
        print()
        print(f"{len(results) - len(failures) - len(warnings)}/{len(results)} passed, "
              f"{len(warnings)} warning(s), {len(failures)} failure(s)")
        if failures:
            print("Failures block delivery. Fix the composition, re-run, or record the deliberate "
                  "exception in the delivery note.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
