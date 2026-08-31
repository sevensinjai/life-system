# iOS experience

## Purpose and navigation

The SwiftUI client under `ios/LifeSystem` is a native, offline-first game-like client backed by a SwiftData snapshot that can sync through the player's private iCloud store. `LocalDataStore` preserves the API-shaped request boundary while applying quest, player, skill-tree, practice-journal, event, and attachment mutations locally. `MainTabView` owns five destinations: Home, Board, Skills, System, and More. Dashboard cards route to Player State, the quest board, and the event feed. Debug-only deterministic launch arguments in `LifeSystemApp.swift` render important feature states and exercise the durable progression loop without external credentials.

## Visual system

- `SystemTheme.swift` owns the shared charcoal, parchment, tarnished-gold, and ember palette, gradient `SystemBackdrop`, rune-corner `SystemCard`, and serif `SystemHeader`.
- Dashboard, authentication, quest, skill-tree, practice, log, settings, and shared controls inherit this Souls-style language.
- `StatusView.swift` provides the richer Player State treatment. It displays player identity, canonical stats, EXP, skill count, and skill mastery from live `/players/me` plus `/skills` data.
- The extended “Hundred Facets” modal groups 100 generated human traits into Physical, Cognitive, Emotional, Social, Creative, Practical, Discipline, Perception, Resilience, and Character. Scores are derived presentation data, not backend state.

## Skill sigils

- `SkillIcons.xcassets` contains 150 curated template-vector SVGs from Game-icons.net, 15 in each of ten categories.
- `SkillIconCatalog.swift` is the key/title/category/author registry and provides name-aware SF Symbol fallback.
- `SkillIconPicker.swift` provides an always-visible live search field, horizontally scrolling category filters, four-column selection grid, automatic fallback, selection highlighting, and an empty-search state.
- Creation and detail editing persist the optional `icon_key`; tree and Player State consume it.
- `SkillIconCreditsView` is reachable from More → Library. Source attribution is also recorded in `SkillIconAttribution.md`. Preserve CC BY 3.0 credit when changing or redistributing these assets.

## Practice journal

- `LogPracticeView` is a lightweight note-style logger for practice duration, text, up to six selected photos, and audio recording. The backend limit is eight total attachments.
- Recording exposes a visible active/stop state. Saved journal history appears on skill detail with attachment counts.
- Media is stored by the backend and fetched through ownership-protected attachment URLs. Playback, full-screen viewing, and entry editing/deletion are future work.
- In the offline-first store, practice atomically saves the entry and attachment bytes, updates the focused skill, rolls the same EXP through its ancestors, emits skill-level events, and preserves the nested hierarchy.

## Offline progression invariants

- A completed quest pays player EXP and its direct stat reward exactly once, applies level thresholds and stat points, records System events, and leaves the active Today board.
- A skill-linked quest credits the same practice-minute amount to the selected skill and every ancestor.
- Direct practice persists notes and attachment data together with all skill awards.
- Child creation remains nested, and nested skill updates preserve existing descendants.
- `-progressionProof` runs the real local request path and displays durable checks for player rewards, level/stat changes, Today filtering, nesting, roll-up, and journal media; relaunching it proves the prior state was persisted.
- Quest completion presents a player-facing reward receipt, including the player EXP award and level-up direction.

## Lock Screen quick actions

- `ios/QuoteWidget/QuoteWidget.swift` currently exports `QuickActionsWidget` as the extension's sole `@main` widget.
- It supports only `.accessoryRectangular` and presents Home, Board, Practice/System Log, and Skills links using the `lifesystem://` scheme.
- `MainTabView.onOpenURL` maps those hosts to tabs. iOS controls Lock Screen widget size, placement, authentication, and whether multiple interaction targets are honored in the current Lock Screen context.
- `LockScreenWidgetSimulationView` is a deterministic in-app visual simulation; it is not the actual system Lock Screen editor.

## Verification and evidence

- Follow `.codex/skills/harness/SKILL.md` for Xcode build, Simulator launch, and screenshot requirements.
- Stable launch arguments currently cover dashboard, skills, player state, the extended attributes list, icon picker, practice journal/media/recording, routine creation, quest reward receipt, durable progression proof, and Lock Screen simulation.
- Useful acceptance artifacts live under `ios/Screenshots/`; screenshots are evidence, not runtime resources.
