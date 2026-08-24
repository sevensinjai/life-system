/** The quote collection and the one line a day it surfaces. */

import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
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
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { Textarea } from "@/components/ui/textarea"
import { useApi } from "@/hooks/use-api"
import { formatDate, formatDateTime, plural } from "@/lib/format"
import { queryKeys } from "@/lib/query-keys"
import { parseBulkQuotes } from "@/lib/bulk-quotes"
import type { Quote } from "@/lib/types"

export function QuotesView() {
  const { api } = useApi()
  const queryClient = useQueryClient()

  const [includeArchived, setIncludeArchived] = useState(false)
  const [draft, setDraft] = useState({ text: "", author: "" })
  const [bulk, setBulk] = useState("")
  const [editing, setEditing] = useState<Quote | null>(null)

  const today = useQuery({
    queryKey: queryKeys.quoteToday,
    queryFn: () => api.quoteOfTheDay(),
  })

  const quotes = useQuery({
    queryKey: queryKeys.quoteList(includeArchived),
    queryFn: () => api.quotes({ include_archived: includeArchived || undefined }),
  })

  const refreshQuotes = () =>
    queryClient.invalidateQueries({ queryKey: queryKeys.quotes })

  const addOne = useMutation({
    mutationFn: () =>
      api.createQuote({ text: draft.text, author: draft.author.trim() || null }),
    onSuccess: () => {
      setDraft({ text: "", author: "" })
      toast.success("Quote added to the rotation.")
      void refreshQuotes()
    },
  })

  const addBatch = useMutation({
    mutationFn: () => api.createQuotes(parseBulkQuotes(bulk)),
    onSuccess: (result) => {
      setBulk("")
      toast.success(
        `Added ${result.created_count}` +
          (result.skipped_count
            ? `, skipped ${plural(result.skipped_count, "duplicate")}.`
            : ".")
      )
      void refreshQuotes()
    },
  })

  const save = useMutation({
    mutationFn: (quote: Quote) =>
      api.updateQuote(quote.id, {
        text: quote.text,
        author: quote.author?.trim() || null,
        is_active: quote.is_active,
      }),
    onSuccess: () => {
      setEditing(null)
      toast.success("Quote updated.")
      void refreshQuotes()
    },
  })

  const retire = useMutation({
    mutationFn: (id: number) => api.archiveQuote(id),
    onSuccess: () => {
      toast("Quote retired. It keeps its id.")
      void refreshQuotes()
    },
  })

  const restore = useMutation({
    mutationFn: (id: number) => api.updateQuote(id, { is_active: true }),
    onSuccess: () => {
      toast.success("Quote back in rotation.")
      void refreshQuotes()
    },
  })

  return (
    <>
      <div className="grid items-start gap-6 lg:grid-cols-2">
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Today's quote</CardTitle>
              <CardDescription>
                A pure read — no daily reset needed, and stable all day.
              </CardDescription>
              <CardAction>
                <Badge variant="outline" className="font-mono text-xs">
                  {formatDate(today.data?.local_date)}
                </Badge>
              </CardAction>
            </CardHeader>
            <CardContent className="grid gap-3">
              {today.isLoading && <Skeleton className="h-24 w-full" />}
              {today.data &&
                (today.data.quote ? (
                  <figure className="grid gap-2">
                    <blockquote className="text-xl leading-relaxed">
                      &ldquo;{today.data.quote.text}&rdquo;
                    </blockquote>
                    <figcaption className="text-muted-foreground text-sm">
                      — {today.data.quote.author ?? "you"} ·{" "}
                      <span className="font-mono">#{today.data.quote.id}</span>
                    </figcaption>
                  </figure>
                ) : (
                  <EmptyState>Nothing in rotation yet. Write one below.</EmptyState>
                ))}
              {today.data && (
                <p className="text-muted-foreground font-mono text-xs">
                  pool {today.data.pool_size} · turns over{" "}
                  {formatDateTime(today.data.refresh_after)}
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Write a quote</CardTitle>
            </CardHeader>
            <CardContent>
              <form
                className="grid gap-4"
                onSubmit={(event) => {
                  event.preventDefault()
                  addOne.mutate()
                }}
              >
                <div className="grid gap-2">
                  <Label htmlFor="quote-text">Text</Label>
                  <Input
                    id="quote-text"
                    maxLength={500}
                    required
                    placeholder="Arise."
                    value={draft.text}
                    onChange={(event) => setDraft({ ...draft, text: event.target.value })}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="quote-author">Author</Label>
                  <Input
                    id="quote-author"
                    maxLength={120}
                    placeholder="leave blank for your own"
                    value={draft.author}
                    onChange={(event) =>
                      setDraft({ ...draft, author: event.target.value })
                    }
                  />
                </div>
                <Button type="submit" disabled={addOne.isPending}>
                  Add
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Paste a batch</CardTitle>
              <CardDescription>
                One per line, optionally <code className="font-mono">text -- author</code>
                . Duplicates already in rotation are skipped, not rejected.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form
                className="grid gap-4"
                onSubmit={(event) => {
                  event.preventDefault()
                  if (!parseBulkQuotes(bulk).length) {
                    toast.error("Nothing to add — write one quote per line.")
                    return
                  }
                  addBatch.mutate()
                }}
              >
                <Textarea
                  aria-label="Quotes, one per line"
                  className="min-h-32 font-mono text-xs"
                  placeholder={"Arise. -- The System\nHard days make hard people.\nOne more rep."}
                  value={bulk}
                  onChange={(event) => setBulk(event.target.value)}
                />
                <Button type="submit" variant="secondary" disabled={addBatch.isPending}>
                  Add batch
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Collection</CardTitle>
            <CardDescription>Newest first.</CardDescription>
            <CardAction>
              <Badge variant="outline" className="font-mono text-xs">
                {plural(quotes.data?.length ?? 0, "quote")}
              </Badge>
            </CardAction>
          </CardHeader>
          <CardContent className="grid gap-3">
            <Label htmlFor="include-retired" className="text-muted-foreground text-xs font-normal">
              <Checkbox
                id="include-retired"
                checked={includeArchived}
                onCheckedChange={(checked) => setIncludeArchived(checked === true)}
              />
              include retired
            </Label>

            {quotes.isLoading && <Skeleton className="h-32 w-full" />}
            {quotes.data?.length === 0 && (
              <EmptyState>No quotes yet. The lock screen has nothing to show.</EmptyState>
            )}
            {quotes.data?.map((quote) => (
              <article
                key={quote.id}
                className={`flex flex-wrap items-start justify-between gap-3 rounded-lg border p-3 ${
                  quote.is_active ? "" : "opacity-60"
                }`}
              >
                <div className="min-w-40 flex-1">
                  <p>&ldquo;{quote.text}&rdquo;</p>
                  <p className="text-muted-foreground mt-1 font-mono text-xs">
                    #{quote.id}
                    {quote.author ? ` · ${quote.author}` : ""}
                    {quote.is_active ? "" : " · retired"}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="ghost" onClick={() => setEditing(quote)}>
                    Edit
                  </Button>
                  {quote.is_active ? (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-destructive hover:text-destructive"
                      onClick={() => retire.mutate(quote.id)}
                    >
                      Retire
                    </Button>
                  ) : (
                    <Button size="sm" variant="ghost" onClick={() => restore.mutate(quote.id)}>
                      Restore
                    </Button>
                  )}
                </div>
              </article>
            ))}
          </CardContent>
        </Card>
      </div>

      <Dialog open={Boolean(editing)} onOpenChange={(open) => !open && setEditing(null)}>
        <DialogContent>
          {editing && (
            <form
              onSubmit={(event) => {
                event.preventDefault()
                save.mutate(editing)
              }}
            >
              <DialogHeader>
                <DialogTitle>Edit quote #{editing.id}</DialogTitle>
              </DialogHeader>

              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="edit-quote-text">Text</Label>
                  <Input
                    id="edit-quote-text"
                    maxLength={500}
                    required
                    value={editing.text}
                    onChange={(event) =>
                      setEditing({ ...editing, text: event.target.value })
                    }
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="edit-quote-author">Author</Label>
                  <Input
                    id="edit-quote-author"
                    maxLength={120}
                    value={editing.author ?? ""}
                    onChange={(event) =>
                      setEditing({ ...editing, author: event.target.value })
                    }
                  />
                </div>
                <Label htmlFor="edit-quote-active" className="font-normal">
                  <Checkbox
                    id="edit-quote-active"
                    checked={editing.is_active}
                    onCheckedChange={(checked) =>
                      setEditing({ ...editing, is_active: checked === true })
                    }
                  />
                  in rotation
                </Label>
              </div>

              <DialogFooter>
                <Button type="button" variant="ghost" onClick={() => setEditing(null)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={save.isPending}>
                  Save
                </Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}
