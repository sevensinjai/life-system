import path from "node:path"

import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// The client is served from /web by the API in production, and from Vite's own
// dev server (proxying to the API) while developing.
export default defineConfig({
  base: "/web/",
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: Object.fromEntries(
      [
        "/auth",
        "/players",
        "/quests",
        "/quotes",
        "/system",
        "/health",
        "/openapi.json",
      ].map((route) => [route, { target: "http://127.0.0.1:8000", changeOrigin: true }])
    ),
  },
})
