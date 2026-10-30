#!/usr/bin/env python3
"""Build an Animate prototype page (ASCII frames, lanes, optional live demos) from a spec.

Usage:
    python build_prototype.py spec.json [--out PATH]

Default output: .animate/prototypes/<slug>.html (relative to the current directory).
The spec is validated first; an invalid spec is refused.
Standard library only.
"""
import argparse
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from validate_spec import validate  # noqa: E402

TEMPLATE = os.path.join(HERE, "..", "assets", "prototype-template.html")

BRIDGE = """<script>
(function(){
  var rate = 1;
  function apply(){ try { document.getAnimations().forEach(function(a){ a.playbackRate = rate; }); } catch (e) {} }
  window.addEventListener('message', function(e){
    var d = e.data || {};
    if (d.type === 'rate') { rate = d.value || 1; apply(); }
    if (d.type === 'replay') { if (typeof window.play === 'function') { window.play(); apply(); } else { location.reload(); } }
    if (d.type === 'reverse' && typeof window.reverse === 'function') { window.reverse(); apply(); }
  });
  ['transitionrun','animationstart'].forEach(function(n){ document.addEventListener(n, apply, true); });
})();
</script>"""


def esc(s):
    return html.escape(str(s), quote=True)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-") or "prototype"


def render_lanes(opt):
    lanes = opt.get("lanes") or []
    if not lanes:
        return ""
    total = max([ln["end"] for ln in lanes] + [opt["timing"]["duration_ms"]]) or 1
    rows = []
    for ln in lanes:
        left = 100.0 * ln["start"] / total
        width = max(100.0 * (ln["end"] - ln["start"]) / total, 1.5)
        tech = f" {esc(ln['technique'])}" if ln.get("technique") else ""
        rows.append(
            f'<div class="lane"><span>{esc(ln["element"])}</span>'
            f'<div class="bar"><i style="left:{left:.1f}%;width:{width:.1f}%"></i></div>'
            f'<span class="ltime">{ln["start"]}-{ln["end"]}ms{tech}</span></div>'
        )
    return '<div class="lanes" role="group" aria-label="Animation timing lanes">' + "".join(rows) + "</div>"


def render_sequence(seq):
    frames = seq["frames"]
    data = esc(json.dumps([{"t": f["t"], "art": f["art"]} for f in frames]))
    cards = []
    for f in frames:
        note = f'<span class="note">{esc(f["note"])}</span>' if f.get("note") else ""
        cards.append(
            f'<div class="frame"><div class="ft">{f["t"]}ms{note}</div><pre>{esc(f["art"])}</pre></div>'
        )
    return (
        f'<figure class="seq" data-frames="{data}">'
        f'<figcaption>{esc(seq["label"])} '
        f'<button class="play" type="button">Play</button>'
        f'<label>speed <select aria-label="Playback speed">'
        f'<option value="1">1x</option><option value="0.5">0.5x</option><option value="0.25">0.25x</option>'
        f'</select></label></figcaption>'
        f'<pre class="player" aria-live="off"></pre>'
        f'<div class="frames">{"".join(cards)}</div></figure>'
    )


def render_demo(opt, has_reverse):
    demo = opt.get("demo_html")
    if not demo:
        return ""
    doc = ("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' "
           "content='width=device-width, initial-scale=1'></head><body style='margin:0;font-family:system-ui,sans-serif'>"
           + demo + BRIDGE + "</body></html>")
    reverse_btn = '<button class="reverse" type="button">Reverse</button>' if has_reverse else ""
    return (
        '<div class="demo"><h3>Live prototype</h3><div class="controls">'
        '<button class="replay" type="button">Replay</button>' + reverse_btn +
        '<label>speed <select aria-label="Demo speed"><option value="1">1x</option>'
        '<option value="0.5">0.5x</option><option value="0.25">0.25x</option></select></label></div>'
        f'<iframe title="Live prototype for option {esc(opt["id"])}" sandbox="allow-scripts" srcdoc="{esc(doc)}"></iframe></div>'
    )


def render_option(opt, recommended):
    t = opt["timing"]
    tags = "".join(f'<span class="tag">{esc(x)}</span>' for x in opt.get("techniques", []))
    star = " (recommended)" if recommended else ""
    facts = [
        ("Feel", opt["feel"]),
        ("Synchronization", opt.get("sync", "none")),
        ("Interactive", "yes" if opt.get("interactive") else "no"),
        ("Timing", f'{t["duration_ms"]}ms, {t["easing"]}'),
        ("Animates", ", ".join(opt.get("properties", [])) or "not listed"),
        ("Reduced motion", opt["reduced_motion"]),
    ]
    if opt.get("risk"):
        facts.append(("Risk", opt["risk"]))
    if opt.get("duration_exception"):
        facts.append(("Duration exception", opt["duration_exception"]))
    if opt.get("layout_exception"):
        facts.append(("Layout exception", opt["layout_exception"]))
    if opt.get("needs_html") and not opt.get("demo_html"):
        facts.append(("ASCII limits", opt.get("html_reason", "")))
    dl = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in facts)
    seqs = "".join(render_sequence(s) for s in opt["sequences"])
    has_reverse = any(s["label"].lower().startswith("reverse") for s in opt["sequences"])
    return (
        f'<section class="option" id="option-{esc(opt["id"])}">'
        f'<h2>Option {esc(opt["id"])}: {esc(opt["name"])}{star}</h2>'
        f'<div>{tags}</div><p class="concept">{esc(opt["concept"])}</p>'
        f'<dl class="facts">{dl}</dl>{render_lanes(opt)}{seqs}{render_demo(opt, has_reverse)}</section>'
    )


def build(spec):
    with open(TEMPLATE, encoding="utf-8") as fh:
        page = fh.read()
    rec = spec.get("recommendation") or {}
    body = "".join(render_option(o, o["id"] == rec.get("option")) for o in spec["options"])
    meta = "".join(f'<span class="chip">{esc(x)}</span>' for x in (
        f'command: {spec["command"]}', f'tier: {spec["tier"]}', f'target: {spec["target"]}',
        f'{len(spec["options"])} options'))
    rec_html = ""
    if rec:
        rec_html = (f'<div class="rec"><strong>Recommendation: option {esc(rec.get("option"))}.</strong> '
                    f'{esc(rec.get("reason", ""))}</div>')
    for key, val in (("__TITLE__", esc(spec["title"])),
                     ("__SUBTITLE__", esc(f'ASCII animation prototype for {spec["target"]}')),
                     ("__META__", meta), ("__RECOMMENDATION__", rec_html), ("__BODY__", body)):
        page = page.replace(key, val)
    return page


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out")
    args = ap.parse_args()
    with open(args.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    errors, warnings = validate(spec)
    for w in warnings:
        print(f"warning {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"ERROR   {e}", file=sys.stderr)
        print("spec is invalid; fix the errors and run again", file=sys.stderr)
        sys.exit(1)
    out = args.out or os.path.join(".animate", "prototypes", f'{slug(spec["target"])}-{spec["command"]}.html')
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(build(spec))
    print(out)


if __name__ == "__main__":
    main()
