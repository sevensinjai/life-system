/**
 * A trial of admission: the side quest a constellation sets when it agrees to
 * hear you.
 *
 * It is an ordinary side quest offer and goes through the ordinary side quest
 * endpoints — accept it, log progress, clear it — but it is the only one this
 * screen ever shows, because clearing it is what makes you friends.
 */

import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import { useApi } from "@/hooks/use-api"
import { formatRelative, percent } from "@/lib/format"
import { TRIAL_KEYS, queryKeys } from "@/lib/query-keys"

export function TrialSheet({
  offerId,
  onOpenChange,
}: {
  offerId: number | null
  onOpenChange: (open: boolean) => void
}) {
  return (
    <Sheet open={offerId !== null} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="pb-safe max-h-[92vh] overflow-y-auto">
        {offerId !== null && <Trial offerId={offerId} onDone={() => onOpenChange(false)} />}
      </SheetContent>
    </Sheet>
  )
}

function Trial({ offerId, onDone }: { offerId: number; onDone: () => void }) {
  const { api } = useApi()
  const queryClient = useQueryClient()
  const [amount, setAmount] = useState("1")

  const offer = useQuery({
    queryKey: queryKeys.sideQuestOffer(offerId),
    queryFn: () => api.sideQuestOffer(offerId),
  })

  const invalidate = () =>
    Promise.all(TRIAL_KEYS.map((key) => queryClient.invalidateQueries({ queryKey: key })))

  const accept = useMutation({
    mutationFn: () => api.acceptSideQuest(offerId),
    onSuccess: () => {
      toast.success("Trial accepted. Clear it and you are friends.")
      void invalidate()
    },
  })

  const decline = useMutation({
    mutationFn: () => api.declineSideQuest(offerId),
    onSuccess: () => {
      toast("Trial declined. The request closes, and the wait starts.")
      onDone()
      void invalidate()
    },
  })

  const logProgress = useMutation({
    mutationFn: (value: number) => api.progressSideQuest(offerId, value),
    onSuccess: (result) => {
      if (result.completed) {
        toast.success("Trial cleared. You are one of theirs.")
        onDone()
      } else {
        toast(`${result.offer.progress} / ${result.offer.target_count}.`)
      }
      void invalidate()
    },
  })

  const complete = useMutation({
    mutationFn: () => api.completeSideQuest(offerId),
    onSuccess: () => {
      toast.success("Trial cleared. You are one of theirs.")
      onDone()
      void invalidate()
    },
  })

  if (offer.isLoading) return <Skeleton className="m-4 h-56" />
  if (!offer.data) return null

  const { side_quest: quest, status } = offer.data
  const busy = accept.isPending || decline.isPending || logProgress.isPending || complete.isPending
  const open = status === "offered"
  const accepted = status === "accepted"

  return (
    <>
      <SheetHeader>
        <SheetTitle>{quest.title}</SheetTitle>
        <SheetDescription>
          {quest.constellation
            ? `Set by ${quest.constellation.name}.`
            : "A trial of admission."}{" "}
          {quest.penalty_exp === 0
            ? "Failing it costs nothing but the audition."
            : `Failing it costs ${quest.penalty_exp} EXP.`}
        </SheetDescription>
      </SheetHeader>

      <div className="grid gap-4 px-4">
        {quest.description && <p className="text-sm">{quest.description}</p>}

        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className="font-mono text-xs">
            {quest.difficulty}
          </Badge>
          <Badge variant="outline" className="font-mono text-xs">
            {quest.exp_reward} EXP
          </Badge>
          {quest.stat_reward && (
            <Badge variant="outline" className="font-mono text-xs">
              +{quest.stat_reward_amount} {quest.stat_reward}
            </Badge>
          )}
          <Badge variant="outline" className="font-mono text-xs">
            {status}
          </Badge>
        </div>

        <div className="grid gap-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-mono">
              {offer.data.progress} / {offer.data.target_count}
              {quest.unit ? ` ${quest.unit}` : ""}
            </span>
            <span className="text-muted-foreground">
              {offer.data.expires_at ? `expires ${formatRelative(offer.data.expires_at)}` : "no deadline"}
            </span>
          </div>
          <Progress value={percent(offer.data.progress, offer.data.target_count)} />
        </div>
      </div>

      <div className="grid gap-2 p-4">
        {open && (
          <Button disabled={busy} onClick={() => accept.mutate()}>
            Accept the trial
          </Button>
        )}

        {accepted && (
          <>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                className="flex-1"
                disabled={busy}
                onClick={() => logProgress.mutate(1)}
              >
                +1
              </Button>
              <Input
                aria-label="Progress amount"
                data-testid="trial-amount"
                type="number"
                inputMode="numeric"
                className="w-20 shrink-0 text-center font-mono"
                value={amount}
                onChange={(event) => setAmount(event.target.value)}
              />
              <Button
                variant="secondary"
                className="flex-1"
                disabled={busy}
                onClick={() => logProgress.mutate(Number(amount) || 1)}
              >
                Add
              </Button>
            </div>
            <Button disabled={busy} onClick={() => complete.mutate()}>
              Clear it
            </Button>
          </>
        )}

        {(open || accepted) && (
          <Button
            variant="ghost"
            className="text-destructive"
            disabled={busy}
            onClick={() => decline.mutate()}
          >
            Decline
          </Button>
        )}

        <Button variant="ghost" onClick={onDone}>
          Close
        </Button>
      </div>
    </>
  )
}
