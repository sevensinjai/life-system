# Player progression and status

## Purpose and flow

The player has a level, EXP toward the next level, lifetime earned EXP, unspent stat points, and five stats: strength, agility, vitality, intelligence, and perception. Completing work awards EXP; crossing thresholds may gain multiple levels and grants stat points per level. Penalties can remove current EXP and levels but lifetime earned EXP remains historical.

## Public API

- `GET /players/me` — complete status window with derived EXP target/progress.
- `PATCH /players/me` — update hunter name or IANA timezone.
- `POST /players/me/allocate` — atomically spend points among five stats.

Contracts: `app/schemas/player.py`. Routes: `app/routers/players.py`.

## Ownership and services

- Persistence: `Player` in `app/models/player.py`.
- Status projection: `app/services/status.py`.
- Pure level math: `app/services/leveling.py`.
- Award, penalty, stat allocation, and event emission: `app/services/progression.py`.
- Tuning: `exp_curve_base`, `exp_curve_exponent`, `stat_points_per_level`, and `penalty_exp_multiplier` in `app/config.py`.

## Invariants

- `exp` is progress within the current level; `total_exp_earned` is lifetime positive awards.
- Allocation is all-or-nothing and cannot exceed available points or use negative values.
- Stat rewards on completed quests are separate from spendable stat points.
- A timezone edit changes future local-day interpretation; it does not re-date existing quest instances.
- Progression changes should write suitable System events through `log_event`.

## Clients and gaps

- Web status UI supports status, allocation, profile editing, daily reset, and account display in `web/src/features/status/status-view.tsx`.
- iOS opens on `DashboardView.swift`, which composes player progression, today's quote, active quest progress, attributes, and the latest System event. Tapping the level card drills into the Souls-style `StatusView.swift`, which loads `/players/me` and `/skills` together and presents identity, level/EXP, the five canonical stats, and skill mastery.
- “See all 100 attributes” opens ten groups of human ability/personality facets. These values are deterministic client-side projections from the five canonical stats; they are not independent persisted stats and cannot be allocated or trained separately.
- Stat allocation and profile editing are not yet implemented on iOS. Daily reset runs when the dashboard enters rather than from Player State.
- Offline iOS authored-quest penalties remove only EXP in the current level, never de-level the player, and do not reduce lifetime earned EXP; the durable penalty record stores the amount actually lost.

## Verification

- Primary tests: `tests/test_leveling.py`, `tests/test_players.py`; quest/side-quest tests cover integrated awards and losses.
- Cover exact threshold, multi-level awards, loss across level boundaries, zero floor, allocation atomicity, and configured curves.
