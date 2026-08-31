# Quote rotation

## Purpose

Players maintain a private pool of motivational quotes. The System deterministically selects one active quote per player-local date for daily in-app presentation. Repeated reads during a day are stable; the next local midnight is returned for refresh scheduling.

## Public API

- `POST /quotes` — create one.
- `POST /quotes/bulk` — import many, reporting created and skipped duplicates.
- `GET /quotes` — list newest first, optionally include archived.
- `GET /quotes/today` — selected quote, pool size, local date, and `refresh_after`.
- `GET /quotes/{id}` — resolve active or archived quote.
- `PATCH /quotes/{id}` — edit or restore.
- `DELETE /quotes/{id}` — archive from rotation.

Contracts: `app/schemas/quote.py`; routes: `app/routers/quotes.py`; model: `app/models/quote.py`; selection/import rules: `app/services/quotes.py`.

## Invariants

- Quotes are player-private and never globally published.
- Text whitespace is normalized before storage/deduplication.
- Bulk import skips duplicates instead of failing the whole batch.
- Selection is deterministic from active quote IDs and local date, without storing a daily assignment.
- An empty pool is a successful response with `quote = null`.
- Archive is soft so a widget holding yesterday's ID can still resolve it.

## Clients and gaps

- Web collection and daily view: `web/src/features/quotes/quotes-view.tsx`.
- iOS shows the daily quote on the dashboard and still has no quote collection/editor screen.
- The WidgetKit extension no longer exposes the quote widget; its public widget is now Lock Screen quick actions. `QuoteWidgetSync.swift` and the dormant quote widget/provider code remain and should be removed or reactivated deliberately rather than treated as current UI.

## Verification

- Primary tests: `tests/test_quotes.py`, `tests/test_quote_rotation.py`.
- Cover normalization, duplicate import, player isolation, date stability/turnover, timezone refresh time, archive behavior, and empty pool.
