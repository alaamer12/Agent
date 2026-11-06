#!/usr/bin/env python3
"""Assemble an avatar SVG from a rig (rig.json + parts/<slot>/<id>.svg).

  python scripts/assemble.py RIG_DIR --list                      # slots and variants
  python scripts/assemble.py RIG_DIR --lint                      # contract checks on every part
  python scripts/assemble.py RIG_DIR --pick hair=wavy nose=wedge -o out.svg
  python scripts/assemble.py RIG_DIR --picker picker.html        # self-contained swap-parts demo page

A part file is an <svg> holding <g data-layer="LAYER"> groups (and optionally <defs>).
Layers are stacked in the order given by rig.json "layers"; a slot may only paint the
layers it lists. Colors come from palette variables: fill="var(--skin)".
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
NS_RE = re.compile(r'\sxmlns(:\w+)?="[^"]+"')
VAR_RE = re.compile(r"var\(--([\w-]+)\)")
HARD_COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")


def local(tag):
    return tag.split("}", 1)[-1]


def load_rig(rig_dir):
    p = Path(rig_dir) / "rig.json"
    if not p.exists():
        sys.exit(f"rig.json not found in {rig_dir}")
    rig = json.loads(p.read_text(encoding="utf-8"))
    for key in ("viewBox", "palette", "layers", "slots", "default"):
        if key not in rig:
            sys.exit(f"rig.json is missing '{key}'")
    for slot, spec in rig["slots"].items():
        bad = [l for l in spec["layers"] if l not in rig["layers"]]
        if bad:
            sys.exit(f"slot '{slot}' lists unknown layers {bad}")
    return rig


def list_variants(rig_dir, rig):
    out = {}
    for slot in rig["slots"]:
        d = Path(rig_dir) / "parts" / slot
        out[slot] = sorted(p.stem for p in d.glob("*.svg")) if d.is_dir() else []
    return out


def read_part(rig_dir, slot, vid):
    """Return {'defs': [xml...], 'layers': {layer: xml}} for one part file."""
    path = Path(rig_dir) / "parts" / slot / f"{vid}.svg"
    if not path.exists():
        raise FileNotFoundError(f"missing part {slot}/{vid} ({path})")
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    defs, layers = [], {}
    for child in root:
        name = local(child.tag)
        if name == "defs":
            defs.extend(NS_RE.sub("", ET.tostring(c, encoding="unicode")) for c in child)
        elif name == "g" and child.get("data-layer"):
            child.set("data-slot", slot)
            child.set("data-part", vid)
            layers[child.get("data-layer")] = NS_RE.sub("", ET.tostring(child, encoding="unicode"))
    return {"defs": defs, "layers": layers}


def lint(rig_dir, rig):
    """Return a list of (level, message). level is 'error' or 'warn'."""
    issues = []
    palette = set(rig["palette"])
    for slot, ids in list_variants(rig_dir, rig).items():
        if not ids:
            issues.append(("error", f"slot '{slot}' has no parts"))
        for vid in ids:
            path = Path(rig_dir) / "parts" / slot / f"{vid}.svg"
            tag = f"{slot}/{vid}"
            text = path.read_text(encoding="utf-8")
            try:
                part = read_part(rig_dir, slot, vid)
            except ET.ParseError as e:
                issues.append(("error", f"{tag}: invalid XML ({e})"))
                continue
            extra = set(part["layers"]) - set(rig["slots"][slot]["layers"])
            if extra:
                issues.append(("error", f"{tag}: paints layers {sorted(extra)} that slot '{slot}' does not own"))
            if not part["layers"]:
                issues.append(("error", f"{tag}: no <g data-layer=...> group"))
            for var in set(VAR_RE.findall(text)) - palette:
                issues.append(("error", f"{tag}: unknown palette variable --{var}"))
            if HARD_COLOR_RE.search(text):
                issues.append(("warn", f"{tag}: hard-coded color; use palette variables so recoloring works"))
            for m in re.finditer(r'\bid="([^"]+)"', text):
                if not m.group(1).startswith(f"{slot}-{vid}"):
                    issues.append(("error", f"{tag}: id '{m.group(1)}' must start with '{slot}-{vid}' to avoid collisions"))
            if re.search(r"<script|<image|href=\"https?:|xlink:", text):
                issues.append(("error", f"{tag}: scripts, raster images, remote or xlink references are not allowed"))
    return issues


def compose(rig_dir, rig, picks=None, include_backdrop=True, palette=None):
    """Build the assembled <svg> string for one combination."""
    chosen = dict(rig["default"])
    chosen.update(picks or {})
    unknown = set(chosen) - set(rig["slots"])
    if unknown:
        raise ValueError(f"unknown slots: {sorted(unknown)}")
    by_layer = {l: [] for l in rig["layers"]}
    defs = []
    for slot, vid in chosen.items():
        spec = rig["slots"][slot]
        if spec.get("backdrop") and not include_backdrop:
            continue
        part = read_part(rig_dir, slot, vid)
        defs.extend(part["defs"])
        for layer, xml in part["layers"].items():
            if layer not in spec["layers"]:
                raise ValueError(f"{slot}/{vid} paints layer '{layer}' that slot '{slot}' does not own")
            by_layer[layer].append(xml)
    pal = dict(rig["palette"])
    pal.update(palette or {})
    css = ";".join(f"--{k}:{v}" for k, v in pal.items())
    frame = rig.get("frame")
    clip_open = clip_close = ""
    if frame and frame.get("shape") == "circle":
        defs.insert(0, f'<clipPath id="avatar-frame"><circle cx="{frame["cx"]}" cy="{frame["cy"]}" r="{frame["r"]}"/></clipPath>')
        clip_open, clip_close = '<g clip-path="url(#avatar-frame)">', "</g>"
    body = "".join("".join(by_layer[l]) for l in rig["layers"])
    return (
        f'<svg xmlns="{SVG_NS}" class="avatar-rig" viewBox="{rig["viewBox"]}" role="img" aria-label="Avatar">'
        f"<style>.avatar-rig{{{css}}}</style><defs>{''.join(defs)}</defs>{clip_open}{body}{clip_close}</svg>"
    )


PICKER = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Avatar parts picker</title>
<style>
:root{color-scheme:light dark;--bg:#faf6ee;--fg:#2b2118;--card:#fff;--line:#e4dccb}
@media (prefers-color-scheme:dark){:root{--bg:#1d1813;--fg:#f1e8d8;--card:#2a231c;--line:#3d3429}}
*{box-sizing:border-box}body{margin:0;font:15px/1.4 system-ui,sans-serif;background:var(--bg);color:var(--fg);
display:grid;grid-template-columns:minmax(260px,420px) minmax(240px,320px);gap:28px;justify-content:center;padding:32px 20px}
@media (max-width:760px){body{grid-template-columns:1fr}}
#stage{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px}
#stage svg{width:100%;height:auto;display:block}
form{display:grid;gap:12px;align-content:start}label{display:grid;gap:4px;font-weight:600;font-size:13px}
select,button{font:inherit;padding:8px 10px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--fg)}
button{cursor:pointer;font-weight:600}h2{margin:8px 0 0;font-size:13px;text-transform:uppercase;letter-spacing:.06em;opacity:.7}
.sw{display:grid;grid-template-columns:1fr 44px;align-items:center;gap:8px;font-weight:500}.sw input{width:44px;height:30px;padding:0;border:0;background:none}
</style></head><body>
<div id="stage"></div>
<form id="controls"></form>
<script>
const DATA = __DATA__;
const state = Object.assign({}, DATA.default), pal = Object.assign({}, DATA.palette);
const stage = document.getElementById('stage'), form = document.getElementById('controls');
function compose(){
  const layers = {}, defs = [];
  if (DATA.frame) defs.push(`<clipPath id="avatar-frame"><circle cx="${DATA.frame.cx}" cy="${DATA.frame.cy}" r="${DATA.frame.r}"/></clipPath>`);
  for (const [slot, id] of Object.entries(state)) {
    const p = DATA.slots[slot][id]; defs.push(...p.defs);
    for (const [l, xml] of Object.entries(p.layers)) (layers[l] = layers[l] || []).push(xml);
  }
  const css = Object.entries(pal).map(([k,v]) => `--${k}:${v}`).join(';');
  const body = DATA.layers.map(l => (layers[l]||[]).join('')).join('');
  stage.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="avatar-rig" viewBox="${DATA.viewBox}" role="img" aria-label="Avatar"><style>.avatar-rig{${css}}</style><defs>${defs.join('')}</defs>${DATA.frame?'<g clip-path="url(#avatar-frame)">':''}${body}${DATA.frame?'</g>':''}</svg>`;
}
function build(){
  form.innerHTML = '';
  for (const slot of Object.keys(DATA.slots)) {
    const l = document.createElement('label'); l.textContent = slot;
    const s = document.createElement('select');
    for (const id of Object.keys(DATA.slots[slot])) s.add(new Option(id, id, false, id === state[slot]));
    s.onchange = () => { state[slot] = s.value; compose(); };
    l.append(s); form.append(l);
  }
  const rnd = document.createElement('button'); rnd.type = 'button'; rnd.textContent = 'Randomize parts';
  rnd.onclick = () => { for (const slot of Object.keys(DATA.slots)) { const ids = Object.keys(DATA.slots[slot]); state[slot] = ids[Math.floor(Math.random()*ids.length)]; } build(); compose(); };
  form.append(rnd);
  const h = document.createElement('h2'); h.textContent = 'Palette'; form.append(h);
  for (const k of Object.keys(pal)) {
    const w = document.createElement('label'); w.className = 'sw'; w.textContent = k;
    const i = document.createElement('input'); i.type = 'color'; i.value = pal[k];
    i.oninput = () => { pal[k] = i.value; compose(); };
    w.append(i); form.append(w);
  }
}
build(); compose();
</script></body></html>
"""


def build_picker(rig_dir, rig):
    slots = {}
    for slot, ids in list_variants(rig_dir, rig).items():
        slots[slot] = {vid: read_part(rig_dir, slot, vid) for vid in ids}
    data = {k: rig[k] for k in ("viewBox", "palette", "layers", "default")}
    data["frame"] = rig.get("frame") if (rig.get("frame") or {}).get("shape") == "circle" else None
    data["slots"] = slots
    return PICKER.replace("__DATA__", json.dumps(data).replace("</", "<\\/"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rig_dir")
    ap.add_argument("--pick", nargs="*", default=[], metavar="SLOT=ID")
    ap.add_argument("-o", "--out", default="avatar.svg")
    ap.add_argument("--no-backdrop", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--lint", action="store_true")
    ap.add_argument("--picker", metavar="HTML")
    a = ap.parse_args()

    rig = load_rig(a.rig_dir)
    if a.list:
        for slot, ids in list_variants(a.rig_dir, rig).items():
            mark = lambda i: f"*{i}" if rig["default"].get(slot) == i else i
            print(f"{slot:10s} {', '.join(mark(i) for i in ids) or '(none)'}")
        return
    if a.lint:
        issues = lint(a.rig_dir, rig)
        for level, msg in issues:
            print(f"{level.upper():5s} {msg}")
        errors = sum(1 for l, _ in issues if l == "error")
        print(f"lint: {errors} error(s), {len(issues) - errors} warning(s)")
        sys.exit(1 if errors else 0)
    if a.picker:
        Path(a.picker).write_text(build_picker(a.rig_dir, rig), encoding="utf-8")
        print(f"wrote {a.picker}")
        return
    picks = dict(p.split("=", 1) for p in a.pick)
    Path(a.out).write_text(compose(a.rig_dir, rig, picks, not a.no_backdrop), encoding="utf-8")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
