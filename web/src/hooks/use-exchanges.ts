/** The request log, subscribed straight from the client's own store. */

import { useSyncExternalStore } from "react"

import type { Exchange } from "@/lib/api"
import { useApi } from "@/hooks/use-api"

export function useExchanges(): readonly Exchange[] {
  const { api } = useApi()
  return useSyncExternalStore(api.subscribe, api.getExchanges, api.getExchanges)
}
