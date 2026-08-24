/** The notification feed and the penalty ledger. */

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { EmptyState } from "@/components/empty-state"
import { JsonBlock } from "@/components/json-block"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useApi } from "@/hooks/use-api"
import { formatDateTime } from "@/lib/format"
import { queryKeys } from "@/lib/query-keys"
import { EVENT_TYPES, type EventType } from "@/lib/types"

const PAGE_SIZE = 25
const ANY_TYPE = "all"

export function LogView() {
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

  const penalties = useQuery({
    queryKey: queryKeys.penalties,
    queryFn: () => api.penalties({ limit: PAGE_SIZE }),
  })

  const rows = events.data ?? []

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>System log</CardTitle>
          <CardDescription>
            Newest first. Rows carrying a payload expand — that structured detail is what
            drives System-style popups in the app.
          </CardDescription>
          <CardAction className="flex flex-wrap items-center gap-2">
            <Select
              value={eventType}
              onValueChange={(value) => {
                setEventType(value as EventType | typeof ANY_TYPE)
                setOffset(0)
              }}
            >
              <SelectTrigger size="sm" className="w-44" aria-label="Filter by event type">
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
            <Button
              size="sm"
              variant="outline"
              disabled={offset === 0}
              onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            >
              Newer
            </Button>
            <Badge variant="ghost" className="text-muted-foreground font-mono text-xs">
              {rows.length ? `${offset + 1}–${offset + rows.length}` : "—"}
            </Badge>
            <Button
              size="sm"
              variant="outline"
              disabled={rows.length < PAGE_SIZE}
              onClick={() => setOffset(offset + PAGE_SIZE)}
            >
              Older
            </Button>
          </CardAction>
        </CardHeader>
        <CardContent>
          {events.isLoading && <Skeleton className="h-40 w-full" />}
          {!events.isLoading && rows.length === 0 && <EmptyState>No events yet.</EmptyState>}
          {rows.length > 0 && (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-44">When</TableHead>
                    <TableHead className="w-40">Type</TableHead>
                    <TableHead>Message</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rows.map((event) => {
                    const hasPayload = Object.keys(event.payload ?? {}).length > 0
                    return (
                      <TableRow
                        key={event.id}
                        data-testid={`event-${event.id}`}
                        className={hasPayload ? "cursor-pointer" : undefined}
                        onClick={() =>
                          hasPayload && setExpanded(expanded === event.id ? null : event.id)
                        }
                      >
                        <TableCell className="text-muted-foreground font-mono text-xs">
                          {formatDateTime(event.created_at)}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="font-mono text-xs">
                            {event.event_type}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {event.message}
                          {expanded === event.id && (
                            <div className="mt-2">
                              <JsonBlock value={event.payload} />
                            </div>
                          )}
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Penalties</CardTitle>
          <CardDescription>Every EXP loss on record.</CardDescription>
        </CardHeader>
        <CardContent>
          {penalties.isLoading && <Skeleton className="h-24 w-full" />}
          {penalties.data?.length === 0 && (
            <EmptyState>No EXP lost yet. Keep it that way.</EmptyState>
          )}
          {penalties.data && penalties.data.length > 0 && (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-44">When</TableHead>
                    <TableHead>Reason</TableHead>
                    <TableHead className="w-24 text-right">EXP lost</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {penalties.data.map((penalty) => (
                    <TableRow key={penalty.id}>
                      <TableCell className="text-muted-foreground font-mono text-xs">
                        {formatDateTime(penalty.created_at)}
                      </TableCell>
                      <TableCell>{penalty.reason}</TableCell>
                      <TableCell className="text-destructive text-right font-mono">
                        -{penalty.exp_lost}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
