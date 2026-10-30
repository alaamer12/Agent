"""Small dependency-free CSS parser plus colour/length helpers (used by `design`).

Handles minified CSS, nested at-rules (@media/@supports/@container/@layer/...), CSS nesting,
@font-face, @keyframes, @property and @import. Not a validator: it extracts what the
design-token and pattern analyzers need.
"""
from __future__ import annotations

import colorsys
import re

from _data import load_json

# ---------- low-level scanning ----------

def _skip_string(s: str, i: int) -> int:
    q = s[i]
    i += 1
    while i < len(s):
        if s[i] == "\\":
            i += 2
            continue
        if s[i] == q:
            return i + 1
        i += 1
    return i


def _find(s: str, i: int, stops: str) -> int:
    """Index of the first char in `stops` outside strings and (...) / [...]; len(s) if none."""
    depth, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\":                 # escaped char (e.g. Tailwind selectors like .md\\:flex)
            i += 2
            continue
        if c in "\"'":
            i = _skip_string(s, i)
            continue
        if c in "([":
            depth += 1
        elif c in ")]":
            depth = max(0, depth - 1)
        elif depth == 0 and c in stops:
            return i
        i += 1
    return n


def _match_brace(s: str, i: int) -> int:
    depth, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c in "\"'":
            i = _skip_string(s, i)
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n - 1


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def split_top(value: str, sep: str = ",") -> list[str]:
    """Split on `sep` outside parentheses/strings."""
    out, i, n = [], 0, len(value)
    while i <= n:
        j = _find(value, i, sep)
        out.append(value[i:j].strip())
        i = j + 1
        if j >= n:
            break
    return [x for x in out if x != ""]


def split_ws(value: str) -> list[str]:
    """Split on whitespace outside parentheses/strings (for margin/padding shorthands)."""
    out, cur, depth, i, n = [], "", 0, 0, len(value)
    while i < n:
        c = value[i]
        if c == "\\":
            cur += value[i:i + 2]
            i += 2
            continue
        if c in "\"'":
            j = _skip_string(value, i)
            cur += value[i:j]
            i = j
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth = max(0, depth - 1)
        if c.isspace() and depth == 0:
            if cur:
                out.append(cur)
                cur = ""
        else:
            cur += c
        i += 1
    if cur:
        out.append(cur)
    return out


# ---------- parser ----------

BLOCK_AT = {"media", "supports", "container", "layer", "scope", "starting-style", "document"}


class Sheet:
    def __init__(self):
        self.rules: list[dict] = []        # {src, sel, ctx(tuple[str]), decls[(prop, val, important)]}
        self.fontfaces: list[dict] = []    # {src, ctx, decls{prop: val}}
        self.keyframes: list[dict] = []    # {src, name, stops[str]}
        self.properties: list[dict] = []   # @property {src, name, decls{}}
        self.imports: list[str] = []


def parse_decls(body: str) -> list[tuple[str, str, bool]]:
    out, i, n = [], 0, len(body)
    while i < n:
        j = _find(body, i, ";")
        chunk = body[i:j].strip()
        i = j + 1
        if not chunk or ":" not in chunk:
            continue
        prop, _, val = chunk.partition(":")
        prop, val = prop.strip(), val.strip()
        if not prop.startswith("--"):
            prop = prop.lower()
        imp = bool(re.search(r"!\s*important\s*$", val, flags=re.I))
        if imp:
            val = re.sub(r"\s*!\s*important\s*$", "", val, flags=re.I)
        out.append((prop, val, imp))
    return out


def _parse(s: str, ctx: tuple, sheet: Sheet, src: str, parent: str | None, in_rule: bool, rule: dict | None):
    i, n = 0, len(s)
    while i < n:
        while i < n and s[i].isspace():
            i += 1
        if i >= n:
            break
        j = _find(s, i, "{;}")
        prelude = s[i:j].strip() if j <= n else s[i:].strip()
        c = s[j] if j < n else ";"
        if c == "}":
            i = j + 1
            continue
        if c == ";":
            i = j + 1
            if in_rule and ":" in prelude and rule is not None:
                rule["decls"].extend(parse_decls(prelude))
            elif prelude.lower().startswith("@import"):
                m = re.search(r"""@import\s+(?:url\(\s*)?["']?([^"')\s;]+)""", prelude, flags=re.I)
                if m:
                    sheet.imports.append(m.group(1))
            continue
        k = _match_brace(s, j)
        body = s[j + 1:k]
        i = k + 1
        _block(prelude, body, ctx, sheet, src, parent)


def _block(prelude: str, body: str, ctx: tuple, sheet: Sheet, src: str, parent: str | None):
    if prelude.startswith("@"):
        m = re.match(r"@([\w-]+)\s*(.*)", prelude, flags=re.S)
        if not m:                      # "@{...}" / "@ {...}": malformed at-rule, ignore its block
            return
        name, rest = m.group(1).lower(), m.group(2).strip()
        if name == "font-face":
            sheet.fontfaces.append({"src": src, "ctx": ctx, "decls": {p: v for p, v, _ in parse_decls(body)}})
        elif name.endswith("keyframes"):
            stops = re.findall(r"(?:^|[;}\s])((?:from|to|\d+(?:\.\d+)?%)(?:\s*,\s*(?:from|to|\d+(?:\.\d+)?%))*)\s*\{", body)
            sheet.keyframes.append({"src": src, "name": rest, "stops": stops})
        elif name == "property":
            sheet.properties.append({"src": src, "name": rest, "decls": {p: v for p, v, _ in parse_decls(body)}})
        elif name in BLOCK_AT:
            _parse(body, ctx + (f"@{name} {rest}".strip(),), sheet, src, parent, False, None)
        return
    sel = prelude
    if parent:
        sel = ", ".join(p.replace("&", parent) if "&" in p else f"{parent} {p}" for p in split_top(prelude))
    rule = {"src": src, "sel": sel, "ctx": ctx, "decls": []}
    sheet.rules.append(rule)
    _parse(body, ctx, sheet, src, sel, True, rule)


def parse_css(css: str, src: str = "", sheet: Sheet | None = None) -> Sheet:
    sheet = sheet or Sheet()
    _parse(strip_comments(css), (), sheet, src, None, False, None)
    return sheet


# ---------- colours ----------

# The full CSS named-colour table, loaded from data (name -> #rrggbb).
NAMED = load_json("css_named_colors.json")
HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![0-9a-zA-Z_-])")
FUNC_NAMES = ("rgba", "rgb", "hsla", "hsl", "hwb", "oklch", "oklab", "lch", "lab", "color-mix", "color")
FUNC_RE = re.compile(r"(?<![\w-])(" + "|".join(FUNC_NAMES) + r")\(")
NAMED_RE = re.compile(r"(?<![\w#-])(" + "|".join(sorted(NAMED, key=len, reverse=True)) + r")(?![\w-])", re.I)


def _balanced(s: str, start: int) -> int:
    """Index just past the ')' matching the '(' at/after `start`."""
    i = s.index("(", start)
    depth = 0
    while i < len(s):
        if s[i] == "(":
            depth += 1
        elif s[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(s)


def remove_calls(value: str, names: tuple[str, ...]) -> str:
    """Remove name(...) calls (balanced), e.g. url() and var(), before colour scanning."""
    pat = re.compile(r"(?<![\w-])(" + "|".join(names) + r")\(", re.I)
    out, i = [], 0
    while True:
        m = pat.search(value, i)
        if not m:
            out.append(value[i:])
            break
        out.append(value[i:m.start()])
        i = _balanced(value, m.start())
    return " ".join(out)


def _num(tok: str, scale: float = 1.0) -> float | None:
    tok = tok.strip()
    try:
        if tok.endswith("%"):
            return float(tok[:-1]) / 100.0 * scale
        return float(tok)
    except ValueError:
        return None


def _hex(r: float, g: float, b: float, a: float = 1.0) -> str:
    c = lambda v: max(0, min(255, int(round(v))))
    h = f"#{c(r):02x}{c(g):02x}{c(b):02x}"
    return h + f"{c(a * 255):02x}" if a < 0.995 else h


def normalize_color(token: str) -> str | None:
    """-> '#rrggbb' / '#rrggbbaa' for hex/rgb/hsl/named; lowercased raw for other colour functions."""
    t = token.strip()
    if HEX_RE.fullmatch(t):
        h = t[1:].lower()
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        if len(h) == 8 and h.endswith("ff"):
            h = h[:6]
        return "#" + h
    low = t.lower()
    if low in NAMED:
        return NAMED[low]
    m = re.match(r"(rgba?|hsla?)\((.*)\)$", low, flags=re.S)
    if m:
        parts = [p for p in re.split(r"[\s,/]+", m.group(2).strip()) if p]
        if len(parts) >= 3 and not any("var(" in p or "from" == p for p in parts):
            a = _num(parts[3]) if len(parts) > 3 else 1.0
            a = 1.0 if a is None else a
            if m.group(1).startswith("rgb"):
                v = [_num(p, 255) for p in parts[:3]]
                if None not in v:
                    return _hex(*v, a)
            else:
                h = _num(parts[0].replace("deg", ""))
                s, l = _num(parts[1], 1.0), _num(parts[2], 1.0)
                if None not in (h, s, l):
                    r, g, b = colorsys.hls_to_rgb((h % 360) / 360.0, l, s)
                    return _hex(r * 255, g * 255, b * 255, a)
    if re.match(r"(oklch|oklab|lch|lab|hwb|color|color-mix)\(", low):
        return re.sub(r"\s+", " ", low)
    return None


def extract_colors(value: str, allow_named: bool = True) -> list[str]:
    """All colours in a declaration value (normalized), ignoring url()/var() content and quoted strings.
    allow_named=False skips colour *names* (use for properties where a word like 'tomato' is not a colour)."""
    v = re.sub(r"\"[^\"]*\"|'[^']*'", " ", remove_calls(value, ("url", "var", "image-set")))
    found: list[str] = []
    spans: list[tuple[int, int]] = []
    for m in FUNC_RE.finditer(v):
        if any(a <= m.start() < b for a, b in spans):
            continue
        end = _balanced(v, m.start())
        spans.append((m.start(), end))
        c = normalize_color(v[m.start():end])
        if c:
            found.append(c)
    rest = v
    for a, b in reversed(spans):
        rest = rest[:a] + " " + rest[b:]
    for m in HEX_RE.finditer(rest):
        c = normalize_color(m.group(0))
        if c:
            found.append(c)
    if allow_named:
        for m in NAMED_RE.finditer(HEX_RE.sub(" ", rest)):
            found.append(NAMED[m.group(1).lower()])
    return found


def color_info(c: str) -> dict:
    """Lightness/saturation classification for '#rrggbb[aa]'; empty dict for non-hex colour functions."""
    if not re.fullmatch(r"#[0-9a-f]{6}(?:[0-9a-f]{2})?", c):
        return {}
    r, g, b = (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    kind = "neutral" if (s < 0.14 or l < 0.03 or l > 0.97) else "accent"
    return {"h": round(h * 360), "s": round(s, 2), "l": round(l, 2), "kind": kind,
            "alpha": round(int(c[7:9], 16) / 255, 2) if len(c) == 9 else 1.0}


# ---------- lengths ----------

LEN_RE = re.compile(r"^(-?\d*\.?\d+)(px|rem|em|pt|vw|vh|vmin|vmax|svh|dvh|lvh|cqw|cqi|ch|ex|%|fr|s|ms)?$")


def to_px(token: str) -> float | None:
    m = LEN_RE.match(token.strip())
    if not m:
        return None
    n, unit = float(m.group(1)), m.group(2)
    if unit in (None, "px"):
        return n
    if unit in ("rem", "em"):
        return n * 16.0
    if unit == "pt":
        return n * 4.0 / 3.0
    return None


def fmt_num(n: float) -> str:
    return str(int(n)) if abs(n - round(n)) < 1e-9 else f"{n:.2f}".rstrip("0").rstrip(".")
