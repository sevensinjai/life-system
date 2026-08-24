/** Providers, then the phone shell. */

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
      <Toaster
        position="top-center"
        richColors
        closeButton
        offset={{ top: "72px" }}
        mobileOffset={{ top: "72px" }}
      />
    </ThemeProvider>
  )
}

/**
 * A phone-sized app, and only that.
 *
 * The iOS client is the thing being stood in for, so there is no desktop
 * layout to fall back to: on a big screen the same UI sits centred at phone
 * width instead of reflowing into something the app will never look like.
 */
function Shell() {
  const { authenticated } = useApi()

  return (
    <div className="bg-muted/40 flex h-full justify-center">
      <div className="bg-background system-backdrop flex h-full w-full max-w-[430px] flex-col overflow-hidden sm:border-x">
        <AppHeader />
        {authenticated ? (
          <Workspace />
        ) : (
          <main className="flex-1 overflow-y-auto overscroll-contain px-4 pt-4 pb-8">
            <AuthScreen />
          </main>
        )}
      </div>
    </div>
  )
}
