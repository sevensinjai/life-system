/** The system log: the notification feed and the penalty ledger. */

import { empty, esc, fmtDateTime, json, qs } from "../dom.js";

const EVENT_TYPES = [
  "quest_created",
  "quest_progress",
  "quest_completed",
  "quest_failed",
  "level_up",
  "stats_allocated",
  "penalty_applied",
  "daily_reset",
];

const PAGE_SIZE = 25;

function eventRow(event) {
  const hasPayload = event.payload && Object.keys(event.payload).length > 0;
  return `
    <tr class="${hasPayload ? "clickable" : ""}" data-event="${event.id}">
      <td class="mono muted">${fmtDateTime(event.created_at)}</td>
      <td><span class="pill">${esc(event.event_type)}</span></td>
      <td>
        ${esc(event.message)}
        ${hasPayload ? `<div hidden data-payload="${event.id}">${json(event.payload)}</div>` : ""}
      </td>
    </tr>`;
}

export function createLogView(ctx) {
  const root = qs("#view-log");
  const state = { eventType: "", offset: 0 };

  async function refresh() {
    const [events, penalties] = await Promise.all([
      ctx.api.events({
        event_type: state.eventType || undefined,
        limit: PAGE_SIZE,
        offset: state.offset,
      }),
      ctx.api.penalties({ limit: PAGE_SIZE }),
    ]);

    root.innerHTML = `
      <div class="card">
        <div class="spread">
          <h2>System log</h2>
          <div class="row">
            <label class="inline-field">
              <span>type</span>
              <select data-filter="event_type">
                <option value="">all</option>
                ${EVENT_TYPES.map(
                  (type) =>
                    `<option value="${type}"${
                      state.eventType === type ? " selected" : ""
                    }>${type}</option>`
                ).join("")}
              </select>
            </label>
            <button class="btn small ghost" data-page="prev" type="button"${
              state.offset === 0 ? " disabled" : ""
            }>Newer</button>
            <span class="pill">${state.offset + 1}–${state.offset + events.length}</span>
            <button class="btn small ghost" data-page="next" type="button"${
              events.length < PAGE_SIZE ? " disabled" : ""
            }>Older</button>
          </div>
        </div>
        <p class="muted" style="margin-top:0">Newest first. Rows with a payload expand.</p>
        ${
          events.length
            ? `<div class="table-wrap"><table>
                 <thead><tr><th>When</th><th>Type</th><th>Message</th></tr></thead>
                 <tbody>${events.map(eventRow).join("")}</tbody>
               </table></div>`
            : empty("No events yet.")
        }
      </div>

      <div class="card">
        <h2>Penalties</h2>
        ${
          penalties.length
            ? `<div class="table-wrap"><table>
                 <thead><tr><th>When</th><th>Reason</th><th>EXP lost</th></tr></thead>
                 <tbody>${penalties
                   .map(
                     (penalty) => `
                       <tr>
                         <td class="mono muted">${fmtDateTime(penalty.created_at)}</td>
                         <td>${esc(penalty.reason)}</td>
                         <td class="mono status-4xx">-${penalty.exp_lost}</td>
                       </tr>`
                   )
                   .join("")}</tbody>
               </table></div>`
            : empty("No EXP lost yet. Keep it that way.")
        }
      </div>`;
  }

  root.addEventListener("change", async (event) => {
    if (event.target.dataset.filter !== "event_type") return;
    state.eventType = event.target.value;
    state.offset = 0;
    await ctx.guard(refresh);
  });

  root.addEventListener("click", async (event) => {
    const pager = event.target.closest("[data-page]");
    if (pager) {
      state.offset = Math.max(
        0,
        state.offset + (pager.dataset.page === "next" ? PAGE_SIZE : -PAGE_SIZE)
      );
      await ctx.guard(refresh);
      return;
    }

    const row = event.target.closest("tr[data-event]");
    if (!row) return;
    const payload = row.querySelector("[data-payload]");
    if (payload) payload.hidden = !payload.hidden;
  });

  return { refresh, clear: () => (root.innerHTML = "") };
}
