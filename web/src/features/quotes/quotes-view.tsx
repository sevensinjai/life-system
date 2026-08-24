/** The quote collection and the one line a day it surfaces. */

import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ListPlus, Plus } from "lucide-react"
import { toast } from "sonner"

import { EmptyState } from "@/components/empty-state"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import { Textarea } from "@/components/ui/textarea"
import { useApi } from "@/hooks/use-api"
import { parseBulkQuotes } from "@/lib/bulk-quotes"
import { formatDate, formatDateTime, plural } from "@/lib/format"
import { queryKeys } from "@/lib/query-keys"
import type { Quote } from "@/lib/types"

type Editor = { mode: "write" } | { mode: "batch" } | { mode: "edit"; quote: Quote }

export function QuotesView() {
  const { api } = useApi()
  const queryClient = useQueryClient()

  const [includeArchived, setIncludeArchived] = useState(false)
  const [editor, setEditor] = useState<Editor | null>(null)
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

  const close = () => {
    setEditor(null)
    setEditing(null)
  }

  const addOne = useMutation({
    mutationFn: () =>
      api.createQuote({ text: draft.text, author: draft.author.trim() || null }),
    onSuccess: () => {
      setDraft({ text: "", author: "" })
      close()
      toast.success("Quote added to the rotation.")
      void refreshQuotes()
    },
  })

  const addBatch = useMutation({
    mutationFn: () => api.createQuotes(parseBulkQuotes(bulk)),
    onSuccess: (result) => {
      setBulk("")
      close()
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
      close()
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
    <div className="grid gap-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Today's quote</CardTitle>
          <CardAction>
            <Badge variant="outline" className="font-mono text-xs">
              {formatDate(today.data?.local_date)}
            </Badge>
          </CardAction>
        </CardHeader>
        <CardContent className="grid gap-3">
          {today.isLoading && <Skeleton className="h-20 w-full" />}
          {today.data &&
            (today.data.quote ? (
              <figure className="grid gap-2">
                <blockquote className="text-lg leading-relaxed">
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
            <p className="text-muted-foreground font-mono text-[0.7rem]">
              pool {today.data.pool_size} · turns over{" "}
              {formatDateTime(today.data.refresh_after)}
            </p>
          )}
        </CardContent>
      </Card>

      <div className="flex gap-2">
        <Button className="flex-1" onClick={() => setEditor({ mode: "write" })}>
          <Plus /> Write
        </Button>
        <Button
          variant="secondary"
          className="flex-1"
          onClick={() => setEditor({ mode: "batch" })}
        >
          <ListPlus /> Paste batch
        </Button>
      </div>

      <div className="flex items-center justify-between">
        <h2 className="font-semibold">
          Collection{" "}
          <span className="text-muted-foreground font-mono text-xs">
            {quotes.data?.length ?? 0}
          </span>
        </h2>
        <Label htmlFor="include-retired" className="text-muted-foreground text-xs font-normal">
          <Checkbox
            id="include-retired"
            checked={includeArchived}
            onCheckedChange={(checked) => setIncludeArchived(checked === true)}
          />
          include retired
        </Label>
      </div>

      {quotes.isLoading && <Skeleton className="h-32 w-full" />}
      {quotes.data?.length === 0 && (
        <EmptyState>No quotes yet. The lock screen has nothing to show.</EmptyState>
      )}
      {quotes.data?.map((quote) => (
        <article
          key={quote.id}
          className={`rounded-lg border p-3 ${quote.is_active ? "" : "opacity-60"}`}
        >
          <p className="text-sm">&ldquo;{quote.text}&rdquo;</p>
          <div className="mt-2 flex items-center justify-between gap-2">
            <p className="text-muted-foreground font-mono text-[0.7rem]">
              #{quote.id}
              {quote.author ? ` · ${quote.author}` : ""}
              {quote.is_active ? "" : " · retired"}
            </p>
            <div className="flex shrink-0 gap-1">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setEditing(quote)
                  setEditor({ mode: "edit", quote })
                }}
              >
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
          </div>
        </article>
      ))}

      <Sheet open={Boolean(editor)} onOpenChange={(open) => !open && close()}>
        <SheetContent side="bottom" className="pb-safe max-h-[92vh] overflow-y-auto">
          {editor?.mode === "write" && (
            <form
              onSubmit={(event) => {
                event.preventDefault()
                addOne.mutate()
              }}
            >
              <SheetHeader>
                <SheetTitle>Write a quote</SheetTitle>
                <SheetDescription>
                  It joins the rotation immediately, though not necessarily as today's.
                </SheetDescription>
              </SheetHeader>
              <div className="grid gap-4 px-4">
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
                    onChange={(event) => setDraft({ ...draft, author: event.target.value })}
                  />
                </div>
              </div>
              <div className="p-4">
                <Button type="submit" className="w-full" disabled={addOne.isPending}>
                  Add
                </Button>
              </div>
            </form>
          )}

          {editor?.mode === "batch" && (
            <form
              onSubmit={(event) => {
                event.preventDefault()
                if (!parseBulkQuotes(bulk).length) {
                  toast.error("Nothing to add — write one quote per line.")
                  return
                }
                addBatch.mutate()
              }}
            >
              <SheetHeader>
                <SheetTitle>Paste a batch</SheetTitle>
                <SheetDescription>
                  One per line, optionally <code className="font-mono">text -- author</code>.
                  Duplicates already in rotation are skipped, not rejected.
                </SheetDescription>
              </SheetHeader>
              <div className="px-4">
                <Textarea
                  aria-label="Quotes, one per line"
                  className="min-h-40 font-mono text-xs"
                  placeholder={"Arise. -- The System\nHard days make hard people.\nOne more rep."}
                  value={bulk}
                  onChange={(event) => setBulk(event.target.value)}
                />
              </div>
              <div className="p-4">
                <Button type="submit" className="w-full" disabled={addBatch.isPending}>
                  Add batch
                </Button>
              </div>
            </form>
          )}

          {editor?.mode === "edit" && editing && (
            <form
              onSubmit={(event) => {
                event.preventDefault()
                save.mutate(editing)
              }}
            >
              <SheetHeader>
                <SheetTitle>Edit quote #{editing.id}</SheetTitle>
                <SheetDescription>
                  Retiring keeps the id, so a widget holding it still resolves.
                </SheetDescription>
              </SheetHeader>
              <div className="grid gap-4 px-4">
                <div className="grid gap-2">
                  <Label htmlFor="edit-quote-text">Text</Label>
                  <Input
                    id="edit-quote-text"
                    maxLength={500}
                    required
                    value={editing.text}
                    onChange={(event) => setEditing({ ...editing, text: event.target.value })}
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
              <div className="p-4">
                <Button type="submit" className="w-full" disabled={save.isPending}>
                  Save
                </Button>
              </div>
            </form>
          )}
        </SheetContent>
      </Sheet>
    </div>
  )
}
