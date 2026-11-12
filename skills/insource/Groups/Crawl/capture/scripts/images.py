#!/usr/bin/env python3
"""
`capture images` — download every image a page can show, at its highest resolution.

Visits a URL, waits for network idle, optionally scrolls (a pixel count, to the end of
the page, or until a target text match appears) to trigger lazy loading, records each
image request with the scroll position where it first appeared, upgrades every asset to
its canonical original where reachable, deduplicates resized and perceptually identical
variants, applies --between / --exclude / --min-bytes filters, and writes a JSON report
that explains every keep, drop and failure.

TLS/JA3 impersonation via curl_cffi covers WAF-protected endpoints (Medium's /_/graphql
and the original-resolution asset URLs) without an external bridge or subprocess.

Run it through the dispatcher:
  python capture.py images --url https://example.com --scroll to-end --exclude "small|medium"
Directly (same flags):
  python images.py --url https://example.com --output-dir .capture/images
"""

from __future__ import annotations

import argparse
import asyncio
import datetime
import hashlib
import io
import json
import math
import os
import re
import sys
import time
from urllib.parse import urlparse, urljoin

from _cli import (add_device_args, add_json_args, add_output_args, add_session_args,  # noqa: E402
                  add_theme_args, add_view_args, begin, check_file, emit, list_devices,
                  resolve_device, resolve_viewport)
from _common import default_user_agent

# Third-party modules are imported by load_deps() at run time, so that `capture.py`
# can import this command on a machine without them (same convention as the browser
# commands) and the error names the missing package instead of crashing the dispatcher.
async_playwright = None
cffi_requests = None
Image = None

INSTALL_HINT = ('pip install "playwright>=1.40" "curl_cffi>=0.6" "Pillow>=10.0" '
                "&& python -m playwright install chromium")


def load_deps():
    """Import playwright / curl_cffi / Pillow into this module's globals, or exit clearly."""
    global async_playwright, cffi_requests, Image
    try:
        from playwright.async_api import async_playwright as _playwright
        from curl_cffi import requests as _cffi
        from PIL import Image as _Image
    except ImportError as e:
        raise SystemExit(f"Missing dependency '{e.name}' for capture images. Install: {INSTALL_HINT}")
    async_playwright, cffi_requests, Image = _playwright, _cffi, _Image



def detect_image_ext(buffer: bytes) -> str | None:
    if not buffer or len(buffer) < 4:
        return None
    # PNG: 89 50 4E 47
    if buffer[:4] == b'\x89PNG':
        return '.png'
    # JPEG: FF D8 FF
    if buffer[:3] == b'\xff\xd8\xff':
        return '.jpg'
    # GIF: GIF87a or GIF89a
    if buffer[:3] == b'GIF':
        return '.gif'
    # WEBP: RIFF....WEBP
    if len(buffer) >= 12 and buffer[:4] == b'RIFF' and buffer[8:12] == b'WEBP':
        return '.webp'
    # AVIF / HEIC (ftypavif / ftypisom)
    if len(buffer) >= 12 and buffer[4:8] == b'ftyp':
        ftype = buffer[8:12]
        if ftype in (b'avif', b'avis'):
            return '.avif'
    # SVG
    if b'<svg' in buffer[:300].lower():
        return '.svg'
    return None


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9._-]', '_', name)[:200]
    return cleaned or 'image'


def normalize_text(text: str) -> str:
    """Normalize text across quotes, unicode replacement characters, dashes, and whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[\u2018\u2019\u201a\u201b'`\ufffd\u00ad�]", "'", text)
    text = re.sub(r'[\u201c\u201d\u201e\u201f"]', '"', text)
    text = re.sub(r"[\u2013\u2014\u2212-]", "-", text)
    text = re.sub(r"[^a-z0-9']", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_canonical_asset_info(url: str) -> tuple[str, str | None]:
    """
    Returns (canonical_id, original_url_candidate).
    Extracts the core image identity so multiple resizes map to the same image.
    For Medium/Miro images, extracts the original unresized URL.
    """
    clean_url = url.split('#')[0]
    parsed = urlparse(clean_url)
    domain = parsed.netloc.lower()
    path = parsed.path

    # Medium CDN: miro.medium.com or cdn-images-*.medium.com
    if 'medium.com' in domain:
        # Match asset ID like 1*8OgOeQ3TtocGsUdAQvo_RA.jpeg or 0*dThUCAgUA5N75ttY
        m = re.search(r'([01]\*[a-zA-Z0-9_\-@]+(?:\.[a-zA-Z0-9]+)?)', path)
        if m:
            asset_id = m.group(1)
            canonical_id = f"medium:{asset_id}"
            original_url = f"https://miro.medium.com/{asset_id}"
            return canonical_id, original_url

    # WordPress / generic resize suffix: e.g. image-300x200.jpg -> image.jpg
    m_wp = re.search(r'^(.*)-\d+x\d+(\.[a-zA-Z0-9]+)$', path)
    if m_wp:
        orig_path = f"{m_wp.group(1)}{m_wp.group(2)}"
        orig_url = f"{parsed.scheme}://{parsed.netloc}{orig_path}"
        canonical_id = f"file:{os.path.basename(orig_path)}"
        return canonical_id, orig_url

    # Generic: strip query params and use basename
    base = os.path.basename(path)
    if not base or base == '/':
        h = hashlib.md5(clean_url.encode('utf-8')).hexdigest()[:12]
        base = f"image_{h}"
    canonical_id = f"file:{base}"
    return canonical_id, clean_url.split('?')[0]


def get_image_info(buffer: bytes) -> tuple[int, int, int | None]:
    """Returns (width, height, dhash_int)."""
    if not buffer or len(buffer) < 8:
        return 0, 0, None
    try:
        with Image.open(io.BytesIO(buffer)) as im:
            w, h = im.size
            if w <= 0 or h <= 0:
                return 0, 0, None
            # Compute 64-bit dhash for perceptual comparison
            small = im.convert('L').resize((9, 8), Image.Resampling.LANCZOS)
            if hasattr(small, 'get_flattened_data'):
                pixels = list(small.get_flattened_data())
            elif hasattr(small, 'getdata'):
                pixels = list(small.getdata())
            else:
                pixels = list(small.tobytes())
            diff = []
            for row in range(8):
                row_start = row * 9
                for col in range(8):
                    diff.append(pixels[row_start + col] > pixels[row_start + col + 1])
            dhash_int = sum(1 << i for i, v in enumerate(diff) if v)
            return w, h, dhash_int
    except Exception:
        return 0, 0, None


def get_image_size_label(width: int, height: int) -> str:
    """
    Classifies an image into small | medium | large | larger.
    - small: thumbnail / avatar scale (max dimension <= 150)
    - medium: icon / card scale (max dimension <= 400)
    - large: content / banner scale (max dimension <= 1200)
    - larger: hero / full-resolution original scale (max dimension > 1200)
    """
    max_dim = max(width, height)
    if max_dim <= 150:
        return 'small'
    elif max_dim <= 400:
        return 'medium'
    elif max_dim <= 1200:
        return 'large'
    else:
        return 'larger'


def parse_exclude_rules(exclude_val: str | None) -> list[dict]:
    """
    Parses --exclude argument into a list of rules.
    Supports comma- or pipe-separated rules such as:
      "200x200", "small", "small,medium", "small | medium | large | larger"
      "<200x200", "<=200x200", ">1200x1200"
    """
    if not exclude_val or not str(exclude_val).strip():
        return []

    rules = []
    # Split by comma or pipe
    tokens = [t.strip() for t in re.split(r'[,|]+', str(exclude_val)) if t.strip()]

    for token in tokens:
        low = token.lower()
        if low in ('small', 'medium', 'large', 'larger'):
            rules.append({'type': 'label', 'value': low, 'raw': token})
            continue

        # Check dimension pattern like 200x200, <=200x200, <200x200, >=200x200, >200x200
        m = re.match(r'^([<>]=?)?\s*(\d+)\s*[xX*]\s*(\d+)$', token)
        if m:
            op = m.group(1) or '<='
            w = int(m.group(2))
            h = int(m.group(3))
            rules.append({
                'type': 'dim',
                'op': op,
                'width': w,
                'height': h,
                'raw': token,
            })
            continue

        # Single number shorthand (e.g. 200 -> 200x200)
        m_single = re.match(r'^([<>]=?)?\s*(\d+)$', token)
        if m_single:
            op = m_single.group(1) or '<='
            val = int(m_single.group(2))
            rules.append({
                'type': 'dim',
                'op': op,
                'width': val,
                'height': val,
                'raw': token,
            })
            continue

        raise ValueError(f"Unknown --exclude rule: '{token}'. Must be 'small', 'medium', 'large', 'larger', or '<width>x<height>' (e.g. 200x200).")

    return rules


def matches_exclude(width: int, height: int, rules: list[dict]) -> tuple[bool, str | None]:
    """
    Checks if an image with (width, height) matches any exclude rule.
    Returns (True, reason) if excluded, or (False, None) otherwise.
    """
    if not rules or width <= 0 or height <= 0:
        return False, None

    img_label = get_image_size_label(width, height)

    for rule in rules:
        if rule['type'] == 'label':
            if img_label == rule['value']:
                return True, f"Matches size label '{rule['value']}' ({width}x{height})"
        elif rule['type'] == 'dim':
            rw = rule['width']
            rh = rule['height']
            op = rule['op']
            if op in ('<=', '<'):
                # Images within / under the specified dimensions
                if (op == '<=' and width <= rw and height <= rh) or (op == '<' and width < rw and height < rh):
                    return True, f"Dimensions ({width}x{height}) {op} {rw}x{rh}"
            elif op in ('>=', '>'):
                if (op == '>=' and width >= rw and height >= rh) or (op == '>' and width > rw and height > rh):
                    return True, f"Dimensions ({width}x{height}) {op} {rw}x{rh}"

    return False, None


def hamming_distance(h1: int | None, h2: int | None) -> int:
    if h1 is None or h2 is None:
        return 999
    return bin(h1 ^ h2).count('1')


def filename_from_url(img_url: str, buffer: bytes | None = None) -> str:
    try:
        parsed = urlparse(img_url)
        base = os.path.basename(parsed.path)
        root, ext = os.path.splitext(base)

        real_ext = detect_image_ext(buffer) if buffer else None
        if real_ext:
            if ext:
                base = f"{root}{real_ext}"
            else:
                base = f"{base}{real_ext}"
        elif not base or base == '/' or not ext:
            h = hashlib.md5(img_url.encode('utf-8')).hexdigest()[:10]
            base = f"image-{h}.jpg"
        return sanitize_filename(base)
    except Exception:
        real_ext = detect_image_ext(buffer) or '.jpg' if buffer else '.jpg'
        h = hashlib.md5(img_url.encode('utf-8')).hexdigest()[:10]
        return f"image-{h}{real_ext}"


def is_likely_image_request(request) -> bool:
    if request.resource_type == 'image':
        return True
    u = request.url.split('?')[0].lower()
    return bool(re.search(r'\.(png|jpe?g|gif|webp|avif|svg|bmp)$', u))


TEXT_FINDER_JS = '''(searchQuery) => {
    function norm(s) {
        if (!s) return '';
        return s.toLowerCase()
            .replace(/[\\u2018\\u2019\\u201a\\u201b'`\\ufffd\\u00ad�]/g, "'")
            .replace(/[\\u201c\\u201d\\u201e\\u201f\"]/g, '\"')
            .replace(/[\\u2013\\u2014\\u2212\\-]/g, '-')
            .replace(/[^a-z0-9']/g, ' ')
            .replace(/\\s+/g, ' ')
            .trim();
    }

    const qNorm = norm(searchQuery);
    if (!qNorm) return null;

    // Check DOM elements
    const elements = Array.from(document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, blockquote, li, td, th, div, span, section, article'));
    let bestMatch = null;
    let shortestLength = Infinity;

    for (const el of elements) {
        const text = el.innerText || el.textContent || '';
        const eNorm = norm(text);
        if (!eNorm) continue;

        // Check if query is in element or element is in query
        if (eNorm.includes(qNorm) || qNorm.includes(eNorm)) {
            // Prefer more specific (shorter) elements
            if (eNorm.length < shortestLength) {
                shortestLength = eNorm.length;
                const rect = el.getBoundingClientRect();
                bestMatch = {
                    found: true,
                    top: rect.top + window.scrollY,
                    bottom: rect.bottom + window.scrollY,
                    text: text.trim().substring(0, 160)
                };
            }
        }
    }

    // Fallback: check tree walker text nodes if no element matched
    if (!bestMatch) {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let node;
        while (node = walker.nextNode()) {
            const nNorm = norm(node.nodeValue);
            if (nNorm && (nNorm.includes(qNorm) || qNorm.includes(nNorm))) {
                const parent = node.parentElement;
                if (parent) {
                    const rect = parent.getBoundingClientRect();
                    return {
                        found: true,
                        top: rect.top + window.scrollY,
                        bottom: rect.bottom + window.scrollY,
                        text: node.nodeValue.trim().substring(0, 160)
                    };
                }
            }
        }
    }

    return bestMatch;
}'''


async def find_text_position(page, query: str):
    if not query or not query.strip():
        return None
    try:
        return await page.evaluate(TEXT_FINDER_JS, query)
    except Exception as e:
        print(f"Error searching text '{query[:40]}...': {e}", file=sys.stderr)
        return None


def add_args(parser):
    """Register the `images` flags on a parser (dispatcher subparser or standalone)."""
    parser.add_argument('url_pos', nargs='?', metavar='URL', help="Page to visit")
    parser.add_argument('--url', dest='url_opt', help="Page to visit, same as the positional")
    add_output_args(parser, single=False, default_dir='.capture/images',
                    dir_help="Download directory (default .capture/images)")
    parser.add_argument('--report', default=None, help="Report JSON path (default: <output-dir>/report.json)")
    parser.add_argument('--scroll', default='0', help='Total px to scroll, "to-end" for whole page, or matching text to scroll to (default: 0)')
    parser.add_argument('--scroll-step', type=int, default=800, help="Px per scroll step (default: 800)")
    parser.add_argument('--scroll-wait', type=int, default=700, help="Wait after each scroll step (ms, default: 700)")
    parser.add_argument('--between', default=None, help='Filter range: "min,max" px, or text matching e.g. "start_text,end_text" or "text"')
    parser.add_argument('--exclude', default=None, help='Exclude images matching dimension (e.g. 200x200) or size labels ("small | medium | large | larger")')
    parser.add_argument('--idle-timeout', type=int, default=10000, help="networkidle wait timeout in ms (default: 10000)")
    parser.add_argument('--timeout', type=int, default=120000, help="Overall hard timeout in ms (default: 120000)")
    parser.add_argument('--nav-timeout', type=int, default=30000, help="Initial navigation timeout in ms (default: 30000)")
    parser.add_argument('--wait-until', choices=["networkidle", "load", "domcontentloaded"], default="domcontentloaded",
                        help="Initial navigation readiness (default: domcontentloaded)")
    parser.add_argument('--wait-ms', type=int, default=0, help="Extra settle time after navigation, ms (default: 0)")
    parser.add_argument('--concurrency', type=int, default=5, help="Accepted for compatibility (unused)")
    parser.add_argument('--min-bytes', type=int, default=0, help="Skip images smaller than this many bytes (default: 0)")
    add_view_args(parser)
    parser.add_argument('--scale', type=float, default=1.0, help="Device pixel ratio, e.g. 2 for retina (default 1)")
    parser.add_argument('--user-agent', default=None,
                        help="User agent (default: browser-like; env CAPTURE_USER_AGENT overrides)")
    add_device_args(parser)
    add_session_args(parser)
    add_theme_args(parser)
    parser.add_argument('--headed', action='store_true', help="Run browser headed")
    parser.add_argument('--no-pretty', action='store_true', help="Emit compact JSON report")
    add_json_args(parser)
    return parser


def prepare(args):
    """Validate and normalise before any browser starts. Returns the exclude rules."""
    args.url = args.url_opt or args.url_pos
    if not args.url:
        raise SystemExit("Give the page URL (positional or --url).")
    check_file(args.storage_state, "--storage-state")
    bad = []
    for name in ("timeout", "nav_timeout", "idle_timeout", "scroll_step",
                 "scroll_wait", "wait_ms", "min_bytes", "concurrency"):
        value = getattr(args, name)
        if value < 0:
            bad.append("--" + name.replace("_", "-") + " cannot be negative (got " + str(value) + ")")
    for name in ("timeout", "nav_timeout"):
        if getattr(args, name) == 0:
            bad.append("--" + name.replace("_", "-") + " must be greater than 0")
    vw, vh = resolve_viewport(args)
    if not (0 < vw <= 16384 and 0 < vh <= 16384):
        bad.append("--width and --height must be between 1 and 16384")
    if not 0 < args.scale <= 8:
        bad.append("--scale must be between 0 and 8 (got " + str(args.scale) + ")")
    if bad:
        raise SystemExit("INVALID OPTION(S): " + "; ".join(bad))
    exclude_rules = []
    if args.exclude:
        try:
            exclude_rules = parse_exclude_rules(args.exclude)
        except Exception as e:
            raise SystemExit(f"Invalid --exclude: {e}")
    if not args.report:
        args.report = os.path.join(args.output_dir, 'report.json')
    return exclude_rules


async def run_async(args, exclude_rules):
    start_time = time.time()
    deadline = start_time + (args.timeout / 1000.0)

    def check_timeout(label: str):
        if time.time() > deadline:
            raise TimeoutError(f"Overall --timeout ({args.timeout}ms) exceeded during: {label}")

    os.makedirs(args.output_dir, exist_ok=True)

    cffi_session = cffi_requests.Session(impersonate="chrome120")

    # Determine scroll mode
    scroll_arg = str(args.scroll).strip()
    scroll_mode = 'none'  # 'px', 'to-end', 'text'
    scroll_target_px = 0
    scroll_target_text = None

    if scroll_arg.lower() in ('to-end', 'to_end', 'end'):
        scroll_mode = 'to-end'
    elif scroll_arg.isdigit():
        scroll_target_px = int(scroll_arg)
        scroll_mode = 'px' if scroll_target_px > 0 else 'none'
    else:
        scroll_mode = 'text'
        scroll_target_text = scroll_arg

    print(f"Visiting: {args.url}")
    print(f"Scroll mode: {scroll_mode} (arg='{scroll_arg[:60]}...')")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=not args.headed,
            args=['--disable-blink-features=AutomationControlled'],
        )
        if args.device:
            ctx_kwargs = dict(resolve_device(pw, args.device))
            if args.user_agent:
                ctx_kwargs['user_agent'] = args.user_agent
        else:
            vw, vh = resolve_viewport(args)
            ctx_kwargs = {
                'user_agent': args.user_agent or default_user_agent(),
                'viewport': {'width': vw, 'height': vh},
                'device_scale_factor': args.scale,
            }
        if args.theme:
            ctx_kwargs['color_scheme'] = args.theme
        if args.storage_state:
            ctx_kwargs['storage_state'] = args.storage_state
        context = await browser.new_context(**ctx_kwargs)
        page = await context.new_page()
        if args.theme and args.theme_key:
            await page.add_init_script("try{localStorage.setItem(%r,%r)}catch(e){}" % (args.theme_key, args.theme))

        # Handle Cloudflare-protected API calls like Medium's GraphQL via curl_cffi directly in Python
        async def handle_route(route):
            req = route.request
            try:
                loop = asyncio.get_running_loop()
                req_url = req.url
                req_method = req.method
                req_headers = {k: v for k, v in req.headers.items() if k.lower() not in ['host', 'content-length', 'connection', 'accept-encoding']}
                req_body = req.post_data

                def do_fetch():
                    if req_method.upper() == 'POST':
                        return cffi_session.post(req_url, data=req_body, headers=req_headers, timeout=25)
                    else:
                        return cffi_session.get(req_url, headers=req_headers, timeout=25)

                resp = await loop.run_in_executor(None, do_fetch)
                resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in ['transfer-encoding', 'content-encoding', 'connection']}
                await route.fulfill(
                    status=resp.status_code,
                    headers=resp_headers,
                    body=resp.content,
                )
            except Exception as e:
                # If page is closing or closed, ignore route errors
                if "closed" not in str(e).lower():
                    print(f"[curl_cffi] Proxying error for {req.url}: {e}", file=sys.stderr)
                try:
                    await route.continue_()
                except Exception:
                    pass

        await page.route("**/_/graphql", handle_route)

        seen_images = {}  # url -> {"firstSeenAtScrollPx": int, "firstSeenAt": float}
        current_scroll_px = 0

        image_buffers = {}  # url -> bytes
        image_auth_blocked = {}  # url -> status
        image_fetch_errors = {}  # url -> str
        pending_body_reads = []

        def on_response(response):
            nonlocal current_scroll_px
            request = response.request
            if not is_likely_image_request(request):
                return
            u = response.url
            if u not in seen_images:
                seen_images[u] = {
                    "firstSeenAtScrollPx": current_scroll_px,
                    "firstSeenAt": time.time(),
                }

            status = response.status
            if status in (401, 403):
                image_auth_blocked[u] = status
                return
            if status < 200 or status >= 300:
                image_fetch_errors[u] = f"HTTP {status}"
                return

            async def read_body():
                try:
                    buf = await response.body()
                    image_buffers[u] = buf
                except Exception as err:
                    image_fetch_errors[u] = str(err)

            pending_body_reads.append(asyncio.create_task(read_body()))

        page.on("response", on_response)

        nav_error = None
        try:
            await page.goto(args.url, wait_until=args.wait_until, timeout=args.nav_timeout)
            await page.wait_for_load_state('networkidle', timeout=args.idle_timeout)
        except Exception as err:
            nav_error = str(err)
            print(f"Warning: initial load/idle wait had an issue: {nav_error}", file=sys.stderr)
        if args.theme:
            await page.evaluate("t=>{const r=document.documentElement;"
                                "r.classList.toggle('dark',t==='dark');r.setAttribute('data-theme',t)}", args.theme)
        if args.wait_ms:
            await page.wait_for_timeout(args.wait_ms)

        check_timeout('initial page load')

        # Scrolling phase
        scroll_log = []
        text_match_result = None
        at_end_count = 0
        last_page_height = 0

        if scroll_mode != 'none':
            scrolled = 0
            reached_target = False

            while not reached_target:
                check_timeout('scroll loop')
                count_before = len(seen_images)

                # Check if target text already reached before scrolling further
                if scroll_mode == 'text':
                    match = await find_text_position(page, scroll_target_text)
                    if match:
                        text_match_result = match
                        # Check if element is at or above viewport bottom
                        view_bottom = await page.evaluate("window.scrollY + window.innerHeight")
                        if view_bottom >= match["top"]:
                            print(f"Target text matched at Y={match['top']:.1f}px: '{match['text'][:60]}...'. Stopping scroll.")
                            reached_target = True
                            break

                # Determine step size
                if scroll_mode == 'px':
                    remaining = scroll_target_px - scrolled
                    if remaining <= 0:
                        break
                    step = min(args.scroll_step, remaining)
                else:
                    step = args.scroll_step

                await page.evaluate("(px) => window.scrollBy(0, px)", step)
                scrolled += step
                current_scroll_px = scrolled

                await page.wait_for_timeout(args.scroll_wait)

                count_after = len(seen_images)
                scroll_log.append({
                    "fromPx": scrolled - step,
                    "toPx": scrolled,
                    "newImagesThisStep": count_after - count_before,
                })
                print(f"Scrolled to {scrolled}px — {count_after - count_before} new image request(s) (total so far: {count_after})")

                # Check text match after step
                if scroll_mode == 'text':
                    match = await find_text_position(page, scroll_target_text)
                    if match:
                        text_match_result = match
                        view_bottom = await page.evaluate("window.scrollY + window.innerHeight")
                        if view_bottom >= match["top"]:
                            print(f"Target text reached at Y={match['top']:.1f}px: '{match['text'][:60]}...'. Stopping scroll.")
                            reached_target = True
                            break

                # Check page bottom / to-end termination
                scroll_metrics = await page.evaluate('''() => ({
                    scrollY: window.scrollY,
                    innerHeight: window.innerHeight,
                    scrollHeight: Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)
                })''')
                current_height = scroll_metrics["scrollHeight"]
                is_at_bottom = (scroll_metrics["scrollY"] + scroll_metrics["innerHeight"] >= current_height - 15)

                if is_at_bottom and current_height == last_page_height:
                    at_end_count += 1
                else:
                    at_end_count = 0
                last_page_height = current_height

                if scroll_mode == 'to-end' and at_end_count >= 2:
                    print(f"Reached end of page at {current_height}px. Stopping scroll.")
                    reached_target = True
                    break

                if scroll_mode == 'text' and at_end_count >= 3:
                    print("Reached end of page without finding target text. Stopping scroll.")
                    reached_target = True
                    break

                if scroll_mode == 'px' and scrolled >= scroll_target_px:
                    reached_target = True
                    break

        # Check if text matching is required for --between
        between_bounds = None
        if args.between:
            between_str = str(args.between).strip()
            # Can be "min,max" or "textA,textB" or "text" or "0,text"
            if ',' in between_str:
                parts = [p.strip() for p in between_str.split(',', 1)]
                p1, p2 = parts[0], parts[1]

                # Resolve start
                min_y = 0
                if p1:
                    if p1.isdigit():
                        min_y = int(p1)
                    else:
                        m1 = await find_text_position(page, p1)
                        if m1:
                            min_y = m1["top"]
                            print(f"--between start text matched at {min_y:.1f}px: '{m1['text'][:50]}...'")

                # Resolve end
                max_y = float('inf')
                if p2:
                    if p2.isdigit():
                        max_y = int(p2)
                    else:
                        m2 = await find_text_position(page, p2)
                        if m2:
                            max_y = m2["bottom"]
                            print(f"--between end text matched at {max_y:.1f}px: '{m2['text'][:50]}...'")

                between_bounds = (min_y, max_y)
            else:
                # Single text or single number
                if between_str.isdigit():
                    between_bounds = (0, int(between_str))
                else:
                    m = await find_text_position(page, between_str)
                    if m:
                        between_bounds = (0, m["bottom"])
                        print(f"--between text matched up to {m['bottom']:.1f}px: '{m['text'][:50]}...'")

        # Feed detection heuristic
        looks_like_infinite_feed = False
        feed_detection_reasoning = "No scrolling performed (--scroll not set), cannot assess."

        if scroll_log:
            tail_count = max(2, math.ceil(len(scroll_log) * 0.3))
            tail_steps = scroll_log[-tail_count:]
            tail_new_images = sum(s["newImagesThisStep"] for s in tail_steps)
            tail_steps_with_new_images = sum(1 for s in tail_steps if s["newImagesThisStep"] > 0)
            last_step = scroll_log[-1]

            if last_step["newImagesThisStep"] > 0 and tail_steps_with_new_images == len(tail_steps):
                looks_like_infinite_feed = True
                feed_detection_reasoning = (
                    f"Every one of the last {len(tail_steps)} scroll step(s) (covering the final "
                    f"{tail_steps[0]['fromPx']}px–{last_step['toPx']}px) "
                    f"produced new image requests ({tail_new_images} total in that window), with no sign of "
                    f"tapering off by the time scrolling stopped. This suggests the feed would likely keep "
                    f"producing more images beyond the configured scroll limit."
                )
            elif last_step["newImagesThisStep"] == 0:
                looks_like_infinite_feed = False
                reversed_log = list(reversed(scroll_log))
                last_non_zero_idx = next((i for i, s in enumerate(reversed_log) if s["newImagesThisStep"] > 0), -1)
                tapered_at_step = len(scroll_log) - last_non_zero_idx if last_non_zero_idx != -1 else 0
                step_px = scroll_log[max(0, tapered_at_step - 1)]["toPx"] if tapered_at_step > 0 else 0
                feed_detection_reasoning = (
                    f"New image requests stopped appearing after scroll step {tapered_at_step} of {len(scroll_log)} "
                    f"(around {step_px}px), and the final {len(tail_steps)} step(s) produced no new images. "
                    f"This looks like a finite, fully-loaded set of images rather than an infinite feed."
                )
            else:
                looks_like_infinite_feed = False
                feed_detection_reasoning = (
                    f"New images appeared inconsistently in the tail of the scroll budget "
                    f"({tail_steps_with_new_images}/{len(tail_steps)} of the last steps had new images, but not the final step). "
                    f"Ambiguous — leaning toward NOT an infinite feed."
                )

        check_timeout('after scrolling, before download phase')

        # Filter by --between
        all_images = [
            {"url": u, "firstSeenAtScrollPx": meta["firstSeenAtScrollPx"]}
            for u, meta in seen_images.items()
        ]
        to_download = []
        excluded_by_between = []

        for img in all_images:
            if between_bounds:
                min_px, max_px = between_bounds
                if img["firstSeenAtScrollPx"] < min_px or img["firstSeenAtScrollPx"] > max_px:
                    excluded_by_between.append(img)
                    continue
            to_download.append(img)

        print(f"Found {len(all_images)} image URL(s) total. {len(to_download)} within range, {len(excluded_by_between)} excluded by --between.")

        # Ensure all queued body reads finish
        if pending_body_reads:
            await asyncio.gather(*pending_body_reads, return_exceptions=True)

        try:
            await page.unroute_all(behavior='ignoreErrors')
        except Exception:
            pass

        await context.close()
        await browser.close()

    # Phase: Deduplicate & upgrade to original highest resolution
    print("Processing images and upgrading to original/highest resolution versions...")

    # Group images by canonical identity
    canonical_groups = {}  # canonical_id -> list of img items
    for img in to_download:
        u = img["url"]
        cid, orig_candidate = parse_canonical_asset_info(u)
        if cid not in canonical_groups:
            canonical_groups[cid] = {
                "canonical_id": cid,
                "original_candidate": orig_candidate,
                "variants": [],
            }
        canonical_groups[cid]["variants"].append(img)

    downloaded = []
    auth_blocked = []
    failed = []
    skipped_small = []
    dedup_skipped = []
    excluded_by_condition = []

    # Process each canonical group
    resolved_assets = []
    for cid, group in canonical_groups.items():
        orig_url = group["original_candidate"]
        variants = group["variants"]

        best_buffer = None
        best_url = None
        best_first_seen = min(v["firstSeenAtScrollPx"] for v in variants)

        # 1. If an original unresized URL is available (e.g. Medium original miro.medium.com/1*...), try fetching it
        if orig_url:
            try:
                loop = asyncio.get_running_loop()
                resp = await loop.run_in_executor(None, lambda: cffi_session.get(orig_url, timeout=15))
                if resp.status_code == 200 and len(resp.content) > 100:
                    best_buffer = resp.content
                    best_url = orig_url
            except Exception as e:
                pass

        # 2. Compare with any captured variants to find the biggest scale / highest resolution
        for v in variants:
            vu = v["url"]
            if vu in image_auth_blocked and not best_buffer:
                auth_blocked.append({
                    "url": vu,
                    "status": image_auth_blocked[vu],
                    "firstSeenAtScrollPx": v["firstSeenAtScrollPx"],
                })
                continue

            v_buf = image_buffers.get(vu)
            if not v_buf:
                continue

            if best_buffer is None:
                best_buffer = v_buf
                best_url = vu
            else:
                # Compare resolutions
                w_best, h_best, _ = get_image_info(best_buffer)
                w_v, h_v, _ = get_image_info(v_buf)
                pixels_best = w_best * h_best
                pixels_v = w_v * h_v

                if (pixels_v > pixels_best) or (pixels_v == pixels_best and len(v_buf) > len(best_buffer)):
                    best_buffer = v_buf
                    best_url = vu

        if best_buffer:
            w, h, dh = get_image_info(best_buffer)
            resolved_assets.append({
                "canonical_id": cid,
                "url": best_url,
                "buffer": best_buffer,
                "width": w,
                "height": h,
                "pixels": w * h,
                "bytes": len(best_buffer),
                "dhash": dh,
                "firstSeenAtScrollPx": best_first_seen,
                "variants_count": len(variants),
            })
        elif not any(v["url"] in image_auth_blocked for v in variants):
            for v in variants:
                failed.append({
                    "url": v["url"],
                    "status": None,
                    "error": image_fetch_errors.get(v["url"], "No response body captured"),
                    "firstSeenAtScrollPx": v["firstSeenAtScrollPx"],
                })

    # Second pass: Perceptual deduplication across different canonical IDs (e.g. different CDNs or filenames)
    # Sort by resolution (pixels then bytes) descending
    resolved_assets.sort(key=lambda a: (a["pixels"], a["bytes"]), reverse=True)
    unique_assets = []

    for asset in resolved_assets:
        # Check if it duplicates an already accepted higher-resolution asset
        is_dup = False
        for accepted in unique_assets:
            # Check aspect ratio compatibility and dhash hamming distance
            if asset["dhash"] is not None and accepted["dhash"] is not None:
                dist = hamming_distance(asset["dhash"], accepted["dhash"])
                # Check aspect ratio
                ar1 = asset["width"] / max(1, asset["height"])
                ar2 = accepted["width"] / max(1, accepted["height"])
                if dist <= 2 and abs(ar1 - ar2) < 0.05:
                    is_dup = True
                    dedup_skipped.append({
                        "url": asset["url"],
                        "skippedInFavorOf": accepted["url"],
                        "reason": f"Lower resolution variant ({asset['width']}x{asset['height']} vs {accepted['width']}x{accepted['height']})",
                        "firstSeenAtScrollPx": asset["firstSeenAtScrollPx"],
                    })
                    break
        if not is_dup:
            unique_assets.append(asset)

    # Save the winners to disk
    written_files = set()
    for asset in unique_assets:
        buf = asset["buffer"]
        u = asset["url"]
        w = asset["width"]
        h = asset["height"]

        # Check --exclude rules (dimensions e.g. 200x200 or labels small|medium|large|larger)
        is_excluded, exclude_reason = matches_exclude(w, h, exclude_rules)
        if is_excluded:
            excluded_by_condition.append({
                "url": u,
                "width": w,
                "height": h,
                "sizeLabel": get_image_size_label(w, h),
                "reason": exclude_reason,
                "firstSeenAtScrollPx": asset["firstSeenAtScrollPx"],
            })
            continue

        fname = filename_from_url(u, buf)

        # Ensure no accidental overwriting if two completely different images had the same name
        dest_path = os.path.join(args.output_dir, fname)
        if dest_path in written_files or os.path.exists(dest_path):
            root, ext = os.path.splitext(fname)
            n = 1
            while dest_path in written_files or os.path.exists(dest_path):
                dest_path = os.path.join(args.output_dir, f"{root}_{n}{ext}")
                n += 1

        if len(buf) < args.min_bytes:
            skipped_small.append({
                "url": u,
                "reason": f"Below --min-bytes ({len(buf)} < {args.min_bytes})",
                "firstSeenAtScrollPx": asset["firstSeenAtScrollPx"],
            })
            continue

        with open(dest_path, 'wb') as f:
            f.write(buf)
        written_files.add(dest_path)

        downloaded.append({
            "url": u,
            "savedAs": os.path.basename(dest_path),
            "bytes": len(buf),
            "width": asset["width"],
            "height": asset["height"],
            "firstSeenAtScrollPx": asset["firstSeenAtScrollPx"],
        })

    report = {
        "url": args.url,
        "startedAt": datetime.datetime.fromtimestamp(start_time, tz=datetime.timezone.utc).isoformat(),
        "finishedAt": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        "durationMs": int((time.time() - start_time) * 1000),
        "timedOut": time.time() > deadline,
        "navigationError": nav_error,
        "options": {
            "scroll": args.scroll,
            "scrollMode": scroll_mode,
            "scrollStep": args.scroll_step,
            "between": args.between,
            "betweenBounds": between_bounds,
            "exclude": args.exclude,
            "excludeRules": exclude_rules,
            "timeout": args.timeout,
            "minBytes": args.min_bytes,
        },
        "textMatch": text_match_result,
        "scrollLog": scroll_log,
        "feedDetection": {
            "looksLikeInfiniteFeed": looks_like_infinite_feed,
            "reasoning": feed_detection_reasoning,
        },
        "summary": {
            "totalImagesDiscovered": len(all_images),
            "totalEligibleForDownload": len(to_download),
            "excludedByBetween": len(excluded_by_between),
            "excludedByCondition": len(excluded_by_condition),
            "downloaded": len(downloaded),
            "deduplicated": len(dedup_skipped),
            "authBlocked": len(auth_blocked),
            "failed": len(failed),
            "skippedSmall": len(skipped_small),
        },
        "downloaded": downloaded,
        "deduplicated": dedup_skipped,
        "authBlocked": auth_blocked,
        "failed": failed,
        "skippedSmall": skipped_small,
        "excludedByCondition": excluded_by_condition,
        "excludedByBetween": excluded_by_between,
    }

    indent = None if args.no_pretty else 2
    with open(args.report, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=indent)

    print(f"\nWrote report to: {args.report}")
    print(f"Summary: {len(downloaded)} unique images downloaded (highest resolution preserved), "
          f"{len(dedup_skipped)} duplicates removed, {len(excluded_by_condition)} excluded by condition, "
          f"{len(auth_blocked)} auth-blocked, {len(failed)} failed, {len(skipped_small)} skipped, "
          f"{len(excluded_by_between)} excluded by --between.")
    return report


def run(args):
    """Entry point used by the `capture` dispatcher."""
    if list_devices(args, "images"):
        return
    exclude_rules = prepare(args)
    load_deps()
    payload = {"command": "images", "url": args.url, "output_dir": args.output_dir, "report": args.report}
    with begin(args) as real:
        report = asyncio.run(run_async(args, exclude_rules))
    if report:
        payload.update(report.get("summary", {}))
        payload["report"] = args.report
        payload["downloaded"] = [d.get("savedAs") for d in report.get("downloaded", [])]
    emit(args, payload, real)


if __name__ == '__main__':
    from _common import utf8_console

    utf8_console()
    _ap = argparse.ArgumentParser(
        prog="capture images",
        description="Visit a URL, scroll to trigger lazy loading, download every image at its "
                    "highest resolution, deduplicate, and write a JSON report.",
    )
    add_args(_ap)
    run(_ap.parse_args())
