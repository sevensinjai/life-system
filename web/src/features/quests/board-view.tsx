/** What has a period open right now. */

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { EmptyState } from "@/components/empty-state"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { QuestCard } from "@/features/quests/quest-card"
import { QuestEditDialog } from "@/features/quests/quest-edit-dialog"
import { useApi } from "@/hooks/use-api"
import { queryKeys } from "@/lib/query-keys"
import type { Quest } from "@/lib/types"

export function BoardView() {
  const { api } = useApi()
  const [editing, setEditing] = useState<Quest | null>(null)

  const board = useQuery({ queryKey: queryKeys.board, queryFn: () => api.board() })

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>On the board today</CardTitle>
          <CardDescription>
            Everything with a period open right now, ordered by deadline. Run the daily
            reset on the Status tab first if periods look stale.
          </CardDescription>
          <CardAction>
            <Badge variant="outline" className="font-mono text-xs">
              {board.data?.length ?? 0} open
            </Badge>
          </CardAction>
        </CardHeader>
        <CardContent className="grid gap-3">
          {board.isLoading && <Skeleton className="h-32 w-full" />}
          {board.data?.length === 0 && (
            <EmptyState>Nothing open. Author a quest, or run the daily reset.</EmptyState>
          )}
          {board.data?.map((quest) => (
            <QuestCard key={quest.id} quest={quest} onEdit={setEditing} />
          ))}
        </CardContent>
      </Card>

      <QuestEditDialog quest={editing} onOpenChange={(open) => !open && setEditing(null)} />
    </>
  )
}
