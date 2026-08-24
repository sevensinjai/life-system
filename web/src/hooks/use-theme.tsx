/** Dark by default — the System is a night-time overlay — with a light mode. */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"
import type { ReactNode } from "react"

export type Theme = "dark" | "light"

const STORAGE_KEY = "system.theme"

const ThemeContext = createContext<{ theme: Theme; toggle: () => void } | null>(null)

function stored(): Theme {
  try {
    return window.localStorage.getItem(STORAGE_KEY) === "light" ? "light" : "dark"
  } catch {
    return "dark"
  }
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(stored)

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark")
    try {
      window.localStorage.setItem(STORAGE_KEY, theme)
    } catch {
      // A blocked store just means the choice does not persist.
    }
  }, [theme])

  const toggle = useCallback(() => {
    setTheme((current) => (current === "dark" ? "light" : "dark"))
  }, [])

  const value = useMemo(() => ({ theme, toggle }), [theme, toggle])
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  const value = useContext(ThemeContext)
  if (!value) throw new Error("useTheme must be used inside <ThemeProvider>.")
  return value
}
