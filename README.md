# System

A backend for running your life like a progression RPG — the *系統* / System
trope from manhwa such as *Solo Leveling*, built as a real API.

You accept quests, log progress against them, and earn EXP. EXP levels you up,
levels grant stat points, and stat points raise your stats. Daily quests reset
at your local midnight, and the ones you left unfinished **fail and cost you
EXP**. The penalty is what makes the loop mean something.

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

# Accept a daily quest
curl -X POST localhost:8000/quests -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{
    "title": "100 push-ups",
    "quest_type": "daily",
    "difficulty": "D",
    "target_count": 100,
    "unit": "reps",
    "stat_reward": "strength",
    "stat_reward_amount": 1
  }'

# Log reps as you do them; the quest clears itself at 100
curl -X POST localhost:8000/quests/1/progress -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"amount": 40}'

# Check your status window
curl localhost:8000/players/me -H "Authorization: Bearer $TOKEN"
```

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
| `POST`   | `/quests` | Accept a new quest |
| `GET`    | `/quests` | List quests (`?quest_type=`, `?include_archived=`) |
| `GET`    | `/quests/today` | Today's daily quests |
| `GET`    | `/quests/{id}` | Fetch one quest |
| `PATCH`  | `/quests/{id}` | Edit a quest |
| `DELETE` | `/quests/{id}` | Archive it (history is kept) |
| `POST`   | `/quests/{id}/progress` | Log progress |
| `POST`   | `/quests/{id}/complete` | Clear it outright |

### System
| Method | Path | Purpose |
| ------ | ---- | ------- |
| `POST` | `/system/daily-reset` | Roll the day over: fail lapsed dailies, issue today's |
| `GET`  | `/system/events` | The notification feed (`?event_type=`, `?limit=`, `?offset=`) |
| `GET`  | `/system/penalties` | Every EXP loss on record |

## How progression works

**The EXP curve.** Advancing from level *N* costs `100 × N^1.5`, rounded to a
multiple of ten: 100, 280, 520, 800, 1120, 1470… Both the base and the exponent
are settings, so you can retune the whole curve without touching code.

**Difficulty sets rewards.** A quest's rank determines its default EXP, which
you can override per quest:

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

## Daily quests and penalties

A daily quest is a template that spawns one instance per day. At your local
midnight, any instance still unfinished from a past date is marked **failed**,
and you lose EXP equal to that quest's reward (scaled by
`APP_PENALTY_EXP_MULTIPLIER`).

Two deliberate design decisions:

- **Penalties never de-level you.** EXP already banked into a level is
  permanent; only progress toward the *next* level is at risk. A bad week
  should sting without erasing months of work.
- **The floor is zero.** If you have less EXP than the penalty, you lose what
  you have and no more. The recorded `exp_lost` reflects what was actually
  taken, not what was owed.

The rollover is **idempotent within a local day** — running it repeatedly
neither double-penalizes nor duplicates quests — enforced by a unique
constraint on `(quest_id, quest_date)`.

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

Each player stores an IANA timezone, and the day turns at *their* local
midnight. For a player in `Asia/Seoul`, 20:00 UTC is already 05:00 the next
day. Changing your timezone shifts future rollovers; it does not re-date
instances that already exist.

## Layout

```
app/
  main.py              # create_app() factory + `app` ASGI entrypoint
  config.py            # Settings; progression tuning lives here
  db.py                # engine, session factory, declarative Base
  security.py          # Argon2 hashing, JWT encode/decode
  deps.py              # settings / db / current-player dependencies
  errors.py            # AppError hierarchy + JSON error envelope
  models/              # User, Player, Quest, QuestInstance, Penalty, SystemEvent
  schemas/             # Pydantic request/response models
  services/
    leveling.py        # pure EXP math — no ORM, no clock
    progression.py     # awarding EXP, level-ups, penalties, stat spending
    quests.py          # quest lifecycle
    daily.py           # the daily reset
    clock.py           # timezone-aware date handling
    status.py          # building the status window
  routers/             # health, auth, players, quests, system
alembic/               # migrations
scripts/daily_reset.py # cron entrypoint
tests/
```

The EXP math in `services/leveling.py` is deliberately pure — no database, no
clock, no settings object — which is what makes the curve cheap to test and
safe to retune.

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
- Quest actions return the quest, its instance, `exp_gained`, and `leveled_up`
  in one response, so a completion needs no follow-up request to animate a
  level-up.
- `GET /system/events` is the notification feed. Each entry carries a
  `payload` with structured detail — `new_level`, `stat_points_gained`,
  `exp_lost` — so you can render System-style popups without parsing strings.

## Not built yet

Titles and achievements, rank (E–S) and job classes, and multi-day dungeon
challenges were scoped out of v1. The event log and quest model leave room for
all three.
