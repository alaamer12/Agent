#!/usr/bin/env python3
"""Turn a locked video spec into a numeric build sheet.

The six creative axes — genre, pacing, visual style, camera style, editing style,
tone — are adjectives. A composition needs numbers. This validates a spec against
the taxonomy and derives the canvas, the shot budget, per-scene timecodes, the
transition durations, the hyperframes-animation rules and blueprints each choice
implies, and the motion checks the finished render has to pass.

  python3 scripts/spec.py --example > video-spec.json   # start from the template
  python3 scripts/spec.py video-spec.json               # human-readable build sheet
  python3 scripts/spec.py video-spec.json --json        # machine-readable

Exit 0 = spec is buildable (warnings allowed). Exit 1 = errors; fix the spec first.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ASPECTS = {
    "16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080),
    "4:5": (1080, 1350), "4:3": (1440, 1080), "3:2": (1620, 1080),
    "16:10": (1728, 1080), "21:9": (2560, 1080),
}

FPS = {24, 25, 30, 50, 60, 120, 240}

AUDIO = {"none", "music", "voiceover", "music+voiceover", "music+sfx", "voiceover+sfx",
         "music+voiceover+sfx"}

GENRES = {
    "educational", "documentary", "tutorial", "vlog", "interview", "news", "commentary",
    "review", "storytelling", "comedy", "drama", "action", "horror", "thriller", "romance",
    "advertisement", "product_showcase", "cinematic", "music_video", "short_film",
    "animation", "explainer", "motivational", "gaming", "reaction", "travel", "cooking",
    "fitness", "podcast", "announcement",
}

# cuts/min band, shot length band (s), transition band (ms), what the viewer feels
PACING = {
    "very_slow": ((2, 6), (10.0, 30.0), (900, 1600), "meditative; each shot is sat in"),
    "slow": ((6, 12), (5.0, 10.0), (600, 1000), "calm; gradual reveals, long holds"),
    "moderate": ((12, 24), (2.5, 5.0), (350, 600), "conversational; one idea per shot"),
    "fast": ((24, 45), (1.3, 2.5), (150, 350), "energetic; little is held, arrivals are sharp"),
    "very_fast": ((45, 90), (0.5, 1.3), (60, 150), "relentless; information density is the point"),
}

EDITING = {
    "long_takes": ("few cuts, motion inside the frame carries it", "dissolve or none"),
    "standard_cuts": ("clean cuts on idea boundaries", "short dissolve or hard cut"),
    "jump_cuts": ("same framing, content jumps forward", "hard cut"),
    "montage": ("compressed sequence of fragments", "hard cut, occasional wipe"),
    "rapid_cuts": ("cuts on beats, sub-second shots", "hard cut only — dissolves read as mush"),
    "mixed": ("varies by beat", "per scene"),
}

VISUAL_STYLES = {
    "cinematic": "wide gamut contrast, letterbox, shallow focus, motivated light",
    "realistic": "natural colour, no stylised grade, documentary framing",
    "minimal": "one subject, generous negative space, flat or single-hue field",
    "animated": "illustrated or motion-graphic surfaces, exaggerated easing",
    "handheld": "imperfect framing, breathing frame, live texture",
    "stylized": "deliberate art direction that is not any of the above",
    "flat": "2D graphic shapes, no simulated depth",
    "editorial": "type-led, grid-driven, print-magazine rhythm",
}

CAMERA_STYLES = {
    "static": {"rules": [], "note": "no camera rule; motion must come from inside the frame"},
    "handheld": {"rules": ["sine-wave-loop"], "note": "idle drift on the world wrapper"},
    "tracking": {"rules": ["camera-cursor-tracking", "nudge-curve"], "note": "viewport follows a focal point"},
    "drone": {"rules": ["3d-camera-flight", "viewport-change"], "note": "flight through depth"},
    "closeup": {"rules": ["coordinate-target-zoom", "depth-of-field-blur"], "note": "push in and rack focus"},
    "wide": {"rules": ["multi-phase-camera", "viewport-change"], "note": "establish, then pull back to reveal"},
    "mixed": {"rules": ["multi-phase-camera", "coordinate-target-zoom"], "note": "one camera language per beat"},
}

TONES = {
    "calm": "sine.inOut / power1 — slow in, slow out, long holds",
    "energetic": "back.out / power4 — overshoot, snap, short holds",
    "serious": "power2 — no overshoot, no bounce, deliberate",
    "funny": "elastic.out / back.out — overshoot and settle, timing is the joke",
    "emotional": "sine.inOut over long durations — slow reveals, soft landings",
    "mysterious": "power1.in — things arrive late, holds outlast comfort",
    "inspirational": "power3.out — fast start, long glide into the rest",
}

# canonical role -> (accepted spellings, blueprint ids from hyperframes-animation)
ROLES = {
    "hook": (["hook", "open", "opening", "cold_open"], ["kinetic-type-beats", "ticker-takeover", "typewriter-reveal", "cta-morph-press"]),
    "pain_point": (["pain_point", "problem", "pain"], ["kinetic-type-beats", "spatial-pan-stations", "overwhelm-surround", "dataviz-countup"]),
    "product_intro": (["product_intro", "intro"], ["kinetic-type-beats", "logo-assemble-lockup", "titlecard-reveal", "video-text-pivot"]),
    "feature_showcase": (["feature_showcase", "feature"], ["grid-card-assemble", "cursor-ui-demo", "device-surface-showcase", "panel-edit-live-sync"]),
    "benefit_highlight": (["benefit_highlight", "benefit", "benefits"], ["kinetic-type-beats", "grid-card-assemble", "camera-journey", "zoom-out-workspace-reveal"]),
    "social_proof": (["social_proof", "proof"], ["constellation-hub", "grid-card-assemble", "titlecard-reveal", "dataviz-countup"]),
    "demo": (["demo", "walkthrough", "howto"], ["prompt-type-submit-generate", "cursor-ui-demo", "device-surface-showcase", "transcript-scroll-artifact-reveal"]),
    "cta": (["cta", "call_to_action"], ["cta-morph-press", "kinetic-type-beats", "logo-assemble-lockup", "constellation-hub"]),
    "branding": (["branding", "outro", "brand_outro", "close", "sign_off"], ["titlecard-reveal", "logo-assemble-lockup", "kinetic-type-beats", "fixed-anchor-cycle"]),
    "segment": (["segment", "body", "establishing", "explainer", "step", "scene", "title", "credit", "transition", "payoff"], []),
}

DIRECTIONS = {"top", "top-right", "right", "bottom-right", "bottom", "bottom-left", "left",
              "top-left", "in-place"}

EXAMPLE = {
    "title": "Untitled",
    "purpose": "One sentence: what must the viewer know, feel, or do after watching.",
    "audience": "who this is for",
    "aspect": "16:9",
    "duration_seconds": 30,
    "fps": 30,
    "audio": "music",
    "language": "en",
    "dimensions": {
        "genre": "explainer",
        "pacing": "moderate",
        "visual_style": "minimal",
        "camera_style": "static",
        "editing_style": "standard_cuts",
        "tone": "calm",
    },
    "structure": [
        {"role": "hook", "intent": "name the frustration in the viewer's own words",
         "seconds": 4, "content": "[slot]", "motion": {"expect": "in-place",
         "what": "the line swaps words in place; nothing travels"}},
        {"role": "pain_point", "intent": "make the cost of the status quo visible",
         "seconds": 5, "content": "[slot]"},
        {"role": "product_intro", "intent": "reveal the thing, named once",
         "seconds": 6, "content": "[slot]"},
        {"role": "feature_showcase", "intent": "one capability, shown working not claimed",
         "seconds": 9, "content": "[slot]",
         "motion": {"expect": "right", "what": "the panel slides in from the left edge"}},
        {"role": "cta", "intent": "one action, one button", "seconds": 6, "content": "[slot]",
         "motion": {"expect": "top", "what": "the button rises from below into rest"}},
    ],
    "assets": {"logo": "[path]", "footage": [], "fonts": [], "music": "[path]"},
    "constraints": {"brand_colours": [], "must_include": [], "must_avoid": [], "deadline": None},
}


def tc(seconds: float) -> str:
    m, s = divmod(max(0.0, seconds), 60)
    return f"{int(m):02d}:{s:04.1f}"


def norm_role(raw: str) -> tuple[str, list[str]] | None:
    key = raw.strip().lower().replace(" ", "_").replace("-", "_")
    for canon, (spellings, blueprints) in ROLES.items():
        if key in spellings:
            return canon, blueprints
    return None


def validate(spec: dict, errors: list, warnings: list) -> dict:
    """Check every field, and return the derived build plan."""
    for field in ("title", "purpose", "aspect", "duration_seconds", "fps", "audio",
                  "dimensions", "structure"):
        if field not in spec:
            errors.append(f"missing required field: {field}")

    dims = spec.get("dimensions") or {}
    for axis, table in (("genre", GENRES), ("pacing", PACING), ("visual_style", VISUAL_STYLES),
                        ("camera_style", CAMERA_STYLES), ("editing_style", EDITING), ("tone", TONES)):
        value = dims.get(axis)
        if value is None:
            errors.append(f"dimensions.{axis} is unset — every axis must be pinned, not implied")
        elif value not in table:
            errors.append(f"dimensions.{axis}={value!r} is not a known value; "
                          f"choose from: {', '.join(sorted(table))}")

    aspect = spec.get("aspect", "16:9")
    canvas = ASPECTS.get(aspect)
    if canvas is None:
        errors.append(f"aspect={aspect!r} unknown; choose from: {', '.join(ASPECTS)}")
        canvas = ASPECTS["16:9"]

    duration = spec.get("duration_seconds", 0)
    if not isinstance(duration, (int, float)) or duration <= 0:
        errors.append("duration_seconds must be a positive number")
        duration = 0.0

    fps = spec.get("fps", 30)
    if fps not in FPS:
        warnings.append(f"fps={fps} is outside the usual set ({', '.join(str(f) for f in sorted(FPS))})")

    audio = spec.get("audio", "none")
    if audio not in AUDIO:
        errors.append(f"audio={audio!r} unknown; choose from: {', '.join(sorted(AUDIO))}")

    pacing_key = dims.get("pacing") if dims.get("pacing") in PACING else "moderate"
    pacing = PACING[pacing_key]
    camera = CAMERA_STYLES.get(dims.get("camera_style"), CAMERA_STYLES["static"])
    editing = EDITING.get(dims.get("editing_style"), EDITING["standard_cuts"])

    scenes = spec.get("structure") or []
    if not scenes:
        errors.append("structure is empty — the spec needs at least one scene")

    total = 0.0
    plan = []
    for index, scene in enumerate(scenes, start=1):
        seconds = scene.get("seconds", 0)
        if not isinstance(seconds, (int, float)) or seconds <= 0:
            errors.append(f"scene {index}: seconds must be a positive number")
            seconds = 0.0
        start, total = total, total + seconds

        resolved = norm_role(scene.get("role", "segment"))
        if resolved is None:
            errors.append(f"scene {index}: role={scene.get('role')!r} is not a known role; "
                          f"choose from: {', '.join(sorted({s for _, (sp, _) in ROLES.items() for s in sp}))}")
            canon, blueprints = "segment", []
        else:
            canon, blueprints = resolved

        if not scene.get("intent"):
            errors.append(f"scene {index} ({canon}): no intent — say what this beat must do to the viewer")
        if not scene.get("content"):
            warnings.append(f"scene {index} ({canon}): content is empty — the build will stall on it")

        lo, hi = pacing[1]
        median_shot = (lo + hi) / 2
        beats = max(1, int(round(seconds / median_shot))) if seconds else 0
        if seconds > hi * 3:
            warnings.append(f"scene {index} ({canon}) runs {seconds:.1f}s — {beats} arrivals' worth at "
                            f"{pacing_key} pacing. Keep content landing on that rhythm; one "
                            f"static block filling that window reads as frozen.")

        motion = scene.get("motion")
        promise = None
        if isinstance(motion, dict):
            expect = motion.get("expect")
            if expect not in DIRECTIONS:
                errors.append(f"scene {index}: motion.expect={expect!r} must be one of "
                              f"{', '.join(sorted(DIRECTIONS))} — the direction the subject TRAVELS, "
                              f"not where it comes from")
            else:
                promise = {"expect": expect, "what": motion.get("what", "")}
        elif isinstance(motion, str) and motion.strip():
            warnings.append(f"scene {index}: motion is free text ({motion.strip()[:40]}…) — give "
                            f"{{'expect': <direction>, 'what': <sentence>}} so the render can be checked")

        plan.append({"index": index, "role": canon, "intent": scene.get("intent", ""),
                     "content": scene.get("content", ""), "start": start, "end": total,
                     "seconds": seconds, "beats": beats, "blueprints": blueprints,
                     "promise": promise})

    if duration and scenes:
        drift = abs(total - duration) / duration
        if drift > 0.05:
            errors.append(f"structure totals {total:.1f}s but duration_seconds is {duration:.1f}s "
                          f"({drift:.0%} off). Fix one of them; do not let the build guess.")

    cuts_lo, cuts_hi = pacing[0]
    expected = (duration / 60.0) * ((cuts_lo + cuts_hi) / 2.0)
    planned_beats = sum(s["beats"] for s in plan)
    if duration and expected >= 2:
        if planned_beats < expected * 0.6:
            warnings.append(f"{pacing_key} pacing over {duration:.0f}s implies ~{expected:.0f} "
                            f"arrivals; the plan lands {planned_beats}. Add beats inside the scenes, "
                            f"or slow the pacing — otherwise it will read as stalled.")
        elif planned_beats > expected * 1.6:
            warnings.append(f"the plan lands ~{planned_beats} arrivals against the ~{expected:.0f} "
                            f"{pacing_key} pacing implies. That is a busier cut than the brief "
                            f"says; confirm it is wanted before building.")

    return {"canvas": canvas, "duration": duration, "fps": fps, "total": total,
            "pacing": pacing, "camera": camera, "editing": editing, "plan": plan,
            "aspect": aspect, "dims": dims}


def render_markdown(spec: dict, derived: dict, errors: list, warnings: list) -> str:
    dims, (lo, hi), (shot_lo, shot_hi), (tr_lo, tr_hi), feel = (
        derived["dims"], derived["pacing"][0], derived["pacing"][1], derived["pacing"][2],
        derived["pacing"][3])
    w, h = derived["canvas"]
    out = [f"# Build sheet — {spec.get('title', 'Untitled')}", ""]
    out.append(f"**Purpose:** {spec.get('purpose', '—')}")
    out.append(f"**Audience:** {spec.get('audience', '—')}")
    out.append(f"**Language:** {spec.get('language', 'en')}  ·  **Audio:** {spec.get('audio', 'none')}")
    out.append("")
    out.append("## The six axes")
    out.append("")
    out.append("| Axis | Value | What it forces |")
    out.append("|---|---|---|")
    out.append(f"| Genre | {dims.get('genre', '—')} | what the viewer expects the video to be |")
    out.append(f"| Pacing | {dims.get('pacing', '—')} | {lo}–{hi} cuts/min · shots {shot_lo:.1f}–{shot_hi:.1f}s · {feel} |")
    out.append(f"| Visual style | {dims.get('visual_style', '—')} | {VISUAL_STYLES.get(dims.get('visual_style'), '—')} |")
    out.append(f"| Camera style | {dims.get('camera_style', '—')} | {derived['camera']['note']} |")
    out.append(f"| Editing style | {dims.get('editing_style', '—')} | {derived['editing'][0]}; {derived['editing'][1]} |")
    out.append(f"| Tone | {dims.get('tone', '—')} | {TONES.get(dims.get('tone'), '—')} |")
    out.append("")
    out.append("## Frame budget")
    out.append("")
    out.append(f"- Canvas **{w}x{h}** ({derived['aspect']}) at **{derived['fps']} fps** "
               f"= **{int(derived['duration'] * derived['fps'])} frames**")
    out.append(f"- Planned runtime {derived['total']:.1f}s across {len(derived['plan'])} scenes")
    out.append(f"- Transitions **{tr_lo}–{tr_hi} ms** ({tr_lo / derived['fps']:.0f}–"
               f"{tr_hi / derived['fps']:.0f} frames) — {derived['editing'][1]}")
    expected_beats = derived["duration"] / 60 * (lo + hi) / 2
    planned = sum(s["beats"] for s in derived["plan"])
    out.append(f"- Arrivals: pacing implies ~{expected_beats:.0f}; the plan lands **{planned}**")
    out.append("")
    out.append("## Scenes")
    out.append("")
    out.append("| # | Role | Window | Len | Beats | Intent | Suggested blueprint | Motion promise |")
    out.append("|---|---|---|---|---|---|---|---|")
    for scene in derived["plan"]:
        blueprint = ", ".join(scene["blueprints"][:2]) or "compose from rules"
        promise = f"{scene['promise']['expect']} — {scene['promise']['what']}" if scene["promise"] else "—"
        out.append(f"| {scene['index']} | {scene['role']} | {tc(scene['start'])}–{tc(scene['end'])} | "
                   f"{scene['seconds']:.1f}s | {scene['beats']} | {scene['intent']} | {blueprint} | "
                   f"{promise} |")
    out.append("")
    out.append("## Motion to read from hyperframes-animation")
    out.append("")
    rules = [r for r in derived["camera"]["rules"]]
    if dims.get("pacing") in ("fast", "very_fast"):
        rules += ["spring-pop-entrance", "waterfall-entry", "nudge-curve"]
    if dims.get("pacing") in ("very_slow", "slow"):
        rules += ["sine-wave-loop", "ambient-glow-bloom"]
    if dims.get("tone") in ("energetic", "funny"):
        rules += ["kinetic-beat-slam", "particle-burst"]
    if dims.get("tone") in ("mysterious", "emotional"):
        rules += ["depth-of-field-blur", "gradient-text-sweep"]
    rules = [r for r in dict.fromkeys(rules) if r not in derived["camera"]["rules"]]
    out.append("- Camera: " + (", ".join(derived["camera"]["rules"]) or "none — frame stays locked"))
    out.append("- Arrival and emphasis: " + (", ".join(rules) or "pick from rules-index.md by tag"))
    out.append("- Transitions: `transitions/catalog.md` — "
               f"{derived['editing'][1]}, at {tr_lo}–{tr_hi} ms")
    out.append("- Easing: " + TONES.get(dims.get("tone"), "—"))
    out.append("")

    checks = [s for s in derived["plan"] if s["promise"]]
    if checks:
        entrance = (tr_lo + tr_hi) / 2 / 1000

        def window(scene):
            """Two times where the subject is opaque in both, so the pair measures
            travel rather than a fade from nothing."""
            if scene["promise"]["expect"] == "in-place":
                a = round(scene["start"] + entrance * 1.3, 2)
                return a, round(a + 0.25, 2)
            return round(scene["start"] + entrance * 0.45, 2), round(scene["start"] + entrance * 0.95, 2)

        out.append("## Verify after render")
        out.append("")
        out.append("Both frames of a pair must show the subject already opaque: a fade measured from")
        out.append("invisible to visible leaves no darkened trail, and reads as a one-sided change")
        out.append("instead of a direction. An `in-place` promise is checked after the arrival lands —")
        out.append("the claim there is that it holds position.")
        out.append("")
        out.append("```bash")
        out.append("npx hyperframes check . --json --at-transitions")
        for scene in checks:
            a, b = window(scene)
            out.append(f"# scene {scene['index']} — expect {scene['promise']['expect']}")
            out.append(f"npx hyperframes snapshot . --at {a:.2f},{b:.2f} --no-end -o snapshots/scene-{scene['index']:02d}")
            out.append(f"python3 {Path(__file__).resolve().parent / 'motion.py'} "
                       f"snapshots/scene-{scene['index']:02d}/frame-00-at-{a:.2f}s.png "
                       f"snapshots/scene-{scene['index']:02d}/frame-01-at-{b:.2f}s.png")
        out.append("```")
        out.append("")
        out.append("A promise that comes back a different direction, or `cannot-determine`, is a bug "
                   "in the composition — fix the tween, not the expectation.")

    if warnings:
        out.append("")
        out.append("## Warnings")
        out.append("")
        out += [f"- {x}" for x in warnings]
    if errors:
        out.append("")
        out.append("## Errors — resolve before building")
        out.append("")
        out += [f"- {x}" for x in errors]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(prog="spec", description=__doc__.splitlines()[0])
    ap.add_argument("spec", nargs="?", type=Path, help="video-spec.json")
    ap.add_argument("--json", action="store_true", help="emit the derived plan as JSON")
    ap.add_argument("--example", action="store_true", help="print a template spec and exit")
    args = ap.parse_args()

    if args.example:
        print(json.dumps(EXAMPLE, indent=2))
        return 0
    if not args.spec:
        ap.error("give a spec file, or use --example")
    path = args.spec.expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"spec not found: {path}")
    try:
        spec = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path} is not valid JSON: {exc}")

    errors: list[str] = []
    warnings: list[str] = []
    derived = validate(spec, errors, warnings)

    if args.json:
        print(json.dumps({"ok": not errors, "errors": errors, "warnings": warnings,
                          "canvas": {"width": derived["canvas"][0], "height": derived["canvas"][1]},
                          "transition_ms": list(derived["pacing"][2]),
                          "shot_seconds": list(derived["pacing"][1]),
                          "scenes": derived["plan"]}, indent=2))
    else:
        print(render_markdown(spec, derived, errors, warnings))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
