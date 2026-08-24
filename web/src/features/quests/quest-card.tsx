/** One quest, with its open period and whatever you can do to it right now. */

import { useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import { useQuestActions } from "@/features/quests/use-quest-actions"
import { cn } from "@/lib/utils"
import { formatDate, percent } from "@/lib/format"
import type { Quest } from "@/lib/types"

export function QuestCard({
  quest,
  onEdit,
  showSchedule = true,
}: {
  quest: Quest
  onEdit: (quest: Quest) => void
  showSchedule?: boolean
}) {
  const { progress, complete, archive, restore } = useQuestActions()
  const [amount, setAmount] = useState("1")

  const instance = quest.current_instance
  // Only an active period takes progress; a cleared or failed one is history
  // the API refuses to touch, so it gets a badge instead of buttons.
  const open = instance?.status === "active"
  const busy = progress.isPending || complete.isPending

  const facts = [
    `${quest.exp_reward} EXP`,
    quest.stat_reward ? `+${quest.stat_reward_amount} ${quest.stat_reward}` : null,
    showSchedule ? quest.schedule.label : null,
    quest.unit ? `${quest.target_count} ${quest.unit}` : null,
  ].filter(Boolean)

  return (
    <article className={cn("rounded-lg border p-4", !quest.is_active && "opacity-60")}>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className={cn(
              "size-6 justify-center rounded-md p-0 font-mono font-bold",
              "ABS".includes(quest.difficulty) && "border-chart-4/60 text-chart-4"
            )}
          >
            {quest.difficulty}
          </Badge>
          <h3 className="font-medium">{quest.title}</h3>
          {!quest.is_active && (
            <Badge variant="secondary" className="text-xs">
              archived
            </Badge>
          )}
        </div>
        <Badge variant="ghost" className="text-muted-foreground font-mono text-xs">
          #{quest.id}
        </Badge>
      </div>

      {quest.description && (
        <p className="text-muted-foreground mt-1 text-sm">{quest.description}</p>
      )}

      <p className="text-muted-foreground mt-1 font-mono text-xs">{facts.join(" · ")}</p>

      {instance ? (
        <div className="mt-3 grid gap-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-mono">
              {instance.progress} / {instance.target_count}
              {quest.unit ? ` ${quest.unit}` : ""}
            </span>
            <span className="text-muted-foreground">
              {open
                ? instance.period_end
                  ? `due ${formatDate(instance.period_end)}`
                  : "no deadline"
                : instance.status === "completed"
                  ? "cleared"
                  : "failed"}
            </span>
          </div>
          <Progress
            value={percent(instance.progress, instance.target_count)}
            className={cn(!open && instance.status === "completed" && "[&>*]:bg-chart-3")}
          />
          {!open && quest.next_due_date && (
            <p className="text-muted-foreground text-xs">
              Next period {formatDate(quest.next_due_date)}.
            </p>
          )}
        </div>
      ) : (
        <p className="text-muted-foreground mt-2 text-sm">
          No open period.{" "}
          {quest.next_due_date ? `Next due ${formatDate(quest.next_due_date)}.` : "Waiting."}
        </p>
      )}

      <div className="mt-3 flex flex-wrap items-center gap-2">
        {open && (
          <>
            <Button
              size="sm"
              variant="secondary"
              disabled={busy}
              onClick={() => progress.mutate({ id: quest.id, amount: 1 })}
            >
              +1
            </Button>
            <Input
              aria-label={`Progress amount for ${quest.title}`}
              data-testid={`amount-${quest.id}`}
              type="number"
              className="h-8 w-20 font-mono"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
            />
            <Button
              size="sm"
              variant="secondary"
              disabled={busy}
              onClick={() =>
                progress.mutate({ id: quest.id, amount: Number(amount) || 1 })
              }
            >
              Add
            </Button>
            <Button size="sm" disabled={busy} onClick={() => complete.mutate(quest.id)}>
              Complete
            </Button>
          </>
        )}
        <Button size="sm" variant="ghost" onClick={() => onEdit(quest)}>
          Edit
        </Button>
        {quest.is_active ? (
          <Button
            size="sm"
            variant="ghost"
            className="text-destructive hover:text-destructive"
            disabled={archive.isPending}
            onClick={() => archive.mutate(quest.id)}
          >
            Archive
          </Button>
        ) : (
          <Button
            size="sm"
            variant="ghost"
            disabled={restore.isPending}
            onClick={() => restore.mutate(quest.id)}
          >
            Restore
          </Button>
        )}
      </div>
    </article>
  )
}
