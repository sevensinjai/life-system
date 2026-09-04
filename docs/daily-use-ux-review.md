# Life System iOS — New-user and Daily-use UX Review

Date: 31 August 2026  
Device: iPhone 17 Pro Simulator, iOS 26.5  
Build: Debug build succeeded  
Reviewer perspective: a new player adopting the app as a daily life and skill-progression tool

## Executive summary

Life System has a strong, distinctive product idea: turn real-life quests and deliberate practice into a private progression RPG. Its populated screens make that promise feel exciting. The visual language is coherent, the Skill Tree is memorable, the Practice Journal is unusually thoughtful, and the widgets could make the System feel present outside the app.

The largest problem is not visual quality; it is the gap between presentation and lived behavior. A new player sees an empty, unexplained dashboard and must design the progression system before experiencing its reward. A returning player has no truly fast daily action, limited planning or reflection tools, and weak feedback after completing work. More seriously, several local persistence paths do not yet update the progression state implied by the UI.

The best next milestone would be a complete, reliable five-minute daily loop:

1. Open the app and immediately understand today's priorities.
2. Log or complete an action in one or two taps.
3. See exactly what changed: quest progress, player EXP, skill EXP, level, or stats.
4. Feel a small but satisfying moment of reward.
5. Leave with a clear sense of what remains today.

## What was exercised

The app was built and launched repeatedly in Simulator. The review covered:

- A fresh local profile and empty Home screen
- The populated Dashboard
- Quest creation and skill-linked routine creation
- Quest board and quest-card behavior through source-backed flow inspection
- Empty and populated Skill Tree states
- Player State and the extended 100-attribute view
- Practice logging with notes, photos, audio, and active recording
- Skill icon search and selection
- System Log and More/Settings information architecture
- Home Screen and Lock Screen widget simulations
- Relaunch and local persistence behavior
- Extra-extra-extra-large accessibility text on Dashboard and quest creation

Deterministic runtime states were used for populated and media-heavy scenarios. The review did not simulate weeks passing in real time, validate CloudKit on two physical devices, or complete system-level widget installation.

## Product promise as I understand it

The app provides four connected systems:

- **Quests:** self-authored actions with schedules, targets, difficulty, EXP, and optional stat rewards.
- **Player progression:** quest EXP raises the player's level and grants stat points.
- **Skills:** a user-authored hierarchy in which practice earns skill EXP and rolls a share up to parent skills.
- **Presence and reflection:** motivational quotes, a System event history, journal notes, photographic or audio proof, and widgets.

This is a compelling combination. The app is strongest when those systems reinforce one another. It is weakest when the player must infer how they connect.

## Simulated daily-use diary

### Day 1: first launch

I arrive at “Welcome back, Player,” Level 1, an empty quest board, five tabs, and a quote. The interface looks finished, but I do not know what the app expects from me. “Board clear” sounds like an achievement even though I have done nothing. There is no player-name setup, explanation of the game loop, starter quest, or guided payoff.

My likely behavior as an ordinary user would be to explore several tabs, feel that each is empty, and postpone setup. This is a dangerous activation point: the app asks for configuration before it has demonstrated value.

### Day 2: creating a routine

The New Quest screen exposes title, description, recurrence, difficulty, target, unit, practice minutes, stat reward, and review information. This is powerful, but it asks me to understand the economy immediately.

I do not know whether “Practice: 10 minutes” is my goal, my reward, or metadata. I also do not know why an E-rank quest may award the same EXP as another difficulty, or whether target count affects EXP. When a routine is linked to a skill, the relationship becomes even harder to predict: will completion grant player EXP, skill EXP, or both?

I want presets such as “Read 20 minutes daily,” “Exercise three times per week,” or “Practice guitar for 15 minutes.” After creating one, I want a plain-language preview of its outcome.

### Day 3: completing today's work

The Quest Board supports `+1` and `Complete`. This works for counters, but it is not ideal for every unit. A 30-minute reading quest would require repeated increments unless I use Complete, and Complete may overstate what happened. I cannot enter an arbitrary amount, start a timer, undo an accidental tap, or add a quick note.

After completion, I expect a strong result moment: “Quest cleared · +20 player EXP · Reading +20 skill EXP · 80 EXP until Level 2.” That feedback is central to the fantasy. A quiet state refresh is not enough.

### Day 7: reviewing a week

By now the populated Dashboard and Skill Tree are motivating. I can see levels, branches, stats, quotes, and recent transmissions. However, I cannot answer the practical questions that keep a habit system useful:

- Which days did I complete this routine?
- What is my current or best streak?
- Am I improving week over week?
- Which quest do I regularly miss?
- How much time did I spend on each skill?
- What notes or recordings did I make last Tuesday?
- What changed when I levelled up?

The System Log is an event stream, not yet a useful review surface. The app needs weekly reflection and history before it can become a long-term daily companion.

### Day 30: maintaining the system

The custom skill hierarchy is the app's most defensible feature, but it can become long and difficult to manage. I would need reordering, collapse/expand, archive, edit, merge, and search. I would also need a way to pause routines without deleting history and to adjust an over-ambitious schedule without silently breaking streaks or penalties.

At this point, trust matters more than novelty. Sync status, conflict behavior, data export, backups, and transparent penalty rules become essential.

## What works well

### Distinctive identity

The Souls/manhwa styling is not a superficial skin. Gold borders, ember accents, serif headings, ranks, transmissions, sigils, and “Player State” all speak the same language. A populated profile looks desirable, which is valuable motivation in itself.

### Populated Dashboard

The Dashboard gives level, EXP, quote, today's quest progress, core stats, and the latest event a sensible hierarchy. It feels like a status screen rather than a generic habit tracker. The links into Player State, Board, and System are understandable.

### Skill Tree concept

The tree communicates a genuinely useful idea: practice focused sub-skills while retaining progress in the broader craft. Indentation, branch bars, icons, levels, EXP bars, and child counts make the model legible. This is the feature most likely to differentiate the product.

### Practice Journal

The journal is the clearest interaction reviewed. Duration has a sensible default, the prompt encourages reflection, and photos/audio make it suitable for music, fitness, art, cooking, and other non-textual skills. The active recording state is visually unmistakable.

### Custom sigils

The icon picker is rich, searchable, and thematically consistent. Search plus category filters are the correct interaction for a library of this size. Automatic selection is a useful fallback.

### Widgets and deep links

Quick actions on the Lock Screen fit a daily-use product well. They can shorten the path to logging work and make the System feel ambient rather than requiring a deliberate app session.

## Highest-priority findings

### P0 — Make progression behavior truthful and reliable

**Progress update — 31 August 2026:** The offline-first iOS loop now applies player EXP, levels, stat points, direct stat rewards, skill EXP, and ancestor roll-up durably. Completed quests leave Today and cannot pay twice; child skills stay nested; practice notes, attachment metadata, and attachment bytes persist. Quest completion now shows an EXP/level-up receipt. These behaviors passed the in-app progression proof both before and after force-quit/relaunch. Recurring period spawning, reset penalties, undo, full media playback, and multi-device CloudKit conflict testing remain unresolved, so this P0 is improved but not closed.

The local data implementation currently returns rewards without consistently mutating the state shown elsewhere:

- ~~Quest completion reports EXP gained but does not update player EXP or level.~~ Resolved in the offline-first store and verified across relaunch.
- ~~Practice creates a journal entry but does not update skill EXP or levels.~~ Resolved, including ancestor roll-up and skill-level events.
- ~~Practice attachments are accepted by the UI but discarded by the local persistence path.~~ Resolved for durable local bytes and metadata; playback remains future work.
- ~~Completed quests remain active in the locally returned “today” list.~~ Resolved for the current local instance.
- ~~Child-skill creation and nested skill updates appear unable to maintain the intended hierarchy reliably.~~ Resolved and covered by the progression proof.
- Daily reset currently returns a placeholder and does not implement recurrence, failure, or penalties.

These are trust-breaking issues because they affect the central promise. The app should not celebrate or display a reward that has not been durably applied.

### P0 — Fix Dynamic Type before release

At extra-extra-extra-large text, the Dashboard becomes effectively unusable. The date, greeting, player name, card headings, values, and stat-points label expand far beyond their layouts. Important text is clipped or reduced to fragments. Quest creation similarly turns a single screen into enormous labels and controls with poor information density.

Recommended response:

- Cap decorative display typography separately from functional text.
- Switch horizontal rows to vertical layouts at accessibility sizes.
- Avoid fixed frames for text-bearing controls.
- Use `ViewThatFits`, `AnyLayout`, and accessibility-size-specific variants.
- Keep key buttons visible and preserve logical focus order.
- Add screenshot or UI tests for at least Large, XXXL, and AX5 sizes.

### P1 — Deliver first-session activation

Replace the empty-dashboard introduction with a short guided sequence:

1. Ask what the System should call the player.
2. Ask what they want to improve.
3. Offer a small editable starter skill and routine.
4. Let them complete a sample action.
5. Show the resulting player EXP and skill EXP.
6. Reveal the full navigation after the payoff.

The flow should be skippable and should never require the player to understand ranks, stat rewards, schedules, or parent EXP distribution before taking the first action.

### P1 — Create a fast daily interaction

The most common action should require no navigation through a detail screen. Consider:

- Swipe or tap to increment common quests directly.
- Long-press or secondary action for “Complete,” “Add amount,” and “Undo.”
- A numeric entry option for minutes, pages, repetitions, and custom units.
- A timer for practice-based tasks.
- A global “Log practice” action that remembers recent skills.
- Lock Screen or Home Screen actions that land directly in the relevant logger.

### P1 — Add a meaningful completion moment

After a quest or practice entry is saved, show one concise reward sheet or animation:

- What was completed
- Player EXP gained
- Skill EXP gained, including parent roll-up
- Level-up or stat-point changes
- Streak impact
- Remaining progress to the next relevant level

Use celebration selectively. Repeated `+1` actions should be lightweight; completing a period, levelling up, or reaching a mastery milestone should feel special.

## Detailed UX feedback

### Home / Dashboard

**Good**

- Strong visual hierarchy in the populated state.
- Today's missions are visible without opening the Board.
- Quote and transmission add personality.
- Player status is an attractive long-term motivator.

**Problems**

- “Welcome back” is inappropriate on first launch.
- “Player” feels like placeholder data rather than an intentional identity.
- “Board clear” conflates “nothing configured” with “everything completed.”
- The home progress percentage combines different quest units. `40/100 reps` and `20/30 minutes` producing one aggregate percentage looks precise but has questionable meaning.
- Only three quests are previewed; there is no indication of hidden count beyond the total active number.
- Core stat abbreviations are thematic but not self-explanatory to every new user.
- The quote says it is kept in a “daily player record,” but no quote history is exposed.

**Recommendations**

- Distinguish `No quests yet`, `Nothing scheduled`, and `All done today`.
- Use completed quest count, such as `2 of 5 missions cleared`, rather than aggregating unlike units.
- Add a single recommended next action near the top.
- Allow the player to edit name and identity from Player State.
- Make the daily quote tappable to open quote history or management.

### Quest Board

**Good**

- Cards show rank, title, schedule, progress, deadline, and reward context.
- `+1` and Complete are easy to locate.

**Problems**

- `+1` assumes all targets are conveniently countable one at a time.
- Complete can bypass the target without confirmation or a record of actual effort.
- There is no arbitrary amount, undo, timer, note, snooze, skip, pause, or edit action.
- “DUE Today” provides no exact time or penalty context.
- Completed, failed, upcoming, and paused quests lack separate sections.
- Error feedback is a small red line of text at the bottom of the scrolling content.

**Recommendations**

- Tailor the primary control to the unit: counter, duration, checkbox, or timer.
- Add haptics and reversible confirmation for completion.
- Surface the consequence before a penalized period expires.
- Provide Today, Upcoming, Completed, and Paused filters.
- Keep recoverable error messages close to the action that failed.

### Quest creation

**Good**

- The form contains the necessary scheduling and reward controls.
- Defaults enable a quick creation path once the concepts are understood.
- Skill-linked routine creation explains that EXP rolls up the branch.

**Problems**

- Too many game-economy decisions are presented at once.
- “Practice minutes” looks like another target, but is also used as an EXP award.
- Difficulty does not visibly explain its consequence.
- Unit is free text, which can create inconsistent labels such as `min`, `mins`, and `minutes`.
- Schedule copy uses system language such as “period” and “local day.”
- The form does not preview the next due date or penalty.
- A user can create an unrealistic or contradictory configuration without guidance.

**Recommendations**

- Start with Title, Frequency, and Goal; put advanced rewards behind disclosure.
- Provide typed units with a custom option.
- Show an always-updated summary: “Every day, read 20 pages. Completion gives 15 player EXP and 15 Reading EXP. Resets at midnight.”
- Offer templates and explain ranks through examples.
- Warn gently about aggressive schedules rather than blocking them.

### Skills

**Good**

- Clear explanation of roll-up behavior.
- Branch indentation is understandable at shallow depths.
- Levels and EXP bars make practice tangible.

**Problems**

- A long tree becomes a flat scrolling list with subtle indentation.
- Repeated gold branch bars are difficult to trace across many siblings.
- No collapse, reordering, search, archive, edit, or merge operations are visible.
- “Total minutes mastered” and current-level EXP can be confused.
- The app does not explain the parent's configured EXP share at the point of logging.

**Recommendations**

- Support expandable branches and remember their state.
- Add search and a “recently practised” view.
- Expose parent roll-up as an optional breakdown after logging.
- Provide edit and reorganization tools without losing history.
- Consider a graph/tree view for exploration and a list view for fast daily logging.

### Player State and 100 attributes

**Good**

- Player State is one of the strongest fantasy payoffs.
- Level, EXP, unspent points, core attributes, and mastery are visually coherent.
- The screen gives long-term progression a sense of weight.

**Problems**

- “Ashen Wanderer” and “Bearer of the System” look user-specific but their origin and editability are unclear.
- The 100 extended attributes look authoritative even though they are derived presentation data.
- Repeating one icon for every row in a category makes scanning harder.
- A list of 100 numeric traits provides little actionability or explanation.
- It is unclear how scores change or what a difference between 59 and 60 means.

**Recommendations**

- Clearly label generated/derived traits and explain their calculation.
- Show changes over time rather than only absolute values.
- Lead with notable strengths, recent growth, and meaningful milestones.
- Allow categories to collapse and provide search.
- Treat the full 100-trait list as an optional curiosity, not a primary progression mechanic, unless it becomes directly actionable.

### Practice Journal

**Good**

- Strong prompt for useful reflection.
- Notes, photos, and audio support many real-world skills.
- The recording state is clear and urgent.
- Attachment limit is communicated.

**Problems**

- Minute adjustment by stepper is slow for large changes.
- The user cannot play back or inspect an audio attachment before saving.
- Photo thumbnails have a small removal target.
- Saved journal entries do not yet expose full viewing, editing, deletion, playback, or media viewing.
- There is no autosaved draft if the sheet is dismissed or the app is interrupted.
- Permission denial and storage failures need dedicated recovery states.

**Recommendations**

- Make duration directly editable and offer common chips such as 5, 15, 30, and 60.
- Show recording duration, playback, replace, and delete before save.
- Autosave drafts locally.
- Allow later editing and media review.
- Add optional tags such as technique, difficulty, mood, or quality only after the basic loop is solid.

### Icon picker

**Good**

- Search and category chips are immediately visible.
- Four-column grid balances density and recognition.
- Selection has a strong border.

**Problems**

- Some icons render as plain circles, which looks like a missing asset rather than an intentional symbol.
- Category chips can be cut off horizontally with little affordance that more exist.
- “Automatic” sits beside concrete icons without explaining what it will choose.
- The library may encourage customization before the first skill is even useful.

**Recommendations**

- Eliminate or label fallback-circle assets.
- Keep Automatic as a separate recommended option with explanatory copy.
- Defer manual icon choice during onboarding; allow it later from skill detail.

### System Log

**Good**

- “Transmission” fits the fantasy and can reinforce accomplishments.
- Event type, message, and time form a simple record.

**Problems**

- Raw ISO-style timestamps are not friendly daily reading.
- No grouping by day, filtering, search, or event details.
- It is not a substitute for quest history, practice history, or analytics.
- Failures and penalties need especially clear explanations and recovery paths.

**Recommendations**

- Use relative/localized time and day sections.
- Add event-specific detail views.
- Let users filter rewards, quests, skills, levels, and penalties.
- Keep the log as narrative history while adding a separate weekly review.

### More / Settings

**Good**

- Storage and sync are acknowledged.
- Quest library and icon credits have logical homes.
- Widget setup instructions are present.

**Problems**

- “Sync: iCloud” looks like a guaranteed current status rather than a capability.
- There is no last-sync time, offline/conflict state, export, reset, notification control, appearance setting, accessibility setting, or help.
- Refreshing the Lock Screen quote is an implementation-oriented action most users should not need.

**Recommendations**

- Show truthful sync state and last successful sync.
- Add data export, privacy, notifications, player identity, and help.
- Explain what is private and what is stored in iCloud.
- Hide manual widget refresh unless an error requires it.

### Widgets

**Good**

- Lock Screen quick actions are a natural fit for frequent logging.
- The Home Screen quote adds ambient motivation.
- Deep-link destinations match core app areas.

**Problems**

- Four unlabeled Lock Screen icons may be ambiguous.
- A generic running figure appears to imply practice, but its destination is described elsewhere as System Log.
- The current extension and documentation disagree about whether the widget is a quote widget or quick-actions widget.
- The simulation is not proof that system-level multiple interaction targets work in every Lock Screen context.

**Recommendations**

- Verify the actual widget on supported devices and OS versions.
- Use the most direct action destinations, especially Log Practice and Today's Board.
- Keep names, instructions, extension behavior, and screenshots consistent.

## Information architecture feedback

Five tabs are understandable, but “System” is vague next to the app itself being called System. The practical meaning is “Activity” or “History.” “More” contains important quest management that may deserve a clearer route.

A daily user's mental model is likely:

- **Today:** what should I do now?
- **Skills:** what am I learning and how is it growing?
- **Progress:** how is my player changing?
- **History:** what have I done?
- **Settings:** how does the app behave?

The current Home and Board split is defensible, but the primary action should not require choosing the correct tab. A global quick-log action could reduce navigation cost while retaining the five destinations.

## Language and terminology

The thematic vocabulary is effective when it adds feeling, but some copy prioritizes system precision over comprehension.

Suggested translations:

| Current language | Clearer user-facing language |
| --- | --- |
| Board clear | No quests yet / All done today |
| A fresh period opens each local day | Resets every day at midnight |
| Practice minutes | Player EXP reward, or Expected duration, depending on intended meaning |
| Latest transmission | Latest activity, with “transmission” retained as secondary flavor |
| System events | Activity history |
| Completion credits 10 minutes | Completion logs 10 minutes of practice |

Game terminology should remain, but the consequence should be stated in plain language nearby.

## Accessibility and visual design

### Contrast

Muted gray text and disabled placeholders are often too dim against black and dark charcoal. This affects explanatory copy, form placeholders, timestamps, and disabled actions. Gold is attractive but should not be the only indication of state.

### Dynamic Type

The largest tested text size breaks core screens. This is a release blocker for accessibility support. Decorative headings and functional data need separate scaling strategies.

### Touch targets

Most major buttons are comfortably sized. Smaller concerns include attachment removal, compact chevrons, branch rows, and some icon-only actions. Verify at least 44×44 points and provide meaningful accessibility labels.

### Color and state

Progress and selection should remain understandable without relying solely on gold, cyan, or red. Add icons, labels, or patterns where state matters.

### Motion and celebration

Level-up and completion effects should honor Reduce Motion. Haptics should be optional and semantically different for increment, completion, failure, and level-up.

### VoiceOver

The visual tree, aggregate status cards, progress bars, and icon grid need intentional reading order and combined labels. Examples:

- “Pitch accuracy, level 3, 160 of 220 experience, one sub-skill.”
- “Morning strength training, C rank, 40 of 100 repetitions, due today.”
- “Run sigil, selected.”

## Retention and motivation

Penalties give the product meaning, but they can also create avoidance. A user who misses several days may stop opening the app if the first thing they see is loss and failure.

Recommended motivational safeguards:

- Make penalties explicit and opt-in at quest creation.
- Offer pause/vacation and compassionate recovery modes.
- Distinguish “skipped intentionally” from “forgotten.”
- Celebrate consistency without making streak loss irreversible.
- Suggest reducing an repeatedly missed target.
- Use the System voice to be firm but not shaming.

The ideal tone is: “The contract mattered, the result is recorded, and the next useful action is clear.”

## Trust, privacy, and data durability

Because the app stores personal routines, reflections, photos, and audio, it should explain:

- Whether data is only on-device or also in private iCloud storage
- How attachments sync
- What happens when iCloud is unavailable or full
- Whether deletion removes synced copies
- How to export data
- How conflicts between devices are resolved

The current single-snapshot persistence approach should be reviewed for multi-device conflict risk. A status label reading “iCloud” is not enough to establish that the latest journal entry is safely synced.

## Documentation and product consistency issues

- The iOS README describes an offline-first SwiftData/CloudKit app.
- The iOS feature map still describes an authenticated API shell in places.
- Harness instructions reference authentication and Keychain behavior that no longer matches the currently launched local-only flow.
- Widget documentation alternates between a Daily System Quote widget and a Quick Actions widget, while the extension currently exports only one main widget configuration.

These inconsistencies make QA and product expectations unreliable. The current architecture and shipping feature set should have one canonical description.

## Recommended roadmap

### Phase 1 — Trustworthy core loop

- Apply player and skill rewards durably and atomically.
- Correct quest completion, recurrence, and today filtering.
- Preserve practice attachments and child-skill hierarchy.
- Add reward confirmation and undo where appropriate.
- Fix Dynamic Type and baseline VoiceOver labels.
- Add end-to-end tests for create → progress → complete → relaunch.

### Phase 2 — Activation and speed

- Add identity setup and guided first quest/skill.
- Add templates and simplified quest creation.
- Add arbitrary amount entry, timers, and recent-skill quick logging.
- Improve empty states and direct actions.
- Make widget deep links land on actionable screens.

### Phase 3 — Long-term usefulness

- Add calendar/history, streaks, weekly review, and time-by-skill trends.
- Add editing, pausing, archiving, search, and tree organization.
- Add journal playback, editing, deletion, and draft recovery.
- Add truthful sync status, export, and conflict handling.

### Phase 4 — Richer game layer

- Add thoughtful level-up ceremonies, titles, and milestones.
- Make extended attributes explainable and action-oriented.
- Introduce optional side quests and constellation features only after the personal loop is reliable.

## Suggested acceptance scenarios

1. A fresh user can create a named player, one skill, and one daily routine in under two minutes without knowing the terminology.
2. Completing a quest updates the quest, player EXP, level, stat points, event history, Dashboard, and widget consistently after relaunch.
3. Logging practice updates the selected skill and every configured parent award, saves notes/media, and explains the award breakdown.
4. A completed daily quest leaves the active Board and appears in today's completed history.
5. A failed recurring quest applies exactly the disclosed penalty once, records why, and opens the next period correctly.
6. A user can undo an accidental progress or completion action without corrupting rewards.
7. The app remains usable at AX5 text size without clipped controls or unreadable cards.
8. VoiceOver can create a quest, complete it, and log practice with meaningful labels and logical focus order.
9. An offline change persists after force quit and reconciles predictably when iCloud returns.
10. A second device receives the latest quest and journal data without silently overwriting newer changes.

## Final assessment

The app already has the emotional shell of a product people could care about. The populated states successfully answer, “What might my life look like if progress felt visible?” The next work should focus less on adding more systems and more on making the existing loop immediate, trustworthy, accessible, and rewarding every single day.

If the first five minutes teach the loop, the next five seconds make logging effortless, and every reward is durably true, Life System can feel substantially more compelling than either a standard habit tracker or a decorative RPG dashboard.

## Product-development history — 1 September 2026

### Dynamic Type Dashboard vertical slice

Carried-forward finding: **P0 — Fix Dynamic Type before release**.

The populated Dashboard now adopts accessibility-specific layouts instead of forcing its normal horizontal composition through AX sizes. Player status and mission summaries stack, mission titles wrap, attributes become a two-column grid with full names, and the latest transmission stacks vertically. Decorative welcome and eyebrow typography caps at AX2 while functional values and controls continue scaling through AX5. The affected status, mission, attribute, and activity controls also gained combined VoiceOver descriptions and navigation hints.

Verification on the iPhone 17 Pro Simulator running iOS 26.5:

- The Debug app build completed with `** BUILD SUCCEEDED **`.
- The deterministic populated Dashboard was launched at Large and AX5 using `-dashboardPreview`.
- Large and AX5 screenshots were inspected for horizontal clipping, card-boundary overflow, unreadable mission titles, and lost controls. The adaptive layouts remained within the viewport width; the AX5 screen remains vertically scrollable as expected.
- Evidence: `ios/Screenshots/dashboard-dynamic-type-large.png` and `ios/Screenshots/dashboard-dynamic-type-ax5.png`.

This is a verified partial resolution, not closure of the original P0. Quest creation and the remaining core screens still require the same Large/XXXL/AX5 treatment and VoiceOver journey verification before the release blocker can be marked resolved.

## Product-development history — 1 September 2026 (quest creation accessibility)

### Dynamic Type quest-creation vertical slice

Carried-forward finding: **P0 — Fix Dynamic Type before release**.

Quest and skill-linked routine authoring now remain usable when the system is set to AX5. The dense form supports scaling through AX2 rather than expanding every field and section heading without bound. At accessibility sizes, the selected-weekday control becomes a two-column grid with full day names and 44-point minimum targets instead of forcing seven initials into one row. Schedule explanations and review titles wrap, the review heading can stack, and VoiceOver receives one plain-language summary of the configured quest and rewards.

Verification on the iPhone 17 Pro Simulator running iOS 26.5:

- The Debug app build completed with `** BUILD SUCCEEDED **`.
- The deterministic quest-creation screen was launched at Large and AX5 using `-createQuestPreview`.
- Large and AX5 screenshots were inspected for horizontal clipping, card-boundary overflow, readable fields, retained toolbar actions, and scrollable access to later sections. The accessibility weekday state was separately launched with `-createQuestWeekdaysPreview`; it displayed full day labels in two columns without horizontal clipping.
- Evidence: `ios/Screenshots/quest-creation-dynamic-type-large.png` and `ios/Screenshots/quest-creation-dynamic-type-ax5.png`.

This is another verified partial resolution, not closure of the original P0. The remaining core screens and a complete VoiceOver create → complete → practice journey still need Large/XXXL/AX5 verification before the release blocker can be marked resolved.

## Product-development history — 1 September 2026 (offline recurring settlement)

### Durable recurring reset and disclosed penalties

Carried-forward finding: **P0 — Make progression behavior truthful and reliable**, specifically “Daily reset currently returns a placeholder and does not implement recurrence, failure, or penalties.” Acceptance scenario addressed: **5. A failed recurring quest applies exactly the disclosed penalty once, records why, and opens the next period correctly.**

The offline-first iOS store now persists recurrence configuration and period identity, settles lapsed active periods, deducts no more than the player's current-level EXP, preserves lifetime earned EXP and level, records durable failure/penalty/reset transmissions and penalty metadata, and opens the period currently due. Repeating reset against that period is idempotent. Recurring quest creation now states the maximum current-EXP loss in both visible review copy and its combined VoiceOver summary.

Verification on the iPhone 17 Pro Simulator running iOS 26.5:

- The Debug app build completed with `** BUILD SUCCEEDED **`.
- The deterministic `-dailyResetProof` journey funded current EXP, backdated one daily quest, ran reset twice, and verified one failure, one 25 EXP loss, one fresh zero-progress period, and saved failure/penalty transmissions.
- After force-quit and relaunch, the persisted snapshot decoded successfully and the complete proof passed again; this also verified that repeated settlement remained one-time within each generated period.
- Quest creation was inspected at Large and AX5 after adding the penalty disclosure. The form remained vertically scrollable with retained controls; no new horizontal clipping was observed.
- Evidence: `ios/Screenshots/daily-reset-proof.png`, `ios/Screenshots/daily-reset-proof-relaunch.png`, `ios/Screenshots/quest-penalty-disclosure-large.png`, and `ios/Screenshots/quest-penalty-disclosure-ax5.png`.

This resolves the offline authored-quest portion of the reset placeholder. The P0 remains open for foreground-trigger coverage, a player-facing penalty-history surface, physical-device/multi-device CloudKit conflict testing, and side-quest parity in the offline store.
