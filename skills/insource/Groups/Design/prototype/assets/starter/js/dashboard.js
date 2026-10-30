import { mountState, rng } from "./_app.js";
import { DASH_SPEC } from "./specs.js";
import { icon } from "./glyphs.js";
import { sparkline } from "./charts.js";

let api;   // handlers fire only after first render, when mountState has assigned it

/** Refresh dropdown — a second component with its own enumerable states:
 *  ?refresh=open|loading|done  */
function refreshMenu(state) {
  if (!state.refresh) return "";
  const body =
    state.refresh === "loading" ? `<div class="menu"><div class="shimmer-row w60"></div></div>`
    : state.refresh === "done"  ? `<div class="menu"><p class="muted ok-line">Updated 14:07 UTC</p></div>`
    : `<div class="menu"><button class="menu-item" data-refresh="loading">Re-aggregate now</button>
       <button class="menu-item" data-refresh="loading">From last snapshot</button></div>`;
  return `<div class="refresh-wrap"><button class="btn-ghost refresh-btn">Refresh ${icon("chevron")}</button>${body}</div>`;
}

const ACTS = ["NAV published", "deviation flagged", "settlement retry queued", "window recalculated"];
function activityLines(state) {
  const base = ["14:02 — Meridian Income NAV published", "13:41 — Copperline deviation flagged (-2.1%)",
                "11:20 — Sable MM settlement failed, retry queued"];
  if (!state.filled) return base;
  const r = rng(state.filled);
  for (let i = 0; i < 24; i++) {
    const t = String(Math.floor(r() * 14)).padStart(2, "0") + ":" + String(Math.floor(r() * 60)).padStart(2, "0");
    base.push(`${t} — Fund ${200 + i} ${ACTS[Math.floor(r() * ACTS.length)]}`);
  }
  return base;
}

function render(state) {
  const app = document.body.querySelector(".app") || document.createElement("div");
  if (!app.isConnected) document.body.appendChild(app);
  app.className = "app";
  app.innerHTML = `
    <header class="topbar">
      <div class="brand">${icon("menu")} NAV Intelligence</div>
      <div class="tools">${refreshMenu(state)}</div>
      <a class="navlink" href="/funds">Funds</a>
    </header>
    <nav class="tabs">
      ${DASH_SPEC.tab.values.map(t => `<button class="tab ${state.tab === t ? "active" : ""}" data-tab="${t}">${t}</button>`).join("")}
    </nav>
    <section class="panel">
      ${state.tab === "summary"
        ? `<div class="cards">
             <div class="card"><h4>AUM</h4><div class="big">$1.24B</div>${sparkline([1.0, 1.1, 1.15, 1.2, 1.18, 1.22, 1.24])}</div>
             <div class="card"><h4>Settled today</h4><div class="big">212</div></div>
             <div class="card"><h4>Exceptions</h4><div class="big down">3</div></div>
           </div>`
        : `<ul class="activity">${activityLines(state).map(a => `<li>${a}</li>`).join("")}</ul>`}
    </section>`;
  app.querySelectorAll("[data-tab]").forEach(b => b.onclick = () => api.sync({ tab: b.dataset.tab }, { key: "tab" }));
  app.querySelector(".refresh-btn")?.addEventListener("click", () =>
    api.sync({ refresh: state.refresh ? null : "open" }, { key: "refresh" }));
  app.querySelectorAll("[data-refresh]").forEach(b => b.onclick = () => api.sync({ refresh: b.dataset.refresh }, { key: "refresh" }));
}

api = mountState(DASH_SPEC, render);
