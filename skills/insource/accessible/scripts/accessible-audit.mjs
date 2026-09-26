#!/usr/bin/env node
/**
 * accessible-audit.mjs — render a UI and measure it.
 *
 * Part of the `accessible` skill. Drives a headless Chrome over CDP (Node >= 22,
 * no npm dependencies) and reports the things a redesign pass is supposed to have
 * achieved, so "it looks calmer" becomes a number you can compare against a
 * reference file instead of a claim.
 *
 *   node accessible-audit.mjs <url-or-file> [--out report.json] [--shot shot.png]
 *                           [--chrome /path/to/chrome] [--width 1440] [--height 1000]
 *                           [--baseline reference.json] [--json]
 *
 * What it measures, and why each one matters to this skill specifically:
 *   contrast-floor   text below WCAG AA            -> illegible  (the classic check)
 *   contrast-ceiling text above ~15:1, and high-chroma colour on a near-black
 *                    ground                        -> halation, eye strain. AA never
 *                    catches this; it is a minimum, not a range.
 *   whitespace       ink-to-ground ratio per region, and sibling gaps
 *                                                  -> "open up spacing" as a number
 *   focus            what visually dominates, by area x contrast x chroma
 *                                                  -> flat hierarchy = nothing wins
 *   accent-load      how many regions carry saturated colour
 *                                                  -> brand hue should be concentrated
 *   type-scale       min / median / max font size  -> cramped vs comfortable vs enormous
 *   hit-targets      interactive controls too small to click
 *   clipping         overflowing text and boxes    -> only visible once actually rendered
 *   length           screens tall, longest unbroken run with no heading, where the
 *                    height comes from -> long is a real cost, but only when the
 *                    length is stacked content rather than a paginated data table
 *
 * Exit code: 0 clean, 1 findings above threshold, 2 usage/runtime error.
 */

import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

/* ------------------------------------------------------------------ args */

const argv = process.argv.slice(2);
const target = argv.find((a) => !a.startsWith('--'));
const flag = (name, fallback) => {
  const i = argv.indexOf(`--${name}`);
  return i === -1 ? fallback : argv[i + 1];
};
const has = (name) => argv.includes(`--${name}`);

if (!target) {
  console.error('usage: node accessible-audit.mjs <url-or-file> [--out r.json] [--shot s.png] [--chrome path] [--width 1440] [--height 1000] [--baseline ref.json] [--json]');
  process.exit(2);
}

const url = /^https?:\/\//.test(target) ? target : 'file://' + path.resolve(target);
const width = Number(flag('width', 1440));
const height = Number(flag('height', 1000));
const shotPath = flag('shot', null);
const outPath = flag('out', null);
const baselinePath = flag('baseline', null);
const exclude = (flag('exclude', '') || '').split(',').map((s) => s.trim()).filter(Boolean);

/* -------------------------------------------------------- find a browser */

async function findChrome() {
  const explicit = flag('chrome', process.env.CHROME_PATH);
  const candidates = [];
  if (explicit) candidates.push(explicit);
  // Playwright's cache is the most common place one already exists on this machine.
  for (const root of [process.env.HOME, '/root', '/home/codespace'].filter(Boolean)) {
    for (const v of ['chromium', 'chromium_headless_shell']) {
      const dir = path.join(root, '.cache/ms-playwright');
      if (!existsSync(dir)) continue;
      try {
        for (const build of (await import('node:fs')).readdirSync(dir).filter((d) => d.startsWith(v + '-'))) {
          candidates.push(
            path.join(dir, build, 'chrome-linux64/chrome'),
            path.join(dir, build, 'chrome-linux/chrome'),
            path.join(dir, build, 'chrome-headless-shell-linux64/chrome-headless-shell'),
          );
        }
      } catch { /* ignore */ }
    }
  }
  for (const p of ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
                   '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']) candidates.push(p);
  for (const c of candidates) if (c && existsSync(c)) return c;
  throw new Error('no Chrome binary found. Pass --chrome /path/to/chrome (any headless Chrome or Chromium works).');
}

/* ------------------------------------------------------------- CDP client */

function makeClient(ws) {
  let id = 0;
  const waiting = new Map();
  ws.addEventListener('message', (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && waiting.has(msg.id)) {
      const { resolve, reject } = waiting.get(msg.id);
      waiting.delete(msg.id);
      msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
    }
  });
  return {
    send(method, params = {}) {
      const mid = ++id;
      ws.send(JSON.stringify({ id: mid, method, params }));
      return new Promise((resolve, reject) => waiting.set(mid, { resolve, reject }));
    },
  };
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function waitForJson(endpoint, tries = 60) {
  for (let i = 0; i < tries; i++) {
    try { const r = await fetch(endpoint); if (r.ok) return await r.json(); } catch { /* not up yet */ }
    await sleep(250);
  }
  throw new Error('Chrome DevTools endpoint never came up');
}

/* ------------------------------------------------ page-side measurement */

const PAGE_SCRIPT = () => {
  const clamp2 = (n, lo = 0, hi = 100) => Math.max(lo, Math.min(hi, n));
  /* ---- colour maths (sRGB) ---- */
  const parse = (str) => {
    if (!str) return null;
    let m = str.match(/rgba?\(([^)]+)\)/);
    if (m) {
      const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
      return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
    }
    m = str.match(/^#([0-9a-f]{3,8})$/i);
    if (m) {
      let h = m[1];
      if (h.length === 3 || h.length === 4) h = h.split('').map((c) => c + c).join('');
      return { r: parseInt(h.slice(0, 2), 16), g: parseInt(h.slice(2, 4), 16), b: parseInt(h.slice(4, 6), 16), a: h.length >= 8 ? parseInt(h.slice(6, 8), 16) / 255 : 1 };
    }
    return null;
  };
  const chan = (v) => { const c = v / 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
  const lum = (c) => 0.2126 * chan(c.r) + 0.7152 * chan(c.g) + 0.0722 * chan(c.b);
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const over = (fg, bg) => ({
    r: fg.r * fg.a + bg.r * (1 - fg.a),
    g: fg.g * fg.a + bg.g * (1 - fg.a),
    b: fg.b * fg.a + bg.b * (1 - fg.a),
    a: 1,
  });
  // HSL chroma: how much actual colour, versus grey.
  const chroma = (c) => { const mx = Math.max(c.r, c.g, c.b) / 255, mn = Math.min(c.r, c.g, c.b) / 255; return mx - mn; };

  const bgOf = (el) => {
    let n = el;
    while (n && n.nodeType === 1) {
      const cs = getComputedStyle(n);
      const c = resolve(cs.backgroundColor);
      if (c && c.a > 0.02) {
        if (c.a < 1 && n.parentElement) return over(c, bgOf(n.parentElement));
        return c;
      }
      const grad = cs.backgroundImage;
      if (grad && grad !== 'none') { const first = grad.match(/rgba?\([^)]+\)|#[0-9a-f]{3,8}/i); const gc = first && resolve(first[0]); if (gc) return gc.a < 1 ? over(gc, bgOf(n.parentElement)) : gc; }
      n = n.parentElement;
    }
    return { r: 255, g: 255, b: 255, a: 1 };
  };

  const visible = (r) => r.width > 1 && r.height > 1;

  // Chrome does NOT normalise modern colours (oklch / oklab / lab / lch / color-mix /
  // color()) anywhere you can read them back — not in computed styles, and not even in
  // canvas `fillStyle`, which echoes the authored string. String-parsing them yields
  // nothing, and every check below then reports a clean pass on a page that is not
  // clean. The only reliable resolution is to paint the colour and read the sRGB pixel
  // back out of the framebuffer, which forces the browser to actually resolve it.
  const px = document.createElement('canvas');
  px.width = 1; px.height = 1;
  const cx = px.getContext('2d', { willReadFrequently: true });
  const REJECT_SENTINEL = 'rgba(0, 0, 0, 0)';
  const resolve = (str) => {
    if (!str || typeof str !== 'string') return null;
    cx.globalCompositeOperation = 'copy';
    cx.fillStyle = REJECT_SENTINEL;
    cx.fillStyle = str;
    if (cx.fillStyle === REJECT_SENTINEL) return null; // unparseable: setter rejected
    cx.clearRect(0, 0, 1, 1);
    cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    return { r: d[0], g: d[1], b: d[2], a: d[3] / 255 };
  };
  const vw = innerWidth, vh = innerHeight;

  // Regions the caller declared low-dwell-time chrome (a brand rail, a top bar) are
  // allowed bolder and higher-contrast treatment than the working surface, so their
  // ceiling hits are expected rather than failures. Pass --exclude to name them.
  const EXCL = (window.__EXCLUDE || []).filter(Boolean);
  const excluded = (el) => EXCL.some((s) => { try { return el.closest(s); } catch { return false; } });

  /* ---- 1. contrast, floor and ceiling ---- */
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const text = [];
  let node;
  while ((node = walker.nextNode())) {
    if (!node.nodeValue || !node.nodeValue.trim()) continue;
    const el = node.parentElement;
    if (!el) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || Number(cs.opacity) < 0.05) continue;
    const range = document.createRange();
    range.selectNodeContents(node);
    const rects = [...range.getClientRects()].filter(visible);
    if (!rects.length) continue;
    const area = rects.reduce((s, r) => s + r.width * r.height, 0);
    const fg = resolve(cs.color);
    if (!fg) continue;
    const bg = bgOf(el);
    const size = parseFloat(cs.fontSize);
    const bold = Number(cs.fontWeight) >= 700;
    // WCAG large-text threshold: 18.66px bold or 24px normal
    const large = size >= 24 || (size >= 18.66 && bold);
    text.push({
      sample: node.nodeValue.trim().slice(0, 48),
      size: Math.round(size * 10) / 10,
      weight: cs.fontWeight,
      large,
      area: Math.round(area),
      ratio: Math.round(ratio(over(fg, bg), bg) * 100) / 100,
      chrome: excluded(el),
      fgChroma: Math.round(chroma(over(fg, bg)) * 100) / 100,
      bgLum: Math.round(lum(bg) * 1000) / 1000,
      selector: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : ''),
    });
  }
  // --exclude marks low-dwell chrome. Chrome is exempt from the *ceiling* only: bold,
  // high-contrast, saturated treatment is acceptable on a region you glance at. It is
  // never exempt from the AA *floor* — text must be readable everywhere.
  const floor = text.filter((t) => t.ratio < (t.large ? 3 : 4.5));
  const chromeFloor = text.filter((t) => t.chrome && t.ratio < (t.large ? 3 : 4.5));
  // Ceiling: harsh only where it is *read*. A huge display numeral at 20:1 is fine;
  // a paragraph at 20:1 on near-black is the thing that hurts.
  const darkGround = (t) => t.bgLum < 0.09;
  const ceiling = text.filter((t) => !t.chrome && t.area > 400 && (
    (darkGround(t) && (t.ratio > 14 || (t.fgChroma > 0.35 && t.ratio > 8 && t.size < 20))) ||
    (!darkGround(t) && t.ratio > 19)
  ));
  const halation = text.filter((t) => !t.chrome && darkGround(t) && t.fgChroma > 0.4 && t.size < 22 && t.area > 300);

  /* ---- 2. whitespace: ink coverage on a coarse grid ---- */
  const CELL = 8;
  const cols = Math.max(1, Math.ceil(vw / CELL)), rows = Math.max(1, Math.ceil(vh / CELL));
  const grid = new Uint8Array(cols * rows);
  const LEAF = 'a,button,input,select,textarea,img,svg,canvas,video,th,td,li,label,h1,h2,h3,h4,h5,h6,p,span,code,kbd';
  const markRect = (r) => {
    const x0 = Math.max(0, Math.floor(r.left / CELL)), x1 = Math.min(cols - 1, Math.floor(r.right / CELL));
    const y0 = Math.max(0, Math.floor(r.top / CELL)), y1 = Math.min(rows - 1, Math.floor(r.bottom / CELL));
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) grid[y * cols + x] = 1;
  };
  // Text ranges are the honest measure of ink; boxes over-count whitespace badly.
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let tn;
  while ((tn = tw.nextNode())) {
    if (!tn.nodeValue || !tn.nodeValue.trim()) continue;
    const rg = document.createRange(); rg.selectNodeContents(tn);
    for (const r of rg.getClientRects()) if (visible(r) && r.top < vh && r.bottom > 0) markRect(r);
  }
  for (const el of document.querySelectorAll('img,svg,canvas,video,button,input,select,textarea,th,td')) {
    const r = el.getBoundingClientRect();
    if (visible(r) && r.top < vh && r.bottom > 0) markRect(r);
  }
  const occupied = grid.reduce((s, v) => s + v, 0);
  const inkRatio = occupied / (cols * rows);

  // Vertical breathing room: gaps between successive top-level blocks in each column.
  const gaps = [];
  const containers = [...document.querySelectorAll('body, main, [class*="wrap"], [class*="main"], [class*="content"], section, article, table, form')]
    .filter((e) => { const r = e.getBoundingClientRect(); return r.width > vw * 0.3 && r.height > 100; });
  for (const c of containers.slice(0, 6)) {
    const kids = [...c.children].map((k) => k.getBoundingClientRect()).filter(visible).sort((a, b) => a.top - b.top);
    for (let i = 1; i < kids.length; i++) { const g = kids[i].top - kids[i - 1].bottom; if (g >= 0 && g < 400) gaps.push(Math.round(g)); }
  }
  gaps.sort((a, b) => a - b);
  const medianGap = gaps.length ? gaps[Math.floor(gaps.length / 2)] : null;

  // Per-region density, so a calm header can't hide a jammed table.
  const regions = [...document.querySelectorAll('table, thead, tbody, [class*="card"], [class*="panel"], aside, nav, header, footer, section')]
    .map((e) => {
      const r = e.getBoundingClientRect();
      if (!visible(r) || r.top > vh || r.bottom < 0 || r.width < 80) return null;
      const x0 = Math.max(0, Math.floor(r.left / CELL)), x1 = Math.min(cols - 1, Math.floor(r.right / CELL));
      const y0 = Math.max(0, Math.floor(r.top / CELL)), y1 = Math.min(rows - 1, Math.floor(r.bottom / CELL));
      let hit = 0, tot = 0;
      for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) { tot++; if (grid[y * cols + x]) hit++; }
      const cs = getComputedStyle(e);
      return {
        tag: e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/)[0] : ''),
        area: Math.round(r.width * r.height),
        ink: Math.round((hit / Math.max(1, tot)) * 1000) / 10,
        pad: Math.round(parseFloat(cs.paddingLeft) + parseFloat(cs.paddingTop)),
      };
    }).filter(Boolean).sort((a, b) => b.ink - a.ink);

  /* ---- 3. focus: what actually wins the eye ---- */
  const focus = [...document.querySelectorAll('h1,h2,h3,p,span,td,th,button,a,svg,img,[class*="stat"],[class*="card"],[class*="tile"],[class*="fig"]')]
    .map((e) => {
      const r = e.getBoundingClientRect();
      if (!visible(r) || r.top > vh || r.bottom < 0) return null;
      const cs = getComputedStyle(e);
      const fg = resolve(cs.color); if (!fg) return null;
      const bg = bgOf(e);
      const size = parseFloat(cs.fontSize);
      const weight = Number(cs.fontWeight) || 400;
      const c = ratio(over(fg, bg), bg);
      const sat = Math.max(chroma(over(fg, bg)), chroma(bg));
      const score = Math.sqrt(r.width * r.height) * (size / 16) * (1 + weight / 1000) * Math.min(3, c / 4.5) * (1 + sat * 1.5);
      return { tag: e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/)[0] : ''), size: Math.round(size), score: Math.round(score), text: (e.textContent || '').trim().slice(0, 40) };
    }).filter(Boolean).sort((a, b) => b.score - a.score).slice(0, 8);
  const topScore = focus.length ? focus[0].score : 1;
  // Flat hierarchy: the top competitor is barely ahead of the 5th.
  const fifth = focus.length >= 5 ? focus[4].score : topScore;
  const hierarchySpread = Math.round((topScore / Math.max(1, fifth)) * 100) / 100;

  /* ---- 4. accent load: how many regions are saturated ---- */
  const accents = [...document.querySelectorAll('*')].filter((e) => {
    const r = e.getBoundingClientRect();
    if (!visible(r) || r.width * r.height < 900 || r.top > vh) return false;
    if (excluded(e)) return false;
    const bg = resolve(getComputedStyle(e).backgroundColor);
    if (!bg || bg.a < 0.5) return false;
    return chroma(bg) > 0.32;
  });
  const accentAreas = accents.map((e) => { const r = e.getBoundingClientRect(); return Math.round(r.width * r.height); }).sort((a, b) => b - a);
  const accentTotal = accents.reduce((s, e) => { const r = e.getBoundingClientRect(); return s + r.width * r.height; }, 0);
  const accentCoverage = Math.round((accentTotal / (vw * vh)) * 1000) / 10;

  /* ---- 5. type scale ---- */
  const sizes = [...document.querySelectorAll('body *')].filter((e) => (e.textContent || '').trim()).map((e) => parseFloat(getComputedStyle(e).fontSize)).filter((n) => n > 0);
  sizes.sort((a, b) => a - b);
  const uniq = [...new Set(sizes.map((s) => Math.round(s * 10) / 10))];

  /* ---- 6. hit targets ---- */
  const ttag = (e) => e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/)[0] : '');
  const targets = [...document.querySelectorAll('button,a[href],input,select,summary,[role="button"],[role="checkbox"]')]
    .filter((e) => !excluded(e))
    .map((e) => { const r = e.getBoundingClientRect(); return { tag: ttag(e), w: Math.round(r.width), h: Math.round(r.height), min: Math.round(Math.min(r.width, r.height)), link: e.tagName === 'A' && e.hasAttribute('href'), inline: getComputedStyle(e).display === 'inline', text: (e.textContent || e.getAttribute('aria-label') || '').trim().slice(0, 30) }; })
    .filter((x) => x.w > 0 && x.h > 0 && !x.inline);
  // Links are judged separately from controls and reported only as advisory. WCAG's
  // target-size criteria exempt links "in a sentence" and links whose purpose is met by an
  // equivalent control elsewhere — breadcrumb, nav and prose links nearly always qualify,
  // and their rect height is the text line box, not a designed tap area. Counting them as
  // AA breaches buries the real findings (a 15px checkbox genuinely is one).
  const controlTargets = targets.filter((t) => !t.link);
  const linkTargets = targets.filter((t) => t.link && t.min < 24);
  const tinyTargets = controlTargets.filter((t) => t.min < 24);               // WCAG 2.5.8 AA breach
  const snugTargets = controlTargets.filter((t) => t.min >= 24 && t.min < 44); // below 2.5.5 AAA

  /* ---- 7. clipping / overflow, only visible once rendered ---- */
  const clipped = [...document.querySelectorAll('body *')].filter((e) => {
    if (!e.children.length && e.scrollWidth > e.clientWidth + 2 && /hidden|auto|scroll/.test(getComputedStyle(e).overflowX)) return true;
    return false;
  }).map((e) => ({ tag: e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/)[0] : ''), overflow: e.scrollWidth - e.clientWidth, text: (e.textContent || '').trim().slice(0, 30) })).slice(0, 20);
  const hOverflow = document.documentElement.scrollWidth > vw + 2;

  /* ---- 8. page length: long is not automatically bad, long-without-structure is ---- */
  const docH = document.documentElement.scrollHeight;
  const screens = Math.round((docH / vh) * 100) / 100;

  // Structural signposts, in document order: anything telling the reader a new part
  // has started. A long run between two of them is the actual failure.
  const marks = [...document.querySelectorAll('h1,h2,h3,h4,legend,summary,thead,nav')]
    .map((e) => { const r = e.getBoundingClientRect(); return { top: Math.round(r.top + scrollY), tag: e.tagName.toLowerCase() }; })
    .filter((m) => m.top >= 0).sort((a, b) => a.top - b.top);
  let wall = 0, wallAt = 0, prev = 0;
  for (const m of marks) { if (m.top - prev > wall) { wall = m.top - prev; wallAt = prev; } prev = m.top; }
  if (docH - prev > wall) { wall = docH - prev; wallAt = prev; }
  const longestWallPx = Math.round(wall);
  const longestWallScreens = Math.round((wall / vh) * 100) / 100;

  // Where the height actually comes from, so the fix is actionable.
  const tallest = [...document.querySelectorAll('section, article, table, [class*="card"], [class*="panel"], main > div')]
    .map((e) => { const r = e.getBoundingClientRect(); return { tag: e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/)[0] : ''), h: Math.round(r.height), isTable: e.tagName === 'TABLE' || !!e.querySelector(':scope > table') }; })
    .filter((x) => x.h > 200).sort((a, b) => b.h - a.h).slice(0, 6);

  // Long because a data table has many rows is fine — that is what pagination is for.
  // Long because N dashboard blocks are stacked is the redistribution move not having
  // happened. Attribute the height before judging it.
  const tablePx = [...document.querySelectorAll('table')].reduce((t, e) => t + e.getBoundingClientRect().height, 0);
  const lengthIsData = tablePx > docH * 0.5;

  // Repeated sibling blocks: "undifferentiated repetition", measured in pixels.
  // body itself must be included: repeated blocks that are direct children of body are
  // the most common shape of a page that is long purely because of stacking.
  const repeats = [document.body, ...document.querySelectorAll('body *')].map((e) => {
    const kids = [...e.children]; if (kids.length < 5) return null;
    const tally = {};
    for (const k of kids) { const key = k.tagName.toLowerCase() + (typeof k.className === 'string' && k.className.trim() ? '.' + k.className.trim().split(/\s+/)[0] : ''); tally[key] = (tally[key] || 0) + 1; }
    const top = Object.entries(tally).sort((a, b) => b[1] - a[1])[0];
    if (!top || top[1] < 5) return null;
    const sample = kids.find((k) => (k.tagName.toLowerCase() + (typeof k.className === 'string' && k.className.trim() ? '.' + k.className.trim().split(/\s+/)[0] : '')) === top[0]);
    return { parent: e.tagName.toLowerCase(), child: top[0], count: top[1], estHeight: Math.round((sample ? sample.getBoundingClientRect().height : 0) * top[1]) };
  }).filter(Boolean).sort((a, b) => b.estHeight - a.estHeight).slice(0, 5);

  const stickyNav = [...document.querySelectorAll('nav, header, [class*="rail"], [class*="chrome"], [class*="topbar"], [class*="sidebar"]')]
    .some((e) => { const cs = getComputedStyle(e); const r = e.getBoundingClientRect(); return (cs.position === 'sticky' || cs.position === 'fixed') && r.height > 24 && r.height < vh * 0.85; });

  const interactive = [...document.querySelectorAll('button,a[href],input,select,summary')].map((e) => Math.round(e.getBoundingClientRect().top + scrollY)).filter((y) => y >= 0);
  const screensToLastAction = interactive.length ? Math.round((Math.max(...interactive) / vh) * 100) / 100 : 0;

  const lengthFlags = [];
  if (!lengthIsData && screens > 4) lengthFlags.push(`page runs ${screens} screens and no data table accounts for the bulk of it`);
  if (longestWallScreens > 1.2) lengthFlags.push(`${longestWallScreens} screens (${longestWallPx}px) with no heading or section break — an unbroken wall`);
  if (!lengthIsData && repeats.length && repeats[0].count > 8 && repeats[0].estHeight > vh) lengthFlags.push(`${repeats[0].count} stacked "${repeats[0].child}" blocks ~${repeats[0].estHeight}px tall — redistribute or paginate`);
  if (!stickyNav && screens > 3) lengthFlags.push(`${screens} screens tall with no persistent navigation or sticky orientation`);

  /* ---- 9. palette coherence: shades are good, dispersion is what hurts ---- */
  // IMPORTANT distinction this measures. Many SHADES — a rich tonal ramp of lightness
  // steps held to one hue temperature — is a virtue and is rewarded below. What damages
  // readability is many unrelated SATURATED HUES all claiming attention at once, because
  // then colour stops carrying meaning and starts competing with itself. Count of colours
  // is never the problem; count of competing hue families is.
  const toHsl = (c) => {
    const r = c.r / 255, g = c.g / 255, b = c.b / 255;
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
    let h = 0;
    if (d) {
      if (mx === r) h = ((g - b) / d) % 6; else if (mx === g) h = (b - r) / d + 2; else h = (r - g) / d + 4;
      h = (h * 60 + 360) % 360;
    }
    const l = (mx + mn) / 2;
    return { h, l, chroma: d };
  };
  const BINS = 24, binW = 360 / BINS;
  const hueArea = new Array(BINS).fill(0);
  let colouredArea = 0;
  const satBins = new Set();
  const addHue = (col, area, saturated) => {
    if (!col || col.a < 0.35) return;
    const { h, chroma } = toHsl(col);
    if (chroma < 0.06) return;                       // neutrals carry no hue signal
    const bin = Math.floor(h / binW) % BINS;
    hueArea[bin] += area; colouredArea += area;
    // Only a LARGE, genuinely saturated block counts as an attention claim. A 12px icon
    // in a fifth colour is not a rainbow; six gradient cards are.
    if (saturated && area > 3000) satBins.add(bin);
  };
  for (const e of document.querySelectorAll('*')) {
    const r = e.getBoundingClientRect();
    if (!visible(r) || r.top > vh || r.width * r.height < 400) continue;
    const cs = getComputedStyle(e);
    const bg = resolve(cs.backgroundColor);
    if (bg && bg.a > 0.4) addHue(bg, r.width * r.height, toHsl(bg).chroma > 0.25);
    const bd = resolve(cs.borderTopColor);
    if (bd) addHue(bd, Math.min(r.width, r.height) * r.width * 0.02, false);
  }
  for (const t of text) {
    const el = [...document.querySelectorAll('*')].find((e) => e.textContent && e.textContent.trim().startsWith(t.sample.slice(0, 12)));
    if (!el) continue;
    const c = resolve(getComputedStyle(el).color);
    if (c) addHue(c, t.area, false);
  }
  const shares = hueArea.map((a) => (colouredArea ? a / colouredArea : 0));
  const hueBinsUsed = shares.filter((v) => v > 0.01).length;
  const dominantHueShare = Math.round(Math.max(0, ...shares) * 1000) / 10;
  const hueEntropy = Math.round((() => {
    const p = shares.filter((v) => v > 0); if (!p.length) return 0;
    const tot = p.reduce((a, b) => a + b, 0) || 1;
    return -p.reduce((a, b) => a + (b / tot) * Math.log2(b / tot), 0) / Math.log2(BINS);
  })() * 1000) / 1000;
  const competingHues = satBins.size;

  // The ramp: neutral-ish large surfaces, measured for how many lightness steps they form
  // and whether they share one temperature.
  const surf = [...document.querySelectorAll('body, body *')].map((e) => {
    const r = e.getBoundingClientRect(); if (!visible(r) || r.width * r.height < 20000 || r.top > vh) return null;
    const c = resolve(getComputedStyle(e).backgroundColor); if (!c || c.a < 0.5) return null;
    const { h, l, chroma } = toHsl(c);
    // Only near-neutral large surfaces define the ramp's temperature. Status callouts are
    // deliberately red/blue/green and are judged by competingHues instead — counting them
    // here would call every well-designed semantic status colour an incoherent palette.
    if (chroma > 0.05) return null;
    return { h, l, chroma, area: r.width * r.height };
  }).filter(Boolean).sort((a, b) => b.area - a.area).slice(0, 8);
  const rampSteps = [...new Set(surf.map((x) => Math.round(x.l * 100)))].length;
  // A hue read off a near-grey is arbitrary — rgb(250,248,245) and rgb(247,248,250) are both
  // "white" but sit 160 degrees apart on the wheel. Only surfaces tinted enough for hue to
  // mean something may vote on the ramp's temperature.
  const tinted = surf.filter((x) => x.chroma > 0.012);   // below this, hue is rounding noise
  // Hue is an angle: 350 and 10 are 20 apart, not 340. Compare circularly.
  let rampHueSpread = 0;
  for (let i = 0; i < tinted.length; i++) for (let j = i + 1; j < tinted.length; j++) {
    const d = Math.abs(tinted[i].h - tinted[j].h);
    rampHueSpread = Math.max(rampHueSpread, Math.min(d, 360 - d));
  }
  rampHueSpread = tinted.length >= 3 ? Math.round(rampHueSpread * 10) / 10 : 0;

  const paletteFlags = [];
  if (competingHues >= 5) paletteFlags.push(`${competingHues} large saturated hue families competing — colour is decoration, not meaning`);
  if (hueEntropy > 0.55 && colouredArea > 20000) paletteFlags.push(`hue entropy ${hueEntropy} — no dominant family (rainbow)`);
  if (rampHueSpread > 45) paletteFlags.push(`${tinted.length} base surfaces scattered across ${rampHueSpread}° of hue — mixed colour temperatures, not one ramp`);
  const paletteScore = clamp2(100
    - Math.max(0, competingHues - 3) * 13          // too many attention hues
    - Math.max(0, hueEntropy - 0.40) * 85          // hue spread thin
    - Math.max(0, rampHueSpread - 45) * 0.9        // inconsistent temperature
    + (rampSteps >= 3 && rampSteps <= 9 && rampHueSpread <= 40 ? Math.min(12, (rampSteps - 2) * 3) : 0) // reward a real ramp
    - (rampSteps <= 1 && colouredArea > 0 ? 6 : 0));   // no ramp at all: everything one plane

  return {
    viewport: { width: vw, height: vh, scrollHeight: document.documentElement.scrollHeight },
    title: document.title,
    counts: { textNodes: text.length, elements: document.querySelectorAll('*').length },
    contrast: {
      floor: floor.slice(0, 25), floorCount: floor.length,
      inChrome: chromeFloor.slice(0, 10), inChromeCount: chromeFloor.length,
      ceiling: ceiling.slice(0, 25), ceilingCount: ceiling.length,
      halation: halation.slice(0, 15), halationCount: halation.length,
      medianRatio: (() => { const r = text.map((t) => t.ratio).sort((a, b) => a - b); return r.length ? Math.round(r[Math.floor(r.length / 2)] * 100) / 100 : null; })(),
    },
    whitespace: {
      inkRatio: Math.round(inkRatio * 1000) / 10,
      medianGapPx: medianGap,
      sampleGaps: gaps.slice(0, 12),
      densestRegions: regions.slice(0, 8),
      roomiestRegions: regions.slice(-4),
    },
    focus: { ranked: focus, hierarchySpread },
    accents: { count: accents.length, coveragePct: accentCoverage, largestAreas: accentAreas.slice(0, 6) },
    type: { min: sizes[0] ?? null, median: sizes[Math.floor(sizes.length / 2)] ?? null, max: sizes[sizes.length - 1] ?? null, distinctSteps: uniq.length },
    hitTargets: {
      aaViolations: tinyTargets.slice(0, 20), aaCount: tinyTargets.length,
      belowComfort: snugTargets.slice(0, 20), comfortCount: snugTargets.length,
      linkAdvisory: linkTargets.slice(0, 10), linkCount: linkTargets.length,
      measured: targets.length, controls: controlTargets.length,
    },
    clipping: { elements: clipped, count: clipped.length, horizontalPageOverflow: hOverflow },
    palette: { competingHues, hueEntropy, dominantHueShare, hueBinsUsed,
      rampSteps, rampHueSpread, score: Math.round(paletteScore), flags: paletteFlags },
    length: { screens, docHeight: docH, longestWallPx, longestWallScreens, signposts: marks.length,
      headingsPerScreen: marks.length ? Math.round((marks.length / screens) * 100) / 100 : 0,
      lengthIsData, stickyNav, screensToLastAction, tallest, repeats, flags: lengthFlags },
  };
};

/* ------------------------------------------------------------------ main */

function format(r) {
  const L = [];
  const bad = (n) => (n ? `\x1b[31m${n}\x1b[0m` : '0');
  L.push(`\n\x1b[1maccessible audit — ${r.title || '(untitled)'}\x1b[0m`);
  L.push(`  ${r.viewport.width}x${r.viewport.height} viewport · ${r.viewport.scrollHeight}px tall · ${r.counts.textNodes} text runs · ${r.counts.elements} elements\n`);
  L.push(`\x1b[1m  contrast\x1b[0m   median ${r.contrast.medianRatio}:1`);
  L.push(`    below AA floor .............. ${bad(r.contrast.floorCount)}${r.contrast.inChromeCount ? ` \u2190 ${r.contrast.inChromeCount} inside excluded chrome` : ''}${r.contrast.floor.length ? '\n        ' + r.contrast.floor.slice(0, 4).map((t) => `${t.ratio}:1 "${t.sample}" (${t.selector} ${t.size}px)`).join('\n        ') : ''}`);
  L.push(`    above comfort ceiling ....... ${bad(r.contrast.ceilingCount)}${r.contrast.ceiling.length ? '\n        ' + r.contrast.ceiling.slice(0, 4).map((t) => `${t.ratio}:1 "${t.sample}" (${t.size}px on bgL ${t.bgLum})`).join('\n        ') : ''}`);
  L.push(`    saturated-on-dark (halation)  ${bad(r.contrast.halationCount)}`);
  L.push(`\n\x1b[1m  whitespace\x1b[0m ink ${r.whitespace.inkRatio}% of viewport · median block gap ${r.whitespace.medianGapPx ?? 'n/a'}px`);
  L.push(`    densest: ${r.whitespace.densestRegions.slice(0, 3).map((x) => `${x.tag} ${x.ink}%ink/${x.pad}px pad`).join('  |  ')}`);
  L.push(`\n\x1b[1m  hierarchy\x1b[0m  top-vs-5th focus score ${r.focus.hierarchySpread}x ${r.focus.hierarchySpread < 2 ? '\x1b[33m(flat — nothing wins the eye)\x1b[0m' : ''}`);
  r.focus.ranked.slice(0, 3).forEach((f, i) => L.push(`      ${i + 1}. ${f.tag} score ${f.score} "${f.text}"`));
  L.push(`\n\x1b[1m  accent load\x1b[0m ${r.accents.count} saturated regions covering ${r.accents.coveragePct}% of the viewport ${r.accents.coveragePct > 25 ? '\x1b[33m(spread thin — concentrate the brand hue)\x1b[0m' : ''}`);
  L.push(`\n\x1b[1m  type\x1b[0m       ${r.type.min}px → ${r.type.max}px, median ${r.type.median}px across ${r.type.distinctSteps} steps`);
  L.push(`\n\x1b[1m  palette\x1b[0m     ${r.palette.competingHues} competing hue famil${r.palette.competingHues === 1 ? 'y' : 'ies'} · entropy ${r.palette.hueEntropy} · dominant ${r.palette.dominantHueShare}% · ramp of ${r.palette.rampSteps} shades across ${r.palette.rampHueSpread}° · coherence ${r.palette.score}`);
  if (r.palette.flags.length) L.push('    \x1b[31m' + r.palette.flags.join('\n    ') + '\x1b[0m');
  L.push(`\n\x1b[1m  page length\x1b[0m  ${r.length.screens} screens · ${r.length.signposts} signposts (${r.length.headingsPerScreen}/screen) · longest unbroken run ${r.length.longestWallScreens} screens`);
  L.push(`    ${r.length.lengthIsData ? '\x1b[36mlong due to a data table — expected\x1b[0m' : 'long due to stacked content'} · sticky nav ${r.length.stickyNav ? 'yes' : 'no'} · last control at screen ${r.length.screensToLastAction}`);
  if (r.length.tallest.length) L.push(`    height from: ${r.length.tallest.slice(0,3).map((t)=>`${t.tag} ${t.h}px`).join('  |  ')}`);
  if (r.length.flags.length) L.push(`    \x1b[31m${r.length.flags.length} length issue(s):\x1b[0m\n        ` + r.length.flags.join('\n        '));
  L.push(`\n\x1b[1m  hit targets\x1b[0m ${r.hitTargets.controls} controls: ${bad(r.hitTargets.aaCount)} under 24px (AA breach), ${r.hitTargets.comfortCount || 0} under 44px \x1b[33m(advisory)\x1b[0m${r.hitTargets.linkCount ? ` · ${r.hitTargets.linkCount} small text links \x1b[33m(advisory)\x1b[0m` : ''}`);
  if (r.hitTargets.aaViolations.length) L.push('        ' + r.hitTargets.aaViolations.slice(0, 4).map((t) => `${t.tag} ${t.w}x${t.h} "${t.text}"`).join('\n        '));
  L.push(`\x1b[1m  clipping\x1b[0m     ${bad(r.clipping.count)} overflowing${r.clipping.horizontalPageOverflow ? ' + page-level horizontal overflow' : ''}`);
  if (r.clipping.elements.length) L.push('        ' + r.clipping.elements.slice(0, 4).map((c) => `${c.tag} +${c.overflow}px "${c.text}"`).join('\n        '));
  const issues = r.contrast.floorCount + r.contrast.ceilingCount + r.contrast.halationCount + r.hitTargets.aaCount + r.clipping.count + r.length.flags.length + r.palette.flags.length;
  L.push(`\n  ${issues === 0 ? '\x1b[32mno hard failures\x1b[0m' : `\x1b[31m${issues} hard failure(s)\x1b[0m`} — advisories (sub-44px targets, hierarchy spread, accent load, ink ratio) need a human look.\n`);
  return L.join('\n');
}

function compare(r, baseline) {
  const L = ['\n\x1b[1m  vs baseline\x1b[0m'];
  const row = (label, a, b, betterLower = true) => {
    if (a == null || b == null) return;
    const d = Math.round((a - b) * 100) / 100;
    const good = betterLower ? d < 0 : d > 0;
    L.push(`    ${label.padEnd(26)} ${String(b).padStart(7)} → ${String(a).padStart(7)}  ${d === 0 ? '=' : good ? `\x1b[32m${d > 0 ? '+' : ''}${d}\x1b[0m` : `\x1b[31m${d > 0 ? '+' : ''}${d}\x1b[0m`}`);
  };
  row('AA floor violations', r.contrast.floorCount, baseline.contrast?.floorCount);
  row('ceiling violations', r.contrast.ceilingCount, baseline.contrast?.ceilingCount);
  row('halation candidates', r.contrast.halationCount, baseline.contrast?.halationCount);
  row('ink ratio % (lower=airier)', r.whitespace.inkRatio, baseline.whitespace?.inkRatio);
  row('median block gap px', r.whitespace.medianGapPx, baseline.whitespace?.medianGapPx, false);
  row('hierarchy spread (x)', r.focus.hierarchySpread, baseline.focus?.hierarchySpread, false);
  row('accent coverage %', r.accents.coveragePct, baseline.accents?.coveragePct);
  row('median font px', r.type.median, baseline.type?.median, false);
  row('hit targets <24px (AA)', r.hitTargets.aaCount, baseline.hitTargets?.aaCount);
  row('hit targets <44px (adv)', r.hitTargets.comfortCount, baseline.hitTargets?.comfortCount);
  row('clipped elements', r.clipping.count, baseline.clipping?.count);
  row('page length (screens)', r.length.screens, baseline.length?.screens);
  row('longest unbroken run', r.length.longestWallScreens, baseline.length?.longestWallScreens);
  row('signposts per screen', r.length.headingsPerScreen, baseline.length?.headingsPerScreen, false);
  row('length issues', r.length.flags.length, baseline.length?.flags?.length);
  row('competing hues', r.palette.competingHues, baseline.palette?.competingHues);
  row('hue entropy', r.palette.hueEntropy, baseline.palette?.hueEntropy);
  row('palette coherence', r.palette.score, baseline.palette?.score, false);
  row('ramp shades', r.palette.rampSteps, baseline.palette?.rampSteps, false);
  row('palette flags', r.palette.flags.length, baseline.palette?.flags?.length);
  return L.join('\n');
}

let chrome;
try { chrome = await findChrome(); } catch (e) { console.error('error:', e.message); process.exit(2); }

const profile = mkdtempSync(path.join(tmpdir(), 'acc-chrome-'));
const port = 9700 + Math.floor(Math.random() * 300);
const proc = spawn(chrome, [
  '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
  '--hide-scrollbars', '--force-device-scale-factor=1',
  `--window-size=${width},${height}`, `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check', 'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });

let stderr = '';
proc.stderr.on('data', (d) => { stderr += d.toString(); });
proc.on('exit', (code) => { if (code !== 0 && code !== null) { rmSync(profile, { recursive: true, force: true }); console.error(`chrome exited ${code}\n${stderr.slice(0, 800)}`); process.exit(2); } });

try {
  const version = await waitForJson(`http://127.0.0.1:${port}/json/version`, 80);
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  let page = list.find((t) => t.type === 'page');
  if (!page) {
    try { page = await (await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(url)}`, { method: 'PUT' })).json(); }
    catch { page = await (await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(url)}`)).json(); }
  }
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });
  const cdp = makeClient(ws);

  await cdp.send('Page.enable');
  await cdp.send('Runtime.enable');
  await cdp.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
  await cdp.send('Page.navigate', { url });
  await sleep(2500);

  const evalRes = await cdp.send('Runtime.evaluate', {
    expression: `window.__EXCLUDE = ${JSON.stringify(exclude)};\n(${PAGE_SCRIPT.toString()})()`,
    returnByValue: true, awaitPromise: false,
  });
  if (evalRes.exceptionDetails) throw new Error('page script threw: ' + JSON.stringify(evalRes.exceptionDetails).slice(0, 500));
  const report = evalRes.result.value;

  if (shotPath) {
    const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
    writeFileSync(shotPath, Buffer.from(shot.data, 'base64'));
    console.log(`screenshot → ${shotPath}`);
  }

  writeFileSync(outPath || path.join(tmpdir(), 'accessible-audit.json'), JSON.stringify(report, null, 2));
  if (outPath) console.log(`report → ${outPath}`);

  if (has('json')) console.log(JSON.stringify(report, null, 2));
  else {
    console.log(format(report));
    if (baselinePath && existsSync(baselinePath)) console.log(compare(report, JSON.parse((await import('node:fs')).readFileSync(baselinePath, 'utf8'))));
    else console.log('\n  tip: pass --baseline <report.json> from your reference output to compare numerically.');
  }

  const issues = report.contrast.floorCount + report.contrast.ceilingCount + report.contrast.halationCount + report.hitTargets.aaCount + report.clipping.count + report.length.flags.length + report.palette.flags.length;
  ws.close();
  proc.kill();
  process.exit(issues > 0 ? 1 : 0);
} catch (e) {
  console.error('error:', e.message);
  proc.kill();
  process.exit(2);
} finally {
  rmSync(profile, { recursive: true, force: true });
}
