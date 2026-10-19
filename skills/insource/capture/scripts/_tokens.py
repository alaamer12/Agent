"""Design-token extraction from a parsed Sheet: colours, variables, typography, spacing, motion, layout."""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from _cssparse import (_balanced, color_info, extract_colors, fmt_num, normalize_color, split_top,
                       split_ws, to_px)
from _data import load_json

ROOTISH = {":root", "html", ":host", "*", "body", "html, body", ":root, :host"}


def family_of(name: str) -> tuple[str, str | None]:
    """('--margin', 'xs') for '--margin-xs'. Any variables sharing everything but the last segment form a
    family, whatever the suffix vocabulary (xs/small/1/primary/...); no suffix list involved."""
    head, sep, tail = name.rpartition("-")
    if not sep or not tail or not head.startswith("--") or head == "--":
        return name, None
    return head, tail


# Properties where a bare colour *name* is a colour although the property is not in COLOR_ROLE.
NAMED_OK_PROPS = {"accent-color", "scrollbar-color", "text-emphasis-color", "stop-color", "flood-color",
                  "lighting-color", "column-rule", "column-rule-color"}
SIZE_ORDER = {"xxxxs": 0, "xxxs": 1, "xxs": 2, "xs": 3, "s": 4, "sm": 4, "m": 5, "md": 5, "l": 6, "lg": 6,
              "xl": 7, "xxl": 8, "xxxl": 9, "xxxxl": 10}

COLOR_ROLE = [
    (lambda p: p in ("color", "caret-color", "text-decoration-color", "-webkit-text-fill-color"), "text"),
    (lambda p: p in ("background", "background-color", "background-image"), "background"),
    (lambda p: p in ("fill", "stroke"), "svg"),
    (lambda p: p in ("box-shadow", "text-shadow", "filter", "drop-shadow"), "shadow"),
    (lambda p: (p.startswith("border") or p.startswith("outline")) and "radius" not in p, "border"),
]
SPACING_PROPS = ("margin", "padding", "gap", "row-gap", "column-gap")
RADIUS_PROPS = ("border-radius", "border-top-left-radius", "border-top-right-radius",
                "border-bottom-left-radius", "border-bottom-right-radius")
_FEATURES = load_json("css_features.json")
MODERN_PROPS = _FEATURES["modern_properties"]          # data: reporting lists, easy to extend
SELECTOR_FEATURES = tuple(_FEATURES["selector_features"])

# Safety limits and heuristic parameters (named so they are visible and tunable in one place).
MAX_RESOLVED_CHARS = 4000      # cap on an expanded var() value; protects against cyclic / exploding variable graphs
MAX_VAR_DEPTH = 8              # nesting depth followed through fallbacks
MAX_VALUE_CHARS = 20000        # declaration values longer than this are corrupt/minified blobs and are skipped
GRID_BASES = (8, 4, 2)         # spacing grids tried, coarsest first
GRID_MIN_FIT = 0.85            # share of spacing px values that must be multiples of the base
INHERIT = ("inherit", "initial", "unset", "revert", "revert-layer")
TYPO_PROPS = ("font-family", "font-size", "font-weight", "line-height", "letter-spacing", "text-transform")
TAG_SEL = re.compile(r"^(html|body|h[1-6]|p|a|small|strong|em|code|pre|button|input|select|textarea|label|li|blockquote|th|td)$")


def role_of(prop: str) -> str:
    for test, role in COLOR_ROLE:
        if test(prop):
            return role
    return "other"


def _top(counter: Counter, n: int) -> list[tuple]:
    return counter.most_common(n)


class Resolver:
    def __init__(self, rules):
        self.defs: dict[str, list[dict]] = defaultdict(list)
        self._memo: dict[str, str] = {}
        self._active: set[str] = set()
        for r in rules:
            for prop, val, _ in r["decls"]:
                if prop.startswith("--"):
                    self.defs[prop].append({"value": val, "sel": r["sel"], "ctx": r["ctx"]})

    def base_value(self, name: str) -> str | None:
        entries = self.defs.get(name)
        if not entries:
            return None
        for e in entries:
            if not e["ctx"] and e["sel"].strip() in ROOTISH:
                return e["value"]
        for e in entries:
            if not e["ctx"]:
                return e["value"]
        return entries[0]["value"]

    def _name_value(self, name: str) -> str | None:
        """Fully resolved value of a variable: memoized, cycle-safe (a cycle stays symbolic) and size-capped."""
        if name in self._memo:
            return self._memo[name]
        base = self.base_value(name)
        if base is None:
            return None
        if name in self._active:
            return f"var({name})"
        self._active.add(name)
        try:
            val = self.resolve(base)
        finally:
            self._active.discard(name)
        val = val[:MAX_RESOLVED_CHARS]
        self._memo[name] = val
        return val

    def resolve(self, value: str, depth: int = 0) -> str:
        if depth > MAX_VAR_DEPTH or "var(" not in value:
            return value
        out, i = [], 0
        while True:
            j = value.find("var(", i)
            if j < 0:
                out.append(value[i:])
                break
            out.append(value[i:j])
            end = _balanced(value, j)
            inner = value[j + 4:end - 1]
            parts = split_top(inner)
            name = parts[0].strip() if parts else ""
            resolved = self._name_value(name)
            if resolved is not None:
                out.append(resolved)
            elif len(parts) > 1:
                out.append(self.resolve(",".join(parts[1:]).strip(), depth + 1))
            else:
                out.append(f"var({name})")
            i = end
        return "".join(out)[:MAX_RESOLVED_CHARS]


def _ctx_label(ctx: tuple) -> str:
    return " & ".join(c.replace("@media ", "").strip() for c in ctx)


def analyze_tokens(sheet, top: int = 25) -> dict:
    rules = sheet.rules
    R = Resolver(rules)
    res = R.resolve

    use_count: Counter = Counter()
    props: Counter = Counter()
    colors: Counter = Counter()
    color_roles: dict[str, Counter] = defaultdict(Counter)
    role_tokens: dict[str, Counter] = defaultdict(Counter)
    fonts: Counter = Counter()
    sizes: Counter = Counter()
    size_raw: dict[str, str] = {}
    weights, line_heights, letter_sp, transforms = Counter(), Counter(), Counter(), Counter()
    spacing_raw, spacing_px, radius_raw = Counter(), Counter(), Counter()
    spacing_tok: dict[str, str] = {}
    borders, shadows, gradients, opacity, z_index = Counter(), Counter(), Counter(), Counter(), Counter()
    durations, easings, trans_props, anim_names = Counter(), Counter(), Counter(), Counter()
    display, position, direction, grid_cols, max_w = Counter(), Counter(), Counter(), Counter(), Counter()
    units: Counter = Counter()
    color_scheme: Counter = Counter()
    type_rows: dict[tuple, dict] = {}
    tag_styles: dict[str, dict] = defaultdict(dict)
    selector_feats: Counter = Counter()

    for r in rules:
        sel, ctx = r["sel"], r["ctx"]
        for f in SELECTOR_FEATURES:
            if f in sel:
                selector_feats[f.strip(":(").replace("(", "")] += 1
        rec = {}
        for prop, val, _ in r["decls"]:
            props[prop] += 1
            for m in re.finditer(r"var\(\s*(--[\w-]+)", val):
                use_count[m.group(1)] += 1
            if prop.startswith("--"):
                continue
            if len(val) > MAX_VALUE_CHARS:
                continue
            rv = res(val)
            for u in re.findall(r"(?<![\w.#-])-?\d*\.?\d+(px|rem|em|vw|vh|dvh|svh|ch|%|fr|cqw|cqi)(?![\w-])", rv):
                units[u] += 1
            # colours
            cols = extract_colors(rv, allow_named=role_of(prop) != "other" or prop in NAMED_OK_PROPS)
            if cols:
                role = role_of(prop)
                for c in cols:
                    colors[c] += 1
                    color_roles[c][role] += 1
                for name in set(re.findall(r"var\(\s*(--[\w-]+)", val)):
                    base = R.base_value(name)
                    if base is not None and extract_colors(res(base)):
                        role_tokens[role][name] += 1
            # typography
            if prop in TYPO_PROPS and rv.strip().lower() in INHERIT:
                continue
            if prop == "font-family":
                fonts[res(val)] += 1
            elif prop == "font-size":
                px = to_px(rv)
                key = fmt_num(px) + "px" if px is not None else rv
                sizes[key] += 1
                size_raw.setdefault(key, val)
                rec["size"] = key
            elif prop == "font-weight":
                weights[rv] += 1
                rec["weight"] = rv
            elif prop == "line-height":
                line_heights[rv] += 1
                rec["lh"] = rv
            elif prop == "letter-spacing":
                letter_sp[rv] += 1
                rec["ls"] = rv
            elif prop == "text-transform":
                transforms[rv] += 1
                rec["tt"] = rv
            if prop == "font-family":
                rec["family"] = split_top(rv)[0].strip("\"' ") if split_top(rv) else rv
            # spacing / radius
            if prop in SPACING_PROPS or prop.split("-")[0] in ("margin", "padding") and prop.count("-") == 1:
                for tok in split_ws(val):
                    if tok in ("auto", "inherit", "initial", "unset", "0"):
                        continue
                    spacing_raw[tok] += 1
                    px = to_px(res(tok))
                    spacing_tok.setdefault(tok, res(tok))
                    if px is not None and px > 0:
                        spacing_px[px] += 1
            if prop in RADIUS_PROPS:
                for tok in split_ws(val):
                    if tok not in ("0", "/", "inherit", "initial"):
                        radius_raw[tok] += 1
                        spacing_tok.setdefault(tok, res(tok))
            # borders / shadows / gradients
            if prop.startswith("border") and prop not in RADIUS_PROPS and "radius" not in prop and prop != "border-collapse" \
                    and re.search(r"\d", rv) and prop not in ("border-spacing",):
                borders[re.sub(r"\s+", " ", rv)] += 1
            if prop in ("box-shadow", "text-shadow"):
                for part in split_top(rv):
                    shadows[(prop, re.sub(r"\s+", " ", part))] += 1
            if prop in ("filter", "backdrop-filter"):
                for m in re.finditer(r"drop-shadow\(", rv):
                    shadows[("drop-shadow", re.sub(r"\s+", " ", rv[m.end():_balanced(rv, m.start()) - 1]))] += 1
            for m in re.finditer(r"(?:repeating-)?(?:linear|radial|conic)-gradient\(", rv):
                gradients[re.sub(r"\s+", " ", rv[m.start():_balanced(rv, m.start())])] += 1
            if prop == "opacity":
                opacity[rv] += 1
            if prop == "z-index":
                z_index[rv] += 1
            # motion
            if prop in ("transition", "transition-duration", "animation", "animation-duration",
                        "transition-timing-function", "animation-timing-function", "transition-delay"):
                for t, unit in re.findall(r"(?<![\w.-])(\d*\.?\d+)(ms|s)\b", rv):
                    ms = float(t) * (1000 if unit == "s" else 1)
                    if "delay" not in prop:
                        durations[fmt_num(ms) + "ms"] += 1
                for m in re.finditer(r"cubic-bezier\(|steps\(", rv):
                    easings[re.sub(r"\s+", "", rv[m.start():_balanced(rv, m.start())])] += 1
                for kw in re.findall(r"(?<![\w-])(ease-in-out|ease-in|ease-out|ease|linear)(?![\w-])", rv):
                    easings[kw] += 1
                if prop == "transition":
                    for part in split_top(rv):
                        first = part.split()[0] if part.split() else ""
                        if first and not re.match(r"^[\d.]", first):
                            trans_props[first] += 1
                elif prop == "transition-property":
                    for p_ in split_top(rv):
                        trans_props[p_] += 1
            if prop == "animation-name" or (prop == "animation" and rv):
                for tok in rv.replace(",", " ").split():
                    if re.match(r"^[a-zA-Z_][\w-]*$", tok) and tok not in ("infinite", "alternate", "forwards", "backwards", "both", "none", "normal", "reverse", "paused", "running") \
                            and not re.match(r"^(ease|linear|steps)", tok):
                        anim_names[tok] += 1
            # layout
            if prop == "display":
                display[rv] += 1
            elif prop == "position":
                position[rv] += 1
            elif prop == "flex-direction":
                direction[rv] += 1
            elif prop == "grid-template-columns":
                grid_cols[re.sub(r"\s+", " ", rv)] += 1
            elif prop in ("max-width", "width") and "px" in rv and "calc" not in rv and prop == "max-width":
                max_w[rv] += 1
            elif prop == "color-scheme":
                color_scheme[rv] += 1
        # type ramp rows (rules that set font-size)
        if "size" in rec:
            key = (rec["size"], rec.get("weight", ""), rec.get("lh", ""), rec.get("ls", ""), rec.get("family", ""), rec.get("tt", ""))
            row = type_rows.setdefault(key, {"count": 0, "selectors": []})
            row["count"] += 1
            if len(row["selectors"]) < 3:
                row["selectors"].append(sel[:70])
        for part in split_top(sel):
            if TAG_SEL.match(part.strip()) and not ctx:
                for prop, val, _ in r["decls"]:
                    if prop in ("font-family", "font-size", "font-weight", "line-height", "letter-spacing", "color"):
                        tag_styles[part.strip()][prop] = f"{val}  ->  {res(val)}" if "var(" in val else val

    # ----- variables -----
    var_entries = []
    for name, entries in R.defs.items():
        base = R.base_value(name)
        resolved = R.resolve(base) if base is not None else ""
        over: dict[str, str] = {}
        for e in entries:
            if e["ctx"] and e["sel"].strip() in ROOTISH and e["value"] != base:
                over[_ctx_label(e["ctx"])] = R.resolve(e["value"])
        scoped = [e for e in entries if e["sel"].strip() not in ROOTISH and not e["ctx"]]
        is_color = bool(extract_colors(resolved)) and normalize_color(resolved.strip()) is not None
        var_entries.append({"name": name, "value": base if base is not None else entries[0]["value"], "resolved": resolved or entries[0]["value"],
                            "is_color": is_color, "uses": use_count.get(name, 0), "overrides": over,
                            "scoped_in": len(scoped), "defined_at": entries[0]["sel"][:40]})

    families: dict[str, list] = defaultdict(list)
    for v in var_entries:
        fam, suffix = family_of(v["name"])
        families[fam].append((suffix, v))
    fam_out, ramps = [], defaultdict(dict)
    for fam, mem in families.items():
        if len(mem) < 3 or any(step is None for step, _ in mem):
            continue
        if all(v["is_color"] for _, v in mem if v["scoped_in"] == 0):
            if all(sfx.isdigit() for sfx, _ in mem):            # numeric colour steps -> palette ramp
                parts = fam.lstrip("-").split("-")
                prefix = "--" + parts[0] if len(parts) > 1 else fam
                ramps[prefix][fam[len(prefix) + 1:] if len(parts) > 1 else fam] = [
                    (int(sfx), v["resolved"].lower()) for sfx, v in sorted(mem, key=lambda x: int(x[0]))]
            continue                                             # named colour roles stay in the Colors section
        order = {id(v): i for i, (_, v) in enumerate(mem)}      # definition order is the fallback
        def sort_key(item):
            sfx, v = item
            if sfx.isdigit():
                return (0, int(sfx), 0)
            if sfx in SIZE_ORDER:
                return (1, SIZE_ORDER[sfx], 0)
            return (2, 0, order[id(v)])
        fam_out.append({"family": fam, "kind": "scale", "members": [
            {"name": v["name"], "value": v["resolved"], "uses": v["uses"], "overrides": v["overrides"]}
            for _, v in sorted(mem, key=sort_key)]})
    in_family = {m["name"] for f in fam_out for m in f["members"]}
    ramp_names = {f"{p}-{n}-{s}" for p, d in ramps.items() for n, steps in d.items() for s, _ in steps}
    singles = [v for v in var_entries if v["name"] not in in_family and v["name"] not in ramp_names]

    # theme / variant scopes, detected structurally: a selector (or colour-scheme media query) that
    # re-defines most of the variables the root defines is a theme or variant, whatever it is called.
    root_vars = {n for n, entries in R.defs.items() if any(not e["ctx"] and e["sel"].strip() in ROOTISH for e in entries)}
    scope_vars: dict[tuple, set] = defaultdict(set)
    for n, entries in R.defs.items():
        for e in entries:
            ctx = _ctx_label(e["ctx"])
            if e["sel"].strip() in ROOTISH and (not e["ctx"] or "prefers-color-scheme" not in ctx):
                continue                                         # root definitions and responsive root overrides
            scope_vars[(e["sel"][:80], ctx)].add(n)
    override_scopes = []
    for (sel_, ctx_), vs in scope_vars.items():
        overlap = len(vs & root_vars) / len(vs)
        if root_vars and len(vs) >= 3 and overlap >= 0.5:
            override_scopes.append({"selector": sel_, "context": ctx_, "variables": len(vs), "overlap": round(overlap, 2)})
    override_scopes.sort(key=lambda x: (-x["variables"], x["selector"]))

    # scoped (context-switching) variables
    scoped_by_fam: dict[str, dict] = {}
    for name, entries in R.defs.items():
        fam = family_of(name)[0]
        for e in entries:
            if not e["ctx"] and e["sel"].strip() not in ROOTISH:
                d = scoped_by_fam.setdefault(fam, {"selectors": set(), "vars": set()})
                d["selectors"].add(e["sel"][:70])
                d["vars"].add(name)
    scoped = [{"family": f, "selectors": len(d["selectors"]), "variables": len(d["vars"]),
               "examples": sorted(d["selectors"])[:3]} for f, d in scoped_by_fam.items()]
    scoped.sort(key=lambda x: -x["selectors"])

    # ----- colours -----
    in_use = []
    for c, n in colors.most_common(top * 2):
        info = color_info(c)
        in_use.append({"hex": c, "count": n, "roles": dict(color_roles[c].most_common()), **info})
    roles_out = {}
    for role, ctr in role_tokens.items():
        roles_out[role] = [{"token": t, "value": R.resolve(f"var({t})").lower(), "count": n} for t, n in ctr.most_common(10)]
    neutral = sum(1 for c in colors if color_info(c).get("kind") == "neutral")

    # ----- spacing -----
    pxs = sorted(spacing_px.items())
    total_px = sum(n for _, n in pxs) or 1
    base_fit = {b: round(sum(n for px, n in pxs if px % b == 0) / total_px, 2) for b in GRID_BASES}
    scale_guess = next((f"{b}px grid" for b in GRID_BASES if base_fit[b] >= GRID_MIN_FIT), "no strict grid")

    # ----- breakpoints -----
    bps: Counter = Counter()
    ctx_counter: Counter = Counter()
    for r in rules:
        for c in r["ctx"]:
            ctx_counter[c.split()[0]] += 1
            for kind, dim, val, unit in re.findall(r"\(\s*(min|max)-(width|height)\s*:\s*([\d.]+)(px|rem|em)", c):
                px = float(val) * (16 if unit != "px" else 1)
                bps[(kind, dim, fmt_num(px))] += 1
    bp_rows = [{"query": f"{k}-{d}", "px": int(float(v)), "rules": n} for (k, d, v), n in sorted(bps.items(), key=lambda kv: (kv[0][1], float(kv[0][2]), kv[0][0]))]

    # ----- type ramp -----
    def px_of(k):
        m = re.match(r"^(-?[\d.]+)px$", k)
        return float(m.group(1)) if m else -1
    ramp_rows = [{"size": k[0], "weight": k[1], "line_height": k[2], "letter_spacing": k[3], "family": k[4],
                  "transform": k[5], "rules": v["count"], "examples": v["selectors"]} for k, v in type_rows.items()]
    ramp_rows.sort(key=lambda r: (-px_of(r["size"]), r["size"]))
    families_used = []
    for stack, n in fonts.most_common(10):
        families_used.append({"stack": stack, "uses": n})
    faces = []
    for ff in sheet.fontfaces:
        d = ff["decls"]
        files = re.findall(r"url\(\s*[\"']?([^)\"']+)", d.get("src", ""))
        faces.append({"family": d.get("font-family", "").strip("\"' "), "weight": d.get("font-weight", ""),
                      "style": d.get("font-style", ""), "stretch": d.get("font-stretch", ""),
                      "display": d.get("font-display", ""), "files": files, "src": ff["src"],
                      "variation": d.get("font-variation-settings", "")})

    mod_feats = {p: props[p] for p in MODERN_PROPS if props.get(p)}
    scale_tokens = {t: v for t, v in spacing_tok.items()}

    def tok_rows(counter, n):
        rows = []
        for tok, c in counter.most_common(n):
            res_v = scale_tokens.get(tok, tok)
            px = to_px(res_v)
            rows.append({"token": tok, "resolved": res_v if res_v != tok else "", "px": fmt_num(px) if px is not None else "", "uses": c})
        return rows

    return {
        "stats": {"rules": len(rules), "declarations": sum(props.values()), "unique_colors": len(colors),
                  "neutral_colors": neutral, "variables": len(var_entries), "fontfaces": len(faces),
                  "keyframes": len(sheet.keyframes), "at_rules": dict(ctx_counter)},
        "colors": {"in_use": in_use[:top * 2], "roles": roles_out,
                   "ramps": {p: {n: [{"step": s, "value": v} for s, v in steps] for n, steps in d.items()} for p, d in ramps.items()},
                   "single_variables": [v for v in singles if v["is_color"]]},
        "variables": {"scales": fam_out, "other": [v for v in singles if not v["is_color"]],
                      "scoped": scoped[:15], "responsive": [v for v in var_entries if v["overrides"]]},
        "typography": {"fonts": faces, "families_used": families_used,
                       "sizes": [{"px": k, "uses": n, "source": size_raw.get(k, "")} for k, n in sorted(sizes.items(), key=lambda kv: -px_of(kv[0]))],
                       "ramp": ramp_rows[:40], "weights": _top(weights, 10), "line_heights": _top(line_heights, 12),
                       "letter_spacing": _top(letter_sp, 10), "text_transform": _top(transforms, 5),
                       "tag_styles": {k: v for k, v in tag_styles.items()}},
        "spacing": {"tokens": tok_rows(spacing_raw, top), "px_values": [{"px": fmt_num(px), "uses": n} for px, n in pxs[:25]],
                    "grid_fit": base_fit, "scale_guess": scale_guess},
        "radius": tok_rows(radius_raw, 12),
        "borders": _top(borders, 10),
        "shadows": [{"type": t, "value": v, "uses": n} for (t, v), n in shadows.most_common(10)],
        "gradients": _top(gradients, 8),
        "opacity": _top(opacity, 8),
        "z_index": sorted(((int(k), n) for k, n in z_index.items() if re.fullmatch(r"-?\d+", k))),
        "motion": {"durations": _top(durations, 10), "easings": _top(easings, 10), "transition_properties": _top(trans_props, 10),
                   "keyframes": [k["name"] for k in sheet.keyframes][:20], "animation_names": _top(anim_names, 10),
                   "reduced_motion_rules": sum(1 for r in rules if any("prefers-reduced-motion" in c for c in r["ctx"]))},
        "breakpoints": bp_rows,
        "layout": {"display": _top(display, 8), "position": _top(position, 6), "flex_direction": _top(direction, 4),
                   "grid_template_columns": _top(grid_cols, 8), "max_widths": _top(max_w, 8),
                   "modern_properties": mod_feats, "selector_features": dict(selector_feats.most_common())},
        "themes": {"color_scheme": _top(color_scheme, 4), "override_scopes": override_scopes[:12], "override_scope_count": len(override_scopes),
                   "prefers_color_scheme_rules": sum(1 for r in rules if any("prefers-color-scheme" in c for c in r["ctx"]))},
        "units": _top(units, 10),
    }


# ---------- markdown ----------

def _tbl(headers: list[str], rows: list[list]) -> str:
    if not rows:
        return "_none_\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |")
    return "\n".join(out) + "\n"


def render_tokens_md(t: dict, meta: dict) -> str:
    L: list[str] = []
    s = t["stats"]
    L += [f"# Design system: {meta.get('host', '')}", "",
          f"Source: {meta.get('url', '')}  ", f"Analysed {s['rules']:,} CSS rules / {s['declarations']:,} declarations from "
          f"{meta.get('css_sources', '?')} stylesheet source(s) (see `css.dump`).", ""]

    # summary
    th = t["themes"]
    scheme = th["color_scheme"][0][0] if th["color_scheme"] else ("light/dark via media query" if th["prefers_color_scheme_rules"] else "not declared")
    def _plain(v):
        return v.split("->")[-1].strip() if v else ""
    ts = t["typography"]["tag_styles"]
    body_font = _plain(ts.get("body", {}).get("font-family") or ts.get("html", {}).get("font-family", ""))
    code_font = _plain(ts.get("code", {}).get("font-family", ""))
    fam = body_font or (t["typography"]["families_used"][0]["stack"] if t["typography"]["families_used"] else "n/a")
    sz = [float(x["px"][:-2]) for x in t["typography"]["sizes"] if x["px"].endswith("px")]
    L += ["## Summary", ""]
    L += [f"- **Color scheme:** {scheme}; variable-override scopes (themes/variants): {th['override_scope_count']}; `prefers-color-scheme` rules: {th['prefers_color_scheme_rules']}",
          f"- **Colors:** {s['unique_colors']} distinct in use ({s['neutral_colors']} neutral); {sum(len(d) for d in t['colors']['ramps'].values())} ramps defined as variables",
          f"- **Variables:** {s['variables']} custom properties; {len(t['variables']['scales'])} named scales",
          f"- **Body font:** `{fam[:90]}`" + (f"; **code font:** `{code_font[:60]}`" if code_font else ""),
          f"- **Font sizes in use:** {len(sz)} distinct" + (f" ({fmt_num(min(sz))}px to {fmt_num(max(sz))}px)" if sz else ""),
          f"- **Spacing:** {t['spacing']['scale_guess']} (fit 8px: {t['spacing']['grid_fit'][8]:.0%}, 4px: {t['spacing']['grid_fit'][4]:.0%})",
          "- **Breakpoints:** " + (", ".join(sorted({f"{b['px']}px" for b in t['breakpoints'] if b['query'].endswith('width')}, key=lambda x: int(x[:-2]))) or "none"),
          "- **Units:** " + ", ".join(f"{u} x{n}" for u, n in t["units"][:6]), ""]

    # colours
    L += ["## Colors", ""]
    for prefix, d in t["colors"]["ramps"].items():
        L += [f"### Palette ramps `{prefix}-<name>-<step>`  ({len(d)} ramps)", ""]
        steps = max(len(v) for v in d.values())
        L.append(_tbl(["ramp"] + [f"{i}" for i in range(1, steps + 1)], [[n] + [x["value"] for x in v] for n, v in d.items()]))
    if t["colors"]["single_variables"]:
        L += ["### Color variables (not part of a ramp)", ""]
        L.append(_tbl(["variable", "value", "uses"], [[v["name"], v["resolved"], v["uses"]] for v in sorted(t["colors"]["single_variables"], key=lambda v: -v["uses"])[:30]]))
    L += ["### Colors in use (resolved through variables)", ""]
    L.append(_tbl(["color", "uses", "kind", "hue/sat/light", "roles"], [
        [c["hex"], c["count"], c.get("kind", "fn"), f"{c.get('h','')}/{c.get('s','')}/{c.get('l','')}" if c.get("kind") else "",
         ", ".join(f"{k} {v}" for k, v in c["roles"].items())] for c in t["colors"]["in_use"][:30]]))
    if t["colors"]["roles"]:
        L += ["### Which tokens are used for what", ""]
        for role, rows in t["colors"]["roles"].items():
            L.append(f"- **{role}:** " + ", ".join(f"`{r['token']}` ({r['value']}) x{r['count']}" for r in rows[:8]))
        L.append("")

    # variables
    L += ["## Variables (tokens)", ""]
    for f in t["variables"]["scales"]:
        L += [f"### `{f['family']}-*`", ""]
        has_over = any(m["overrides"] for m in f["members"])
        if has_over:
            octx = sorted({c for m in f["members"] for c in m["overrides"]})
            L.append(_tbl(["name", "base"] + octx + ["uses"], [[m["name"], m["value"]] + [m["overrides"].get(c, "") for c in octx] + [m["uses"]] for m in f["members"]]))
        else:
            L.append(_tbl(["name", "value", "uses"], [[m["name"], m["value"], m["uses"]] for m in f["members"]]))
    if t["variables"]["other"]:
        L += ["### Other variables", ""]
        L.append(_tbl(["name", "value", "uses"], [[v["name"], v["resolved"][:70], v["uses"]] for v in sorted(t["variables"]["other"], key=lambda v: -v["uses"])[:40]]))
    if t["variables"]["scoped"]:
        L += ["### Context-switching variables (set on selectors other than :root)", "",
              "These re-point a variable family per context (e.g. an accent colour per section/component class), a common theming mechanism:", ""]
        L.append(_tbl(["variable family", "selectors that set it", "examples"], [[s_["family"] + "-*", s_["selectors"], "; ".join(s_["examples"])] for s_ in t["variables"]["scoped"][:10]]))

    # typography
    if t["themes"]["override_scopes"]:
        L += ["### Variable-override scopes (themes and variants)", "",
              "Detected structurally: each selector below re-defines most of the variables the root defines, so it switches the look "
              "(dark mode, a theme class, a data attribute) whatever it is called.", ""]
        L.append(_tbl(["selector", "context", "variables", "overlap with root"], [
            [f"`{x['selector']}`", x["context"], x["variables"], f"{x['overlap']:.0%}"] for x in t["themes"]["override_scopes"]]))
    ty = t["typography"]
    L += ["## Typography", "", "### Font faces (@font-face)", ""]
    L.append(_tbl(["family", "weight", "style", "stretch", "display", "files"], [[f["family"], f["weight"], f["style"], f["stretch"], f["display"], ", ".join(f["files"])] for f in ty["fonts"]]))
    L += ["### Font stacks in use", ""]
    L.append(_tbl(["stack", "uses"], [[f["stack"][:100], f["uses"]] for f in ty["families_used"]]))
    L += ["### Type scale (distinct font-size values)", "",
          "Sizes are resolved with the base (mobile-first) variable values; breakpoint overrides of the size variables are listed under Variables.", ""]
    L.append(_tbl(["size", "uses", "authored as"], [[x["px"], x["uses"], x["source"][:40]] for x in ty["sizes"]]))
    L += ["### Type styles (rules that set a font-size)", ""]
    L.append(_tbl(["size", "weight", "line-height", "letter-spacing", "family", "transform", "example selectors"], [
        [r["size"], r["weight"], r["line_height"], r["letter_spacing"], r["family"], r["transform"], "; ".join(r["examples"])[:80]] for r in ty["ramp"][:25]]))
    if ty["tag_styles"]:
        L += ["### Base element styles", ""]
        for tag, d in ty["tag_styles"].items():
            L.append(f"- `{tag}`: " + "; ".join(f"{k}: {v}" for k, v in d.items()))
        L.append("")
    L.append("**Weights:** " + ", ".join(f"{w} x{n}" for w, n in ty["weights"]) + "  ")
    L.append("**Line heights:** " + ", ".join(f"{w} x{n}" for w, n in ty["line_heights"]) + "  ")
    L.append("**Letter spacing:** " + ", ".join(f"{w} x{n}" for w, n in ty["letter_spacing"]) + "  ")
    L.append("**Text transform:** " + ", ".join(f"{w} x{n}" for w, n in ty["text_transform"]) + "\n")

    # spacing etc.
    L += ["## Spacing", ""]
    L.append(_tbl(["token / value", "resolves to", "px", "uses"], [[r["token"], r["resolved"], r["px"], r["uses"]] for r in t["spacing"]["tokens"]]))
    L.append("Literal px values (all sources): " + ", ".join(f"{x['px']}px x{x['uses']}" for x in t["spacing"]["px_values"][:18]) + "\n")
    L += ["## Radius", ""]
    L.append(_tbl(["token / value", "resolves to", "px", "uses"], [[r["token"], r["resolved"], r["px"], r["uses"]] for r in t["radius"]]))
    L += ["## Borders", ""]
    L.append(_tbl(["value", "uses"], [[v, n] for v, n in t["borders"]]))
    L += ["## Shadows and effects", ""]
    L.append(_tbl(["type", "value", "uses"], [[s_["type"], s_["value"][:90], s_["uses"]] for s_ in t["shadows"]]))
    if t["gradients"]:
        L += ["### Gradients", ""]
        L.append(_tbl(["value", "uses"], [[g[:110], n] for g, n in t["gradients"]]))
    if t["z_index"]:
        L.append("**z-index scale:** " + ", ".join(f"{z}" for z, _ in t["z_index"]) + "\n")
    if t["opacity"]:
        L.append("**Opacity values:** " + ", ".join(f"{v} x{n}" for v, n in t["opacity"]) + "\n")

    m = t["motion"]
    L += ["## Motion", "",
          "- **Durations:** " + (", ".join(f"{d} x{n}" for d, n in m["durations"]) or "none"),
          "- **Easings:** " + (", ".join(f"`{e}` x{n}" for e, n in m["easings"]) or "none"),
          "- **Transitioned properties:** " + (", ".join(f"{p} x{n}" for p, n in m["transition_properties"]) or "none"),
          f"- **@keyframes:** {', '.join(m['keyframes']) or 'none'}; `prefers-reduced-motion` rules: {m['reduced_motion_rules']}", ""]

    L += ["## Breakpoints and layout", ""]
    L.append(_tbl(["query", "px", "rules"], [[b["query"], b["px"], b["rules"]] for b in t["breakpoints"]]))
    lay = t["layout"]
    L += ["- **display:** " + ", ".join(f"{d} x{n}" for d, n in lay["display"]),
          "- **position:** " + ", ".join(f"{d} x{n}" for d, n in lay["position"]),
          "- **flex-direction:** " + ", ".join(f"{d} x{n}" for d, n in lay["flex_direction"]),
          "- **grid-template-columns:** " + (", ".join(f"`{d}` x{n}" for d, n in lay["grid_template_columns"]) or "none"),
          "- **max-width values:** " + (", ".join(f"{d} x{n}" for d, n in lay["max_widths"]) or "none"),
          "- **Modern CSS in use:** " + (", ".join(f"{p} x{n}" for p, n in lay["modern_properties"].items()) or "none"),
          "- **Selector features:** " + (", ".join(f"{p} x{n}" for p, n in lay["selector_features"].items()) or "none"), ""]
    L += ["---", "Notes: values are resolved through `var()` chains using the `:root`/`html` definition; px values assume 1rem = 16px. "
          "Raw sources are in `css.dump`; machine-readable data is in `design-tokens.json`.", ""]
    return "\n".join(L)
