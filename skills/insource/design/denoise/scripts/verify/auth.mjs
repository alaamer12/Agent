#!/usr/bin/env node
/**
 * auth.mjs — get an authenticated session for a running app, and prove you have one.
 *
 * Part of the `accessible` skill's verification scripts. No npm dependencies; Node >= 22.
 *
 *   node auth.mjs --discover [--root .]                       # where might the creds be?
 *   node auth.mjs --login http://localhost:5173/login \
 *        --email-env ADMIN_EMAIL --password-env ADMIN_PASSWORD \
 *        --state session.json
 *   node auth.mjs --probe http://localhost:5173 --state session.json
 *
 * Credentials are looked for in this order, and the order is the point:
 *
 *   1. Given to you now, on the command line or in the environment.
 *   2. The person running the pass. Ask them — they usually have a dev account, and asking
 *      is one sentence. This is the default when (1) finds nothing.
 *   3. Already in the project: seed files, fixtures, .env, docs. --discover locates
 *      candidates and prints only file:line, never the value, so nothing secret lands in a
 *      transcript while you look.
 *   4. Creating a throwaway test user. This writes to someone's database. It is the last
 *      option, it needs explicit permission, and --create-cmd exists so the command that
 *      does it is one the person can see and approve before it runs.
 *
 * Never write a credential into a tracked file. Pass it through the environment.
 */
import { readFileSync, writeFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { openSession, sleep, findChrome } from './browser.mjs';

const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf(`--${n}`); return i === -1 ? d : argv[i + 1]; };
const has = (n) => argv.includes(`--${n}`);

/* ------------------------------------------------------------ --discover */

if (has('discover')) {
  const root = path.resolve(flag('root', '.'));
  const SKIP = new Set(['node_modules', '.git', 'dist', 'build', '.next', '.nuxt', 'coverage', '.venv', 'target']);
  const NAME = /(^|[/\\.])(\.env[^/\\]*|seed|seeds?\.|fixture|conftest|factory|factories|test[-_]user|users\.(sql|rb|py|ts|js)|db\.(sql|rb)|README[^/\\]*)$/i;
  const HINT = /(passw|secret|admin|credential|login|email|user_name|apikey|api_key)/i;
  const hits = [];
  const walk = (dir, depth) => {
    if (depth > 6 || hits.length > 40) return;
    let entries = [];
    try { entries = readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (e.name.startsWith('.') && !/^\.env/.test(e.name)) continue;
      if (SKIP.has(e.name)) continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) { walk(p, depth + 1); continue; }
      if (!NAME.test(p)) continue;
      let text = '';
      try { text = readFileSync(p, 'utf8'); } catch { continue; }
      text.split('\n').forEach((line, i) => {
        if (!HINT.test(line)) return;
        // Report where to look, not what is there.
        hits.push(`${path.relative(root, p)}:${i + 1}  ${line.replace(/[^\x20-\x7e]/g, '').slice(0, 60).replace(/=\s*\S+/, '= <redacted>')}`);
      });
    }
  };
  walk(root, 0);
  console.log(`${hits.length} candidate locations under ${root} — values are redacted on purpose:\n`);
  hits.slice(0, 40).forEach((h) => console.log('  ' + h));
  console.log(`
Read the files you need. If none of them is a usable dev login, ASK THE PERSON — do not
guess a password, and do not create a user in their database without saying so first.`);
  process.exit(0);
}

/* ------------------------------------------------------- login and probe */

const base = flag('base', flag('login', flag('probe', null)));
if (!base) {
  console.error('usage: node auth.mjs --login <url> [--email-env V --password-env V] [--state session.json]\n       node auth.mjs --probe <url> --state session.json\n       node auth.mjs --discover [--root .]');
  process.exit(2);
}
const email = process.env[flag('email-env', 'A11Y_EMAIL')] ?? flag('email', null);
const password = process.env[flag('password-env', 'A11Y_PASSWORD')] ?? flag('password', null);
const statePath = flag('state', null);
const loginPath = flag('login-path', 'login');
const submitRe = flag('submit', 'sign in|log in|login|continue|submit');
const chrome = flag('chrome', null);

/**
 * A framework binds its model to the *input* event, so assigning .value is invisible to it
 * and the form submits empty — which reads like "the login is broken" when the harness is
 * the thing that never typed anything. Use the prototype setter, then dispatch like a key.
 */
async function fill(s, index, value) {
  return s.evl(`(function(){
    var el=document.querySelectorAll('input')[${index}];
    if(!el) return 'no input at ${index}';
    var d=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value');
    d.set.call(el, ${JSON.stringify(String(value))});
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
    return 'ok';
  })()`);
}

const s = await openSession({ chrome, startUrl: base });

if (has('probe')) {
  await sleep(2500);
  if (statePath && existsSync(statePath)) {
    const st = JSON.parse(readFileSync(statePath, 'utf8'));
    await s.send('Network.enable');
    if (st.cookies?.length) await s.send('Network.setCookies', { cookies: st.cookies.map((c) => ({ ...c, sameSite: c.sameSite || 'Unset' })) });
    if (st.origin) await s.goto(st.origin);
    if (st.localStorage) await s.evl(`(function(){try{Object.entries(${JSON.stringify(st.localStorage)}).forEach(function(e){localStorage.setItem(e[0],e[1])})}catch(x){}})()`);
  }
  await s.goto(base);
  const snap = await s.settle({ timeoutMs: 12000 });
  const url = snap?.url || '(no answer)';
  const ok = !url.includes(loginPath);
  console.log(`  ${ok ? '\x1b[32mlogged in\x1b[0m' : '\x1b[31mnot authenticated\x1b[0m'} — ${url}`);
  console.log(ok ? '  Proceed with the sweep.' : `  Stop and get a session first:
    1. ask the person for a dev account, or
    2. node auth.mjs --discover --root .   (find one in the project), or
    3. create a throwaway test user — but only after saying so out loud.`);
  s.close();
  process.exit(ok ? 0 : 1);
}

if (!email || !password) {
  console.error(`No credential in the environment.
  Look for one in the project:  node auth.mjs --discover --root .
  Or ask the person running this pass for a dev login — that is a one-sentence question,
  and guessing or fabricating one is not an option.`);
  process.exit(2);
}

await s.goto(base);
let inputs = 0;
for (let i = 0; i < 40; i++) {
  inputs = Number(await s.evl(`document.querySelectorAll('input').length`, 0));
  if (inputs >= 2) break;
  await sleep(1000);
}
if (inputs < 2) {
  console.error(`  \x1b[31monly ${inputs} input(s) at ${base} — that is not a login form.\x1b[0m
  Point --login at the actual sign-in URL, or check the dev server is serving the app and
  not an error page (curl the URL and look at it).`);
  s.close();
  process.exit(3);
}
console.log(`  fill: ${await fill(s, 0, email)} / ${await fill(s, 1, password)}`);
await sleep(400);
const clicked = await s.evl(`(function(){
  var b=[].slice.call(document.querySelectorAll('button,[role=button],input[type=submit]'))
    .find(function(x){return new RegExp(${JSON.stringify(submitRe)},'i').test(x.innerText||x.value||'')});
  if(!b) return 'no submit control'; b.click(); return 'clicked ' + (b.innerText||b.value).trim();
})()`);
console.log(`  submit: ${clicked}`);

let snap = null;
for (let i = 0; i < 20; i++) {
  snap = await s.settle({ timeoutMs: 4000 });
  if (snap && !String(snap.url).includes(loginPath)) break;
  await sleep(1000);
}
const url = snap?.url || '(no answer)';
if (String(url).includes(loginPath)) {
  console.error(`  \x1b[31mlogin did not take — still at ${url}\x1b[0m`);
  s.events().filter((e) => e.kind === 'error').slice(0, 5).forEach((e) => console.error('     ' + e.text.slice(0, 140)));
  console.error(`  Do not conclude the app is broken. Check, in order: the credential; whether the
  backend is running at all; whether the browser origin is allowed by the API's CORS
  allowlist (a disallowed origin shows a login that fails with no useful error); whether
  the form needs something other than the first two inputs.`);
  s.close();
  process.exit(4);
}

await s.send('Network.enable');
const { cookies = [] } = await s.send('Network.getCookies', { urls: [url] }).catch(() => ({ cookies: [] }));
const storage = await s.evl(`(function(){try{return JSON.stringify(Object.assign({},localStorage))}catch(x){return '{}'}})()`);
if (statePath) {
  writeFileSync(statePath, JSON.stringify({ origin: url, at: new Date().toISOString(), cookies, localStorage: JSON.parse(storage || '{}') }, null, 2));
  console.log(`  \x1b[32m✓ authenticated at ${url}\x1b[0m — session written to ${statePath}`);
} else {
  console.log(`  \x1b[32m✓ authenticated at ${url}\x1b[0m (no --state given, so the session lives only in this process)`);
}
s.close();
