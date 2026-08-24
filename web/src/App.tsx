/** Providers, then the signed-in/out switch. */

import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { toast } from "sonner"

import { AppHeader } from "@/components/app-header"
import { Toaster } from "@/components/ui/sonner"
import { ApiProvider, useApi } from "@/hooks/use-api"
import { ThemeProvider } from "@/hooks/use-theme"
import { ApiClient, ApiError, browserStore } from "@/lib/api"
import { AuthScreen } from "@/features/auth/auth-screen"
import { Workspace } from "@/features/workspace"

const client = new ApiClient(browserStore(), window.location.origin)

/**
 * One QueryClient owns every read.
 *
 * Failures are reported here rather than per call site, and mutations
 * invalidate by key, so clearing a quest updates the board, the quest list,
 * the status window, and the log from a single call.
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false, refetchOnWindowFocus: false, staleTime: 5_000 },
    mutations: { retry: false },
  },
  queryCache: new QueryCache({ onError: report }),
  mutationCache: new MutationCache({ onError: report }),
})

/** Stable identity, so the provider's sign-out listener is not re-bound. */
function clearCache() {
  queryClient.clear()
}

function report(error: unknown) {
  toast.error(
    error instanceof ApiError
      ? error.fullMessage
      : String((error as Error)?.message ?? error)
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <ApiProvider client={client} onSignOut={clearCache}>
        <QueryClientProvider client={queryClient}>
          <Shell />
        </QueryClientProvider>
      </ApiProvider>
      <Toaster position="top-right" richColors closeButton />
    </ThemeProvider>
  )
}

function Shell() {
  const { authenticated } = useApi()

  return (
    <div className="system-backdrop min-h-screen">
      <AppHeader />
      <main className="mx-auto w-full max-w-6xl px-4 pt-6 pb-20">
        {authenticated ? <Workspace /> : <AuthScreen />}
      </main>
    </div>
  )
}
