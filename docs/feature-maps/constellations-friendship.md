# Constellations and friendship

## Purpose

Constellations are authored narrative entities behind side quests. Each player/constellation pair may have favor history and friendship state. A constellation sends ordinary trials only to friends. A player petitions for friendship; the arbiter may refuse, or issue an admission trial as a normal side-quest offer. Completing that trial establishes friendship.

## Public API

- `GET /constellations` — pantheon with player-specific standing and friendship blocks.
- `GET /constellations/{code}` — one constellation, retired included.
- `POST /constellations/{code}/friendship` — petition with optional message; response may be refusal or challenge, not necessarily an error.
- `DELETE /constellations/{code}/friendship` — walk away and begin retry wait.

Contracts: `app/schemas/constellation.py`; routes: `app/routers/constellations.py`.

## Persistence and services

- Models: `Constellation`, `ConstellationFavor`, `FriendshipRequest` in `app/models/constellation.py`.
- Pantheon/favor operations: `app/services/constellations.py`.
- Petition/challenge settlement: `app/services/friendship.py`.
- Standing thresholds, favor deltas, narrative line selection: `app/services/story.py`.
- Authored pantheon and voice data: `app/content/pantheon.py`; seed through `scripts/seed_pantheon.py`.

## Invariants

- `Constellation.code` is stable identity; display name/voice may change.
- Missing favor means no history and should be projected read-only without creating a row.
- Standing is derived from numeric favor; it is not stored separately.
- Favor tracks offer outcome counts and timestamps, but never directly changes player EXP/stats.
- Friendship gates constellation broadcast eligibility.
- A player cannot petition while already friends, during an open challenge, or before `may_ask_after`.
- Refusal, failed/declined/expired admission trial, and voluntarily ending friendship impose the retry delay.
- Trial settlement is driven by the linked side-quest offer.
- Voice lines are stored as data and the response line is read back from the emitted event so API response and feed cannot disagree.

## Clients and gaps

No web or iOS pantheon, standing, friendship petition, or admission-trial UI exists.

## Verification

- Primary tests: `tests/test_constellations.py`, `tests/test_friendship.py`, `tests/test_story.py`; side-quest tests cover offer integration.
- Use deterministic/fake arbiters in tests. Cover missing-history reads, cooldowns, all challenge endings, favor bands, retirement, ending/rejoining, and event narration.
