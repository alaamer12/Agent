/**
 * stories.renderers.js — the seam between a story card and a real component.
 *
 * Two supported modes, chosen WITH THE USER (see references/06-integration-with-prototype.md):
 *
 *  A. SHARED (preferred when js/components/ exists): import the project's renderers and re-export
 *     them here, so a card renders exactly what a page renders — the gallery can never drift.
 *         import { toggle, numericField } from "./components/index.js";
 *         export const renderers = { toggle, "numeric-field": numericField };
 *
 *  B. CLONED (only when the user chose it, or the component does not exist yet): implement locally,
 *     copy the markup and classes from the page verbatim, and mark the clone so the drift is
 *     visible:  fn.storySource = "cloned-from:pages/funds.html";
 *
 * Contract for every renderer: (props, stateKey) => Element. It must produce real state —
 * `disabled` sets the disabled attribute and the aria state, `invalid` renders the error message
 * and the error styling hook — never a CSS filter pretending to be a state.
 *
 * The template below is a working example of the contract, not project copy: replace everything
 * with the project's components and real subject matter.
 */

const h = (tag, cls, text) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined && text !== null) n.textContent = text;
  return n;
};

function labelledField(control, props) {
  const wrap = h("div", "field");
  if (props.label) wrap.append(h("label", "field__label", props.label));
  wrap.append(control);
  if (props.error) wrap.append(h("p", "field__error", props.error));
  else if (props.hint) wrap.append(h("p", "field__hint", props.hint));
  return wrap;
}

function toggle(props, stateKey) {
  const row = h("div", "c-toggle" + (stateKey === "disabled" ? " is-disabled" : ""));
  const btn = h("button", "c-toggle__switch");
  btn.type = "button";
  btn.setAttribute("role", "switch");
  btn.setAttribute("aria-checked", String(!!props.on));
  btn.setAttribute("aria-label", props.label || "تبديل");
  if (stateKey === "disabled" || stateKey === "required-off") btn.disabled = true;
  row.append(h("span", "c-toggle__label", props.label || ""), btn);
  return row;
}

function numericField(props, stateKey) {
  const input = h("input", "c-input");
  input.type = "number";
  input.value = props.value === null || props.value === undefined ? "" : String(props.value);
  input.setAttribute("aria-label", props.label || "قيمة رقمية");
  if (stateKey === "invalid") input.setAttribute("aria-invalid", "true");
  if (stateKey === "disabled") input.disabled = true;
  const box = h("div", "c-number");
  box.append(input);
  if (props.unit) box.append(h("span", "c-number__unit", props.unit));
  return labelledField(box, props);
}

function textEntry(props, stateKey) {
  const input = h("input", "c-input");
  input.type = "text";
  input.value = props.value || "";
  input.setAttribute("aria-label", props.label || "نص");
  if (stateKey === "invalid") input.setAttribute("aria-invalid", "true");
  return labelledField(input, props);
}

function slider(props, stateKey) {
  const wrap = h("div", "c-slider");
  const input = h("input", "c-slider__input");
  input.type = "range";
  input.min = String(props.min ?? 0);
  input.max = String(props.max ?? 100);
  input.value = String(props.value ?? 0);
  input.setAttribute("aria-label", props.label || "مؤشر");
  if (stateKey === "disabled") input.disabled = true;
  wrap.append(h("span", "c-slider__value", String(props.value ?? 0)), input);
  return labelledField(wrap, props);
}

function filePicker(props, stateKey) {
  const row = h("div", "c-file");
  if (props.file) {
    row.append(h("code", "c-file__name", props.file), h("button", "c-file__action", props.action || "تغيير"));
  } else {
    const btn = h("button", "c-file__pick", "اختيار ملف...");
    btn.type = "button";
    if (stateKey === "disabled") btn.disabled = true;
    row.append(btn);
  }
  return labelledField(row, props);
}

export const renderers = {
  toggle,
  "numeric-field": numericField,
  "text-entry": textEntry,
  slider,
  "file-picker": filePicker,
};
