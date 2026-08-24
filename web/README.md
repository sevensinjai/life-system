# System — web client

A React client for driving the [System API](../README.md) by hand: register,
author quests, log progress, write quotes, run the daily reset, and watch every
request the page makes.

The iOS app is the real client. This one exists so the API can be exercised
without it, over the same public endpoints.

## Develop

```bash
npm install
npm run dev          # http://localhost:5173, proxying the API on :8000
```

Run the API alongside it (`uvicorn app.main:app --reload` from the repo root).
Vite proxies `/auth`, `/players`, `/quests`, `/quotes`, `/system`, and
`/health` to it, so the browser sees one origin and CORS never enters into it.

## Build

```bash
npm run build        # type-checks, then emits dist/
npm run lint
```

`dist/` is what the API serves at `/web` — see **Web client** in the root
README. It is gitignored, so a fresh clone needs one `npm run build` before
`uvicorn` can serve the client.

## Stack

- **React 19** + **TypeScript**, built by **Vite**
- **Tailwind v4** for styling, themed with **shadcn/ui** design tokens
- **shadcn/ui** components (Radix primitives) in `src/components/ui`
- **TanStack Query** for server state — one cache, invalidated by key

## Layout

```
src/
  lib/
    api.ts             # the API client: fetch, error envelope, request log
    types.ts           # the API's shapes, mirroring app/schemas
    format.ts          # dates, percentages, plurals
    bulk-quotes.ts     # "one quote per line" parsing
    query-keys.ts      # every cache key, and what a quest action invalidates
  hooks/
    use-api.tsx        # the client as context + signed-in state
    use-theme.tsx      # dark/light
    use-exchanges.ts   # the request log, via useSyncExternalStore
  features/
    auth/              # register and log in
    status/            # status window, allocation, profile, daily reset
    quests/            # the board, the designer, the edit dialog
    quotes/            # the collection and today's pick
    log/               # events and penalties
    requests/          # what went over the wire
    workspace.tsx      # the tab shell
  components/ui/       # shadcn components, unmodified
```

## Sharing this with an iOS app

If the iOS client ends up in React Native, the split above is the reusable
part: `src/lib` and `src/hooks/use-api.tsx` carry over as-is — no DOM, no
browser globals beyond `fetch`, and storage is injected (`KeyValueStore`), so
`browserStore()` becomes an AsyncStorage-backed store and nothing else moves.
TanStack Query runs unchanged there too.

What does *not* carry over is `src/components/ui`: shadcn/ui is built on Radix,
which is DOM-only. The React Native equivalents are NativeWind for the Tailwind
class names and a component set such as react-native-reusables, which follows
shadcn's copy-the-source model. Keep view logic in `features/` thin and the
swap stays mechanical.

## Adding shadcn components

```bash
npx shadcn@latest add <component>
```

`components.json` is configured for this project (Vite, Radix base, the `@/`
alias, `src/index.css`), so components land in `src/components/ui` themed by
the tokens already defined there.
