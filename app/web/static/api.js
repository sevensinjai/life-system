/**
 * A thin client for the System API.
 *
 * Every request goes through `request()`, which unwraps the JSON error
 * envelope into an `ApiError` and records the exchange so the Requests tab can
 * show exactly what went over the wire — the point of a hand-testing client.
 */

const TOKEN_KEY = "system.token";
const BASE_KEY = "system.api_base";
const LOG_LIMIT = 60;

export class ApiError extends Error {
  constructor({ status, code, message, details }) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details ?? [];
  }

  get unauthenticated() {
    return this.status === 401;
  }
}

export class Api {
  constructor() {
    this.base = localStorage.getItem(BASE_KEY) ?? "";
    this.token = localStorage.getItem(TOKEN_KEY);
    this.exchanges = [];
    this._listeners = new Set();
    this._nextId = 1;
  }

  get authenticated() {
    return Boolean(this.token);
  }

  setBase(base) {
    this.base = (base ?? "").trim().replace(/\/+$/, "");
    if (this.base) localStorage.setItem(BASE_KEY, this.base);
    else localStorage.removeItem(BASE_KEY);
  }

  setToken(token) {
    this.token = token;
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  }

  /** Subscribe to completed exchanges; used by the Requests tab. */
  observe(listener) {
    this._listeners.add(listener);
    return () => this._listeners.delete(listener);
  }

  clearExchanges() {
    this.exchanges = [];
    this._listeners.forEach((listener) => listener(null));
  }

  url(path, query) {
    // Concatenated rather than resolved, so a base that includes a path
    // prefix ("https://host/api") keeps it.
    const origin = this.base || window.location.origin;
    const url = new URL(`${origin}${path}`);
    for (const [key, value] of Object.entries(query ?? {})) {
      if (value === undefined || value === null || value === "") continue;
      url.searchParams.set(key, value);
    }
    return url;
  }

  async request(method, path, { body, query, auth = true } = {}) {
    const url = this.url(path, query);
    const headers = { Accept: "application/json" };
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (auth && this.token) headers.Authorization = `Bearer ${this.token}`;

    const started = performance.now();
    const exchange = {
      id: this._nextId++,
      at: new Date(),
      method,
      path: `${url.pathname}${url.search}`,
      url: url.toString(),
      request: body ?? null,
      status: 0,
      ms: 0,
      response: null,
    };

    let response;
    try {
      response = await fetch(url, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
      });
    } catch (cause) {
      exchange.ms = Math.round(performance.now() - started);
      exchange.response = { error: String(cause) };
      this._record(exchange);
      throw new ApiError({
        status: 0,
        code: "network_error",
        message: `Could not reach ${url.origin}. Is the API running, and does its CORS policy allow this page?`,
      });
    }

    const text = await response.text();
    let payload = null;
    if (text) {
      try {
        payload = JSON.parse(text);
      } catch {
        payload = text;
      }
    }

    exchange.status = response.status;
    exchange.ms = Math.round(performance.now() - started);
    exchange.response = payload;
    this._record(exchange);

    if (!response.ok) {
      const envelope = (payload && payload.error) || {};
      throw new ApiError({
        status: response.status,
        code: envelope.code ?? "http_error",
        message: envelope.message ?? `Request failed with ${response.status}.`,
        details: envelope.details,
      });
    }

    return payload;
  }

  _record(exchange) {
    this.exchanges.unshift(exchange);
    if (this.exchanges.length > LOG_LIMIT) this.exchanges.length = LOG_LIMIT;
    this._listeners.forEach((listener) => listener(exchange));
  }

  // --- health -------------------------------------------------------------

  health() {
    return this.request("GET", "/health", { auth: false });
  }

  // --- auth ---------------------------------------------------------------

  register(payload) {
    return this.request("POST", "/auth/register", { body: payload, auth: false });
  }

  login(payload) {
    return this.request("POST", "/auth/login", { body: payload, auth: false });
  }

  account() {
    return this.request("GET", "/auth/me");
  }

  // --- player -------------------------------------------------------------

  status() {
    return this.request("GET", "/players/me");
  }

  updatePlayer(payload) {
    return this.request("PATCH", "/players/me", { body: payload });
  }

  allocate(payload) {
    return this.request("POST", "/players/me/allocate", { body: payload });
  }

  // --- quests -------------------------------------------------------------

  quests(query) {
    return this.request("GET", "/quests", { query });
  }

  board() {
    return this.request("GET", "/quests/today");
  }

  quest(id) {
    return this.request("GET", `/quests/${id}`);
  }

  createQuest(payload) {
    return this.request("POST", "/quests", { body: payload });
  }

  updateQuest(id, payload) {
    return this.request("PATCH", `/quests/${id}`, { body: payload });
  }

  archiveQuest(id) {
    return this.request("DELETE", `/quests/${id}`);
  }

  logProgress(id, amount) {
    return this.request("POST", `/quests/${id}/progress`, { body: { amount } });
  }

  completeQuest(id) {
    return this.request("POST", `/quests/${id}/complete`);
  }

  // --- quotes -------------------------------------------------------------

  quotes(query) {
    return this.request("GET", "/quotes", { query });
  }

  quoteOfTheDay() {
    return this.request("GET", "/quotes/today");
  }

  quote(id) {
    return this.request("GET", `/quotes/${id}`);
  }

  createQuote(payload) {
    return this.request("POST", "/quotes", { body: payload });
  }

  createQuotes(quotes) {
    return this.request("POST", "/quotes/bulk", { body: { quotes } });
  }

  updateQuote(id, payload) {
    return this.request("PATCH", `/quotes/${id}`, { body: payload });
  }

  archiveQuote(id) {
    return this.request("DELETE", `/quotes/${id}`);
  }

  // --- system -------------------------------------------------------------

  dailyReset() {
    return this.request("POST", "/system/daily-reset");
  }

  events(query) {
    return this.request("GET", "/system/events", { query });
  }

  penalties(query) {
    return this.request("GET", "/system/penalties", { query });
  }
}
