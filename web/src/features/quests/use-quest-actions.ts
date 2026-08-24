/** Quest mutations shared by the board and the quest list. */

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { useApi } from "@/hooks/use-api"
import { PROGRESSION_KEYS } from "@/lib/query-keys"
import type { QuestAction } from "@/lib/types"

export function useQuestActions() {
  const { api } = useApi()
  const queryClient = useQueryClient()

  /** A quest action moves the board, the list, the status window, and the log. */
  const invalidate = () =>
    Promise.all(
      PROGRESSION_KEYS.map((key) => queryClient.invalidateQueries({ queryKey: key }))
    )

  const report = (result: QuestAction) => {
    if (result.completed) {
      const gained = result.exp_gained ? ` +${result.exp_gained} EXP` : ""
      toast.success(
        `${result.quest.title} cleared.${gained}${result.leveled_up ? " LEVEL UP!" : ""}`
      )
    } else {
      toast(`${result.quest.title}: ${result.instance.progress} / ${result.instance.target_count}.`)
    }
    void invalidate()
  }

  const progress = useMutation({
    mutationFn: ({ id, amount }: { id: number; amount: number }) =>
      api.logProgress(id, amount),
    onSuccess: report,
  })

  const complete = useMutation({
    mutationFn: (id: number) => api.completeQuest(id),
    onSuccess: report,
  })

  const archive = useMutation({
    mutationFn: (id: number) => api.archiveQuest(id),
    onSuccess: () => {
      toast("Quest archived. Its history is kept.")
      void invalidate()
    },
  })

  const restore = useMutation({
    mutationFn: (id: number) => api.updateQuest(id, { is_active: true }),
    onSuccess: () => {
      toast.success("Quest restored.")
      void invalidate()
    },
  })

  return { progress, complete, archive, restore, invalidate }
}
