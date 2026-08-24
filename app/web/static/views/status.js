/** The status window: level, EXP, stats, allocation, profile, daily reset. */

import {
  delegate,
  empty,
  esc,
  formValues,
  fmtDateTime,
  meter,
  plural,
  qs,
  toast,
} from "../dom.js";

const STATS = ["strength", "agility", "vitality", "intelligence", "perception"];

function statusWindow(status) {
  return `
    <div class="card">
      <div class="spread">
        <h2>${esc(status.name)}</h2>
        <span class="pill">LEVEL ${status.level}</span>
      </div>
      <p class="muted mono">
        ${status.exp} / ${status.exp_to_next_level} EXP
        &middot; ${Math.round(status.exp_progress * 100)}% to level ${status.level + 1}
      </p>
      ${meter(status.exp, status.exp_to_next_level)}
      <div class="numbers" style="margin-top:0.9rem">
        <div><div class="label">Total EXP</div><div class="value">${status.total_exp_earned}</div></div>
        <div><div class="label">Unspent points</div><div class="value">${status.stat_points}</div></div>
        <div><div class="label">Timezone</div><div class="value" style="font-size:0.9rem">${esc(
          status.timezone
        )}</div></div>
      </div>
      <div class="numbers stats" style="margin-top:0.6rem">
        ${STATS.map(
          (stat) => `
            <div>
              <div class="label">${stat.slice(0, 3)}</div>
              <div class="value">${status.stats[stat]}</div>
            </div>`
        ).join("")}
      </div>
    </div>`;
}

function allocateForm(status) {
  const disabled = status.stat_points === 0 ? " disabled" : "";
  return `
    <div class="card">
      <h2>Allocate stat points</h2>
      <p class="muted">${plural(status.stat_points, "point")} available. An
      unaffordable allocation is rejected whole.</p>
      <form id="allocate-form" class="stack">
        <div class="numbers">
          ${STATS.map(
            (stat) => `
              <label class="field">
                <span>${stat}</span>
                <input type="number" name="${stat}" min="0" value="0"${disabled} />
              </label>`
          ).join("")}
        </div>
        <div class="row">
          <button class="btn primary" type="submit"${disabled}>Spend</button>
        </div>
      </form>
    </div>`;
}

function profileForm(status, account) {
  return `
    <div class="card">
      <h2>Profile</h2>
      <p class="muted mono">
        ${account ? esc(account.email) : "—"}
        ${account ? `&middot; account #${account.id}` : ""}
      </p>
      <form id="profile-form" class="stack">
        <label class="field">
          <span>Hunter name</span>
          <input name="name" type="text" maxlength="80" value="${esc(status.name)}" />
        </label>
        <label class="field">
          <span>Timezone</span>
          <input name="timezone" type="text" spellcheck="false" value="${esc(
            status.timezone
          )}" />
          <small>Periods turn at midnight here. Changing it shifts future rollovers only.</small>
        </label>
        <div class="row"><button class="btn" type="submit">Save</button></div>
      </form>
    </div>`;
}

function resetCard(result) {
  return `
    <div class="card">
      <h2>Daily reset</h2>
      <p class="muted">
        <code class="mono">POST /system/daily-reset</code> lapses periods that
        ended before today and opens the ones now due. Idempotent within a local
        day — the iOS client calls it on launch and on foreground.
      </p>
      <div class="row">
        <button class="btn primary" data-action="daily-reset" type="button">Run reset</button>
        ${
          result
            ? `<span class="pill">${result.reset_date} &middot; ${result.failed_count} failed
               &middot; ${result.spawned_count} opened${
                 result.total_exp_lost ? ` &middot; -${result.total_exp_lost} EXP` : ""
               }</span>`
            : ""
        }
      </div>
      ${
        result && result.failed_count
          ? `<p class="muted" style="margin-bottom:0">Ran at ${fmtDateTime(
              new Date().toISOString()
            )}.</p>`
          : ""
      }
    </div>`;
}

export function createStatusView(ctx) {
  const root = qs("#view-status");
  let lastReset = null;

  async function refresh() {
    const [status, account] = await Promise.all([ctx.api.status(), ctx.api.account()]);
    root.innerHTML = `
      <div class="grid">
        <div>${statusWindow(status)}${resetCard(lastReset)}</div>
        <div>${allocateForm(status)}${profileForm(status, account)}</div>
      </div>`;
  }

  delegate(root, "click", "[data-action='daily-reset']", async () => {
    await ctx.guard(async () => {
      lastReset = await ctx.api.dailyReset();
      const { failed_count: failed, spawned_count: spawned, total_exp_lost: lost } = lastReset;
      toast(
        `Reset ${lastReset.reset_date}: ${failed} failed, ${spawned} opened` +
          (lost ? `, -${lost} EXP.` : "."),
        failed ? "error" : "success"
      );
      await ctx.refresh("status", "board", "quests", "log");
    });
  });

  root.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;

    if (form.id === "allocate-form") {
      const values = formValues(form);
      const payload = Object.fromEntries(
        STATS.map((stat) => [stat, Number(values[stat] ?? 0)])
      );
      await ctx.guard(async () => {
        await ctx.api.allocate(payload);
        toast("Stat points spent.", "success");
        await ctx.refresh("status", "log");
      });
      return;
    }

    if (form.id === "profile-form") {
      await ctx.guard(async () => {
        await ctx.api.updatePlayer(formValues(form));
        toast("Profile updated.", "success");
        await ctx.refresh("status");
      });
    }
  });

  return { refresh, clear: () => (root.innerHTML = empty("Loading…")) };
}
