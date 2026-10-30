"""Technology evidence: observable facts first, names second.

A closed list of library names cannot be correct: new frameworks appear constantly and many leave
no name behind. So detection works in two layers:

1. EVIDENCE (no vocabulary): generator meta tags, informative response headers, cookie names, packages
   inferred from CDN/URL grammars, attribute-prefix census, generated class-name shapes, inline JSON ids and
   window globals, CSS banners, third-party hosts, build fingerprints. This layer surfaces technology the
   skill has never heard of.
2. ATTRIBUTION (data): `data/tech_signatures.json` (extensible with `--signatures FILE`) maps evidence to
   names with a confidence level. It is a starter list, not a closed world.

Absence of a name is never reported as absence of the technology.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from functools import lru_cache
from urllib.parse import parse_qs, urljoin, urlparse

from _data import host_listed, load_json, load_lines

# Standards vocabularies (HTML/HTTP), not third-party products.
STANDARD_META = {"charset", "viewport", "description", "keywords", "author", "robots", "googlebot", "referrer", "theme-color",
                 "color-scheme", "format-detection", "generator", "application-name", "mobile-web-app-capable",
                 "google-site-verification", "msvalidate.01", "yandex-verification", "facebook-domain-verification"}
STANDARD_META_PREFIX = ("og:", "twitter:", "article:", "fb:", "apple-", "msapplication-", "profile:", "book:", "music:", "video:")
NON_STANDARD_HYPHEN = {"aria", "http", "accept", "xlink", "xml", "xmlns", "data"}
# Caps keep reports readable and analysis fast on very large pages.
MAX_URLS, MAX_INLINE_CHARS, MAX_ATTR_NAMES, MAX_CLASSES, MAX_COMMENTS = 2000, 60_000, 3000, 6000, 15


# ---------- helpers ----------

def _trunc(s: str, n: int = 110) -> str:
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s if len(s) <= n else s[:n - 1] + "…"


def _nq(url: str) -> str:
    """URL without query string / fragment: signatures match host + path, never tracking parameters."""
    return url.split("?", 1)[0].split("#", 1)[0]


def _alnum_mix(h: str) -> bool:
    """Looks like a generated hash: letters and digits interleaved (>=2 letter/digit transitions)."""
    if not (re.search(r"[A-Za-z]", h) and re.search(r"\d", h)):
        return False
    kinds = ["d" if c.isdigit() else "a" for c in h if c.isalnum()]
    return sum(1 for a, b in zip(kinds, kinds[1:]) if a != b) >= 2


def attr_prefix(name: str) -> str | None:
    """Prefix family of a non-standard attribute name (hx-get -> 'hx-', wire:click -> 'wire:',
    data-astro-cid-x -> 'data-astro', @click -> '@'), or None for plain attributes."""
    n = name.lower()
    if n.startswith("aria-") or n.startswith("on") and n[2:].isalpha():
        return None
    if n[:1] in "@:#*[(":
        return n[:1]
    if ":" in n:
        head = n.split(":", 1)[0]
        return None if head in NON_STANDARD_HYPHEN else head + ":"
    if n.startswith("_") and "-" in n:
        return n.split("-", 1)[0]
    if n.startswith("data-"):
        parts = n.split("-")
        return "-".join(parts[:2]) if len(parts) >= 3 else None      # data-<ns>-... only: plain data-foo is not a family
    if "-" in n:
        head = n.split("-", 1)[0]
        return None if head in NON_STANDARD_HYPHEN else head + "-"
    return None


def class_shape(c: str) -> tuple[str, str] | None:
    """('name-hash', prefix) / ('module-hash', prefix) for generated-looking class names, else None."""
    m = re.fullmatch(r"([A-Za-z][A-Za-z0-9]*)-([A-Za-z0-9]{5,10})", c)
    if m and _alnum_mix(m.group(2)):
        return "name-hash", m.group(1)
    m = re.fullmatch(r"([A-Za-z][\w-]*_[A-Za-z0-9]+)__([A-Za-z0-9_-]{5})", c)
    if m and _alnum_mix(m.group(2)):
        return "module__hash", m.group(1).split("_")[0]
    return None


def last_header_block(text: str) -> str:
    """The final `HTTP/...` header block of a curl -D dump (the response after any redirects)."""
    blocks = [b for b in re.split(r"\r?\n\r?\n", text.strip()) if b.strip().upper().startswith("HTTP/")]
    return blocks[-1] if blocks else ""


def parse_header_block(text: str) -> dict[str, list[str]]:
    """Parse the last `HTTP/... ` header block in `text` into {lowercase-name: [values]}."""
    block = last_header_block(text)
    out: dict[str, list[str]] = defaultdict(list)
    if not block:
        return out
    for line in block.splitlines()[1:]:
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip().lower()].append(v.strip())
    return dict(out)


def redact_headers(raw: str) -> str:
    """Remove cookie VALUES from a raw header block (names and attributes are kept)."""
    def fix(m):
        return f"{m.group(1)}{m.group(2)}=<redacted>"
    return re.sub(r"(?im)^(set-cookie:\s*)([^=\r\n;]+)=[^;\r\n]*", fix, raw)


def _header_policy():
    pol = load_json("tech_signatures.json")["header_policy"]      # data: which response headers are informative vs noise
    return set(pol["informative"]), tuple(pol["informative_prefixes"]), tuple(pol["noise_prefixes"])


def informative_headers(headers: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    """-> (['name: value', ...] informative response headers, cookie names). Cookie values are never kept."""
    info, info_prefixes, noise_prefixes = _header_policy()
    lines, cookies = [], []
    for k, vals in (headers or {}).items():
        if k == "set-cookie":
            cookies += [re.split(r"[=;]", v, 1)[0].strip() for v in vals]
            continue
        keep = k in info or (k.startswith(info_prefixes) and not k.startswith(noise_prefixes))
        if keep:
            lines += [f"{k}: {_trunc(v, 120)}" for v in vals]
    return lines, cookies


@lru_cache(maxsize=None)
def _rx(pattern: str):
    return re.compile(pattern, re.I)


def load_signatures(user_file: str | None = None) -> dict:
    """Built-in signatures merged with an optional user file (same format; same-name entries replace)."""
    base = load_json("tech_signatures.json")
    sigs = {s["name"]: s for s in base["signatures"]}
    cdn = list(base["cdn_patterns"])
    if user_file:
        import json
        from pathlib import Path
        user = json.loads(Path(user_file).read_text(encoding="utf-8"))
        for s in user.get("signatures", []):
            sigs[s["name"]] = s
        cdn = list(user.get("cdn_patterns", [])) + cdn
    return {"signatures": list(sigs.values()), "cdn_patterns": cdn}


# ---------- evidence ----------

def collect_evidence(root, comments, headers, css_text, css_banners, base_url, cdn_patterns) -> dict:
    page_host = (urlparse(base_url).hostname or "").lower()
    metas: dict[str, list[str]] = defaultdict(list)
    scripts, stylesheets, other_links, media_urls = [], [], [], []
    inline_parts: list[str] = []
    json_ids, script_types, input_names = [], [], []
    attr_names: set[str] = set()
    prefix_ctr: Counter = Counter()
    prefix_examples: dict[str, set] = defaultdict(set)
    classes: Counter = Counter()
    tags: set[str] = set()
    rel_flags = Counter()
    html_node = body = None

    for n in root.walk():
        t = n.tag
        if t == "#root":
            continue
        tags.add(t)
        if t == "html":
            html_node = n
        elif t == "body":
            body = n
        if t == "meta":
            name = (n.attrs.get("name") or n.attrs.get("property") or "").lower()
            if name:
                metas[name].append(n.attrs.get("content", ""))
        elif t == "script":
            src, typ = n.attrs.get("src"), n.attrs.get("type", "").strip().lower()
            if typ:
                script_types.append(typ)
            if n.attrs.get("id"):
                json_ids.append(n.attrs["id"])
            if src:
                scripts.append({"src": urljoin(base_url, src), "type": typ, "async": "async" in n.attrs, "defer": "defer" in n.attrs, "nomodule": "nomodule" in n.attrs})
            elif not any(k in typ for k in ("json", "importmap", "speculationrules")):
                inline_parts.append("".join(n.text))
        elif t == "link":
            rel, href = n.attrs.get("rel", "").lower(), n.attrs.get("href", "")
            for r in rel.split():
                rel_flags[r] += 1
            if href:
                u = urljoin(base_url, href)
                (stylesheets if "stylesheet" in rel else other_links if not any(r in rel for r in ("canonical", "alternate", "next", "prev", "author")) else []).append(u)
        elif t in ("img", "source", "iframe", "video", "audio", "embed"):
            if n.attrs.get("src"):
                media_urls.append(urljoin(base_url, n.attrs["src"]))
        elif t in ("input", "select", "textarea", "button") and n.attrs.get("name"):
            input_names.append(n.attrs["name"])
        if not n.in_svg:
            for a in n.attrs:
                if len(attr_names) < MAX_ATTR_NAMES:
                    attr_names.add(a)
                p = attr_prefix(a)
                if p:
                    prefix_ctr[p] += 1
                    if len(prefix_examples[p]) < 3:
                        prefix_examples[p].add(a if len(a) < 40 else a[:39] + "…")
            for c in n.cls:
                if len(classes) < MAX_CLASSES:
                    classes[c] += 1

    inline = "\n".join(inline_parts)[:MAX_INLINE_CHARS]

    # window globals / dunder identifiers assigned or referenced inline
    globals_ctr: Counter = Counter()
    for m in re.finditer(r"\b(?:window|self|globalThis)\s*(?:\.|\[\s*[\"'])([A-Za-z_$][\w$]*)[\"']?\s*\]?\s*(?:=|\|\|=)", inline):
        globals_ctr[m.group(1)] += 1
    for m in re.finditer(r"\b(__[A-Za-z][\w$]*)", inline):
        globals_ctr[m.group(1)] += 1
    for m in re.finditer(r"\b(\$docsify|drupalSettings)\b", inline):
        globals_ctr[m.group(1)] += 1

    # packages from URL grammars (CDN schemes, node_modules paths, versioned filenames)
    all_urls = ([s["src"] for s in scripts] + stylesheets + other_links + media_urls)[:MAX_URLS]
    packages, seen_pkg = [], set()
    compiled = [(p["name"], _rx(p["re"])) for p in cdn_patterns]
    for u in [s["src"] for s in scripts] + stylesheets + other_links:
        for cname, rx in compiled:
            m = rx.search(u)
            if m and m.groupdict().get("pkg"):
                pkg, ver = m.group("pkg").lower(), (m.groupdict().get("ver") or "")
                if (pkg, ver) not in seen_pkg:
                    seen_pkg.add((pkg, ver))
                    packages.append({"name": pkg, "version": ver, "via": cname, "url": _trunc(u, 90)})
                break

    # Google-Fonts-style stylesheet URLs (css/css2?family=...), generic grammar
    fonts: list[str] = []
    for u in stylesheets + other_links:
        pu = urlparse(u)
        if re.search(r"/css2?$", pu.path) and "family" in pu.query:
            for fam in parse_qs(pu.query).get("family", []):
                for part in fam.split("|"):
                    name = part.split(":")[0].replace("+", " ").strip()
                    if name and name not in fonts:
                        fonts.append(name)

    # hosts
    hosts: dict[str, dict] = {}
    trackers = load_lines("trackers.txt")
    first_party = 0
    for kind, urls in (("script", [s["src"] for s in scripts]), ("style", stylesheets), ("link", other_links), ("media", media_urls)):
        for u in urls:
            h = (urlparse(u).hostname or "").lower()
            if not h:
                continue
            fp = (not page_host) or h == page_host or h.endswith("." + page_host) or page_host.endswith("." + h)
            if urlparse(u).scheme in ("http", "https") and not fp:
                d = hosts.setdefault(h, {"host": h, "count": 0, "kinds": set(), "tracker": host_listed(h, trackers)})
                d["count"] += 1
                d["kinds"].add(kind)
            else:
                first_party += 1

    # build fingerprints
    hashed = 0
    for u in [s["src"] for s in scripts] + stylesheets:
        base = urlparse(u).path.rsplit("/", 1)[-1]
        m = re.search(r"[.-]([A-Za-z0-9_-]{8,})\.(?:m?js|css)$", base)
        if m and _alnum_mix(m.group(1)):
            hashed += 1
    build = {"hashed_assets": hashed, "module_scripts": sum(1 for s in scripts if s["type"] == "module"),
             "nomodule_scripts": sum(1 for s in scripts if s["nomodule"]), "importmap": "importmap" in script_types,
             "modulepreload": rel_flags.get("modulepreload", 0), "web_manifest": rel_flags.get("manifest", 0) > 0,
             "service_worker": bool(re.search(r"serviceWorker\s*\.\s*register", inline)), "inline_scripts": len(inline_parts),
             "script_files": [urlparse(s["src"]).path.rsplit("/", 1)[-1] for s in scripts if (urlparse(s["src"]).hostname or "").lower() in ("", page_host)][:25]}

    # generated class shapes
    shapes: dict[str, dict] = {}
    for c, cnt in classes.items():
        sh = class_shape(c)
        if sh:
            d = shapes.setdefault(sh[0], {"shape": sh[0], "count": 0, "prefixes": Counter(), "examples": []})
            d["count"] += cnt
            d["prefixes"][sh[1]] += cnt
            if len(d["examples"]) < 3:
                d["examples"].append(c)
    class_prefixes = sorted({p for d in shapes.values() for p in d["prefixes"]})

    gen_names = metas.get("generator", [])
    hdr_lines, cookie_names = informative_headers(headers)
    comment_hits = [_trunc(c, 120) for c in comments
                    if re.search(r"(generated|built|created|powered|made|compiled)\s+(by|with|in|using|on)\b|\bv(ersion)?\s*\d+(\.\d+)+", c, re.I)][:MAX_COMMENTS]
    root_markers: list[str] = []
    for node in (html_node, body):
        if node is not None:
            root_markers += [f"{k}={v}" if v else k for k, v in node.attrs.items() if k != "style"]
            root_markers += list(node.cls)
    if body is not None:
        root_markers += [c.attrs["id"] for c in body.children if c.attrs.get("id")][:10]
    unusual_meta = sorted({k for k in metas if k not in STANDARD_META and not k.startswith(STANDARD_META_PREFIX)})[:25]

    pools = {
        "meta_generator": gen_names, "meta_name": list(metas), "header": hdr_lines, "cookie_name": cookie_names,
        "script_src": [_nq(s["src"]) for s in scripts], "stylesheet_href": [_nq(u) for u in stylesheets], "any_url": [_nq(u) for u in all_urls], "comment": [c.strip() for c in comments],
        "attr_name": sorted(attr_names), "attr_prefix": sorted(prefix_ctr), "class_name": list(classes), "class_prefix": class_prefixes,
        "tag": sorted(tags), "inline_script": inline, "json_script_id": json_ids, "script_type": script_types,
        "global": list(globals_ctr), "css_banner": [b["banner"] for b in css_banners], "css_text": css_text[:5_000_000],
        "root_marker": root_markers, "input_name": input_names, "package": [p["name"] for p in packages],
    }
    evidence = {
        "generator": [_trunc(g) for g in gen_names], "headers": hdr_lines, "cookie_names": sorted(set(cookie_names)),
        "packages": packages, "google_fonts": fonts,
        "third_party_hosts": sorted(({**d, "kinds": sorted(d["kinds"])} for d in hosts.values()), key=lambda d: -d["count"])[:20],
        "first_party_assets": first_party, "build": build,
        "attribute_prefixes": [{"prefix": p, "count": c, "examples": sorted(prefix_examples[p])} for p, c in prefix_ctr.most_common(15)],
        "generated_classes": [{"shape": d["shape"], "count": d["count"], "examples": d["examples"], "prefixes": d["prefixes"].most_common(5)} for d in shapes.values()],
        "json_script_ids": sorted(set(json_ids))[:20], "script_types": sorted(set(script_types)),
        "globals": [g for g, _ in globals_ctr.most_common(25)], "css_banners": css_banners[:12],
        "root_markers": root_markers[:25], "unusual_meta": unusual_meta, "comments": comment_hits,
        "custom_elements": sorted(t for t in tags if re.fullmatch(r"[a-z][a-z0-9]*(-[a-z0-9]+)+", t)),
    }
    return {"pools": pools, "evidence": evidence, "packages": packages}


# ---------- attribution ----------

_VER = re.compile(r"(?<![\w.])v?(\d+\.\d+(?:\.\d+)?(?:[-+][\w.]+)?)")


def match_signatures(pools: dict, packages: list[dict], signatures: list[dict]) -> list[dict]:
    found = []
    for sig in signatures:
        hits = []
        for s in sig.get("signals", []):
            pool = pools.get(s["in"])
            if not pool:
                continue
            rx = _rx(s["re"])
            if isinstance(pool, str):
                m = rx.search(pool)
                matches = [m.group(0)] if m else []
            else:
                matches = [x for x in pool if rx.search(x)][:2]
            if matches:
                hits.append({"pool": s["in"], "weight": s.get("weight", "medium"), "match": _trunc(matches[0], 90)})
        if not hits:
            continue
        w = Counter(h["weight"] for h in hits)
        conf = "high" if w["strong"] else "medium" if (w["medium"] >= 2 or (w["medium"] and w["weak"])) else "low"
        version = ""
        for pref in ("meta_generator", "header", "css_banner", "package"):
            for h in hits:
                if h["pool"] != pref:
                    continue
                if pref == "package":
                    version = next((p["version"] for p in packages if p["name"] == h["match"] and p["version"]), "")
                else:
                    m = _VER.search(h["match"])
                    version = m.group(1) if m else ""
                if version:
                    break
            if version:
                break
        found.append({"name": sig["name"], "category": sig.get("category", ""), "confidence": conf, "version": version,
                      "evidence": [f"{h['pool']}: {h['match']}" for h in hits][:4]})
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(found, key=lambda f: (order[f["confidence"]], f["name"].lower()))


def detect(root, comments, headers, css_text, css_banners, base_url, signatures_file=None) -> dict:
    sigs = load_signatures(signatures_file)
    ev = collect_evidence(root, comments, headers, css_text, css_banners, base_url, sigs["cdn_patterns"])
    identified = match_signatures(ev["pools"], ev["packages"], sigs["signatures"])
    out = ev["evidence"]
    out["identified"] = identified
    out["headers_available"] = bool(headers)
    return out


def css_banner_list(css_sources: list[tuple[str, str]]) -> list[dict]:
    """First comment of each CSS source when it looks like a banner (version/license/copyright)."""
    out = []
    for label, text in css_sources:
        m = re.match(r"\s*/\*!?(.*?)\*/", text[:3000], re.S)
        if m and re.search(r"\d+\.\d+|licen[sc]e|copyright|©|\bMIT\b|apache|@preserve|generated|built", m.group(1), re.I):
            out.append({"source": _trunc(label.split("/")[-1] or label, 50), "banner": _trunc(m.group(1), 160)})
    return out


# ---------- markdown ----------

def render_tech_md(t: dict) -> list[str]:
    L = ["## Technology evidence", "",
         "Facts observed in the HTML, response headers and CSS. Names come from `scripts/data/tech_signatures.json` "
         "(extend with `--signatures FILE`). **A missing name does not mean the technology is absent**: unknown or "
         "server-side technology only shows up if it leaves a trace, and the raw evidence below lists those traces regardless of any name list.", ""]
    ident = t["identified"]
    L += ["### Identified (attribution from the signature data)", ""]
    if ident:
        L += ["| technology | category | confidence | version | evidence |", "|---|---|---|---|---|"]
        for i in ident:
            L.append(f"| {i['name']} | {i['category']} | {i['confidence']} | {i['version']} | " + "; ".join(i["evidence"]).replace("|", "\\|") + " |")
        L.append("")
    else:
        L += ["_No signature matched._ This does not mean nothing is used; see the raw evidence.", ""]

    def bullet(label, items, fmt=lambda x: f"`{x}`", limit=12):
        if items:
            L.append(f"- **{label}:** " + ", ".join(fmt(x) for x in items[:limit]) + (f" (+{len(items) - limit} more)" if len(items) > limit else ""))

    L += ["### Raw evidence (independent of the signature list)", ""]
    if not t["headers_available"]:
        L.append("- _Response headers were not available (analysed from a file); header-based evidence is missing._")
    bullet("Generator meta", t["generator"])
    bullet("Informative response headers", t["headers"])
    bullet("Cookie names (values never stored)", t["cookie_names"])
    bullet("Packages inferred from URLs", t["packages"], lambda p: f"`{p['name']}" + (f"@{p['version']}" if p["version"] else "") + f"` via {p['via']}")
    bullet("Google-Fonts-style families", t["google_fonts"])
    b = t["build"]
    L.append(f"- **Build fingerprints:** content-hashed assets {b['hashed_assets']}, module scripts {b['module_scripts']}, nomodule {b['nomodule_scripts']}, "
             f"importmap {'yes' if b['importmap'] else 'no'}, modulepreload {b['modulepreload']}, web manifest {'yes' if b['web_manifest'] else 'no'}, "
             f"service worker registration {'yes' if b['service_worker'] else 'no'}, inline scripts {b['inline_scripts']}")
    bullet("First-party script files", b["script_files"])
    bullet("Attribute-prefix families (framework conventions)", t["attribute_prefixes"],
           lambda p: f"`{p['prefix']}` x{p['count']} ({', '.join(p['examples'][:2])})")
    bullet("Generated class-name shapes", t["generated_classes"],
           lambda g: f"`{g['shape']}` x{g['count']} (prefixes: {', '.join(f'{p} x{n}' for p, n in g['prefixes'][:3])}; e.g. {', '.join(g['examples'][:2])})")
    bullet("Inline JSON / script ids", t["json_script_ids"])
    bullet("Window globals set inline", t["globals"])
    bullet("CSS banners", t["css_banners"], lambda b_: f"{b_['source']}: {b_['banner']}", limit=6)
    bullet("Third-party hosts", t["third_party_hosts"],
           lambda h: f"`{h['host']}` x{h['count']} ({'/'.join(h['kinds'])}{', tracker' if h['tracker'] else ''})")
    bullet("Root markers (html/body attributes, classes, ids)", t["root_markers"], limit=14)
    bullet("Unusual meta names", t["unusual_meta"])
    bullet("Informative HTML comments", t["comments"], lambda c: f'"{c}"', limit=6)
    L.append("")
    return L
