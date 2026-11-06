#!/usr/bin/env node
// spike — capture and diff the observable state of a UI unit, before and after one change.
//
// It measures: computed styles, element geometry, a tight crop, a node inventory, and
// interaction facts (what receives focus, where the ring is drawn, whether Tab reaches it).
// It reports arithmetic: identical / changed / not-comparable, with before->after values.
//
// It refuses to: build the app, serve your bundle, decide whether a difference is acceptable,
// or classify drift into a category. The exit code says whether the measurement ran. It never
// says whether the change is good. That asymmetry is the whole design: a script that printed
// "PASS" would be a script whose judgment nobody reviews.

import { mkdirSync, readFileSync, writeFileSync, readdirSync, existsSync, statSync } from "node:fs";
import path from "node:path";

const VERSION = "1.0";

const USAGE = `spike ${VERSION} — measure a unit in each of its states, before and after

  node scripts/spike.mjs capture <run-dir> --spec <spec.json> --base <url> [options]
  node scripts/spike.mjs diff <before-dir> <after-dir> [options]
  node scripts/spike.mjs help

capture
  --spec <file>      The state list: routes, locators, properties, interactions.
                     See assets/spec.example.json. Nothing is hardcoded here on purpose: a
                     spike that knows your component names in advance is a spike that only
                     measures what its author remembered.
  --base <url>       Where the bundle is already being served. REQUIRED: this script never
                     starts or binds a server. Give the exact URL the app is mounted at: a
                     route in the spec starting with "/" replaces any path prefix in --base.
  --cdp <url>        Attach to a browser you already started (recommended). Otherwise the
                     script launches one, which allocates an ephemeral internal debugging port;
                     if your environment forbids that, start the browser and pass --cdp.
  --browser-channel <name>  Passed to the launcher when --cdp is absent (default: the launcher's own)
  --only <stateId>   Capture one state only; repeatable.
  --keep-open        Debugging aid: leave the browser connected until Enter is pressed.
  --json             Print the summary as JSON.

diff
  <before-dir> <after-dir>   Two capture run directories.
  --ignore <a,b>     Properties to exclude from the drift list (a known-noisy property is
                     excluded by *name*, by you; the script never decides what is noise).
  --attention <a,b>  Names to group separately in the output (focus and role properties
                     usually). Grouping is not judging: it is ordering the print.

  Exit codes, for BOTH commands: 0 the measurement ran (drift may be empty, large, or absent);
  1 the measurement did not run properly (a directory is missing, no state was comparable, a
  capture errored); 2 bad input. The exit code never encodes an opinion about the change.

What this script refuses to do
  - build or serve the app, or bind a server port;
  - decide whether a difference matters, or call a run pass/fail/worth-it;
  - categorise drift (cosmetic vs structural vs behavioural) - that is prose, and prose is
    written by the person who has to live with the verdict;
  - invent a state you did not ask for, or silently skip one it could not reach: an unreachable
    state is reported as an error and makes the run exit 1.
`;

// ------------------------------------------------------------------ tiny arg parser

function parseArgs(argv) {
  const pos = [];
  const flags = {};
  const set = (key, value) => {
    if (key in flags) flags[key] = ([]).concat(flags[key], value);
    else flags[key] = value;
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--help" || a === "-h") flags.help = true;
    else if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next !== undefined && !next.startsWith("--")) {
        set(key, next);
        i++;
      } else set(key, true);
    } else pos.push(a);
  }
  return { pos, flags };
}

function many(flags, name) {
  const raw = flags[name];
  if (raw === undefined) return [];
  return ([]).concat(raw)
    .flatMap((v) => String(v).split(","))
    .map((s) => s.trim())
    .filter((s) => s && s !== "true" && s !== "false"); // a bare --ignore with no value is empty, not "true"
}

function fail2(message) {
  process.stderr.write(`spike: ${message}\n`);
  process.exit(2);
}

// ------------------------------------------------------------------ capture

async function loadChromium(flags) {
  for (const name of ["playwright", "playwright-core"]) {
    try {
      const mod = await import(name);
      return mod.chromium ?? mod.default?.chromium;
    } catch {
      /* try the next package name */
    }
  }
  fail2(
    "no browser driver found. Install the project's own Playwright (or pass a CDP endpoint with " +
      "--cdp and a driver that speaks it). This script will not vendor a browser of its own.",
  );
}

function readSpec(file) {
  if (!existsSync(file)) fail2(`spec not found: ${file}`);
  let spec;
  try {
    spec = JSON.parse(readFileSync(file, "utf8"));
  } catch (e) {
    fail2(`spec is not valid JSON (${file}): ${e.message}`);
  }
  if (!Array.isArray(spec.states) || spec.states.length === 0) fail2(`spec has no states: ${file}`);
  return spec;
}

function buildUrl(base, state) {
  const url = new URL(state.route ?? "/", base.endsWith("/") ? base : `${base}/`);
  for (const [k, v] of Object.entries(state.query ?? {})) url.searchParams.set(k, String(v));
  return url.toString();
}

const DEFAULT_STYLES = [
  "display", "position", "width", "height", "padding", "margin", "gap", "flex-direction",
  "justify-content", "align-items", "color", "background-color", "border-radius", "box-shadow",
  "font-size", "font-weight", "line-height", "visibility", "opacity", "overflow",
  "outline-width", "outline-style", "outline-color",
];

async function capture(runDir, flags) {
  const spec = readSpec(flags.spec ?? fail2("capture needs --spec <file>"));
  const base = flags.base ?? fail2("capture needs --base <url>: the caller serves the bundle, never this script");
  const only = many(flags, "only");
  const defaults = spec.defaults ?? {};
  const styles = defaults.styles ?? DEFAULT_STYLES;
  const waitMs = defaults.timeoutMs ?? 15000;

  mkdirSync(path.join(runDir, "states"), { recursive: true });

  const chromium = await loadChromium(flags);
  const browser = flags.cdp
    ? await chromium.connectOverCDP(String(flags.cdp))
    : await chromium.launch({ headless: true, channel: flags["browser-channel"] ? String(flags["browser-channel"]) : undefined });

  const context = await browser.newContext({
    viewport: spec.viewport ?? { width: 390, height: 844 },
    deviceScaleFactor: spec.deviceScaleFactor ?? 2,
    ...(spec.locale ? { locale: spec.locale } : {}),
    ...(spec.timezoneId ? { timezoneId: spec.timezoneId } : {}),
    ...(spec.geolocation ? { geolocation: spec.geolocation } : {}),
  });
  const page = await context.newPage();
  if (Array.isArray(spec.permissions)) await context.grantPermissions(spec.permissions).catch(() => {});

  const summary = [];
  for (const state of spec.states) {
    if (only.length && !only.includes(state.id)) continue;
    const record = { id: state.id, ok: false, url: buildUrl(base, state) };
    try {
      await page.goto(record.url, { waitUntil: defaults.waitUntil ?? "load", timeout: waitMs });
      const settle = state.waitFor ?? defaults.waitFor ?? null;
      if (settle) await page.waitForSelector(settle, { timeout: waitMs });
      if (defaults.awaitFonts !== false) await page.evaluate(() => document.fonts.ready);
      if (state.settleMs ?? defaults.settleMs) await page.waitForTimeout(state.settleMs ?? defaults.settleMs);

      for (const step of state.interactions ?? []) {
        const target = step.target ?? state.locator;
        switch (step.action) {
          case "click": await page.click(target, { timeout: waitMs }); break;
          case "fill": await page.fill(target, String(step.value ?? ""), { timeout: waitMs }); break;
          case "focus": await page.focus(target, { timeout: waitMs }); break;
          case "press": await page.keyboard.press(String(step.key ?? "Tab")); break;
          case "hover": await page.hover(target, { timeout: waitMs }); break;
          case "wait": await page.waitForTimeout(step.ms ?? 250); break;
          default: throw new Error(`unknown interaction action: ${step.action}`);
        }
        if (step.afterWaitMs) await page.waitForTimeout(step.afterWaitMs);
      }

      const loc = page.locator(state.locator).first();
      const box = await loc.boundingBox();
      record.rect = box;

      const props = state.styles ?? styles;
      record.styles = await loc.evaluate((el, names) => {
        const cs = getComputedStyle(el);
        const out = {};
        for (const n of names) out[n] = cs.getPropertyValue(n);
        return out;
      }, props);

      record.nodes = await loc.evaluate((el, maxDepth) => {
        const tally = {};
        let total = 0;
        const walk = (node, depth) => {
          for (const child of node.children) {
            total++;
            const key = depth <= maxDepth ? child.tagName.toLowerCase() : `depth>${maxDepth}`;
            tally[key] = (tally[key] ?? 0) + 1;
            walk(child, depth + 1);
          }
        };
        walk(el, 1);
        return { directChildCount: el.children.length, totalDescendants: total, tagTally: tally };
      }, state.nodeDepth ?? defaults.nodeDepth ?? 3);

      record.identity = await loc.evaluate((el) => ({
        role: el.getAttribute("role"),
        ariaLabel: el.getAttribute("aria-label"),
        ariaLabelledby: el.getAttribute("aria-labelledby"),
        textSample: (el.textContent ?? "").trim().slice(0, 80),
        tabindex: el.getAttribute("tabindex"),
        disabled: el.hasAttribute("disabled"),
        hidden: el.getAttribute("aria-hidden"),
      }));

      if (state.focusProbe ?? defaults.focusProbe) {
        const sel = typeof state.focusProbe === "string" ? state.focusProbe : state.locator;
        const describeFocus = () =>
          page.evaluate((unitSel) => {
            const el = document.activeElement;
            const unit = document.querySelector(unitSel);
            if (!el || el === document.body) return { tag: el ? "body" : "null", insideUnit: false, depth: -1, outline: null };
            const cs = getComputedStyle(el);
            let depth = 0;
            let n = el;
            while (n && n !== unit) {
              n = n.parentElement;
              depth++;
            }
            return {
              tag: el.tagName.toLowerCase(),
              insideUnit: unit ? unit.contains(el) : false,
              depth: n ? depth : -1,
              outline: { width: cs.outlineWidth, style: cs.outlineStyle, color: cs.outlineColor, shadow: cs.boxShadow },
            };
          }, state.locator);

        await page.focus(sel);
        const afterFocus = await describeFocus();
        const tabs = [];
        for (let i = 0; i < (state.tabProbe ?? defaults.tabProbe ?? 0); i++) {
          await page.keyboard.press("Tab");
          tabs.push(await describeFocus());
        }
        record.focusProbe = { afterFocus, tabs };
      }

      record.crop = `states/${state.id}.png`;
      await loc.screenshot({ path: path.join(runDir, record.crop) }).catch(async (e) => {
        record.cropError = String(e.message ?? e);
        await page.screenshot({ path: path.join(runDir, record.crop) }); // whole page, and it is recorded
      });

      record.ok = true;
    } catch (e) {
      record.error = String(e?.message ?? e);
    }
    summary.push({ id: state.id, ok: record.ok, error: record.error ?? null });
    writeFileSync(path.join(runDir, "states", `${state.id}.json`), JSON.stringify(record, null, 2));
  }

  if (flags["keep-open"]) {
    process.stdout.write("browser still attached; press Enter to close.\n");
    await new Promise((resolve) => process.stdin.once("data", resolve));
  }
  await browser.close();

  const captured = summary.filter((s) => s.ok).length;
  const manifest = {
    tool: `spike ${VERSION}`,
    mode: "capture",
    spec: flags.spec,
    base,
    capturedAt: new Date().toISOString(),
    statesRequested: summary.length,
    statesCaptured: captured,
    statesFailed: summary.length - captured,
    viewport: spec.viewport ?? { width: 390, height: 844 },
    note: "No verdict is contained in this file. It is arithmetic waiting for a reader.",
    summary,
  };
  writeFileSync(path.join(runDir, "manifest.json"), JSON.stringify(manifest, null, 2));

  const line = `captured ${captured}/${summary.length} states into ${runDir}`;
  if (flags.json) process.stdout.write(JSON.stringify(manifest, null, 2) + "\n");
  else process.stdout.write(`${line}\n${summary.map((s) => `  ${s.ok ? "ok  " : "FAIL"} ${s.id}${s.error ? `  ${s.error}` : ""}`).join("\n")}\n`);
  // A zero-offender run is not proof anything was measured: fail if any state was unreachable.
  process.exit(captured === summary.length && captured > 0 ? 0 : 1);
}

// ------------------------------------------------------------------ diff

function loadRun(dir) {
  if (!existsSync(dir) || !statSync(dir).isDirectory()) fail2(`run directory missing: ${dir}`);
  const stateDir = path.join(dir, "states");
  if (!existsSync(stateDir)) fail2(`no states/ inside ${dir} — was this ever a capture run?`);
  const out = {};
  for (const f of readdirSync(stateDir).filter((n) => n.endsWith(".json"))) {
    const rec = JSON.parse(readFileSync(path.join(stateDir, f), "utf8"));
    out[rec.id] = rec;
  }
  return out;
}

const bytesEqual = (a, b) => a.length === b.length && a.equals(b);

function diff(beforeDir, afterDir, flags) {
  const A = loadRun(beforeDir);
  const B = loadRun(afterDir);
  const ignore = new Set(many(flags, "ignore"));
  const attention = new Set(many(flags, "attention"));
  const ids = [...new Set([...Object.keys(A), ...Object.keys(B)])].sort();

  const reports = ids.map((id) => {
    const a = A[id];
    const b = B[id];
    if (!a || !b) return { id, comparable: false, reason: "state exists on one side only", missingFrom: !a ? beforeDir : afterDir };
    // A state that failed to capture is NOT a state with no drift. Comparing two empty records would
    // print "no drift detected" for exactly the rows the run could not reach, so it is refused here.
    if (a.ok !== true || b.ok !== true) {
      return {
        id,
        comparable: false,
        reason: "capture failed on one or both sides",
        failedOn: [a.ok !== true ? beforeDir : null, b.ok !== true ? afterDir : null].filter(Boolean),
        errors: { before: a.error ?? "(no error recorded, ok flag not true)", after: b.error ?? "(no error recorded, ok flag not true)" },
      };
    }
    const styleDrift = [];
    const keys = [...new Set([...Object.keys(a.styles ?? {}), ...Object.keys(b.styles ?? {})])];
    for (const k of keys.sort()) {
      if (ignore.has(k)) continue;
      if ((a.styles?.[k] ?? null) !== (b.styles?.[k] ?? null)) {
        styleDrift.push({ prop: k, before: a.styles?.[k] ?? null, after: b.styles?.[k] ?? null, attention: attention.has(k) });
      }
    }
    const rect = JSON.stringify(a.rect ?? null) === JSON.stringify(b.rect ?? null) ? null : { before: a.rect ?? null, after: b.rect ?? null };
    const nodeDrift = JSON.stringify(a.nodes) === JSON.stringify(b.nodes) ? null : { before: a.nodes, after: b.nodes };
    const identityDrift = JSON.stringify(a.identity) === JSON.stringify(b.identity) ? null : { before: a.identity, after: b.identity };
    const focusDrift =
      JSON.stringify(a.focusProbe ?? null) === JSON.stringify(b.focusProbe ?? null) ? null : { before: a.focusProbe ?? null, after: b.focusProbe ?? null };
    let crop = null;
    if (a.crop && b.crop) {
      const pa = path.join(beforeDir, a.crop);
      const pb = path.join(afterDir, b.crop);
      if (existsSync(pa) && existsSync(pb)) {
        const ba = readFileSync(pa);
        const bb = readFileSync(pb);
        crop = { identical: bytesEqual(ba, bb), bytesBefore: ba.length, bytesAfter: bb.length };
      } else crop = { identical: null, note: "a crop file is missing on one side" };
    }
    return { id, comparable: true, styleDrift, rect, nodeDrift, identityDrift, focusDrift, crop };
  });

  const comparable = reports.filter((r) => r.comparable);
  const notComparable = reports.length - comparable.length;
  // The measurement either ran on everything it was asked about, or it did not: partial coverage is
  // reported as a failure to run, never as an empty drift list.
  const ranCleanly = comparable.length > 0 && notComparable === 0;
  const totalStyleDrift = comparable.reduce((n, r) => n + r.styleDrift.length, 0);
  const structural = comparable.filter((r) => r.nodeDrift || r.rect).length;
  const behavioural = comparable.filter((r) => r.focusDrift || r.identityDrift).length;

  if (flags.json) {
    process.stdout.write(
      JSON.stringify(
        {
          tool: `spike ${VERSION}`, mode: "diff", before: beforeDir, after: afterDir,
          statesCompared: comparable.length, statesNotComparable: notComparable,
          totalStyleDrift, statesWithStructuralChange: structural, statesWithBehaviouralChange: behavioural,
          ignore: [...ignore], attention: [...attention], reports,
          note: "This file contains no verdict. 'Structural' and 'behavioural' label WHICH SENSOR moved, not whether it matters. The exit code says whether the measurement ran, never whether the change is acceptable.",
        },
        null, 2,
      ) + "\n",
    );
    return ranCleanly ? 0 : 1;
  }

  process.stdout.write(
    `spike ${VERSION} diff — ${comparable.length} states compared, ${notComparable} not comparable\n` +
      `style properties changed: ${totalStyleDrift} | states with node/geometry change: ${structural} | ` +
      `states with focus/identity change: ${behavioural}\n` +
      (ignore.size ? `ignored properties: ${[...ignore].join(", ")}\n` : "") +
      `crop note: identical bytes means identical pixels; differing bytes says nothing about magnitude.\n\n`,
  );
  for (const r of reports) {
    if (!r.comparable) {
      process.stdout.write(`  ${r.id}: NOT COMPARABLE — ${r.reason}${r.failedOn ? ` (${r.failedOn.join(", ")})` : ""}\n`);
      if (r.errors) {
        if (r.errors.before && r.errors.before !== "(no error recorded, ok flag not true)") process.stdout.write(`      before: ${r.errors.before}\n`);
        if (r.errors.after && r.errors.after !== "(no error recorded, ok flag not true)") process.stdout.write(`      after:  ${r.errors.after}\n`);
      }
      continue;
    }
    const bits = [];
    if (r.styleDrift.length) bits.push(`${r.styleDrift.length} style`);
    if (r.rect) bits.push("geometry");
    if (r.nodeDrift) bits.push("node inventory");
    if (r.identityDrift) bits.push("identity/accessible name");
    if (r.focusDrift) bits.push("focus path");
    if (r.crop && r.crop.identical === false) bits.push("crop bytes");
    process.stdout.write(`  ${r.id}: ${bits.length ? bits.join(", ") : "no drift detected by any sensor"}\n`);
    for (const d of r.styleDrift) {
      process.stdout.write(`      ${d.attention ? "* " : "  "}${d.prop}: ${JSON.stringify(d.before)} -> ${JSON.stringify(d.after)}\n`);
    }
    if (r.nodeDrift) process.stdout.write(`      nodes: ${JSON.stringify(r.nodeDrift.before)} -> ${JSON.stringify(r.nodeDrift.after)}\n`);
    if (r.focusDrift) process.stdout.write(`      focus: ${JSON.stringify(r.focusDrift.before)} -> ${JSON.stringify(r.focusDrift.after)}\n`);
    if (r.identityDrift) process.stdout.write(`      identity: ${JSON.stringify(r.identityDrift.before)} -> ${JSON.stringify(r.identityDrift.after)}\n`);
  }
  process.stdout.write(
    `\n(* marks a property you listed in --attention; it does not rank it.)\n` +
      (ranCleanly
        ? `All ${comparable.length} requested states were captured on both sides and compared.\n`
        : `THE MEASUREMENT IS INCOMPLETE: ${notComparable} state(s) were not comparable, so "no drift" above is not evidence about them.\n`),
  );
  return ranCleanly ? 0 : 1;
}

// ------------------------------------------------------------------ entry

async function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0];
  if (!cmd || cmd === "help" || (cmd.startsWith("--") && cmd !== "--help")) {
    process.stdout.write(USAGE);
    return cmd && cmd !== "help" ? 2 : 0;
  }
  if (cmd === "--help" || cmd === "-h") {
    process.stdout.write(USAGE);
    return 0;
  }
  const { pos, flags } = parseArgs(argv.slice(1));
  if (flags.help) {
    process.stdout.write(USAGE);
    return 0;
  }
  if (cmd === "capture") {
    if (!pos[0]) fail2("capture needs a run directory");
    await capture(pos[0], flags); // capture() sets its own exit code
  }
  if (cmd === "diff") {
    if (pos.length < 2) fail2("diff needs two run directories: <before> <after>");
    return diff(pos[0], pos[1], flags);
  }
  fail2(`unknown command: ${cmd} (capture | diff | help)`);
}

main().then((code) => process.exit(code ?? 0)).catch((e) => {
  process.stderr.write(`spike: ${e?.stack ?? e}\n`);
  process.exit(1);
});
