import { mountState, rng } from "./_app.js";
import { FUNDS_SPEC } from "./specs.js";
import { icon } from "./glyphs.js";
import { sparkline } from "./charts.js";

const NAV = [
  { id: "101", name: "Alpha Growth Fund",     cat: "equity",    nav: 24.31, chg: 0.82,  status: "settled", series: [21, 22, 21.5, 23, 24, 23.5, 24.31] },
  { id: "102", name: "Meridian Income Fund",  cat: "bond",      nav: 12.07, chg: -0.14, status: "pending", series: [12.4, 12.3, 12.25, 12.1, 12.15, 12.1, 12.07] },
  { id: "103", name: "Northern Light Index",  cat: "equity",    nav: 45.90, chg: 1.24,  status: "settled", series: [43, 44, 44.8, 45, 45.4, 45.6, 45.9] },
  { id: "104", name: "Sable Money Market",    cat: "cash",      nav: 1.00,  chg: 0.01,  status: "failed",  series: [1, 1, 1, 1, 1, 1, 1.0] },
  { id: "105", name: "Copperline Commodity",  cat: "commodity", nav: 18.44, chg: -2.1,  status: "pending", series: [22, 21, 20.4, 19.8, 19, 18.9, 18.44] },
];

/* ?filled=seed -> a FULL dataset appended to the sparse base rows.
   Seeded (never Math.random()): the same seed must draw the same funds. */
const NAME_A = ["Beacon", "Harbor", "Lattice", "Orchard", "Pinnacle", "Quarry", "Riverbend", "Summit", "Thistle", "Vanguard"];
const NAME_B = ["Growth", "Income", "Core", "Opportunity", "Reserve", "Balanced", "Dividend", "Momentum"];
const CATS = ["equity", "bond", "cash", "commodity", "real asset"];
function filledRows(seed) {
  const r = rng(seed);
  const rows = Array.from({ length: 26 }, (_, i) => {
    const name = `${NAME_A[Math.floor(r() * NAME_A.length)]} ${NAME_B[Math.floor(r() * NAME_B.length)]} ${200 + i}`;
    const nav = +(1 + r() * 60).toFixed(2);
    const chg = +((r() - 0.45) * 4).toFixed(2);
    const status = ["settled", "pending", "failed"][Math.floor(r() * 3)];
    const series = Array.from({ length: 7 }, () => +(nav * (0.96 + r() * 0.08)).toFixed(2));
    return { id: String(200 + i), name, cat: CATS[Math.floor(r() * CATS.length)], nav, chg, status, series };
  });
  // adversarial rows on purpose: fill mode must stress the renderer, not flatter it
  rows.push({ id: "998", name: "Consolidated Emerging-Market Sustainable Dividend Opportunity Growth Income Fund plc", cat: "exotic", nav: 1234567.89, chg: -9.99, status: "pending", series: [1e6, 9e5, 1.1e6, 8e5, 1.2e6, 7e5, 1.23e6] });
  rows.push({ id: "997", name: "—", cat: "", nav: 0, chg: 0, status: "failed", series: [0, 0, 0, 0, 0, 0, 0] });
  return rows;
}
const allFunds = state => state.filled ? [...NAV, ...filledRows(state.filled)] : NAV;

const ERRORS = {
  network:    { title: "Couldn’t reach the exchange", detail: "Request timed out after 10s.",                    action: "Retry" },
  validation: { title: "Amount exceeds NAV limit",    detail: "Max ticket for this fund is $25,000.",              action: "Edit amount" },
  permission: { title: "Trading locked",              detail: "This fund requires accredited-investor clearance.", action: "Request access" },
};

const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function fundRows(state) {
  let rows = [...allFunds(state)];
  if (state.status) rows = rows.filter(f => f.status === state.status);
  if (state.q) rows = rows.filter(f => f.name.toLowerCase().includes(state.q.toLowerCase()));
  rows.sort((a, b) => { const d = state.direction === "desc" ? -1 : 1; return a[state.sort] > b[state.sort] ? d : -d; });
  return rows.map(f => `<tr data-id="${f.id}">
    <td>${esc(f.name)}<div class="sub">${f.cat}</div></td>
    <td class="num">${f.nav.toFixed(2)}</td>
    <td class="num ${f.chg >= 0 ? "up" : "down"}">${f.chg >= 0 ? "+" : ""}${f.chg.toFixed(2)}%</td>
    <td><span class="pill ${f.status}">${f.status}</span></td>
    <td>${sparkline(f.series)}</td>
    <td class="num">
      <button class="btn-ghost open-details" data-id="${f.id}">Details ${icon("chevron")}</button>
      <button class="btn-ghost trade" data-id="${f.id}">Trade</button>
    </td></tr>`).join("");
}

/** Bottom sheet — the contract in one component: its FULL state set plus
 *  sub-states, every one queryable:
 *    ?open=plain|selection|loading|error
 *    ?loading=header|input-fields|all        (sub-state when open=loading)
 *    ?error=network|validation|permission    (sub-state when open=error) */
function sheetMarkup(state) {
  const open = state.open;
  if (!open) return "";
  let body;
  if (open === "plain") {
    body = `<h3>Trade · Alpha Growth Fund</h3>
      <p class="muted">NAV 24.31 · settles daily 16:00 UTC</p>
      <label class="field">Amount<input type="text" placeholder="$1,000.00"/></label>
      <button class="btn wide">Review order</button>`;
  } else if (open === "selection") {
    body = `<h3>Choose a fund</h3>
      <div class="options">${NAV.slice(0, 6).map(f => `<label class="option">
        <input type="radio" name="pick" ${f.id === "102" ? "checked" : ""}/> ${esc(f.name)}</label>`).join("")}</div>
      <button class="btn wide">Continue</button>`;
  } else if (open === "loading") {
    const part = state.loading;   // honest shimmer: only the parts actually arriving
    const head = (part === "header" || part === "all")
      ? `<div class="shimmer-row w40"></div>`
      : `<h3>Trade · Alpha Growth Fund</h3>`;
    const fields = (part === "input-fields" || part === "all")
      ? `<div class="shimmer-row"></div><div class="shimmer-row h40"></div>`
      : `<label class="field">Amount<input type="text" placeholder="$1,000.00"/></label>
         <button class="btn wide">Review order</button>`;
    body = head + fields;
  } else {
    const e = ERRORS[state.error] || ERRORS.network;
    body = `<h3 class="down">${e.title}</h3><p class="muted">${e.detail}</p>
      <div class="sheet-actions"><button class="btn sheet-retry">${e.action}</button>
      <button class="btn-ghost close-sheet">Dismiss</button></div>`;
  }
  return `<div class="backdrop sheet-backdrop"></div>
    <div class="sheet" role="dialog" aria-modal="true" data-story="bottom-sheet" data-testid="bottom-sheet"><div class="sheet-handle"></div>
      <button class="x close-sheet" aria-label="close">${icon("close")}</button>${body}
    </div>`;
}

let api;   // handlers fire only after first render, when mountState has assigned it

function render(state) {
  const app = document.body.querySelector(".app") || document.createElement("div");
  if (!app.isConnected) document.body.appendChild(app);
  app.className = "app";
  app.innerHTML = `
    <header class="topbar" data-story="topbar" data-testid="topbar">
      <div class="brand">${icon("menu")} NAV Intelligence</div>
      <div class="tools">${icon("search")}<input class="q" placeholder="Search funds" value="${esc(state.q)}" aria-label="search"/>${icon("bell")}</div>
      <a class="navlink" href="/dashboard">Dashboard</a>
    </header>
    <nav class="tabs" data-story="tabs" data-testid="tabs">
      ${FUNDS_SPEC.tab.values.map(t => `<button class="tab ${state.tab === t ? "active" : ""}" data-tab="${t}">${t}</button>`).join("")}
    </nav>
    ${state.tab === "overview" ? `<section class="panel" data-story="funds-panel" data-testid="funds-panel">
      <div class="filters" data-story="filters" data-testid="filters">${["pending", "failed", "settled"].map(s =>
        `<button class="chip ${state.status === s ? "on" : ""}" data-status="${s}">${s}</button>`).join("")}
        <span class="spacer"></span>
        <select class="sort">${FUNDS_SPEC.sort.values.map(s => `<option ${state.sort === s ? "selected" : ""}>${s}</option>`).join("")}</select>
        <button class="dir">${state.direction === "asc" ? icon("up") : icon("down")}</button>
      </div>
      <table class="funds-table" data-story="funds-table" data-testid="funds-table"><thead><tr><th>Fund</th><th>NAV</th><th>Δ</th><th>Status</th><th>7d</th><th></th></tr></thead>
      <tbody>${fundRows(state)}</tbody></table>
    </section>`
      : state.tab === "transactions" ? `<section class="panel" data-story="transactions-panel" data-testid="transactions-panel"><h2>Transactions</h2>
        <p class="muted">${allFunds(state).filter(f => f.status === "pending").length} pending · ${allFunds(state).filter(f => f.status === "failed").length} failed today (placeholder dataset).</p></section>`
      : `<section class="panel" data-story="performance-panel" data-testid="performance-panel"><h2>Performance</h2>${allFunds(state).slice(0, state.filled ? 200 : NAV.length).map(f => `<div class="perf">${esc(f.name)} ${sparkline(f.series, { color: f.chg >= 0 ? "var(--up)" : "var(--down)" })}</div>`).join("")}</section>`}
    ${state.modal === "transaction-details" ? `<div class="backdrop modal-backdrop"><div class="modal" data-story="modal" data-testid="modal">
      <header>Transaction ${esc(state.transactionId || "—")}<button class="x close-modal">${icon("close")}</button></header>
      <p class="muted">Settlement detail for #${esc(state.transactionId || "—")} (placeholder content, real shape).</p></div></div>` : ""}
    ${sheetMarkup(state)}
    ${state.toast ? `<div class="toast ${state.toast}" data-story="toast" data-testid="toast">${esc(state.toast)} notice (previewed via URL)</div>` : ""}
  `;
  app.querySelectorAll("[data-tab]").forEach(b => b.onclick = () => api.sync({ tab: b.dataset.tab }, { key: "tab" }));
  app.querySelectorAll("[data-status]").forEach(b => b.onclick = () =>
    api.sync({ status: state.status === b.dataset.status ? null : b.dataset.status }, { key: "status" }));
  app.querySelector(".sort")?.addEventListener("change", e => api.sync({ sort: e.target.value }, { key: "sort" }));
  app.querySelector(".dir")?.addEventListener("click", () =>
    api.sync({ direction: state.direction === "asc" ? "desc" : "asc" }, { key: "direction" }));
  app.querySelector(".q")?.addEventListener("input", e => api.sync({ q: e.target.value }, { key: "q", replace: true }));
  app.querySelectorAll(".open-details").forEach(b => b.onclick = () =>
    api.sync({ modal: "transaction-details", transactionId: b.dataset.id }, { key: "modal" }));
  app.querySelectorAll(".trade").forEach(b => b.onclick = () => api.sync({ open: "plain" }, { key: "open" }));
  app.querySelectorAll(".close-sheet").forEach(b => b.onclick = () => api.sync({ open: null }, { key: "open" }));
  app.querySelector(".sheet-backdrop")?.addEventListener("click", () => api.sync({ open: null }, { key: "open" }));
  app.querySelector(".sheet-retry")?.addEventListener("click", () =>
    api.sync({ open: "loading", loading: "all" }, { key: "open" }));
  app.querySelector(".close-modal")?.addEventListener("click", () => api.sync({ modal: null }, { key: "modal" }));
  app.querySelector(".modal-backdrop")?.addEventListener("click",
    e => e.target === e.currentTarget && api.sync({ modal: null }));
}

api = mountState(FUNDS_SPEC, render);
