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
