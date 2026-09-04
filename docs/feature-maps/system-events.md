# System events

## Purpose

`SystemEvent` is the player's notification/history feed. Domain services write a human-readable message plus structured JSON payload whenever meaningful progression, quest, reset, side-quest, or constellation story changes occur.

## Public API

- `GET /system/events` — newest first, filterable by event type, with limit/offset pagination.
- `GET /system/penalties` — related but separate financial/progression loss history; see the scheduling map.

Contracts: `app/schemas/event.py`; routes: `app/routers/system.py`; model: `app/models/event.py`; common writer: `app/services/progression.py::log_event` plus domain-specific services.

## Event sources

- Player EXP awards, level-ups, stat changes, and penalties.
- Authored quest completion/failure and daily reset summary.
- Side-quest offer, decision, completion, failure, expiry, withdrawal, and narrative outcomes.
- Constellation petitions, replies, admission trials, friendship changes, favor/standing story.

Exact event values are defined by `EventType` in `app/models/enums.py`. Payloads are intentionally structured for richer clients; preserve backward-readable keys when evolving them.

## Invariants

- Events are scoped to one player and ordered by newest ID/time.
- A message is displayable without interpreting payload.
- Payload carries machine-readable context such as new level or narrative line.
- Event creation should occur in the same transaction as the domain state change to avoid a feed that disagrees with reality.
- Do not put secrets, passwords, tokens, or sensitive request bodies in messages/payloads.

## Clients and gaps

- Web: `web/src/features/system/system-view.tsx` combines System/event and request visibility.
- iOS: `SystemLogView.swift` shows type, message, and raw created timestamp. Offline recurring settlement now writes `quest_failed`, `penalty_applied`, and summary `daily_reset` transmissions in the same persisted snapshot as the quest and player mutations; no type-specific rendering, pagination, or payload presentation exists yet.

## Verification

- Primary tests: `tests/test_system_log.py`; daily, quest, progression, friendship, side-quest, and story tests assert specific integrated events.
- Verify event count/idempotency as well as wording and payload when changing a domain transition.
