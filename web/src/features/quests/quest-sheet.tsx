/**
 * Authoring and editing, in one bottom sheet.
 *
 * The form is the same either way — a quest you are writing and a quest you
 * are changing differ only in whether an id exists — so a phone gets one
 * screen for both instead of a page and a dialog.
 */

import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { QuestFields } from "@/features/quests/quest-form"
import {
  emptyQuestForm,
  formToPayload,
  questToForm,
} from "@/features/quests/quest-form-state"
import { useApi } from "@/hooks/use-api"
import { PROGRESSION_KEYS } from "@/lib/query-keys"
import type { Quest } from "@/lib/types"

export type QuestSheetTarget = { mode: "create" } | { mode: "edit"; quest: Quest }

export function QuestSheet({
  target,
  onOpenChange,
}: {
  target: QuestSheetTarget | null
  onOpenChange: (open: boolean) => void
}) {
  return (
    <Sheet open={Boolean(target)} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="pb-safe max-h-[92vh] overflow-y-auto">
        {/* Keyed by target, so opening a different quest remounts the form
            with its own state instead of syncing props into state. */}
        {target && (
          <QuestForm
            key={target.mode === "edit" ? target.quest.id : "new"}
            target={target}
            onDone={() => onOpenChange(false)}
          />
        )}
      </SheetContent>
    </Sheet>
  )
}

function QuestForm({
  target,
  onDone,
}: {
  target: QuestSheetTarget
  onDone: () => void
}) {
  const { api } = useApi()
  const queryClient = useQueryClient()
  const [form, setForm] = useState(() =>
    target.mode === "edit" ? questToForm(target.quest) : emptyQuestForm()
  )

  const save = useMutation({
    mutationFn: () =>
      target.mode === "edit"
        ? api.updateQuest(target.quest.id, formToPayload(form))
        : api.createQuest(formToPayload(form)),
    onSuccess: (quest) => {
      toast.success(
        target.mode === "edit"
          ? "Quest updated. Schedule changes apply from the next period."
          : `"${quest.title}" added to your board.`
      )
      onDone()
      void Promise.all(
        PROGRESSION_KEYS.map((key) => queryClient.invalidateQueries({ queryKey: key }))
      )
    },
  })

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        save.mutate()
      }}
    >
      <SheetHeader>
        <SheetTitle>
          {target.mode === "edit" ? `Edit quest #${target.quest.id}` : "Author a quest"}
        </SheetTitle>
        <SheetDescription>
          {target.mode === "edit"
            ? `Currently ${target.quest.schedule.label.toLowerCase()}. Changing target count also updates the open period; changing the schedule applies from the next one.`
            : "You are the designer and the player. Its first period opens immediately if the schedule falls on today."}
        </SheetDescription>
      </SheetHeader>

      <div className="px-4">
        <QuestFields
          value={form}
          onChange={setForm}
          idPrefix={target.mode === "edit" ? "edit-quest" : "new-quest"}
        />
      </div>

      <div className="grid gap-2 p-4">
        <Button type="submit" disabled={save.isPending}>
          {target.mode === "edit" ? "Save changes" : "Create quest"}
        </Button>
        <Button type="button" variant="ghost" onClick={onDone}>
          Cancel
        </Button>
      </div>
    </form>
  )
}
