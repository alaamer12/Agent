/**
 * specs.js — single-owner declaration of every page's component states.
 * Pure data: pages import their spec, the gallery imports the preview lists.
 * A component's FULL state set (and sub-states) must be enumerable here —
 * if it isn't declared, it isn't queryable, which breaks the contract.
 */

export const FUNDS_SPEC = {
  // tabs / list controls — one param per independent piece of state
  tab:        { default: "overview", values: ["overview", "transactions", "performance"] },
  status:     { default: null,       values: [null, "pending", "failed", "settled"] },
  sort:       { default: "name",     values: ["name", "nav", "chg"] },
  direction:  { default: "asc",      values: ["asc", "desc"] },
  q:          { default: "",         push: "replace" },

  // THE BOTTOM SHEET — its own component with a full enumerable state set,
  // and sub-states for the parts inside it. This is the contract's shape:
  //   ?open=plain|selection|loading|error
  //   ?loading=header|input-fields|all          (sub-state of open=loading)
  //   ?error=network|validation|permission      (sub-state of open=error)
  open:            { default: null, values: [null, "plain", "selection", "loading", "error"] },
  loading:         { default: "all", values: ["header", "input-fields", "all"] },
  error:           { default: "network", values: ["network", "validation", "permission"] },

  // modal component — states + its parametrized subject
  modal:           { default: null, values: [null, "transaction-details"] },
  transactionId:   { default: null },

  toast:           { default: null },
  filled:          { default: null },
};

export const DASH_SPEC = {
  tab: { default: "summary", values: ["summary", "activity"] },
  filled: { default: null },
  // the refresh dropdown as a queryable component with its own states
  refresh: { default: null, values: [null, "open", "loading", "done"] },
};

/** Gallery previews: curated meaningful combinations, owned by the page
 *  spec's author — the gallery only RENDERS this list, never types URLs. */
export const FUNDS_GALLERY = [
  { label: "default",                          query: "" },
  { label: "transactions · pending · Δ sort",  query: "?tab=transactions&status=pending&sort=chg&direction=desc" },
  { label: "search: meridian",                 query: "?q=meridian" },
  { label: "sheet · plain",                    query: "?open=plain" },
  { label: "sheet · selection",                query: "?open=selection" },
  { label: "sheet · loading (header)",         query: "?open=loading&loading=header" },
  { label: "sheet · loading (all)",            query: "?open=loading&loading=all" },
  { label: "sheet · error (permission)",       query: "?open=error&error=permission" },
  { label: "modal · transaction #102",         query: "?modal=transaction-details&transactionId=102" },
  { label: "toast · retry",                    query: "?open=error&error=network&toast=retry" },
  { label: "filled · seed 17",                   query: "?filled=17" },
  { label: "filled · seed 42",                   query: "?filled=42" },
];

export const DASH_GALLERY = [
  { label: "summary",            query: "" },
  { label: "activity",           query: "?tab=activity" },
  { label: "dropdown · open",    query: "?refresh=open" },
  { label: "dropdown · loading", query: "?refresh=loading" },
];
