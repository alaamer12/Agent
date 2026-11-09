#!/usr/bin/env node
/**
 * browser.mjs — one headless Chrome session, driven over CDP, with the failure modes this
 * skill already walked into designed out of it.
 *
 * Shared by auth.mjs and sweep.mjs. No npm dependencies; Node >= 22 (global WebSocket).
 *
 * Four things here exist because each one produced a confidently wrong conclusion first:
 *
 * 1. A fixed --remote-debugging-port. If a browser from an earlier run still holds it, the
 *    new Chrome fails to bind, /json/version answers anyway from the OLD instance, and every
 *    command goes to a wedged tab. The walk then hangs with no output at all, which looks
 *    like a broken app rather than a broken harness. Port 0 plus the DevToolsActivePort file
 *    guarantees the instance you talk to is the one you spawned.
 *
 * 2. Untimed Runtime.evaluate. One unanswerable eval stops the whole sweep forever. Every
 *    call has a ceiling and a fallback, so a dead page is recorded as a dead page.
 *
 * 3. Trusting "no console errors". That is also what a dead dev server, a blank page, or a
 *    page that never mounted reports. Two signals are needed, because one is never enough:
 *    the navigation's own errorText, and a mounted application root. A node-count floor alone
 *    passed five healthy routes against a port with nothing listening — Chrome's error page
 *    has a heading, real text and dozens of nodes.
 *
 * 4. Filtering Log.entryAdded on source 'js'. The real value is 'javascript', so the
 *    listener never fired and a page with an injected error still reported clean.
 */
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, readFileSync, writeFileSync, existsSync, readdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** $CHROME_PATH, then Playwright's cache, then common system locations. */
export function findChrome(explicit) {
  const candidates = [];
  if (explicit) candidates.push(explicit);
  if (process.env.CHROME_PATH) candidates.push(process.env.CHROME_PATH);
  for (const root of [process.env.HOME, '/root', '/home/codespace'].filter(Boolean)) {
    const dir = path.join(root, '.cache/ms-playwright');
    if (!existsSync(dir)) continue;
    for (const build of readdirSync(dir)) {
      if (!build.startsWith('chromium')) continue;
      candidates.push(
        path.join(dir, build, 'chrome-linux64/chrome'),
        path.join(dir, build, 'chrome-linux/chrome'),
        path.join(dir, build, 'chrome-headless-shell-linux64/chrome-headless-shell'),
      );
    }
  }
  for (const p of ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']) candidates.push(p);
  const hit = candidates.find((c) => c && existsSync(c));
  if (!hit) throw new Error('no Chrome binary found — pass --chrome /path/to/chrome');
  return hit;
}

/**
 * Open a session. `startUrl` is passed on the command line rather than navigated to later:
 * a cross-document navigation away from about:blank can hand the tab a new target, leaving
 * the attached websocket pointed at a detached one.
 */
export async function openSession({ chrome, startUrl = 'about:blank', width = 1440, height = 1000, keepProfile } = {}) {
  const profile = mkdtempSync(path.join(tmpdir(), 'a11y-'));
  const proc = spawn(findChrome(chrome), [
    '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
    '--hide-scrollbars', `--window-size=${width},${height}`,
    '--remote-debugging-port=0', `--user-data-dir=${profile}`, '--no-first-run', startUrl,
  ], { stdio: 'ignore' });

  const close = () => {
    try { proc.kill(); } catch { /* gone */ }
    if (keepProfile) return;
    // Chrome is still writing into the profile when we kill it, so this can transiently
    // fail with ENOTEMPTY. It is a temp directory: dropping it is best-effort, never fatal.
    try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 }); } catch { /* left behind in tmp */ }
  };
  process.on('exit', close);

  let port = 0;
  for (let i = 0; i < 160 && !port; i++) {
    try { port = Number(readFileSync(path.join(profile, 'DevToolsActivePort'), 'utf8').split('\n')[0]); } catch { /* not written yet */ }
    if (!port) await sleep(250);
  }
  if (!port) { close(); throw new Error('chrome never published a debugging port'); }

  let tabs = [];
  for (let i = 0; i < 40 && !tabs.length; i++) {
    try { tabs = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).filter((t) => t.type === 'page'); } catch { await sleep(250); }
  }
  if (!tabs.length) { close(); throw new Error('no page target on the browser we spawned'); }

  const ws = new WebSocket(tabs[0].webSocketDebuggerUrl);
  await new Promise((ok, no) => { ws.addEventListener('open', ok); ws.addEventListener('error', no); });

  let id = 0;
  const waiting = new Map();
  const events = [];
  ws.addEventListener('message', (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && waiting.has(msg.id)) {
      const { resolve, reject } = waiting.get(msg.id);
      waiting.delete(msg.id);
      msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
      return;
    }
    if (msg.method === 'Runtime.exceptionThrown') {
      const d = msg.params.exceptionDetails;
      events.push({ kind: 'error', text: d.exception?.description || d.text || 'exception' });
    } else if (msg.method === 'Runtime.consoleAPICalled') {
      if (msg.params.type === 'error' || msg.params.type === 'warning') {
        const text = (msg.params.args || []).map((a) => a.value ?? a.description ?? a.unserializableValue ?? '').join(' ');
        events.push({ kind: msg.params.type, text });
      }
    } else if (msg.method === 'Log.entryAdded') {
      const e = msg.params.entry;
      if (e.level === 'error' && e.source === 'javascript') events.push({ kind: 'error', text: e.text });
    }
  });

  const send = (method, params = {}) => {
    const mid = ++id;
    ws.send(JSON.stringify({ id: mid, method, params }));
    return new Promise((resolve, reject) => waiting.set(mid, { resolve, reject }));
  };
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Log.enable');
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });

  /** Bounded eval. A page that will not answer is a finding, not a place to hang. */
  const evl = async (expression, fallback = null, ms = 8000) => {
    try {
      const r = await Promise.race([
        send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }),
        sleep(ms).then(() => null),
      ]);
      return r === null ? fallback : (r.result?.value ?? fallback);
    } catch { return fallback; }
  };

  return {
    send, evl, close, profile,
    /** Console output since the last clear(), de-duplicated, with an ignore list. */
    events(ignore = []) {
      const seen = new Set();
      return events.filter((e) => {
        const t = String(e.text).replace(/\s+/g, ' ').trim();
        if (!t || ignore.some((re) => re.test(t))) return false;
        const key = e.kind + '\u0000' + t.slice(0, 200);
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      }).map((e) => ({ kind: e.kind, text: String(e.text).replace(/\s+/g, ' ').trim().slice(0, 240) }));
    },
    clearEvents: () => { events.length = 0; },
    /** Returns the CDP result — `errorText` is the only reliable signal that the navigation
     * itself failed. A Chrome error page has real text and real nodes, so no content-based
     * check can tell it apart from an app that rendered. */
    async goto(url) { return send('Page.navigate', { url }); },
    async shot(file) {
      const png = await send('Page.captureScreenshot', { format: 'png' });
      writeFileSync(file, Buffer.from(png.data, 'base64'));
      return file;
    },
    /**
     * Wait for content to stop changing — not for a fixed number of milliseconds.
     * Returns null if the page never answered at all, which the caller must treat as a
     * failure rather than as "no errors".
     *
     * `root` records whether anything that looks like the application itself mounted. It is
     * here because a browser's own error page has a heading, several paragraphs and dozens of
     * nodes, and passes every text-and-count test you can devise against it.
     */
    async settle({ timeoutMs = 15000, minChars = 60, stableFor = 3, rootSelector = 'main' } = {}) {
      const started = Date.now();
      let last = '', stable = 0, snap = null;
      while (Date.now() - started < timeoutMs) {
        await sleep(700);
        const raw = await evl(`(function(){var t=(document.body&&document.body.innerText)||'';
          return JSON.stringify({url:location.href,chars:t.replace(/\\s+/g,' ').trim().length,
            mounted:document.querySelectorAll('body *').length,
            root:!!document.querySelector(${JSON.stringify(rootSelector)}),
            heading:(function(){var e=document.querySelector('h1,h2');return e?e.innerText.replace(/\\s+/g,' ').trim().slice(0,90):''})()})})()`, null, 6000);
        if (raw === null) continue;
        snap = JSON.parse(raw);
        stable = raw === last ? stable + 1 : 0;
        last = raw;
        if (stable >= stableFor && snap.chars >= minChars) return snap;
      }
      return snap;
    },
  };
}

/**
 * Label a settle() result honestly. `mounted` is measured against the whole body because a
 * shell-only render (nav present, page absent) still clears a low selector-specific floor.
 */
export function verdict(snap, { minMounted = 25, navError = null } = {}) {
  if (navError) return { rendered: false, why: `navigation failed: ${navError}` };
  if (!snap) return { rendered: false, why: 'the page never answered' };
  if (snap.mounted < minMounted) return { rendered: false, why: `only ${snap.mounted} nodes mounted` };
  if (snap.root === false) return { rendered: false, why: 'no application root — this is a browser error page, not the app' };
  return { rendered: true, why: '' };
}

/** Replay a session written by auth.mjs --state. Returns the origin it was captured on. */
export async function restoreSession(s, statePath) {
  const st = JSON.parse(readFileSync(statePath, 'utf8'));
  await s.send('Network.enable');
  if (st.cookies?.length) {
    await s.send('Network.setCookies', { cookies: st.cookies.map((c) => ({ ...c, sameSite: c.sameSite || 'Unset' })) });
  }
  if (st.origin) await s.goto(st.origin);
  if (st.localStorage && Object.keys(st.localStorage).length) {
    await s.evl(`(function(){try{Object.entries(${JSON.stringify(st.localStorage)}).forEach(function(e){localStorage.setItem(e[0],e[1])})}catch(x){}})()`);
  }
  return st.origin || '';
}

/**
 * Pull label→figure pairs out of the rendered text, for value parity between two builds.
 * Deliberately generic: it reads what a person reads off the screen, so it works on any
 * framework and does not care how the number got there.
 */
export function valueReader(labels) {
  return `(function(){
    function clean(s){return (s||'').replace(/\\s+/g,' ').trim();}
    var txt=clean(document.body&&document.body.innerText); var out={};
    (${JSON.stringify(labels)}).forEach(function(L){
      var i=txt.toLowerCase().indexOf(L.toLowerCase()); if(i<0) return;
      var m=txt.slice(i+L.length).match(/^[\\s]*([\\d][\\d,\\.]*\\s*(?:%|of[\\s]*[\\d,\\.]+)?)/);
      if(m) out[L]=clean(m[1]);
    });
    return JSON.stringify(out);
  })()`;
}
