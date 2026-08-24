/**
 * Every request this page has made, newest first.
 *
 * The reason to run a web client at all is to watch the API answer, so the
 * exchange log is a tab rather than something buried in devtools.
 */

import { Fragment, useState } from "react"

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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useApi } from "@/hooks/use-api"
import { useExchanges } from "@/hooks/use-exchanges"
import { formatTime, statusTone } from "@/lib/format"

export function RequestsView() {
  const { api } = useApi()
  const exchanges = useExchanges()
  const [expanded, setExpanded] = useState<number | null>(null)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Request log</CardTitle>
        <CardDescription>
          Click a row for the JSON that went out and came back.
        </CardDescription>
        <CardAction className="flex items-center gap-2">
          <Badge variant="outline" className="font-mono text-xs">
            {exchanges.length} recent
          </Badge>
          <Button size="sm" variant="outline" onClick={() => api.clearExchanges()}>
            Clear
          </Button>
        </CardAction>
      </CardHeader>
      <CardContent>
        {exchanges.length === 0 ? (
          <EmptyState>Nothing yet.</EmptyState>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-24">Time</TableHead>
                  <TableHead className="w-20">Method</TableHead>
                  <TableHead>Path</TableHead>
                  <TableHead className="w-20">Status</TableHead>
                  <TableHead className="w-20 text-right">Took</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {exchanges.map((exchange) => (
                  <Fragment key={exchange.id}>
                    <TableRow
                      data-testid={`exchange-${exchange.id}`}
                      className="cursor-pointer"
                      onClick={() =>
                        setExpanded(expanded === exchange.id ? null : exchange.id)
                      }
                    >
                      <TableCell className="text-muted-foreground font-mono text-xs">
                        {formatTime(exchange.at)}
                      </TableCell>
                      <TableCell className="font-mono text-xs">{exchange.method}</TableCell>
                      <TableCell className="font-mono text-xs">{exchange.path}</TableCell>
                      <TableCell className={`font-mono text-xs ${statusTone(exchange.status)}`}>
                        {exchange.status || "ERR"}
                      </TableCell>
                      <TableCell className="text-muted-foreground text-right font-mono text-xs">
                        {exchange.ms} ms
                      </TableCell>
                    </TableRow>
                    {expanded === exchange.id && (
                      <TableRow>
                        <TableCell colSpan={5}>
                          <div className="grid gap-3">
                            {exchange.request != null && (
                              <div className="grid gap-1">
                                <span className="text-muted-foreground text-xs tracking-[0.12em] uppercase">
                                  Request
                                </span>
                                <JsonBlock value={exchange.request} />
                              </div>
                            )}
                            <div className="grid gap-1">
                              <span className="text-muted-foreground text-xs tracking-[0.12em] uppercase">
                                Response
                              </span>
                              <JsonBlock value={exchange.response} />
                            </div>
                          </div>
                        </TableCell>
                      </TableRow>
                    )}
                  </Fragment>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
