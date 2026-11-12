"""Save the fully rendered, fully expanded DOM of JS-heavy pages as plain .html for scraping.

Loads each page in a real headless browser, then *forces* hidden content to appear before saving
the final DOM (what DevTools shows, not the raw "view source"), so BeautifulSoup/lxml/regex can
parse it with no JavaScript:

  - scrolls until nothing new loads (infinite scroll, inner scrollable feeds / virtual lists)
  - clicks "Load more / Show more / Read more" buttons and opens collapsed accordions
  - opens <details>, promotes lazy attributes (data-src -> src, data-srcset -> srcset)
  - flattens open shadow DOM and (optionally) same-page iframes into the HTML
  - makes every link/src absolute so extracted URLs are usable

Usage:
  python dom.py https://example.com/products -o products.html
  python dom.py https://a.com https://b.com --output-dir .capture/dom --text
  python dom.py https://shop.com/list --click ".pager .more" --wait-for ".product-card" --api
  python dom.py https://site.com/feed --max-rounds 40 --iframes

Not a site mirror: use `website` to download a browsable offline copy (JS, CSS, fonts).
Requires: pip install playwright && playwright install chromium
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli import (add_device_args, add_json_args, add_output_args, add_session_args,  # noqa: E402
                  add_theme_args, add_view_args, begin, check_file, emit, list_devices,
                  resolve_device, resolve_viewport, seed_theme, apply_theme)
from _common import default_user_agent, ensure_parent, resolve_output  # noqa: E402
from _data import load_json  # noqa: E402
from screenshots import folder_name, normalize_url  # noqa: E402

# Tunables, named so they can be found and changed in one place.
MAX_IFRAMES = 30               # iframes inlined with --iframes
API_MAX_ENTRIES = 200          # JSON responses kept with --api
API_MAX_BYTES = 2_000_000      # per JSON response
GRADUAL_MAX_STEPS = 40         # viewport steps in the first lazy-load pass
GRADUAL_STEP_PAUSE_MS = 120
NETWORKIDLE_PROBE_MS = 3000    # how long to wait for network idle after each round
MAX_SCROLL_CONTAINERS = 20     # inner scrollable panels scrolled per round
MAX_LABEL_CHARS = 40           # button texts longer than this are never treated as 'show more'
LABEL_SUFFIX_SLACK = 14        # extra characters allowed after a phrase (a count, an arrow...)

METRICS_JS = ("() => [Math.max(document.body ? document.body.scrollHeight : 0, "
              "document.documentElement.scrollHeight), document.getElementsByTagName('*').length]")

SCROLL_JS = r"""(maxContainers) => {
  window.scrollTo(0, document.documentElement.scrollHeight);
  let n = 0;
  for (const el of document.querySelectorAll('*')) {
    if (n >= maxContainers) break;
    if (el.scrollHeight > el.clientHeight + 50) {
      const s = getComputedStyle(el);
      if (s.overflowY === 'auto' || s.overflowY === 'scroll') { el.scrollTop = el.scrollHeight; n++; }
    }
  }
  return n;
}"""

# "Show more" detection: phrases come from data/more_phrases.json (many languages) plus --more-phrase;
# --more-pattern adds a regex. Real links are never clicked (only buttons, summaries, #-anchors).
CLICK_JS = r"""(o) => {
  const norm = s => (s || '').replace(/\s+/g, ' ').trim().toLowerCase();
  const phrases = (o.phrases || []).map(norm).filter(Boolean);
  const extra = o.pattern ? new RegExp(o.pattern, 'i') : null;
  const isMore = txt => phrases.some(p => txt === p || (txt.startsWith(p) && txt.length <= p.length + (o.suffixSlack || 0))) || (extra && extra.test(txt));
  const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  let n = 0;
  if (o.expand) {
    const sel = 'button, [role=button], summary, input[type=button], a[href^="#"], a:not([href])';
    document.querySelectorAll(sel).forEach(el => {
      if (el.disabled || !vis(el)) return;
      const txt = norm(el.innerText || el.value || el.getAttribute('aria-label'));
      if (!txt || txt.length > o.maxLabelChars) return;
      const collapsed = el.getAttribute('aria-expanded') === 'false' &&
        !el.closest('nav, header, [role=menu], [role=menubar], [role=dialog]');
      if (isMore(txt) || collapsed) { try { el.click(); n++; } catch (e) {} }
    });
  }
  for (const s of (o.selectors || [])) {
    document.querySelectorAll(s).forEach(el => { if (vis(el)) { try { el.click(); n++; } catch (e) {} } });
  }
  return n;
}"""

FINALIZE_JS = r"""(o) => {
  const st = {details: 0, shadow: 0, lazy: 0, abs: 0};
  document.querySelectorAll('details:not([open])').forEach(d => { d.open = true; st.details++; });
  if (o.shadow) {            // deepest hosts first so nested shadow content is carried upward
    const hosts = [];
    const collect = root => root.querySelectorAll('*').forEach(el => {
      if (el.shadowRoot) { hosts.push(el); collect(el.shadowRoot); } });
    collect(document);
    for (const el of hosts.reverse()) {
      const d = document.createElement('div');
      d.setAttribute('data-shadow-root', 'open');
      d.innerHTML = el.shadowRoot.innerHTML;
      el.appendChild(d); st.shadow++;
    }
  }
  // Lazy media, structurally: a data-* attribute whose VALUE looks like a URL (path or media extension) is a
  // lazy-load candidate, promoted to the real attribute only when that one is missing or a placeholder. With several
  // candidates, those whose NAME hints at a source win; a single candidate needs no name hint at all.
  // --lazy-attr adds explicit names (any attribute, not only data-*).
  const lazyAttrs = o.lazyAttrs || [];
  const NAME_HINT = /(^|-)(src|source|original|lazy|url|image|img|poster|thumb)(set)?($|-)/i;   // tie-breaker only
  const URLISH = /^(?:(?:https?:)?\/\/|\/|\.{1,2}\/)|\.(?:avif|webp|png|jpe?g|gif|svg|ico|mp4|webm|m4v|mov|mp3|ogg|m3u8)(?:[?#\s,]|$)/i;
  const PLACEHOLDER = v => !v || v.startsWith('data:') || /(^|[\/_-])(blank|placeholder|spacer|pixel|transparent|loading)([._-]|$)|1x1/i.test(v);
  document.querySelectorAll('img, source, video, iframe, audio').forEach(el => {
    const cands = [];
    for (const a of el.getAttributeNames()) {
      const explicit = lazyAttrs.includes(a);
      if (!explicit && !a.startsWith('data-')) continue;
      const v = (el.getAttribute(a) || '').trim();
      if (!v || !(explicit || URLISH.test(v))) continue;
      cands.push({a, v, explicit, hint: NAME_HINT.test(a)});
    }
    const picked = cands.filter(c => c.explicit);
    if (!picked.length) {
      const hinted = cands.filter(c => c.hint);
      if (hinted.length) picked.push(...hinted); else if (cands.length === 1) picked.push(cands[0]);
    }
    for (const {a, v} of picked) {
      let to = /poster/i.test(a) ? 'poster' : (/set$/i.test(a) || /\s\d+(\.\d+)?[wx](,|$)/.test(v) ? 'srcset' : 'src');
      if (to === 'src' && el.tagName === 'SOURCE' && el.parentElement && el.parentElement.tagName === 'PICTURE') to = 'srcset';
      if (PLACEHOLDER(el.getAttribute(to))) { el.setAttribute(to, v); st.lazy++; }
    }
    if (el.getAttribute('loading') === 'lazy') el.setAttribute('loading', 'eager');
  });
  if (o.absolute) {
    const skip = v => !v || /^(#|javascript:|mailto:|tel:|data:|blob:|about:)/i.test(v);
    const abs = v => { try { return new URL(v, document.baseURI).href; } catch (e) { return v; } };
    document.querySelectorAll('[href],[src],[poster],[action],[data-src]').forEach(el => {
      for (const a of ['href','src','poster','action','data-src']) {
        const v = el.getAttribute(a); if (skip(v)) continue;
        const r = abs(v); if (r !== v) { el.setAttribute(a, r); st.abs++; }
      }
    });
    document.querySelectorAll('[srcset]').forEach(el => {
      const v = el.getAttribute('srcset');
      const out = v.split(/,\s+(?=\S)/).map(p => { const [u, ...rest] = p.trim().split(/\s+/);
        return [abs(u), ...rest].join(' '); }).join(', ');
      if (out !== v) { el.setAttribute('srcset', out); st.abs++; }
    });
  }
  return st;
}"""


def more_phrases(a) -> list[str]:
    """'Show more' phrases for the selected languages (default: all in data/more_phrases.json) + --more-phrase."""
    data = load_json("more_phrases.json")
    langs = a.more_lang or [k for k in data if not k.startswith("_")]
    return [ph for lang in langs for ph in data.get(lang, [])] + list(a.more_phrase or [])


def gradual_scroll(page, max_steps=GRADUAL_MAX_STEPS):
    """First pass: walk down one viewport at a time so IntersectionObserver-driven content fires."""
    vh = page.evaluate("window.innerHeight") or 800
    y = 0
    for _ in range(max_steps):
        if y >= page.evaluate(METRICS_JS)[0]:
            break
        page.evaluate(f"window.scrollTo(0,{y})")
        page.wait_for_timeout(GRADUAL_STEP_PAUSE_MS)
        y += vh


def force_load(page, a) -> dict:
    """Scroll/click until the page stops growing. Returns stats."""
    opts = {"pattern": a.more_pattern, "phrases": more_phrases(a), "expand": not a.no_expand, "selectors": a.click or [],
            "maxLabelChars": MAX_LABEL_CHARS, "suffixSlack": LABEL_SUFFIX_SLACK}
    stats = {"rounds": 0, "clicks": 0}
    gradual_scroll(page)
    prev, stable = None, 0
    for rnd in range(1, a.max_rounds + 1):
        stats["rounds"] = rnd
        stats["clicks"] += page.evaluate(CLICK_JS, opts)
        page.evaluate(SCROLL_JS, MAX_SCROLL_CONTAINERS)
        page.wait_for_timeout(a.scroll_pause_ms)
        try:
            page.wait_for_load_state("networkidle", timeout=NETWORKIDLE_PROBE_MS)
        except Exception:
            pass
        cur = tuple(page.evaluate(METRICS_JS))
        stable = stable + 1 if cur == prev else 0
        prev = cur
        print(f"    round {rnd}: height={cur[0]} elements={cur[1]} clicks={stats['clicks']}")
        if stable >= a.stable_rounds:
            break
    else:
        print(f"    reached --max-rounds {a.max_rounds}; page may have more content")
    stats["height"], stats["elements"] = prev or (0, 0)
    page.evaluate("window.scrollTo(0,0)")
    return stats


def include_iframes(page, fopts) -> int:
    n = 0
    for frame in page.frames[1:MAX_IFRAMES + 1]:
        try:
            frame.evaluate(FINALIZE_JS, fopts)
            html = frame.evaluate("document.body ? document.body.innerHTML : ''")
            if not html.strip():
                continue
            frame.frame_element().evaluate(
                "(el, html) => { const d = document.createElement('div');"
                " d.setAttribute('data-iframe-src', el.getAttribute('src') || 'srcdoc'); d.innerHTML = html; el.after(d); }", html)
            n += 1
        except Exception:
            continue
    return n


def snapshot(browser, url: str, a, out: Path, dev: dict | None = None) -> dict:
    if dev:
        ctx_args = dict(dev)
        if a.user_agent:
            ctx_args["user_agent"] = a.user_agent
    else:
        w, h = resolve_viewport(a, (1366, 900))
        ctx_args = {"user_agent": a.user_agent or default_user_agent(browser.version),
                    "viewport": {"width": w, "height": h},
                    "device_scale_factor": a.scale}
    if a.theme:
        ctx_args["color_scheme"] = a.theme
    if a.storage_state:
        ctx_args["storage_state"] = a.storage_state
    ctx = browser.new_context(**ctx_args)
    page = ctx.new_page()
    seed_theme(page, a.theme, a.theme_key)
    api: list[dict] = []

    if a.api:
        def on_resp(r):
            try:
                if "json" in r.headers.get("content-type", "").lower() and r.status == 200 and len(api) < API_MAX_ENTRIES:
                    body = r.text()
                    if len(body) <= API_MAX_BYTES:
                        try:
                            data = json.loads(body)
                        except Exception:
                            data = body
                        api.append({"url": r.url, "method": r.request.method, "data": data})
            except Exception:
                pass
        page.on("response", on_resp)

    print(f"[+] {url}")
    resp = None
    try:
        resp = page.goto(url, wait_until=a.wait_until, timeout=a.timeout)
    except Exception as e:                      # keep going with whatever rendered
        print(f"    navigation notice: {str(e).splitlines()[0]}")
    apply_theme(page, a.theme)
    ctype = (resp.headers.get("content-type", "") if resp else "").lower()
    if ctype and not any(k in ctype for k in ("html", "xml")):
        print(f"    warning: the response is {ctype!r}, not HTML; the saved DOM is only the browser's rendering of that file")
    if a.wait_for:
        try:
            page.wait_for_selector(a.wait_for, timeout=a.timeout)
        except Exception:
            print(f"    --wait-for {a.wait_for!r} never appeared")

    stats = {"rounds": 0, "clicks": 0}
    if not a.no_force:
        stats = force_load(page, a)
    elif a.click:
        stats["clicks"] += page.evaluate(CLICK_JS, {"pattern": a.more_pattern, "expand": False, "selectors": a.click})
    if a.wait_ms:
        page.wait_for_timeout(a.wait_ms)

    fopts = {"shadow": not a.no_shadow, "absolute": not a.keep_relative, "lazyAttrs": a.lazy_attr or []}
    fin = page.evaluate(FINALIZE_JS, fopts)
    frames = include_iframes(page, fopts) if a.iframes else 0
    if frames:       # iframe content was inserted into the main page: make its links absolute too
        page.evaluate(FINALIZE_JS, {"shadow": False, "absolute": fopts["absolute"]})

    html = page.content()
    text = page.evaluate("document.body ? document.body.innerText : ''") if a.text else None
    final_url = page.url
    ctx.close()

    if a.base_tag and "<base" not in html.lower():
        tag = f'<base href="{final_url}">'
        html, k = re.subn(r"(<head[^>]*>)", r"\1\n" + tag, html, count=1, flags=re.I)
        if not k:
            html = tag + html

    ensure_parent(str(out))
    out.write_text(html, encoding="utf-8")
    sidecars = []
    if text is not None:
        t = out.with_suffix(".txt"); t.write_text(text, encoding="utf-8"); sidecars.append(str(t))
    if a.api:
        j = out.with_suffix(".responses.json"); j.write_text(json.dumps(api, indent=2, ensure_ascii=False), encoding="utf-8")
        sidecars.append(f"{j} ({len(api)} JSON responses)")

    n_el = len(re.findall(r"<[a-zA-Z]", html))
    print(f"    rounds={stats['rounds']} clicks={stats['clicks']} details_opened={fin['details']} "
          f"shadow_roots={fin['shadow']} lazy_promoted={fin['lazy']} iframes={frames}")
    print(f"Saved: {out} ({len(html):,} chars, ~{n_el:,} tags)")
    for s in sidecars:
        print(f"Saved: {s}")
    return {"url": url, "file": str(out)}


# ---------- CLI ----------
def add_args(p):
    p.add_argument("urls_pos", nargs="*", metavar="URL", help="Pages to snapshot (URL, bare domain, or local HTML path)")
    p.add_argument("--url", "--urls", dest="url", nargs="+", default=[], metavar="URL", help="Same as positionals")
    add_output_args(
        p,
        dir_help="Folder for several pages: <dir>/<name>.html (default .capture/dom)",
        default_dir=".capture/dom",
    )
    add_json_args(p)
    g = p.add_argument_group("forcing content to load (on by default)")
    g.add_argument("--no-force", action="store_true", help="Plain snapshot: no scrolling/clicking loop")
    g.add_argument("--max-rounds", type=int, default=20, help="Cap on scroll/click rounds (default 20)")
    g.add_argument("--stable-rounds", type=int, default=2, help="Stop after N rounds with no growth (default 2)")
    g.add_argument("--scroll-pause-ms", type=int, default=800, help="Pause after each round (default 800)")
    g.add_argument("--click", action="append", metavar="SELECTOR",
                   help="Also click elements matching this CSS selector every round (repeatable)")
    g.add_argument("--no-expand", action="store_true", help="Do not auto-click Load/Show/Read more buttons or open accordions")
    g.add_argument("--more-lang", nargs="+", metavar="CODE", choices=sorted(k for k in load_json("more_phrases.json") if not k.startswith("_")),
                   help="Languages of 'show more' phrases to recognise (default: all in data/more_phrases.json)")
    g.add_argument("--more-phrase", action="append", metavar="TEXT", help="Extra button text that means 'show more' (repeatable)")
    g.add_argument("--more-pattern", default=None, help="Extra regex for button text that means 'show more' (in addition to the phrases)")
    g.add_argument("--lazy-attr", action="append", metavar="NAME",
                   help="Extra attribute holding a lazy-loaded media URL (repeatable); data-* names that look like sources are found automatically")
    g.add_argument("--wait-for", metavar="SELECTOR", help="Wait for this selector before forcing content")
    c = p.add_argument_group("what ends up in the HTML")
    c.add_argument("--no-shadow", action="store_true", help="Do not flatten open shadow DOM into the HTML")
    c.add_argument("--iframes", action="store_true", help="Inline iframe contents next to each <iframe>")
    c.add_argument("--keep-relative", action="store_true", help="Leave href/src as authored (default: made absolute)")
    c.add_argument("--base-tag", action="store_true", help="Inject <base href> so the saved file renders when opened")
    c.add_argument("--text", action="store_true", help="Also write visible text to <name>.txt")
    c.add_argument("--api", action="store_true", help="Also write JSON responses seen on the wire to <name>.responses.json")
    s = p.add_argument_group("browser")
    s.add_argument("--wait-until", choices=["networkidle", "load", "domcontentloaded"], default="networkidle")
    s.add_argument("--wait-ms", type=int, default=2000, help="Final settle time before saving (default 2000)")
    s.add_argument("--timeout", type=int, default=60000, help="Navigation timeout ms (default 60000)")
    add_view_args(s)
    s.add_argument("--scale", type=float, default=1.0, help="Device pixel ratio, e.g. 2 for retina (default 1)")
    s.add_argument("--user-agent", help="Override the browser user agent")
    add_device_args(s)
    add_theme_args(s)
    add_session_args(s)
    s.add_argument("--headed", action="store_true", help="Show the browser window (debugging)")


def run(args):
    if list_devices(args, "dom"):
        return
    from playwright.sync_api import sync_playwright

    urls = list(dict.fromkeys(normalize_url(u) for u in args.urls_pos + args.url))
    if not urls:
        sys.exit("Give at least one URL.")
    check_file(args.storage_state, "--storage-state")
    if args.max_rounds < 0 or args.stable_rounds < 1 or args.scroll_pause_ms < 0 or args.wait_ms < 0 or args.timeout <= 0:
        sys.exit("--max-rounds, --scroll-pause-ms and --wait-ms cannot be negative; --stable-rounds must be at least 1 and --timeout positive")
    vw, vh = resolve_viewport(args, (1366, 900))
    if not (0 < vw <= 16384 and 0 < vh <= 16384):
        sys.exit("--width and --height must be between 1 and 16384")
    if not 0 < args.scale <= 8:
        sys.exit("--scale must be between 0 and 8")
    if args.output and len(urls) > 1:
        sys.exit("--output is for a single page; use --output-dir for several.")

    failures = []
    saved = []
    payload = {"command": "dom", "files": saved, "failed": failures}
    with begin(args) as real:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not args.headed)
            dev = resolve_device(p, args.device) if args.device else None
            try:
                for url in urls:
                    out = Path(resolve_output(args.output)) if args.output else Path(args.output_dir) / f"{folder_name(url)}.html"
                    try:
                        res = snapshot(browser, url, args, out, dev)
                        if res.get("file"):
                            saved.append(res["file"])
                    except Exception as e:
                        failures.append({"url": url, "error": str(e)})
                        print(f"FAILED {url}: {e}", file=sys.stderr)
            finally:
                browser.close()
    emit(args, payload, real)
    if failures:
        sys.exit(f"{len(failures)} of {len(urls)} page(s) failed: "
                 + ", ".join(f["url"] for f in failures))


if __name__ == "__main__":
    from _common import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_args(ap)
    try:
        run(ap.parse_args())
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
