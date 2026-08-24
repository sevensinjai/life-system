/** One constellation, answered from this player's side of it. */

import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { ChevronDown, Sparkles } from "lucide-react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { StandingBadge } from "@/features/sky/standing-badge"
import { useApi } from "@/hooks/use-api"
import { formatDate, formatRelative } from "@/lib/format"
import { queryKeys } from "@/lib/query-keys"
import { cn } from "@/lib/utils"
import type { BlockedBy, Constellation } from "@/lib/types"

/** What a disabled ask button should say, straight off `blocked_by`. */
const BLOCKED_LABEL: Record<BlockedBy, string> = {
  already_friends: "Already your friend",
  request_open: "A trial is already set",
  too_soon: "Will not hear you yet",
  retired: "No longer answers",
}

export function ConstellationCard({
  constellation,
  onAsk,
  onOpenTrial,
}: {
  constellation: Constellation
  onAsk: (constellation: Constellation) => void
  onOpenTrial: (offerId: number) => void
}) {
  const { api } = useApi()
  const queryClient = useQueryClient()
  const [showRecord, setShowRecord] = useState(false)

  const { friendship, standing } = constellation
  const trialId = friendship.challenge_offer_id

  const end = useMutation({
    mutationFn: () => api.endFriendship(constellation.code),
    onSuccess: () => {
      toast("Friendship ended. Your standing stays where it stood.")
      void queryClient.invalidateQueries({ queryKey: queryKeys.constellations })
      void queryClient.invalidateQueries({ queryKey: queryKeys.system })
    },
  })

  return (
    <article
      className={cn(
        "rounded-lg border p-3",
        friendship.is_friend && "border-primary/40 bg-primary/[0.04]"
      )}
    >
      <div className="flex items-start gap-2">
        <Sparkles
          className={cn(
            "mt-0.5 size-4 shrink-0",
            friendship.is_friend ? "text-primary" : "text-muted-foreground"
          )}
        />
        <div className="min-w-0 flex-1">
          <h3 className="text-sm leading-tight font-medium">{constellation.name}</h3>
          {constellation.epithet && (
            <p className="text-muted-foreground text-xs italic">{constellation.epithet}</p>
          )}
        </div>
        <StandingBadge standing={standing.standing} favor={standing.favor} />
      </div>

      {constellation.description && (
        <p className="text-muted-foreground mt-2 text-sm">{constellation.description}</p>
      )}

      <div className="mt-2 flex flex-wrap items-center gap-1.5">
        <Badge variant="outline" className="font-mono text-[0.65rem]">
          {constellation.domain ?? "the habit itself"}
        </Badge>
        {friendship.is_friend && (
          <Badge variant="outline" className="border-primary/50 text-primary text-[0.65rem]">
            friend since {formatDate(friendship.befriended_at?.slice(0, 10))}
          </Badge>
        )}
      </div>

      {trialId !== null && (
        <div className="border-primary/40 bg-primary/5 mt-3 rounded-md border p-2">
          <p className="text-xs">
            It set you a <strong>trial of admission</strong>. Clear it and you are friends.
          </p>
          <Button
            size="sm"
            className="mt-2 w-full"
            data-testid={`open-trial-${constellation.code}`}
            onClick={() => onOpenTrial(trialId)}
          >
            Open the trial
          </Button>
        </div>
      )}

      <div className="mt-3 grid gap-2">
        {friendship.is_friend ? (
          <Button
            variant="outline"
            className="text-destructive w-full"
            disabled={end.isPending}
            onClick={() => end.mutate()}
          >
            End friendship
          </Button>
        ) : friendship.may_ask ? (
          <Button
            className="w-full"
            data-testid={`ask-${constellation.code}`}
            onClick={() => onAsk(constellation)}
          >
            Ask to be befriended
          </Button>
        ) : (
          trialId === null && (
            <Button variant="outline" className="w-full" disabled>
              {friendship.blocked_by ? BLOCKED_LABEL[friendship.blocked_by] : "Will not hear you"}
              {friendship.blocked_by === "too_soon" && friendship.retry_after
                ? ` — ask ${formatRelative(friendship.retry_after)}`
                : ""}
            </Button>
          )
        )}

        <button
          type="button"
          className="text-muted-foreground flex items-center justify-center gap-1 text-xs"
          onClick={() => setShowRecord(!showRecord)}
        >
          <ChevronDown className={cn("size-3 transition-transform", showRecord && "rotate-180")} />
          {showRecord ? "Hide" : "Show"} record
        </button>
      </div>

      {showRecord && (
        <>
          <Separator className="my-2" />
          <dl className="grid grid-cols-3 gap-2 text-center">
            {(
              [
                ["offered", standing.offers_received],
                ["cleared", standing.completed],
                ["declined", standing.declined],
                ["expired", standing.expired],
                ["failed", standing.failed],
                ["favor", standing.favor],
              ] as const
            ).map(([label, value]) => (
              <div key={label} className="bg-muted/40 rounded-md border px-2 py-1">
                <dt className="text-muted-foreground text-[0.6rem] tracking-[0.1em] uppercase">
                  {label}
                </dt>
                <dd className="font-mono text-sm">{value}</dd>
              </div>
            ))}
          </dl>
          {standing.last_seen_at && (
            <p className="text-muted-foreground mt-2 text-center font-mono text-[0.65rem]">
              last heard from {formatRelative(standing.last_seen_at)}
            </p>
          )}
        </>
      )}
    </article>
  )
}
