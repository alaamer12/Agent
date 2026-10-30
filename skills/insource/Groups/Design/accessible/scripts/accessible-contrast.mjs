#!/usr/bin/env node
/**
 * accessible-contrast.mjs — measure the contrast text ACTUALLY has, not the contrast
 * its CSS claims it has.
 *
 *   node accessible-contrast.mjs <file.html|url> [--chrome path] [--width 1440]
 *                              [--height 1000] [--fails-only] [--json] [--csv out.csv]
 *
 * Why this exists next to accessible-audit.mjs:
 *
 * The audit resolves a text run's background by walking up the DOM compositing
 * background-colour values. That is an approximation, and it breaks on exactly the
 * cases that matter most:
 *   - text over a GRADIENT — the left of the string sits on a different colour than
 *     the right, so one ratio per run is a fiction
 *   - text over an IMAGE or a canvas
 *   - translucent overlays, backdrop-filter, mix-blend-mode
 *   - a coloured border or box-shadow bleeding under descenders
 *
 * So this script screenshots the rendered page, decodes the PNG, and for every text
 * run samples the pixels that are actually behind it. It reports two numbers:
 *
 *   inner  — contrast between the glyph colour and the dominant measured backdrop
 *   worst  — contrast against the single nearest-luminance pixel in that box, i.e. the
 *            point where the text is hardest to read. A gradient can pass "inner" and
 *            fail "worst", which is precisely the failure being hidden.
 *
 * Pure Node, no npm dependencies. Needs Node >= 22 (global WebSocket) and headless Chrome.
 */

import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import zlib from 'node:zlib';

const argv = process.argv.slice(2);
const target = argv.find((a) => !a.startsWith('--') && argv[argv.indexOf(a) - 1] !== '--chrome' && argv[argv.indexOf(a) - 1] !== '--csv');
const flag = (n, f) => { const i = argv.indexOf(`--${n}`); return i === -1 ? f : argv[i + 1]; };
if (!target) { console.error('usage: node accessible-contrast.mjs <file.html|url> [--chrome path] [--width 1440] [--height 1000] [--fails-only] [--json] [--csv out.csv]'); process.exit(2); }
const url = /^https?:\/\//.test(target) ? target : 'file://' + path.resolve(target);
const width = Number(flag('width', 1440)), height = Number(flag('height', 1000));

/* ------------------------------------------------ minimal PNG decoder (8-bit) */

function decodePng(buf) {
  if (buf.readUInt32BE(0) !== 0x89504e47) throw new Error('not a PNG');
  let pos = 8, w = 0, h = 0, depth = 0, ctype = 0, idat = [];
  while (pos < buf.length) {
    const len = buf.readUInt32BE(pos);
    const type = buf.toString('ascii', pos + 4, pos + 8);
    const data = buf.subarray(pos + 8, pos + 8 + len);
    if (type === 'IHDR') { w = data.readUInt32BE(0); h = data.readUInt32BE(4); depth = data[8]; ctype = data[9]; if (data[12] !== 0) throw new Error('interlaced PNG unsupported'); }
    else if (type === 'IDAT') idat.push(data);
    else if (type === 'IEND') break;
    pos += 12 + len;
  }
  if (depth !== 8) throw new Error(`bit depth ${depth} unsupported`);
  const ch = ctype === 6 ? 4 : ctype === 2 ? 3 : ctype === 0 ? 1 : (() => { throw new Error(`colour type ${ctype} unsupported`); })();
  const raw = zlib.inflateSync(Buffer.concat(idat));
  const stride = w * ch;
  const out = Buffer.alloc(h * stride);
  const paeth = (a, b, c) => { const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c); return pa <= pb && pa <= pc ? a : pb <= pc ? b : c; };
  let rp = 0;
  for (let y = 0; y < h; y++) {
    const f = raw[rp++];
    for (let x = 0; x < stride; x++) {
      const v = raw[rp + x];
      const a = x >= ch ? out[y * stride + x - ch] : 0;
      const b = y > 0 ? out[(y - 1) * stride + x] : 0;
      const c = (x >= ch && y > 0) ? out[(y - 1) * stride + x - ch] : 0;
      let val;
      switch (f) {
        case 0: val = v; break;
        case 1: val = v + a; break;
        case 2: val = v + b; break;
        case 3: val = v + ((a + b) >> 1); break;
        case 4: val = v + paeth(a, b, c); break;
        default: throw new Error('bad filter ' + f);
      }
      out[y * stride + x] = val & 0xff;
    }
    rp += stride;
  }
  return { w, h, ch, data: out };
}

/* -------------------------------------------------------------- colour maths */

const lin = (c) => { const s = c / 255; return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4; };
const Y = (r, g, b) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
const ratio = (l1, l2) => { const [a, b] = [l1, l2].sort((p, q) => q - p); return (a + 0.05) / (b + 0.05); };
const hex = (r, g, b) => '#' + [r, g, b].map((v) => v.toString(16).padStart(2, '0')).join('');

/* -------------------------------------------------------- browser + CDP glue */

async function findChrome() {
  const cands = [flag('chrome', process.env.CHROME_PATH)].filter(Boolean);
  for (const root of [process.env.HOME, '/root', '/home/codespace'].filter(Boolean)) {
    const dir = path.join(root, '.cache/ms-playwright');
    if (!exists(dir)) continue;
    for (const d of readdir(dir)) if (d.startsWith('chromium')) {
      cands.push(path.join(dir, d, 'chrome-linux64/chrome'), path.join(dir, d, 'chrome-headless-shell-linux64/chrome-headless-shell'));
    }
  }
  cands.push('/usr/bin/google-chrome', '/usr/bin/chromium');
  for (const c of cands) if (c && exists(c)) return c;
  throw new Error('no Chrome found — pass --chrome /path/to/chrome');
}
const fsmod = await import('node:fs');
const exists = (p) => { try { fsmod.statSync(p); return true; } catch { return false; } };
const readdir = (p) => fsmod.readdirSync(p);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const profile = mkdtempSync(path.join(tmpdir(), 'acc-contrast-'));
const port = 9900 + Math.floor(Math.random() * 90);
let chrome;
try { chrome = await findChrome(); } catch (e) { console.error('error:', e.message); process.exit(2); }

const proc = spawn(chrome, ['--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
  '--hide-scrollbars', '--force-device-scale-factor=1', `--window-size=${width},${height}`,
  `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, '--no-first-run', 'about:blank'],
  { stdio: ['ignore', 'ignore', 'ignore'] });
proc.on('exit', (code) => { rmSync(profile, { recursive: true, force: true }); if (code) { console.error('chrome exited', code); process.exit(2); } });

let version = null;
for (let i = 0; i < 80; i++) { try { const r = await fetch(`http://127.0.0.1:${port}/json/version`); if (r.ok) { version = await r.json(); break; } } catch { } await sleep(250); }
if (!version) { console.error('DevTools never came up'); proc.kill(); process.exit(2); }

const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const page = list.find((t) => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });
let mid = 0; const wait = new Map();
ws.addEventListener('message', (e) => { const m = JSON.parse(e.data); if (m.id && wait.has(m.id)) { const { ok, no } = wait.get(m.id); wait.delete(m.id); m.error ? no(new Error(m.error.message)) : ok(m.result); } });
const send = (method, params = {}) => { const i = ++mid; ws.send(JSON.stringify({ id: i, method, params })); return new Promise((ok, no) => wait.set(i, { ok, no })); };

await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url });
await sleep(2500);

/* ask the page for every text run and its authored colour */
const runs = await send('Runtime.evaluate', {
  expression: `(() => {
    // Resolve the authored colour to real sRGB *in the page*. Chrome hands back oklch(),
    // oklab(), lab(), lch() and color-mix() exactly as written — from computed styles and
    // from canvas fillStyle alike — so a node-side parser sees nothing and every text run
    // on a modern palette is silently dropped. Paint it and read the pixel.
    const px = document.createElement('canvas'); px.width = 1; px.height = 1;
    const cx = px.getContext('2d', { willReadFrequently: true });
    const SENT = 'rgba(0, 0, 0, 0)';
    const res = (str) => {
      cx.globalCompositeOperation = 'copy'; cx.fillStyle = SENT; cx.fillStyle = str;
      if (cx.fillStyle === SENT) return null;
      cx.clearRect(0, 0, 1, 1); cx.fillRect(0, 0, 1, 1);
      const d = cx.getImageData(0, 0, 1, 1).data;
      return 'rgba(' + d[0] + ', ' + d[1] + ', ' + d[2] + ', ' + (d[3] / 255).toFixed(3) + ')';
    };
    const out = [];
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      if (!n.nodeValue || !n.nodeValue.trim()) continue;
      const el = n.parentElement; if (!el) continue;
      const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || cs.display === 'none' || Number(cs.opacity) < 0.05) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) {
        if (r.width < 3 || r.height < 3 || r.bottom < 0 || r.right < 0 || r.top > innerHeight) continue;
        out.push({ text: n.nodeValue.trim().slice(0, 44), size: Math.round(parseFloat(cs.fontSize) * 10) / 10,
          weight: cs.fontWeight, color: res(cs.color), x: Math.round(r.left), y: Math.round(r.top),
          w: Math.round(r.width), h: Math.round(r.height) });
      }
    }
    return JSON.stringify(out);
  })()`,
  returnByValue: true,
});
const textRuns = JSON.parse(runs.result.value);

const shot = await send('Page.captureScreenshot', { format: 'png' });
const img = decodePng(Buffer.from(shot.data, 'base64'));

/* ------------------------------------------------------- measure each run */

function parseAuthored(str) {
  // NB: [^)]] closes the class at the first ] — it silently demanded a literal
  // bracket and matched nothing. [^)]+ is the intent.
  const m = str && str.match(/rgba?\(([^)]+)\)/);
  if (!m) return null;
  const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
  return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
}

const results = [];
for (const run of textRuns) {
  const authored = parseAuthored(run.color);
  if (!authored) continue;   // genuinely unresolvable colour, not a parse gap
  // Sample the backdrop from a RING around the glyphs, not from inside them. Sampling
  // inside the box counts anti-aliased edge pixels — which are blends of ink and surface —
  // as backdrop, and every run then reports a worst-case of ~1.2 against its own halo.
  // The ring is untouched surface, and for a gradient it still spans the run's full width.
  const M = 4;
  const rx0 = Math.max(0, run.x - M), rx1 = Math.min(img.w - 1, run.x + run.w + M);
  const ry0 = Math.max(0, run.y - M), ry1 = Math.min(img.h - 1, run.y + run.h + M);
  const ix0 = Math.max(0, run.x), ix1 = Math.min(img.w - 1, run.x + run.w);
  const iy0 = Math.max(0, run.y), iy1 = Math.min(img.h - 1, run.y + run.h);
  if (rx1 <= rx0 || ry1 <= ry0) continue;

  const buckets = new Map();
  const backdrop = [];
  let glyphPixels = 0, boxPixels = 0;
  const inkDist = (r, g, b) => Math.abs(r - authored.r) + Math.abs(g - authored.g) + Math.abs(b - authored.b);
  for (let y = ry0; y <= ry1; y++) {
    const insideY = y >= iy0 && y <= iy1;
    for (let x = rx0; x <= rx1; x++) {
      const i = (y * img.w + x) * img.ch;
      const r = img.data[i], g = img.data[i + 1], b = img.data[i + 2];
      if (insideY && x >= ix0 && x <= ix1) {
        boxPixels++;
        if (inkDist(r, g, b) < 70) glyphPixels++;
        continue;                                  // inside the glyphs: not backdrop
      }
      const key = `${r >> 3},${g >> 3},${b >> 3}`;
      buckets.set(key, (buckets.get(key) || 0) + 1);
      backdrop.push({ r, g, b, L: Y(r, g, b) });
    }
  }
  if (backdrop.length < 20) continue;              // too little clean surface to judge

  const inkL = Y(authored.r, authored.g, authored.b);
  // Dominant backdrop colour, ignoring any bucket that is really the ink itself.
  const inkKey = `${authored.r >> 3},${authored.g >> 3},${authored.b >> 3}`;
  let bestKey = null, bestCount = -1;
  for (const [k, v] of buckets) {
    if (k === inkKey) continue;
    const [kr, kg, kb] = k.split(',').map((x) => Number(x) << 3);
    if (inkDist(kr, kg, kb) < 90) continue;         // still essentially the glyph colour
    if (v > bestCount) { bestCount = v; bestKey = k; }
  }
  if (!bestKey) continue;
  const [br, bg, bb] = bestKey.split(',').map((v) => Math.min(255, (Number(v) << 3) + 4));
  const bgL = Y(br, bg, bb);

  const inner = ratio(inkL, bgL);
  // Worst = the *surface* pixel whose luminance comes closest to the ink's. Restricted to
  // pixels near the dominant backdrop colour, because a ring around one label will also
  // catch the glyphs of its neighbour — and comparing this text against someone else's ink
  // reports a bogus 1.00 on a perfectly flat background. On a flat surface worst ~= inner;
  // on a gradient or an image it is the end where the text disappears.
  const near = (p) => Math.abs(p.r - br) + Math.abs(p.g - bg) + Math.abs(p.b - bb) < 90;
  let worst = Infinity;
  for (const p of backdrop) {
    if (!near(p)) continue;
    const rr = ratio(inkL, p.L);
    if (rr < worst) worst = rr;
  }
  if (worst === Infinity) worst = inner;
  if (boxPixels) glyphPixels = Math.round((glyphPixels / boxPixels) * 100); else glyphPixels = 0;
  const large = run.size >= 24 || (run.size >= 18.66 && Number(run.weight) >= 700);
  const need = large ? 3 : 4.5;
  results.push({
    text: run.text, size: run.size, weight: run.weight, large,
    authored: hex(authored.r, authored.g, authored.b),
    measuredBg: hex(br, bg, bb),
    bgShare: Math.round((bestCount / backdrop.length) * 100),
    inkCoverage: glyphPixels,
    inner: Math.round(inner * 100) / 100,
    worst: Math.round(worst * 100) / 100,
    need,
    passInner: inner >= need,
    passWorst: worst >= need,
    // the gap is the interesting part: authored-CSS contrast looks fine, the rendered
    // right-hand end of the gradient does not
    gradientRisk: Math.round((inner - worst) * 100) / 100,
    box: `${run.x},${run.y} ${run.w}x${run.h}`,
  });
}

const fails = results.filter((r) => !r.passInner || !r.passWorst);
const risky = results.filter((r) => r.passInner && !r.passWorst);

if (argv.includes('--json')) { console.log(JSON.stringify({ url, runs: results }, null, 2)); }
else {
  const show = argv.includes('--fails-only') ? fails : results;
  console.log(`\n\x1b[1m  inner contrast — ${path.basename(target)}\x1b[0m`);
  console.log(`  ${results.length} text runs measured from rendered pixels · ${fails.length} failing · ${risky.length} pass on average but fail at their worst point\n`);
  console.log(`    ${'inner'.padStart(6)} ${'worst'.padStart(6)} need  authored  measured-bg  bg%  ink%  text`);
  console.log('    ' + '─'.repeat(96));
  for (const r of show) {
    const col = !r.passWorst || !r.passInner ? '\x1b[31m' : r.gradientRisk > 1.5 ? '\x1b[33m' : '\x1b[32m';
    console.log(`  ${col}${String(r.inner).padStart(6)} ${String(r.worst).padStart(6)} ${String(r.need).padStart(5)}  ${r.authored}  ${r.measuredBg.padEnd(9)} ${String(r.bgShare).padStart(3)}% ${String(r.inkCoverage).padStart(4)}%\x1b[0m  ${r.text.slice(0, 40)}`);
  }
  if (risky.length) {
    console.log(`\n  \x1b[33mHidden by any computed-style checker (${risky.length}):\x1b[0m`);
    for (const r of risky.slice(0, 8)) console.log(`    "${r.text.slice(0, 36)}" averages ${r.inner}:1 but drops to ${r.worst}:1 at its worst pixel`);
  }
}

if (flag('csv', null)) {
  const hdr = ['text', 'size', 'authored', 'measured_bg', 'bg_share', 'ink_coverage', 'inner', 'worst', 'need', 'pass_inner', 'pass_worst'];
  const rows = results.map((r) => [JSON.stringify(r.text), r.size, r.authored, r.measuredBg, r.bgShare, r.inkCoverage, r.inner, r.worst, r.need, r.passInner, r.passWorst].join(','));
  fsmod.writeFileSync(flag('csv'), [hdr.join(','), ...rows].join('\n'));
  console.log(`\n  csv → ${flag('csv')}`);
}

ws.close(); proc.kill();
process.exit(fails.length ? 1 : 0);
