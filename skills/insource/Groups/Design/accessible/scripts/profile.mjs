#!/usr/bin/env node
/**
 * profile.mjs — loads a stack profile and compiles its regexes.
 *
 * Shared by mode-audit.mjs and rollout/map.mjs so the stack assumptions live in exactly one
 * place: the JSON in assets/stack-profiles/, not in the code.
 *
 * The important behaviour is `measure()`. A disabled knob returns `null`, and callers must
 * render that as "not measured" rather than 0. A Tailwind palette regex run against a Sass
 * project returns zero matches, which reads as "no raw colours — the pass is clean" and is a
 * lie. Confusing absence with a zero is the single most common way a check certifies something
 * it never looked at.
 */
import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PROFILE_DIR = path.resolve(HERE, '../assets/stack-profiles');

const deepMerge = (a, b) => {
  const out = { ...a };
  for (const [k, v] of Object.entries(b ?? {})) {
    if (k === '$comment' || k === '$commentNote') continue;
    out[k] = v && typeof v === 'object' && !Array.isArray(v) ? deepMerge(a[k] ?? {}, v) : v;
  }
  return out;
};

/** `--profile vue-tailwind`, a path, or nothing for the neutral base. */
export function loadProfile(spec) {
  if (!spec) spec = 'base';
  const base = JSON.parse(readFileSync(path.join(PROFILE_DIR, 'base.json'), 'utf8'));
  if (spec === 'base') return { profile: base, source: 'base (neutral defaults)' };
  const direct = existsSync(path.resolve(spec)) ? path.resolve(spec) : path.join(PROFILE_DIR, spec.endsWith('.json') ? spec : `${spec}.json`);
  if (!existsSync(direct)) {
    const known = existsSync(PROFILE_DIR) ? readFileSync : null;
    throw new Error(`no stack profile "${spec}". Shipped: base, vue-tailwind, react-tailwind, plain-css — or pass a path to your own. Deriving one takes a few greps; see references/stack-profiles.md.`);
  }
  const merged = deepMerge(base, JSON.parse(readFileSync(direct, 'utf8')));
  return { profile: merged, source: path.basename(direct, '.json') };
}

/**
 * Compiled view. `rx()` returns null for a disabled knob; `measurable()` tells the caller
 * whether to report a number at all.
 */
export function compile(profile) {
  const cache = new Map();
  const rx = (source, flags = 'g') => {
    if (!source) return null;
    const key = source + '|' + flags;
    if (!cache.has(key)) cache.set(key, new RegExp(source, flags));
    return cache.get(key);
  };
  const count = (text, source, flags = 'g') => {
    const re = rx(source, flags);
    if (!re) return null;                       // null = not measured, NOT 0
    return (text.match(new RegExp(re.source, flags)) || []).length;
  };
  const set = (text, source, group = 1, flags = 'gm') => {
    const re = rx(source, flags);
    if (!re) return null;
    return new Set([...text.matchAll(new RegExp(re.source, flags))].map((m) => (m[group] ?? '').replace(/\/$/, '')).filter(Boolean));
  };

  const c = profile.colour ?? {};
  const e = profile.elevation ?? {};
  const r = profile.routes ?? {};
  const ix = profile.interaction ?? {};

  return {
    profile,
    exts: profile.exts ?? [],
    skipDirs: new Set(profile.skipDirs ?? []),
    snapshotDirRx: rx(profile.snapshotDirPattern, 'i'),
    configFilesRx: rx(r.configFilePattern, 'i'),
    logicStyle: profile.logicBlock?.style ?? 'auto',
    localPrefixes: profile.components?.localPrefixes ?? [],

    /** Every colour measure reports whether it ran, so the caller can say "not measured". */
    colours(text) {
      const utility = count(text, c.utilityClasses);
      const literal = count(text, c.inlineLiterals);
      return {
        utility, literal,
        total: utility === null ? literal : (literal === null ? utility : utility + literal),
        measured: utility !== null || literal !== null,
        note: utility === null ? 'no utility-class rule in this profile' : '',
      };
    },
    tokens(text) { return count(text, c.tokenDefinitions); },
    rampMin: () => c.rampMinTokens ?? 12,
    rampFactor: () => c.rampGrowthFactor ?? 1.5,

    elevation(text) {
      const defs = set(text, e.tokenPattern, 1);
      const used = count(text, e.usagePattern);
      if (!defs) return { steps: null, consumed: null, measured: false };
      const scale = [...defs].filter((n) => /elev|shadow|depth/i.test(n));
      return { steps: new Set(scale).size, consumed: used ?? 0, measured: true,
        radiusSteps: new Set([...defs].filter((n) => /radius/i.test(n))).size };
    },

    routes(text) {
      const stripped = r.redirectStubPattern ? text.replace(new RegExp(r.redirectStubPattern, 'g'), '') : text;
      const found = set(stripped, r.declarationPattern, 1);
      return found ? { paths: found, measured: true } : { paths: new Set(), measured: false };
    },

    /**
     * The writing surfaces — forms, dialogs, pickers, wizards: where a user *does* something
     * rather than reads something. A signature is the ordered list of controls with their
     * identity attributes, so repainting a dialog leaves it untouched and re-sequencing the
     * dialog moves it. Without that distinction, "every modal got new colours" and "the modals
     * were designed" both look like styling work and grade identically.
     */
    interaction: {
      enabled: Boolean(ix.surfacePattern && ix.controlPattern),
      isSurface(text) {
        if (!ix.surfacePattern) return null;
        return new RegExp(ix.surfacePattern).test(text);
      },
      signature(text) {
        if (!ix.controlPattern) return null;
        const idr = ix.identityAttrPattern ? new RegExp(ix.identityAttrPattern, 'g') : null;
        const out = [];
        for (const m of text.matchAll(new RegExp(ix.controlPattern, 'g'))) {
          const tag = (m[1] || '').toLowerCase();
          const attrs = m[2] || '';
          const ids = idr ? [...new Set([...attrs.matchAll(idr)].map((x) => x[1]))].sort() : [];
          out.push(tag + (ids.length ? `[${ids.join(',')}]` : ''));
        }
        return out;
      },
      listTop: ix.listTop ?? 8,
    },

    patternCount(text, group, flags = 'g') {
      const pats = profile[group]?.patterns ?? [];
      if (!pats.length) return null;
      return pats.reduce((n, p) => n + (count(text, p, flags) ?? 0), 0);
    },
  };
}
