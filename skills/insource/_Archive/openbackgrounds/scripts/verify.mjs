import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const args = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? fallback : args[i + 1];
};

const url = flag("url", null);
const urlTemplate = flag("url-template", null);
const manifestPath = flag("manifest", null);
const selector = flag("selector", "canvas");
const duration = Number(flag("duration", "3500"));
const out = flag("out", null);
const idList = flag("ids", null);
const posterFlag = flag("poster", null);
const shotDir = flag("shot-dir", null);

if (!url && !(urlTemplate && manifestPath)) {
  console.error(
    "usage: node verify.mjs --url <page> | --manifest <manifest.json> --url-template <url with {id}>\n" +
      "       [--selector canvas] [--duration 3500] [--ids a,b] [--out report.json]",
  );
  process.exit(2);
}

let chromium;
try {
  ({ chromium } = await import("playwright"));
} catch {
  // Skill directories rarely carry node_modules; let the caller point at a
  // project that already depends on Playwright.
  const { createRequire } = await import("node:module");
  const { pathToFileURL } = await import("node:url");
  const require = createRequire(import.meta.url);
  let resolved = null;
  for (const base of [process.env.PLAYWRIGHT_DIR, process.cwd()]) {
    if (!base) continue;
    try {
      resolved = require.resolve("playwright", { paths: [base] });
      break;
    } catch {}
  }
  if (!resolved) {
    console.error(
      "verify.mjs needs Playwright: npm i -D playwright && npx playwright install chromium\n" +
        "or set PLAYWRIGHT_DIR to a folder whose node_modules contains playwright",
    );
    process.exit(2);
  }
  const mod = await import(pathToFileURL(resolved).href);
  chromium = mod.chromium ?? mod.default?.chromium;
  if (!chromium) {
    console.error("verify.mjs resolved Playwright but found no chromium export");
    process.exit(2);
  }
}

let targets;
if (url) {
  targets = [{
    id: "page",
    url,
    poster: posterFlag ? path.resolve(posterFlag) : null,
  }];
} else {
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  const keep = idList ? new Set(idList.split(",").map((s) => s.trim())) : null;
  targets = manifest.scenes
    .filter((s) => !keep || keep.has(s.id))
    .map((s) => ({
      id: s.id,
      url: urlTemplate.replace("{id}", s.id),
      poster: path.join(ROOT, s.poster),
    }));
}

const browser = await chromium.launch({
  args: [
    "--use-gl=angle",
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--ignore-gpu-blocklist",
    "--disable-dev-shm-usage",
    "--disable-gpu-sandbox",
    "--no-sandbox",
  ],
});

const context = await browser.newContext({
  viewport: { width: 640, height: 400 },
  deviceScaleFactor: 1,
  reducedMotion: "no-preference",
});

await context.addInitScript(() => {
  const raf = window.requestAnimationFrame.bind(window);
  window.__frames = 0;
  window.requestAnimationFrame = (cb) => raf((t) => {
    window.__frames += 1;
    return cb(t);
  });
});

// A live WebGL canvas cannot be sampled with drawImage once the compositor has
// swapped it, so the caller screenshots the element and this runs on the PNG.
const analyse = async (imageB64, posterB64) => {
  const imgBlob = await (await fetch(`data:image/png;base64,${imageB64}`)).blob();
  const img = await createImageBitmap(imgBlob);
  const c = document.createElement("canvas");
  c.width = 96;
  c.height = 60;
  const g = c.getContext("2d", { willReadFrequently: true });
  g.drawImage(img, 0, 0, 96, 60);
  const d = g.getImageData(0, 0, 96, 60).data;

  const luma = [];
  const buckets = new Set();
  const hues = new Array(12).fill(0);
  for (let i = 0; i < d.length; i += 4) {
    const r = d[i], gg = d[i + 1], b = d[i + 2];
    luma.push(0.2126 * r + 0.7152 * gg + 0.0722 * b);
    buckets.add((r >> 4) << 8 | (gg >> 4) << 4 | (b >> 4));
    const max = Math.max(r, gg, b), min = Math.min(r, gg, b);
    if (max > 40 && max - min > 12) {
      let hue = 0;
      if (max === r) hue = ((gg - b) / (max - min)) % 6;
      else if (max === gg) hue = (b - r) / (max - min) + 2;
      else hue = (r - gg) / (max - min) + 4;
      hues[(Math.floor(((hue + 6) % 6) / 6 * 12) + 12) % 12] += 1;
    }
  }
  const mean = luma.reduce((a, b) => a + b, 0) / luma.length;
  const variance = luma.reduce((a, b) => a + (b - mean) ** 2, 0) / luma.length;
  const signature = [];
  for (let y = 0; y < 20; y += 1) {
    for (let x = 0; x < 32; x += 1) {
      signature.push(luma[(y * 3) * 96 + x * 3]);
    }
  }
  const hueTotal = hues.reduce((a, b) => a + b, 0) || 1;
  const hueHist = hues.map((v) => v / hueTotal);

  const result = {
    variance,
    distinct: buckets.size,
    signature,
    hueHist,
    width: img.width,
    height: img.height,
  };
  if (!posterB64) return result;

  {
    const blob = await (await fetch(`data:image/jpeg;base64,${posterB64}`)).blob();
    const bmp = await createImageBitmap(blob);
    const pc = document.createElement("canvas");
    pc.width = 32;
    pc.height = 20;
    const pg = pc.getContext("2d", { willReadFrequently: true });
    pg.drawImage(bmp, 0, 0, 32, 20);
    const pd = pg.getImageData(0, 0, 32, 20).data;
    const pSig = [];
    const pHues = new Array(12).fill(0);
    for (let i = 0; i < pd.length; i += 4) {
      const r = pd[i], gg = pd[i + 1], b = pd[i + 2];
      pSig.push(0.2126 * r + 0.7152 * gg + 0.0722 * b);
      const max = Math.max(r, gg, b), min = Math.min(r, gg, b);
      if (max > 40 && max - min > 12) {
        let hue = 0;
        if (max === r) hue = ((gg - b) / (max - min)) % 6;
        else if (max === gg) hue = (b - r) / (max - min) + 2;
        else hue = (r - gg) / (max - min) + 4;
        pHues[(Math.floor(((hue + 6) % 6) / 6 * 12) + 12) % 12] += 1;
      }
    }
    const pTotal = pHues.reduce((a, b) => a + b, 0) || 1;
    const pHist = pHues.map((v) => v / pTotal);
    const overlap = pHist.reduce((a, v, i) => a + Math.min(v, result.hueHist[i]), 0);
    const ma = pSig.reduce((a, b) => a + b, 0) / pSig.length;
    const mb = result.signature.reduce((a, b) => a + b, 0) / result.signature.length;
    let num = 0, da = 0, db = 0;
    for (let i = 0; i < pSig.length; i += 1) {
      num += (pSig[i] - ma) * (result.signature[i] - mb);
      da += (pSig[i] - ma) ** 2;
      db += (result.signature[i] - mb) ** 2;
    }
    const corr = da && db ? num / Math.sqrt(da * db) : 0;
    result.posterDiff = Math.max(0, Math.min(1, 1 - (0.6 * Math.max(0, corr) + 0.4 * overlap)));
    return result;
  }
};

const rows = [];
let hardFailures = 0;

for (const target of targets) {
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });

  let verdict = "OK";
  let stats = {};
  let frames = 0;

  try {
    await page.goto(target.url, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForSelector(selector, { timeout: 30000 });
    await page.waitForTimeout(duration);
    frames = await page.evaluate(() => window.__frames || 0);
    const shot = await page.locator(selector).screenshot();
    if (shotDir) {
      fs.mkdirSync(shotDir, { recursive: true });
      fs.writeFileSync(path.join(shotDir, `${target.id}.png`), shot);
    }
    const posterB64 = target.poster && fs.existsSync(target.poster)
      ? fs.readFileSync(target.poster).toString("base64")
      : null;
    stats = await page.evaluate(
      (args) => (0, eval)(`(${args.fn})`)(args.img, args.poster),
      { fn: analyse.toString(), img: shot.toString("base64"), poster: posterB64 },
    );
  } catch (error) {
    errors.push(String(error));
  }

  const fps = frames / (duration / 1000);
  if (errors.length) verdict = "ERROR";
  else if (!stats || stats.error) verdict = "ERROR";
  else if (frames < 3) verdict = "FROZEN";
  else if (stats.variance <= 8 && stats.distinct <= 16) verdict = "BLANK";
  else if (stats.variance <= 25 || stats.distinct <= 14) verdict = "THIN";

  if (["ERROR", "BLANK", "FROZEN"].includes(verdict)) hardFailures += 1;

  const line = [
    `${target.id}: ${verdict}`,
    `fps=${fps.toFixed(1)}`,
    `var=${(stats?.variance ?? 0).toFixed(1)}`,
    `distinct=${stats?.distinct ?? 0}`,
    stats?.posterDiff != null ? `posterDiff=${stats.posterDiff.toFixed(2)}` : null,
    errors.length ? `errors=${errors.length}` : null,
  ].filter(Boolean).join(" ");

  rows.push({ id: target.id, verdict, fps, ...stats, errors });
  console.log(line);
  await page.close();
}

await browser.close();

if (out) fs.writeFileSync(out, JSON.stringify(rows, null, 2) + "\n");
if (hardFailures) process.exitCode = 1;
