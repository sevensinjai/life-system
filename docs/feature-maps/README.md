# Life System feature maps

These files are routing context for coding agents. Read this index, then load only the map for the feature being changed. A map describes the feature's behavior, ownership, invariants, API, clients, and verification surface; it is not a replacement for reading the touched code.

## Product loop

An account owns one player. The player authors quests, builds a skill tree, links routines to specific skills or sub-skills, and records practice in a lightweight text/photo/audio journal. Completing work awards EXP, levels, stat points, optional stat rewards, and skill EXP. A local-day reset opens and settles authored quest periods. Separately, opted-in players may receive absolute-time side quests from constellations they have befriended. Outcomes update constellation favor and write System events. The player's private quote pool supplies a deterministic quote each local day.

## Maps

- [Authentication and accounts](authentication.md) — registration, login, JWTs, ownership boundaries, iOS Keychain.
- [Player progression and status](player-progression.md) — EXP, levels, stats, profile, allocation.
- [Authored quests](authored-quests.md) — quest authoring, instances, progress, rewards, archive behavior.
- [Scheduling, reset, and penalties](scheduling-reset-penalties.md) — local-date periods, daily rollover, failures, penalty history.
- [Skills and practice](skills.md) — skill tree, practice minutes, roll-up, quest linkage.
- [Quote rotation](quotes.md) — private quote collection and deterministic daily selection.
- [Side quests](side-quests.md) — opt-in broadcast offers, lifecycle, rewards, and safe ignoring.
- [Constellations and friendship](constellations-friendship.md) — pantheon, favor, standing, petitions, admission trials, narrative voice.
- [System events](system-events.md) — notification/event feed and structured payloads.
- [iOS experience](ios-experience.md) — Souls-style design system, player state, extended attributes, skill sigils, practice journal, and Lock Screen quick actions.

## Cross-cutting implementation

- Backend: FastAPI routers in `app/routers`, SQLAlchemy models in `app/models`, domain rules in `app/services`, Pydantic contracts in `app/schemas`.
- Local persistence: SQLite at `system.db`, schema managed by Alembic.
- Production: one Cloudflare Python Worker with D1 and static React assets; entrypoint `worker.py`, config `wrangler.jsonc`, D1 migrations under `d1/migrations`.
- Web: React/Vite phone-width client under `web/src`.
- iOS: SwiftUI client under `ios/LifeSystem`; use the project-local `$harness` skill for previews, simulator builds, API-connected checks, and screenshots.
- Authentication is the ownership boundary for every player-scoped feature. Route dependencies resolve the current user/player; service queries must continue to include player ownership.
- API errors share `{ "error": { "code", "message", "details"? } }` through `app/errors.py`.

## Current client coverage

| Feature | Backend | Web | iOS |
| --- | --- | --- | --- |
| Authentication | Complete | Login/register | Login/register + Keychain |
| Player progression | Complete | Status/profile/allocation/reset | Dashboard + Souls-style Player State + 100 derived facets |
| Authored quests | Complete | Author/run/archive | Author/list/run; no editing yet |
| Scheduling/penalties | Complete | Reset + log visibility | Reset; no penalty view |
| Skills | Complete | None | Tree/create/practice journal/linked routine/150-icon picker; limited editing |
| Quotes | Complete | Collection + daily quote | Daily dashboard quote; no collection UI |
| Side quests | Complete | None | None |
| Constellations/friendship | Complete | None | None |
| System events | Complete | Feed | Themed feed |
| Lock Screen quick actions | N/A | N/A | Rectangular widget for Home, Board, Practice, and Skills |

Update the relevant map whenever a change alters behavior, data shape, a public endpoint, an invariant, or client coverage.
