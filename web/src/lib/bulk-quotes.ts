/** Parsing for the paste-a-list case, kept pure so it is trivially testable. */

import type { QuoteDraft } from "@/lib/types"

const BULK_SEPARATOR = " -- "

/** One quote per line, with an optional " -- author" suffix. */
export function parseBulkQuotes(text: string): QuoteDraft[] {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const at = line.lastIndexOf(BULK_SEPARATOR)
      if (at === -1) return { text: line }
      return {
        text: line.slice(0, at).trim(),
        author: line.slice(at + BULK_SEPARATOR.length).trim() || null,
      }
    })
    .filter((quote) => quote.text.length > 0)
}
