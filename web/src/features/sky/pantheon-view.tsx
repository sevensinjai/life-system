/**
 * The pantheon: who is watching, and whether they will have you.
 *
 * Nothing a constellation issues reaches you until it has befriended you, so
 * this is the screen the side-quest half of the game starts from.
 */

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { EmptyState } from "@/components/empty-state"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { BefriendSheet } from "@/features/sky/befriend-sheet"
import { ConstellationCard } from "@/features/sky/constellation-card"
import { TrialSheet } from "@/features/sky/trial-sheet"
import { useApi } from "@/hooks/use-api"
import { queryKeys } from "@/lib/query-keys"
import type { Constellation } from "@/lib/types"

export function PantheonView() {
  const { api } = useApi()
  const [asking, setAsking] = useState<Constellation | null>(null)
  const [trialId, setTrialId] = useState<number | null>(null)

  const pantheon = useQuery({
    queryKey: queryKeys.constellations,
    queryFn: () => api.constellations(),
  })

  const friends = pantheon.data?.filter((one) => one.friendship.is_friend).length ?? 0

  return (
    <div className="grid gap-3">
      <div className="flex items-baseline justify-between">
        <h2 className="text-lg font-semibold">The sky</h2>
        <Badge variant="outline" className="font-mono text-xs">
          {friends} / {pantheon.data?.length ?? 0} friends
        </Badge>
      </div>
      <p className="text-muted-foreground -mt-2 text-sm">
        You do not join a constellation — you ask, and it decides. Until one has
        befriended you, nothing it issues reaches you.
      </p>

      {pantheon.isLoading && <Skeleton className="h-56 w-full" />}
      {pantheon.data?.length === 0 && (
        <EmptyState>
          The sky is empty. Seed the pantheon with{" "}
          <code className="font-mono">python -m scripts.seed_pantheon</code>.
        </EmptyState>
      )}

      {pantheon.data?.map((constellation) => (
        <ConstellationCard
          key={constellation.code}
          constellation={constellation}
          onAsk={setAsking}
          onOpenTrial={setTrialId}
        />
      ))}

      <BefriendSheet
        constellation={asking}
        onOpenChange={(open) => !open && setAsking(null)}
        onOpenTrial={setTrialId}
      />
      <TrialSheet offerId={trialId} onOpenChange={(open) => !open && setTrialId(null)} />
    </div>
  )
}
