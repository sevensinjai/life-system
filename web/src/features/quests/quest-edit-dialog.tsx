/** Edit a quest from either quest view. */

import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { QuestFields } from "@/features/quests/quest-form"
import { formToPayload, questToForm } from "@/features/quests/quest-form-state"
import { useApi } from "@/hooks/use-api"
import { PROGRESSION_KEYS } from "@/lib/query-keys"
import type { Quest } from "@/lib/types"

export function QuestEditDialog({
  quest,
  onOpenChange,
}: {
  quest: Quest | null
  onOpenChange: (open: boolean) => void
}) {
  return (
    <Dialog open={Boolean(quest)} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        {/* Keyed by quest, so opening a different one remounts the form with
            its own state instead of syncing props into state. */}
        {quest && <EditForm key={quest.id} quest={quest} onDone={() => onOpenChange(false)} />}
      </DialogContent>
    </Dialog>
  )
}

function EditForm({ quest, onDone }: { quest: Quest; onDone: () => void }) {
  const { api } = useApi()
  const queryClient = useQueryClient()
  const [form, setForm] = useState(() => questToForm(quest))

  const save = useMutation({
    mutationFn: () => api.updateQuest(quest.id, formToPayload(form)),
    onSuccess: () => {
      toast.success("Quest updated. Schedule changes apply from the next period.")
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
      <DialogHeader>
        <DialogTitle>Edit quest #{quest.id}</DialogTitle>
        <DialogDescription>
          Currently {quest.schedule.label.toLowerCase()}. Changing target count also
          updates the open period; changing the schedule applies from the next one.
        </DialogDescription>
      </DialogHeader>

      <div className="py-4">
        <QuestFields value={form} onChange={setForm} idPrefix="edit-quest" />
      </div>

      <DialogFooter>
        <Button type="button" variant="ghost" onClick={onDone}>
          Cancel
        </Button>
        <Button type="submit" disabled={save.isPending}>
          Save changes
        </Button>
      </DialogFooter>
    </form>
  )
}
