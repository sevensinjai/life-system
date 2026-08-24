/** The signed-in surface: a scrolling screen over a bottom tab bar. */

import { useState } from "react"
import { Gauge, ListChecks, Quote, ScrollText, Terminal } from "lucide-react"
import type { LucideIcon } from "lucide-react"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BoardView } from "@/features/quests/board-view"
import { QuestsView } from "@/features/quests/quests-view"
import { QuotesView } from "@/features/quotes/quotes-view"
import { SystemView } from "@/features/system/system-view"
import { StatusView } from "@/features/status/status-view"

interface Screen {
  value: string
  label: string
  icon: LucideIcon
  render: () => React.ReactNode
}

// Five, deliberately: a phone tab bar stops being tappable past that, so the
// event log and the request log share one "System" screen.
const SCREENS: Screen[] = [
  { value: "status", label: "Status", icon: Gauge, render: () => <StatusView /> },
  { value: "board", label: "Board", icon: ListChecks, render: () => <BoardView /> },
  { value: "quests", label: "Quests", icon: ScrollText, render: () => <QuestsView /> },
  { value: "quotes", label: "Quotes", icon: Quote, render: () => <QuotesView /> },
  { value: "system", label: "System", icon: Terminal, render: () => <SystemView /> },
]

const STORAGE_KEY = "system.tab"

function remembered(): string {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY)
    return SCREENS.some((screen) => screen.value === value) ? value! : "status"
  } catch {
    return "status"
  }
}

export function Workspace() {
  const [tab, setTab] = useState(remembered)

  return (
    <Tabs
      value={tab}
      onValueChange={(value) => {
        setTab(value)
        try {
          window.localStorage.setItem(STORAGE_KEY, value)
        } catch {
          // Not persisting the tab is survivable.
        }
      }}
      className="flex min-h-0 flex-1 flex-col gap-0"
    >
      <div className="flex-1 overflow-y-auto overscroll-contain px-4 pt-4 pb-6">
        {SCREENS.map((screen) => (
          <TabsContent key={screen.value} value={screen.value} className="mt-0">
            {screen.render()}
          </TabsContent>
        ))}
      </div>

      <TabsList className="pb-safe bg-background/95 h-auto w-full shrink-0 justify-around rounded-none border-t p-0 backdrop-blur">
        {SCREENS.map((screen) => (
          <TabsTrigger
            key={screen.value}
            value={screen.value}
            className="text-muted-foreground flex h-14 flex-1 flex-col items-center justify-center gap-1 rounded-none border-0 bg-transparent px-0 text-[0.65rem] font-medium data-[state=active]:text-primary data-[state=active]:bg-transparent data-[state=active]:shadow-none dark:data-[state=active]:bg-transparent dark:data-[state=active]:border-transparent dark:data-[state=active]:text-primary"
          >
            <screen.icon className="size-5" />
            {screen.label}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  )
}
