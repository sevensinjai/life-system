/** The quest authoring form, shared by "create" and the edit dialog. */

import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { NO_STAT, type QuestFormState } from "@/features/quests/quest-form-state"
import {
  DAY_NAMES,
  DIFFICULTIES,
  SCHEDULE_KINDS,
  STAT_NAMES,
  type QuestDifficulty,
  type ScheduleKind,
  type StatName,
} from "@/lib/types"

export function QuestFields({
  value,
  onChange,
  idPrefix,
}: {
  value: QuestFormState
  onChange: (next: QuestFormState) => void
  idPrefix: string
}) {
  const set = <K extends keyof QuestFormState>(key: K, next: QuestFormState[K]) =>
    onChange({ ...value, [key]: next })

  const id = (name: string) => `${idPrefix}-${name}`

  return (
    <div className="grid gap-4">
      <div className="grid gap-2">
        <Label htmlFor={id("title")}>Title</Label>
        <Input
          id={id("title")}
          maxLength={200}
          required
          value={value.title}
          onChange={(event) => set("title", event.target.value)}
        />
      </div>

      <div className="grid gap-2">
        <Label htmlFor={id("description")}>Description</Label>
        <Input
          id={id("description")}
          value={value.description}
          onChange={(event) => set("description", event.target.value)}
        />
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="grid gap-2">
          <Label htmlFor={id("difficulty")}>Difficulty</Label>
          <Select
            value={value.difficulty}
            onValueChange={(next) => set("difficulty", next as QuestDifficulty)}
          >
            <SelectTrigger id={id("difficulty")} className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DIFFICULTIES.map((rank) => (
                <SelectItem key={rank} value={rank}>
                  {rank}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="grid gap-2">
          <Label htmlFor={id("target")}>Target count</Label>
          <Input
            id={id("target")}
            type="number"
            min={1}
            className="font-mono"
            value={value.targetCount}
            onChange={(event) => set("targetCount", event.target.value)}
          />
        </div>

        <div className="grid gap-2">
          <Label htmlFor={id("unit")}>Unit</Label>
          <Input
            id={id("unit")}
            maxLength={32}
            placeholder="reps"
            value={value.unit}
            onChange={(event) => set("unit", event.target.value)}
          />
        </div>

        <div className="grid gap-2">
          <Label htmlFor={id("minutes")}>Practice minutes</Label>
          <Input
            id={id("minutes")}
            type="number"
            min={1}
            required
            placeholder="10"
            className="font-mono"
            value={value.practiceMinutes}
            onChange={(event) => set("practiceMinutes", event.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="grid gap-2">
          <Label htmlFor={id("pace")}>Units per minute</Label>
          <Input
            id={id("pace")}
            type="number"
            min={0.01}
            step="any"
            placeholder="optional conversion"
            className="font-mono"
            value={value.unitsPerMinute}
            onChange={(event) => set("unitsPerMinute", event.target.value)}
          />
        </div>
        <p className="text-muted-foreground self-end pb-2 text-xs">
          {value.unitsPerMinute && Number(value.unitsPerMinute) > 0
            ? `${Math.max(1, Math.ceil((Number(value.targetCount) || 1) / Number(value.unitsPerMinute)))} minutes on completion`
            : "Set a pace for reps, pages, distance, or another count."}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="grid gap-2">
          <Label htmlFor={id("stat")}>Stat reward</Label>
          <Select
            value={value.statReward}
            onValueChange={(next) => set("statReward", next as StatName | typeof NO_STAT)}
          >
            <SelectTrigger id={id("stat")} className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={NO_STAT}>none</SelectItem>
              {STAT_NAMES.map((stat) => (
                <SelectItem key={stat} value={stat}>
                  {stat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="grid gap-2">
          <Label htmlFor={id("stat-amount")}>Stat amount</Label>
          <Input
            id={id("stat-amount")}
            type="number"
            min={0}
            className="font-mono"
            value={value.statRewardAmount}
            onChange={(event) => set("statRewardAmount", event.target.value)}
          />
        </div>
      </div>

      <fieldset className="grid gap-3 rounded-lg border p-3">
        <legend className="text-muted-foreground px-1 text-xs tracking-[0.12em] uppercase">
          Schedule
        </legend>

        <div className="grid grid-cols-2 gap-3">
          <div className="grid gap-2">
            <Label htmlFor={id("kind")}>Kind</Label>
            <Select
              value={value.kind}
              onValueChange={(next) => set("kind", next as ScheduleKind)}
            >
              <SelectTrigger id={id("kind")} className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SCHEDULE_KINDS.map((kind) => (
                  <SelectItem key={kind} value={kind}>
                    {kind}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {value.kind === "interval" && (
            <div className="grid gap-2">
              <Label htmlFor={id("interval")}>Every N days</Label>
              <Input
                id={id("interval")}
                type="number"
                min={1}
                max={365}
                className="font-mono"
                value={value.intervalDays}
                onChange={(event) => set("intervalDays", event.target.value)}
              />
            </div>
          )}

          {value.kind === "weekly" && (
            <div className="grid gap-2">
              <Label htmlFor={id("week-start")}>Week starts</Label>
              <Select
                value={value.weekStart}
                onValueChange={(next) => set("weekStart", next)}
              >
                <SelectTrigger id={id("week-start")} className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DAY_NAMES.map((day, index) => (
                    <SelectItem key={day} value={String(index)}>
                      {day}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          <div className="grid gap-2">
            <Label htmlFor={id("anchor")}>Anchor</Label>
            <Input
              id={id("anchor")}
              type="date"
              value={value.anchor}
              onChange={(event) => set("anchor", event.target.value)}
            />
          </div>
        </div>

        {value.kind === "weekdays" && (
          <div className="flex flex-wrap gap-3" data-testid="weekday-picker">
            {DAY_NAMES.map((day, index) => (
              <Label
                key={day}
                htmlFor={id(`day-${index}`)}
                className="flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-normal"
              >
                <Checkbox
                  id={id(`day-${index}`)}
                  checked={value.days.includes(index)}
                  onCheckedChange={(checked) =>
                    set(
                      "days",
                      checked
                        ? [...value.days, index]
                        : value.days.filter((day) => day !== index)
                    )
                  }
                />
                {day}
              </Label>
            ))}
          </div>
        )}
      </fieldset>
    </div>
  )
}
