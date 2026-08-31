# iOS experience

## Purpose and navigation

The SwiftUI client under `ios/LifeSystem` is a native game-like shell over the authenticated API. `MainTabView` owns five destinations: Home, Board, Skills, System, and More. Dashboard cards route to Player State, the quest board, and the event feed. Debug-only deterministic launch arguments in `LifeSystemApp.swift` render important feature states without API credentials for simulator evidence.

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

## Lock Screen quick actions

- `ios/QuoteWidget/QuoteWidget.swift` currently exports `QuickActionsWidget` as the extension's sole `@main` widget.
- It supports only `.accessoryRectangular` and presents Home, Board, Practice/System Log, and Skills links using the `lifesystem://` scheme.
- `MainTabView.onOpenURL` maps those hosts to tabs. iOS controls Lock Screen widget size, placement, authentication, and whether multiple interaction targets are honored in the current Lock Screen context.
- `LockScreenWidgetSimulationView` is a deterministic in-app visual simulation; it is not the actual system Lock Screen editor.

## Verification and evidence

- Follow `.codex/skills/harness/SKILL.md` for Xcode build, Simulator launch, and screenshot requirements.
- Stable launch arguments currently cover dashboard, skills, player state, the extended attributes list, icon picker, practice journal/media/recording, routine creation, and Lock Screen simulation.
- Useful acceptance artifacts live under `ios/Screenshots/`; screenshots are evidence, not runtime resources.
