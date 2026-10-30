#!/usr/bin/env node
/**
 * EAS Build archive audit.
 *
 * Reproduces, without uploading anything, the file set `eas build` packs:
 *   - with a root .easignore: EAS uses ONLY that file (plus .git/node_modules)
 *   - without one: EAS uses the .gitignore stack, including nested files
 *
 * Usage:  node eas-archive-audit.mjs [--top N]
 */
import { execFileSync } from 'node:child_process';
import { existsSync, statSync } from 'node:fs';
import { join, resolve } from 'node:path';

const TOP = (() => {
  const i = process.argv.indexOf('--top');
  return i > -1 ? Number(process.argv[i + 1]) || 15 : 15;
})();

const git = (args) => {
  try {
    return execFileSync('git', args, { encoding: 'utf8', maxBuffer: 1 << 28 })
      .split('\0')
      .filter(Boolean);
  } catch {
    return [];
  }
};

const root = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim();
process.chdir(root);

if (!existsSync(join(root, '.git'))) {
  console.log('not a git repository — EAS falls back to a plain filesystem copy here.');
}

const hasEasignore = existsSync(join(root, '.easignore'));

// EAS always excludes these two, ignore file or not.
const ALWAYS = /(^|\/)(node_modules|\.git)(\/|$)/;
const tracked = git(['ls-files', '-z']);
const untracked = hasEasignore
  ? git(['ls-files', '-z', '-o', '--exclude-from=.easignore'])
  : git(['ls-files', '-z', '-o', '--exclude-standard']);

// Clone brings in every tracked file; EAS then deletes the ones its rules match.
const dropped = hasEasignore
  ? new Set(git(['ls-files', '-z', '--exclude-from=.easignore', '--ignored', '--cached']))
  : new Set();

const files = [...new Set([...tracked, ...untracked])].filter((p) => !ALWAYS.test(p) && !dropped.has(p));

const SOURCE = /\.(ts|tsx|js|jsx|mjs|cjs|md|snap|test\.[jt]sx?)$/i;
const SECRET_FILE = /\.(env|p8|pem|key|jks|keystore|p12|mobileprovision|cer|der)$/i;
const SECRET_NAME = /(^|\/)(\.env[^/]*$|.*service[-_]account.*\.json$|secrets\/)/;
// Firebase/Google client config is NOT a secret and prebuild needs it in the archive.
const CLIENT_CONFIG = /(^|\/)(google-services\.json|GoogleService-Info\.plist)$/;
const NATIVE = [/(^|\/)android\//i, /(^|\/)ios\//i, /gradle-wrapper\.properties$/i, /\.xcworkspace\//i, /Podfile\.lock$/i];
const BUILD = [/(^|\/)(dist|build|out|coverage)\//i, /(^|\/)\.(next|expo|turbo|cache|tamagui|nyc_output|pw)\//i, /\.tsbuildinfo$/i];

let total = 0;
const byDir = new Map();
const big = [];
for (const f of files) {
  try {
    const size = statSync(join(root, f)).size;
    total += size;
    const parts = f.split('/');
    const dir = parts.length > 2 ? `${parts[0]}/${parts[1]}` : parts.length > 1 ? `${parts[0]}/` : `<root>`;
    byDir.set(dir, (byDir.get(dir) ?? 0) + size);
    if (size > 5 << 20) big.push([size, f]);
  } catch {
    /* unreadable — skip */
  }
}

const mb = (n) => (n / 1048576).toFixed(1).padStart(7);
const hit = (res) => files.filter((f) => res.some((re) => re.test(f)));

console.log(`EAS archive audit  —  ${root}`);
console.log(`ignore source: ${hasEasignore ? '.easignore (REPLACES every .gitignore rule, nested included)' : 'no .easignore — using the .gitignore stack'}`);
console.log(`files: ${files.length}   uncompressed: ${mb(total)} MB   (EAS warns above 150 MB, rejects above 2 GB)`);

console.log('\n--- largest groups ---');
[...byDir.entries()].sort((a, b) => b[1] - a[1]).slice(0, TOP)
  .forEach(([d, s]) => console.log(`${mb(s)} MB  ${d}`));

const secrets = hit([SECRET_FILE, SECRET_NAME]).filter((f) => !SOURCE.test(f) && !CLIENT_CONFIG.test(f));
console.log(`\n--- secrets / credentials in archive: ${secrets.length} ---`);
secrets.slice(0, 12).forEach((f) => console.log(`  ${f}`));
if (secrets.length) console.log('  these reach the build service — exclude them (build-time config should come from EAS env vars / credentials instead)');

const clientConfig = hit([CLIENT_CONFIG]);
if (clientConfig.length) {
  console.log(`\n--- client config that must STAY in the archive: ${clientConfig.length} ---`);
  clientConfig.forEach((f) => console.log(`  ${f}  (referenced by app.json googleServicesFile; prebuild copies it into the native project)`));
}

const native = hit(NATIVE);
console.log(`\n--- native project files in archive: ${native.length} ---`);
native.slice(0, 10).forEach((f) => console.log(`  ${f}`));
if (native.length) console.log('  if the project uses expo prebuild/CNG these must NOT ship: a stale gradle-wrapper.properties or Podfile makes EAS skip prebuild and build with the wrong toolchain');

const build = hit(BUILD);
console.log(`\n--- generated output in archive: ${build.length} ---`);
build.slice(0, 10).forEach((f) => console.log(`  ${f}`));
if (build.length) console.log('  check package.json "exports" before excluding — safe only if nothing resolves into these dirs');

if (big.length) {
  console.log('\n--- single files over 5 MB ---');
  big.sort((a, b) => b[0] - a[0]).slice(0, 10).forEach(([s, f]) => console.log(`${mb(s)} MB  ${f}`));
}

const rules = new Set();
if (hasEasignore) {
  [...byDir.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5)
    .filter(([d]) => d !== '<root>' && !files.some((f) => /^(src|app)\//.test(f) && f.startsWith(d)))
    .forEach(([d]) => rules.add(`${d.replace(/\/$/, '')}/`));
} else {
  ['node_modules/', '.git/', 'dist/', 'build/', '.next/', '.expo/', '.turbo/', 'coverage/', '*.tsbuildinfo']
    .forEach((r) => rules.add(r));
  ['android/', 'ios/', '.env', '.env*.local', '*.p8', '*.pem', '*.jks', '*.keystore', '*.mobileprovision']
    .forEach((r) => rules.add(r));
}
console.log('\n--- suggested .easignore additions ---');
console.log([...rules].join('\n') || '(none — archive already looks lean)');
console.log('\nAfter editing, preview the deletions EAS will make from tracked files:');
console.log('  git ls-files --exclude-from=.easignore --ignored --cached');
