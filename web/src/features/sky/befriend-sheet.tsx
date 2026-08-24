/**
 * Asking a constellation to befriend you.
 *
 * You do not join a constellation — you ask, and it decides, at once. Both
 * answers are answers rather than errors, so the sheet stays open and shows
 * what it said: a refusal with the date you may ask again, or a trial of
 * admission you can open from here.
 */

import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Textarea } from "@/components/ui/textarea"
import { useApi } from "@/hooks/use-api"
import { formatDateTime, formatRelative } from "@/lib/format"
import { queryKeys } from "@/lib/query-keys"
import type { Constellation, FriendshipRequestResult } from "@/lib/types"

export function BefriendSheet({
  constellation,
  onOpenChange,
  onOpenTrial,
}: {
  constellation: Constellation | null
  onOpenChange: (open: boolean) => void
  onOpenTrial: (offerId: number) => void
}) {
  return (
    <Sheet open={Boolean(constellation)} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="pb-safe max-h-[92vh] overflow-y-auto">
        {constellation && (
          <Petition
            key={constellation.code}
            constellation={constellation}
            onClose={() => onOpenChange(false)}
            onOpenTrial={onOpenTrial}
          />
        )}
      </SheetContent>
    </Sheet>
  )
}

function Petition({
  constellation,
  onClose,
  onOpenTrial,
}: {
  constellation: Constellation
  onClose: () => void
  onOpenTrial: (offerId: number) => void
}) {
  const { api } = useApi()
  const queryClient = useQueryClient()
  const [message, setMessage] = useState("")
  const [answer, setAnswer] = useState<FriendshipRequestResult | null>(null)

  const ask = useMutation({
    mutationFn: () => api.requestFriendship(constellation.code, message),
    onSuccess: (result) => {
      setAnswer(result)
      void queryClient.invalidateQueries({ queryKey: queryKeys.constellations })
      void queryClient.invalidateQueries({ queryKey: queryKeys.system })
    },
  })

  return (
    <>
      <SheetHeader>
        <SheetTitle>{constellation.name}</SheetTitle>
        <SheetDescription>
          {constellation.epithet ? `${constellation.epithet}. ` : ""}
          It issues trials to its friends and to nobody else, so this is the way in.
        </SheetDescription>
      </SheetHeader>

      {answer ? (
        <Answer answer={answer} onOpenTrial={onOpenTrial} onClose={onClose} />
      ) : (
        <form
          className="grid gap-4 px-4"
          onSubmit={(event) => {
            event.preventDefault()
            ask.mutate()
          }}
        >
          {constellation.description && (
            <p className="text-muted-foreground text-sm">{constellation.description}</p>
          )}

          <div className="grid gap-2">
            <Label htmlFor="petition-message">What you want to say for yourself</Label>
            <Textarea
              id="petition-message"
              maxLength={1000}
              placeholder="I fell too."
              value={message}
              onChange={(event) => setMessage(event.target.value)}
            />
            <p className="text-muted-foreground text-xs">
              Optional, and kept with the request. Nothing weighs it yet.
            </p>
          </div>

          <div className="grid gap-2 pb-4">
            <Button type="submit" disabled={ask.isPending}>
              Ask to be befriended
            </Button>
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </form>
      )}
    </>
  )
}

function Answer({
  answer,
  onOpenTrial,
  onClose,
}: {
  answer: FriendshipRequestResult
  onOpenTrial: (offerId: number) => void
  onClose: () => void
}) {
  const challenged = answer.status === "challenged" && answer.challenge_offer_id !== null

  return (
    <div className="grid gap-4 px-4 pb-4" data-testid="friendship-answer">
      {answer.line && (
        <blockquote className="border-primary/60 border-l-2 pl-3 text-lg leading-relaxed">
          {answer.line}
        </blockquote>
      )}

      <p className="text-muted-foreground text-sm">
        {challenged
          ? "It set you a trial of admission. Clear it and you are friends; fail, decline, or ignore it and the request closes."
          : `It would not hear you this time. You may ask again ${formatRelative(
              answer.retry_after
            )}${answer.retry_after ? ` (${formatDateTime(answer.retry_after)})` : ""}.`}
      </p>

      <div className="grid gap-2">
        {challenged && (
          <Button
            onClick={() => {
              onClose()
              onOpenTrial(answer.challenge_offer_id!)
            }}
          >
            Open the trial
          </Button>
        )}
        <Button variant={challenged ? "ghost" : "default"} onClick={onClose}>
          Close
        </Button>
      </div>
    </div>
  )
}
