/**
 * Query keys in one place.
 *
 * Mutations invalidate by prefix — completing a quest touches the board, the
 * quest list, the status window, and the log — so the keys are grouped by the
 * resource they read rather than by the screen that shows them.
 */

export const queryKeys = {
  health: ["health"] as const,
  account: ["account"] as const,
  status: ["status"] as const,
  quests: ["quests"] as const,
  questList: (filters: Record<string, unknown>) => ["quests", "list", filters] as const,
  board: ["quests", "board"] as const,
  quest: (id: number) => ["quests", "detail", id] as const,
  quotes: ["quotes"] as const,
  quoteList: (includeArchived: boolean) => ["quotes", "list", includeArchived] as const,
  quoteToday: ["quotes", "today"] as const,
  constellations: ["constellations"] as const,
  constellation: (code: string) => ["constellations", code] as const,
  sideQuests: ["side-quests"] as const,
  sideQuestOffer: (id: number) => ["side-quests", id] as const,
  system: ["system"] as const,
  events: (filters: Record<string, unknown>) => ["system", "events", filters] as const,
  penalties: ["system", "penalties"] as const,
}

/** Everything a quest action can move. */
export const PROGRESSION_KEYS = [
  queryKeys.quests,
  queryKeys.status,
  queryKeys.system,
] as const

/**
 * Everything a trial of admission can move.
 *
 * Clearing one pays EXP and settles the friendship behind it, so the status
 * window and the pantheon both go stale along with the offer itself.
 */
export const TRIAL_KEYS = [
  queryKeys.sideQuests,
  queryKeys.constellations,
  queryKeys.status,
  queryKeys.system,
] as const
