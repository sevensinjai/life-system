# Scheduling, reset, and penalties

## Purpose

Authored quests use player-local calendar periods. The daily reset closes lapsed periods, applies failures and EXP penalties, opens periods now due, and settles expired side-quest offers. It is safe to call at launch and foreground because it is idempotent within the resulting periods.

## Schedule kinds

- `once` — opens once and never lapses.
- `daily` — one local calendar day.
- `weekdays` — chosen weekdays, each one day; Monday is `0`.
- `interval` — anchored repeating window of N days.
- `weekly` — seven-day window beginning on `week_start`.

Core pure operations are `validate`, `current_period`, `next_occurrence`, and `describe` in `app/services/scheduling.py`.

## Public API and jobs

- `POST /system/daily-reset` — reset one authenticated player.
- `GET /system/penalties` — paginated penalty history.
- `scripts/daily_reset.py` and Worker scheduled handling reset all players in production.
- Cloudflare cron configuration is in `wrangler.jsonc`; Worker dispatch is in `worker.py`.

## Invariants

- Calendar calculations use `Player.timezone`; side quests use absolute UTC instants instead.
- Only active, unfinished, lapsed authored instances fail.
- A one-time instance has `period_end = null` and never fails from time passage.
- Unique quest period rows prevent duplicate opening on repeated reset.
- Penalty records retain a textual reason and use nullable `SET NULL` references so history survives source deletion.
- Ignored/declined side quests never incur penalties; only accepted unfinished offers with a configured penalty can lose EXP.
- Reset writes a summary System event and returns counts/losses.

## Clients and gaps

- Web runs reset from the status screen and exposes log/penalty information in the System screen.
- iOS calls reset once when the dashboard enters. Its offline-first store now settles every lapsed active recurring instance, deducts at most the player's current-level EXP, records durable failure/penalty/reset events and penalty metadata, and opens the period currently due. Stored period-start identity makes repeated reset idempotent. Quest creation discloses the maximum loss alongside the reward. The app has no penalty-history screen and does not yet observe every subsequent foreground transition.

## Verification

- Primary tests: `tests/test_scheduling.py`, `tests/test_schedule_lifecycle.py`, `tests/test_daily.py`, and side-quest lifecycle tests.
- Freeze/override time in tests; cover timezone boundaries, repeat reset, missing days, weekly/interval anchors, and combined quest/side-quest settlement.
- The iOS `-dailyResetProof` Debug journey backdates a daily period, funds current EXP, runs reset twice, and checks failure, one-time loss, respawn, and events. Relaunching the proof also exercises decoding and mutation of the persisted snapshot.
