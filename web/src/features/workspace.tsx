/** The signed-in surface: six tabs over the API. */

import { useState } from "react"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BoardView } from "@/features/quests/board-view"
import { LogView } from "@/features/log/log-view"
import { QuestsView } from "@/features/quests/quests-view"
import { QuotesView } from "@/features/quotes/quotes-view"
import { RequestsView } from "@/features/requests/requests-view"
import { StatusView } from "@/features/status/status-view"

const TABS = [
  { value: "status", label: "Status", render: () => <StatusView /> },
  { value: "board", label: "Board", render: () => <BoardView /> },
  { value: "quests", label: "Quests", render: () => <QuestsView /> },
  { value: "quotes", label: "Quotes", render: () => <QuotesView /> },
  { value: "log", label: "Log", render: () => <LogView /> },
  { value: "requests", label: "Requests", render: () => <RequestsView /> },
]

const STORAGE_KEY = "system.tab"

function remembered(): string {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY)
    return TABS.some((tab) => tab.value === value) ? value! : "status"
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
    >
      <TabsList className="mb-6 w-full justify-start overflow-x-auto">
        {TABS.map((entry) => (
          <TabsTrigger key={entry.value} value={entry.value}>
            {entry.label}
          </TabsTrigger>
        ))}
      </TabsList>

      {TABS.map((entry) => (
        <TabsContent key={entry.value} value={entry.value}>
          {entry.render()}
        </TabsContent>
      ))}
    </Tabs>
  )
}
