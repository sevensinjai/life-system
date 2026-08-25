# System

A backend for running your life like a progression RPG — the *系統* / System
trope from manhwa such as *Solo Leveling*, built as a real API.

You **design your own quests**, then run them. Quests earn EXP, EXP levels you
up, levels grant stat points, and stat points raise your stats. Recurring
quests open a period on whatever schedule you author, and a period that closes
unfinished **fails and costs you EXP**. The penalty is what makes the loop mean
something.

Quests also train **skills**, which level on their own curve. You design the
skill graph yourself — Singing holding Pitch accuracy holding Interval jumps —
and practising a sub-skill rolls EXP up the branch, so the skill above levels
off the work done inside it.

You also keep a collection of **motivational quotes** you write yourself, and
the System puts one of them on your lock screen each day.

And if you want it to, the System will occasionally hand you a **side quest**
of its own — the same one it broadcast to every other player who opted in.
Those come from **constellations**, who send only to the players they have
agreed to befriend, and who remember what you did with the last one.

Built backend-first so an iOS client can sit on top of it, with a
[web client](#web-client) served alongside the API for testing it by hand.

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

- Web client: http://127.0.0.1:8000/ (after `cd web && npm run build`)
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

## Side quests

Quests are yours: you write them, you tune them, nobody else sees them. A
**side quest** is the opposite — the System issues one to everybody at once,
on behalf of one of the [constellations](#the-constellations). You choose
whether any of it reaches you, twice over: once by opting in at all, and once
by [befriending](#befriending-a-constellation) the constellation that sent it.

### Opting in

Off until you turn it on. A player who has never answered the question has no
preference row at all, which reads as opted out — nobody is enrolled quietly.

```bash
curl -X PATCH localhost:8000/side-quests/preferences \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{
    "is_opted_in": true,
    "frequency": "occasional",
    "max_difficulty": "B",
    "auto_accept": false
  }'
```

| Setting | Meaning |
| ------- | ------- |
| `is_opted_in` | Whether broadcasts reach you at all |
| `frequency` | How many may reach you per rolling week: `rare` 1, `occasional` 3, `frequent` 7 |
| `max_difficulty` | The hardest rank you will be sent; `null` accepts anything |
| `auto_accept` | Skip the yes/no step and be counted in automatically |

The frequency cap is what "occasionally" actually means: the System broadcasts
as often as it likes, and this decides how much of that traffic you see. It is
measured over a rolling seven days, and a *declined* offer still uses a slot —
what you rationed is the interruption, not the acceptance.

Opting in takes effect immediately. Any broadcast still open that you are
eligible for is offered to you on the spot, up to your cap, rather than making
you wait for the next one. Opting out stops new offers but leaves anything you
already accepted alone; the System does not retract a quest you took up.

### The three tables

| Table | Scope | Holds |
| ----- | ----- | ----- |
| `side_quests` | one row for everyone | the broadcast: rewards, rank, audience, window |
| `side_quest_offers` | one row per player reached | their answer and their progress |
| `side_quest_preferences` | one row per player | the opt-in above |

An offer is unique per (side quest, player), which is what makes dispatch
idempotent: re-running a broadcast reaches only the players it missed the
first time — someone who opted in an hour late, or who was at their cap until
now.

Unlike quests, side quests run on **absolute UTC instants** rather than
player-local days. A broadcast reaches Seoul and São Paulo at the same moment,
so its window cannot be a calendar date. Offers snapshot the deadline and the
target count at dispatch, so retuning a broadcast mid-flight cannot move
anyone's goalposts.

### Ignoring one is free

Only an offer you **accepted** and then left unfinished can cost you EXP, and
only when the broadcast carried a `penalty_exp` at all (the default is zero).
The endings are recorded separately because they are different stories:

| Ending | When | Costs |
| ------ | ---- | ----- |
| `declined` | you passed on it | nothing |
| `expired` | you never answered before the window closed | nothing |
| `withdrawn` | the broadcast was cancelled | nothing |
| `completed` | you cleared it | pays EXP and any stat reward |
| `failed` | you accepted it, then the window closed short | the broadcast's penalty |

An optional system that punishes you for opting in is not optional, so the
only branch with teeth is the one you deliberately walked into.

### Getting broadcasts out

Three steps, deliberately separate: *what* goes out, *when* it goes out, and
*how it ends*.

```bash
# once at setup, and after any edit to the written pantheon
.venv/bin/python -m scripts.seed_pantheon

# daily: put the next written trial on the calendar, if the sky is quiet
0 9 * * * cd /srv/system && .venv/bin/python -m scripts.schedule_side_quest

# often: put scheduled trials in front of the players they are meant for
*/15 * * * * cd /srv/system && .venv/bin/python -m scripts.broadcast_side_quests
```

`schedule_side_quest` does nothing while a broadcast is still open, so trials
arrive one at a time rather than three at once, and it walks the catalog in
rotation — everything written is seen before anything repeats, with a 30-day
rest before a trial can come round again. Pass a catalog code to send a
specific one instead.

Offers are settled per player by `POST /system/daily-reset`, which the app
already calls on launch: unanswered offers expire for free, accepted ones that
fell short fail and pay their penalty.

## The constellations

A side quest comes from somebody. The pantheon is six of them, each with a
domain it cares about and a voice of its own — written by hand in
`app/content/pantheon.py` and seeded into the database, so a constellation is
a row a broadcast points at rather than a name typed into each one.

Nothing they issue reaches you until you have befriended them, so the pantheon
screen is where the game actually starts.

| Constellation | Domain | Cares about |
| ------------- | ------ | ----------- |
| The Fallen Star | strength | getting up after you did not |
| The Long Road | agility | distance covered, not destinations |
| The Empty Bowl | vitality | putting something down for a while |
| The Silent Library | intelligence | learning a thing well enough to say it |
| The Unblinking Eye | perception | noticing what you walk past |
| The Sleepless Lantern | — | coming back, however badly |

The trials themselves live in `app/content/broadcasts.py` — three per
constellation, written to be clearable by anyone, anywhere, with nothing to
buy. Each constellation also has one **trial of admission** in
`app/content/challenges.py`: the smallest true test of what it cares about,
set for whoever asks to be befriended.

### Befriending a constellation

A constellation issues trials to its friends and to nobody else, so opting in
is only half of it: until you have befriended somebody, nothing arrives. You
do not join a constellation — you ask, and it decides.

```bash
curl -X POST localhost:8000/constellations/fallen_star/friendship \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{ "message": "I fell too." }'
```

The answer comes back at once, and it is one of two things:

**Refused.** It would not hear you this time. `retry_after` says when you may
ask again — seven days by default (`APP_FRIENDSHIP_RETRY_DAYS`).

**Challenged.** It set you a **trial of admission**, which arrives as an
ordinary side quest: accept it, log progress, complete it through the same
endpoints as anything else. Clear it and you are friends. Fail it, decline it,
or let it lapse and the request closes with the same seven-day wait.

```
The Constellation of the Fallen Star: Not today. Ask me again when you have done something.
    ... seven days later ...
The Constellation of the Fallen Star: You asked. Twenty, then. Now.
The Constellation of the Fallen Star: Fine. You are one of mine. (+100 EXP)
```

Three things the trial of admission deliberately is not. It carries **no
penalty** — a stranger who fails an audition has lost the audition, which is
enough. It does not **spend your weekly cap**, because you asked for it and
the cap rations interruptions. And it is **addressed, not broadcast**: nobody
else can see it or be handed it.

Ending a friendship is a `DELETE` on the same path. Its trials stop reaching
you; your standing is left exactly where it stood, because the history
happened; and coming back waits out the same seven days, so this is not a
switch to flip twice a day. Anything you already accepted stays yours to
finish.

Every request is kept, refusals included — it is the record of how you got in.

#### Who decides, and how

Whether a request is heard is one function behind a protocol:

```python
class Arbiter(Protocol):
    def __call__(self, petition: Petition) -> Verdict: ...
```

Today that is `ChanceArbiter` — it hears `APP_FRIENDSHIP_ACCEPT_RATE` of
requests (30% by default) and reads nothing. It is a placeholder with the
manners of a real one: it takes the whole `Petition` and returns a `Verdict`
with a reason, both of which are stored. So the arbiter that actually *reads*
a request — the player's history, their standing with this constellation, what
they wrote in `message`, what the constellation cares about — is one callable,
with no call sites to change and a `verdict_reason` column already waiting for
its words.

At 30% with a seven-day wait, befriending one constellation takes about three
weeks on average, and an unlucky player can wait considerably longer. Both
numbers are settings for exactly that reason.

### Standing

Each constellation keeps a favor score on you, and the band that score falls
into is your **standing** with it: `forsaken`, `slighted`, `stranger`,
`noticed`, `favored`, `champion`. Everyone starts a stranger.

| What you did | Favor |
| ------------ | ----- |
| Cleared its trial | +3, and more the harder the rank (up to +13 at S) |
| Accepted, then let it lapse | −2, and worse the harder the rank |
| Declined it | −1, whatever the rank — you passed on the interruption, not the difficulty |
| Never answered | −2 |
| It withdrew the trial | nothing; that ending was its doing |

**Standing never touches EXP, levels, or stats.** That separation is the whole
reason favor is allowed to be harsh: the worst a constellation can do is lose
interest in you. Only a side quest you *accepted* and then abandoned costs
anything, and that is the broadcast's penalty, not the constellation's
opinion.

What standing does change is what you hear and what you are sent. A voice has
a line per outcome and can have a different one per band, so a constellation
does not greet a champion the way it greets a stranger, and a trial can carry
a `min_standing` reserving it for players who have earned its attention.

Standing and friendship are separate on purpose: favor is what a constellation
*thinks* of you, friendship is whether it *speaks* to you at all. You can be
its champion and still walk away; you can be slighted and still be a friend.

```
The Constellation of the Fallen Star: You do not know me yet. Get up anyway.
The Constellation of the Fallen Star: Then do it.
One hundred, in one day: 100/100
The Constellation of the Fallen Star: That is what standing up looks like. (+200 EXP)
```

The System log carries the voice; the title, rank, EXP and favor movement ride
on the event `payload`, so the feed reads as somebody talking while a client
still has structured data to render a card from.

### Writing more of it

Everything a player reads that is not built from their own data lives in
`app/content/`, as data rather than as strings in the services. A rewrite
shows up as a diff of what a constellation *says*, not of how the app works,
and re-running `scripts/seed_pantheon.py` updates the rows in place — matched
on `code`, so every player's history with that constellation survives the
edit.

Lines resolve most specific first: the trial's own line for your standing,
then its default, then the constellation's, then the plain System register. A
half-written voice degrades to "Side quest complete." rather than to silence,
so nothing has to be written before it is worth writing.

This is English-only for now. Nothing is interpolated — a line is a finished
sentence, and every number a client might want is on the payload — so adding
another language later means another catalog beside this one, not an audit of
every string in the codebase.

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

### Skills
| Method | Path | Purpose |
| ------ | ---- | ------- |
| `POST`   | `/skills` | Add a skill, optionally under another |
| `GET`    | `/skills` | Your graph, nested (`?include_archived=`) |
| `GET`    | `/skills/{id}` | One skill, with its breadcrumb and children |
| `PATCH`  | `/skills/{id}` | Rename, describe, move, archive or restore |
| `DELETE` | `/skills/{id}` | Archive it and everything under it |
| `POST`   | `/skills/{id}/practice` | Log practice no quest covers |

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

### Side quests
| Method | Path | Purpose |
| ------ | ---- | ------- |
| `GET`   | `/side-quests/preferences` | Your opt-in settings and this week's count |
| `PATCH` | `/side-quests/preferences` | Opt in or out, set frequency and rank cap |
| `GET`   | `/side-quests` | Side quests you were offered (`?status=`, `?live_only=`) |
| `GET`   | `/side-quests/{id}` | Fetch one offer |
| `POST`  | `/side-quests/{id}/accept` | Take it up |
| `POST`  | `/side-quests/{id}/decline` | Pass on it |
| `POST`  | `/side-quests/{id}/progress` | Log progress |
| `POST`  | `/side-quests/{id}/complete` | Clear it outright |

### Constellations
| Method | Path | Purpose |
| ------ | ---- | ------- |
| `GET`    | `/constellations` | The pantheon, each with your standing and friendship |
| `GET`    | `/constellations/{code}` | One of them |
| `POST`   | `/constellations/{code}/friendship` | Ask to be befriended |
| `DELETE` | `/constellations/{code}/friendship` | End a friendship |

### System
| Method | Path | Purpose |
| ------ | ---- | ------- |
| `POST` | `/system/daily-reset` | Roll periods over: lapse the closed, open the due, settle side quests |
| `GET`  | `/system/events` | The notification feed (`?event_type=`, `?limit=`, `?offset=`) |
| `GET`  | `/system/penalties` | Every EXP loss on record |

## Web client

The iOS app is the real client. Until it exists — and afterwards, when you want
to see what the API actually returns — there is a React client in
[`web/`](web/README.md) that covers every endpoint on this page.

It is **a phone UI**: one column at phone width, a bottom tab bar, and sheets
rather than side-by-side panels, so what you are testing looks like what the
app will be. On a desktop browser it sits centred at phone width instead of
reflowing. The dev server listens on the local network, so a real phone on the
same Wi-Fi can open it.

```bash
cd web
npm install
npm run dev     # http://localhost:5173, proxying the API on :8000
```

Run it against `uvicorn app.main:app --reload` in another shell. For a
single-process setup, build it once and the API serves it at `/web`, with `/`
redirecting there:

```bash
cd web && npm run build      # emits web/dist
uvicorn app.main:app         # http://127.0.0.1:8000/
```

`web/dist` is a build artifact and is not committed, so a fresh clone needs
that build before the API has anything to serve; without it the mount is
skipped and the API runs as usual.

It covers register and log in, the status window and stat allocation,
authoring and editing quests on any schedule, logging progress, clearing
quests, the quote collection and today's pick, the daily reset, the event feed,
and the penalty ledger. The **System** tab also lists every call the page has
made with its JSON, its status, and how long it took, so a failure is legible
without opening devtools.

Two things worth knowing:

- **The API target lives behind the gear icon.** Leave it blank to use the
  server that served the page; point it at another host to drive a deployed
  backend from a local page. That is a cross-origin request, so the target's
  `APP_CORS_ORIGINS` has to allow this page's origin.
- **The client talks to the API over the same public endpoints the app will**,
  so what works there works here. Nothing is rendered server-side and no route
  exists for its benefit.

The token lives in the browser's local storage, so a reload keeps you signed
in. Set `APP_WEB_CLIENT=false` to leave the client out of a deployment
entirely; the mount and the `/` redirect both disappear with it.

React 19, Vite, Tailwind v4, shadcn/ui, and TanStack Query — see
[`web/README.md`](web/README.md) for the layout, and for which parts are meant
to be shared with a React Native client.

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

**Skills level separately.** A quest with a `skill_id` also trains that skill
and everything above it in the graph; see [The skill graph](#the-skill-graph).
Player EXP and skill EXP are tracked independently — clearing a quest can level
you, the skill, both, or neither.

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

Side quests are penalized on the same terms but only when you accepted one:
see [Ignoring one is free](#ignoring-one-is-free). An offer you never answered
expires for nothing.

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

## The skill graph

The player has a level. So does every skill, on its own curve, and you decide
what the skills are.

```bash
# Design the graph
curl -X POST localhost:8000/skills -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{ "name": "Singing" }'

curl -X POST localhost:8000/skills -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{
    "name": "Pitch accuracy", "parent_id": 1
  }'

# A quest that trains it
curl -X POST localhost:8000/quests -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{
    "title": "Sing scales for 20 min",
    "schedule": { "kind": "daily" },
    "difficulty": "C",
    "skill_id": 2
  }'
```

Clearing that quest pays the player 200 EXP **and** trains the branch:

```
Singing         Lv.1 (0/100)     ->  Lv.2 (100/280)
  Pitch accuracy  Lv.1 (0/100)   ->  Lv.2 (100/280)
```

### Rolling up

**Practising a sub-skill is practising its parent.** EXP awarded to a skill is
credited to every skill above it, so Singing advances because Pitch accuracy
did. The completion response carries one entry per skill credited — the skill
trained first, then each step up — so a client can animate the whole branch
without refetching.

`APP_SKILL_EXP_ROLLUP` is the share that reaches each step up, compounding with
distance. At the default `1.0` a branch is credited in full; at `0.5` a parent
takes half and a grandparent a quarter; at `0.0` only the skill you trained
advances. The chain stops as soon as a share rounds to zero.

### Why a tree and not a general graph

Every skill has one parent, so every skill has exactly one path to its root.
That is what makes rolling EXP upward unambiguous — with two parents, a shared
ancestor could be credited twice for the same practice, and "how good am I at
Singing" would depend on which way you counted. The cost is that a sub-skill
cannot sit under two parents; **Breath control** under both Singing and
Swimming has to be two skills.

### Shaping it

Skills nest up to `APP_MAX_SKILL_DEPTH` levels (5 by default). Moving a skill
takes its subtree along, and two moves are refused outright:

- one that would make a skill its own ancestor, and
- one that would push a branch past the depth limit — measured against the
  *whole subtree*, so moving a three-level branch under a deep node is caught
  even though the moved skill itself would fit.

Siblings cannot share a name (case-insensitively); the same name under
different parents is fine.

### Practice time and skill EXP

One EXP is one minute of practice. A quest stores its estimated
`practice_minutes` and pays them only when the period is completed. Count-based
quests may instead provide `units_per_minute`; the System rounds
`target_count / units_per_minute` up to a whole minute. For example, 100
push-ups at 10 reps per minute are worth 10 practice minutes and therefore 10
player EXP plus 10 EXP for the linked skill.

The period snapshots its practice minutes when it opens, so editing the quest
does not change the value of work already underway. Parent-skill roll-up is
categorisation, not extra elapsed time: 10 minutes credited to Push-ups,
Calisthenics and Fitness still represents 10 real minutes overall.

| Source | How |
| ------ | --- |
| A quest | Give the quest a `skill_id`; completion credits its `practice_minutes` to both player and skill |
| Practice | `POST /skills/{id}/practice` with a `minutes` amount, for work no quest covers |

Skills level on the same curve shape as the player, tuned separately through
`APP_SKILL_EXP_CURVE_BASE` and `APP_SKILL_EXP_CURVE_EXPONENT` — so skills can
advance faster or slower than the player without touching code.

### Archiving

Archiving a skill archives everything under it, and restoring one restores its
ancestors. Both directions hold the same invariant: **an active skill never
hangs under an archived parent.** An archived skill takes no practice and
receives no roll-up; a quest still pointing at one completes normally and
simply trains nothing, rather than failing.

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
  db.py                # engine, session factory, declarative Base, SQLite FK pragma
  security.py          # Argon2 hashing, JWT encode/decode
  deps.py              # settings / db / current-player dependencies
  errors.py            # AppError hierarchy + JSON error envelope
  content/             # written content: the pantheon, its trials, its auditions
  models/              # User, Player, Quest, Skill, Quote, SideQuest, Constellation, Penalty, SystemEvent
  schemas/             # Pydantic request/response models
  services/
    leveling.py        # pure EXP math — no ORM, no clock
    scheduling.py      # pure period math — when a quest is due, how long you have
    skills.py          # the skill graph; pure tree math, then EXP roll-up
    quotes.py          # the quote collection; pure rotation for the daily pick
    progression.py     # awarding EXP, level-ups, penalties, stat spending
    quests.py          # quest lifecycle
    side_quests.py     # the opt-in, broadcasting, and answering side quests
    story.py           # pure story rules — standing bands, favor, which line
    constellations.py  # the pantheon in the database, and its regard
    friendship.py      # asking to be befriended; the arbiter that decides
    broadcasting.py    # picking written trials off the catalog and scheduling them
    daily.py           # the rollover
    clock.py           # timezone-aware date handling
    status.py          # building the status window
  routers/             # health, auth, players, quests, skills, quotes, side-quests, constellations, system
alembic/               # migrations
web/                   # the React client (see web/README.md)
scripts/               # entrypoints: daily_reset, seed_pantheon,
                       #   schedule_side_quest, broadcast_side_quests
tests/
```

`services/leveling.py`, `services/scheduling.py` and `services/story.py` are
deliberately pure — no database, no clock, no settings object — which is what
makes the EXP curve, the schedule rules and the favor curve cheap to test
exhaustively and safe to retune. The same holds for `pick_for_day` in
`services/quotes.py` and the tree arithmetic at the
top of `services/skills.py` — cycles, depth and subtree height are the rules
easiest to get wrong, so they are testable against plain dictionaries.

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
| `APP_WEB_CLIENT` | `true` | Serve the built web client at `/web` |
| `APP_EXP_CURVE_BASE` | `100` | EXP for level 1 → 2 |
| `APP_EXP_CURVE_EXPONENT` | `1.5` | How steeply the curve climbs |
| `APP_STAT_POINTS_PER_LEVEL` | `3` | Points granted per level |
| `APP_PENALTY_EXP_MULTIPLIER` | `1.0` | Multiple of quest reward lost on failure |
| `APP_FRIENDSHIP_ACCEPT_RATE` | `0.30` | Share of requests a constellation agrees to hear |
| `APP_FRIENDSHIP_RETRY_DAYS` | `7` | Wait before asking the same one again |
| `APP_SKILL_EXP_CURVE_BASE` | `100` | EXP for a skill's level 1 → 2 |
| `APP_SKILL_EXP_CURVE_EXPONENT` | `1.5` | How steeply the skill curve climbs |
| `APP_SKILL_EXP_ROLLUP` | `1.0` | Share of skill EXP reaching each step up the branch |
| `APP_MAX_SKILL_DEPTH` | `5` | How deep the skill graph may nest |

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
- `GET /skills` returns the graph already nested, each node carrying `level`,
  `exp_progress` and `depth` — enough to render an outline without a second
  pass. Quest and practice responses both return `skill_awards`, ordered from
  the skill trained outward, so a level-up animation can walk the branch.
- `GET /quotes/today` backs the lock-screen widget. It is a pure read — no
  daily-reset call needed first — and `refresh_after` is the exact instant the
  quote changes, which is what a WidgetKit timeline wants for its next reload.
  An empty collection returns `quote: null` rather than a 404, so render a
  prompt to write one instead of an error state.
- `GET /constellations` backs a "who is watching" screen: the whole pantheon
  with your standing in each, and a safe read — looking at a constellation you
  have never heard from does not start a history with it. Each carries a
  `friendship` block with `may_ask`, `blocked_by` and `retry_after`, so a
  button can be disabled with the right label instead of the client
  discovering the answer by asking.
- A refusal is a `201` with `status: "refused"`, not an error. The `422` is
  for asking when you may not — already friends, a trial still open, or still
  inside the wait.
- Side quest events carry the voice in `message` and everything structured in
  `payload` (`title`, `constellation`, `standing`, `favor_delta`,
  `standing_changed`), so a popup can show the line and the numbers without
  parsing prose.
- `GET /side-quests/preferences` backs the opt-in screen. It reports
  `offers_per_week` against `offers_this_week`, so you can show what the
  chosen frequency actually means rather than just the word.
- Side quest timestamps are absolute UTC instants, not local dates, and always
  come back with an offset. `expires_at` is the deadline; null means none.
- `GET /system/events` is the notification feed. Each entry carries a
  `payload` with structured detail — `new_level`, `stat_points_gained`,
  `exp_lost` — so you can render System-style popups without parsing strings.

## Not built yet

Titles and achievements, rank (E–S) and job classes, multi-day dungeon
challenges, quest chains, and reusable drafts or templates. The event log and
quest model leave room for all of them.

On the skill side: skill-gated quests, decay for skills left untrained, and
sharing one sub-skill between two parents — which needs an answer to the
double-crediting question before the graph can stop being a tree.

On the quote side: pinning a specific line to a specific day, tagging quotes so
a mood or a training block draws from its own pool, and a starter set to write
against instead of a blank collection.

On the side quest side: there is no authoring API — trials are written into
`app/content/broadcasts.py` and scheduled by script, which is fine while the
author and the operator are the same person. Standing gates what you are sent
and changes what you hear, but nothing else yet; a constellation could
plausibly offer better terms to a champion. Multi-part arcs, quiet hours,
per-player deadlines, and a shared record of who else cleared a broadcast are
all further out. So is a second language, which the content layout is shaped
for but nothing implements.

On friendship: the arbiter rolls dice. Replacing it with one that reads the
request is the next obvious move, and everything it would need is already
stored. A constellation might also plausibly *offer* friendship to someone it
has watched clearing another's trials, rather than only ever being asked.
