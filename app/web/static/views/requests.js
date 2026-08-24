/**
 * Every request this page has made, newest first.
 *
 * The reason to run a web client at all is to watch the API answer, so the
 * exchange log is a first-class view rather than something buried in devtools.
 */

import { empty, esc, fmtTime, json, qs } from "../dom.js";

function statusClass(status) {
  if (status === 0) return "status-0";
  if (status >= 500) return "status-5xx";
  if (status >= 400) return "status-4xx";
  return "status-2xx";
}

function exchangeRow(exchange) {
  return `
    <tr class="clickable" data-exchange="${exchange.id}">
      <td class="mono muted">${fmtTime(exchange.at)}</td>
      <td class="mono">${esc(exchange.method)}</td>
      <td class="mono">${esc(exchange.path)}</td>
      <td class="mono ${statusClass(exchange.status)}">${
        exchange.status || "ERR"
      }</td>
      <td class="mono muted">${exchange.ms} ms</td>
    </tr>
    <tr hidden data-detail="${exchange.id}">
      <td colspan="5">
        ${exchange.request ? `<h3>Request</h3>${json(exchange.request)}` : ""}
        <h3>Response</h3>
        ${exchange.response === null ? "<pre>(empty)</pre>" : json(exchange.response)}
      </td>
    </tr>`;
}

export function createRequestsView(ctx) {
  const root = qs("#view-requests");

  function refresh() {
    const exchanges = ctx.api.exchanges;
    root.innerHTML = `
      <div class="card">
        <div class="spread">
          <h2>Request log</h2>
          <div class="row">
            <span class="pill">${exchanges.length} recent</span>
            <button class="btn small ghost" data-action="clear" type="button">Clear</button>
          </div>
        </div>
        <p class="muted" style="margin-top:0">
          Click a row for the JSON that went out and came back.
        </p>
        ${
          exchanges.length
            ? `<div class="table-wrap"><table>
                 <thead><tr><th>Time</th><th>Method</th><th>Path</th><th>Status</th><th>Took</th></tr></thead>
                 <tbody>${exchanges.map(exchangeRow).join("")}</tbody>
               </table></div>`
            : empty("Nothing yet.")
        }`;
    return Promise.resolve();
  }

  root.addEventListener("click", (event) => {
    if (event.target.closest("[data-action='clear']")) {
      ctx.api.clearExchanges();
      refresh();
      return;
    }
    const row = event.target.closest("tr[data-exchange]");
    if (!row) return;
    const detail = root.querySelector(`tr[data-detail="${row.dataset.exchange}"]`);
    if (detail) detail.hidden = !detail.hidden;
  });

  // Re-render only while this tab is the visible one, so logging stays cheap.
  ctx.api.observe(() => {
    if (!root.hidden) refresh();
  });

  return { refresh, clear: () => (root.innerHTML = "") };
}
