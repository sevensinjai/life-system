/** What has a period open right now. */

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { EmptyState } from "@/components/empty-state"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { QuestCard } from "@/features/quests/quest-card"
import { QuestSheet, type QuestSheetTarget } from "@/features/quests/quest-sheet"
import { useApi } from "@/hooks/use-api"
import { queryKeys } from "@/lib/query-keys"

export function BoardView() {
  const { api } = useApi()
  const [target, setTarget] = useState<QuestSheetTarget | null>(null)

  const board = useQuery({ queryKey: queryKeys.board, queryFn: () => api.board() })

  return (
    <div className="grid gap-3">
      <div className="flex items-baseline justify-between">
        <h2 className="text-lg font-semibold">Today</h2>
        <Badge variant="outline" className="font-mono text-xs">
          {board.data?.length ?? 0} open
        </Badge>
      </div>
      <p className="text-muted-foreground -mt-2 text-sm">
        Everything with a period open right now, ordered by deadline.
      </p>

      {board.isLoading && <Skeleton className="h-40 w-full" />}
      {board.data?.length === 0 && (
        <EmptyState>Nothing open. Author a quest, or run the daily reset.</EmptyState>
      )}
      {board.data?.map((quest) => (
        <QuestCard
          key={quest.id}
          quest={quest}
          onEdit={(target) => setTarget({ mode: "edit", quest: target })}
        />
      ))}

      <QuestSheet target={target} onOpenChange={(open) => !open && setTarget(null)} />
    </div>
  )
}
