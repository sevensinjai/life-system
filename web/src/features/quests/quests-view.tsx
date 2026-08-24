/** Author quests, and everything you have authored. */

import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { EmptyState } from "@/components/empty-state"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
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
import { QuestEditDialog } from "@/features/quests/quest-edit-dialog"
import { QuestFields } from "@/features/quests/quest-form"
import {
  emptyQuestForm,
  formToPayload,
  type QuestFormState,
} from "@/features/quests/quest-form-state"
import { useApi } from "@/hooks/use-api"
import { PROGRESSION_KEYS, queryKeys } from "@/lib/query-keys"
import { SCHEDULE_KINDS, type Quest, type ScheduleKind } from "@/lib/types"

const ANY_SCHEDULE = "all"

export function QuestsView() {
  const { api } = useApi()
  const queryClient = useQueryClient()

  const [form, setForm] = useState<QuestFormState>(emptyQuestForm)
  const [editing, setEditing] = useState<Quest | null>(null)
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

  const create = useMutation({
    mutationFn: () => api.createQuest(formToPayload(form)),
    onSuccess: (quest) => {
      toast.success(`"${quest.title}" added to your board.`)
      setForm(emptyQuestForm())
      void Promise.all(
        PROGRESSION_KEYS.map((key) => queryClient.invalidateQueries({ queryKey: key }))
      )
    },
  })

  return (
    <>
      <div className="grid items-start gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Author a quest</CardTitle>
            <CardDescription>
              You are the designer and the player. Its first period opens immediately if
              the schedule falls on today.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form
              className="grid gap-4"
              onSubmit={(event) => {
                event.preventDefault()
                create.mutate()
              }}
            >
              <QuestFields value={form} onChange={setForm} idPrefix="new-quest" />
              <div className="flex gap-2">
                <Button type="submit" disabled={create.isPending}>
                  Create quest
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setForm(emptyQuestForm())}
                >
                  Reset form
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Your quests</CardTitle>
            <CardDescription>Archived quests keep their history.</CardDescription>
            <CardAction>
              <Badge variant="outline" className="font-mono text-xs">
                {quests.data?.length ?? 0}
              </Badge>
            </CardAction>
          </CardHeader>
          <CardContent className="grid gap-3">
            <div className="flex flex-wrap items-center gap-4">
              <Select
                value={filters.schedule}
                onValueChange={(value) =>
                  setFilters({
                    ...filters,
                    schedule: value as ScheduleKind | typeof ANY_SCHEDULE,
                  })
                }
              >
                <SelectTrigger size="sm" className="w-36" aria-label="Filter by schedule">
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

            {quests.isLoading && <Skeleton className="h-32 w-full" />}
            {quests.data?.length === 0 && (
              <EmptyState>No quests match. Author one on the left.</EmptyState>
            )}
            {quests.data?.map((quest) => (
              <QuestCard key={quest.id} quest={quest} onEdit={setEditing} />
            ))}
          </CardContent>
        </Card>
      </div>

      <QuestEditDialog quest={editing} onOpenChange={(open) => !open && setEditing(null)} />
    </>
  )
}
