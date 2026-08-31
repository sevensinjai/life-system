# Authored quests

## Purpose and lifecycle

Authored quests are private player-defined templates. A `Quest` describes work, schedule, target, practice-minute/EXP reward, optional direct stat reward, and optional linked skill. A `QuestInstance` snapshots one open attempt/period. Players log progress or complete outright; reaching the target completes automatically.

## Public API

- `POST /quests` — author a quest.
- `GET /quests` — list, optionally filter schedule/recurrence and include archived.
- `GET /quests/today` — active instances the player can progress now.
- `GET /quests/{id}` — definition plus current instance and next due date.
- `PATCH /quests/{id}` — edit or restore.
- `DELETE /quests/{id}` — archive, never hard-delete.
- `POST /quests/{id}/progress` — add or correct units; zero is invalid.
- `POST /quests/{id}/complete` — complete the open instance outright.

Contracts: `app/schemas/quest.py`; routes: `app/routers/quests.py`.

## Persistence and services

- Models: `Quest`, `QuestInstance`, `Penalty` in `app/models/quest.py`.
- Main domain operations: `app/services/quests.py`.
- Schedule calculations: `app/services/scheduling.py`; rollover in `app/services/daily.py`.
- Completion calls progression awards and, when linked, skill awards.

## Invariants

- Every query/action is scoped to the current player.
- `(quest_id, period_start)` is unique, making period creation idempotent.
- An instance snapshots target and practice minutes so later definition edits cannot rewrite resolved history.
- Editing `target_count` intentionally updates the currently active instance; schedule edits apply to future periods.
- Changing interval length preserves the original anchor unless a new anchor is explicitly supplied.
- One practice minute equals one player EXP; deprecated `exp_reward`/`skill_exp_reward` aliases must agree with canonical minutes.
- A linked skill receives the same credited minutes and rolls awards up its ancestor chain.
- Archived quests stop spawning periods but retain history.

## Clients and gaps

- Web: board, authoring/edit sheet, archive/restore, progress, and completion under `web/src/features/quests`.
- iOS: `QuestViews.swift` provides board progress/completion, a completion reward receipt, and the quest library. `CreateQuestView.swift` authors one-time, daily, selected-weekday, interval, and weekly quests with target, rank, practice-minute/EXP reward, and optional stat reward. Starting the form from a skill detail pre-links that skill. The offline-first store applies player EXP, level/stat-point changes, direct stat rewards, linked-skill roll-up, event history, and Today removal atomically and rejects duplicate payouts from an already completed instance. General skill selection, editing, archive/restore, custom progress amounts, and pace conversion are not implemented.

## Verification

- Primary tests: `tests/test_quests.py`, `tests/test_quest_authoring.py`, `tests/test_schedule_lifecycle.py`, `tests/test_scheduling.py`.
- Integrated behavior also appears in leveling, skills, daily reset, and system log tests.
- Verify both action response state and downstream player/skill/event state.
