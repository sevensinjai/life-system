/** The board (quests open right now) and the quest designer. */

import {
  delegate,
  empty,
  esc,
  fmtDate,
  formValues,
  meter,
  qs,
  toast,
} from "../dom.js";

const DIFFICULTIES = ["E", "D", "C", "B", "A", "S"];
const SCHEDULE_KINDS = ["once", "daily", "weekdays", "interval", "weekly"];
const STATS = ["strength", "agility", "vitality", "intelligence", "perception"];
const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

/** One quest, with its open period if it has one. */
function questCard(quest, { showSchedule = true } = {}) {
  const instance = quest.current_instance;
  // Only an active period takes progress; a cleared or failed one is history
  // the API will refuse to touch, so it gets a badge instead of buttons.
  const open = instance !== null && instance !== undefined && instance.status === "active";
  const done = instance ? instance.status === "completed" || instance.progress >= instance.target_count : false;

  const facts = [
    `${quest.exp_reward} EXP`,
    quest.stat_reward
      ? `+${quest.stat_reward_amount} ${quest.stat_reward}`
      : null,
    showSchedule ? esc(quest.schedule.label) : null,
    quest.unit ? `${quest.target_count} ${esc(quest.unit)}` : null,
    !quest.is_active ? "archived" : null,
  ].filter(Boolean);

  const period = instance
    ? `
      <div style="margin-top:0.6rem">
        <div class="spread" style="font-size:0.82rem">
          <span class="mono">${instance.progress} / ${instance.target_count}${
        quest.unit ? ` ${esc(quest.unit)}` : ""
      }</span>
          <span class="muted">${
            open
              ? instance.period_end
                ? `due ${fmtDate(instance.period_end)}`
                : "no deadline"
              : instance.status === "completed"
              ? "cleared"
              : "failed"
          }</span>
        </div>
        ${meter(instance.progress, instance.target_count, { done })}
      </div>`
    : `<p class="muted" style="margin:0.5rem 0 0;font-size:0.85rem">
         No open period. ${
           quest.next_due_date ? `Next due ${fmtDate(quest.next_due_date)}.` : "Waiting."
         }
       </p>`;

  const nextUp =
    instance && !open && quest.next_due_date
      ? `<p class="muted" style="margin:0.4rem 0 0;font-size:0.8rem">Next period ${fmtDate(
          quest.next_due_date
        )}.</p>`
      : "";

  const actions = open
    ? `
      <button class="btn small" data-action="progress" data-id="${quest.id}" data-amount="1" type="button">+1</button>
      <input class="mono" type="number" value="1" data-amount-for="${quest.id}" style="width:4.5rem" />
      <button class="btn small" data-action="progress-custom" data-id="${quest.id}" type="button">Add</button>
      <button class="btn small primary" data-action="complete" data-id="${quest.id}" type="button">Complete</button>`
    : "";

  return `
    <article class="item${quest.is_active ? "" : " archived"}">
      <div class="spread">
        <div class="item-title">
          <span class="rank" data-rank="${quest.difficulty}">${quest.difficulty}</span>
          <span>${esc(quest.title)}</span>
        </div>
        <span class="pill">#${quest.id}</span>
      </div>
      ${
        quest.description
          ? `<p class="muted" style="margin:0.35rem 0 0;font-size:0.86rem">${esc(
              quest.description
            )}</p>`
          : ""
      }
      <p class="muted mono" style="margin:0.35rem 0 0;font-size:0.78rem">${facts.join(
        " &middot; "
      )}</p>
      ${period}
      ${nextUp}
      <div class="row" style="margin-top:0.6rem">
        ${actions}
        <button class="btn small ghost" data-action="edit" data-id="${quest.id}" type="button">Edit</button>
        ${
          quest.is_active
            ? `<button class="btn small danger" data-action="archive" data-id="${quest.id}" type="button">Archive</button>`
            : `<button class="btn small ghost" data-action="restore" data-id="${quest.id}" type="button">Restore</button>`
        }
      </div>
    </article>`;
}

/** The shared authoring form, used for both creating and editing. */
function questForm(quest) {
  const schedule = quest?.schedule ?? { kind: "once", week_start: 0 };
  const days = schedule.days ?? [];
  return `
    <div class="stack">
      <label class="field">
        <span>Title</span>
        <input name="title" type="text" maxlength="200" required value="${esc(
          quest?.title ?? ""
        )}" />
      </label>
      <label class="field">
        <span>Description</span>
        <input name="description" type="text" value="${esc(quest?.description ?? "")}" />
      </label>
      <div class="row">
        <label class="field">
          <span>Difficulty</span>
          <select name="difficulty">
            ${DIFFICULTIES.map(
              (rank) =>
                `<option value="${rank}"${
                  (quest?.difficulty ?? "E") === rank ? " selected" : ""
                }>${rank}</option>`
            ).join("")}
          </select>
        </label>
        <label class="field">
          <span>Target count</span>
          <input name="target_count" type="number" min="1" value="${
            quest?.target_count ?? 1
          }" />
        </label>
        <label class="field">
          <span>Unit</span>
          <input name="unit" type="text" maxlength="32" placeholder="reps" value="${esc(
            quest?.unit ?? ""
          )}" />
        </label>
        <label class="field">
          <span>EXP override</span>
          <input name="exp_reward" type="number" min="0" placeholder="by rank" value="${
            quest ? quest.exp_reward : ""
          }" />
        </label>
      </div>
      <div class="row">
        <label class="field">
          <span>Stat reward</span>
          <select name="stat_reward">
            <option value="">none</option>
            ${STATS.map(
              (stat) =>
                `<option value="${stat}"${
                  quest?.stat_reward === stat ? " selected" : ""
                }>${stat}</option>`
            ).join("")}
          </select>
        </label>
        <label class="field">
          <span>Stat amount</span>
          <input name="stat_reward_amount" type="number" min="0" value="${
            quest?.stat_reward_amount ?? 0
          }" />
        </label>
      </div>

      <h3>Schedule</h3>
      <div class="row">
        <label class="field">
          <span>Kind</span>
          <select name="kind" data-schedule-kind>
            ${SCHEDULE_KINDS.map(
              (kind) =>
                `<option value="${kind}"${
                  schedule.kind === kind ? " selected" : ""
                }>${kind}</option>`
            ).join("")}
          </select>
        </label>
        <label class="field" data-when="interval">
          <span>Every N days</span>
          <input name="interval_days" type="number" min="1" max="365" value="${
            schedule.interval_days ?? 2
          }" />
        </label>
        <label class="field" data-when="weekly">
          <span>Week starts</span>
          <select name="week_start">
            ${DAY_NAMES.map(
              (day, index) =>
                `<option value="${index}"${
                  (schedule.week_start ?? 0) === index ? " selected" : ""
                }>${day}</option>`
            ).join("")}
          </select>
        </label>
        <label class="field">
          <span>Anchor</span>
          <input name="anchor" type="date" value="${schedule.anchor ?? ""}" />
        </label>
      </div>
      <div class="days" data-when="weekdays">
        ${DAY_NAMES.map(
          (day, index) =>
            `<label><input type="checkbox" name="days" value="${index}"${
              days.includes(index) ? " checked" : ""
            } />${day}</label>`
        ).join("")}
      </div>
    </div>`;
}

/** Show only the schedule fields that apply to the selected kind. */
function syncScheduleFields(form) {
  const kind = form.querySelector("[data-schedule-kind]").value;
  for (const node of form.querySelectorAll("[data-when]")) {
    node.hidden = node.dataset.when !== kind;
  }
}

/** Turn the form into a QuestCreate/QuestUpdate payload. */
function readQuestForm(form) {
  const values = formValues(form);
  const kind = values.kind ?? "once";

  const schedule = { kind };
  if (kind === "weekdays") {
    schedule.days = [...form.querySelectorAll("input[name='days']:checked")].map((box) =>
      Number(box.value)
    );
  }
  if (kind === "interval") schedule.interval_days = Number(values.interval_days ?? 1);
  if (kind === "weekly") schedule.week_start = Number(values.week_start ?? 0);
  if (values.anchor) schedule.anchor = values.anchor;

  const payload = {
    title: values.title,
    description: values.description ?? null,
    schedule,
    difficulty: values.difficulty ?? "E",
    target_count: Number(values.target_count ?? 1),
    unit: values.unit ?? null,
    stat_reward: values.stat_reward ?? null,
    stat_reward_amount: Number(values.stat_reward_amount ?? 0),
  };

  // Omitted rather than sent as null: a quest's EXP reward is not nullable, so
  // a blank field means "the rank's default" on create and "leave it" on edit.
  if (values.exp_reward !== undefined) payload.exp_reward = Number(values.exp_reward);

  return payload;
}

/** Announce what a quest action earned, since the response carries it. */
function reportAction(result) {
  if (result.completed) {
    const gained = result.exp_gained ? ` +${result.exp_gained} EXP` : "";
    toast(
      `${result.quest.title} cleared.${gained}${result.leveled_up ? " LEVEL UP!" : ""}`,
      "success"
    );
  } else {
    const { progress, target_count: target } = result.instance;
    toast(`${result.quest.title}: ${progress} / ${target}.`);
  }
}

/** Wire the quest actions shared by the board and the quest list. */
function bindQuestActions(root, ctx, { onChange }) {
  const amountFor = (id) => {
    const input = root.querySelector(`[data-amount-for="${id}"]`);
    const amount = Number(input?.value ?? 1);
    return Number.isFinite(amount) && amount !== 0 ? amount : 1;
  };

  delegate(root, "click", "[data-action]", async (event, button) => {
    const { action, id } = button.dataset;
    const questId = Number(id);
    if (!questId) return;

    await ctx.guard(async () => {
      switch (action) {
        case "progress":
        case "progress-custom": {
          const amount =
            action === "progress" ? Number(button.dataset.amount) : amountFor(questId);
          reportAction(await ctx.api.logProgress(questId, amount));
          break;
        }
        case "complete":
          reportAction(await ctx.api.completeQuest(questId));
          break;
        case "archive":
          await ctx.api.archiveQuest(questId);
          toast("Quest archived. Its history is kept.");
          break;
        case "restore":
          await ctx.api.updateQuest(questId, { is_active: true });
          toast("Quest restored.", "success");
          break;
        case "edit":
          await onChange.edit(questId);
          return;
        default:
          return;
      }
      await ctx.refresh("board", "quests", "status", "log");
    });
  });
}

export function createBoardView(ctx) {
  const root = qs("#view-board");

  async function refresh() {
    const quests = await ctx.api.board();
    root.innerHTML = `
      <div class="card">
        <div class="spread">
          <h2>On the board today</h2>
          <span class="pill">${quests.length} open</span>
        </div>
        <p class="muted" style="margin-top:0">
          Everything with a period open right now, ordered by deadline. Run the
          daily reset on the Status tab first if periods look stale.
        </p>
        ${
          quests.length
            ? quests.map((quest) => questCard(quest)).join("")
            : empty("Nothing open. Author a quest, or run the daily reset.")
        }
      </div>`;
  }

  bindQuestActions(root, ctx, { onChange: { edit: (id) => ctx.editQuest(id) } });
  return { refresh, clear: () => (root.innerHTML = "") };
}

export function createQuestsView(ctx) {
  const root = qs("#view-quests");
  const filters = { schedule: "", recurring_only: false, include_archived: false };

  async function refresh() {
    const query = {
      schedule: filters.schedule || undefined,
      recurring_only: filters.recurring_only ? "true" : undefined,
      include_archived: filters.include_archived ? "true" : undefined,
    };
    const quests = await ctx.api.quests(query);

    root.innerHTML = `
      <div class="grid">
        <div class="card">
          <h2>Author a quest</h2>
          <form id="create-quest">
            ${questForm(null)}
            <div class="row" style="margin-top:0.8rem">
              <button class="btn primary" type="submit">Create quest</button>
              <button class="btn ghost" type="reset">Reset form</button>
            </div>
          </form>
        </div>

        <div class="card">
          <div class="spread">
            <h2>Your quests</h2>
            <span class="pill">${quests.length}</span>
          </div>
          <div class="row" style="margin:0.4rem 0 0.8rem">
            <label class="inline-field">
              <span>schedule</span>
              <select data-filter="schedule">
                <option value="">all</option>
                ${SCHEDULE_KINDS.map(
                  (kind) =>
                    `<option value="${kind}"${
                      filters.schedule === kind ? " selected" : ""
                    }>${kind}</option>`
                ).join("")}
              </select>
            </label>
            <label class="checkbox">
              <input type="checkbox" data-filter="recurring_only"${
                filters.recurring_only ? " checked" : ""
              } /> recurring only
            </label>
            <label class="checkbox">
              <input type="checkbox" data-filter="include_archived"${
                filters.include_archived ? " checked" : ""
              } /> include archived
            </label>
          </div>
          ${
            quests.length
              ? quests.map((quest) => questCard(quest)).join("")
              : empty("No quests match. Author one on the left.")
          }
        </div>
      </div>`;

    syncScheduleFields(qs("#create-quest", root));
  }

  root.addEventListener("change", async (event) => {
    const { filter } = event.target.dataset;
    if (filter) {
      filters[filter] =
        event.target.type === "checkbox" ? event.target.checked : event.target.value;
      await ctx.guard(refresh);
      return;
    }
    if (event.target.matches("[data-schedule-kind]")) {
      syncScheduleFields(event.target.closest("form"));
    }
  });

  root.addEventListener("submit", async (event) => {
    if (event.target.id !== "create-quest") return;
    event.preventDefault();
    const form = event.target;
    await ctx.guard(async () => {
      const quest = await ctx.api.createQuest(readQuestForm(form));
      toast(`"${quest.title}" added to your board.`, "success");
      form.reset();
      await ctx.refresh("quests", "board", "log");
    });
  });

  bindQuestActions(root, ctx, { onChange: { edit: (id) => ctx.editQuest(id) } });
  return { refresh, clear: () => (root.innerHTML = "") };
}

/**
 * The edit dialog, shared by both quest views.
 *
 * Kept at the app level rather than inside a view so editing from the board
 * and from the quest list open the same thing.
 */
export function createQuestEditor(ctx) {
  const dialog = document.createElement("dialog");
  dialog.id = "quest-editor";
  document.body.append(dialog);

  dialog.addEventListener("change", (event) => {
    if (event.target.matches("[data-schedule-kind]")) {
      syncScheduleFields(event.target.closest("form"));
    }
  });

  dialog.addEventListener("click", (event) => {
    if (event.target.dataset.action === "cancel") dialog.close();
  });

  dialog.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    const id = Number(form.dataset.questId);
    await ctx.guard(async () => {
      await ctx.api.updateQuest(id, readQuestForm(form));
      dialog.close();
      toast("Quest updated. Schedule changes apply from the next period.", "success");
      await ctx.refresh("quests", "board", "log");
    });
  });

  async function open(questId) {
    const quest = await ctx.api.quest(questId);
    dialog.innerHTML = `
      <form method="dialog" data-quest-id="${quest.id}">
        <div class="spread">
          <h2>Edit quest #${quest.id}</h2>
          <span class="pill">${esc(quest.schedule.label)}</span>
        </div>
        ${questForm(quest)}
        <div class="row" style="margin-top:0.9rem">
          <button class="btn primary" type="submit">Save changes</button>
          <button class="btn ghost" type="button" data-action="cancel">Cancel</button>
        </div>
      </form>`;
    syncScheduleFields(dialog.querySelector("form"));
    dialog.showModal();
  }

  return { open };
}
