# System

A backend for running your life like a progression RPG — the *系統* / System
trope from manhwa such as *Solo Leveling*, built as a real API.

You **design your own quests**, then run them. Quests earn EXP, EXP levels you
up, levels grant stat points, and stat points raise your stats. Recurring
quests open a period on whatever schedule you author, and a period that closes
unfinished **fails and costs you EXP**. The penalty is what makes the loop mean
something.

You also keep a collection of **motivational quotes** you write yourself, and
the System puts one of them on your lock screen each day.

Built backend-first so an iOS client can sit on top of it.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env
alembic upgrade head
```

## Run

```bash
uvicorn app.main:app --reload
```

- Interactive docs: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Test

```bash
pytest
```

## The loop

```bash
# Register — you get a token back immediately
curl -X POST localhost:8000/auth/register -H 'Content-Type: application/json' -d '{
  "email": "me@example.com",
  "password": "your-password",
  "name": "Sung Jinwoo",
  "timezone": "Asia/Seoul"
}'

TOKEN=...   # access_token from the response

# Design a quest: 100 push-ups, every Mon/Wed/Fri, worth C-rank EXP
curl -X POST localhost:8000/quests -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{
    "title": "100 push-ups",
    "schedule": { "kind": "weekdays", "days": [0, 2, 4] },
    "difficulty": "C",
    "target_count": 100,
    "unit": "reps",
    "stat_reward": "strength",
    "stat_reward_amount": 1
  }'

# Log reps as you do them; the quest clears itself at 100
curl -X POST localhost:8000/quests/1/progress -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"amount": 40}'

# What is on the board right now
curl localhost:8000/quests/today -H "Authorization: Bearer $TOKEN"
```

## Authoring quests

You are both the designer and the player. A quest is yours alone — nothing is
shared or published — so you can tune the difficulty and rewards honestly.

Every quest has a **schedule**, which decides when it opens a **period** and
how long that period stays open:

| `kind` | Meaning | Period length | Extra fields |
| ------ | ------- | ------------- | ------------ |
| `once` | No recurrence; waits until you clear it | never closes | — |
| `daily` | Every day | 1 day | — |
| `weekdays` | Only on chosen days | 1 day | `days`, e.g. `[0,2,4]` |
| `interval` | Every N days | N days | `interval_days` |
| `weekly` | Once a week | 7 days | `week_start` (optional) |

`days` are `0 = Monday` through `6 = Sunday`. `anchor` sets the day a
recurrence counts from, and defaults to the day you authored the quest.

**"Three runs a week"** is a `weekly` quest with `target_count: 3` and
`unit: "runs"` — you log one run at a time and it clears when the third lands.
Because everything is expressed as *progress toward a target inside a period*,
every schedule kind behaves identically; only the window changes.

```jsonc
// Every 3 days, and you get the full 3 days to do it
{ "title": "Deep clean", "schedule": { "kind": "interval", "interval_days": 3 } }

// Three runs a week, any days you like
{ "title": "Run", "schedule": { "kind": "weekly" }, "target_count": 3, "unit": "runs" }
```

Editing a quest applies from the next period onward — the open one is left
alone rather than retroactively re-dated. Changing an interval's length keeps
the original anchor, so re-tuning a quest does not silently restart its cycle.

## Endpoints

### Auth
| Method | Path | Purpose |
| ------ | ---- | ------- |
| `POST` | `/auth/register` | Create an account and player profile; returns a token |
| `POST` | `/auth/login` | Exchange credentials for a token |
| `GET`  | `/auth/me` | The authenticated account |

### Player
| Method | Path | Purpose |
| ------ | ---- | ------- |
| `GET`   | `/players/me` | Status window: level, EXP, stats, unspent points |
| `PATCH` | `/players/me` | Change name or timezone |
| `POST`  | `/players/me/allocate` | Spend stat points |

### Quests
| Method | Path | Purpose |
| ------ | ---- | ------- |
| `POST`   | `/quests` | Author a new quest |
| `GET`    | `/quests` | List quests (`?schedule=`, `?recurring_only=`, `?include_archived=`) |
| `GET`    | `/quests/today` | Everything with a period open right now |
| `GET`    | `/quests/{id}` | Fetch one quest |
| `PATCH`  | `/quests/{id}` | Redesign a quest |
| `DELETE` | `/quests/{id}` | Archive it (history is kept) |
| `POST`   | `/quests/{id}/progress` | Log progress |
| `POST`   | `/quests/{id}/complete` | Clear it outright |

### Quotes
| Method | Path | Purpose |
| ------ | ---- | ------- |
| `POST`   | `/quotes` | Write a quote |
| `POST`   | `/quotes/bulk` | Write a batch of them |
| `GET`    | `/quotes` | Your collection (`?include_archived=`) |
| `GET`    | `/quotes/today` | Today's quote — what the lock screen renders |
| `GET`    | `/quotes/{id}` | Fetch one, archived included |
| `PATCH`  | `/quotes/{id}` | Reword, re-attribute, or restore it |
| `DELETE` | `/quotes/{id}` | Retire it from the rotation |

### System
| Method | Path | Purpose |
| ------ | ---- | ------- |
| `POST` | `/system/daily-reset` | Roll periods over: lapse the closed, open the due |
| `GET`  | `/system/events` | The notification feed (`?event_type=`, `?limit=`, `?offset=`) |
| `GET`  | `/system/penalties` | Every EXP loss on record |

## How progression works

**The EXP curve.** Advancing from level *N* costs `100 × N^1.5`, rounded to a
multiple of ten: 100, 280, 520, 800, 1120, 1470… Both the base and the exponent
are settings, so you can retune the whole curve without touching code.

**Difficulty sets rewards.** A quest's rank determines its default EXP, which
you can override per quest when you author it:

| Rank | E | D | C | B | A | S |
| ---- | - | - | - | - | - | - |
| EXP | 50 | 100 | 200 | 400 | 800 | 1600 |

**Levels grant stat points.** Three per level by default, spent freely across
strength, agility, vitality, intelligence, and perception. Allocation is
all-or-nothing: an unaffordable request is rejected whole rather than partly
applied.

**Quests can also grant stats directly.** `stat_reward` and
`stat_reward_amount` pay out on completion, on top of EXP — so push-ups can
raise strength specifically.

## Penalties

When a period closes with its target unmet, the instance is marked **failed**
and you lose EXP equal to that quest's reward (scaled by
`APP_PENALTY_EXP_MULTIPLIER`).

The rule is uniform across schedules: *a period that ended before today
lapses*. A daily quest lapses the next day; a weekly quest survives midweek and
lapses when the week turns; an "every 3 days" quest lapses only when the fourth
day opens the next window. One-time quests have no period end, so they never
lapse — they wait indefinitely.

Two deliberate design decisions:

- **Penalties never de-level you.** EXP already banked into a level is
  permanent; only progress toward the *next* level is at risk. A bad week
  should sting without erasing months of work.
- **The floor is zero.** If you have less EXP than the penalty, you lose what
  you have and no more. The recorded `exp_lost` reflects what was actually
  taken, not what was owed.

The rollover is **idempotent within a local day** — running it repeatedly
neither double-penalizes nor duplicates periods — enforced by a unique
constraint on `(quest_id, period_start)`.

### Triggering the rollover

`POST /system/daily-reset` performs it for the calling player. Call it when the
app launches or returns to the foreground; it is cheap and safe to repeat.

Read endpoints never mutate state, so the rollover only happens when something
asks for it. If you want penalties to land on time even when the app goes
unopened for days, run the job from cron as well:

```cron
*/15 * * * * cd /srv/system && .venv/bin/python -m scripts.daily_reset
```

Run it at least hourly — players in different timezones cross midnight at
different moments.

### Timezones

Each player stores an IANA timezone, and periods turn at *their* local
midnight. For a player in `Asia/Seoul`, 20:00 UTC is already 05:00 the next
day. Changing your timezone shifts future rollovers; it does not re-date
periods that already exist.

## Daily quotes

Alongside quests you keep a collection of motivational lines — written by you,
for you — and the System puts one of them on your lock screen each day.

```bash
# Write a few in one go
curl -X POST localhost:8000/quotes/bulk -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{
    "quotes": [
      { "text": "Arise.", "author": "The System" },
      { "text": "Hard days make hard people." },
      { "text": "One more rep." }
    ]
  }'

# What the widget asks for
curl localhost:8000/quotes/today -H "Authorization: Bearer $TOKEN"
```

```json
{
  "local_date": "2026-08-24",
  "quote": { "id": 2, "text": "Hard days make hard people.", "author": null,
             "is_active": true, "created_at": "2026-08-24T09:12:44" },
  "pool_size": 3,
  "refresh_after": "2026-08-24T15:00:00Z"
}
```

**One quote per local day, chosen by rotation.** Not a random draw, for two
reasons: the same day always resolves to the same quote no matter how often the
widget asks — so the lock screen never flickers between two lines — and
consecutive days step through the collection in order, so every quote gets a
turn before any of them repeats.

Which quote a day lands on is *computed* from the pool rather than stored, so
there is no state to roll over and no job to run: `/quotes/today` is a pure
read that works whether or not the app has been opened. The trade is that
adding or retiring a quote reshuffles which one future days land on. Today's
answer holds for as long as the pool does.

**The day turns at your local midnight**, the same one quests reset at.
`refresh_after` is the UTC instant that happens, so a widget can schedule its
own reload instead of polling.

**Duplicates are skipped, not rejected.** Writing quotes is a paste-a-list
activity, so a batch that repeats something already in your rotation adds only
what is new and tells you what it skipped. Matching ignores case, whitespace,
and attribution — the same words credited differently are still the same line
on a lock screen. Only *active* quotes are matched against, so re-adding
something you retired puts it back rather than silently doing nothing.

**Retiring is archiving, not deleting.** A retired quote leaves the rotation
but keeps its id, so a widget still holding yesterday's resolves it instead of
erroring. `PATCH is_active=true` puts it back.

## Layout

```
app/
  main.py              # create_app() factory + `app` ASGI entrypoint
  config.py            # Settings; progression tuning lives here
  db.py                # engine, session factory, declarative Base
  security.py          # Argon2 hashing, JWT encode/decode
  deps.py              # settings / db / current-player dependencies
  errors.py            # AppError hierarchy + JSON error envelope
  models/              # User, Player, Quest, QuestInstance, Quote, Penalty, SystemEvent
  schemas/             # Pydantic request/response models
  services/
    leveling.py        # pure EXP math — no ORM, no clock
    scheduling.py      # pure period math — when a quest is due, how long you have
    quotes.py          # the quote collection; pure rotation for the daily pick
    progression.py     # awarding EXP, level-ups, penalties, stat spending
    quests.py          # quest lifecycle
    daily.py           # the rollover
    clock.py           # timezone-aware date handling
    status.py          # building the status window
  routers/             # health, auth, players, quests, quotes, system
alembic/               # migrations
scripts/daily_reset.py # cron entrypoint
tests/
```

`services/leveling.py` and `services/scheduling.py` are deliberately pure — no
database, no clock, no settings object — which is what makes the EXP curve and
the schedule rules cheap to test exhaustively and safe to retune. The same
holds for `pick_for_day` in `services/quotes.py`.

## Errors

Every failure returns the same envelope, including unmatched routes and
request-validation failures:

```json
{ "error": { "code": "not_found", "message": "No quest with id 42." } }
```

Codes: `not_found`, `validation_error`, `unauthenticated`, `conflict`,
`http_error`, `internal_error`. Validation failures add a `details` array
naming the offending fields.

## Configuration

Settings load from environment variables prefixed `APP_`, or from `.env`.

| Variable | Default | Notes |
| -------- | ------- | ----- |
| `APP_ENVIRONMENT` | `development` | `development` \| `test` \| `production` |
| `APP_DATABASE_URL` | `sqlite:///./system.db` | Any SQLAlchemy URL |
| `APP_JWT_SECRET` | dev placeholder | **Required in production** |
| `APP_ACCESS_TOKEN_EXPIRE_MINUTES` | `20160` (14 days) | Long, since it is a phone app |
| `APP_CORS_ORIGINS` | `["*"]` | Narrow before deploying |
| `APP_EXP_CURVE_BASE` | `100` | EXP for level 1 → 2 |
| `APP_EXP_CURVE_EXPONENT` | `1.5` | How steeply the curve climbs |
| `APP_STAT_POINTS_PER_LEVEL` | `3` | Points granted per level |
| `APP_PENALTY_EXP_MULTIPLIER` | `1.0` | Multiple of quest reward lost on failure |

### Before deploying

The app refuses to start in production with a default or under-length signing
key. Generate a real one:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

Also narrow `APP_CORS_ORIGINS`, and switch `APP_DATABASE_URL` to Postgres if
you want more than one process writing at a time — SQLite's single-writer lock
is the practical limit here.

## Migrations

```bash
alembic upgrade head                              # apply
alembic revision --autogenerate -m "description"  # create after model changes
alembic downgrade -1                              # roll back one
```

The URL comes from application settings rather than `alembic.ini`, so
migrations always target the same database the app uses.

## Notes for the iOS client

- `POST /system/daily-reset` on launch and on foreground, before rendering.
- `GET /players/me` drives the status window; `exp_progress` is a 0–1 fraction
  ready for a progress bar.
- `GET /quests/today` is the main board: everything with an open period,
  ordered by deadline, with open-ended one-time quests last.
- Every quest carries `schedule.label` ("Every Mon, Wed, Fri") for display, and
  `next_due_date` for quests not currently open.
- `current_instance.period_end` is the deadline; null means no deadline.
- Quest actions return the quest, its instance, `exp_gained`, and `leveled_up`
  in one response, so a completion needs no follow-up request to animate a
  level-up.
- `GET /quotes/today` backs the lock-screen widget. It is a pure read — no
  daily-reset call needed first — and `refresh_after` is the exact instant the
  quote changes, which is what a WidgetKit timeline wants for its next reload.
  An empty collection returns `quote: null` rather than a 404, so render a
  prompt to write one instead of an error state.
- `GET /system/events` is the notification feed. Each entry carries a
  `payload` with structured detail — `new_level`, `stat_points_gained`,
  `exp_lost` — so you can render System-style popups without parsing strings.

## Not built yet

Titles and achievements, rank (E–S) and job classes, multi-day dungeon
challenges, quest chains, and reusable drafts or templates. The event log and
quest model leave room for all of them.

On the quote side: pinning a specific line to a specific day, tagging quotes so
a mood or a training block draws from its own pool, and a starter set to write
against instead of a blank collection.
