# System — web client

A React client for driving the [System API](../README.md) by hand: register,
author quests, log progress, write quotes, run the daily reset, and watch every
request the page makes.

The iOS app is the real client. This one exists so the API can be exercised
without it, over the same public endpoints — and it is **a phone UI only**.
There is no desktop layout: one column at phone width, a bottom tab bar, and
sheets instead of side-by-side panels. On a big screen the same UI sits centred
at 430px rather than reflowing into something the app will never look like.

Open it on a real phone with `npm run dev` — the dev server listens on the
local network, so `http://<your-machine>:5173/web/` works from a device on the
same Wi-Fi. It declares the iOS web-app meta tags, so Add to Home Screen gives
you a full-screen version to poke at.

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
    quests/            # the board, the card, the authoring sheet
    sky/               # the pantheon: standing, asking to be befriended,
                       #   and the trial of admission that decides it
    quotes/            # the collection and today's pick
    system/            # events, penalties, and what went over the wire
    workspace.tsx      # the bottom tab bar and the screens it switches
  components/ui/       # shadcn components, unmodified
```

Six tabs is the ceiling at phone width: the event log, the penalty ledger and
the request log share the System screen rather than taking one each.

**Sky** is the pantheon. Each constellation shows your standing with it and
what asking would do right now — the API answers that with a `blocked_by`
reason, so the button says "will not hear you yet — ask in 7 days" instead of
finding out by asking. Asking opens a sheet, and the constellation's answer
lands in it: a refusal with the date you may ask again, or a trial of
admission you can open, accept, log progress on, and clear without leaving the
screen. Clearing it is what makes you friends.

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

The phone-only layout is deliberate here too: screens, tab bar, and sheets map
onto what the app will have, so a decision made here is a decision made once.

## Adding shadcn components

```bash
npx shadcn@latest add <component>
```

`components.json` is configured for this project (Vite, Radix base, the `@/`
alias, `src/index.css`), so components land in `src/components/ui` themed by
the tokens already defined there.
