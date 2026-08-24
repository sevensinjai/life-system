/**
 * The System screen: what the app would show as notifications, and what this
 * page actually sent.
 *
 * Two logs on one screen rather than two tabs, because a phone tab bar only
 * has room for five and these are both "what happened" views.
 */

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { EmptyState } from "@/components/empty-state"
import { JsonBlock } from "@/components/json-block"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useApi } from "@/hooks/use-api"
import { useExchanges } from "@/hooks/use-exchanges"
import { formatDateTime, formatTime, statusTone } from "@/lib/format"
import { queryKeys } from "@/lib/query-keys"
import { EVENT_TYPES, type EventType } from "@/lib/types"

const PAGE_SIZE = 25
const ANY_TYPE = "all"

export function SystemView() {
  return (
    <Tabs defaultValue="events" className="gap-4">
      <TabsList className="w-full">
        <TabsTrigger value="events" className="flex-1">
          Events
        </TabsTrigger>
        <TabsTrigger value="penalties" className="flex-1">
          Penalties
        </TabsTrigger>
        <TabsTrigger value="requests" className="flex-1">
          Requests
        </TabsTrigger>
      </TabsList>

      <TabsContent value="events" className="mt-0">
        <EventsPanel />
      </TabsContent>
      <TabsContent value="penalties" className="mt-0">
        <PenaltiesPanel />
      </TabsContent>
      <TabsContent value="requests" className="mt-0">
        <RequestsPanel />
      </TabsContent>
    </Tabs>
  )
}

function EventsPanel() {
  const { api } = useApi()
  const [eventType, setEventType] = useState<EventType | typeof ANY_TYPE>(ANY_TYPE)
  const [offset, setOffset] = useState(0)
  const [expanded, setExpanded] = useState<number | null>(null)

  const query = {
    event_type: eventType === ANY_TYPE ? undefined : eventType,
    limit: PAGE_SIZE,
    offset,
  }

  const events = useQuery({
    queryKey: queryKeys.events(query),
    queryFn: () => api.events(query),
  })

  const rows = events.data ?? []

  return (
    <div className="grid gap-3">
      <Select
        value={eventType}
        onValueChange={(value) => {
          setEventType(value as EventType | typeof ANY_TYPE)
          setOffset(0)
        }}
      >
        <SelectTrigger size="sm" className="w-full" aria-label="Filter by event type">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={ANY_TYPE}>all types</SelectItem>
          {EVENT_TYPES.map((type) => (
            <SelectItem key={type} value={type}>
              {type}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {events.isLoading && <Skeleton className="h-40 w-full" />}
      {!events.isLoading && rows.length === 0 && <EmptyState>No events yet.</EmptyState>}

      {rows.map((event) => {
        const hasPayload = Object.keys(event.payload ?? {}).length > 0
        return (
          <button
            key={event.id}
            type="button"
            data-testid={`event-${event.id}`}
            className="rounded-lg border p-3 text-left"
            onClick={() => hasPayload && setExpanded(expanded === event.id ? null : event.id)}
          >
            <div className="flex items-center justify-between gap-2">
              <Badge variant="outline" className="font-mono text-[0.65rem]">
                {event.event_type}
              </Badge>
              <span className="text-muted-foreground font-mono text-[0.65rem]">
                {formatDateTime(event.created_at)}
              </span>
            </div>
            <p className="mt-1.5 text-sm">{event.message}</p>
            {expanded === event.id && (
              <div className="mt-2">
                <JsonBlock value={event.payload} />
              </div>
            )}
          </button>
        )
      })}

      {(offset > 0 || rows.length === PAGE_SIZE) && (
        <div className="flex items-center justify-between gap-2">
          <Button
            size="sm"
            variant="outline"
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
          >
            Newer
          </Button>
          <span className="text-muted-foreground font-mono text-xs">
            {rows.length ? `${offset + 1}–${offset + rows.length}` : "—"}
          </span>
          <Button
            size="sm"
            variant="outline"
            disabled={rows.length < PAGE_SIZE}
            onClick={() => setOffset(offset + PAGE_SIZE)}
          >
            Older
          </Button>
        </div>
      )}
    </div>
  )
}

function PenaltiesPanel() {
  const { api } = useApi()
  const penalties = useQuery({
    queryKey: queryKeys.penalties,
    queryFn: () => api.penalties({ limit: PAGE_SIZE }),
  })

  if (penalties.isLoading) return <Skeleton className="h-32 w-full" />
  if (!penalties.data?.length) {
    return <EmptyState>No EXP lost yet. Keep it that way.</EmptyState>
  }

  return (
    <div className="grid gap-3">
      {penalties.data.map((penalty) => (
        <div key={penalty.id} className="flex items-start justify-between gap-3 rounded-lg border p-3">
          <div className="min-w-0">
            <p className="text-sm">{penalty.reason}</p>
            <p className="text-muted-foreground mt-1 font-mono text-[0.65rem]">
              {formatDateTime(penalty.created_at)}
            </p>
          </div>
          <span className="text-destructive shrink-0 font-mono">-{penalty.exp_lost}</span>
        </div>
      ))}
    </div>
  )
}

function RequestsPanel() {
  const { api } = useApi()
  const exchanges = useExchanges()
  const [expanded, setExpanded] = useState<number | null>(null)

  return (
    <div className="grid gap-3">
      <div className="flex items-center justify-between">
        <span className="text-muted-foreground text-xs">
          Every call this page has made. Tap for the JSON.
        </span>
        <Button size="sm" variant="outline" onClick={() => api.clearExchanges()}>
          Clear
        </Button>
      </div>

      {exchanges.length === 0 && <EmptyState>Nothing yet.</EmptyState>}

      {exchanges.map((exchange) => (
        <button
          key={exchange.id}
          type="button"
          data-testid={`exchange-${exchange.id}`}
          className="rounded-lg border p-3 text-left"
          onClick={() => setExpanded(expanded === exchange.id ? null : exchange.id)}
        >
          <div className="flex items-center gap-2 font-mono text-xs">
            <span className="text-muted-foreground w-12 shrink-0">{exchange.method}</span>
            <span className="min-w-0 flex-1 truncate">{exchange.path}</span>
            <span className={statusTone(exchange.status)}>{exchange.status || "ERR"}</span>
          </div>
          <div className="text-muted-foreground mt-1 flex justify-between font-mono text-[0.65rem]">
            <span>{formatTime(exchange.at)}</span>
            <span>{exchange.ms} ms</span>
          </div>
          {expanded === exchange.id && (
            <div className="mt-2 grid gap-2">
              {exchange.request != null && (
                <>
                  <span className="text-muted-foreground text-[0.65rem] tracking-[0.1em] uppercase">
                    Request
                  </span>
                  <JsonBlock value={exchange.request} />
                </>
              )}
              <span className="text-muted-foreground text-[0.65rem] tracking-[0.1em] uppercase">
                Response
              </span>
              <JsonBlock value={exchange.response} />
            </div>
          )}
        </button>
      ))}
    </div>
  )
}
