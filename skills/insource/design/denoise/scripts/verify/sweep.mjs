#!/usr/bin/env node
/**
 * sweep.mjs — walk an authenticated app route by route and record what each one did.
 *
 * Part of the `accessible` skill's verification scripts. No npm dependencies; Node >= 22.
 *
 *   node sweep.mjs --base http://localhost:5173 --state session.json --side after \
 *        --out sweep-after.json [--shots shots-after] [--crawl|--routes routes.json] \
 *        [--values "Total Funds,Total Users"] [--settle 15000] [--max 80] \
 *        [--not-found-probe /__a11y_not_found_probe__] [--not-found-path <regex>] [--skip-not-found]
 *
 * Run it once per build and diff the two records with parity.mjs. One route list must be
 * used for both sides — a page that exists on only one side is not a comparison.
 *
 * Why this exists rather than a screenshot of the page you were just told about: a redesign
 * claim of "nothing broke" needs the whole surface checked, and the failures that matter
 * hide on the pages nobody thought to look at.
 *
 * Two recording rules, both learned the hard way:
 *   - Every route gets a render guard. "No console errors" is also what a dead dev server
 *     reports, and an early version of this tool cheerfully returned a clean sweep against
 *     one.
 *   - Figures are polled until they stop moving, and an all-zero set is flagged instead of
 *     trusted, because 0 is a digit: "every card has a number in it" is not "the data
 *     loaded", and reading the skeleton as the result once made two builds look identically
 *     broken.
 *   - And a route that renders the app's *own* not-found page is reported as `NOT-FOUND`,
 *     because a dead port says `NOT RENDERED` while a deleted route says nothing at all: the
 *     404 screen mounts inside the real shell with a real heading, so the render guard passes
 *     it. That asymmetry let six routes which no longer existed in the router appear in a
 *     documented sweep of 73 as "0 failed to render".
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { openSession, sleep, verdict, restoreSession, valueReader } from './browser.mjs';

const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf(`--${n}`); return i === -1 ? d : argv[i + 1]; };
const has = (n) => argv.includes(`--${n}`);

const base = (flag('base', '') || '').replace(/\/$/, '');
if (!base) { console.error('usage: node sweep.mjs --base <url> [--state session.json] [--side name] [--out sweep.json] [--crawl|--routes f.json] [--values "a,b"] [--shots dir] [--settle 15000] [--max 120] [--ignore <regex>] [--not-found-probe <path>] [--not-found-path <regex>] [--skip-not-found]'); process.exit(2); }
const side = flag('side', 'a');
const outPath = flag('out', `sweep-${side}.json`);
const shotDir = flag('shots', null);
const statePath = flag('state', null);
const settleMs = Number(flag('settle', 15000));
const maxRoutes = Number(flag('max', 120));
const labels = (flag('values', '') || '').split(',').map((s) => s.trim()).filter(Boolean);
const loginPath = flag('login-path', 'login');
/** Override this if your app mounts somewhere unusual — see the render-guard note below. */
const rootSelector = flag('root-selector', 'main,#app,#root,#__next,[data-v-app],#nuxt');

/**
 * Not-found detection, on unless you switch it off.
 *
 * The guard cannot be a list of strings somebody remembers to pass. It asks the running app
 * what *its* not-found screen looks like — by navigating to a path that cannot exist — and
 * then recognises that screen wherever it turns up, including under a URL that still looks
 * perfectly legitimate. A catch-all route (`/:pathMatch(.*)*` in Vue Router, `path="*"` in
 * React Router) renders the 404 component *in place*, so `location.pathname` is unchanged and
 * the only way to know is to compare what the page says with what the probe said.
 *
 *   --not-found-probe <path>   the path used to fingerprint the app's 404 (default below)
 *   --not-found-path <regex>   extra URL pattern treated as a not-found route
 *   --skip-not-found           turn the extra navigations off (old A/B files stay comparable;
 *                              nothing else does)
 */
const NF = {
  on: !has('skip-not-found'),
  probe: flag('not-found-probe', '/__a11y_not_found_probe__'),
  pathRe: new RegExp(flag('not-found-path', '404|not[-_]?found|page[-_]?not[-_]?found'), 'i'),
  usable: false,
  landed: '',
  heading: '',
  lines: [],
  why: 'not checked (--skip-not-found)',
};

/** Pathname the app actually landed on, from whatever the page reported. */
const pathnameOf = (href) => {
  const h = String(href || '');
  if (!/^https?:\/\//i.test(h)) return '';
  try { return new URL(h).pathname.replace(/\/$/, '') || '/'; } catch { return ''; }
};

/** Reads back the page's own identity: landed path, h1 text, and the sentences it renders. */
const pageReader = (cap) => `(function(){
  var t=(document.body&&document.body.innerText)||'';var seen={},lines=[];
  t.split('\\n').forEach(function(s){var k=s.replace(/\\s+/g,' ').trim().toLowerCase();
    if(k.length<12||k.indexOf(' ')===-1||seen[k])return; seen[k]=1; lines.push(k.slice(0,120));});
  var h=[];document.querySelectorAll('h1').forEach(function(e){var x=(e.innerText||'').replace(/\\s+/g,' ').trim();if(x&&h.indexOf(x)===-1)h.push(x)});
  return JSON.stringify({path:location.pathname,h1:h.slice(0,3).join(' | '),lines:lines.slice(0,${cap})})})()`;

/** Per route: the landed path, the h1, and how many of the not-found sentences are on screen. */
const nfReader = (want) => `(function(){
  var t=(document.body&&document.body.innerText)||'';var L={},seen={};
  t.split('\\n').forEach(function(s){var k=s.replace(/\\s+/g,' ').trim().toLowerCase();
    if(k.length<12||seen[k])return; seen[k]=1; L[k.slice(0,120)]=1});
  var want=${JSON.stringify(want)},hit=0;
  want.forEach(function(k){if(L[k])hit++});
  var h=[];document.querySelectorAll('h1').forEach(function(e){var x=(e.innerText||'').replace(/\\s+/g,' ').trim();if(x&&h.indexOf(x)===-1)h.push(x)});
  return JSON.stringify({path:location.pathname,h1:h.slice(0,3).join(' | '),hit:hit,need:want.length})})()`;

/**
 * Console noise that belongs to the harness or the dev server rather than to either build.
 * Named rather than silently dropped, and parity.mjs re-reports anything it filtered.
 */
const IGNORE = [
  /\[vite\]/i, /Live reload/i, /Enabling hot module replacement/i,
  /Failed to fetch dynamically imported module/i,   // stale optimised-dep chunk after a restart
  /Download the React DevTools|Vue Devtools/i,
];
if (flag('ignore', '')) IGNORE.push(new RegExp(flag('ignore'), 'i'));

if (shotDir) mkdirSync(shotDir, { recursive: true });

const s = await openSession({ chrome: flag('chrome', null), startUrl: base });
if (statePath) {
  if (!existsSync(statePath)) { console.error(`no session file at ${statePath} — run auth.mjs --login first`); process.exit(2); }
  await restoreSession(s, statePath);
}

/* ------------------------------------------------------------ route list */
let routes = [];
if (flag('routes', null)) {
  const parsed = JSON.parse(readFileSync(flag('routes'), 'utf8'));
  // Accept a bare array of paths, or a previous sweep's output — reusing the exact list the
  // other side walked is the whole point, and re-typing it is how the two drift apart.
  routes = Array.isArray(parsed) ? parsed : (parsed.routes || []);
} else {
  // Crawl the navigation, not the whole site: a redesign pass changes chrome plus pages, and
  // the links a person can actually reach from the shell are the surface that matters.
  await s.goto(base);
  await s.settle({ timeoutMs: 10000 });
  const found = await s.evl(`(function(){
    var out=[];var here=location.origin;
    document.querySelectorAll('a[href]').forEach(function(a){
      var u;try{u=new URL(a.href,location.href)}catch(x){return}
      if(u.origin!==here)return;
      if(/\\.(png|jpe?g|svg|pdf|zip|csv)$/i.test(u.pathname))return;
      var p=u.pathname.replace(/\\/$/,'')||'/';
      if(out.indexOf(p)===-1)out.push(p);
    });
    return JSON.stringify(out);
  })()`, '[]');
  routes = JSON.parse(found);
  if (!routes.length) {
    console.error(`  \x1b[31mthe crawl found no same-origin links at ${base}\x1b[0m
  Either the nav is not anchor-based (router-link with click handlers, a JS menu), or you are
  not authenticated and got a login page. Pass an explicit --routes file, or check auth.mjs.`);
    s.close(); process.exit(3);
  }
}
routes = [...new Set(routes)].filter((r) => !r.includes(':')).slice(0, maxRoutes);
console.log(`  ${routes.length} routes · side "${side}" · ${base}`);

/* ------------------------------------------------- what this app's 404 looks like */
if (NF.on) {
  s.clearEvents();
  await s.goto(base + NF.probe);
  const pSnap = await s.settle({ timeoutMs: Math.min(settleMs, 8000), rootSelector });
  const pv = verdict(pSnap, {});
  if (!pv.rendered) {
    NF.why = `probe ${NF.probe} did not mount: ${pv.why} — not-found detection falls back to the URL pattern only`;
  } else {
    const p = JSON.parse(await s.evl(pageReader(30), '{}') || '{}');
    NF.landed = p.path || NF.probe;
    NF.heading = p.h1 || '';
    // Sentences the not-found page says and the probe path itself does not appear in: the
    // dynamic "Route: /x" line differs on every URL, so it can never be a shared signal.
    NF.lines = (p.lines || []).filter((l) => !l.includes(NF.probe.toLowerCase()));
    NF.usable = !!(NF.heading || NF.lines.length);
    NF.why = NF.usable
      ? `fingerprinted at ${NF.landed} — heading "${NF.heading || '(none)'}", ${NF.lines.length} sentence(s)`
      : `probe at ${NF.probe} mounted but said nothing distinctive — URL pattern only`;
  }
  s.clearEvents();
  console.log(`  not-found probe: ${NF.why}`);
}

/* ------------------------------------------------------------------ walk */
const results = {};
const paths = [...new Set(routes.map((r) => (r.startsWith('http') ? new URL(r).pathname : r)).map((r) => r.replace(/\/$/, '') || '/'))].filter((r) => r !== '/');
const walk = ['/', ...paths];
for (const route of walk) {
  s.clearEvents();
  const t0 = Date.now();
  const nav = await s.goto(base + route);
  const snap = await s.settle({ timeoutMs: settleMs, rootSelector });
  /*
   * Two things have to be true before a route counts as rendered: the navigation itself
   * succeeded, and something that looks like the application mounted. A browser's own
   * connection-refused page has a heading, paragraphs and dozens of nodes, so it clears any
   * text-or-count threshold — which is how an early version of this walk reported five
   * healthy pages against a port with nothing listening on it.
   */
  const v = verdict(snap, { navError: nav?.errorText || null });
  const url = snap?.url ?? '(no answer)';
  // Where the app says it is. A navigation that never completed leaves the tab on whatever it
  // last committed, so "landed" would be a stale answer rather than a redirect — record
  // nothing in that case.
  let landed = nav?.errorText ? '' : (pathnameOf(url) || route);
  if (String(url).includes(loginPath) && !route.includes(loginPath)) {
    results[route] = { url, landed, notFound: false, rendered: false, why: 'bounced to login — the session did not hold', errors: [], values: {} };
    console.log(`  \x1b[31mAUTH\x1b[0m  ${route}  → bounced to ${url}`);
    continue;
  }
  /*
   * Did the app answer this URL with its own not-found screen? Four signals, any of which is
   * enough: the URL moved to the path the probe landed on; the URL matches a not-found-looking
   * pattern it did not ask for; the page's h1 says what the probe's h1 said; the page contains
   * most of the sentences the probe contained. The last two are the ones that catch a catch-all
   * route, where nothing about the URL changes at all. Only worth asking of a page that
   * mounted — a browser error page has no opinion about routes.
   */
  const nf = { hit: 0, need: 0, how: '' };
  if (NF.on && snap && v.rendered) {
    const info = JSON.parse(await s.evl(nfReader(NF.lines), '{}') || '{}');
    nf.hit = Number(info.hit || 0); nf.need = Number(info.need || 0);
    if (info.path) landed = String(info.path).replace(/\/$/, '') || '/'; // the page's own answer beats the URL we were handed
    const movedToProbe = NF.landed && landed === NF.landed && landed !== route;
    const ontoNotFoundUrl = NF.pathRe.test(landed) && landed !== route;
    const sameHeading = NF.usable && !!NF.heading && info.h1 === NF.heading;
    const sameBody = NF.usable && nf.need > 0 && nf.hit >= Math.max(2, Math.ceil(nf.need * 0.5));
    const how = [movedToProbe && 'redirected to the not-found route', ontoNotFoundUrl && 'landed on a not-found URL',
      sameHeading && 'same heading as the 404 probe', sameBody && `${nf.hit}/${nf.need} of the 404 probe's sentences`].filter(Boolean);
    if (how.length) nf.how = how.join(', ');
  }
  const notFound = !!nf.how;
  // Asking for the not-found page is not the same as being served it.
  const expected = notFound && (NF.pathRe.test(route) || route === NF.landed);
  let values = {};
  if (labels.length && v.rendered && !notFound) values = JSON.parse(await s.evl(valueReader(labels), '{}') || '{}');
  const errs = s.events(IGNORE).filter((e) => e.kind === 'error');
  const allZero = labels.length > 0 && Object.keys(values).length > 0 && !Object.values(values).some((x) => /[1-9]/.test(x));
  results[route] = {
    url, landed, notFound, notFoundExpected: expected, notFoundWhy: nf.how,
    rendered: v.rendered, why: v.why, heading: snap?.heading || '', chars: snap?.chars ?? 0,
    mounted: snap?.mounted ?? 0, values, allZero, errors: errs, tookMs: Date.now() - t0,
  };
  const r = results[route];
  if (shotDir) await s.shot(path.join(shotDir, (route.replace(/^\//, '') || 'root').replace(/[/?&=%]/g, '-')) + '.png');
  // A route that never mounted reports the last URL the browser committed, which is a stale
  // answer rather than a redirect — only say "it moved" when the page actually mounted.
  const moved = r.rendered && landed && landed !== route ? ` → ${landed}` : '';
  const tag = notFound && !expected ? '\x1b[35mNOT-FOUND\x1b[0m'
    : notFound ? '\x1b[36m404 page\x1b[0m'
    : !r.rendered ? '\x1b[31mNOT RENDERED\x1b[0m'
    : errs.length ? `\x1b[33m${errs.length} err\x1b[0m` : '\x1b[32mok\x1b[0m';
  console.log(`  ${route.padEnd(42)} ${tag}${r.why ? ' ' + r.why : ''}${notFound && !expected ? ' ' + r.notFoundWhy : ''}${moved ? `\x1b[2m${moved}\x1b[0m` : ''}${allZero ? ' \x1b[33mall figures zero — captured a loading skeleton, not a result\x1b[0m' : ''}${errs.length ? '\n      ' + errs.map((e) => e.text.slice(0, 150)).join('\n      ') : ''}`);
}

const dead = Object.entries(results).filter(([, r]) => !r.rendered).map(([k]) => k);
const notFoundRoutes = Object.entries(results).filter(([, r]) => r.notFound && !r.notFoundExpected).map(([k]) => k);
const errs = Object.entries(results).filter(([, r]) => r.errors.length).map(([k]) => k);
writeFileSync(outPath, JSON.stringify({
  side, base, at: new Date().toISOString(), routes: walk, results,
  notFoundProbe: { checked: NF.on, probePath: NF.probe, usable: NF.usable, landed: NF.landed, heading: NF.heading, sentences: NF.lines.length, note: NF.why },
}, null, 2));
console.log(`\n  ${side}: ${walk.length} routes · ${dead.length} did not render · \x1b[35m${notFoundRoutes.length} served the app's not-found page\x1b[0m · ${errs.length} with console errors`);
if (dead.length) console.log('    dead: ' + dead.join(', '));
if (notFoundRoutes.length) console.log(`    not-found: ${notFoundRoutes.join(', ')}\n      these *did* render — that is exactly why "0 failed to render" is not the same as "every route still exists"`);
if (NF.on && !NF.usable) console.log(`    \x1b[33mnot-found detection was weak: ${NF.why}\x1b[0m`);
console.log(`  wrote ${outPath}${shotDir ? ' and ' + shotDir : ''}`);
s.close();
