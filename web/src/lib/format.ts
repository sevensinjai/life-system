/** Formatting helpers shared by the views. Framework-free on purpose. */

/** The API sends naive UTC timestamps; make them explicit before parsing. */
export function parseInstant(value: string): Date {
  return new Date(/[zZ]|[+-]\d{2}:?\d{2}$/.test(value) ? value : `${value}Z`)
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—"
  const date = new Date(`${value}T00:00:00`)
  return Number.isNaN(date.valueOf())
    ? value
    : date.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—"
  const date = parseInstant(value)
  return Number.isNaN(date.valueOf()) ? value : date.toLocaleString()
}

export function formatTime(value: number | Date): string {
  const date = value instanceof Date ? value : new Date(value)
  return date.toLocaleTimeString(undefined, { hour12: false })
}

export function plural(count: number, word: string): string {
  return `${count} ${word}${count === 1 ? "" : "s"}`
}

export function percent(value: number, total: number): number {
  if (!total) return 0
  return Math.max(0, Math.min(100, Math.round((value / total) * 100)))
}

/** The browser's IANA timezone, for pre-filling registration. */
export function localTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC"
  } catch {
    return "UTC"
  }
}

export function statusTone(status: number): string {
  if (status === 0 || status >= 500) return "text-destructive"
  if (status >= 400) return "text-chart-4"
  return "text-chart-3"
}
