#!/usr/bin/env python3
"""Validate an Animate prototype spec before building it.

Usage:
    python validate_spec.py spec.json [--format text|json]

Exit status is 1 when there are errors, 0 otherwise (warnings do not fail).
Standard library only.
"""
import argparse
import json
import sys

TIER_CAP_MS = {"routine": 300, "rare": 600, "showcase": 1600}
COMMANDS = {"micro", "component", "transition"}
SYNC = {"none", "instant", "domino", "linked"}
LAYOUT_EXACT = {
    "width", "height", "top", "left", "right", "bottom", "border-width",
    "grid-template-rows", "grid-template-columns", "flex-basis", "font-size", "line-height",
}


def _is_layout(prop: str) -> bool:
    p = prop.strip().lower()
    return p in LAYOUT_EXACT or p.startswith("margin") or p.startswith("padding")


def validate(spec):
    errors, warnings = [], []

    def err(msg):
        errors.append(msg)

    def warn(msg):
        warnings.append(msg)

    if not isinstance(spec, dict):
        return ["spec must be a JSON object"], []

    for key in ("title", "target", "command", "tier", "options"):
        if key not in spec:
            err(f"missing top-level field '{key}'")
    command = spec.get("command")
    tier = spec.get("tier")
    if command not in COMMANDS:
        err(f"command must be one of {sorted(COMMANDS)}, got {command!r}")
    if tier not in TIER_CAP_MS:
        err(f"tier must be one of {sorted(TIER_CAP_MS)}, got {tier!r}")

    options = spec.get("options")
    if not isinstance(options, list) or not options:
        err("'options' must be a non-empty list")
        return errors, warnings
    if len(options) == 1:
        warn("only one option: creative direction should offer two to four options that differ in concept")
    if len(options) > 4:
        warn(f"{len(options)} options: more than four is hard to compare")

    seen = set()
    for i, opt in enumerate(options):
        where = f"option[{i}]"
        if not isinstance(opt, dict):
            err(f"{where} must be an object")
            continue
        oid = opt.get("id")
        where = f"option {oid!r}" if oid else where
        if not oid:
            err(f"{where}: missing 'id'")
        elif oid in seen:
            err(f"{where}: duplicate id")
        seen.add(oid)
        for key in ("name", "concept", "feel", "timing", "sequences", "reduced_motion"):
            if not opt.get(key):
                err(f"{where}: missing '{key}'")

        sync = opt.get("sync", "none")
        if sync not in SYNC:
            err(f"{where}: sync must be one of {sorted(SYNC)}, got {sync!r}")
        if not isinstance(opt.get("interactive", False), bool):
            err(f"{where}: 'interactive' must be true or false")

        # timing
        timing = opt.get("timing") or {}
        dur = timing.get("duration_ms")
        if not isinstance(dur, (int, float)) or dur <= 0:
            err(f"{where}: timing.duration_ms must be a positive number")
        elif tier in TIER_CAP_MS and dur > TIER_CAP_MS[tier] and not opt.get("duration_exception"):
            err(f"{where}: duration {dur}ms exceeds the {tier} cap of {TIER_CAP_MS[tier]}ms; "
                f"shorten it or add 'duration_exception' with a reason")
        if not timing.get("easing"):
            err(f"{where}: missing timing.easing")
        elif "ease-in" in str(timing["easing"]).lower() and "ease-in-out" not in str(timing["easing"]).lower():
            err(f"{where}: ease-in is not allowed for UI motion; use an ease-out curve or a spring")

        # properties
        props = opt.get("properties", [])
        if not isinstance(props, list) or not props:
            warn(f"{where}: list the animated 'properties' so the review can check them")
        else:
            bad = [p for p in props if _is_layout(str(p))]
            if bad and not opt.get("layout_exception"):
                err(f"{where}: layout properties {bad} are animated; use transform/opacity or add "
                    f"'layout_exception' explaining a deliberate container tween")

        # html
        if opt.get("needs_html"):
            if not opt.get("html_reason"):
                err(f"{where}: needs_html is true but 'html_reason' is empty")
            if not opt.get("demo_html"):
                warn(f"{where}: needs_html without demo_html; ask the user whether to keep ASCII or build a live demo")

        # sequences
        seqs = opt.get("sequences")
        labels = []
        if isinstance(seqs, list):
            for j, seq in enumerate(seqs):
                swhere = f"{where} sequence[{j}]"
                if not isinstance(seq, dict) or not seq.get("label"):
                    err(f"{swhere}: needs a 'label'")
                    continue
                labels.append(str(seq["label"]).lower())
                frames = seq.get("frames")
                if not isinstance(frames, list) or len(frames) < 2:
                    err(f"{swhere}: needs at least two frames")
                    continue
                last_t = -1
                line_counts = set()
                for k, fr in enumerate(frames):
                    t = fr.get("t") if isinstance(fr, dict) else None
                    art = fr.get("art") if isinstance(fr, dict) else None
                    if not isinstance(t, (int, float)) or t < 0:
                        err(f"{swhere} frame[{k}]: 't' must be a number >= 0")
                        continue
                    if k == 0 and t != 0:
                        err(f"{swhere}: first frame must be at t=0")
                    if t < last_t:
                        err(f"{swhere} frame[{k}]: times must not decrease")
                    last_t = t
                    if not isinstance(art, str) or not art.strip():
                        err(f"{swhere} frame[{k}]: 'art' must be a non-empty string")
                    else:
                        line_counts.add(len(art.split("\n")))
                if len(frames) > 12:
                    warn(f"{swhere}: {len(frames)} frames; four to nine usually communicate best")
                if len(line_counts) > 1:
                    warn(f"{swhere}: frames have different line counts; use one fixed canvas size")
                if isinstance(dur, (int, float)) and dur > 0 and last_t > dur * 1.6:
                    warn(f"{swhere}: last frame at {last_t}ms is well past duration_ms={dur}")
        elif seqs is not None:
            err(f"{where}: 'sequences' must be a list")

        if command == "transition":
            if not any(l.startswith("forward") for l in labels):
                err(f"{where}: transitions need a 'forward' sequence")
            if not any(l.startswith("reverse") for l in labels):
                err(f"{where}: transitions need a designed 'reverse' sequence")

        # lanes
        lanes = opt.get("lanes", [])
        if isinstance(lanes, list):
            for k, ln in enumerate(lanes):
                s, e = ln.get("start"), ln.get("end")
                if not isinstance(s, (int, float)) or not isinstance(e, (int, float)) or e < s or s < 0:
                    err(f"{where} lane[{k}]: start/end must be numbers with 0 <= start <= end")
                if not ln.get("element"):
                    err(f"{where} lane[{k}]: missing 'element'")
        if sync in ("domino", "linked", "instant") and not lanes:
            warn(f"{where}: sync={sync} reads best with 'lanes' showing who starts and ends when")

    rec = spec.get("recommendation")
    if rec and rec.get("option") not in seen:
        err(f"recommendation.option {rec.get('option')!r} does not match any option id")
    if not rec:
        warn("no recommendation: add one with a reason")
    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()
    try:
        with open(args.spec, encoding="utf-8") as fh:
            spec = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read spec: {exc}", file=sys.stderr)
        sys.exit(2)
    errors, warnings = validate(spec)
    if args.format == "json":
        print(json.dumps({"ok": not errors, "errors": errors, "warnings": warnings}, indent=2))
    else:
        for e in errors:
            print(f"ERROR   {e}")
        for w in warnings:
            print(f"warning {w}")
        print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
