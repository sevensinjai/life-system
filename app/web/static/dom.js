/** Small DOM and formatting helpers shared by the views. */

const ESCAPES = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

/** Escape a value for interpolation into an HTML template literal. */
export function esc(value) {
  if (value === null || value === undefined) return "";
  return String(value).replace(/[&<>"']/g, (char) => ESCAPES[char]);
}

export const qs = (selector, root = document) => root.querySelector(selector);
export const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];

/**
 * Delegate an event to elements matching `selector`.
 *
 * Views re-render by replacing innerHTML, so listeners are bound once on the
 * container rather than on the elements themselves.
 */
export function delegate(root, type, selector, handler) {
  root.addEventListener(type, (event) => {
    const target = event.target.closest(selector);
    if (target && root.contains(target)) handler(event, target);
  });
}

/** Read a form as a plain object, with empty strings dropped. */
export function formValues(form) {
  const values = {};
  for (const [key, raw] of new FormData(form).entries()) {
    const value = typeof raw === "string" ? raw.trim() : raw;
    if (value !== "") values[key] = value;
  }
  return values;
}

export function toast(message, kind = "info") {
  const host = qs("#toasts");
  const node = document.createElement("div");
  node.className = `toast ${kind}`;
  node.textContent = message;
  host.append(node);
  setTimeout(() => node.remove(), kind === "error" ? 7000 : 3500);
}

/** Render an error — API envelope or otherwise — as a toast. */
export function toastError(error) {
  const details = (error.details ?? [])
    .map((item) => `${(item.loc ?? []).slice(1).join(".")}: ${item.msg}`)
    .filter(Boolean);
  const suffix = details.length ? ` (${details.join("; ")})` : "";
  toast(`${error.message}${suffix}`, "error");
}

export function fmtDate(value) {
  if (!value) return "—";
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.valueOf())
    ? value
    : date.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

export function fmtDateTime(value) {
  if (!value) return "—";
  const date = new Date(/[zZ]|[+-]\d{2}:?\d{2}$/.test(value) ? value : `${value}Z`);
  return Number.isNaN(date.valueOf()) ? value : date.toLocaleString();
}

export function fmtTime(value) {
  const date = value instanceof Date ? value : new Date(value);
  return date.toLocaleTimeString(undefined, { hour12: false });
}

export function plural(count, word) {
  return `${count} ${word}${count === 1 ? "" : "s"}`;
}

/** A 0-100 percentage, clamped, for the width of a meter. */
export function percent(value, total) {
  if (!total) return 0;
  return Math.max(0, Math.min(100, Math.round((value / total) * 100)));
}

export function meter(value, total, { done = false } = {}) {
  return `<div class="meter${done ? " done" : ""}"><span style="width:${percent(
    value,
    total
  )}%"></span></div>`;
}

export function empty(message) {
  return `<p class="empty">${esc(message)}</p>`;
}

export function json(value) {
  return `<pre>${esc(JSON.stringify(value, null, 2))}</pre>`;
}

/** The browser's IANA timezone, for pre-filling registration. */
export function localTimezone() {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}
