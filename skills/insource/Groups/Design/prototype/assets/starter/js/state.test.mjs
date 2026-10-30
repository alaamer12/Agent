/**
 * Unit tests for the pure state helper — DOM-free, run with `node js/state.test.mjs`
 * (or npm test). Reuse this harness for every prototype copy: if the helper
 * changes and this stays green, the URL contract holds.
 *
 * The contract under test is the COMPONENT-STATE model: each interactive
 * component owns a small state tree — a mode param plus its sub-state
 * params — and every meaningful (sub)state must be reachable and composable
 * through the URL. E.g. the funds bottom sheet:
 *   ?open=loading&loading=header   (sheet open, loading state, header region arriving)
 *   ?open=error&error=permission   (sheet open, error state, this error kind)
 */
import { parse, toQuery, patch, historyMode, rng } from "./_app.js";
import { FUNDS_SPEC } from "./specs.js";

let failed = 0;
const check = (name, cond) => { console.log((cond ? "OK   " : "FAIL ") + name); if (!cond) failed++; };

// --- component state tree: parent mode + sub-state compose ----------------
const sheetLoading = parse("?open=loading&loading=header", FUNDS_SPEC);
check("component tree: mode + sub-state parse independently",
      sheetLoading.state.open === "loading" && sheetLoading.state.loading === "header");

const sheetDefaultSub = parse("?open=plain", FUNDS_SPEC);
check("component tree: sub-state keeps its own default regardless of parent",
      sheetDefaultSub.state.open === "plain" && sheetDefaultSub.state.loading === "all");

check("component tree: error-kind sub-state queryable",
      parse("?open=error&error=permission", FUNDS_SPEC).state.error === "permission");

check("invalid sub-state value -> its default, never a crash",
      parse("?open=error&error=bogus", FUNDS_SPEC).state.error === "network"
      && parse("?open=error&error=bogus", FUNDS_SPEC).state.open === "error");

// --- multiple components coexist on one URL -------------------------------
const composed = parse("?tab=transactions&status=pending&open=selection&modal=transaction-details&transactionId=102", FUNDS_SPEC);
check("multiple components compose on one URL",
      composed.state.tab === "transactions" && composed.state.status === "pending"
      && composed.state.open === "selection" && composed.state.modal === "transaction-details"
      && composed.state.transactionId === "102");

// --- changing one component preserves the rest (req 8) --------------------
const before = parse("?tab=transactions&open=plain&q=meridian", FUNDS_SPEC);
const afterQuery = toQuery(patch(before.state, { open: "selection" }), FUNDS_SPEC, before.foreign);
check("changing one component's state preserves unrelated params",
      /tab=transactions/.test(afterQuery) && /open=selection/.test(afterQuery) && /q=meridian/.test(afterQuery));

// --- defaults omitted; round-trip stable ----------------------------------
check("defaults omitted (closed sheet / default tab produce no params)",
      toQuery(parse("", FUNDS_SPEC).state, FUNDS_SPEC) === "");

const src = "?tab=performance&sort=nav&direction=desc&q=alpha&open=loading&loading=input-fields";
check("full round-trip stable", toQuery(parse(src, FUNDS_SPEC).state, FUNDS_SPEC) === src);

// --- foreign params survive the component machinery -----------------------
const f = parse("?utm_source=campaign&open=error", FUNDS_SPEC);
check("foreign preserved through parse + write-back",
      f.foreign.utm_source === "campaign"
      && toQuery(patch(f.state, { error: "validation" }), FUNDS_SPEC, f.foreign).includes("utm_source=campaign"));

// --- history policy per discrete vs continuous state ----------------------
check("history policy: discrete component states push, continuous fields replace",
      historyMode("open", FUNDS_SPEC) === "push" && historyMode("q", FUNDS_SPEC) === "replace");

check("?filled round-trips in the URL", toQuery(parse("?filled=17", FUNDS_SPEC).state, FUNDS_SPEC) === "?filled=17");
const r1 = rng("17"), r2 = rng("17"), r3 = rng("42");
check("seeded rng is reproducible and seed-sensitive", r1() === r2() && r1() !== r3());

console.log(failed ? `\n${failed} FAILURE(S)` : "\nALL PASS");
process.exit(failed ? 1 : 0);
