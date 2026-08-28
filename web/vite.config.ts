import path from "node:path"

import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// The client is served from /web by the API in production, and from Vite's own
// dev server (proxying to the API) while developing.
export default defineConfig({
  base: process.env.LIFE_SYSTEM_CLOUDFLARE ? "/" : "/web/",
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    // Reachable from a phone on the same network, which is the point.
    host: true,
    proxy: Object.fromEntries(
      [
        "/auth",
        "/players",
        "/quests",
        "/skills",
        "/quotes",
        "/side-quests",
        "/constellations",
        "/system",
        "/health",
        "/openapi.json",
      ].map((route) => [route, { target: "http://127.0.0.1:8000", changeOrigin: true }])
    ),
  },
})
