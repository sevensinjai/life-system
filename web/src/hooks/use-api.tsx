/**
 * The API client as context, plus the signed-in/out state around it.
 *
 * The client itself is framework-free (see lib/api.ts); this is the thin React
 * binding — the piece a React Native app would rewrite and nothing else.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"
import type { ReactNode } from "react"

import type { ApiClient } from "@/lib/api"

interface ApiContextValue {
  api: ApiClient
  token: string | null
  authenticated: boolean
  baseUrl: string
  signIn: (token: string) => void
  signOut: () => void
  setBaseUrl: (baseUrl: string) => void
}

const ApiContext = createContext<ApiContextValue | null>(null)

export function ApiProvider({
  client,
  onSignOut,
  children,
}: {
  client: ApiClient
  onSignOut?: () => void
  children: ReactNode
}) {
  const [token, setToken] = useState<string | null>(client.token)
  const [baseUrl, setBaseUrlState] = useState(client.baseUrl)

  const signIn = useCallback(
    (next: string) => {
      client.setToken(next)
      setToken(next)
    },
    [client]
  )

  const signOut = useCallback(() => {
    client.setToken(null)
    setToken(null)
    onSignOut?.()
  }, [client, onSignOut])

  // A rejected token is the API's answer, not a decision any view makes.
  useEffect(() => client.onUnauthorized(signOut), [client, signOut])

  const setBaseUrl = useCallback(
    (next: string) => {
      client.setBaseUrl(next)
      setBaseUrlState(client.baseUrl)
    },
    [client]
  )

  const value = useMemo<ApiContextValue>(
    () => ({
      api: client,
      token,
      authenticated: Boolean(token),
      baseUrl,
      signIn,
      signOut,
      setBaseUrl,
    }),
    [client, token, baseUrl, signIn, signOut, setBaseUrl]
  )

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>
}

export function useApi() {
  const value = useContext(ApiContext)
  if (!value) throw new Error("useApi must be used inside <ApiProvider>.")
  return value
}
