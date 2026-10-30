/**
 * serve.mjs — zero-dependency dev server with clean-URL routing.
 * Routes /<name> -> pages/<name>.html (query string preserved automatically
 * because only pathname is matched), statics under /js /css /assets, / -> index.html.
 * Node >= 18. Replace with vite/etc. only when the project needs more.
 */
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL(".", import.meta.url));
const PORT = process.env.PORT || 5173;

const ROUTES = { "/": "index.html", "/funds": "pages/funds.html", "/dashboard": "pages/dashboard.html" };
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css",
                ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png",
                ".woff2": "font/woff2", ".ico": "image/x-icon" };

async function send(res, file, queryIgnored) {
  const safe = normalize(file).replace(/^([.][.][\/\\])+/, "");
  if (safe.startsWith("..")) { res.writeHead(403); return res.end("forbidden"); }
  try {
    const body = await readFile(join(ROOT, safe));
    res.writeHead(200, { "Content-Type": TYPES[extname(safe)] || "application/octet-stream" });
    res.end(body);
  } catch {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("not found");
  }
}

const srv = createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  const path = decodeURIComponent(url.pathname);          // query string lives in url.search — preserved by the browser regardless
  if (ROUTES[path]) return send(res, ROUTES[path]);
  if (/^\/(js|css|assets)\//.test(path)) return send(res, path.slice(1));
  res.writeHead(404, { "Content-Type": "text/plain" });
  res.end(`no route for ${path} — add it to ROUTES in serve.mjs`);
});
srv.on("error", (e) => {
  if (e.code === "EADDRINUSE") { console.error(`port ${PORT} is busy — another serve.mjs may already run (or set PORT=...)`); process.exit(2); }
  throw e;
});
srv.listen(PORT, () => {
  console.log(`prototype at http://localhost:${PORT}   (${Object.keys(ROUTES).join(" ")})`);
});
