/**
 * The API's response shapes, mirroring app/schemas on the server.
 *
 * Hand-written rather than generated so the client stays dependency-free and
 * readable; `/openapi.json` is the source of truth if the two ever disagree.
 */

export type ScheduleKind = "once" | "daily" | "weekdays" | "interval" | "weekly"
export type QuestDifficulty = "E" | "D" | "C" | "B" | "A" | "S"
export type QuestStatus = "active" | "completed" | "failed"
export type StatName =
  | "strength"
  | "agility"
  | "vitality"
  | "intelligence"
  | "perception"
export type Standing =
  | "forsaken"
  | "slighted"
  | "stranger"
  | "noticed"
  | "favored"
  | "champion"
export type FriendshipStatus =
  | "challenged"
  | "accepted"
  | "refused"
  | "failed"
  | "withdrawn"
/** Why a request to be befriended would not be heard right now. */
export type BlockedBy = "already_friends" | "request_open" | "too_soon" | "retired"
export type SideQuestOfferStatus =
  | "offered"
  | "accepted"
  | "declined"
  | "completed"
  | "failed"
  | "expired"
  | "withdrawn"
export type EventType =
  | "quest_created"
  | "quest_progress"
  | "quest_completed"
  | "quest_failed"
  | "level_up"
  | "stats_allocated"
  | "penalty_applied"
  | "daily_reset"

export const DIFFICULTIES: QuestDifficulty[] = ["E", "D", "C", "B", "A", "S"]
export const SCHEDULE_KINDS: ScheduleKind[] = [
  "once",
  "daily",
  "weekdays",
  "interval",
  "weekly",
]
export const STAT_NAMES: StatName[] = [
  "strength",
  "agility",
  "vitality",
  "intelligence",
  "perception",
]
export const EVENT_TYPES: EventType[] = [
  "quest_created",
  "quest_progress",
  "quest_completed",
  "quest_failed",
  "level_up",
  "stats_allocated",
  "penalty_applied",
  "daily_reset",
]
/** 0 is Monday, matching the API. */
export const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

export interface Health {
  status: string
  service: string
  version: string
  environment: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface Account {
  id: number
  email: string
  created_at: string
}

export interface StatBlock {
  strength: number
  agility: number
  vitality: number
  intelligence: number
  perception: number
}

export interface PlayerStatus {
  id: number
  name: string
  level: number
  exp: number
  exp_to_next_level: number
  exp_progress: number
  total_exp_earned: number
  stat_points: number
  stats: StatBlock
  timezone: string
}

export interface ScheduleSpec {
  kind: ScheduleKind
  days?: number[] | null
  interval_days?: number | null
  anchor?: string | null
  week_start?: number
}

export interface ScheduleResponse extends ScheduleSpec {
  week_start: number
  label: string
}

export interface QuestInstance {
  id: number
  quest_id: number
  period_start: string
  period_end: string | null
  progress: number
  target_count: number
  status: QuestStatus
  completed_at: string | null
}

export interface Quest {
  id: number
  title: string
  description: string | null
  schedule: ScheduleResponse
  difficulty: QuestDifficulty
  target_count: number
  unit: string | null
  exp_reward: number
  stat_reward: StatName | null
  stat_reward_amount: number
  is_active: boolean
  created_at: string
  current_instance: QuestInstance | null
  next_due_date: string | null
}

export interface QuestAction {
  quest: Quest
  instance: QuestInstance
  completed: boolean
  exp_gained: number
  leveled_up: boolean
}

export interface QuestPayload {
  title: string
  description?: string | null
  schedule: ScheduleSpec
  difficulty: QuestDifficulty
  target_count: number
  unit?: string | null
  exp_reward?: number
  stat_reward?: StatName | null
  stat_reward_amount: number
  is_active?: boolean
}

export interface Quote {
  id: number
  text: string
  author: string | null
  is_active: boolean
  created_at: string
}

export interface QuoteDraft {
  text: string
  author?: string | null
}

export interface BulkQuoteResult {
  created: Quote[]
  created_count: number
  skipped_count: number
  skipped: string[]
}

export interface DailyQuote {
  local_date: string
  quote: Quote | null
  pool_size: number
  refresh_after: string
}

export interface SystemEvent {
  id: number
  event_type: EventType
  message: string
  payload: Record<string, unknown>
  created_at: string
}

export interface Penalty {
  id: number
  reason: string
  exp_lost: number
  created_at: string
}

export interface DailyReset {
  reset_date: string
  failed_count: number
  spawned_count: number
  total_exp_lost: number
}


// --- the pantheon --------------------------------------------------------

export interface StandingBlock {
  standing: Standing
  favor: number
  offers_received: number
  completed: number
  declined: number
  expired: number
  failed: number
  first_seen_at: string | null
  last_seen_at: string | null
}

export interface FriendshipBlock {
  is_friend: boolean
  befriended_at: string | null
  may_ask: boolean
  blocked_by: BlockedBy | null
  retry_after: string | null
  request_status: FriendshipStatus | null
  challenge_offer_id: number | null
}

export interface Constellation {
  code: string
  name: string
  epithet: string | null
  description: string | null
  domain: StatName | null
  standing: StandingBlock
  friendship: FriendshipBlock
}

/** A constellation's answer, given at once. */
export interface FriendshipRequestResult {
  status: FriendshipStatus
  constellation: string
  line: string | null
  retry_after: string | null
  challenge_offer_id: number | null
}

export interface ConstellationBrief {
  code: string
  name: string
  epithet: string | null
  domain: StatName | null
}

export interface SideQuest {
  id: number
  title: string
  description: string | null
  constellation: ConstellationBrief | null
  difficulty: QuestDifficulty
  target_count: number
  unit: string | null
  exp_reward: number
  stat_reward: StatName | null
  stat_reward_amount: number
  penalty_exp: number
  status: string
  broadcast_at: string
  expires_at: string | null
  min_standing: Standing | null
}

export interface SideQuestOffer {
  id: number
  status: SideQuestOfferStatus
  progress: number
  target_count: number
  expires_at: string | null
  offered_at: string
  responded_at: string | null
  completed_at: string | null
  side_quest: SideQuest
}

export interface SideQuestProgressResult {
  offer: SideQuestOffer
  completed: boolean
}

/** Ordered worst to best, which is also how the meter reads. */
export const STANDINGS: Standing[] = [
  "forsaken",
  "slighted",
  "stranger",
  "noticed",
  "favored",
  "champion",
]
