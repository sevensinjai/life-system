/**
 * The top bar: who you are, whether the API is up, and a settings sheet.
 *
 * Everything that is not day-to-day — the API target, the theme, signing out
 * — lives in the sheet rather than on the bar, which is the only way six
 * controls fit on a phone.
 */

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Diamond, LogOut, Moon, Settings, Sun } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { useApi } from "@/hooks/use-api"
import { useTheme } from "@/hooks/use-theme"
import { queryKeys } from "@/lib/query-keys"
import { cn } from "@/lib/utils"

export function AppHeader() {
  const { api, authenticated, baseUrl, setBaseUrl, signOut } = useApi()
  const { theme, toggle } = useTheme()
  const [open, setOpen] = useState(false)
  // This form is the only writer of the base URL, so it owns the draft.
  const [draft, setDraft] = useState(baseUrl)

  const health = useQuery({
    queryKey: [...queryKeys.health, baseUrl],
    queryFn: () => api.health(),
    retry: false,
    refetchInterval: 30_000,
  })

  const state = health.isSuccess ? "ok" : health.isLoading ? "pending" : "down"

  const status = useQuery({
    queryKey: queryKeys.status,
    queryFn: () => api.status(),
    enabled: authenticated,
  })

  return (
    <header className="pt-safe bg-background/85 z-20 border-b backdrop-blur">
      <div className="flex h-14 items-center gap-2 px-4">
        <Diamond className="text-primary size-4 shrink-0" />
        <span className="text-sm font-bold tracking-[0.28em]">SYSTEM</span>

        {authenticated && status.data && (
          <Badge variant="outline" className="ml-1 font-mono text-[0.65rem]">
            LV {status.data.level}
          </Badge>
        )}

        <span
          data-testid="health"
          data-state={state}
          aria-label={`API ${state}`}
          className={cn(
            "ml-auto size-2 rounded-full",
            state === "ok" && "bg-chart-3 shadow-[0_0_8px] shadow-chart-3/70",
            state === "pending" && "bg-muted-foreground animate-pulse",
            state === "down" && "bg-destructive"
          )}
        />

        <Button
          variant="ghost"
          size="icon-sm"
          aria-label="Settings"
          onClick={() => setOpen(true)}
        >
          <Settings />
        </Button>
      </div>

      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent side="bottom" className="pb-safe max-h-[85vh] overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Settings</SheetTitle>
            <SheetDescription>
              {health.isSuccess
                ? `${health.data.service} ${health.data.version} · ${health.data.environment}`
                : health.isLoading
                  ? "Checking the API…"
                  : "The API is unreachable."}
            </SheetDescription>
          </SheetHeader>

          <div className="grid gap-5 px-4 pb-6">
            <form
              className="grid gap-2"
              onSubmit={(event) => {
                event.preventDefault()
                setBaseUrl(draft)
              }}
            >
              <Label htmlFor="api-base">API base URL</Label>
              <div className="flex gap-2">
                <Input
                  id="api-base"
                  value={draft}
                  spellCheck={false}
                  inputMode="url"
                  placeholder="same origin"
                  onChange={(event) => setDraft(event.target.value)}
                  className="font-mono text-xs"
                />
                <Button type="submit" variant="secondary">
                  Connect
                </Button>
              </div>
              <p className="text-muted-foreground text-xs">
                Blank uses the server that served this page. Another host has to allow
                this origin in <code className="font-mono">APP_CORS_ORIGINS</code>.
              </p>
            </form>

            <Separator />

            <div className="flex items-center justify-between">
              {/* A <label for> would override the button's own name, so this
                  is plain text and the button says what it does. */}
              <span className="text-sm font-medium">Appearance</span>
              <Button variant="outline" size="sm" onClick={toggle}>
                {theme === "dark" ? <Sun /> : <Moon />}
                {theme === "dark" ? "Light" : "Dark"}
              </Button>
            </div>

            {authenticated && (
              <>
                <Separator />
                <Button
                  variant="outline"
                  className="text-destructive w-full"
                  onClick={() => {
                    setOpen(false)
                    signOut()
                  }}
                >
                  <LogOut /> Sign out
                </Button>
              </>
            )}
          </div>
        </SheetContent>
      </Sheet>
    </header>
  )
}
