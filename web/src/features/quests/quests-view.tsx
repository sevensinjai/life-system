/** Everything you have authored, and the button that adds another. */

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Plus } from "lucide-react"

import { EmptyState } from "@/components/empty-state"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { QuestCard } from "@/features/quests/quest-card"
import { QuestSheet, type QuestSheetTarget } from "@/features/quests/quest-sheet"
import { useApi } from "@/hooks/use-api"
import { queryKeys } from "@/lib/query-keys"
import { SCHEDULE_KINDS, type ScheduleKind } from "@/lib/types"

const ANY_SCHEDULE = "all"

export function QuestsView() {
  const { api } = useApi()
  const [target, setTarget] = useState<QuestSheetTarget | null>(null)
  const [filters, setFilters] = useState({
    schedule: ANY_SCHEDULE as ScheduleKind | typeof ANY_SCHEDULE,
    recurringOnly: false,
    includeArchived: false,
  })

  const query = {
    schedule: filters.schedule === ANY_SCHEDULE ? undefined : filters.schedule,
    recurring_only: filters.recurringOnly || undefined,
    include_archived: filters.includeArchived || undefined,
  }

  const quests = useQuery({
    queryKey: queryKeys.questList(query),
    queryFn: () => api.quests(query),
  })

  return (
    <div className="grid gap-3">
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-lg font-semibold">Quests</h2>
        <Button size="sm" onClick={() => setTarget({ mode: "create" })}>
          <Plus /> New
        </Button>
      </div>

      <div className="grid gap-2">
        <div className="flex items-center gap-2">
          <Select
            value={filters.schedule}
            onValueChange={(value) =>
              setFilters({
                ...filters,
                schedule: value as ScheduleKind | typeof ANY_SCHEDULE,
              })
            }
          >
            <SelectTrigger size="sm" className="flex-1" aria-label="Filter by schedule">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={ANY_SCHEDULE}>all schedules</SelectItem>
              {SCHEDULE_KINDS.map((kind) => (
                <SelectItem key={kind} value={kind}>
                  {kind}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Badge variant="outline" className="font-mono text-xs">
            {quests.data?.length ?? 0}
          </Badge>
        </div>

        <div className="flex flex-wrap gap-4">
          <Label htmlFor="recurring-only" className="text-muted-foreground text-xs font-normal">
            <Checkbox
              id="recurring-only"
              checked={filters.recurringOnly}
              onCheckedChange={(checked) =>
                setFilters({ ...filters, recurringOnly: checked === true })
              }
            />
            recurring only
          </Label>
          <Label htmlFor="include-archived" className="text-muted-foreground text-xs font-normal">
            <Checkbox
              id="include-archived"
              checked={filters.includeArchived}
              onCheckedChange={(checked) =>
                setFilters({ ...filters, includeArchived: checked === true })
              }
            />
            include archived
          </Label>
        </div>
      </div>

      {quests.isLoading && <Skeleton className="h-40 w-full" />}
      {quests.data?.length === 0 && (
        <EmptyState>No quests match. Tap New to author one.</EmptyState>
      )}
      {quests.data?.map((quest) => (
        <QuestCard
          key={quest.id}
          quest={quest}
          onEdit={(quest) => setTarget({ mode: "edit", quest })}
        />
      ))}

      <QuestSheet target={target} onOpenChange={(open) => !open && setTarget(null)} />
    </div>
  )
}
