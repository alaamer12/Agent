"""HTML structure/pattern analysis for `design patterns` (stdlib only)."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from html.parser import HTMLParser

from _techdetect import detect as detect_tech
from _techdetect import render_tech_md


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
AUTOCLOSE = {"li", "dt", "dd", "option", "tr", "td", "th", "p"}
SKIP = {"script", "style", "noscript", "template", "link", "meta", "head", "title", "base"}
# Heuristic parameters (thresholds, not vocabularies); named so they are visible and tunable in one place.
MAX_TREE_DEPTH = 512            # like browsers: elements nested deeper are attached at this depth (protects recursion)
BEM_MIN_SHARE = 0.25            # share of class names using __ / -- to call the naming BEM-style
ATOMIC_RULE_MAX_DECLS = 2       # a rule with at most this many declarations is "atomic"
ATOMIC_CLASS_MIN_SHARE = 0.8    # share of a class's rules that must be atomic for the class to count as atomic
MIN_STYLED_CLASSES = 10         # styled classes needed before utility-first can be judged at all
UTILITY_MIN_SHARE = 0.35        # atomic-class share (with >= 3 classes per element) that means utility-first
UTILITY_LAYER_MIN_SHARE = 0.12  # atomic-class share that means "semantic classes plus a utility layer"
WRAPPER_MIN_PX = 600            # max-width at or above this makes a rule a page-wrapper candidate
PX_PER_UNIT = {"px": 1, "rem": 16, "em": 16, "ch": 8}      # approximate unit conversion for that comparison
COMPOUND_CLASSES = re.compile(r"(?:\.(?:\\.|[\w-])+){2,}")   # .a.b.c chains inside a selector


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "text", "depth", "in_svg")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.parent = tag, attrs or {}, parent
        self.depth = parent.depth + 1 if parent is not None else 0
        self.in_svg = tag == "svg" or (parent is not None and parent.in_svg)     # computed once, not per query
        self.children: list[Node] = []
        self.text: list[str] = []

    @property
    def cls(self) -> list[str]:
        return self.attrs.get("class", "").split()

    def walk(self):
        """Pre-order traversal, iterative (no recursion limit on deep documents)."""
        stack = [self]
        while stack:
            n = stack.pop()
            yield n
            stack.extend(reversed(n.children))

    def all_text(self) -> str:
        """Visible text of the subtree in document order, skipping script/style (iterative)."""
        parts, stack = [], [self]
        while stack:
            n = stack.pop()
            if n.tag in ("script", "style"):
                continue
            parts.extend(n.text)
            stack.extend(reversed(n.children))
        return re.sub(r"\s+", " ", " ".join(parts)).strip()


class _Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root
        self.comments: list[str] = []

    def _add(self, tag, attrs):
        if tag in AUTOCLOSE and self.cur.tag == tag and self.cur.parent:
            self.cur = self.cur.parent
        n = Node(tag, {k: (v if v is not None else "") for k, v in attrs}, self.cur)
        self.cur.children.append(n)
        return n

    def handle_starttag(self, tag, attrs):
        n = self._add(tag, attrs)
        if tag not in VOID and n.depth < MAX_TREE_DEPTH:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self._add(tag, attrs)

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.text.append(data)

    def handle_comment(self, data):
        if len(self.comments) < 400:
            self.comments.append(data)


def parse_html_full(html: str) -> tuple[Node, list[str]]:
    """-> (tree, HTML comments). Comments carry generator/version hints and framework markers."""
    b = _Builder()
    b.feed(html)
    b.close()
    return b.root, b.comments


def parse_html(html: str) -> Node:
    return parse_html_full(html)[0]


def find(root: Node, tag: str) -> Node | None:
    return next((n for n in root.walk() if n.tag == tag), None)


def extract_inline_css(root: Node) -> tuple[list[str], list[tuple[str, str]]]:
    blocks = ["".join(n.text) for n in root.walk() if n.tag == "style" and "".join(n.text).strip()]
    attrs = []
    for n in root.walk():
        if n.attrs.get("style", "").strip() and n.tag not in ("svg",):
            label = n.tag + ("".join("." + c for c in n.cls[:2]))
            attrs.append((label, n.attrs["style"]))
    return blocks, attrs


# ---------- serialization helpers ----------

def _short(v: str, n: int = 60) -> str:
    v = re.sub(r"\s+", " ", v)
    return v if len(v) <= n else v[:n - 1] + "…"


def render_node(n: Node, keep_text=False, depth=3, indent=0, max_kids=8) -> str:
    pad = "  " * indent
    keep = []
    for k, v in n.attrs.items():
        if k in ("id", "class", "role", "type", "name", "for", "rel", "target", "aria-label", "lang") or k.startswith(("data-", "aria-")) or k in ("href", "src", "alt", "placeholder"):
            if k in ("href", "src"):
                v = re.sub(r"\?.*$", "", v)
            if k == "alt" and not keep_text:
                v = "…"
            keep.append(f'{k}="{_short(v, 70)}"' if v != "" else k)
        elif k == "style":
            keep.append('style="…"')
        elif k not in ("srcset", "sizes", "d", "points", "viewbox", "xmlns", "width", "height"):
            continue
    attrs = (" " + " ".join(keep[:9])) if keep else ""
    if n.tag in VOID:
        return f"{pad}<{n.tag}{attrs}>"
    if n.tag == "svg":
        return f"{pad}<svg{attrs}>…</svg>"
    kids = [c for c in n.children if c.tag not in ("script", "style")]
    own = " ".join(" ".join(n.text).split())
    txt = (_short(own, 40) if keep_text else "…") if own else ""
    if not kids or depth <= 0:
        inner = txt or ("…" if kids else "")
        return f"{pad}<{n.tag}{attrs}>{inner}</{n.tag}>"
    lines = [f"{pad}<{n.tag}{attrs}>"]
    if txt:
        lines.append(f"{pad}  {txt}")
    shown = kids[:max_kids]
    for c in shown:
        lines.append(render_node(c, keep_text, depth - 1, indent + 1, max_kids))
    if len(kids) > len(shown):
        lines.append(f"{pad}  <!-- +{len(kids) - len(shown)} more -->")
    lines.append(f"{pad}</{n.tag}>")
    return "\n".join(lines)


def label(n: Node, ncls: int = 3) -> str:
    s = n.tag
    if n.attrs.get("id"):
        s += "#" + n.attrs["id"]
    if n.cls:
        s += "." + ".".join(n.cls[:ncls])
    for k in ("role", "size", "data-color", "boxed"):
        if k in n.attrs:
            s += f'[{k}{"=" + n.attrs[k] if n.attrs[k] else ""}]'
    return s


def sig(n: Node, depth: int = 2) -> str:
    base = n.tag + ("." + ".".join(sorted(n.cls)[:3]) if n.cls else "")
    kids = [c for c in n.children if c.tag not in SKIP]
    if depth <= 0 or not kids or n.tag == "svg":
        return base
    out: list[list] = []
    for c in kids[:10]:
        k = sig(c, depth - 1)
        if out and out[-1][0] == k:
            out[-1][1] += 1
        else:
            out.append([k, 1])
    return f"{base}({','.join(k if c == 1 else f'{k}x{c}' for k, c in out)})"


def size_of(n: Node) -> int:
    return sum(1 for _ in n.walk())


# ---------- CSS lookup ----------

CLASS_TOKEN = re.compile(r"\.((?:\\.|[\w-])+)")


def _unescape(s: str) -> str:
    return re.sub(r"\\(.)", r"\1", s)


class CssIndex:
    def __init__(self, rules):
        self.rules = rules
        self.by_class: dict[str, list[int]] = defaultdict(list)
        self.by_tag: dict[str, list[int]] = defaultdict(list)
        self.sel_classes: list[set] = []     # unescaped class names per rule (md\\:flex -> md:flex)
        for i, r in enumerate(rules):
            classes = {_unescape(t) for t in CLASS_TOKEN.findall(r["sel"]) if re.match(r"^-?[_a-zA-Z\\]", t)}
            self.sel_classes.append(classes)
            for c in classes:
                self.by_class[c].append(i)
            for t in set(re.findall(r"(?<![\w.#\[:-])([a-z][a-z0-9]*-[a-z0-9-]+)(?![\w-])", r["sel"])):
                self.by_tag[t].append(i)

    def summarize(self, idxs, limit=6, max_decls=12):
        out = []
        for i in idxs[:limit]:
            r = self.rules[i]
            decls = [f"{p}: {_short(v, 50)}" for p, v, _ in r["decls"]][:max_decls]
            out.append({"selector": _short(r["sel"], 90), "context": " & ".join(c.replace("@media ", "") for c in r["ctx"]), "declarations": decls})
        return out

    def first_rule_with(self, cls: str, prop: str):
        for i in self.by_class.get(cls, []):
            r = self.rules[i]
            if not r["ctx"] and cls in self.sel_classes[i]:
                d = {p: v for p, v, _ in r["decls"]}
                if prop in d:
                    return d
        return None


# ---------- analysis ----------

def analyze_patterns(html: str, rules: list, base_url: str = "", keep_text: bool = False, top: int = 12,
                     headers: dict | None = None, css_text: str = "", css_banners: list | None = None,
                     signatures_file: str | None = None) -> dict:
    root, comments = parse_html_full(html)
    htmln, head, body = find(root, "html"), find(root, "head"), find(root, "body") or root
    css = CssIndex(rules)
    nodes = [n for n in body.walk() if n.tag not in SKIP and n.tag != "#root"]     # #root is the parser's wrapper, not an element

    # head
    metas = {}
    for n in (head.walk() if head else []):
        if n.tag == "meta":
            k = n.attrs.get("name") or n.attrs.get("property") or ("charset" if "charset" in n.attrs else "")
            if k:
                metas[k] = n.attrs.get("content", n.attrs.get("charset", ""))
    links = [n.attrs for n in root.walk() if n.tag == "link"]
    scripts = []
    for n in root.walk():
        if n.tag == "script":
            inline = "".join(n.text)
            scripts.append({"src": n.attrs.get("src", ""), "type": n.attrs.get("type", ""), "async": "async" in n.attrs,
                            "defer": "defer" in n.attrs, "inline_bytes": len(inline.encode()) if not n.attrs.get("src") else 0})
    tech = detect_tech(root, comments, headers or {}, css_text, css_banners or [], base_url, signatures_file)

    # outline and sections
    def outline(n, d, maxd=4, maxk=9):
        lines = []
        kids = [c for c in n.children if c.tag not in SKIP]
        groups: list[list] = []
        for c in kids:
            k = (label(c), sig(c, 1))
            if groups and groups[-1][0] == k:
                groups[-1][1] += 1
            else:
                groups.append([k, 1, c])
        for _k, count, c in groups[:maxk]:
            extra = ""
            if re.fullmatch(r"h[1-6]", c.tag):
                t = c.all_text()
                extra = f'  "{_short(t, 40)}"' if t else ""
            nk = len([x for x in c.children if x.tag not in SKIP])
            lines.append("  " * d + label(c) + (f"  x{count}" if count > 1 else "") + (f"  ({nk} children)" if nk and d + 1 >= maxd else "") + extra)
            if d + 1 < maxd and c.tag != "svg":
                lines += outline(c, d + 1, maxd, maxk)
        if len(groups) > maxk:
            lines.append("  " * d + f"... +{len(groups) - maxk} more blocks")
        return lines

    outline_lines = outline(body, 0)
    main = find(body, "main")
    top_kids = [c for c in (main or body).children if c.tag not in SKIP]
    sections, sections_skipped = [], 0
    for c in top_kids:
        sub = list(c.walk())
        if len(sub) == 1 and not c.text:
            sections_skipped += 1          # empty spacer/placeholder elements
            continue
        cnt = Counter(x.tag for x in sub)
        h = next((x for x in sub if re.fullmatch(r"h[1-6]", x.tag)), None)
        classes_here = [k for k in c.cls]
        lay = {}
        for k in classes_here:
            for p in ("display", "flex-direction", "grid-template-columns", "gap", "max-width"):
                r = css.first_rule_with(k, p)
                if r and p in r:
                    lay[p] = _short(r[p], 40)
        sections.append({"element": label(c), "heading": (_short(h.all_text(), 40) if h and h.all_text() else ""),
                         "heading_tag": h.tag if h else "", "counts": {k: cnt[k] for k in ("a", "button", "img", "svg", "canvas", "video", "p", "li", "input", "form") if cnt[k]},
                         "descendants": len(sub) - 1, "children": [sig(x, 1) for x in c.children if x.tag not in SKIP][:6], "layout": lay})

    # tag/semantic stats
    tag_counts = Counter(n.tag for n in nodes)
    semantic = {t: tag_counts[t] for t in ("header", "nav", "main", "section", "article", "aside", "footer", "figure", "form", "ul", "ol", "table", "button", "dialog", "details") if tag_counts[t]}
    headings = [n.tag for n in nodes if re.fullmatch(r"h[1-6]", n.tag)]

    # classes
    class_ctr = Counter(c for n in nodes for c in n.cls)
    with_cls = [n for n in nodes if n.cls]
    avg_cls = round(sum(len(n.cls) for n in with_cls) / max(1, len(with_cls)), 2)
    names = list(class_ctr)
    bem = sum(1 for c in names if "__" in c or re.search(r"[a-z0-9]--[a-z0-9]", c)) / max(1, len(names))
    # Utility/atomic CSS is measured on the stylesheet, not guessed from class names: a class is "atomic" when
    # (nearly) all of its rules set at most two declarations. None = no stylesheet rules to judge from.
    styled_names = [c for c in names if c in css.by_class]

    def is_atomic(c):
        sizes = [len(css.rules[i]["decls"]) for i in css.by_class[c]]
        return sum(1 for n_ in sizes if n_ <= ATOMIC_RULE_MAX_DECLS) / len(sizes) >= ATOMIC_CLASS_MIN_SHARE

    util = (sum(1 for c in styled_names if is_atomic(c)) / len(styled_names)) if len(styled_names) >= MIN_STYLED_CLASSES else None
    prefixes = Counter(c.split("-")[0] for c in names if "-" in c)
    # State/modifier classes, found structurally: classes CSS uses as an extra class in a compound selector
    # (".menu.is-open") that never appear in the served HTML are toggled at runtime by JavaScript.
    html_classes = set(names)
    modifiers: Counter = Counter()
    for r in rules:
        for chain in COMPOUND_CLASSES.findall(r["sel"]):
            for t_ in [_unescape(x) for x in CLASS_TOKEN.findall(chain)][1:]:
                modifiers[t_] += 1
    states = [c for c, _ in modifiers.most_common() if c not in html_classes]
    if bem >= BEM_MIN_SHARE:
        verdict = "BEM-style (block__element--modifier)"
    elif util is not None and util >= UTILITY_MIN_SHARE and avg_cls >= 3:
        verdict = "utility-first / atomic CSS (many classes per element, each style rule tiny)"
    elif util is not None and util >= UTILITY_LAYER_MIN_SHARE:
        verdict = "semantic component classes plus a utility layer"
    else:
        verdict = "semantic / hand-written component classes"

    # components
    groups: dict[str, list[Node]] = defaultdict(list)
    for n in nodes:
        if n.tag in ("html", "body", "svg", "path", "span", "br") or n.in_svg:
            continue
        kids = [c for c in n.children if c.tag not in SKIP]
        if len(kids) == 0 and not n.cls:
            continue
        groups[sig(n, 2)].append(n)
    cand = [(s, ms) for s, ms in groups.items() if len(ms) >= 3 and (ms[0].cls or len([c for c in ms[0].children if c.tag not in SKIP]) >= 1)]
    cand.sort(key=lambda sm: -(len(sm[1]) * size_of(sm[1][0]) ** 0.5))
    covered: set[int] = set()
    comps = []
    for s, ms in cand:
        if sum(1 for m in ms if id(m) in covered) > len(ms) / 2:
            continue
        ex = ms[0]
        classes = []
        for x in ex.walk():
            for c in x.cls:
                if c not in classes:
                    classes.append(c)
        styled = [c for c in classes if c in css.by_class]
        rules_for = {c: css.summarize(css.by_class[c], limit=4, max_decls=10) for c in styled[:5]}
        for m in ms:
            for x in m.walk():
                covered.add(id(x))
        comps.append({"name": ex.cls[0] if ex.cls else ex.tag, "signature": _short(s, 160), "count": len(ms),
                      "parent": label(ex.parent) if ex.parent and ex.parent.tag != "#root" else "",
                      "classes": classes[:12], "exemplar": render_node(ex, keep_text, depth=3), "css": rules_for})
        if len(comps) >= top:
            break

    # custom elements
    custom = {}
    for n in nodes:
        if "-" in n.tag and re.fullmatch(r"[a-z][a-z0-9]*(-[a-z0-9]+)+", n.tag):
            d = custom.setdefault(n.tag, {"count": 0, "attrs": {}, "css_rules": len(css.by_tag.get(n.tag, []))})
            d["count"] += 1
            for k, v in n.attrs.items():
                if k != "class":
                    d["attrs"].setdefault(k, set()).add(_short(v, 20))
    custom_out = {t: {"count": d["count"], "css_rules": d["css_rules"], "attributes": {k: sorted(v)[:4] for k, v in d["attrs"].items()}} for t, d in custom.items()}

    # attribute-driven variants and hooks
    attr_sel = Counter()
    attr_vals: dict[str, list] = defaultdict(list)
    for r in rules:
        for a, op, v in re.findall(r"\[\s*([\w-]+)\s*([~|^$*]?=)?\s*[\"']?([^\"'\]\s]*)", r["sel"]):
            if a not in ("href", "type", "target", "disabled", "value", "src", "alt", "class", "stroke", "fill", "placeholder", "name", "for", "role", "tabindex", "hidden"):
                attr_sel[a] += 1
                if op and v not in attr_vals[a]:
                    attr_vals[a].append(v)
    data_attrs, aria_attrs, roles = Counter(), Counter(), Counter()
    data_samples: dict[str, set] = defaultdict(set)
    for n in nodes:
        for k, v in n.attrs.items():
            if k.startswith("data-"):
                data_attrs[k] += 1
                if len(data_samples[k]) < 3:
                    data_samples[k].add(_short(v, 24))
            elif k.startswith("aria-"):
                aria_attrs[k] += 1
        if "role" in n.attrs:
            roles[n.attrs["role"]] += 1
    ids = [n.attrs["id"] for n in nodes if n.attrs.get("id") and not n.in_svg]
    css_text_ids = Counter(i for r in rules for i in re.findall(r"#([\w-]+)", r["sel"]))

    # layout recipes for classes that appear in the HTML
    recipes = []
    for c, cnt in class_ctr.most_common(60):
        d = None
        for i in css.by_class.get(c, []):
            r = css.rules[i]
            if not r["ctx"] and c in css.sel_classes[i] and any(p == "display" and v in ("flex", "grid", "inline-flex", "inline-grid") for p, v, _ in r["decls"]):
                d = {p: v for p, v, _ in r["decls"]}
                break
        if d:
            recipes.append({"class": c, "used": cnt, **{k: _short(d[k], 50) for k in ("display", "flex-direction", "flex-wrap", "justify-content", "align-items", "gap", "grid-template-columns", "width", "max-width") if k in d}})
    wrappers = []
    for r in rules:
        d = {p: v for p, v, _ in r["decls"]}
        mw = re.match(r"^([\d.]+)(px|rem|em|ch)$", d.get("max-width", ""))
        wide = bool(mw) and float(mw.group(1)) * PX_PER_UNIT[mw.group(2)] >= WRAPPER_MIN_PX
        if wide and re.match(r"^\.[\w-]+$", r["sel"].strip()) and not r["ctx"] and (d.get("width") == "100%" or "auto" in d.get("margin", "") or "auto" in d.get("margin-inline", "")):
            wrappers.append({"selector": r["sel"], "max-width": d["max-width"], "width": d.get("width", ""), "margin": d.get("margin", d.get("margin-inline", "")), "padding": d.get("padding", "")})

    # media
    imgs = [n for n in nodes if n.tag == "img"]
    media = {"img": len(imgs), "img_with_alt": sum(1 for i in imgs if i.attrs.get("alt")), "img_empty_alt": sum(1 for i in imgs if i.attrs.get("alt", None) == ""),
             "img_lazy": sum(1 for i in imgs if i.attrs.get("loading") == "lazy"), "img_srcset": sum(1 for i in imgs if "srcset" in i.attrs),
             "img_sized": sum(1 for i in imgs if "width" in i.attrs and "height" in i.attrs),
             "picture": tag_counts["picture"], "svg_inline": len([n for n in body.walk() if n.tag == "svg"]), "svg_use": len([n for n in body.walk() if n.tag == "use"]),
             "canvas": tag_counts["canvas"], "video": tag_counts["video"], "audio": tag_counts["audio"], "iframe": tag_counts["iframe"]}
    bg_ext = Counter()
    for r in rules:
        for p, v, _ in r["decls"]:
            if p.startswith(("background", "mask", "-webkit-mask", "list-style")) and "url(" in v:
                for u in re.findall(r"url\(\s*[\"']?([^)\"']+)", v):
                    bg_ext[(re.search(r"\.(\w+)(?:\?|$)", u) or [None, "data" if u.startswith("data:") else "?"])[1].lower()] += 1
    forms = {"forms": tag_counts["form"], "inputs": dict(Counter(n.attrs.get("type", "text") for n in nodes if n.tag == "input")),
             "buttons": tag_counts["button"], "labels": tag_counts["label"], "selects": tag_counts["select"], "textareas": tag_counts["textarea"],
             "anchor_buttons": sum(1 for n in nodes if n.tag == "a" and any(re.search(r"btn|button", c) for c in n.cls))}

    return {
        "document": {"lang": (htmln.attrs.get("lang") if htmln else "") or "", "title": head and next((_short(n.all_text(), 80) for n in head.walk() if n.tag == "title"), ""),
                     "meta": {k: _short(v, 80) for k, v in metas.items() if k in ("charset", "viewport", "description", "theme-color", "color-scheme", "robots", "og:title", "og:image", "twitter:card")},
                     "meta_count": len(metas), "elements": len(nodes), "max_depth": max((n.depth - 1 for n in nodes), default=0)},
        "assets": {"stylesheets": [l.get("href", "") for l in links if "stylesheet" in l.get("rel", "")],
                   "preloads": [{k: l.get(k, "") for k in ("rel", "as", "href", "type")} for l in links if l.get("rel", "") in ("preload", "prefetch", "modulepreload", "preconnect")],
                   "icons": [l.get("href", "") for l in links if "icon" in l.get("rel", "")],
                   "scripts": scripts, "importmap": any(s["type"] == "importmap" for s in scripts),
                   "json_ld": sum(1 for s in scripts if "ld+json" in s["type"])},
        "tech": tech,
        "outline": outline_lines[:90], "sections": sections, "sections_skipped_empty": sections_skipped,
        "semantics": {"landmarks": semantic, "headings": dict(Counter(headings)), "h1_count": headings.count("h1")},
        "classes": {"distinct": len(names), "avg_per_element": avg_cls, "bem_share": round(bem, 2), "utility_share": None if util is None else round(util, 2),
                    "verdict": verdict, "prefixes": prefixes.most_common(10), "most_used": class_ctr.most_common(20), "state_classes": states[:20]},
        "components": comps, "custom_elements": custom_out,
        "hooks": {"data_attributes": [(k, n, sorted(data_samples[k])) for k, n in data_attrs.most_common(15)],
                  "aria": aria_attrs.most_common(10), "roles": roles.most_common(8),
                  "attribute_selectors": [{"attribute": a, "uses": n, "values": attr_vals[a][:8], "distinct_values": len(attr_vals[a])} for a, n in attr_sel.most_common(15)],
                  "ids": [(i, css_text_ids.get(i, 0)) for i in ids[:25]]},
        "layout": {"recipes": recipes[:15], "wrappers": wrappers[:8]},
        "media": {**media, "css_image_types": dict(bg_ext)}, "forms": forms,
    }


# ---------- markdown ----------

def _tbl(headers, rows):
    if not rows:
        return "_none_\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |")
    return "\n".join(out) + "\n"


def _tech_summary(tech: dict, limit: int = 8) -> str:
    """'Astro 4.0 (high), nginx (high), ...' from high/medium-confidence attributions."""
    items = [f"{i['name']}{' ' + i['version'] if i['version'] else ''} ({i['confidence']})" for i in tech["identified"] if i["confidence"] in ("high", "medium")]
    return ", ".join(items[:limit]) + (f" +{len(items) - limit} more" if len(items) > limit else "")


def render_patterns_md(p: dict, tokens: dict | None, meta: dict) -> str:
    L: list[str] = []
    d, a = p["document"], p["assets"]
    L += [f"# Design patterns: {meta.get('host', '')}", "", f"Source: {meta.get('url', '')}  ",
          f"Analysed {d['elements']:,} elements (max depth {d['max_depth']}); raw sources: `html.dump`, `css.dump`.", ""]
    L += ["## Overview", "",
          f"- **Class naming:** {p['classes']['verdict']} ({p['classes']['distinct']} distinct classes, {p['classes']['avg_per_element']} per classed element; BEM {p['classes']['bem_share']:.0%}, utility/atomic {'n/a (too few styled classes)' if p['classes']['utility_share'] is None else format(p['classes']['utility_share'], '.0%')})",
          "- **Landmarks:** " + (", ".join(f"{k} x{v}" for k, v in p["semantics"]["landmarks"].items()) or "none") + f"; h1 count {p['semantics']['h1_count']}",
          "- **Custom elements:** " + (", ".join(f"`<{t}>` x{v['count']}" for t, v in p["custom_elements"].items()) or "none"),
          "- **Technology (evidence-based):** " + (_tech_summary(p["tech"]) or "no signature matched (see Technology evidence for raw traces)") + (" (importmap)" if a["importmap"] else ""),
          f"- **Media:** {p['media']['img']} img, {p['media']['svg_inline']} inline svg, {p['media']['canvas']} canvas, {p['media']['video']} video, {p['media']['iframe']} iframe", ""]

    L += ["## Document skeleton", "", f"`<html lang=\"{d['lang']}\">`, title: {d['title']!r}", "", "Head meta: " + (", ".join(f"`{k}`" for k in d["meta"]) or "none"), "", "```text"]
    L += p["outline"] + ["```", ""]

    L += ["## Page sections (top level, in order)", ""]
    if p.get("sections_skipped_empty"):
        L += [f"_({p['sections_skipped_empty']} empty top-level spacer/placeholder element(s) omitted)_", ""]
    L.append(_tbl(["#", "element", "heading", "contains", "layout (from CSS)", "child blocks"], [
        [i + 1, f"`{s['element']}`", (f"{s['heading_tag']}: {s['heading']}" if s["heading"] else ""), ", ".join(f"{k} {v}" for k, v in s["counts"].items()),
         ", ".join(f"{k}: {v}" for k, v in s["layout"].items()), "; ".join(s["children"][:3])[:90]] for i, s in enumerate(p["sections"])]))

    L += ["## Head and assets", ""]
    L.append("**Stylesheets:** " + (", ".join(f"`{s}`" for s in a["stylesheets"]) or "none inline-only") + "  ")
    L.append("**Preloads/connections:** " + (", ".join(f"{x['rel']} {x['as']} `{x['href']}`".strip() for x in a["preloads"]) or "none") + "  ")
    L.append("**Icons:** " + (", ".join(f"`{i}`" for i in a["icons"]) or "none") + "\n")
    L.append(_tbl(["script", "type", "async", "defer", "inline bytes"], [[f"`{s['src']}`" if s["src"] else "(inline)", s["type"], s["async"], s["defer"], s["inline_bytes"]] for s in a["scripts"]]))

    L += render_tech_md(p["tech"])

    L += ["## Class conventions", ""]
    L.append("**Prefix families:** " + ", ".join(f"`{k}-` x{v}" for k, v in p["classes"]["prefixes"]) + "  ")
    L.append("**Most used classes:** " + ", ".join(f"`{k}` x{v}" for k, v in p["classes"]["most_used"][:14]) + "  ")
    L.append("**JS-toggled state classes (CSS modifiers absent from the served HTML):** " + (", ".join(f"`{s}`" for s in p["classes"]["state_classes"]) or "none") + "\n")

    L += ["## Repeated components (clone these first)", "", "CSS rules shared by several components are listed once, under the first component that uses them.", ""]
    seen_rules: set = set()
    for i, c in enumerate(p["components"], 1):
        L += [f"### {i}. `{c['name']}` x{c['count']}", "", f"- Structure: `{c['signature']}`", f"- Parent: `{c['parent'] or 'body'}`", "", "```html", c["exemplar"], "```", ""]
        for cls, rules in c["css"].items():
            for r in rules[:3]:
                key = (r["selector"], r["context"])
                if key in seen_rules:
                    continue
                seen_rules.add(key)
                ctx = f" @ {r['context']}" if r["context"] else ""
                L.append(f"- `{r['selector']}`{ctx}: " + "; ".join(r["declarations"][:8]))
        L.append("")

    if p["custom_elements"]:
        L += ["## Custom elements (web components)", ""]
        L.append(_tbl(["tag", "count", "CSS rules", "attributes (sample values)"], [[f"`<{t}>`", v["count"], v["css_rules"], "; ".join(f"{k}={'/'.join(vs)}" for k, vs in v["attributes"].items())[:110]] for t, v in p["custom_elements"].items()]))
        L.append("Their behaviour lives in JS (`customElements.define`); the HTML only carries the tag and attributes.\n")

    L += ["## Variants, hooks and state", ""]
    L.append("**Attribute selectors used for variants:** " + (", ".join(
        f"`[{x['attribute']}]` x{x['uses']}" + (f" (values: {', '.join(x['values'][:5])}{', ...' if x['distinct_values'] > 5 else ''})" if x["values"] else "")
        for x in p["hooks"]["attribute_selectors"][:10]) or "none") + "  ")
    L.append("**data-* attributes in HTML:** " + (", ".join(f"`{k}` x{n}" for k, n, _ in p["hooks"]["data_attributes"][:10]) or "none") + "  ")
    L.append("**ARIA:** " + (", ".join(f"`{k}` x{n}" for k, n in p["hooks"]["aria"][:8]) or "none") + "; **roles:** " + (", ".join(f"{k} x{n}" for k, n in p["hooks"]["roles"]) or "none") + "  ")
    L.append("**Ids (JS/anchor hooks, CSS references):** " + (", ".join(f"`#{i}`({n})" for i, n in p["hooks"]["ids"][:14]) or "none") + "\n")

    L += ["## Layout system", ""]
    if p["layout"]["wrappers"]:
        L += ["Wrappers (centered, max-width):", ""]
        L.append(_tbl(["selector", "max-width", "width", "margin", "padding"], [[f"`{w['selector']}`", w["max-width"], w["width"], w["margin"], w["padding"]] for w in p["layout"]["wrappers"]]))
    L += ["Flex/grid recipes for classes present in the HTML:", ""]
    keys = ["display", "flex-direction", "flex-wrap", "justify-content", "align-items", "gap", "grid-template-columns"]
    L.append(_tbl(["class", "used"] + keys, [[f"`{r['class']}`", r["used"]] + [r.get(k, "") for k in keys] for r in p["layout"]["recipes"]]))
    if tokens:
        bps = sorted({b["px"] for b in tokens["breakpoints"] if b["query"].endswith("width")})
        L.append("Breakpoints (px): " + (", ".join(map(str, bps)) or "none") + "\n")

    m, f = p["media"], p["forms"]
    L += ["## Media, icons, forms", "",
          f"- Images: {m['img']} (alt {m['img_with_alt']}, empty alt {m['img_empty_alt']}, lazy {m['img_lazy']}, srcset {m['img_srcset']}, width+height {m['img_sized']}); picture {m['picture']}",
          f"- Inline SVG {m['svg_inline']} (`<use>` {m['svg_use']}); CSS image types via url(): " + (", ".join(f"{k} x{v}" for k, v in m["css_image_types"].items()) or "none"),
          f"- Forms {f['forms']}; inputs {f['inputs']}; buttons {f['buttons']}; labels {f['labels']}; anchor-styled buttons {f['anchor_buttons']}", ""]

    L += ["## Clone checklist", "",
          f"1. Document shell: `lang=\"{d['lang']}\"`, meta " + ", ".join(f"`{k}`" for k in d["meta"]) + ".",
          "2. Load fonts and tokens first (see `design-system.md`); keep the same variable names so the component CSS below works unchanged.",
          "3. Build the wrappers/containers" + (f" (`{p['layout']['wrappers'][0]['selector']}` max-width {p['layout']['wrappers'][0]['max-width']})" if p["layout"]["wrappers"] else "") + ", then the sections in the order shown above.",
          f"4. Implement the {len(p['components'])} repeated components above (structure + CSS), then the custom elements" + (" (" + ", ".join(f"`<{t}>`" for t in p["custom_elements"]) + ")" if p["custom_elements"] else "") + ".",
          "5. Reproduce variants with the same attributes/classes (attribute selectors and state classes listed under Variants).",
          "6. Add scripts last" + (f" (technology hints: {_tech_summary(p['tech'])})" if _tech_summary(p["tech"]) else "") + "; behaviour (animation, interaction) is not in the HTML and must be taken from the scripts.",
          "7. Use `html.dump`/`css.dump` for exact markup/rules when a detail above is not enough.", ""]
    return "\n".join(L)
