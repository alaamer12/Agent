#!/usr/bin/env node
// glob-liveness — prove every configured path/glob matches at least one real file.
//
// It measures one thing: does this pattern touch anything? A rule scoped to a directory
// that no longer exists prints green forever, so this exits non-zero when any pattern
// matches zero files.
//
// It refuses to: decide whether a pattern *should* be dead, edit a config, widen a glob,
// or add an allowlist entry on your behalf. Allowlisting happens in the config, by hand,
// with a reason.

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import path from "node:path";

const VERSION = "1.0";
const DEFAULT_EXCLUDES = [
  "**/node_modules/**",
  "**/.git/**",
  "**/dist/**",
  "**/build/**",
  "**/out/**",
  "**/.venv/**",
  "**/coverage/**",
];

const USAGE = `glob-liveness ${VERSION} — assert every glob matches >= 1 real file

  node scripts/glob-liveness.mjs [options] [glob ...]
  node scripts/glob-liveness.mjs --config auditor-config.example.json [options]

  Globs may also be given as positional arguments. A pattern with no wildcard character is
  checked as a plain path (file or directory).

  --config <file>     JSON config. Shapes accepted:
                        { "root": ".", "globs": ["..."], "exclude": ["..."],
                          "rules": [{ "code": "...", "globs": ["..."] }],
                          "allowEmpty": [{ "glob": "...", "reason": "..." }] }
                      Rules and allowEmpty are optional; globs and root are the same keys
                      the auditor itself reads, so this script can point at the real config.
  --root <dir>        Directory to walk (default: "." resolved against the config's root).
  --exclude <glob>    Extra exclusion, repeatable.
  --no-default-excludes
                      Do not skip the standard build/vendoring directories (audit those too).
  --json              Machine output.
  --help              This text.

  Exit codes: 0 every pattern is live; 1 a pattern matched nothing; 2 bad input
  (missing file, unreadable config, allowlist entry without a reason).

  What this script refuses to do: it never says whether a dead pattern should be deleted,
  kept, or pointed somewhere else, and it never edits the config to make itself pass.
  A dead glob is a fact; the fix is yours.
`;

// ---------------------------------------------------------------- argument parsing

function parseArgs(argv) {
  const opts = {
    patterns: [],
    config: null,
    root: null,
    extraExclude: [],
    defaultExcludes: true,
    json: false,
    help: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    switch (a) {
      case "--help":
      case "-h":
        opts.help = true;
        break;
      case "--config":
        opts.config = argv[++i];
        break;
      case "--root":
        opts.root = argv[++i];
        break;
      case "--exclude":
        opts.extraExclude.push(argv[++i]);
        break;
      case "--no-default-excludes":
        opts.defaultExcludes = false;
        break;
      case "--json":
        opts.json = true;
        break;
      default:
        if (a.startsWith("--")) fail(2, `unknown option: ${a}`);
        opts.patterns.push(a);
    }
  }
  return opts;
}

function fail(code, message) {
  process.stderr.write(`glob-liveness: ${message}\n`);
  process.exit(code);
}

// ---------------------------------------------------------------- glob compilation

function escapeRe(ch) {
  return "\\^$.|?*+(){}[]".includes(ch) ? `\\${ch}` : ch;
}

/** Compile a path glob (supports **, *, ?, {a,b}) into an anchored RegExp over POSIX paths. */
function globToRegExp(pattern) {
  let out = "";
  for (let i = 0; i < pattern.length; i++) {
    const ch = pattern[i];
    if (ch === "*") {
      const doubled = pattern[i + 1] === "*";
      if (doubled) {
        i++;
        if (pattern[i + 1] === "/") {
          i++;
          out += "(?:.*/)?"; // `**/` matches zero or more directories
        } else {
          out += ".*"; // trailing or separator-free `**`
        }
      } else {
        out += "[^/]*";
      }
      continue;
    }
    if (ch === "?") {
      out += "[^/]";
      continue;
    }
    if (ch === "{") {
      const close = pattern.indexOf("}", i);
      if (close > i) {
        const alts = pattern.slice(i + 1, close).split(",");
        out += `(?:${alts.map((s) => s.split("").map(escapeRe).join("")).join("|")})`;
        i = close;
        continue;
      }
    }
    out += escapeRe(ch);
  }
  return new RegExp(`^${out}$`);
}

function hasWildcard(p) {
  return /[*?{[]/.test(p);
}

function toPosix(p) {
  return p.split(path.sep).join("/");
}

// ---------------------------------------------------------------- tree walking

function listFiles(root, excludeRes) {
  const files = [];
  const dirs = [];
  const walk = (abs, rel) => {
    let entries;
    try {
      entries = readdirSync(abs, { withFileTypes: true });
    } catch {
      return; // unreadable directory: nothing here can match, and that is reported as 0
    }
    for (const ent of entries) {
      const childRel = rel ? `${rel}/${ent.name}` : ent.name;
      const childAbs = path.join(abs, ent.name);
      // A directory is tested with a trailing separator so `**/name/**` prunes the walk
      // instead of descending into it and filtering every file one by one.
      const probe = ent.isDirectory() ? `${childRel}/` : childRel;
      if (excludeRes.some((re) => re.test(probe))) continue;
      if (ent.isDirectory()) {
        dirs.push(childRel);
        walk(childAbs, childRel);
      } else if (ent.isFile()) {
        files.push(childRel);
      }
    }
  };
  walk(root, "");
  return { files, dirs };
}

// ---------------------------------------------------------------- reporting

function evaluate(patterns, { files, dirs }, root) {
  return patterns.map((pattern) => {
    const plain = path.posix.normalize(pattern.replace(/^\.\//, ""));
    if (!hasWildcard(pattern)) {
      const exists = files.includes(plain) || dirs.includes(plain) || existsSync(path.join(root, pattern));
      return { pattern, matches: exists ? 1 : 0, sample: exists ? plain : null };
    }
    const re = globToRegExp(pattern);
    const hits = files.filter((f) => re.test(f));
    return { pattern, matches: hits.length, sample: hits[0] ?? null };
  });
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    process.stdout.write(USAGE);
    return 0;
  }

  let cfg = {};
  if (opts.config) {
    if (!existsSync(opts.config)) fail(2, `config not found: ${opts.config}`);
    try {
      cfg = JSON.parse(readFileSync(opts.config, "utf8"));
    } catch (e) {
      fail(2, `config is not valid JSON: ${e.message}`);
    }
  }

  const root = path.resolve(opts.root ?? cfg.root ?? ".");
  if (!existsSync(root)) fail(2, `root does not exist: ${root}`);

  // Collect patterns, keeping the rule code that owns each one when the config has rules.
  const entries = [];
  for (const g of cfg.globs ?? []) entries.push({ pattern: g, code: null });
  for (const rule of cfg.rules ?? []) {
    for (const g of rule.globs ?? []) entries.push({ pattern: g, code: rule.code ?? rule.id ?? null });
  }
  for (const g of opts.patterns) entries.push({ pattern: g, code: null });
  if (entries.length === 0) fail(2, "no patterns given (positional globs or a config with globs/rules)");

  const allowEmpty = new Map();
  for (const item of cfg.allowEmpty ?? []) {
    if (typeof item === "string") fail(2, `allowEmpty entry without a reason: ${item}`);
    if (!item.reason || !String(item.reason).trim()) {
      fail(2, `allowEmpty entry without a reason: ${item.glob}`);
    }
    allowEmpty.set(item.glob, item.reason);
  }

  const excludePatterns = [
    ...(opts.defaultExcludes ? DEFAULT_EXCLUDES : []),
    ...(cfg.exclude ?? []),
    ...opts.extraExclude,
  ].filter((p) => !allowEmpty.has(p));
  const tree = listFiles(root, excludePatterns.map(globToRegExp));

  const results = evaluate(
    entries.map((e) => e.pattern),
    tree,
    root,
  ).map((r, i) => ({ ...r, code: entries[i].code, allowed: allowEmpty.has(r.pattern) }));

  const dead = results.filter((r) => r.matches === 0);
  const deadAndNotAllowed = dead.filter((r) => !r.allowed);

  if (opts.json) {
    process.stdout.write(
      JSON.stringify(
        {
          root,
          filesScanned: tree.files.length,
          exclude: excludePatterns,
          results,
          dead: deadAndNotAllowed.map((r) => r.pattern),
          ok: deadAndNotAllowed.length === 0,
        },
        null,
        2,
      ) + "\n",
    );
    return deadAndNotAllowed.length === 0 ? 0 : 1;
  }

  process.stdout.write(`glob-liveness ${VERSION} — root ${root} — ${tree.files.length} files scanned\n`);
  process.stdout.write(`excluded: ${excludePatterns.length ? excludePatterns.join(", ") : "(nothing)"}\n\n`);
  for (const r of results) {
    const flag = r.matches > 0 ? "live " : r.allowed ? "empty*" : "DEAD ";
    const owner = r.code ? ` [${r.code}]` : "";
    const note = r.matches > 0 ? ` e.g. ${r.sample}` : r.allowed ? ` allowlisted: ${r.allowed}` : "";
    process.stdout.write(`  ${flag} ${String(r.matches).padStart(5)}  ${r.pattern}${owner}${note}\n`);
  }
  process.stdout.write(
    `\n${results.length} patterns, ${results.length - dead.length} live, ${dead.length} matching nothing` +
      `${deadAndNotAllowed.length ? ` (${deadAndNotAllowed.length} not allowlisted)` : ""}.\n`,
  );
  if (deadAndNotAllowed.length) {
    process.stdout.write(
      "A pattern that matches nothing polices nothing. Either the path moved, the rule was\n" +
        "always wrong, or the config is stale — that decision is not this script's.\n",
    );
  }
  return deadAndNotAllowed.length === 0 ? 0 : 1;
}

process.exit(main());
