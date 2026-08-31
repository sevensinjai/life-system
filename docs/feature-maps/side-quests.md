# Side quests

## Purpose and data split

Side quests are global System broadcasts rather than player-authored work. `SideQuest` is the shared broadcast; `SideQuestOffer` is the per-player answer/progress snapshot; `SideQuestPreference` controls whether and how often a player may be interrupted.

## Public player API

- `GET/PATCH /side-quests/preferences` — opt-in, frequency (`rare`, `occasional`, `frequent`), maximum difficulty, auto-accept, and live counts.
- `GET /side-quests` and `GET /side-quests/{offer_id}` — history or live offers.
- `POST /side-quests/{offer_id}/accept`
- `POST /side-quests/{offer_id}/decline`
- `POST /side-quests/{offer_id}/progress`
- `POST /side-quests/{offer_id}/complete`

Contracts: `app/schemas/side_quest.py`; routes: `app/routers/side_quests.py`; models: `app/models/side_quest.py`; domain operations: `app/services/side_quests.py`.

## Broadcast production

- Catalog/content: `app/content/challenges.py` and `app/content/broadcasts.py`.
- Scheduling: `app/services/broadcasting.py`.
- Operator scripts: `scripts/schedule_side_quest.py`, `scripts/broadcast_side_quests.py`.
- Production cron dispatch is handled by `worker.py`/`wrangler.jsonc`.

## Lifecycle and invariants

- No preference row means opted out; nobody is enrolled implicitly.
- Opting in immediately catches up eligible still-open broadcasts within the rolling frequency cap.
- Opting out blocks new offers but does not retract accepted work.
- Offers are unique per `(side quest, player)`, so dispatch is idempotent.
- Windows are absolute UTC instants, shared across timezones.
- Offers snapshot deadline, target, reward, penalty, and story details so broadcast edits do not move goalposts.
- Unanswered offers expire free; declined and withdrawn offers are free; only accepted unfinished offers may fail and pay the configured penalty.
- A declined offer still consumes a frequency slot because the cap measures interruptions.
- Completion awards progression/stat rewards, updates constellation favor/story when applicable, and may settle a friendship trial.

## Clients and gaps

No web or iOS side-quest UI exists. Preferences, inbox/history, accept/decline, progress, and outcome story are backend-only.

## Verification

- Primary tests: `tests/test_side_quest_api.py`, `tests/test_side_quest_optin.py`, `tests/test_side_quest_lifecycle.py`; friendship/story tests cover integration.
- Cover all terminal statuses, eligibility/frequency/max-rank filtering, auto-accept, late opt-in, repeat broadcast/sweep, UTC deadlines, and penalty safety.
