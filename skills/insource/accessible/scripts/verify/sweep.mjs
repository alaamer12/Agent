#!/usr/bin/env node
/**
 * sweep.mjs — walk an authenticated app route by route and record what each one did.
 *
 * Part of the `accessible` skill's verification scripts. No npm dependencies; Node >= 22.
 *
 *   node sweep.mjs --base http://localhost:5173 --state session.json --side after \
 *        --out sweep-after.json [--shots shots-after] [--crawl|--routes routes.json] \
 *        [--values "Total Funds,Total Users"] [--settle 15000] [--max 80]
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
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { openSession, sleep, verdict, restoreSession, valueReader } from './browser.mjs';

const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf(`--${n}`); return i === -1 ? d : argv[i + 1]; };
const has = (n) => argv.includes(`--${n}`);

const base = (flag('base', '') || '').replace(/\/$/, '');
if (!base) { console.error('usage: node sweep.mjs --base <url> [--state session.json] [--side name] [--out sweep.json] [--crawl|--routes f.json] [--values "a,b"] [--shots dir]'); process.exit(2); }
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
  if (String(url).includes(loginPath) && !route.includes(loginPath)) {
    results[route] = { url, rendered: false, why: 'bounced to login — the session did not hold', errors: [], values: {} };
    console.log(`  \x1b[31mAUTH\x1b[0m  ${route}  → bounced to ${url}`);
    continue;
  }
  let values = {};
  if (labels.length && v.rendered) values = JSON.parse(await s.evl(valueReader(labels), '{}') || '{}');
  const errs = s.events(IGNORE).filter((e) => e.kind === 'error');
  const allZero = labels.length > 0 && Object.keys(values).length > 0 && !Object.values(values).some((x) => /[1-9]/.test(x));
  results[route] = {
    url, rendered: v.rendered, why: v.why, heading: snap?.heading || '', chars: snap?.chars ?? 0,
    mounted: snap?.mounted ?? 0, values, allZero, errors: errs, tookMs: Date.now() - t0,
  };
  const r = results[route];
  if (shotDir) await s.shot(path.join(shotDir, (route.replace(/^\//, '') || 'root').replace(/[/?&=%]/g, '-')) + '.png');
  const tag = !r.rendered ? '\x1b[31mNOT RENDERED\x1b[0m' : errs.length ? `\x1b[33m${errs.length} err\x1b[0m` : '\x1b[32mok\x1b[0m';
  console.log(`  ${route.padEnd(42)} ${tag}${r.why ? ' ' + r.why : ''}${allZero ? ' \x1b[33mall figures zero — captured a loading skeleton, not a result\x1b[0m' : ''}${errs.length ? '\n      ' + errs.map((e) => e.text.slice(0, 150)).join('\n      ') : ''}`);
}

const dead = Object.entries(results).filter(([, r]) => !r.rendered).map(([k]) => k);
const errs = Object.entries(results).filter(([, r]) => r.errors.length).map(([k]) => k);
writeFileSync(outPath, JSON.stringify({ side, base, at: new Date().toISOString(), routes: walk, results }, null, 2));
console.log(`\n  ${side}: ${walk.length} routes · ${dead.length} did not render · ${errs.length} with console errors`);
if (dead.length) console.log('    dead: ' + dead.join(', '));
console.log(`  wrote ${outPath}${shotDir ? ' and ' + shotDir : ''}`);
s.close();
