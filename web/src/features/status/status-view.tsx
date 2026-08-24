/** The status window, stat allocation, the profile, and the daily reset. */

import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { RefreshCw } from "lucide-react"
import { toast } from "sonner"

import { EmptyState } from "@/components/empty-state"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import { useApi } from "@/hooks/use-api"
import { percent, plural } from "@/lib/format"
import { PROGRESSION_KEYS, queryKeys } from "@/lib/query-keys"
import { STAT_NAMES, type DailyReset, type StatBlock } from "@/lib/types"

const NO_POINTS: StatBlock = {
  strength: 0,
  agility: 0,
  vitality: 0,
  intelligence: 0,
  perception: 0,
}

export function StatusView() {
  const { api } = useApi()
  const queryClient = useQueryClient()

  const status = useQuery({ queryKey: queryKeys.status, queryFn: () => api.status() })
  const account = useQuery({ queryKey: queryKeys.account, queryFn: () => api.account() })

  const [allocation, setAllocation] = useState<StatBlock>(NO_POINTS)
  const [profile, setProfile] = useState<{ name: string; timezone: string } | null>(null)
  const [lastReset, setLastReset] = useState<DailyReset | null>(null)
  const [allocateOpen, setAllocateOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)

  const invalidate = (keys: readonly (readonly string[])[]) =>
    Promise.all(keys.map((key) => queryClient.invalidateQueries({ queryKey: key })))

  const allocate = useMutation({
    mutationFn: () => api.allocate(allocation),
    onSuccess: () => {
      setAllocation(NO_POINTS)
      setAllocateOpen(false)
      toast.success("Stat points spent.")
      void invalidate([queryKeys.status, queryKeys.system])
    },
  })

  const updateProfile = useMutation({
    mutationFn: () => api.updatePlayer(profile ?? {}),
    onSuccess: () => {
      setProfileOpen(false)
      toast.success("Profile updated.")
      void invalidate([queryKeys.status, queryKeys.quests])
    },
  })

  const runReset = useMutation({
    mutationFn: () => api.dailyReset(),
    onSuccess: (result) => {
      setLastReset(result)
      const lost = result.total_exp_lost ? `, -${result.total_exp_lost} EXP` : ""
      const summary = `Reset ${result.reset_date}: ${result.failed_count} failed, ${result.spawned_count} opened${lost}.`
      if (result.failed_count) toast.error(summary)
      else toast.success(summary)
      void invalidate(PROGRESSION_KEYS)
    },
  })

  if (status.isLoading) return <Skeleton className="h-72 w-full" />
  if (!status.data) return <EmptyState>Could not load the status window.</EmptyState>

  const player = status.data
  const spending = Object.values(allocation).reduce((total, value) => total + value, 0)
  const form = profile ?? { name: player.name, timezone: player.timezone }

  return (
    <div className="grid gap-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">{player.name}</CardTitle>
          <CardDescription className="font-mono text-xs">
            {player.exp} / {player.exp_to_next_level} EXP ·{" "}
            {Math.round(player.exp_progress * 100)}% to level {player.level + 1}
          </CardDescription>
          <CardAction>
            <Badge variant="outline" className="font-mono">
              LEVEL {player.level}
            </Badge>
          </CardAction>
        </CardHeader>
        <CardContent className="grid gap-4">
          <Progress value={percent(player.exp, player.exp_to_next_level)} />

          <div className="grid grid-cols-2 gap-2">
            <Tile label="Total EXP" value={player.total_exp_earned} />
            <Tile label="Unspent points" value={player.stat_points} />
          </div>

          <div className="grid grid-cols-5 gap-1.5">
            {STAT_NAMES.map((stat) => (
              <Tile key={stat} label={stat.slice(0, 3)} value={player.stats[stat]} compact />
            ))}
          </div>

          <Sheet open={allocateOpen} onOpenChange={setAllocateOpen}>
            <SheetTrigger asChild>
              <Button variant="secondary" className="w-full" disabled={player.stat_points === 0}>
                {player.stat_points
                  ? `Allocate ${plural(player.stat_points, "point")}`
                  : "No points to allocate"}
              </Button>
            </SheetTrigger>
            <SheetContent side="bottom" className="pb-safe max-h-[85vh] overflow-y-auto">
              <SheetHeader>
                <SheetTitle>Allocate stat points</SheetTitle>
                <SheetDescription>
                  {plural(player.stat_points, "point")} available. An unaffordable
                  allocation is rejected whole.
                </SheetDescription>
              </SheetHeader>
              <form
                className="grid gap-4 px-4 pb-6"
                onSubmit={(event) => {
                  event.preventDefault()
                  allocate.mutate()
                }}
              >
                {STAT_NAMES.map((stat) => (
                  <div key={stat} className="flex items-center justify-between gap-4">
                    <Label htmlFor={`allocate-${stat}`} className="capitalize">
                      {stat}
                      <span className="text-muted-foreground ml-1 font-mono text-xs">
                        {player.stats[stat]}
                      </span>
                    </Label>
                    <Input
                      id={`allocate-${stat}`}
                      type="number"
                      inputMode="numeric"
                      min={0}
                      className="w-24 font-mono"
                      value={allocation[stat]}
                      onChange={(event) =>
                        setAllocation({
                          ...allocation,
                          [stat]: Math.max(0, Number(event.target.value) || 0),
                        })
                      }
                    />
                  </div>
                ))}
                {spending > player.stat_points && (
                  <p className="text-destructive text-xs">
                    {spending} exceeds the {player.stat_points} you have.
                  </p>
                )}
                <Button type="submit" disabled={spending === 0 || allocate.isPending}>
                  Spend {spending || ""}
                </Button>
              </form>
            </SheetContent>
          </Sheet>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Daily reset</CardTitle>
          <CardDescription>
            Lapses periods that ended before today and opens the ones now due.
            Idempotent within a local day — the iOS client calls it on launch and on
            foreground.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3">
          <Button
            className="w-full"
            onClick={() => runReset.mutate()}
            disabled={runReset.isPending}
          >
            <RefreshCw className={runReset.isPending ? "animate-spin" : undefined} />
            Run reset
          </Button>
          {lastReset && (
            <p className="text-muted-foreground text-center font-mono text-xs">
              {lastReset.reset_date} · {lastReset.failed_count} failed ·{" "}
              {lastReset.spawned_count} opened
              {lastReset.total_exp_lost ? ` · -${lastReset.total_exp_lost} EXP` : ""}
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Profile</CardTitle>
          <CardDescription className="font-mono text-xs break-all">
            {account.data ? `${account.data.email} · #${account.data.id}` : "—"}
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-2">
          <div className="text-muted-foreground flex justify-between text-sm">
            <span>Timezone</span>
            <span className="font-mono">{player.timezone}</span>
          </div>
          <Sheet open={profileOpen} onOpenChange={setProfileOpen}>
            <SheetTrigger asChild>
              <Button variant="outline" className="w-full">
                Edit profile
              </Button>
            </SheetTrigger>
            <SheetContent side="bottom" className="pb-safe max-h-[85vh] overflow-y-auto">
              <SheetHeader>
                <SheetTitle>Profile</SheetTitle>
                <SheetDescription>
                  Periods turn at midnight in your timezone. Changing it shifts future
                  rollovers only.
                </SheetDescription>
              </SheetHeader>
              <form
                className="grid gap-4 px-4 pb-6"
                onSubmit={(event) => {
                  event.preventDefault()
                  updateProfile.mutate()
                }}
              >
                <div className="grid gap-2">
                  <Label htmlFor="profile-name">Hunter name</Label>
                  <Input
                    id="profile-name"
                    maxLength={80}
                    value={form.name}
                    onChange={(event) => setProfile({ ...form, name: event.target.value })}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="profile-timezone">Timezone</Label>
                  <Input
                    id="profile-timezone"
                    spellCheck={false}
                    value={form.timezone}
                    onChange={(event) =>
                      setProfile({ ...form, timezone: event.target.value })
                    }
                  />
                </div>
                <Button type="submit" disabled={updateProfile.isPending}>
                  Save
                </Button>
              </form>
            </SheetContent>
          </Sheet>
        </CardContent>
      </Card>
    </div>
  )
}

function Tile({
  label,
  value,
  compact = false,
}: {
  label: string
  value: string | number
  compact?: boolean
}) {
  return (
    <div className="bg-muted/40 rounded-md border px-2 py-1.5 text-center">
      <div className="text-muted-foreground text-[0.6rem] tracking-[0.1em] uppercase">
        {label}
      </div>
      <div className={compact ? "font-mono text-base" : "font-mono text-lg"}>{value}</div>
    </div>
  )
}
