/** The status window, stat allocation, the profile, and the daily reset. */

import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { RefreshCw } from "lucide-react"

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
import { Skeleton } from "@/components/ui/skeleton"
import { useApi } from "@/hooks/use-api"
import { percent, plural } from "@/lib/format"
import { PROGRESSION_KEYS, queryKeys } from "@/lib/query-keys"
import { STAT_NAMES, type DailyReset, type StatBlock } from "@/lib/types"
import { toast } from "sonner"

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

  const invalidate = (keys: readonly (readonly string[])[]) =>
    Promise.all(keys.map((key) => queryClient.invalidateQueries({ queryKey: key })))

  const allocate = useMutation({
    mutationFn: () => api.allocate(allocation),
    onSuccess: () => {
      setAllocation(NO_POINTS)
      toast.success("Stat points spent.")
      void invalidate([queryKeys.status, queryKeys.system])
    },
  })

  const updateProfile = useMutation({
    mutationFn: () => api.updatePlayer(profile ?? {}),
    onSuccess: () => {
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

  if (status.isLoading || account.isLoading) return <StatusSkeleton />
  if (!status.data) return <EmptyState>Could not load the status window.</EmptyState>

  const player = status.data
  const spending = Object.values(allocation).reduce((total, value) => total + value, 0)
  const form = profile ?? { name: player.name, timezone: player.timezone }

  return (
    <div className="grid items-start gap-6 lg:grid-cols-2">
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">{player.name}</CardTitle>
            <CardDescription className="font-mono">
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
            <div className="grid grid-cols-3 gap-2">
              <Tile label="Total EXP" value={player.total_exp_earned} />
              <Tile label="Unspent" value={player.stat_points} />
              <Tile label="Timezone" value={player.timezone} small />
            </div>
            <div className="grid grid-cols-5 gap-2">
              {STAT_NAMES.map((stat) => (
                <Tile key={stat} label={stat.slice(0, 3)} value={player.stats[stat]} />
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Daily reset</CardTitle>
            <CardDescription>
              <code className="font-mono">POST /system/daily-reset</code> lapses periods
              that ended before today and opens the ones now due. Idempotent within a
              local day — the iOS client calls it on launch and on foreground.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap items-center gap-3">
            <Button onClick={() => runReset.mutate()} disabled={runReset.isPending}>
              <RefreshCw className={runReset.isPending ? "animate-spin" : undefined} />
              Run reset
            </Button>
            {lastReset && (
              <Badge variant="outline" className="font-mono text-xs">
                {lastReset.reset_date} · {lastReset.failed_count} failed ·{" "}
                {lastReset.spawned_count} opened
                {lastReset.total_exp_lost ? ` · -${lastReset.total_exp_lost} EXP` : ""}
              </Badge>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Allocate stat points</CardTitle>
            <CardDescription>
              {plural(player.stat_points, "point")} available. An unaffordable
              allocation is rejected whole.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form
              className="grid gap-4"
              onSubmit={(event) => {
                event.preventDefault()
                allocate.mutate()
              }}
            >
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                {STAT_NAMES.map((stat) => (
                  <div key={stat} className="grid gap-1.5">
                    <Label htmlFor={`allocate-${stat}`} className="text-xs capitalize">
                      {stat}
                    </Label>
                    <Input
                      id={`allocate-${stat}`}
                      type="number"
                      min={0}
                      className="font-mono"
                      value={allocation[stat]}
                      disabled={player.stat_points === 0}
                      onChange={(event) =>
                        setAllocation({
                          ...allocation,
                          [stat]: Math.max(0, Number(event.target.value) || 0),
                        })
                      }
                    />
                  </div>
                ))}
              </div>
              <div className="flex items-center gap-3">
                <Button
                  type="submit"
                  disabled={player.stat_points === 0 || spending === 0 || allocate.isPending}
                >
                  Spend {spending || ""}
                </Button>
                {spending > player.stat_points && (
                  <span className="text-destructive text-xs">
                    {spending} exceeds the {player.stat_points} you have.
                  </span>
                )}
              </div>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
            <CardDescription className="font-mono">
              {account.data ? `${account.data.email} · account #${account.data.id}` : "—"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form
              className="grid gap-4"
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
                <p className="text-muted-foreground text-xs">
                  Periods turn at midnight here. Changing it shifts future rollovers
                  only.
                </p>
              </div>
              <Button type="submit" variant="secondary" disabled={updateProfile.isPending}>
                Save
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function Tile({
  label,
  value,
  small = false,
}: {
  label: string
  value: string | number
  small?: boolean
}) {
  return (
    <div className="bg-muted/40 rounded-md border px-3 py-2">
      <div className="text-muted-foreground text-[0.65rem] tracking-[0.12em] uppercase">
        {label}
      </div>
      <div className={small ? "font-mono text-sm" : "font-mono text-lg"}>{value}</div>
    </div>
  )
}

function StatusSkeleton() {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Skeleton className="h-72 w-full" />
      <Skeleton className="h-72 w-full" />
    </div>
  )
}
