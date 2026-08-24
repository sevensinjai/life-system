/**
 * Bootstrap for the web client.
 *
 * Owns the things every view shares: the API client, the signed-in/out
 * switch, tab activation, and one error handler so a failed call always ends
 * as a toast rather than a silent rejection.
 */

import { Api, ApiError } from "./api.js";
import { localTimezone, qs, qsa, toast, toastError } from "./dom.js";
import { createStatusView } from "./views/status.js";
import { createBoardView, createQuestEditor, createQuestsView } from "./views/quests.js";
import { createQuotesView } from "./views/quotes.js";
import { createLogView } from "./views/log.js";
import { createRequestsView } from "./views/requests.js";

const DEFAULT_TAB = "status";

const api = new Api();
const views = new Map();
let activeTab = DEFAULT_TAB;

/** Run an API call, turning any failure into a toast. Reports success. */
async function guard(action) {
  try {
    await action();
    return true;
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.unauthenticated) {
        signOut({ silent: true });
        toast("Session expired. Log in again.", "error");
      } else {
        toastError(error);
      }
      return false;
    }
    console.error(error);
    toast(String(error?.message ?? error), "error");
    return false;
  }
}

/**
 * Refresh views by id.
 *
 * Only the visible one reloads immediately; the rest are marked stale and
 * reload when their tab is opened, so a quest completion does not fan out
 * into five requests.
 */
async function refresh(...ids) {
  for (const id of ids) {
    const entry = views.get(id);
    if (!entry) continue;
    if (id === activeTab && !qs(`#view-${id}`).hidden) {
      await guard(entry.view.refresh);
    } else {
      entry.stale = true;
    }
  }
}

const ctx = {
  api,
  guard,
  refresh,
  editQuest: (id) => guard(() => questEditor.open(id)),
};

const questEditor = createQuestEditor(ctx);

function register(id, view) {
  views.set(id, { view, stale: true });
}

register("status", createStatusView(ctx));
register("board", createBoardView(ctx));
register("quests", createQuestsView(ctx));
register("quotes", createQuotesView(ctx));
register("log", createLogView(ctx));
register("requests", createRequestsView(ctx));

async function activate(tab) {
  activeTab = tab;
  for (const [id] of views) {
    qs(`#view-${id}`).hidden = id !== tab;
  }
  for (const button of qsa(".tab")) {
    button.setAttribute("aria-selected", String(button.dataset.tab === tab));
  }
  localStorage.setItem("system.tab", tab);

  const entry = views.get(tab);
  if (entry.stale) {
    entry.stale = false;
    // A failed reload leaves the tab stale so the next visit retries it.
    entry.stale = !(await guard(entry.view.refresh));
  }
}

// --- signed in / signed out ------------------------------------------------

function showWorkspace() {
  qs("#auth").hidden = true;
  qs("#workspace").hidden = false;
  qs("#sign-out").hidden = false;
}

function signOut({ silent = false } = {}) {
  api.setToken(null);
  for (const entry of views.values()) {
    entry.stale = true;
    entry.view.clear();
  }
  qs("#workspace").hidden = true;
  qs("#sign-out").hidden = true;
  qs("#auth").hidden = false;
  if (!silent) toast("Signed out.");
}

async function signIn(token) {
  api.setToken(token);
  for (const entry of views.values()) entry.stale = true;
  showWorkspace();
  await activate(activeTab);
}

// --- connection ------------------------------------------------------------

async function checkHealth() {
  const pill = qs("#health");
  pill.className = "pill pending";
  pill.textContent = "checking…";
  try {
    const health = await api.health();
    pill.className = "pill ok";
    pill.textContent = `${health.service} ${health.version} · ${health.environment}`;
  } catch (error) {
    pill.className = "pill bad";
    pill.textContent = "unreachable";
    if (error instanceof ApiError) toastError(error);
  }
}

function wireTopbar() {
  qs("#api-base").value = api.base;

  qs("#api-base-save").addEventListener("click", async () => {
    api.setBase(qs("#api-base").value);
    qs("#api-base").value = api.base;
    await checkHealth();
    if (api.authenticated) {
      for (const entry of views.values()) entry.stale = true;
      await activate(activeTab);
    }
  });

  qs("#api-base").addEventListener("keydown", (event) => {
    if (event.key === "Enter") qs("#api-base-save").click();
  });

  qs("#sign-out").addEventListener("click", () => signOut());

  qs("#refresh-all").addEventListener("click", async () => {
    for (const entry of views.values()) entry.stale = true;
    const entry = views.get(activeTab);
    entry.stale = false;
    await guard(entry.view.refresh);
  });

  for (const button of qsa(".tab")) {
    button.addEventListener("click", () => activate(button.dataset.tab));
  }
}

function wireAuthForms() {
  qs("#register-form").timezone.value = localTimezone();

  qs("#login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    await guard(async () => {
      const token = await api.login({
        email: form.email.value.trim(),
        password: form.password.value,
      });
      form.reset();
      toast("Welcome back.", "success");
      await signIn(token.access_token);
    });
  });

  qs("#register-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.target;
    await guard(async () => {
      const token = await api.register({
        email: form.email.value.trim(),
        password: form.password.value,
        name: form.name.value.trim(),
        timezone: form.timezone.value.trim(),
      });
      form.reset();
      form.timezone.value = localTimezone();
      toast("Player created. The System is watching.", "success");
      await signIn(token.access_token);
    });
  });
}

async function main() {
  wireTopbar();
  wireAuthForms();

  const remembered = localStorage.getItem("system.tab");
  if (remembered && views.has(remembered)) activeTab = remembered;

  await checkHealth();

  if (api.authenticated) {
    showWorkspace();
    await activate(activeTab);
  } else {
    qs("#auth").hidden = false;
  }
}

main();
