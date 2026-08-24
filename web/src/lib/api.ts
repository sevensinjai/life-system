/**
 * The System API client.
 *
 * Deliberately free of React, the DOM, and any browser global beyond `fetch`:
 * storage is injected, so the same file runs under React Native with an
 * AsyncStorage-backed store. Everything above this layer is replaceable UI.
 */

import type {
  Account,
  BulkQuoteResult,
  DailyQuote,
  DailyReset,
  Health,
  Penalty,
  PlayerStatus,
  Quest,
  QuestAction,
  QuestPayload,
  Quote,
  QuoteDraft,
  StatBlock,
  SystemEvent,
  TokenResponse,
} from "./types"

export interface KeyValueStore {
  get(key: string): string | null
  set(key: string, value: string | null): void
}

export interface ValidationDetail {
  loc: (string | number)[]
  msg: string
  type: string
}

/** A failure carrying the API's error envelope, or a network failure as 0. */
export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details: ValidationDetail[]

  constructor(status: number, code: string, message: string, details: ValidationDetail[] = []) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.code = code
    this.details = details
  }

  get unauthenticated() {
    return this.status === 401
  }

  /** The message plus any field-level detail, ready to show. */
  get fullMessage() {
    if (!this.details.length) return this.message
    const fields = this.details
      .map((detail) => `${detail.loc.slice(1).join(".")}: ${detail.msg}`)
      .filter(Boolean)
    return fields.length ? `${this.message} (${fields.join("; ")})` : this.message
  }
}

/** One recorded request/response pair, for the Requests tab. */
export interface Exchange {
  id: number
  at: number
  method: string
  path: string
  status: number
  ms: number
  request: unknown
  response: unknown
}

const TOKEN_KEY = "system.token"
const BASE_KEY = "system.api_base"
const EXCHANGE_LIMIT = 60

type Query = Record<string, string | number | boolean | undefined | null>

interface RequestOptions {
  body?: unknown
  query?: Query
  auth?: boolean
}

export class ApiClient {
  private store: KeyValueStore
  private origin: string
  private listeners = new Set<() => void>()
  private unauthorizedListeners = new Set<() => void>()
  private nextId = 1

  baseUrl: string
  token: string | null
  exchanges: readonly Exchange[] = []

  constructor(store: KeyValueStore, origin: string) {
    this.store = store
    this.origin = origin
    this.baseUrl = store.get(BASE_KEY) ?? ""
    this.token = store.get(TOKEN_KEY)
  }

  get authenticated() {
    return Boolean(this.token)
  }

  /** Where requests actually go: the configured base, else the serving origin. */
  get effectiveBase() {
    return this.baseUrl || this.origin
  }

  setBaseUrl(baseUrl: string) {
    this.baseUrl = baseUrl.trim().replace(/\/+$/, "")
    this.store.set(BASE_KEY, this.baseUrl || null)
    this.emit()
  }

  setToken(token: string | null) {
    this.token = token
    this.store.set(TOKEN_KEY, token)
    this.emit()
  }

  // --- exchange log, shaped for useSyncExternalStore ----------------------

  subscribe = (listener: () => void) => {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }

  getExchanges = () => this.exchanges

  /**
   * Called when the API rejects the token.
   *
   * The rule "a 401 means sign out" belongs with the thing that saw the 401,
   * not scattered across every caller.
   */
  onUnauthorized(listener: () => void) {
    this.unauthorizedListeners.add(listener)
    return () => {
      this.unauthorizedListeners.delete(listener)
    }
  }

  clearExchanges() {
    this.exchanges = []
    this.emit()
  }

  private emit() {
    this.listeners.forEach((listener) => listener())
  }

  private record(exchange: Exchange) {
    this.exchanges = [exchange, ...this.exchanges].slice(0, EXCHANGE_LIMIT)
    this.emit()
  }

  // --- the one call every endpoint goes through ---------------------------

  async request<T>(method: string, path: string, options: RequestOptions = {}): Promise<T> {
    const { body, query, auth = true } = options
    // Concatenated rather than resolved, so a base that carries a path prefix
    // ("https://host/api") keeps it.
    const url = new URL(`${this.effectiveBase}${path}`)
    for (const [key, value] of Object.entries(query ?? {})) {
      if (value === undefined || value === null || value === "") continue
      url.searchParams.set(key, String(value))
    }

    const headers: Record<string, string> = { Accept: "application/json" }
    if (body !== undefined) headers["Content-Type"] = "application/json"
    if (auth && this.token) headers.Authorization = `Bearer ${this.token}`

    const started = Date.now()
    const base: Omit<Exchange, "status" | "ms" | "response"> = {
      id: this.nextId++,
      at: started,
      method,
      path: `${url.pathname}${url.search}`,
      request: body ?? null,
    }

    let response: Response
    try {
      response = await fetch(url.toString(), {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
      })
    } catch (cause) {
      this.record({ ...base, status: 0, ms: Date.now() - started, response: String(cause) })
      throw new ApiError(
        0,
        "network_error",
        `Could not reach ${url.origin}. Is the API running, and does its CORS policy allow this page?`
      )
    }

    const text = await response.text()
    let payload: unknown = null
    if (text) {
      try {
        payload = JSON.parse(text)
      } catch {
        payload = text
      }
    }

    this.record({ ...base, status: response.status, ms: Date.now() - started, response: payload })

    if (!response.ok) {
      if (response.status === 401 && this.token) {
        this.unauthorizedListeners.forEach((listener) => listener())
      }
      const envelope = (payload as { error?: { code?: string; message?: string; details?: ValidationDetail[] } })?.error
      throw new ApiError(
        response.status,
        envelope?.code ?? "http_error",
        envelope?.message ?? `Request failed with ${response.status}.`,
        envelope?.details ?? []
      )
    }

    return payload as T
  }

  // --- endpoints ----------------------------------------------------------

  health = () => this.request<Health>("GET", "/health", { auth: false })

  register = (payload: {
    email: string
    password: string
    name: string
    timezone: string
  }) => this.request<TokenResponse>("POST", "/auth/register", { body: payload, auth: false })

  login = (payload: { email: string; password: string }) =>
    this.request<TokenResponse>("POST", "/auth/login", { body: payload, auth: false })

  account = () => this.request<Account>("GET", "/auth/me")

  status = () => this.request<PlayerStatus>("GET", "/players/me")

  updatePlayer = (payload: { name?: string; timezone?: string }) =>
    this.request<PlayerStatus>("PATCH", "/players/me", { body: payload })

  allocate = (payload: StatBlock) =>
    this.request<PlayerStatus>("POST", "/players/me/allocate", { body: payload })

  quests = (query?: Query) => this.request<Quest[]>("GET", "/quests", { query })

  board = () => this.request<Quest[]>("GET", "/quests/today")

  quest = (id: number) => this.request<Quest>("GET", `/quests/${id}`)

  createQuest = (payload: QuestPayload) =>
    this.request<Quest>("POST", "/quests", { body: payload })

  updateQuest = (id: number, payload: Partial<QuestPayload>) =>
    this.request<Quest>("PATCH", `/quests/${id}`, { body: payload })

  archiveQuest = (id: number) => this.request<Quest>("DELETE", `/quests/${id}`)

  logProgress = (id: number, amount: number) =>
    this.request<QuestAction>("POST", `/quests/${id}/progress`, { body: { amount } })

  completeQuest = (id: number) =>
    this.request<QuestAction>("POST", `/quests/${id}/complete`)

  quotes = (query?: Query) => this.request<Quote[]>("GET", "/quotes", { query })

  quoteOfTheDay = () => this.request<DailyQuote>("GET", "/quotes/today")

  createQuote = (payload: QuoteDraft) =>
    this.request<Quote>("POST", "/quotes", { body: payload })

  createQuotes = (quotes: QuoteDraft[]) =>
    this.request<BulkQuoteResult>("POST", "/quotes/bulk", { body: { quotes } })

  updateQuote = (id: number, payload: Partial<Quote>) =>
    this.request<Quote>("PATCH", `/quotes/${id}`, { body: payload })

  archiveQuote = (id: number) => this.request<Quote>("DELETE", `/quotes/${id}`)

  dailyReset = () => this.request<DailyReset>("POST", "/system/daily-reset")

  events = (query?: Query) => this.request<SystemEvent[]>("GET", "/system/events", { query })

  penalties = (query?: Query) =>
    this.request<Penalty[]>("GET", "/system/penalties", { query })
}

/** localStorage, guarded so a blocked store degrades to in-memory. */
export function browserStore(): KeyValueStore {
  const memory = new Map<string, string>()
  return {
    get(key) {
      try {
        return window.localStorage.getItem(key)
      } catch {
        return memory.get(key) ?? null
      }
    },
    set(key, value) {
      try {
        if (value === null) window.localStorage.removeItem(key)
        else window.localStorage.setItem(key, value)
      } catch {
        if (value === null) memory.delete(key)
        else memory.set(key, value)
      }
    },
  }
}
