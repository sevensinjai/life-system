/**
 * Quest form state, kept apart from the component that renders it.
 *
 * Held as strings and converted on submit: number inputs are text until they
 * are not, and the schedule fields only mean something once `kind` is known.
 * Nothing here touches React, so the same conversion serves any UI.
 */

import {
  type Quest,
  type QuestDifficulty,
  type QuestPayload,
  type ScheduleKind,
  type StatName,
} from "@/lib/types"

export const NO_STAT = "none"

export interface QuestFormState {
  title: string
  description: string
  difficulty: QuestDifficulty
  targetCount: string
  unit: string
  unitsPerMinute: string
  practiceMinutes: string
  statReward: StatName | typeof NO_STAT
  statRewardAmount: string
  kind: ScheduleKind
  days: number[]
  intervalDays: string
  weekStart: string
  anchor: string
}

export function emptyQuestForm(): QuestFormState {
  return {
    title: "",
    description: "",
    difficulty: "E",
    targetCount: "1",
    unit: "",
    unitsPerMinute: "",
    practiceMinutes: "10",
    statReward: NO_STAT,
    statRewardAmount: "0",
    kind: "once",
    days: [],
    intervalDays: "2",
    weekStart: "0",
    anchor: "",
  }
}

export function questToForm(quest: Quest): QuestFormState {
  return {
    title: quest.title,
    description: quest.description ?? "",
    difficulty: quest.difficulty,
    targetCount: String(quest.target_count),
    unit: quest.unit ?? "",
    unitsPerMinute: quest.units_per_minute?.toString() ?? "",
    practiceMinutes: String(quest.practice_minutes),
    statReward: quest.stat_reward ?? NO_STAT,
    statRewardAmount: String(quest.stat_reward_amount),
    kind: quest.schedule.kind,
    days: quest.schedule.days ?? [],
    intervalDays: String(quest.schedule.interval_days ?? 2),
    weekStart: String(quest.schedule.week_start ?? 0),
    anchor: quest.schedule.anchor ?? "",
  }
}

export function formToPayload(form: QuestFormState): QuestPayload {
  const schedule: QuestPayload["schedule"] = { kind: form.kind }
  if (form.kind === "weekdays") schedule.days = [...form.days].sort((a, b) => a - b)
  if (form.kind === "interval") schedule.interval_days = Number(form.intervalDays) || 1
  if (form.kind === "weekly") schedule.week_start = Number(form.weekStart) || 0
  if (form.anchor) schedule.anchor = form.anchor

  const payload: QuestPayload = {
    title: form.title.trim(),
    description: form.description.trim() || null,
    schedule,
    difficulty: form.difficulty,
    target_count: Number(form.targetCount) || 1,
    unit: form.unit.trim() || null,
    practice_minutes: Math.max(1, Number(form.practiceMinutes) || 1),
    stat_reward: form.statReward === NO_STAT ? null : form.statReward,
    stat_reward_amount: Number(form.statRewardAmount) || 0,
  }

  if (form.unitsPerMinute.trim()) {
    payload.units_per_minute = Number(form.unitsPerMinute)
    payload.practice_minutes = Math.max(
      1,
      Math.ceil(payload.target_count / payload.units_per_minute)
    )
  }

  return payload
}
