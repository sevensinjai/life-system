/** Where you sit in one constellation's regard. */

import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { Standing } from "@/lib/types"

// Standing is a story value and never a punishment, so the bad end is muted
// rather than alarming: the worst a constellation does is lose interest.
const TONE: Record<Standing, string> = {
  forsaken: "text-muted-foreground border-muted-foreground/30 line-through",
  slighted: "text-muted-foreground border-muted-foreground/30",
  stranger: "text-muted-foreground",
  noticed: "text-primary border-primary/40",
  favored: "text-primary border-primary/60 bg-primary/10",
  champion: "text-chart-4 border-chart-4/60 bg-chart-4/10",
}

export function StandingBadge({
  standing,
  favor,
  className,
}: {
  standing: Standing
  favor?: number
  className?: string
}) {
  return (
    <Badge variant="outline" className={cn("font-mono text-[0.65rem]", TONE[standing], className)}>
      {standing}
      {favor === undefined ? "" : ` ${favor > 0 ? "+" : ""}${favor}`}
    </Badge>
  )
}
