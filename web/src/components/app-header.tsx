/** Brand, the API target, a health light, the theme toggle, sign out. */

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Diamond, LogOut, Moon, Sun } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useApi } from "@/hooks/use-api"
import { useTheme } from "@/hooks/use-theme"
import { queryKeys } from "@/lib/query-keys"

export function AppHeader() {
  const { api, authenticated, baseUrl, setBaseUrl, signOut } = useApi()
  const { theme, toggle } = useTheme()
  // This form is the only writer of the base URL, so it owns the draft.
  const [draft, setDraft] = useState(baseUrl)

  // Not part of the cache-invalidation graph: it answers "is anything there",
  // so it re-checks on its own schedule and never blocks a view.
  const health = useQuery({
    queryKey: [...queryKeys.health, baseUrl],
    queryFn: () => api.health(),
    retry: false,
    refetchInterval: 30_000,
  })

  return (
    <header className="bg-background/80 supports-[backdrop-filter]:bg-background/60 sticky top-0 z-30 border-b backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center gap-3 px-4 py-3">
        <div className="flex items-baseline gap-2">
          <Diamond className="text-primary size-4 shrink-0 self-center" />
          <span className="text-sm font-bold tracking-[0.3em]">SYSTEM</span>
          <span className="text-muted-foreground hidden text-xs sm:inline">web client</span>
        </div>

        <form
          className="ml-auto flex items-center gap-2"
          onSubmit={(event) => {
            event.preventDefault()
            setBaseUrl(draft)
          }}
        >
          <Label htmlFor="api-base" className="text-muted-foreground text-xs">
            API
          </Label>
          <Input
            id="api-base"
            value={draft}
            spellCheck={false}
            placeholder="same origin"
            onChange={(event) => setDraft(event.target.value)}
            className="h-8 w-44 font-mono text-xs sm:w-60"
          />
          <Button type="submit" variant="outline" size="sm">
            Connect
          </Button>
        </form>

        <Badge
          variant="outline"
          data-testid="health"
          data-state={health.isSuccess ? "ok" : health.isLoading ? "pending" : "down"}
          className={
            health.isSuccess
              ? "border-chart-3/50 text-chart-3 font-mono text-xs"
              : health.isLoading
                ? "text-muted-foreground font-mono text-xs"
                : "border-destructive/50 text-destructive font-mono text-xs"
          }
        >
          {health.isSuccess
            ? `${health.data.service} ${health.data.version} · ${health.data.environment}`
            : health.isLoading
              ? "checking…"
              : "unreachable"}
        </Badge>

        <Button
          variant="ghost"
          size="icon-sm"
          onClick={toggle}
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
          {theme === "dark" ? <Sun /> : <Moon />}
        </Button>

        {authenticated && (
          <Button variant="ghost" size="sm" onClick={signOut}>
            <LogOut /> Sign out
          </Button>
        )}
      </div>
    </header>
  )
}
